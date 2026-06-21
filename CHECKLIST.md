# Checklists de Validation — Cours M2 Nexa Agentic Development


---

## Checklist globale d'installation

Avant de commencer la Séance 1, vérifiez que :

- [ ] Python 3.10+ est installé (`python3 --version`)
- [ ] pip est installé (`python3 -m pip --version`)
- [ ] Git est installé (`git --version`)
- [ ] Docker est installé (`docker --version`)
- [ ] Docker fonctionne (`docker run hello-world`)
- [ ] opencode est installé (`opencode --version`)
- [ ] Le modèle big-pickle fonctionne (`opencode -m opencode/big-pickle -t "Bonjour"`)

---

## Checklist par séance

### Séance 1 — Architecture des LLMs

- [ ] Comprenez la différence entre GPT-3 et les modèles agentiques de 2026
- [ ] Pouvez expliquer MoE, GQA et MLA avec vos propres mots
- [ ] Identifiez les comportements agentiques : CoT, ReAct, tool use, planification
- [ ] Environnement de développement configuré et fonctionnel
- [ ] Premier agent opencode opérationnel

### Séance 2 — Context Window Engineering

- [ ] Comprenez pourquoi la fenêtre de contexte est limitée (O(n²), KV cache)
- [ ] Pouvez calculer la taille du KV cache pour un modèle donné
- [ ] Connaissez les stratégies d'optimisation : sliding window, compression, caching
- [ ] Avez implémenté un sliding window basique
- [ ] Comprennez la différence entre contexte annoncé et contexte effectif

### Séance 3 — Systèmes de Mémoire

- [ ] Distinguez les 3 types de mémoire : épisodique, sémantique, procédurale
- [ ] Comprenez le Continuum Memory Architecture
- [ ] Avez implémenté une mémoire hiérarchique (STM → LTM)
- [ ] Le sliding window fonctionne correctement
- [ ] La persistance JSON fonctionne entre les sessions

### Séance 4 — Model Context Protocol (MCP)

- [ ] Comprenez l'architecture Host/Client/Server
- [ ] Connaissez les 3 transports : stdio, HTTP+SSE, Streamable HTTP
- [ ] Maîtrisez les primitives : Resources, Prompts, Tools
- [ ] Avez créé un serveur MCP fonctionnel avec 3+ tools
- [ ] Le serveur est connecté à opencode via `opencode.json`

### Séance 5 — Agent-to-Agent Protocol (A2A)

- [ ] Comprenez la différence entre MCP et A2A
- [ ] Savez créer une Agent Card valide
- [ ] Maîtrisez le cycle de vie d'une tâche A2A
- [ ] Avez implémenté un agent A2A basique
- [ ] Pouvez expliquer la convergence MCP+A2A

### Séance 6 — GitHub Agents & Platform

- [ ] Comprenez l'architecture du Copilot coding agent
- [ ] Savez configurer un custom agent dans `.github/agents/`
- [ ] Maîtrisez les hooks : preToolUse, postToolUse
- [ ] Avez configuré un agent de revue de code
- [ ] Le fichier `.github/mcp.json` est correctement configuré

### Séance 7 — LangChain & LangGraph

- [ ] Comprenez l'architecture LangChain (chains, tools, memory, retrievers)
- [ ] Savez créer un StateGraph avec LangGraph
- [ ] Maîtrisez les nœuds, arêtes et conditions
- [ ] Avez implémenté un workflow agentique complet
- [ ] Pouvez comparer LangGraph avec les sub-agents opencode

### Séance 8 — CrewAI & AutoGen

- [ ] Comprenez les concepts CrewAI : agents, tâches, crews, processus
- [ ] Comprenez les concepts AutoGen : agents conversationnels, UserProxyAgent
- [ ] Avez implémenté le même cas d'usage avec les 2 frameworks
- [ ] Pouvez justifier le choix d'un framework selon le cas d'usage
- [ ] Connaissez les patterns hybrides (LangGraph + CrewAI)

### Séance 9 — Agentic RAG & Knowledge Systems

- [ ] Comprenez la différence entre RAG classique et Agentic RAG
- [ ] Maîtrisez le cycle : retrieve → evaluate → decide → generate
- [ ] Avez implémenté un backend RAG avec vector store local
- [ ] Le self-correcting retrieval fonctionne
- [ ] Les multi-hop queries sont implémentées

### Séance 10 — Fine-tuning & RL pour Agents

- [ ] Comprenez pourquoi fine-tuner pour les tâches agentiques
- [ ] Maîtrisez les concepts ATLAS et rubric-based RL
- [ ] Comprenez GRPO et curriculum learning
- [ ] Avez conceptualisé un pipeline de fine-tuning
- [ ] Pouvez évaluer quand fine-tuner vs prompt engineering

### Séance 11 — Optimisation Mémoire & Contexte

- [ ] Maîtrisez le calcul de token budget
- [ ] Comprenez la quantization du KV cache (INT8, FP8, INT4)
- [ ] Connaissez les stratégies d'attention sparse
- [ ] Avez configuré un système d'optimisation pour production
- [ ] Pouvez choisir la bonne stratégie selon le hardware

### Séance 12 — Benchmarks & Évaluation

- [ ] Comprenez la famille SWE-bench (Verified, Pro, Live, Multilingual)
- [ ] Maîtrisez les métriques : pass@1, resolve rate, contamination
- [ ] Avez créé un évaluateur de benchmark personnalisé
- [ ] Connaissez les outils de monitoring : LangSmith, AgentOps, W&B
- [ ] Pouvez concevoir un benchmark personnalisé

### Séance 13 — Déploiement & Production

- [ ] Comprenez l'architecture de production complète
- [ ] Avez mis en place une pipeline CI/CD avec GitHub Actions
- [ ] La pipeline inclut : lint, test, build, security audit, deploy
- [ ] Le monitoring et l'observabilité sont configurés
- [ ] La gestion des coûts est maîtrisée

### Séance 14 — Frontières & Futur

- [ ] Comprenez les concepts avancés : DiffMAS, ACE, self-evolving agents
- [ ] Pouvez évaluer les défis actuels de l'Agentic AI
- [ ] Le projet final est complet et fonctionnel
- [ ] La présentation est prête (5-10 minutes)
- [ ] Tous les livrables sont soumis

---

## Checklist de validation du code

Pour chaque fichier Python créé, vérifiez que :

- [ ] Le fichier a un `if __name__ == "__main__":` block
- [ ] Les type hints sont utilisés
- [ ] Les docstrings sont présentes et en français
- [ ] Les commentaires expliquent le "pourquoi", pas le "quoi"
- [ ] Le code passe `ruff check`
- [ ] Les tests unitaires existent et passent
- [ ] Aucune API LLM payante n'est utilisée
- [ ] Aucun secret n'est présent dans le code

---

## Checklist de validation de la configuration

Pour chaque fichier `opencode.json` créé, vérifiez que :

- [ ] Le modèle est `opencode/big-pickle`
- [ ] Les permissions sont configurées explicitement
- [ ] Le mode de l'agent est correct (primary/subagent)
- [ ] Les bash patterns sont restrictifs (principe de moindre privilège)
- [ ] Le fichier est valide JSON (pas de commentaires, ou utiliser `.jsonc`)

---

## Checklist de validation du projet final

- [ ] Tous les composants des séances 1-13 sont intégrés
- [ ] Le README.md est complet (installation, utilisation, architecture)
- [ ] Les tests couvrent > 80% du code
- [ ] La pipeline CI/CD fonctionne (tous les jobs verts)
- [ ] L'audit de sécurité ne trouve pas de vulnérabilité critique
- [ ] La documentation d'architecture est présente
- [ ] La démo fonctionne en live
- [ ] Les choix architecturaux sont justifiés

---

## Checklist de validation de la séance (pour les enseignants)

Avant de livrer une séance, vérifier que :

- [ ] Introduction théorique complète (problème, contexte, lien séances)
- [ ] Objectifs pédagogiques SMART (3-5 objectifs)
- [ ] Chaque concept a : définition → analogie → explication → importance
- [ ] Code commenté ligne par ligne en français
- [ ] Configurations agent décortiquées (chaque champ expliqué)
- [ ] Permissions agent expliquées avec scénario concret
- [ ] Synthèse + lien vers la séance suivante
- [ ] Références contextualisées (pourquoi, niveau de lecture)
- [ ] Zéro référence à Ollama, ChatOllama, langchain_ollama
- [ ] Zéro dépendance à des API LLM externes
- [ ] TP pas à pas avec corrigé complet
- [ ] Checklist de validation présente

---

**Auteur :** yugmerabtene
