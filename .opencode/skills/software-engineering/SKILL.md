---
name: software-engineering
description: Compétences en génie logiciel — Python, architecture, CLI, APIs, bonnes pratiques de code. Skill du software-engineer.
---

# Skill: software-engineering

## Périmètre
- Développement Python (3.11+)
- Architecture logicielle et design patterns
- CLI et APIs (argparse, FastAPI)
- Intégrations MCP et protocoles agents
- Qualité de code et tests

## Conventions de code
- Python 3.11+ — typing, dataclasses, pattern matching
- Style: PEP 8 (via ruff)
- Imports: stdlib → tiers → local (séparés par ligne vide)
- Noms: `snake_case` pour variables/fonctions, `PascalCase` pour classes
- Docstrings: Google style
- Tests: pytest dans `tests/`

## Architecture
```
src/
├── core/          ← Logique métier, modèles
├── cli/           ← Point d'entrée CLI
├── api/           ← Endpoints API
├── mcp/           ← Serveurs MCP
└── utils/         ← Utilitaires partagés
```

## Checklist qualité
- [ ] Typage Python (type hints) partout
- [ ] Pas de dépendances inutiles
- [ ] Tests unitaires pour chaque module
- [ ] `__main__` exécutable pour chaque script
- [ ] Gestion d'erreurs (try/except explicites)
- [ ] Pas de secrets hardcodés
- [ ] Code commenté en anglais
