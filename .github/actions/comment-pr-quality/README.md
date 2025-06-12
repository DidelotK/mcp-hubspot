# Comment PR with Code Quality Report

Action GitHub composite pour poster ou mettre à jour automatiquement des commentaires sur les Pull Requests avec des rapports de qualité de code.

## 📋 Description

Cette action lit un rapport de qualité de code (au format Markdown) et :
- Poste un nouveau commentaire sur la PR si aucun commentaire de qualité n'existe
- Met à jour le commentaire existant s'il y en a déjà un
- Gère intelligemment les erreurs et les cas edge

## 🚀 Utilisation

### Exemple basique

```yaml
- name: Comment PR with code quality report
  uses: ./.github/actions/comment-pr-quality
  with:
    report-path: 'lint_report.md'
    github-token: ${{ secrets.GITHUB_TOKEN }}
```

### Exemple avec génération de rapport

```yaml
- name: Run code quality checks
  run: |
    python scripts/lint_check.py

- name: Comment PR with quality report
  if: always()  # Commenter même si les checks échouent
  uses: ./.github/actions/comment-pr-quality
  with:
    report-path: 'lint_report.md'
    github-token: ${{ secrets.GITHUB_TOKEN }}
```

## 📥 Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `report-path` | Chemin vers le fichier rapport (format Markdown) | ✅ | `lint_report.md` |
| `github-token` | Token GitHub pour l'accès API | ✅ | `${{ github.token }}` |

## 🎯 Fonctionnalités

### ✅ Gestion intelligente des commentaires
- Détecte automatiquement les commentaires existants
- Met à jour plutôt que de créer des doublons
- Utilise l'API GitHub optimisée pour les commentaires

### 🛡️ Robustesse
- Gère les cas où le rapport n'existe pas
- Messages d'erreur clairs
- Pas de plantage si le fichier est manquant

### 🔄 Mise à jour automatique
- Ajoute un footer informatif sur la génération automatique
- Mode `replace` pour éviter l'accumulation de contenu

## 🔧 Dépendances

Cette action utilise les actions GitHub suivantes :
- `peter-evans/find-comment@v3` - Pour trouver les commentaires existants
- `peter-evans/create-or-update-comment@v4` - Pour créer/mettre à jour les commentaires

## 📝 Format du rapport attendu

Le fichier rapport doit être au format Markdown. Exemple :

```markdown
## ✅ Vérification de la qualité du code - SUCCÈS

Toutes les vérifications ont réussi !

✅ **Black**: Code correctement formaté
✅ **isort**: Imports bien organisés
✅ **flake8**: Aucune violation PEP 8
✅ **mypy**: Types correctement définis
```

## 🎨 Personnalisation

Pour personnaliser cette action pour votre projet :

1. Modifiez le `body-includes` dans l'étape `Find existing quality comment`
2. Ajustez le format du footer dans `Create or update PR comment`
3. Adaptez les messages d'erreur selon vos besoins

## 🚦 Codes de sortie

- `0` - Succès (commentaire posté/mis à jour)
- `1` - Erreur (impossible de lire le rapport)

## 🔗 Intégration avec d'autres workflows

Cette action peut être utilisée dans n'importe quel workflow qui génère des rapports de qualité de code :

- Tests unitaires avec couverture
- Analyse de sécurité
- Audits de dépendances
- Vérifications de performance

Il suffit de générer un rapport au format Markdown et d'utiliser cette action pour le poster sur la PR ! 