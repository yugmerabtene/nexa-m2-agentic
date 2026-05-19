# Audit: État de l'art de l'Agentic Development — Mai 2026

## 1. Modèles et capacités

### State of the Art sur SWE-bench (agentic coding)

| Modèle | SWE-bench Verified | SWE-bench Pro | Date |
|--------|-------------------|---------------|------|
| Claude Opus 4.5 (API) | 80.9% | ~46% | Avr 2026 |
| Gemini 3 Pro (API) | 78.8% | — | Avr 2026 |
| GPT-5 Codex | 74.9% | ~42% | Avr 2026 |
| Claude Mythos Preview | **93.9%** | — | Avr 2026 |

**Key insight:** SWE-bench Verified est saturé (~80% = nouveau plafond). SWE-bench Pro (45-47%) est le nouveau benchmark significatif. Le scaffold (architecture agent) compte autant que le modèle: 16 points d'écart entre SWE-agent v1 et Cline sur le même modèle.

### Modèles open-source pour agents 2026
- **Llama 4 Scout** — 10M tokens de contexte natif
- **Gemma 4 E4B** — 4.5B params, vision, tool calling natif, ~5GB quantized
- **Qwen 2.5 Coder** — Meilleur rapport qualité/taille pour le code
- **DeepSeek V3.2** — Performance frontier-level en open-source
- **GLM-4.7-Flash** — Optimisé pour agent loop

---

## 2. GitHub Copilot & Platform (Nouveautés 2025-2026)

### Copilot Coding Agent (devenu Copilot Cloud Agent)
- **Model picker** — Choix du modèle par tâche (rapide pour tests, premium pour refacto)
- **Self-review** — L'agent revoit son propre code avant PR
- **Security scanning** — Code scanning, secret scanning, dependency checks intégrés
- **Custom agents** — `.github/agents/` — agents spécialisés partageables dans l'org
- **CLI handoff** — Sessions cloud ↔ terminal sans perte de contexte
- **Implementation plans** — Génération de plan avant écriture de code
- **Deep research** — Analyse approfondie du codebase
- **Agents panel** — Mission control sur github.com

### VS Code (v1.109-1.110 - Jan/Fév 2026)
- **Multi-agent development** — Copilot, Claude, agents locaux, background, cloud
- **Agent hooks** — lifecycle events (preToolUse, postToolUse)
- **Fork a conversation** — Brancher depuis un checkpoint
- **Agent Memory** — Contexte persistant partagé entre sessions
- **Context compaction** — `/compact` manuel ou automatique
- **Explore subagent** — Recherche codebase parallélisée
- **Sous-agents** — Exécution parallèle de sub-agents
- **Agent plugins** — Packs pré-configurés (skills, tools, hooks, MCP)

### JetBrains (Mars 2026)
- Custom agents, sub-agents, plan agent (GA)
- `AGENTS.md` / `CLAUDE.md` support
- Context window usage indicator
- Auto model selection (GA)

### Visual Studio (Mars-Avril 2026)
- Custom agents via `.agent.md`
- Agent skills réutilisables
- `find_symbol` tool (LSP-aware)
- Profiler agent, PerfTips, Smart Watch
- Enterprise MCP governance

---

## 3. Protocoles & Standards

### MCP (Model Context Protocol)
- **Version stable** depuis Nov 2025
- **Adoption massive:** Anthropic, OpenAI, Google, Microsoft — tous l'ont adopté
- **97M+ downloads/mois** des SDKs
- **500+ serveurs MCP** dans l'écosystème
- **Roadmap 2026:**
  1. Transport Evolution — Streamable HTTP, stateless sessions
  2. Agent Communication — Standardisation inter-agent
  3. Governance Maturation — Contributor ladder, WG delegation
  4. Enterprise Readiness — Audit trails, OAuth 2.1, SSO
- **MCP Server Cards** — Découverte via `.well-known`
- **Extensions:** ext-auth, ext-apps, network equipment (IETF draft)

### A2A (Agent-to-Agent Protocol — Google DeepMind)
- **Annoncé** Avril 2025, version 0.9 (draft), v1.0 prévue Juin 2026
- **50+ partenaires** (Salesforce, SAP, Atlassian, ServiceNow, etc.)
- **Agent Cards** — Découverte de capacités au runtime
- **Task lifecycle** — State machine: submitted → working → completed → failed
- **Asynchrone par défaut** — Callback URLs, SSE streaming
- **Human-in-the-loop** — Approval gates intégrés
- **Observabilité** — Trace IDs OpenTelemetry
- **Hébergé par Linux Foundation** (AI & Data Foundation)

### MCP vs A2A: La stack complémentaire

| Dimension | MCP | A2A |
|-----------|-----|-----|
| Problème | Agent → Tool | Agent → Agent |
| Maturité | Stable (v1) | Émergent (v0.9) |
| Adoption | Massive | Croissante |
| Transport | JSON-RPC (stdio/HTTP) | HTTP + SSE |
| Découverte | tools/list | Agent Cards |
| Auth | Basique | OAuth 2.1 |

**Pattern 2026:** MCP pour les tools, A2A pour la coordination inter-agent. Les deux sont utilisés ensemble dans les systèmes de production.

---

## 4. Frameworks d'orchestration (Classement 2026)

| Framework | Stars GH | Version | Paradigme | Maturité prod | Meilleur pour |
|-----------|----------|---------|-----------|---------------|---------------|
| LangChain/LangGraph | 130K+ | 0.2.x | Graph-based | Très haute | Workflows complexes, contrôle fin |
| CrewAI | 46K+ | 1.11.0 | Role-based | Haute | Équipes multi-agents |
| AutoGen | 56K+ | v0.7.5 | Conversation | Stagnant | Recherche, code execution |
| Semantic Kernel | — | — | Enterprise | Haute | Écosystème .NET/Azure |
| AutoGPT | — | — | Autonomous | Expérimental | Prototypage only |

**Tendances 2026:**
- LangGraph domine pour les systèmes de production
- CrewAI gagne du terrain en entreprise (processus métier)
- AutoGen en déclin (6 mois sans release stable)
- Patterns hybrides: LangGraph orchestre, CrewAI pour les teams spécialisées

---

## 5. Optimisation mémoire & contexte

### Innovations 2026
- **FlashAttention-3** — 1.3 PFLOPs/s sur H100
- **L2A (Learning To Attend)** — ~80% des tokens n'ont pas besoin d'attention globale → 2x training throughput, 50% KV cache reduction
- **RocketKV** — 400x compression ratio, 3.7x speedup
- **AllMem** — SWA + TTT memory networks: 4k window = performance 37k full attention
- **TTT-E2E** — 35x speedup pour 2M tokens
- **Agentic Context Engineering (ACE)** — +10.6% sur agents, contextes évolutifs
- **Continuum Memory Architecture** — Mémoire persistante avec consolidation, temporal chaining

### Stratégies de production
1. Token budget — Allouer comme ressource système
2. RAG optimisé — Chunks sémantiques + reranking + MMR
3. Compression avant expansion — LLMLingua, AutoCompressor
4. Summarization progressive — Recent verbatim, ancien compressé
5. Sliding window + pinned instructions
6. Cache sémantique — Réduction de 90% des coûts sur prompts répétés

---

## 6. Communication inter-agent latente

- **DiffMAS** — KV-mediated latent communication, SFT-like training sur trajectoires multi-agents
  - +26.7% sur AIME24, +20.2% sur GPQA-Diamond
  - Optimisation jointe de la communication + du raisonnement
- **REDEREF** — Thompson sampling pour délégation, 28% réduction tokens, 17% moins d'appels agent
- **ACP (Agent Connect Protocol)** — IBM/AGNTCY, REST-based, minimaliste
- **ANP (Agent Network Protocol)** — Internet d'agents décentralisé, W3C DIDs

---

## 7. Écosystème local & open-source

### Outils clés
- **Ollama** — 168K+ stars, v0.20.4, runtime local de référence
- **llama.cpp** — Moteur C++, support agents natif (llama-agent)
- **llama-agent** — Binary unique, zero deps, tool loop, MCP support, vision
- **OpenHands** — Agent open-source, 68.4% sur SWE-bench Verified
- **SWE-agent** — Princeton NLP, scaffold minimal (100 lines → 65% Verified)
- **Cline** — ~60% Verified, agent mode dans VS Code

### Modèles locaux recommandés pour agents
| Modèle | Taille | VRAM | Cas d'usage |
|--------|--------|------|-------------|
| Qwen 2.5 Coder 1.5B | 1GB | 2GB | Rapide, hardware faible |
| Qwen 2.5 Coder 7B | 4.7GB | 6GB | **Daily driver** |
| Gemma 4 E4B 4.5B | ~5GB | 8GB | Vision + tool calling |
| Llama 4 Maverick 17B | ~10GB | 16GB | Généraliste |
| DeepSeek Coder V2 16B | 9GB | 12GB | Code complexe |

---

## 8. Conclusion & Recommandations pour le cours

### Constats
1. L'agentic coding a passé un cap: 93.9% sur SWE-bench Verified, mais 45% sur Pro
2. MCP est devenu le standard de facto pour l'intégration tool-model
3. GitHub a intégré l'agentic dans sa platform (Copilot agents, panel, custom agents)
4. La mémoire et le contexte sont les goulots d'étranglement principaux
5. Les frameworks ont convergé: LangGraph domine, CrewAI complète
6. L'open-source permet maintenant de faire tourner des agents capables en local

### Axes pédagogiques prioritaires
1. Compréhension profonde des mecanismes de contexte et mémoire
2. Maîtrise de MCP (le standard 2026)
3. Construction d'agents avec LangGraph + CrewAI
4. Optimisation coût/performance pour la production
5. GitHub platform: custom agents, CI/CD agentic, security
6. Évaluation rigoureuse (SWE-bench, benchmarks)
