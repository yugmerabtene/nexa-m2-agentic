# Lab 2 — Agentic RAG & Knowledge Systems (M2 Nexa 2026)

**Durée:** ~15h (5 parties)
**Prérequis:** Lab 1 complété (AI Developer Assistant)
**Objectif:** Étendre l'assistant avec des capacités de recherche intelligente, mémoire vectorielle, et Knowledge Graphs.

> Ce lab est la suite directe du Lab 1. Vous ajoutez des capacités RAG (Retrieval-Augmented Generation) à votre AI Developer Assistant.

---

## Architecture RAG

```
┌──────────────────────────────────────────────────┐
│              AI Developer Assistant + RAG          │
├──────────────────────────────────────────────────┤
│                                                    │
│  ┌──────────────┐        ┌──────────────────┐    │
│  │  Orchestrator │──────►│    RAG Pipeline    │    │
│  │  (Lab 1)     │        │                    │    │
│  └──────┬───────┘        │  Query → Retrieve   │    │
│         │                │  → Rerank → Generate│    │
│         │                └────────┬───────────┘    │
│         │                         │                │
│         │                ┌────────▼───────────┐   │
│         │                │  Vector Store        │   │
│         │                │  (ChromaDB local)    │   │
│         │  │  Embeddings (via API ou local) │
│         │                └────────────────────┘   │
│         │                                         │
│         └──────────────┬──────────────────────┘   │
│                        │                          │
│  ┌─────────────────────▼──────────────────────┐  │
│  │  Knowledge Graph (optionnel)                │  │
│  │  Entités → Relations → Inférences          │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

---

## Plan du Lab 2 (5 parties)

### Partie 1: Embeddings & Vector Store (3h)

**Objectif:** Installer et configurer ChromaDB avec embeddings (via modèle opencode ou sentence-transformers).

**Fichiers:** `lab/code/09_rag/`

**À faire:**
1. Installer ChromaDB: `pip install chromadb`
2. Créer un pipeline d'indexation: documents → chunks → embeddings → store
3. Implémenter la recherche sémantique (cosine similarity)
4. Ajouter un outil MCP `semantic_search` au serveur
5. Tester avec un corpus de documentation technique

**Concepts:** chunking, embedding, vector search, metadata filtering

---

### Partie 2: Agentic RAG — Self-Correcting Retrieval (3h)

**Objectif:** L'agent auto-corrige ses requêtes RAG.

**Fichiers:** `lab/code/09_rag/`

**À faire:**
1. Implémenter le query rewriting (l'agent reformule sa requête)
2. Ajouter un juge qui évalue la pertinence des chunks retrievés
3. Boucle de correction: retrieve → evaluate → re-retrieve si nécessaire
4. Multi-hop: l'agent pose des sous-questions pour des requêtes complexes

**Concepts:** query rewriting, relevancy evaluation, multi-hop RAG, self-correction

---

### Partie 3: Contextual Compression & Reranking (3h)

**Objectif:** Optimiser le contexte avant injection dans le prompt.

**Fichiers:** `lab/code/09_rag/`

**À faire:**
1. Implémenter le reranking (cross-encoder léger ou LLM-based)
2. Ajouter la compression contextuelle: extraire seulement les phrases pertinentes
3. Créer un sliding window de contexte avec priorité
4. Benchmark: qualité vs nombre de tokens avant/après compression

**Concepts:** reranking, contextual compression, extractive summarization, token budget

---

### Partie 4: GraphRAG & Knowledge Graph (3h)

**Objectif:** Extraire et utiliser un graphe de connaissances.

**Fichiers:** `lab/code/09_rag/`

**À faire:**
1. Extraire des entités et relations du corpus avec big-pickle
2. Construire un Neo4j ou JSON-based Knowledge Graph
3. Implémenter la recherche par parcours de graphe
4. Combiner vector search + graph traversal (hybrid retrieval)
5. L'agent utilise le graphe pour répondre à des questions multi-étapes

**Concepts:** entity extraction, relation extraction, graph traversal, hybrid retrieval

---

### Partie 5: Intégration RAG dans l'Assistant (3h)

**Objectif:** Connecter le pipeline RAG à l'AI Developer Assistant du Lab 1.

**Fichiers:** `lab/code/10_rag_integration/`

**À faire:**
1. Ajouter les tools RAG au serveur MCP existant
2. Connecter l'orchestrateur LangGraph au pipeline RAG
3. Ajouter la mémoire vectorielle comme couche de long-term memory
4. Mettre à jour la CI/CD avec les tests RAG
5. Benchmark end-to-end: assistant sans RAG vs avec RAG

---

## Validation

```bash
# Indexer les documents
python lab/code/09_rag/index.py --docs lab/corpus/

# Lancer la recherche RAG
python lab/code/10_rag_integration/rag_query.py --query "explique les patterns agentiques"

# Tester l'assistant avec RAG
python lab/code/10_rag_integration/assistant_rag.py --prompt "compare les frameworks en citant les sources"

# Benchmarks
pytest lab/tests/test_rag.py -v --benchmark
```

## Références
- Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (2020)
- ChromaDB: https://trychroma.com
- Sentence-Transformers: https://sbert.net
- GraphRAG: https://microsoft.github.io/graphrag/
