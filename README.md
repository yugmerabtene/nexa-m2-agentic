# Cours M2 Nexa — Agentic Development 2026

**Concevez et déployez des systèmes agentiques professionnels — des architectures LLM aux protocoles MCP/A2A, en passant par l'orchestration multi-agents.**

Ce cours de Master 2 (60h : 30h CM + 30h TP/Projet) vous guide à travers les concepts et techniques du développement d'agents autonomes. Chaque séance contient :

- **Une section théorique** avec définitions, analogies et schémas
- **Des prérequis clairs** : ce qu'il faut installer avant de commencer
- **Un TP pratique** avec fichiers à créer, commandes à exécuter, et corrigé pas à pas
- **Une checklist de validation** pour vérifier votre progression

**Particularité :** aucun abonnement API requis. Tout fonctionne avec `opencode` et le modèle gratuit `big-pickle`.

**Fil rouge :** un "AI Developer Assistant" dont le cahier des charges est dans [`PROJECT.md`](PROJECT.md). Chaque TP construit ce projet pas à pas.

---

## Parcours et progression

Le cours se découpe en **5 parties** qu'il faut suivre dans l'ordre :

```
Partie I ──► Partie II ──► Partie III ──► Partie IV ──► Partie V
Fondamentaux   Protocoles    Frameworks    Optimisation   Frontières
(S1-S3)        & Standards   & Orchestration (S10-S13)     (S14)
               (S4-S6)       (S7-S9)
```

---

## Prérequis général

Avant de commencer la **Séance 1**, installez ces outils :

### Linux (Ubuntu/Debian)

```bash
# 1. Mettre à jour les paquets
sudo apt update

# 2. Installer Python, pip, Git et Docker
sudo apt install python3 python3-pip python3-venv git docker.io -y

# 3. Autoriser l'utilisateur courant à lancer Docker sans sudo
sudo usermod -aG docker "$USER"

# 4. Redémarrer la session, puis vérifier Docker
docker --version
docker run hello-world

# 5. Installer opencode
python3 -m pip install --user opencode

# 6. Vérifier les outils
python3 --version
python3 -m pip --version
git --version
docker --version
opencode --version

# 7. Tester le modèle gratuit big-pickle
opencode -m opencode/big-pickle -t "Bonjour, quel est ton rôle ?"
```

### macOS

```bash
# 1. Installer Homebrew si nécessaire : https://brew.sh

# 2. Installer Python, Git et Docker Desktop
brew install python git
brew install --cask docker

# 3. Ouvrir Docker Desktop une première fois, puis vérifier Docker
open -a Docker
docker --version
docker run hello-world

# 4. Installer opencode
python3 -m pip install --user opencode

# 5. Vérifier les outils
python3 --version
python3 -m pip --version
git --version
docker --version
opencode --version

# 6. Tester le modèle gratuit big-pickle
opencode -m opencode/big-pickle -t "Bonjour, quel est ton rôle ?"
```

### Windows 10/11 (PowerShell)

```powershell
# 1. Installer Python, Git et Docker Desktop avec winget
winget install Python.Python.3.12
winget install Git.Git
winget install Docker.DockerDesktop

# 2. Redémarrer Windows, lancer Docker Desktop, puis vérifier Docker
docker --version
docker run hello-world

# 3. Installer opencode
py -m pip install --user opencode

# 4. Vérifier les outils
py --version
py -m pip --version
git --version
docker --version
opencode --version

# 5. Tester le modèle gratuit big-pickle
opencode -m opencode/big-pickle -t "Bonjour, quel est ton rôle ?"
```

> **Résultat attendu :** Python, Git, Docker et opencode affichent une version. `docker run hello-world` affiche un message de succès. L'agent opencode répond avec une présentation.

### Convention de commandes pour tout le cours

| Usage | Linux/macOS | Windows PowerShell |
|---|---|---|
| Lancer Python | `python3 script.py` | `py script.py` |
| Installer un paquet | `python3 -m pip install paquet` | `py -m pip install paquet` |
| Lancer pytest | `python3 -m pytest tests/ -v` | `py -m pytest tests/ -v` |
| Commandes Git | `git ...` | `git ...` |
| Commandes Docker | `docker ...` | `docker ...` |
| Commandes opencode | `opencode ...` | `opencode ...` |

Dans les séances, si une commande est écrite avec `python3`, utilisez `py` sous Windows PowerShell.

### Convention de dossiers pour tous les TPs

Quand un TP commence par une commande comme `mkdir mon-projet && cd mon-projet`, cela signifie :

1. Ouvrez un terminal dans le dossier où vous rangez vos exercices, par exemple `~/agentic-labs` sur Linux/macOS ou `C:\Users\VotreNom\agentic-labs` sur Windows.
2. Créez un **nouveau dossier de TP** avec `mkdir`.
3. Entrez dans ce dossier avec `cd`.
4. Tous les fichiers indiqués ensuite doivent être créés dans ce dossier, sauf mention contraire.

---

## Les 14 séances du cours

---

### Partie I — Fondamentaux de l'Agentic AI

#### [Séance 1 — Architecture des LLMs & Genèse Agentique](lectures/01-llm-architectures-agentic.md)

| | |
|---|---|
| **Théorie** | De GPT-3 à 2026 : scaling laws, MoE, MLA, GQA, émergence du comportement agentique |
| **TP** | Installer l'environnement, comprendre les tokens, visualiser l'architecture |
| **⏱ Durée** | 2h |
| **Prérequis** | Python 3.10+, pip |

```bash
# Vérifications avant de commencer
python3 --version && pip --version
```

---

#### [Séance 2 — Context Window Engineering](lectures/02-context-window-engineering.md)

| | |
|---|---|
| **Théorie** | Fenêtre de contexte : attention O(n²), KV cache, limites GPU, stratégies d'optimisation |
| **TP** | Implémenter un sliding window, tester la compression de contexte |
| **⏱ Durée** | 2h |
| **Prérequis** | Séance 1 terminée, Python |

```bash
# Aucune dépendance supplémentaire
```

---

#### [Séance 3 — Systèmes de Mémoire pour Agents](lectures/03-memoire-systemes-agentiques.md)

| | |
|---|---|
| **Théorie** | Mémoire épisodique, sémantique, procédurale. Continuum Memory Architecture |
| **TP** | Implémenter une mémoire hiérarchique avec consolidation STM → LTM |
| **⏱ Durée** | 2h |
| **Prérequis** | Séance 2 terminée, Python |

```bash
# Linux/macOS
python3 -m pip install sentence-transformers

# Windows PowerShell
py -m pip install sentence-transformers
```

---

### Partie II — Protocoles & Standards 2026

#### [Séance 4 — Model Context Protocol (MCP)](lectures/04-mcp-protocol.md)

| | |
|---|---|
| **Théorie** | Architecture MCP : Host, Client, Server. JSON-RPC 2.0, transports, primitives |
| **TP** | Créer un serveur MCP complet avec tools, resources et prompts |
| **⏱ Durée** | 3h |
| **Prérequis** | Séance 3 terminée, Python |

```bash
# Linux/macOS
python3 -m pip install mcp

# Windows PowerShell
py -m pip install mcp
```

---

#### [Séance 5 — Agent-to-Agent Protocol (A2A)](lectures/05-a2a-protocol.md)

| | |
|---|---|
| **Théorie** | Google DeepMind A2A : Agent Cards, task lifecycle, découverte de capacités |
| **TP** | Implémenter un agent A2A avec Agent Card et communication inter-agents |
| **⏱ Durée** | 2h |
| **Prérequis** | Séance 4 terminée, Python |

```bash
# Linux/macOS
python3 -m pip install a2a-sdk

# Windows PowerShell
py -m pip install a2a-sdk
```

---

#### [Séance 6 — GitHub Agents & Platform](lectures/06-github-agents-platform.md)

| | |
|---|---|
| **Théorie** | GitHub Copilot coding agent, custom agents, session management, sécurité |
| **TP** | Configurer un custom agent GitHub avec hooks et MCP |
| **⏱ Durée** | 3h |
| **Prérequis** | Séance 5 terminée, Python, compte GitHub |

```bash
# Vérifier GitHub CLI
gh --version
```

---

### Partie III — Frameworks & Orchestration

#### [Séance 7 — LangChain & LangGraph](lectures/07-langgraph-framework.md)

| | |
|---|---|
| **Théorie** | Architecture LangChain, LangGraph : graphes d'état, cycles, checkpointing |
| **TP** | Implémenter un workflow agentique avec LangGraph |
| **⏱ Durée** | 3h |
| **Prérequis** | Séance 6 terminée, Python |

```bash
# Linux/macOS
python3 -m pip install langgraph langchain-core

# Windows PowerShell
py -m pip install langgraph langchain-core
```

---

#### [Séance 8 — CrewAI & AutoGen](lectures/08-crewai-autogen-comparison.md)

| | |
|---|---|
| **Théorie** | CrewAI : agents rôle-based. AutoGen : agents conversationnels |
| **TP** | Comparer les 4 frameworks sur un cas d'usage identique |
| **⏱ Durée** | 2h |
| **Prérequis** | Séance 7 terminée, Python |

```bash
# Linux/macOS
python3 -m pip install crewai autogen-agentchat

# Windows PowerShell
py -m pip install crewai autogen-agentchat
```

---

#### [Séance 9 — Agentic RAG & Knowledge Systems](lectures/09-agentic-rag-knowledge.md)

| | |
|---|---|
| **Théorie** | RAG 2.0 : agentic RAG, self-correcting retrieval, multi-hop queries |
| **TP** | Implémenter un backend RAG avec vector store local |
| **⏱ Durée** | 3h |
| **Prérequis** | Séance 8 terminée, Python |

```bash
# Linux/macOS
python3 -m pip install chromadb

# Windows PowerShell
py -m pip install chromadb
```

---

### Partie IV — Optimisation & Production

#### [Séance 10 — Fine-tuning & RL pour Agents](lectures/10-finetuning-rl-agents.md)

| | |
|---|---|
| **Théorie** | ATLAS, rubric-based RL, GRPO, curriculum learning |
| **TP** | Implémenter un pipeline de fine-tuning pour tool calling |
| **⏱ Durée** | 2h |
| **Prérequis** | Séance 9 terminée, Python |

```bash
# Aucune dépendance supplémentaire — concepts théoriques
```

---

#### [Séance 11 — Optimisation Mémoire & Contexte](lectures/11-optimisation-memoire-contexte.md)

| | |
|---|---|
| **Théorie** | Token budgets, KV cache quantization, attention sparse, compression |
| **TP** | Configurer un système d'optimisation mémoire pour production |
| **⏱ Durée** | 2h |
| **Prérequis** | Séance 10 terminée, Python |

```bash
# Aucune dépendance supplémentaire
```

---

#### [Séance 12 — Benchmarks & Évaluation](lectures/12-benchmarks-evaluation.md)

| | |
|---|---|
| **Théorie** | SWE-bench, SWE-Compass, métriques, contamination, outils de monitoring |
| **TP** | Créer un évaluateur de benchmark personnalisé |
| **⏱ Durée** | 2h |
| **Prérequis** | Séance 11 terminée, Python |

```bash
# Linux/macOS
python3 -m pip install langsmith

# Windows PowerShell
py -m pip install langsmith
```

---

#### [Séance 13 — Déploiement & Production](lectures/13-deploiement-production.md)

| | |
|---|---|
| **Théorie** | Architecture de production, CI/CD, sécurité, monitoring, coûts |
| **TP** | Mettre en place une pipeline CI/CD complète avec audit sécurité |
| **⏱ Durée** | 2h |
| **Prérequis** | Séance 12 terminée, Python, GitHub |

```bash
# Vérifier GitHub CLI
gh --version
```

---

### Partie V — Frontières & Futur

#### [Séance 14 — Agentic AI : Défis & Opportunités](lectures/14-frontieres-futur.md)

| | |
|---|---|
| **Théorie** | DiffMAS, ACE, self-evolving agents, robot agents, gouvernance |
| **TP** | Projet final : présenter une architecture agentique complète |
| **⏱ Durée** | 2h |
| **Prérequis** | Toutes les séances 1-13 terminées |

```bash
# Vérification finale
python --version && opencode --version && git --version && gh --version
```

---

## Stack technique

| Outil | Rôle | Coût |
|---|---|---|
| [opencode](https://opencode.ai) | Plateforme agentic | Gratuit |
| `opencode/big-pickle` | Modèle LLM gratuit | Gratuit |
| Python 3.10+ | Langage de développement | Gratuit |
| SQLite / ChromaDB | Bases de données | Gratuit |
| Docker | Conteneurisation | Gratuit |
| GitHub Actions | CI/CD | Gratuit |
| MCP SDK | Serveurs Model Context Protocol | Gratuit |
| LangGraph | Orchestration de workflows | Gratuit |

---

## Comment utiliser ce cours

1. **Suivez l'ordre** — chaque séance suppose les connaissances de la précédente
2. **Lisez la théorie** — les concepts sont illustrés de schémas et d'exemples
3. **Faites les prérequis** — les commandes d'installation sont en tête de chaque séance
4. **Réalisez le TP** — fichiers à créer, commandes à exécuter, résultat attendu
5. **Validez avec la checklist** — tout est vert ? Passez à la suite

---

## Projet fil rouge — AI Developer Assistant

Chaque TP construit une pièce du projet final défini dans le
[**Cahier des Charges**](PROJECT.md).

| Séance | Contribution au projet |
|--------|------------------------|
| S1-S3 | Environnement + compréhension LLM + mémoire |
| S4-S6 | Protocoles MCP/A2A + GitHub Agents |
| S7-S9 | Frameworks d'orchestration + RAG |
| S10-S13 | Optimisation + benchmarks + déploiement |
| S14 | **Projet complet présenté en fin de cours** |

---

## Ressources

- [Syllabus complet](syllabus/README.md)
- [Template de séance](syllabus/TEMPLATE.md)
- [Glossaire](GLOSSARY.md)
- [Bibliographie](resources/bibliography.md)
- [Checklists de validation](CHECKLIST.md)
- [Documentation opencode](https://opencode.ai)
- [Cahier des charges du projet](PROJECT.md)

---

## Licence

Ce cours est destiné à un usage pédagogique. Toute reproduction doit mentionner l'auteur.

**Auteur :** yugmerabtene
