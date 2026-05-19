# Lab 1 — AI Developer Assistant (M2 Nexa 2026)

**Durée:** ~30h (8 parties progressives)
**Objectif:** Construire un système agentique complet, de zéro à la production, en utilisant **uniquement opencode** et ses outils intégrés (big-pickle, sub-agents, MCP).

> Chaque partie construit sur la précédente. Le **devops-engineer** gère l'infrastructure CI/CD. Le **scrum-master** suit la progression via GitHub Projects. À la fin, vous aurez un "AI Developer Assistant" fonctionnel.

---

## Méthodologie Agile adaptée

Ce lab suit une approche Scrum adaptée au contexte pédagogique.

### Organisation avec GitHub Projects

```
GitHub Project Board: "AI Developer Assistant"
┌─────────────────────────────────────────────────┐
│ Backlog │ To do │ In Progress │ Review │ Done  │
├─────────┼────────┼─────────────┼────────┼───────┤
│ US-008  │ US-004 │ US-003      │ US-002 │ US-001│
│ US-009  │ US-005 │             │        │       │
│ US-010  │ US-006 │             │        │       │
│         │ US-007 │             │        │       │
└─────────────────────────────────────────────────┘
```

### Rôles dans l'équipe

| Rôle | Étudiant | Outil |
|------|----------|-------|
| **Scrum Master** | 1 étudiant (rotation) | GitHub Projects, Issues |
| **DevOps Engineer** | 1 étudiant (dédié) | CI/CD, GitHub Actions, `.github/` |
| **Backend Engineer** | Tous (binômes) | Code Python, MCP, agents opencode |
| **QA / Test** | 1 étudiant (rotation) | Tests, revue de PR |

### Structure des Sprints

```
Sprint 0 (Setup):   Partie 1         → Environnement, premier agent opencode
Sprint 1 (Core):    Parties 2-3      → MCP + Mémoire persistante
Sprint 2 (Orchestre): Parties 4-5    → Sub-agents + Équipe multi-agents
Sprint 3 (Prod):    Parties 6-7-8    → GitHub Agents + CI/CD + Intégration
```

### User Stories type

```
US-001: En tant que développeur, je veux configurer un agent opencode
        pour comprendre le cycle sub-agent / task.

US-002: En tant que développeur, je veux un serveur MCP
        pour exposer des outils à mon agent.

US-003: En tant que développeur, je veux que mon agent ait
        une mémoire persistante (fichier JSON) entre les sessions.

US-007: En tant que DevOps, je veux une pipeline CI/CD complète
        pour automatiser lint, test, build, et review.
```

Chaque US a :
- **Description** (format Given/When/Then)
- **Critères d'acceptation** (tests automatiques)
- **Definition of Done** (code + tests + CI vert)

---

## Architecture du système cible

```
                    ┌──────────────────────────────────┐
                    │       opencode CLI                 │
                    │       (big-pickle model)           │
                    └────────────┬─────────────────────┘
                                 │
                    ┌────────────▼─────────────────────┐
                    │    opencode.json + AGENTS.md      │
                    │    ┌─────────────────────────┐   │
                    │    │ Sub-agents configurés   │   │
                     │    │ software-engineer          │   │
                    │    │ devops-engineer         │   │
                    │    │ qa-engineer             │   │
                    │    │ cybersecurity-engineer  │   │
                    │    └─────────────────────────┘   │
                    └────────────┬─────────────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
     ┌────▼──────┐        ┌─────▼──────┐        ┌─────▼──────┐
     │ MCP Server │        │ Memory     │        │ GitHub     │
     │ (Python)   │        │ (JSON/FS)  │        │ Agents     │
     │ tools:     │        │            │        │ .github/   │
     │  read_file │        │ sliding    │        │   agents/  │
     │  search_cd │        │ window     │        │   workflows│
     │  run_pythn │        │ compaction │        │   mcp.json │
     └────────────┘        └────────────┘        └────────────┘
                                 │
                    ┌────────────▼─────────────────────┐
                    │     CI/CD Pipeline                │
                    │     GitHub Actions                │
                    │     lint → test → build → deploy  │
                    └──────────────────────────────────┘
```

---

## Plan du Lab 1 (8 parties)

---

### Partie 1: Fondations — Premier agent opencode (3h)

**Objectif:** Comprendre le système de sous-agents opencode.

**User Story:** US-001 — Agent opencode personnalisé

**À faire:**
1. Créer le repo GitHub avec le board Project et les labels
2. Analyser la configuration existante dans `opencode.json`
3. Créer son propre sous-agent dans `.opencode/agents/mon-agent.md`
4. Tester: lancer opencode et déléguer une tâche au sous-agent via `task`
5. Configurer la première GitHub Action (lint)

**Exemple de sous-agent custom:**
```markdown
---
description: Mon assistant de révision de code
mode: subagent
model: opencode/big-pickle
permission:
  read: allow
  glob: allow
  grep: allow
  list: allow
  edit: deny
  bash: { "find *": "allow", "python *": "allow", "*": "ask" }
---

Tu es un assistant de révision de code. Tu vérifies :
1. La qualité du code (pylint, ruff)
2. La couverture de tests
3. Les vulnérabilités de sécurité
Tu travailles en read-only et tu reportes tes résultats.
```

**Concepts:** `opencode.json`, `mode: subagent`, `task` tool, permissions, `AGENTS.md`

---

### Partie 2: Serveur MCP en Python (4h)

**Objectif:** Créer un serveur MCP (Model Context Protocol) avec le SDK Python, sans aucune dépendance LLM externe.

**User Story:** US-002 — Serveur MCP pour outils

**À faire:**
1. Installer le SDK : `pip install mcp`
2. Implémenter 3 tools : `read_file`, `search_code`, `run_python`
3. Ajouter 2 resources : documentation patterns, référence MCP
4. Connecter le serveur à opencode via `opencode.json` → `mcp` section
5. Écrire les tests du serveur MCP
6. CI : ajouter un job de test MCP

**Code — `lab/code/02_mcp_server/server.py`:**
```python
import subprocess
from mcp.server import Server
from mcp.types import Tool, Resource, TextContent

app = Server("dev-assistant")

@app.list_tools()
async def list_tools():
    return [
        Tool(name="read_file",
             description="Read a file from disk",
             inputSchema={"type": "object", "properties": {
                 "path": {"type": "string"}
             }, "required": ["path"]}),
        Tool(name="search_code",
             description="Search for patterns in code",
             inputSchema={"type": "object", "properties": {
                 "pattern": {"type": "string"},
                 "path": {"type": "string", "default": "."}
             }, "required": ["pattern"]}),
        Tool(name="run_python",
             description="Execute Python code safely",
             inputSchema={"type": "object", "properties": {
                 "code": {"type": "string"}
             }, "required": ["code"]}),
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "read_file":
        with open(arguments["path"]) as f:
            return [TextContent(type="text", text=f.read())]
    elif name == "search_code":
        result = subprocess.run(
            ["grep", "-rn", arguments["pattern"], arguments.get("path", ".")],
            capture_output=True, text=True, timeout=10)
        return [TextContent(type="text",
                            text=result.stdout[:3000] or "No matches")]
    elif name == "run_python":
        result = subprocess.run(
            ["python3", "-c", arguments["code"]],
            capture_output=True, text=True, timeout=10)
        return [TextContent(type="text",
                            text=result.stdout + result.stderr)]
    raise ValueError(f"Unknown tool: {name}")

@app.list_resources()
async def list_resources():
    return [
        Resource(uri="docs://agent-patterns",
                 name="Agent Design Patterns",
                 description="Common agent architecture patterns"),
        Resource(uri="docs://mcp-guide",
                 name="MCP Quick Reference",
                 description="MCP protocol summary"),
    ]

@app.read_resource()
async def read_resource(uri: str):
    docs = {
        "docs://agent-patterns": (
            "# Patterns\n1. ReAct Loop\n2. Plan-Execute\n"
            "3. Supervisor\n4. Reflection\n5. Tool-use"
        ),
        "docs://mcp-guide": (
            "# MCP\n- JSON-RPC 2.0\n"
            "- Primitives: Tools, Resources, Prompts\n"
            "- Transports: stdio, HTTP+SSE"
        ),
    }
    return TextContent(type="text", text=docs.get(uri, ""))

if __name__ == "__main__":
    from mcp.server.stdio import stdio_server
    import anyio
    anyio.run(stdio_server, app)
```

**Connexion à opencode — `opencode.json`:**
```json
{
  "mcp": {
    "dev-assistant": {
      "type": "local",
      "command": ["python", "lab/code/02_mcp_server/server.py"],
      "enabled": true
    }
  }
}
```

**Concepts:** MCP, JSON-RPC 2.0, tools, resources, transport stdio

---

### Partie 3: Mémoire persistante (3h)

**Objectif:** Ajouter de la mémoire à long terme à l'agent opencode via fichiers JSON + sliding window.

**User Story:** US-003 — Mémoire persistante

**À faire:**
1. Implémenter une mémoire hiérarchique en Python (STM → LTM → consolidation)
2. Stocker en JSON avec sliding window (garder les N derniers, résumer le reste)
3. Ajouter un outil MCP `memory_search` au serveur de la Partie 2
4. Tester : l'agent retrouve des informations entre sessions
5. CI : backup automatique de la mémoire dans les artefacts

**Code — `lab/code/03_memory/memory.py`:**
```python
import json, os
from datetime import datetime
from collections import deque

class AgentMemory:
    def __init__(self, path: str, window_size: int = 50):
        self.path = path
        self.window_size = window_size
        self.short_term: deque = deque(maxlen=window_size)
        self.long_term: list = []
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path) as f:
                data = json.load(f)
                self.short_term = deque(data.get("short_term", []),
                                         maxlen=self.window_size)
                self.long_term = data.get("long_term", [])

    def _save(self):
        with open(self.path, "w") as f:
            json.dump({
                "short_term": list(self.short_term),
                "long_term": self.long_term,
            }, f, indent=2)

    def add(self, entry: dict):
        entry["timestamp"] = datetime.now().isoformat()
        self.short_term.append(entry)
        if len(self.short_term) == self.window_size:
            # Consolider en long terme
            summary = self._consolidate(self.short_term)
            self.long_term.append(summary)
        self._save()

    def search(self, keyword: str) -> list:
        results = []
        for e in list(self.short_term) + self.long_term:
            text = json.dumps(e)
            if keyword.lower() in text.lower():
                results.append(e)
        return results[-10:]  # max 10 résultats

    def _consolidate(self, entries: deque) -> dict:
        return {
            "summary": f"{len(entries)} events from "
                       f"{entries[0].get('timestamp', '?')}",
            "count": len(entries),
            "compacted": True,
            "timestamp": datetime.now().isoformat()
        }

    def get_context(self, limit: int = 10) -> str:
        recent = list(self.short_term)[-limit:]
        return "\n".join(
            f"[{e.get('timestamp', '?')}] {e.get('content', '')}"
            for e in recent
        )
```

**Concepts:** sliding window, compaction, consolidation, mémoire hiérarchique

---

### Partie 4: Sub-agents & Orchestration opencode (3h)

**Objectif:** Créer une équipe de sous-agents opencode avec des rôles spécialisés.

**User Story:** US-004 — Orchestration multi-agents

**À faire:**
1. Analyser les 6 agents existants dans `.opencode/agents/`
2. Créer 2 nouveaux agents spécialisés :
   - `test-writer` : écrit des tests pour le code
   - `doc-generator` : génère la documentation
3. Configurer les permissions de chaque agent
4. Tester le workflow : `scrum-master` délègue à `test-writer` via `task`
5. Ajouter `agent-instructions` dans chaque fichier agent

**Exemple — `.opencode/agents/test-writer.md`:**
```markdown
---
description: Écrit des tests pytest pour le code du lab.
mode: subagent
model: opencode/big-pickle
permission:
  read: allow
  glob: allow
  grep: allow
  list: allow
  edit: allow
  bash:
    python *: allow
    pytest *: allow
    *: ask
---

Tu es un Test Writer. Pour chaque fichier Python que tu reçois :
1. Analyse les fonctions et classes
2. Écris des tests pytest (unitaires + cas limites)
3. Vérifie que les tests passent avec `python -m pytest`
4. Corrige les tests qui échouent
```

**Concepts:** sub-agent, permissions, délégation, `task` tool

---

### Partie 5: Équipe multi-agents — Workflow complet (3h)

**Objectif:** Faire collaborer plusieurs agents sur un cycle complet : plan → code → test → review.

**User Story:** US-005 — Cycle Dev complet par agents

**À faire:**
1. Définir un workflow dans `AGENTS.md` qui décrit le cycle
2. Créer un agent `tech-lead` qui orchestre les autres
3. Simuler un cycle complet :
    - `software-engineer` écrit une fonction
   - `test-writer` écrit les tests
   - `qa-engineer` valide
   - `cybersecurity-engineer` audite
   - `tech-lead` consolide
4. Documenter le workflow

**Workflow — `AGENTS.md` (section workflow):**
```markdown
## Workflow de développement agentique

1. **Plan** → `tech-lead` décompose la tâche en sous-tâches
2. **Code** → `software-engineer` implémente la solution
3. **Test** → `test-writer` écrit et exécute les tests
4. **Review** → `qa-engineer` valide la qualité
5. **Audit** → `cybersecurity-engineer` vérifie la sécurité (read-only)
6. **Merge** → `scrum-master` approuve et consolide
```

**Concepts:** orchestration, workflow pipeline, cycle Dev, rôles

---

### Partie 6: GitHub Custom Agent (3h)

**Objectif:** Créer un agent GitHub personnalisé pour la revue de code automatique.

**User Story:** US-006 — Agent GitHub de review

**À faire:**
1. Créer `.github/agents/reviewer/agent.md`
2. Définir les hooks `preToolUse` (linter) et `postToolUse` (vérification)
3. Configurer le serveur MCP dans `.github/mcp.json`
4. Créer un workflow GitHub Actions déclenché sur PR
5. Tester: ouvrir une PR → l'agent commente automatiquement

**Exemple — `.github/agents/reviewer/agent.md`:**
```markdown
---
name: PR Reviewer
description: Automated code review on pull requests
model: opencode/big-pickle
hooks:
  preToolUse: "ruff check {file}"
  postToolUse: "python -m pytest {dir} -x"
---

Review every PR for:
1. Code style violations (ruff)
2. Test coverage — suggest missing tests
3. Security issues — secrets, injections
4. Performance — O(n) complexity, N+1 queries

Block the PR if critical issues are found.
```

**Concepts:** GitHub Custom Agents, agent hooks, PR review automation

---

### Partie 7: CI/CD Pipeline complet (4h) ← **Géré par devops-engineer**

**Objectif:** Mettre en place une pipeline CI/CD complète, gérée par le sous-agent `devops-engineer`.

**User Story:** US-007 — Pipeline CI/CD agentique

**Responsable:** Sous-agent `devops-engineer`

**Architecture CI/CD:**

```
                    PR ouverte
                       │
                       ▼
              ┌─────────────────┐
              │  Lint & Format   │  ruff, black, mypy
              └────────┬────────┘
                       │
              ┌────────▼────────┐
              │  Unit Tests      │  pytest (MCP, memory, tools)
              └────────┬────────┘
                       │
              ┌────────▼────────┐
              │  Integration     │  Test MCP server + client
              │  Tests           │
              └────────┬────────┘
                       │
              ┌────────▼────────┐
              │  Build & Package │  pip install -e .
              └────────┬────────┘
                       │
              ┌────────▼────────┐
              │  Agent Review    │  GitHub Custom Agent review
              └────────┬────────┘
                       │
              ┌────────▼────────┐
              │  Merge (auto)    │  si tous verts + review OK
              └─────────────────┘
```

**À faire (via le sous-agent `devops-engineer`):**

Le `devops-engineer` crée et gère via l'outil `task`:

1. **Workflow CI** — `.github/workflows/ci.yml` :
   ```yaml
   name: CI
   on: [push, pull_request]
   jobs:
     lint:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - run: pip install ruff mypy
         - run: ruff check lab/code/
         - run: mypy lab/code/ || true

     test:
       needs: lint
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - run: pip install -r lab/requirements.txt
         - run: pytest lab/tests/ -v --junitxml=report.xml
         - uses: actions/upload-artifact@v4
           with:
             name: test-report
             path: report.xml

     agent-review:
       needs: test
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - name: AI Code Review
           uses: github/copilot-agent@v1
           with:
             agent: reviewer
             prompt: "Review this PR for quality, tests, and security"
   ```

2. **Badges** dans `README.md` : `[![CI](https://github.com/.../workflows/CI/badge.svg)]`

3. **Scripts de backup** : `lab/code/07_cicd/backup.sh` — sauvegarde les mémoires JSON

4. **Documentation** de la pipeline (README section)

**Concepts:** CI/CD, GitHub Actions, artifacts, badges, devops as code

---

### Partie 8: Intégration — AI Developer Assistant complet (4h)

**Objectif:** Assembler toutes les parties en un système cohérent.

**User Story:** US-008 — Assistant complet intégré

**À faire:**
1. Vérifier que tous les agents opencode sont bien configurés
2. Vérifier que le serveur MCP est connecté et fonctionnel
3. Vérifier que la mémoire persiste entre les sessions opencode
4. Vérifier que la CI/CD tourne sur chaque PR
5. Audit final par `cybersecurity-engineer` (read-only)
6. Validation finale par `qa-engineer`

**Critères de succès:**
```
✓ Le scrum-master peut déléguer des tâches aux sous-agents
✓ Le serveur MCP expose 3+ tools et est connecté à opencode
✓ La mémoire JSON persiste entre les sessions
✓ La pipeline CI/CD tourne sur chaque PR (lint + test + review)
✓ Les tests passent (pytest)
✓ Le security audit ne trouve pas de vulnérabilité critique
```

---

## Lab 2 — Agentic RAG & Knowledge Systems (à venir)

Un second lab (optionnel) dédié au RAG agentique. Il viendra compléter celui-ci.

---

## Validation

```bash
# Lancer tous les tests
cd lab && python -m pytest tests/ -v

# Vérifier la configuration opencode
opencode --check-config

# Audit de sécurité
python lab/code/08_integration/security_audit.py

# Vérifier les agents
ls -la .opencode/agents/
cat opencode.json | python -m json.tool
```

## Références
- opencode config: https://opencode.ai/config.json
- GitHub Actions: https://docs.github.com/en/actions
- GitHub Projects: https://docs.github.com/en/issues/planning-and-tracking-with-projects
- MCP Specification: https://modelcontextprotocol.io
