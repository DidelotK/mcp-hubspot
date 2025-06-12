#!/bin/bash
# Script d'installation des hooks Git pour la qualité de code

echo "🔧 Installation des hooks Git..."

# Créer le hook pre-commit
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Hook pre-commit pour vérifier la qualité de code

echo "🔍 Vérification de la qualité de code avant commit..."

# Vérifier que uv est installé
if ! command -v uv &> /dev/null; then
    echo "❌ uv n'est pas installé. Installez-le avec: pip install uv"
    exit 1
fi

# Exécuter les vérifications rapides
echo "🔧 Vérification du formatage..."
if ! uv run black --check src/ main.py tests/ scripts/ 2>/dev/null; then
    echo "❌ Le code n'est pas formaté correctement."
    echo "💡 Exécutez: uv run black src/ main.py tests/ scripts/"
    exit 1
fi

echo "📋 Vérification des imports..."
if ! uv run isort --check-only src/ main.py tests/ scripts/ 2>/dev/null; then
    echo "❌ Les imports ne sont pas triés correctement."
    echo "💡 Exécutez: uv run isort src/ main.py tests/ scripts/"
    exit 1
fi

echo "🔍 Analyse statique rapide..."
if ! uv run flake8 src/ main.py tests/ scripts/ 2>/dev/null; then
    echo "❌ Des problèmes de style ont été détectés."
    echo "💡 Exécutez: uv run flake8 src/ main.py tests/ scripts/"
    exit 1
fi

echo "✅ Vérifications de qualité passées !"
EOF

# Rendre le hook exécutable
chmod +x .git/hooks/pre-commit

# Créer le hook pre-push pour les tests
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
# Hook pre-push pour exécuter les tests

echo "🧪 Exécution des tests avant push..."

if ! uv run python -m pytest --tb=short -q; then
    echo "❌ Les tests ont échoué. Push annulé."
    exit 1
fi

echo "✅ Tous les tests passent !"
EOF

# Rendre le hook exécutable
chmod +x .git/hooks/pre-push

echo "✅ Hooks Git installés avec succès !"
echo ""
echo "📋 Hooks installés:"
echo "  - pre-commit: Vérification du formatage et du style"
echo "  - pre-push: Exécution des tests"
echo ""
echo "💡 Pour désactiver temporairement les hooks:"
echo "  git commit --no-verify"
echo "  git push --no-verify" 