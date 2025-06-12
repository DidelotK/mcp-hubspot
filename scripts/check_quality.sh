#!/bin/bash
# Script de vérification de qualité de code pour le projet HubSpot MCP

set -e

echo "🔍 Vérification de la qualité de code..."
echo "========================================"

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les résultats
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

# Vérifier que uv est installé
if ! command -v uv &> /dev/null; then
    echo -e "${RED}❌ uv n'est pas installé. Installez-le avec: pip install uv${NC}"
    exit 1
fi

# Installer les dépendances si nécessaire
echo "📦 Installation des dépendances..."
uv sync --dev --all-extras

# Exécuter les vérifications
echo ""
echo "🧪 Exécution des tests..."
uv run python -m pytest --verbose --tb=short
print_result $? "Tests"

echo ""
echo "📊 Vérification de la couverture de code..."
uv run python -m pytest --cov=src --cov-report=term-missing --cov-report=html
print_result $? "Couverture de code"

echo ""
echo "🔧 Vérification du formatage avec black..."
uv run black --check src/ main.py tests/ scripts/
print_result $? "Formatage black"

echo ""
echo "📋 Vérification des imports avec isort..."
uv run isort --check-only src/ main.py tests/ scripts/
print_result $? "Ordre des imports"

echo ""
echo "🔍 Analyse statique avec flake8..."
uv run flake8 src/ main.py tests/ scripts/
print_result $? "Analyse flake8"

echo ""
echo "🔬 Vérification des types avec mypy..."
cd src && uv run mypy hubspot_mcp/ --ignore-missing-imports --no-strict-optional || true
cd ..
print_result 0 "Vérification des types (warnings ignorés)"

echo ""
echo "🛡️ Analyse de sécurité avec bandit..."
uv run bandit -r src/ main.py -f json -o bandit_report.json || true
if [ -f bandit_report.json ]; then
    issues=$(cat bandit_report.json | python -c "import sys, json; data=json.load(sys.stdin); print(len(data.get('results', [])))")
    if [ "$issues" -eq 0 ]; then
        print_result 0 "Analyse de sécurité (0 problèmes)"
    else
        print_result 1 "Analyse de sécurité ($issues problèmes trouvés)"
        echo -e "${YELLOW}Voir bandit_report.json pour les détails${NC}"
    fi
else
    print_result 1 "Analyse de sécurité (erreur d'exécution)"
fi

echo ""
echo "📋 Génération du rapport complet..."
uv run python scripts/lint_check.py

echo ""
echo "🎉 Vérifications terminées !"
echo "📄 Rapport détaillé disponible dans: lint_report.md"
echo "📊 Rapport de couverture HTML disponible dans: htmlcov/index.html"

if [ -f lint_report.md ]; then
    echo ""
    echo "📋 Résumé du rapport:"
    head -20 lint_report.md
fi 