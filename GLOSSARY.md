# Glossaire bilingue — Bilingual Glossary

| FR | EN | Définition |
|----|----|------------|
| **Agent** | Agent | Programme autonome qui perçoit son environnement, raisonne et agit pour accomplir un objectif. Dans opencode : un sous-agent est configuré via `.md` frontmatter. |
| **Agent par défaut** | Default agent | Agent chargé automatiquement au lancement d'opencode dans un dossier. Défini par `default_agent` dans `opencode.json`. |
| **Arête conditionnelle** | Conditional edge | Dans LangGraph, fonction qui examine l'état courant et décide du prochain nœud à exécuter. |
| **Boucle ReAct** | ReAct Loop | Cycle Raisonnement (Thought) → Action → Observation qui permet à un agent d'interagir avec des outils de façon dynamique. |
| **Chaîne de pensée** | Chain-of-Thought (CoT) | Technique de prompting où le modèle produit un raisonnement pas à pas avant la réponse finale. |
| **Checkpoint** | Checkpoint | Sauvegarde instantanée de l'état d'un graphe LangGraph, permettant reprise et débogage. |
| **Compaction** | Compaction | Mécanisme opencode qui résume automatiquement l'historique de la conversation pour éviter de saturer la fenêtre de contexte. Configurable via `compaction` dans `opencode.json`. |
| **Contexte** | Context | Ensemble des tokens disponibles pour un LLM lors d'une inférence (prompt système, historique, outils). |
| **Fenêtre de contexte** | Context window | Nombre maximal de tokens qu'un modèle peut traiter en une seule inférence. |
| **Graphe d'état** | StateGraph | Dans LangGraph, graphe orienté où des nœuds (fonctions Python) modifient un état typé qui circule. |
| **Handoff** | Handoff | Transfert d'une session agent entre deux environnements (ex: GitHub cloud ↔ terminal CLI). |
| **Hooks** | Hooks | Dans GitHub Agents, points de vie (`preToolUse`, `postToolUse`) qui déclenchent des actions automatiques. |
| **Inférence** | Inference | Exécution d'un modèle LLM pour générer une sortie à partir d'une entrée. |
| **JSON-RPC 2.0** | JSON-RPC 2.0 | Protocole de requête-réponse utilisé par MCP pour la communication entre host et serveur. |
| **KV Cache** | KV Cache | Mémoire GPU qui stocke les paires clé-valeur de l'attention pour éviter des recalculs. Principal goulot des longues séquences. |
| **MCP** | Model Context Protocol | Protocole standardisé pour connecter un LLM à des outils externes (fichiers, APIs, bases de données). |
| **Mémoire épisodique** | Episodic memory | Historique des interactions de l'agent (qui a fait quoi, quand). |
| **Mémoire sémantique** | Semantic memory | Connaissances consolidées dérivées des interactions (préférences, patterns). |
| **Mémoire procédurale** | Procedural memory | Compétences et procédures (comment utiliser un outil, quel format de réponse). |
| **MoE** | Mixture of Experts | Architecture où seuls les sous-réseaux pertinents sont activés par token, réduisant le coût d'inférence. |
| **Nœud** | Node | Dans LangGraph, fonction Python `state → state` qui constitue une étape du graphe. |
| **Permissions** | Permissions | Dans opencode, règles qui définissent ce qu'un agent peut faire (`allow`, `deny`, `ask`). |
| **Session** | Session | Connexion continue entre un utilisateur et un agent opencode. Le contexte et l'historique y sont conservés. |
| **Session ID** | Session ID | Identifiant unique d'une session, utilisé pour le checkpointing et la reprise. |
| **Sous-agent** | Sub-agent | Agent opencode secondaire, défini dans `.opencode/agents/`, invocable via `task`. |
| **Task** | Task | Dans opencode, outil de délégation à un sous-agent. Dans A2A, unité de travail déléguée d'un agent à un autre. |
| **Token** | Token | Unité de base du texte pour un LLM (~0.75 mot en anglais, ~0.5 mot en français). |
| **Tool calling** | Tool calling | Capacité d'un LLM à générer des appels de fonction structurés (JSON) que le runtime exécute. |
| **Thread ID** | Thread ID | Identifiant de session LangGraph, passé dans la config pour le checkpointing. |

---

## Références clés

| Référence | URL |
|-----------|-----|
| Vaswani et al., "Attention Is All You Need" (2017) | https://arxiv.org/abs/1706.03762 |
| Wei et al., "Chain-of-Thought Prompting" (2022) | https://arxiv.org/abs/2201.11903 |
| Yao et al., "ReAct: Synergizing Reasoning and Acting" (2023) | https://arxiv.org/abs/2210.03629 |
| Lewis et al., "RAG" (2020) | https://arxiv.org/abs/2005.11401 |
| Jimenez et al., "SWE-bench" (2024) | https://arxiv.org/abs/2310.06770 |
| MCP Specification | https://modelcontextprotocol.io |
| A2A Protocol | https://a2aprotocol.org |
| opencode | https://opencode.ai |
| LangGraph | https://langchain-ai.github.io/langgraph/ |
| CrewAI | https://docs.crewai.com |
