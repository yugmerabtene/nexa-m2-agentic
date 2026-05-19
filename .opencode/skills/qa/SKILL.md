---
name: qa
description: Compétences en assurance qualité — tests, validation, benchmarks, linting. Skill du qa-engineer.
---

# Skill: qa

## Périmètre
- Tests unitaires et d'intégration (pytest)
- Validation de code (linting, typing)
- Benchmarks de performance
- Revue de qualité et reporting
- Vérification de cohérence documentation/code

## Structure de tests
```
tests/
├── unit/           ← Tests unitaires par module
├── integration/    ← Tests d'intégration
├── fixtures/       ← Données de test
└── conftest.py     ← Fixtures partagées
```

## Checklist QA
- [ ] Chaque module a des tests unitaires
- [ ] Les imports sont tous valides et disponibles
- [ ] Les exécutables ont un `__main__` fonctionnel
- [ ] Le linting passe (ruff, mypy)
- [ ] Les URLs et endpoints sont valides
- [ ] Pas de références à des APIs payantes
- [ ] La documentation est cohérente avec le code
- [ ] Les benchmarks sont reproductibles

## Commandes de validation
```bash
ruff check src/                          # Linting
mypy src/                                # Typing
pytest tests/ -v --junitxml=report.xml   # Tests
```

## Règles
- Tester avec opencode (big-pickle ou modèle disponible)
- Reporter les problèmes avec: fichier, ligne, gravité, suggestion
- Les tests précèdent le code (TDD si possible)
- Les benchmarks doivent être reproductibles
