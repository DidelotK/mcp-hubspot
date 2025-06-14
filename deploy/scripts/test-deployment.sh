#!/bin/bash
set -euo pipefail

# Configuration
DOMAIN="${DOMAIN:-mcp-hubspot.yourdomain.com}"
NAMESPACE="${NAMESPACE:-production}"
TIMEOUT="${TIMEOUT:-300}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Test functions
test_health_endpoint() {
    log_info "Testing health endpoint..."
    local url="https://${DOMAIN}/health"
    
    if curl -f -s "$url" | jq -e '.status == "healthy"' > /dev/null; then
        log_success "Health endpoint is responding correctly"
        return 0
    else
        log_error "Health endpoint is not responding correctly"
        return 1
    fi
}

test_readiness_endpoint() {
    log_info "Testing readiness endpoint..."
    local url="https://${DOMAIN}/ready"
    
    if curl -f -s "$url" | jq -e '.status == "ready"' > /dev/null; then
        log_success "Readiness endpoint is responding correctly"
        return 0
    else
        log_error "Readiness endpoint is not responding correctly"
        return 1
    fi
}

test_kubernetes_resources() {
    log_info "Testing Kubernetes resources..."
    
    # Check deployment
    if kubectl get deployment hubspot-mcp-server -n "$NAMESPACE" &>/dev/null; then
        log_success "Deployment exists"
    else
        log_error "Deployment not found"
        return 1
    fi
    
    # Check pods
    local ready_pods
    ready_pods=$(kubectl get pods -n "$NAMESPACE" -l app.kubernetes.io/name=hubspot-mcp-server --field-selector=status.phase=Running --no-headers | wc -l)
    
    if [ "$ready_pods" -gt 0 ]; then
        log_success "$ready_pods pod(s) running"
    else
        log_error "No pods running"
        return 1
    fi
    
    # Check service
    if kubectl get service hubspot-mcp-server -n "$NAMESPACE" &>/dev/null; then
        log_success "Service exists"
    else
        log_error "Service not found"
        return 1
    fi
    
    # Check ingress
    if kubectl get ingress -n "$NAMESPACE" | grep -q hubspot-mcp; then
        log_success "Ingress configured"
    else
        log_error "Ingress not found"
        return 1
    fi
    
    return 0
}

test_ssl_certificate() {
    log_info "Testing SSL certificate..."
    
    if echo | openssl s_client -servername "$DOMAIN" -connect "$DOMAIN:443" 2>/dev/null | openssl x509 -noout -issuer | grep -q "Let's Encrypt"; then
        log_success "SSL certificate is valid (Let's Encrypt)"
        return 0
    else
        log_warning "SSL certificate may not be from Let's Encrypt or not yet ready"
        return 1
    fi
}

test_mcp_sse_endpoint() {
    log_info "Testing MCP SSE endpoint..."
    local url="https://${DOMAIN}/sse"
    
    # Test if SSE endpoint accepts connections
    if curl -I -s "$url" | grep -q "200\|404\|405"; then
        log_success "SSE endpoint is accessible"
        return 0
    else
        log_error "SSE endpoint is not accessible"
        return 1
    fi
}

run_performance_test() {
    log_info "Running basic performance test..."
    local url="https://${DOMAIN}/health"
    
    log_info "Testing response times (10 requests)..."
    for i in {1..10}; do
        local response_time
        response_time=$(curl -o /dev/null -s -w "%{time_total}" "$url")
        echo "Request $i: ${response_time}s"
    done
    
    log_success "Performance test completed"
}

check_logs() {
    log_info "Checking application logs..."
    
    # Get recent logs
    local logs
    logs=$(kubectl logs -n "$NAMESPACE" -l app.kubernetes.io/name=hubspot-mcp-server --tail=20 --since=5m)
    
    if echo "$logs" | grep -q "ERROR\|CRITICAL\|Exception"; then
        log_warning "Found error messages in logs:"
        echo "$logs" | grep "ERROR\|CRITICAL\|Exception"
    else
        log_success "No critical errors found in recent logs"
    fi
}

# Main test function
run_tests() {
    log_info "Starting deployment tests for $DOMAIN..."
    local failed_tests=0
    
    # Test Kubernetes resources
    if ! test_kubernetes_resources; then
        ((failed_tests++))
    fi
    
    # Wait a bit for endpoints to be ready
    log_info "Waiting 30 seconds for endpoints to be ready..."
    sleep 30
    
    # Test health endpoint
    if ! test_health_endpoint; then
        ((failed_tests++))
    fi
    
    # Test readiness endpoint
    if ! test_readiness_endpoint; then
        ((failed_tests++))
    fi
    
    # Test SSL certificate
    if ! test_ssl_certificate; then
        ((failed_tests++))
    fi
    
    # Test MCP SSE endpoint
    if ! test_mcp_sse_endpoint; then
        ((failed_tests++))
    fi
    
    # Check logs
    check_logs
    
    # Run performance test
    run_performance_test
    
    # Summary
    if [ $failed_tests -eq 0 ]; then
        log_success "All tests passed! ✅"
        log_info "Your HubSpot MCP Server is ready for production use at: https://$DOMAIN"
        return 0
    else
        log_error "$failed_tests test(s) failed! ❌"
        log_info "Please check the logs and configuration"
        return 1
    fi
}

# Check prerequisites
check_prerequisites() {
    local missing_tools=()
    
    if ! command -v kubectl &> /dev/null; then
        missing_tools+=("kubectl")
    fi
    
    if ! command -v curl &> /dev/null; then
        missing_tools+=("curl")
    fi
    
    if ! command -v jq &> /dev/null; then
        missing_tools+=("jq")
    fi
    
    if ! command -v openssl &> /dev/null; then
        missing_tools+=("openssl")
    fi
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log_info "Please install the missing tools and try again"
        exit 1
    fi
}

# Usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -d, --domain DOMAIN     Domain to test (default: mcp-hubspot.yourdomain.com)"
    echo "  -n, --namespace NS      Kubernetes namespace (default: production)"
    echo "  -t, --timeout SECONDS   Timeout for tests (default: 300)"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Test with defaults"
    echo "  $0 -d mcp.example.com -n prod       # Test specific domain and namespace"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--domain)
            DOMAIN="$2"
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
run_tests 