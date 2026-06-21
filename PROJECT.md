# Projet Fil Rouge — AI Developer Assistant


---

## Présentation du projet

Vous allez construire un **AI Developer Assistant** — un système agentique complet capable d'aider un développeur dans ses tâches quotidiennes : revue de code, recherche de documentation, gestion de mémoire, exécution de scripts, et collaboration multi-agents.

Ce projet est le fil rouge du cours M2 Nexa Agentic Development. Chaque séance construit une pièce du système.

---

## Objectifs pédagogiques

À la fin du cours, vous aurez construit un système qui :

1. **Comprend les requêtes** en langage naturel
2. **Accède à des outils** via le protocole MCP
3. **Mémorise le contexte** entre les sessions
4. **Collabore avec d'autres agents** via A2A
5. **S'intègre à GitHub** pour la revue de code
6. **Utilise des frameworks** d'orchestration (LangGraph, CrewAI)
7. **Effectue du RAG** pour accéder à la documentation
8. **Est déployé en production** avec CI/CD et monitoring

---

## Architecture cible

```
                    ┌──────────────────────────────────┐
                    │       opencode CLI                │
                    │    (opencode/big-pickle)          │
                    └────────────┬─────────────────────┘
                                 │
                    ┌────────────▼─────────────────────┐
                    │    opencode.json + AGENTS.md      │
                    │    ┌─────────────────────────┐   │
                    │    │ Équipe d'agents          │   │
                    │    │ - scrum-master           │   │
                    │    │ - software-engineer      │   │
                    │    │ - devops-engineer        │   │
                    │    │ - qa-engineer            │   │
                    │    │ - cybersecurity-engineer │   │
                    │    └─────────────────────────┘   │
                    └────────────┬─────────────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
     ┌────▼──────┐        ┌─────▼──────┐        ┌─────▼──────┐
     │ MCP Server │        │ Memory     │        │ A2A Agent  │
     │ (Python)   │        │ (JSON/FS)  │        │ (Remote)   │
     │ tools:     │        │            │        │            │
     │  read_file │        │ sliding    │        │ Agent Card │
     │  search   │        │ window     │        │ Task Mgmt  │
     │  run_code │        │ compaction │        │            │
     └────────────┘        └────────────┘        └────────────┘
                                 │
                    ┌────────────▼─────────────────────┐
                    │     CI/CD Pipeline                │
                    │     GitHub Actions                │
                    │     lint → test → build → deploy  │
                    └──────────────────────────────────┘
```

---

## Cahier des charges par séance

### Séance 1-3 : Fondations

| Séance | Livrable | Description |
|--------|----------|-------------|
| S1 | `seance-01/` | Environnement configuré, premier agent opérationnel |
| S2 | `seance-02/` | Compréhension des tokens et du contexte |
| S3 | `seance-03/` | Mémoire persistante (JSON + sliding window) |

### Séance 4-6 : Protocoles

| Séance | Livrable | Description |
|--------|----------|-------------|
| S4 | `seance-04/` | Serveur MCP avec 3+ tools |
| S5 | `seance-05/` | Agent A2A avec Agent Card |
| S6 | `seance-06/` | Custom Agent GitHub avec hooks |

### Séance 7-9 : Orchestration

| Séance | Livrable | Description |
|--------|----------|-------------|
| S7 | `seance-07/` | Workflow LangGraph fonctionnel |
| S8 | `seance-08/` | Équipe CrewAI configurée |
| S9 | `seance-09/` | Backend RAG avec vector store |

### Séance 10-13 : Production

| Séance | Livrable | Description |
|--------|----------|-------------|
| S10 | `seance-10/` | Pipeline de fine-tuning |
| S11 | `seance-11/` | Configuration d'optimisation mémoire |
| S12 | `seance-12/` | Évaluateur de benchmark |
| S13 | `seance-13/` | Pipeline CI/CD complète |

### Séance 14 : Projet final

| Séance | Livrable | Description |
|--------|----------|-------------|
| S14 | `projet-final/` | Architecture complète documentée et présentée |

---

## Spécifications techniques

### Contraintes

- **Aucune API LLM payante** : utiliser uniquement `opencode/big-pickle`
- **Python 3.10+** : version minimale
- **Stockage local** : SQLite, JSON, fichiers (pas de cloud)
- **Open source** : toutes les dépendances doivent être open source
- **Testable** : chaque composant doit avoir des tests

### Structure du code

```
agentic-labs/
├── seance-01/
│   ├── opencode.json
│   ├── AGENTS.md
│   └── .opencode/
│       └── agents/
├── seance-02/
│   └── ...
├── ...
├── seance-14/
│   └── projet-final/
│       ├── README.md
│       ├── src/
│       ├── tests/
│       └── .github/
│           └── workflows/
└── ...
```

### Qualité du code

- **Linting** : `ruff` pour le style
- **Typage** : type hints Python
- **Tests** : `pytest` avec couverture > 80%
- **Documentation** : docstrings et commentaires en français
- **Sécurité** : pas de secrets dans le code

---

## Critères d'évaluation

| Critère | Poids | Description |
|---------|-------|-------------|
| Fonctionnalité | 30% | Le système fonctionne comme spécifié |
| Qualité du code | 20% | Code propre, typé, documenté |
| Tests | 20% | Couverture > 80%, tests pertinents |
| Architecture | 15% | Séparation des responsabilités, extensibilité |
| Documentation | 15% | README, commentaires, présentations |

---

## Livrables finaux

### 1. Code source

- Tous les TPs des séances 1-13
- Projet final intégré dans `seance-14/projet-final/`
- Tests unitaires et d'intégration
- Configuration opencode et agents

### 2. Documentation

- README.md du projet final
- Documentation d'architecture
- Guide d'installation et d'utilisation
- Rapport d'analyse des choix architecturaux

### 3. Présentation

- Démo en live (5-10 minutes)
- Slides ou document de présentation
- Réponse aux questions du jury

---

## Planning suggéré

| Semaine | Séances | Travail attendu |
|---------|---------|-----------------|
| 1-2 | S1-S3 | Fondations + mémoire |
| 3-4 | S4-S6 | Protocoles MCP/A2A + GitHub |
| 5-6 | S7-S9 | Frameworks + RAG |
| 7-8 | S10-S13 | Optimisation + production |
| 9 | S14 | Projet final + présentation |

---

## Ressources

- [README du cours](README.md)
- [Installations](INSTALL.md)
- [Checklists](CHECKLIST.md)
- [Documentation opencode](https://opencode.ai)
- [MCP Specification](https://modelcontextprotocol.io)
- [A2A Protocol](https://a2aprotocol.org)

---

**Auteur :** yugmerabtene
