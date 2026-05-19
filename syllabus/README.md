# Agentic Development — M2 Nexa (2026)

## Syllabus — Master 2, Spécialité Intelligence Artificielle & Systèmes Autonomes

**Année universitaire:** 2026-2027
**Volume horaire:** 60h (30h CM + 30h TP/Projet)
**Langue:** Français (slides), Code & références: Anglais
**Prérequis:** Python avancé, bases en ML/DL, programmation système, Git/GitHub

---

## Vision pédagogique

Ce cours forme les étudiants à concevoir, déployer et optimiser des **systèmes agentiques** — des programmes capables de planifier, raisonner, utiliser des outils et collaborer de façon autonome dans des environnements complexes. La pédagogie suit trois axes:

1. **Fondations théoriques** — architectures transformer, mécanismes d'attention, fenêtres de contexte, mémoire, planification
2. **Protocoles & standards 2026** — MCP (Model Context Protocol), A2A (Agent-to-Agent), GitHub Agents, outils de la plateforme
3. **Ingénierie pratique** — configuration d'agents opencode, serveurs MCP, CI/CD, GitHub Agents, optimisation mémoire/coût

---

## Plan du cours (30h CM)

### Partie I: Fondamentaux de l'Agentic AI (6h)

| Séance | Titre | Contenu |
|--------|-------|---------|
| 1 | **Architecture des LLMs & genèse agentique** (2h) | From GPT-3 à Claude Opus 4.5/GPT-5: scaling laws, MoE, reasoning tokens. Émergence du comportement agentique: ReAct, planification, tool use. Écosystème 2026: panorama des modèles (frontier vs open-source). |
| 2 | **Context Window Engineering** (2h) | Fenêtre de contexte: attention O(n²), KV cache, limites GPU. Stratégies: sliding window, compression (LLMLingua), hierarchies, RAG + cache. Innovations 2026: FlashAttention-3, Ring Attention, Test-Time Training, AllMem. |
| 3 | **Systèmes de mémoire pour agents** (2h) | Memoire épisodique, sémantique, procédurale. Continuum Memory Architecture. Hierarchical memory consolidation (AutoN). LongMemEval: benchmark de mémoire persistante. HydraDB, OMEGA, Zep, Redis Agent Memory. |

### Partie II: Protocoles & Standards 2026 (8h)

| Séance | Titre | Contenu |
|--------|-------|---------|
| 4 | **Model Context Protocol (MCP)** (3h) | Architecture MCP: Host, Client, Server. JSON-RPC 2.0, transports (stdio, HTTP+SSE, Streamable HTTP). Primitives: Resources, Prompts, Tools. OAuth 2.1, roadmap 2026 (scalabilité, auth entreprise, audit trails). Développement de serveurs MCP (Python SDK). |
| 5 | **Agent-to-Agent Protocol (A2A)** (2h) | Google DeepMind A2A: Agent Cards, task lifecycle, découverte de capacités. Comparaison MCP vs A2A: complémentarité. Use cases: orchestration cross-organisation, agent marketplaces. Convergence 2026-2027 vers MCP+A2A stack. |
| 6 | **GitHub Agents & Platform** (3h) | GitHub Copilot coding agent: model picker, self-review, security scanning. Custom agents (`.github/agents/`). Cloud agent vs local agent. Agents panel, CLI handoff, session management. Copilot Memory, sub-agents, plan agent, hooks, MCP integration. Hubrise des `AGENTS.md` / `CLAUDE.md`. |

### Partie III: Frameworks & Orchestration (8h)

| Séance | Titre | Contenu |
|--------|-------|---------|
| 7 | **LangChain & LangGraph** (3h) | Architecture LangChain: chains, tools, memory, retrievers. LangGraph: graphes d'état, cycles, checkpointing, human-in-the-loop. Production patterns: durable execution, branching, fault tolerance. Comparaison 2026: LangGraph domine pour le contrôle fin. |
| 8 | **CrewAI & AutoGen** (2h) | CrewAI: agents rôle-based, crews, tasks, processus hiérarchiques. AutoGen: agents conversationnels, UserProxyAgent, code execution. Benchmark pratique: quand utiliser quoi? Patterns hybrides (LangGraph + CrewAI). |
| 9 | **Agentic RAG & Knowledge Systems** (3h) | RAG 2.0: agentic RAG, self-correcting retrieval, multi-hop queries. Outils: LlamaIndex, LangChain retrievers, vector stores (Chroma, Weaviate, Pinecone). GraphRAG, structured extraction, Knowledge Graphs. Contextual compression post-retrieval. |

### Partie IV: Optimisation & Production (8h)

| Séance | Titre | Contenu |
|--------|-------|---------|
| 10 | **Fine-tuning & RL pour agents** (2h) | ATLAS: Reinforcement Finetuning pour tool spaces. Rubric-based RL. SWE-smith: entraînement de modèles pour SWE. GRPO, curriculum learning. Optimisation de la tool calling. |
| 11 | **Optimisation mémoire & contexte** (2h) | Token budgets, compression (KV cache quantization, INT8/4-bit). Attention sparse (L2A: Learning To Attend). Cache élastique RocketKV. Distillation, Mixture-of-Experts. Stratégies 2026: hierarchical memory, context pruning. |
| 12 | **Benchmarks & Évaluation** (2h) | SWE-bench (Verified, Pro, Live, Multilingual). SWE-Compass: 8 task types, 10 languages. Évolution 2025-2026: de 48% à 93.9% (Claude Mythos). SWE-bench Pro: 45-47% — le nouveau terrain de jeu. Métriques: pass@1, resolve rate, contamination. Outils: LangSmith, AgentOps, W&B. |
| 13 | **Déploiement & Production** (2h) | Architecture de production: GitHub Actions, MCP, load balancing, session management. Sécurité: sandboxing, auto-approval, politique de permissions. Monitoring, observabilité, tracing. Coûts: API vs local, caching, batching. |

### Partie V: Frontières & Futur (séminaires — 2h)

| Séance | Titre | Contenu |
|--------|-------|---------|
| 14 | **Agentic AI: Défis & Opportunités** (2h) | Agent-to-agent latent communication (DiffMAS). Agentic Context Engineering (ACE — Microsoft). Self-evolving agents (Agent-World). REDEREF: probabilistic control. Robot agents (AgenticLab). Alignment, safety, gouvernance. Futur: zero-touch software development, AI dev teams. |

---

## Labs (30h + 15h optionnel)

### Lab 1 — AI Developer Assistant (30h, obligatoire)

Construit un système agentique complet avec méthodologie agile (Scrum + GitHub Projects) et pipeline CI/CD complète gérée par le **devops-engineer**.

| Partie | Titre | Sprint | Responsable |
|--------|-------|--------|-------------|
| 1 | **Fondations — Agent minimal ReAct** (3h) | Sprint 0 | Binôme |
| 2 | **Serveur MCP complet** (4h) | Sprint 1 | Binôme |
| 3 | **Mémoire persistante** (3h) | Sprint 1 | Binôme |
| 4 | **LangGraph — Workflow agent** (3h) | Sprint 2 | Binôme |
| 5 | **CrewAI — Équipe d'agents** (3h) | Sprint 2 | Binôme |
| 6 | **GitHub Custom Agent** (3h) | Sprint 3 | Binôme |
| 7 | **CI/CD Pipeline complet** (4h) | Sprint 3 | **devops-engineer** |
| 8 | **Intégration finale** (4h) | Sprint 3 | Tous |

Détails: `lab/README.md`

### Lab 2 — Agentic RAG & Knowledge Systems (15h, optionnel/suite)

Étend l'assistant avec RAG, embeddings, vector stores, et Knowledge Graphs.

| Partie | Titre |
|--------|-------|
| 1 | **Embeddings & Vector Store** (3h) |
| 2 | **Self-Correcting RAG** (3h) |
| 3 | **Contextual Compression & Reranking** (3h) |
| 4 | **GraphRAG & Knowledge Graph** (3h) |
| 5 | **Intégration RAG dans l'assistant** (3h) |

Détails: `lab/lab2-rag.md`

---

## Projet de fin de cours

**Sujet au choix (binômes):**

1. **DevOps Agent** — Agent autonome qui déploie, surveille et répare une infrastructure cloud
2. **Code Reviewer** — Multi-agent system pour la revue de code avec MCP + GitHub API
3. **Research Assistant** — Agent de recherche bibliographique avec RAG, extraction, synthèse
4. **Sujet libre** — Proposition argumentée et validée par l'enseignant

**Livrables:** Code + README + Démo + Rapport d'analyse des choix architecturaux

---

## Références principales

### Articles fondateurs
- Vaswani et al., "Attention Is All You Need" (2017)
- Wei et al., "Chain-of-Thought Prompting" (2022)
- Yao et al., "ReAct: Synergizing Reasoning and Acting" (2023)
- Jimenez et al., "SWE-bench: Can Language Models Resolve Real-world Github Issues?" (2024)

### Standards 2026
- Model Context Protocol — https://modelcontextprotocol.io
- Agent-to-Agent Protocol (A2A) — https://a2aprotocol.org
- GitHub Copilot Agents — https://github.blog/category/product/ copilot/

### Frameworks
- LangChain / LangGraph — https://langchain.com
- CrewAI — https://crewai.com
- opencode — https://opencode.ai
- LlamaIndex — https://llamaindex.ai

### Articles de recherche clés 2025-2026
- "Agentic Context Engineering" (Microsoft / ICLR 2026)
- "ATLAS: Scaling Agentic Capabilities, Not Context" (2026)
- "AllMem: A Memory-centric Recipe for Long-context" (2026)
- "REDEREF: Training-Free Agentic AI" (2026)
- "L2A: Learning To Attend" (2026)
- "Agent-World: Scaling Real-World Environment Synthesis" (2026)
- "DiffMAS: Learning to Communicate" (2026)
- "The Auton Agentic AI Framework" (2026)
- "The Path Ahead for Agentic AI" (2026)

---

## Évaluation

| Composante | Poids |
|------------|-------|
| Lab (rendu en 3 étapes) | 30% |
| Projet intégrateur | 40% |
| Examen final (QCM + problèmes) | 30% |

---
*Lab 2 (optionnel) : bonus de +5% si complété.*

---

*Document généré le 18 mai 2026 — Syllabus v2.0*
