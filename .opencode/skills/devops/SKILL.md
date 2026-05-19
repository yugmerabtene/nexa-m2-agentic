---
name: devops
description: Compétences DevOps — CI/CD, GitHub Actions, infrastructure, scripts d'automatisation. Skill du devops-engineer.
---

# Skill: devops

## Périmètre
- Pipelines CI/CD (GitHub Actions)
- Configuration et maintenance des workflows
- Scripts d'automatisation (installation, backup, cleanup)
- Gestion de l'environnement local et des dépendances
- Sécurité des pipelines et des secrets

## Pipeline CI/CD de référence
```yaml
jobs:
  lint:      # ruff check, mypy
  test:      # pytest -v
  security:  # audit de sécurité
  release:   # GitHub Release (optionnel)
```

## Bonnes pratiques
1. Un seul fichier workflow par pipeline logique
2. Secrets via GitHub Secrets (jamais hardcodés)
3. Timeout max 15 min par job
4. Artifacts conservés 7 jours
5. Badges de status à jour dans le README

## Checklist DevOps
- [ ] Le workflow CI est fonctionnel et testé
- [ ] Les dépendances sont dans `requirements.txt`
- [ ] Les secrets sont dans GitHub Secrets
- [ ] La config opencode.json est valide JSON
- [ ] Les badges CI sont à jour
