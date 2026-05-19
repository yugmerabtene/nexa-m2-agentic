---
name: cours-agentic-dev
description: Utilise UNIQUEMENT quand on travaille sur le cours M2 Nexa Agentic Dev. Contient la structure, les conventions, et les références du cours.
---

# Skill: cours-agentic-dev

Utiliser UNIQUEMENT quand on édite, crée ou révise le contenu du cours Agentic Development M2 Nexa.

## Structure du cours

```
nexa-m2-agentic/
├── opencode.json           ← Configuration opencode avec équipe de dev
├── AGENTS.md               ← Instructions principales
├── GLOSSARY.md             ← Glossaire bilingue FR/EN
├── syllabus/README.md      ← Syllabus complet
├── lectures/               ← Cours magistraux (CM)
│   ├── 01-llm-architectures-agentic.md
│   ├── 02-context-window-engineering.md
│   ├── 03-memoire-systemes-agentiques.md
│   ├── 04-mcp-protocol.md
│   ├── 05-a2a-protocol.md
│   ├── 06-github-agents-platform.md
│   ├── 07-langgraph-framework.md
│   ├── 08-crewai-autogen-comparison.md
│   ├── 09-agentic-rag-knowledge.md
│   ├── 10-finetuning-rl-agents.md
│   ├── 11-optimisation-memoire-contexte.md
│   ├── 12-benchmarks-evaluation.md
│   ├── 13-deploiement-production.md
│   └── 14-frontieres-futur.md
├── lab/                   ← Lab unique et complet
│   ├── README.md          ← Guide du lab
│   ├── code/              ← Code source des exemples
│   └── tests/             ← Tests de validation
├── projects/README.md     ← Projets
├── research/              ← Recherche et veille
└── resources/             ← Bibliographie

.opencode/
├── agents/                ← Équipe de sous-agents
│   ├── project-manager.md
│   ├── scrum-master.md
│   ├── software-engineer.md
│   ├── devops-engineer.md
│   ├── cybersecurity-engineer.md
│   └── qa-engineer.md
└── skills/
    └── cours-agentic-dev/SKILL.md
```

## Conventions

- **Langue des cours:** Français
- **Langue du code:** Anglais (noms, commentaires, variables)
- **Format:** Markdown GFM
- **Blocs de code:** ```python, ```bash, ```json, ```yaml
- **Tables:** Pipes GFM `|`
- **Agent par défaut:** scrum-master
- **Modèle:** `opencode/big-pickle` (ou autre modèle opencode disponible)

## Hiérarchie des rôles

```
project-manager ← vision, roadmap, références, qualité globale
       │
       └── scrum-master ← exécution agile, sprints, coordination quotidienne
              │
               ├── software-engineer    ← développement full-stack
               ├── devops-engineer     ← CI/CD, workflows, config
              ├── cybersecurity-engineer ← audit sécurité (read-only)
              └── qa-engineer         ← tests, validation, benchmarks
```

## Règles importantes

1. Les sous-agents sont utilisés via l'outil `task` — chaque tâche technique est déléguée
2. Le QA-engineer valide TOUT exemple de code avant merge
3. Le cybersecurity-engineer audite en read-only
4. Les exemples doivent TOUS fonctionner avec opencode (big-pickle ou autre)
5. Aucune dépendance à des APIs payantes (OpenAI, Anthropic) dans les exemples
6. Aucun exemple ne dépend d'API externe (OpenAI, Anthropic) ou de frameworks LLM externes — tout doit pouvoir s'exécuter avec les outils opencode natifs
