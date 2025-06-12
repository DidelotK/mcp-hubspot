#!/usr/bin/env python3
"""
Script pour vérifier la qualité du code et générer un rapport
pour les commentaires de Pull Request.
"""

import subprocess
import sys
from typing import List, Tuple


def run_command(cmd: List[str]) -> Tuple[int, str, str]:
    """Exécute une commande et retourne le code de sortie, stdout et stderr."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)


def check_black() -> Tuple[bool, str]:
    """Vérifie le formatage avec Black."""
    print("🔍 Vérification du formatage avec Black...")

    code, stdout, stderr = run_command(
        ["black", "--check", "--diff", "src/", "main.py", "tests/"]
    )

    if code == 0:
        return True, "✅ **Black**: Code correctement formaté"
    else:
        return False, f"❌ **Black**: Code mal formaté\n```diff\n{stdout}\n```"


def check_isort() -> Tuple[bool, str]:
    """Vérifie l'organisation des imports avec isort."""
    print("🔍 Vérification des imports avec isort...")

    code, stdout, stderr = run_command(
        ["isort", "--check", "--diff", "src/", "main.py", "tests/"]
    )

    if code == 0:
        return True, "✅ **isort**: Imports correctement organisés"
    else:
        return False, f"❌ **isort**: Imports mal organisés\n```diff\n{stdout}\n```"


def check_flake8() -> Tuple[bool, str]:
    """Vérifie la conformité PEP 8 avec flake8."""
    print("🔍 Vérification PEP 8 avec flake8...")

    code, stdout, stderr = run_command(["flake8", "src/", "main.py", "tests/"])

    if code == 0:
        return True, "✅ **flake8**: Aucune violation PEP 8"
    else:
        issues = stdout.strip()
        return False, f"❌ **flake8**: Violations PEP 8 détectées\n```\n{issues}\n```"


def check_mypy() -> Tuple[bool, str]:
    """Vérifie les types avec mypy."""
    print("🔍 Vérification des types avec mypy...")

    code, stdout, stderr = run_command(["mypy", "src/", "main.py"])

    if code == 0:
        return True, "✅ **mypy**: Types correctement définis"
    else:
        issues = stdout.strip()
        return False, f"❌ **mypy**: Erreurs de typage\n```\n{issues}\n```"


def main():
    """Fonction principale pour exécuter toutes les vérifications."""
    print("🚀 Démarrage des vérifications de qualité du code...\n")

    all_checks = [
        ("Black", check_black),
        ("isort", check_isort),
        ("flake8", check_flake8),
        ("mypy", check_mypy),
    ]

    results = []
    all_passed = True

    for name, check_func in all_checks:
        try:
            passed, message = check_func()
            results.append(message)
            if not passed:
                all_passed = False
        except Exception as e:
            results.append(f"❌ **{name}**: Erreur lors de l'exécution: {str(e)}")
            all_passed = False

        print()

    # Génération du rapport final
    print("📋 Rapport de qualité du code:")
    print("=" * 50)

    if all_passed:
        report = "## ✅ Vérification de la qualité du code - SUCCÈS\n\n"
        report += "Toutes les vérifications de qualité du code ont réussi !\n\n"
    else:
        report = "## ❌ Vérification de la qualité du code - ÉCHEC\n\n"
        report += "Certaines vérifications de qualité ont échoué. Veuillez corriger les problèmes suivants :\n\n"

    for result in results:
        report += f"{result}\n\n"
        print(result)

    if not all_passed:
        report += "### 🔧 Comment corriger:\n"
        report += "```bash\n"
        report += "# Formater automatiquement le code\n"
        report += "uv run black src/ main.py tests/\n"
        report += "uv run isort src/ main.py tests/\n\n"
        report += "# Vérifier les problèmes restants\n"
        report += "uv run flake8 src/ main.py tests/\n"
        report += "uv run mypy src/ main.py\n"
        report += "```\n"

    # Sauvegarder le rapport pour GitHub
    with open("lint_report.md", "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n📄 Rapport sauvegardé dans lint_report.md")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
