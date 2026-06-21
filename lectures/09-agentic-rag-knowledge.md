# Séance 9 — Agentic RAG & Knowledge Systems

> **Auteur :** yugmerabtene
> **Version :** 2.0
> **Durée estimée :** 3 heures

---

## Description

Cette séance explore le RAG agentique (Retrieval-Augmented Generation), une évolution du RAG classique qui intègre des boucles de correction et de décision. Vous apprendrez à implémenter un self-correcting retrieval, des multi-hop queries, et à intégrer des knowledge graphs. Cette séance fait le pont entre les frameworks d'orchestration (séance 8) et le fine-tuning (séance 10).

---

## Prérequis

Avant de commencer cette séance, assurez-vous d'avoir :

- Terminé la **Séance 8** et compris les frameworks d'orchestration
- Python 3.10+ installé
- Connaissances de base en embeddings et vector stores

### Installation des dépendances

#### Linux et macOS

```bash
# Vérifier Python
python3 --version

# Installer ChromaDB pour le vector store
python3 -m pip install chromadb

# Vérifier l'installation
python3 -c "import chromadb; print('ChromaDB installé')"
```

#### Windows PowerShell

```powershell
# Vérifier Python
py --version

# Installer ChromaDB pour le vector store
py -m pip install chromadb

# Vérifier l'installation
py -c "import chromadb; print('ChromaDB installé')"
```

> **Résultat attendu :** ChromaDB est installé et importable.

---

## Introduction théorique

**Quel est le problème fondamental ?**

Le RAG classique suit un pipeline linéaire : `chunk → embed → retrieve → generate`. Il échoue sur quatre types de questions :

1. **Multi-hop** — *"Quel framework utilise le checkpointing et qui l'a créé ?"* nécessite deux retrievals distincts.
2. **Ambiguës** — *"Comment gérer la mémoire ?"* peut référer à la STM, LTM, vectorielle ou épisodique.
3. **Contradictoires** — Deux documents opposés sont fusionnés sans conscience du conflit.
4. **Pertinence insuffisante** — Un mauvais retrieval pollue toute la réponse, sans boucle de correction.

**Où se situe ce concept dans l'écosystème agentique 2026 ?**

Trois générations : **RAG Naïf (2023)** embed→retrieve→generate en une passe ; **RAG Avancé (2024)** HyDE, re-ranking, chunking adaptatif mais toujours linéaire ; **Agentic RAG (2025-2026)** l'agent contrôle *quand*, *quoi*, *comment* chercher et *si* le résultat est suffisant. *Self-RAG* (Asai et al., 2023) introduit la réflexion sur les documents ; *Corrective RAG* (Yan et al., 2024) ajoute évaluation et correction.

**Lien avec les séances :**

- **Séance 8 (CrewAI/AutoGen)** : collaboration multi-agents → ici un seul agent orchestre son propre retrieval.
- **Séance 10 (Fine-tuning & RL)** : les politiques de retrieval codées manuellement ici seront optimisées par RL.

> *"Séance 8 : des agents collaborent. Séance 9 : un agent orchestre son retrieval. Séance 10 : le RL optimise les politiques."*

## Objectifs pédagogiques

1. **Analyser** les limites du RAG classique (multi-hop, ambiguïté, contradiction) et justifier l'agentic RAG.
2. **Concevoir** une architecture agentic RAG : décomposition → retrieval → évaluation → reformulation → génération.
3. **Implémenter** une boucle de self-correcting retrieval avec évaluation et reformulation automatique.
4. **Implémenter** un mécanisme multi-hop avec décomposition, retrieval parallèle et fusion.
5. **Construire** un RAGBackend complet avec sentence-transformers et délégation opencode task.

## Plan détaillé

### 9.1 Du RAG classique à l'Agentic RAG

#### Définition

> **Définition :** L'Agentic RAG est un paradigme où un agent LLM contrôle activement le processus de recherche — décomposition, sélection des sources, évaluation, reformulation itérative — plutôt que de subir un pipeline fixe.

#### Tableau comparatif

| Aspect | RAG Naïf (2023) | RAG Avancé (2024) | Agentic RAG (2026) |
|--------|-----------------|-------------------|---------------------|
| Recherche | 1 shot | Multi-stratégie | Auto-décidée |
| Chunking | Fixe | Adaptatif | Dynamique |
| Évaluation | Aucune | Re-ranking | Self-correcting loop |
| Outils | Vector only | Vector + fusion | Multi-outils |
| Mémoire | Aucune | Cache | Historique complet |
| Décision | Pipeline linéaire | Pipeline paramétré | **L'agent décide** |

#### Schéma d'évolution

```
RAG Naïf :      Q ──► Embed ──► Retrieve ──► Generate ──► R
RAG Avancé :    Q ──► Transform ──► Embed ──► Retrieve ──► Rerank ──► Generate ──► R
Agentic RAG :   Q ──► Décompose ──► ┌──────────────────────┐
                ◄───────────────────│ Agent loop           │
                Reformulation ──► Embed ──► Retrieve ──► Évaluer
                                    │ (self-correcting)    │
                                    └──────────────────────┘
                                               │
                                          Generate ──► R
```

#### Pourquoi c'est crucial

Sans agentic RAG, les questions complexes produisent des réponses incorrectes sans que l'utilisateur puisse détecter l'échec. L'architecture passe de *data flow* à *agent loop* : le retrieval devient un outil que l'agent décide d'utiliser, pas une étape imposée.

---

### 9.2 Architecture Agentic RAG

Le cycle complet en six étapes :

```
                    QUESTION
                        │
                        ▼
               ┌────────────────┐
               │ 1. DÉCOMPOSER  │
               │ (sous-questions)│
               └────────┬───────┘
                        ▼
               ┌────────────────┐
               │ 2. RETRIEVER   │
               │ (embed + search)│
               └────────┬───────┘
                        ▼
               ┌────────────────┐
               │ 3. ÉVALUER     │◄────┐
               │ (pertinence)   │     │
               └────────┬───────┘     │
                        │             │
                 ┌──────┴──────┐      │
                 ▼             ▼      │
           Score ≥ seuil  Score < seuil│
                 │             │      │
                 ▼             ▼      │
           ┌──────────┐ ┌──────────┐  │
           │4. GÉNÉRER│ │5. REFORMU│──┘
           └────┬─────┘ │  LER    │
                │       └──────────┘
                ▼
            RÉPONSE
```

Chaque étape est une décision de l'agent : *faut-il décomposer ? quel outil de retrieval ? les documents sont-ils pertinents ? comment reformuler ?*

---

### 9.3 Self-correcting retrieval

#### Définition

> **Définition :** Mécanisme où le système évalue la qualité des documents récupérés et décide itérativement de reformuler la requête jusqu'à un seuil de pertinence acceptable, ou jusqu'à épuisement des tentatives.

#### Boucle de rétroaction

```
Requête ──► Embed ──► Search ──► Évaluer ──► [score ≥ seuil] ──► Générer
                                              │
                                         [score < seuil]
                                              │
                                          Reformuler ──► Embed ──► Search ──► ...
```

#### Composants

1. **Embedding** : sentence-transformers transforme la requête en vecteur.
2. **Search** : similarité cosinus dans le vector store SQLite.
3. **Évaluation** : opencode task évalue chaque document sur 0.0–1.0.
4. **Reformulation** : si la pertinence < seuil (0.6), l'agent reformule.
5. **Itération** : maximum N=3 tentatives avant fallback.

#### Pourquoi c'est crucial

Sans self-correction, une seule mauvaise requête ruine toute la réponse. La boucle permet de détecter l'échec et de corriger la trajectoire.

---

### 9.4 Multi-hop queries

#### Définition

> **Définition :** Requête nécessitant plusieurs étapes de retrieval indépendantes, où chaque étape produit un résultat partiel qui sert de contexte à l'étape suivante.

#### Principe

```
Question originale : "Quel langage utilise LangGraph et qui l'a créé ?"

Décomposition :
1. "Qu'est-ce que LangGraph ?" ──► [doc: framework de graphe d'état]
2. "En quel langage ?"          ──► [doc: Python]
3. "Qui l'a créé ?"             ──► [doc: équipe LangChain]

Fusion : "LangGraph est un framework Python créé par l'équipe LangChain..."
```

#### Types

| Type | Description | Exemple |
|------|-------------|---------|
| Séquentiel | Chaque étape dépend de la précédente | "Qui a créé le framework X ?" |
| Parallèle | Sous-questions indépendantes | "Compare LangGraph et CrewAI" |
| Hiérarchique | Niveaux de granularité | "Frameworks agents → mémoire → comment ?" |

---

### 9.5 Construction guidée — RAGBackend complet

```python
# === AGENTIC RAG — SYSTÈME COMPLET ===
# Fichier : lab/code/09_agentic_rag/rag_backend.py
# Dépendances : sentence-transformers
#
# Embeddings via sentence-transformers (local).
# Génération LLM déléguée à opencode/big-pickle via task().
# Vector store SQLite avec similarité cosinus.

import json
# ↑ Sérialisation JSON pour stocker les embeddings en BLOB SQLite.

import sqlite3
# ↑ Base de données embarquée. Zéro configuration, zéro serveur.

import time
# ↑ Timestamp UNIX pour horodater l'indexation.

from pathlib import Path
# ↑ Chemins de fichiers cross-platform.

from typing import Any
# ↑ Typage des dictionnaires de métadonnées.

from sentence_transformers import SentenceTransformer
# ↑ Embeddings locaux. Modèle téléchargé depuis Hugging Face,
#   puis utilisé hors-ligne. Pas d'API, pas de serveur.


class RAGBackend:
    """Interface unifiée : embedding, génération, évaluation, décomposition.

    Embedding : sentence-transformers (local)
    Génération : déléguée à opencode/big-pickle via task()
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # ↑ Charge le modèle d'embeddings (384 dimensions, bon équilibre
        #   qualité/vitesse). all-mpnet-base-v2 (768 dims) en alternative.
        self.encoder = SentenceTransformer(model_name)

    def embed(self, text: str) -> list[float]:
        # ↑ Texte → vecteur flottant. Sortie numpy convertie en liste
        #   pour le stockage JSON dans SQLite.
        return self.encoder.encode(text).tolist()

    def generate(self, prompt: str, system: str = "") -> str:
        # ↑ Délègue la génération à opencode/big-pickle.
        #   En production : task(agent="big-pickle", prompt=prompt).
        #   Ici, placeholder illustrant le pattern de délégation.
        return f"[Généré par opencode/big-pickle]\n{prompt[:100]}..."

    def evaluate(self, text: str, query: str) -> float:
        # ↑ Évalue la pertinence d'un document pour une requête.
        #   L'agent opencode retourne un score 0.0–1.0.
        prompt = (
            f"Sur une échelle de 0.0 à 1.0, ce texte est-il pertinent "
            f"pour '{query}' ? Réponds uniquement par le nombre."
            f"\n\nTexte: {text[:500]}"
        )
        result = self.generate(prompt)
        try:
            return float(result.strip())
        except (ValueError, TypeError):
            return 0.5
            # ↑ Fallback : score neutre si le LLM ne retourne pas un nombre.

    def decompose(self, question: str) -> list[str]:
        # ↑ Décompose une question complexe en sous-questions atomiques.
        #   Le format JSON facilite le parsing.
        prompt = (
            f"Décompose cette question en sous-questions simples "
            f"et indépendantes. Retourne une liste JSON de strings."
            f"\nQuestion: {question}"
        )
        result = self.generate(prompt)
        try:
            sub_qs = json.loads(result)
            if isinstance(sub_qs, dict):
                sub_qs = list(sub_qs.values())
                # ↑ Certains LLM retournent {"1": "...", "2": "..."}
            return sub_qs
        except (json.JSONDecodeError, TypeError):
            return [question]
            # ↑ Fallback : question unique si le parsing échoue.


class SQLiteVectorStore:
    """Vector store SQLite. Recherche par similarité cosinus en O(n).
    Suffisant pour le prototypage (jusqu'à ~10⁵ vecteurs).
    """

    def __init__(self, db_path: str = "agentic_rag.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                embedding BLOB,
                metadata TEXT,
                created_at REAL
            )
        """)
        self.conn.commit()

    def add(self, content: str, embedding: list[float],
            metadata: dict | None = None) -> int:
        # ↑ Stocke un document avec son embedding pré-calculé.
        cursor = self.conn.execute(
            "INSERT INTO documents (content, embedding, metadata, created_at) "
            "VALUES (?, ?, ?, ?)",
            (content, json.dumps(embedding).encode(),
             json.dumps(metadata or {}), time.time()),
        )
        self.conn.commit()
        return cursor.lastrowid

    def search(self, query_emb: list[float],
               top_k: int = 5) -> list[dict[str, Any]]:
        # ↑ Parcourt tous les documents et calcule la similarité cosinus.
        results = []
        for row in self.conn.execute(
            "SELECT id, content, embedding, metadata FROM documents"
        ):
            stored_emb = json.loads(row[2].decode())
            score = self._cosine_similarity(query_emb, stored_emb)
            results.append({
                "id": row[0], "content": row[1],
                "metadata": json.loads(row[3]), "score": score,
            })
        results.sort(key=lambda r: r["score"], reverse=True)
        return results[:top_k]

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        # ↑ cos(θ) = (A·B) / (||A|| × ||B||)
        dot = sum(x * y for x, y in zip(a, b))
        na = sum(x * x for x in a) ** 0.5
        nb = sum(y * y for y in b) ** 0.5
        return dot / (na * nb) if na * nb > 0 else 0.0


class AgenticRAG:
    """Système RAG agentique complet avec self-correction et multi-hop."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # ↑ Initialise le backend embeddings et le vector store.
        self.backend = RAGBackend(model_name=model_name)
        self.store = SQLiteVectorStore()
        self.conversation_history: list[dict[str, str]] = []

    def ingest_text(self, content: str,
                    metadata: dict | None = None) -> int:
        # ↑ Calcule l'embedding et indexe le texte dans SQLite.
        embedding = self.backend.embed(content)
        return self.store.add(content, embedding, metadata)

    def ingest_file(self, path: str) -> list[int]:
        # ↑ Lit, chuque et indexe un fichier texte.
        content = Path(path).read_text(encoding="utf-8")
        ids = []
        for chunk in self._chunk_text(content):
            ids.append(self.ingest_text(chunk, {"source": path}))
        return ids

    @staticmethod
    def _chunk_text(text: str, chunk_size: int = 500,
                    overlap: int = 50) -> list[str]:
        # ↑ Découpage word-level avec overlap pour ne pas couper
        #   une phrase importante en deux.
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size - overlap):
            chunks.append(" ".join(words[i:i + chunk_size]))
        return chunks

    def query(self, question: str, use_self_correct: bool = True,
              use_multi_hop: bool = True) -> str:
        # ↑ Point d'entrée. Trois modes de retrieval.
        if use_multi_hop:
            answer = self._multi_hop_answer(question)
        elif use_self_correct:
            answer = self._self_correct_answer(question)
        else:
            answer = self._simple_answer(question)
        self.conversation_history.append(
            {"role": "user", "question": question})
        self.conversation_history.append(
            {"role": "assistant", "answer": answer})
        return answer

    def _simple_answer(self, question: str) -> str:
        # ↑ RAG classique : embed → search → generate (baseline).
        emb = self.backend.embed(question)
        docs = self.store.search(emb, top_k=3)
        context = "\n\n".join(d["content"] for d in docs)
        return self.backend.generate(
            prompt=f"Question: {question}\n\nContexte:\n{context}",
            system="Réponds précisément en te basant sur le contexte.",
        )

    def _self_correct_answer(self, question: str) -> str:
        # ↑ Boucle de self-correction : recherche → évalue → reformule.
        emb = self.backend.embed(question)
        docs = self.store.search(emb, top_k=5)

        relevance = self.backend.evaluate(
            "\n".join(d["content"][:200] for d in docs), question)
        # ↑ L'agent évalue la pertinence des documents trouvés.

        if relevance < 0.6:
            # ↑ Seuil : si la pertinence est insuffisante, reformulation.
            refined = self.backend.generate(
                prompt=f"Reformule cette requête pour meilleure recherche: {question}"
            )
            emb = self.backend.embed(refined)
            docs = self.store.search(emb, top_k=5)

        return self.backend.generate(
            prompt=f"Question: {question}\n\nDocuments:\n"
                   f"{chr(10).join(d['content'][:500] for d in docs)}"
        )

    def _multi_hop_answer(self, question: str) -> str:
        # ↑ Multi-hop : décomposition → retrievals → fusion.
        sub_questions = self.backend.decompose(question)
        partials = []

        for i, sub_q in enumerate(sub_questions):
            # ↑ Contexte des 3 dernières réponses pour le chaînage.
            context = "; ".join(partials[-3:]) if partials else ""
            contextual_q = f"[{context}] {sub_q}" if context else sub_q

            emb = self.backend.embed(contextual_q)
            docs = self.store.search(emb, top_k=3)

            answer = self.backend.generate(
                prompt=f"Sous-question {i+1}: {sub_q}\n\nDocuments:\n"
                       f"{chr(10).join(d['content'] for d in docs)}"
            )
            partials.append(f"{sub_q}: {answer}")

        # ↑ Fusion : synthèse finale à partir des réponses partielles.
        return self.backend.generate(
            prompt=f"Synthèse des étapes:\n{chr(10).join(partials)}"
                   f"\n\nQuestion originale: {question}"
        )

    def chat(self, message: str) -> str:
        # ↑ Mode conversationnel avec historique des 6 derniers échanges.
        history = "\n".join(
            f"{'User' if m['role']=='user' else 'Assistant'}: "
            f"{m.get('question', m.get('answer', ''))}"
            for m in self.conversation_history[-6:]
        )
        ctx = f"Historique:\n{history}\n\n" if history else ""
        return self.query(f"{ctx}{message}")


# === EXEMPLE D'UTILISATION ===
if __name__ == "__main__":
    rag = AgenticRAG()

    # Indexation de documents de référence
    rag.ingest_text(
        "LangGraph orchestre les agents avec un graphe d'état. "
        "Le checkpointing sauvegarde et restaure les sessions.",
        {"source": "lecture_07", "topic": "langgraph"},
    )
    rag.ingest_text(
        "CrewAI définit des agents avec rôles, goals et tools. "
        "L'orchestration est séquentielle ou hiérarchique.",
        {"source": "lecture_08", "topic": "crewai"},
    )
    rag.ingest_text(
        "La mémoire persistante utilise des embeddings vectoriels. "
        "Les solutions 2026 incluent HydraDB et OMEGA.",
        {"source": "lecture_03", "topic": "memory"},
    )

    print("--- Simple ---")
    print(rag.query("Qu'est-ce que le checkpointing ?",
                    use_self_correct=False, use_multi_hop=False))

    print("\n--- Self-correcting ---")
    print(rag.query("Quels frameworks utilisent des embeddings ?",
                    use_self_correct=True, use_multi_hop=False))

    print("\n--- Multi-hop ---")
    print(rag.query(
        "Compare LangGraph et CrewAI sur la gestion de la mémoire.",
        use_multi_hop=True,
    ))
```

**Scénario concret :**

1. L'utilisateur pose une question complexe.
2. `AgenticRAG.query()` active le mode multi-hop.
3. `RAGBackend.decompose()` génère les sous-questions via opencode task.
4. `SQLiteVectorStore.search()` retrouve les documents par similarité cosinus.
5. `RAGBackend.evaluate()` vérifie la pertinence ; si < 0.6, reformulation.
6. `RAGBackend.generate()` (opencode task) produit la réponse finale.
7. L'historique est mis à jour pour les questions suivantes.

---

## Synthèse

| Concept | Résumé | Section |
|---------|--------|---------|
| Évolution RAG | Trois générations de 2023 à 2026. L'agent contrôle le retrieval. | 9.1 |
| Architecture | Cycle en 6 étapes : décomposer → retriever → évaluer → reformuler → générer. | 9.2 |
| Self-correcting | Boucle de rétroaction avec évaluation, reformulation, re-retrieval. | 9.3 |
| Multi-hop | Décomposition, retrieval parallèle, fusion en réponse finale. | 9.4 |
| RAGBackend | Implémentation complète : sentence-transformers + SQLite + opencode task. | 9.5 |

**Lien avec la séance 10 :** Les politiques de retrieval que nous avons codées manuellement (seuils, boucles, décomposition) seront optimisées par fine-tuning et apprentissage par renforcement. L'architecture RAGBackend devient l'environnement cible du RL.

## Références contextualisées

- **[Asai et al., "Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection" (2023)]**
  *Contexte :* Fondation du self-correcting retrieval. Le modèle apprend à décider quand retriever et quand critiquer.
  *Niveau :* Avancé → https://arxiv.org/abs/2310.11511

- **[Yan et al., "Corrective Retrieval Augmented Generation" (2024)]**
  *Contexte :* Extension avec correction explicite (reformulation, web search). Base de la section 9.3.
  *Niveau :* Avancé → https://arxiv.org/abs/2401.15884

- **[Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (2020)]**
  *Contexte :* Article fondateur du RAG. Point de départ de l'évolution (section 9.1).
  *Niveau :* Introduction → https://arxiv.org/abs/2005.11401

- **[Gao et al., "RAG for LLMs: A Survey" (2024)]**
  *Contexte :* Survey 2020–2024 couvrant toutes les générations. Source du tableau comparatif.
  *Niveau :* Introduction → https://arxiv.org/abs/2312.10997

- **[Documentation sentence-transformers]**
  *Contexte :* API pour les modèles d'embeddings utilisés en section 9.5.
  *Niveau :* Technique → https://www.sbert.net/

- **[Documentation SQLite]**
  *Contexte :* Syntaxe SQL et stockage BLOB pour le vector store de la section 9.5.
  *Niveau :* Technique → https://www.sqlite.org/docs.html

---

## Lab associé

```bash
# LAB : Construction d'un système Agentic RAG
# Objectif : Implémenter et tester le RAGBackend
# Durée : 4h | Prérequis : Séance 9 + pip install sentence-transformers
#
# 1. Copier le code section 9.5 dans lab/code/09_agentic_rag/
# 2. Ingérer 3 fichiers .md du syllabus
# 3. Tester les 3 modes (simple, self-correct, multi-hop)
# 4. Ajouter un mode chat avec historique persistant
```

Voir `lab/README.md` — Partie 4 pour les instructions complètes.
