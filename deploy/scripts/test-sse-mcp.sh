#!/bin/bash
set -euo pipefail

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="${DOMAIN:-}"
MCP_AUTH_KEY="${MCP_AUTH_KEY:-}"
NAMESPACE="${NAMESPACE:-mcp-hubspot}"
TIMEOUT="${TIMEOUT:-30}"
TEST_CONTACT_LIMIT="${TEST_CONTACT_LIMIT:-5}"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_debug() {
    echo -e "${PURPLE}[DEBUG]${NC} $1"
}

# Load environment configuration
load_environment() {
    if [[ -f "$DEPLOY_DIR/environment" ]]; then
        source "$DEPLOY_DIR/environment"
        log_info "Environment loaded from $DEPLOY_DIR/environment"
    else
        log_warning "Environment file not found at $DEPLOY_DIR/environment"
    fi

    # Set defaults if not provided
    DOMAIN="${DOMAIN:-mcp-hubspot.keltio.fr}"

    # Check required variables
    if [[ -z "$DOMAIN" ]]; then
        log_error "DOMAIN is required. Set it in environment file or as environment variable."
        exit 1
    fi

    if [[ -z "$MCP_AUTH_KEY" ]]; then
        log_warning "MCP_AUTH_KEY not set. Some tests may fail."
    fi
}

# Test basic connectivity
test_basic_connectivity() {
    log_info "Testing basic connectivity to $DOMAIN..."

    local health_url="https://$DOMAIN/health"
    local ready_url="https://$DOMAIN/ready"

    # Test health endpoint
    if curl -f -s -m $TIMEOUT "$health_url" >/dev/null; then
        log_success "Health endpoint accessible"
    else
        log_error "Health endpoint not accessible"
        return 1
    fi

    # Test ready endpoint
    if curl -f -s -m $TIMEOUT "$ready_url" >/dev/null; then
        log_success "Ready endpoint accessible"
    else
        log_error "Ready endpoint not accessible"
        return 1
    fi

    return 0
}

# Test SSE endpoint accessibility
test_sse_endpoint() {
    log_info "Testing SSE endpoint accessibility..."

    local sse_url="https://$DOMAIN/sse"

    # Test without authentication first
    local response_code
    response_code=$(curl -s -o /dev/null -w "%{http_code}" -m $TIMEOUT "$sse_url")

    if [[ "$response_code" == "401" ]]; then
        log_success "SSE endpoint requires authentication (401) - as expected"
        return 0
    elif [[ "$response_code" == "200" ]]; then
        log_warning "SSE endpoint accessible without authentication"
        return 0
    else
        log_error "SSE endpoint returned unexpected status: $response_code"
        return 1
    fi
}

# Test MCP tools listing via HTTP POST
test_mcp_list_tools() {
    log_info "Testing MCP list_tools functionality..."

    if [[ -z "$MCP_AUTH_KEY" ]]; then
        log_warning "Skipping list_tools test - MCP_AUTH_KEY not set"
        return 0
    fi

    local base_url="https://$DOMAIN"

    # Send list_tools request via HTTP POST
    local request_payload='{
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }'

    local response
    response=$(curl -s -m $TIMEOUT \
        -H "X-API-Key: $MCP_AUTH_KEY" \
        -H "Content-Type: application/json" \
        -X POST \
        -d "$request_payload" \
        "$base_url/" 2>/dev/null)

    if echo "$response" | jq -e '.result.tools[]' >/dev/null 2>&1; then
        local tool_count
        tool_count=$(echo "$response" | jq -r '.result.tools | length')
        log_success "MCP tools listed successfully - found $tool_count tools"

        # Show some tools
        log_debug "Available tools:"
        echo "$response" | jq -r '.result.tools[].name' | head -5 | sed 's/^/  - /'
        return 0
    else
        log_error "Failed to list MCP tools"
        log_debug "Response: $response"
        return 1
    fi
}

# Test MCP tool execution
test_mcp_tool_execution() {
    log_info "Testing MCP tool execution..."

    if [[ -z "$MCP_AUTH_KEY" ]]; then
        log_warning "Skipping tool execution test - MCP_AUTH_KEY not set"
        return 0
    fi

    local base_url="https://$DOMAIN"

    # Test list_hubspot_contacts tool
    local request_payload='{
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "list_hubspot_contacts",
            "arguments": {
                "limit": '$TEST_CONTACT_LIMIT'
            }
        }
    }'

    local response
    response=$(curl -s -m $TIMEOUT \
        -H "X-API-Key: $MCP_AUTH_KEY" \
        -H "Content-Type: application/json" \
        -X POST \
        -d "$request_payload" \
        "$base_url/" 2>/dev/null)

    if echo "$response" | jq -e '.result.content[0].text' >/dev/null 2>&1; then
        log_success "MCP tool execution successful - list_hubspot_contacts worked"

        # Show preview of result
        local preview
        preview=$(echo "$response" | jq -r '.result.content[0].text' | head -3)
        log_debug "Tool execution result preview:"
        echo "$preview" | sed 's/^/  /'
        return 0
    else
        log_error "Failed to execute MCP tool"
        log_debug "Response: $response"
        return 1
    fi
}

# Test authentication scenarios
test_authentication() {
    log_info "Testing authentication scenarios..."

    local base_url="https://$DOMAIN"

    # Test without authentication
    local response_code
    response_code=$(curl -s -o /dev/null -w "%{http_code}" -m $TIMEOUT "$base_url/")

    if [[ "$response_code" == "401" ]]; then
        log_success "Authentication required - endpoint properly secured"
    else
        log_warning "Authentication not required - endpoint may be insecure"
    fi

    # Test with wrong authentication
    if [[ -n "$MCP_AUTH_KEY" ]]; then
        response_code=$(curl -s -o /dev/null -w "%{http_code}" -m $TIMEOUT \
            -H "X-API-Key: wrong-key" "$base_url/")

        if [[ "$response_code" == "401" ]]; then
            log_success "Wrong authentication rejected - security working"
        else
            log_warning "Wrong authentication accepted - security issue"
        fi
    fi

    return 0
}

# Test SSE streaming
test_sse_streaming() {
    log_info "Testing SSE streaming functionality..."

    if [[ -z "$MCP_AUTH_KEY" ]]; then
        log_warning "Skipping SSE streaming test - MCP_AUTH_KEY not set"
        return 0
    fi

    local sse_url="https://$DOMAIN/sse"
    local temp_file=$(mktemp)

    log_info "Testing SSE stream for 10 seconds..."

    # Start SSE connection in background
    curl -s -m 15 \
        -H "X-API-Key: $MCP_AUTH_KEY" \
        -H "Accept: text/event-stream" \
        -H "Cache-Control: no-cache" \
        "$sse_url" > "$temp_file" &

    local curl_pid=$!
    sleep 10
    kill $curl_pid 2>/dev/null || true
    wait $curl_pid 2>/dev/null || true

    if [[ -s "$temp_file" ]]; then
        local line_count
        line_count=$(wc -l < "$temp_file")
        log_success "SSE streaming working - received $line_count lines"

        if [[ $line_count -gt 0 ]]; then
            log_debug "Sample SSE data:"
            head -n 5 "$temp_file" | sed 's/^/  /'
        fi
        rm -f "$temp_file"
        return 0
    else
        log_error "SSE streaming not working - no data received"
        rm -f "$temp_file"
        return 1
    fi
}

# Performance test
test_performance() {
    log_info "Testing performance..."

    if [[ -z "$MCP_AUTH_KEY" ]]; then
        log_warning "Skipping performance test - MCP_AUTH_KEY not set"
        return 0
    fi

    local base_url="https://$DOMAIN"
    local total_time=0
    local successful_requests=0
    local failed_requests=0

    log_info "Running 5 performance test requests..."

    for i in {1..5}; do
        local start_time=$(date +%s.%N)

        local request_payload='{
            "jsonrpc": "2.0",
            "id": '$i',
            "method": "tools/list",
            "params": {}
        }'

        if curl -s -m $TIMEOUT \
            -H "X-API-Key: $MCP_AUTH_KEY" \
            -H "Content-Type: application/json" \
            -X POST \
            -d "$request_payload" \
            "$base_url/" >/dev/null 2>&1; then
            ((successful_requests++))
        else
            ((failed_requests++))
        fi

        local end_time=$(date +%s.%N)
        local request_time=$(echo "$end_time - $start_time" | bc)
        total_time=$(echo "$total_time + $request_time" | bc)

        echo "  Request $i: ${request_time}s"
    done

    local avg_time
    avg_time=$(echo "scale=3; $total_time / 5" | bc)

    log_success "Performance test completed:"
    echo "  - Successful requests: $successful_requests/5"
    echo "  - Failed requests: $failed_requests/5"
    echo "  - Average response time: ${avg_time}s"

    return 0
}

# Run all tests
run_all_tests() {
    log_info "=== HubSpot MCP Server SSE Testing ==="
    log_info "Target: https://$DOMAIN"
    log_info "Namespace: $NAMESPACE"
    log_info "Timeout: ${TIMEOUT}s"
    echo ""

    local failed_tests=0

    # Test basic connectivity
    if ! test_basic_connectivity; then
        ((failed_tests++))
    fi
    echo ""

    # Test SSE endpoint
    if ! test_sse_endpoint; then
        ((failed_tests++))
    fi
    echo ""

    # Test authentication
    test_authentication
    echo ""

    # Test SSE streaming
    if ! test_sse_streaming; then
        ((failed_tests++))
    fi
    echo ""

    # Test MCP tools listing
    if ! test_mcp_list_tools; then
        ((failed_tests++))
    fi
    echo ""

    # Test MCP tool execution
    if ! test_mcp_tool_execution; then
        ((failed_tests++))
    fi
    echo ""

    # Performance test
    test_performance
    echo ""

    # Summary
    if [[ $failed_tests -eq 0 ]]; then
        log_success "=== All SSE MCP tests passed! ✅ ==="
        log_info "Your HubSpot MCP Server SSE endpoint is working correctly"
        return 0
    else
        log_error "=== $failed_tests test(s) failed! ❌ ==="
        log_info "Please check the configuration and try again"
        return 1
    fi
}

# Check prerequisites
check_prerequisites() {
    local missing_tools=()

    if ! command -v curl &> /dev/null; then
        missing_tools+=("curl")
    fi

    if ! command -v jq &> /dev/null; then
        missing_tools+=("jq")
    fi

    if ! command -v bc &> /dev/null; then
        missing_tools+=("bc")
    fi

    if [[ ${#missing_tools[@]} -ne 0 ]]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log_info "Please install missing tools:"
        log_info "  Ubuntu/Debian: sudo apt-get install ${missing_tools[*]}"
        log_info "  macOS: brew install ${missing_tools[*]}"
        exit 1
    fi
}

# Usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Test HubSpot MCP Server SSE functionality"
    echo ""
    echo "Options:"
    echo "  -d, --domain DOMAIN        Domain to test (default: from environment)"
    echo "  -k, --auth-key KEY         MCP authentication key (default: from environment)"
    echo "  -n, --namespace NS         Kubernetes namespace (default: mcp-hubspot)"
    echo "  -t, --timeout SECONDS      Timeout for requests (default: 30)"
    echo "  -l, --contact-limit N      Contact limit for test (default: 5)"
    echo "  -h, --help                 Show this help message"
    echo ""
    echo "Environment variables:"
    echo "  DOMAIN                     Target domain"
    echo "  MCP_AUTH_KEY              Authentication key"
    echo "  NAMESPACE                 Kubernetes namespace"
    echo ""
    echo "Examples:"
    echo "  $0                                           # Use environment configuration"
    echo "  $0 -d mcp.example.com -k mykey              # Test specific domain with key"
    echo "  $0 -d mcp.example.com -k mykey -l 10        # Test with 10 contacts limit"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--domain)
            DOMAIN="$2"
            shift 2
            ;;
        -k|--auth-key)
            MCP_AUTH_KEY="$2"
            shift 2
            ;;
        -n|--namespace)
            NAMESPACE="$2"
            shift 2
            ;;
        -t|--timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        -l|--contact-limit)
            TEST_CONTACT_LIMIT="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Main execution
check_prerequisites
load_environment
run_all_tests
