# Équipe de Développement

Ce répertoire est un projet standard utilisant opencode avec une équipe d'agents spécialisés configurée dans `opencode.json`.

## Équipe

| Agent | Rôle | Mode |
|-------|------|------|
| `project-manager` | Chef de projet global — vision, roadmap, références, coordination | **primary** |
| `scrum-master` | Chef de projet — planifie, coordonne, valide | **primary** (défaut) |
| `software-engineer` | Développement logiciel (backend, frontend, API, CLI) | subagent |
| `devops-engineer` | CI/CD, GitHub Actions, workflows, config | subagent |
| `cybersecurity-engineer` | Audit sécurité, OWASP LLM, permissions | subagent |
| `qa-engineer` | Tests, validation, benchmarks | subagent |

## Structure du projet

```
/
├── opencode.json               ← Configuration avec équipe de dev
├── AGENTS.md                   ← vous êtes ici
├── README.md                   ← Page d'accueil du cours
├── INSTALL.md                  ← Guide d'installation
├── PROJECT.md                  ← Projet fil rouge
├── CHECKLIST.md                ← Checklists de validation
├── STATUS.md                   ← Statut du projet
├── .opencode/
│   ├── agents/                 ← Définitions des agents
│   └── skills/                 ← Skills métier (domaine du projet)
├── lectures/                   ← 14 séances de cours
├── lab/                        ← Laboratoires pratiques
│   ├── code/                   ← Code des labs
│   └── tests/                  ← Tests des labs
├── syllabus/                   ← Syllabus et templates
├── resources/                  ← Références et bibliographie
├── research/                   ← Notes de recherche
└── projects/                   ← Idées de projets
```

## Conventions

1. **Langue:** Communication en français, code et références techniques en anglais
2. **Format:** Markdown (GFM) — lisible en CLI et rendu GitHub
3. **Code:** Blocs ```python, ```bash, ```json, ```yaml
4. **Modèle:** `opencode/big-pickle`
5. **Pas d'APIs payantes:** Aucune dépendance à OpenAI/Anthropic dans les exemples

## Hiérarchie des rôles

```
project-manager ← vision, roadmap, références, qualité globale
       │
       └── scrum-master ← exécution agile, sprints, coordination quotidienne
              │
              ├── software-engineer     ← développement logiciel (full-stack)
              ├── devops-engineer       ← CI/CD, workflows, config
              ├── cybersecurity-engineer ← audit sécurité (read-only)
              └── qa-engineer           ← tests, validation, benchmarks
```

## Workflow

1. Le `project-manager` définit la vision et la roadmap globale
2. Le `scrum-master` décompose en sprints et user stories
3. Les tâches techniques sont déléguées aux sous-agents via `task`
4. Le `cybersecurity-engineer` audite en read-only
5. Le `qa-engineer` valide tout le code
6. Le `scrum-master` consolide et rapporte au `project-manager`
7. Le `project-manager` présente le bilan à l'utilisateur

## Charger la skill métier

```bash
# Charger la skill du domaine projet (si disponible)
skill("nom-de-la-skill")
```

## Changer d'agent

Pour basculer vers un autre agent pendant la session :

- **CLI :** `opencode --agent <nom-agent>`
- **CLI (raccourci) :** `opencode -a project-manager`
- **Dans le chat :** utiliser `Ctrl+.` (ou la commande de changement d'agent)
- **Mention :** `@project-manager` pour déléguer une tâche spécifique

Agents disponibles : `project-manager`, `scrum-master`, `software-engineer`, `devops-engineer`, `cybersecurity-engineer`, `qa-engineer`

## Commande de vérification

```bash
find . -name "*.md" -type f | sort
```
