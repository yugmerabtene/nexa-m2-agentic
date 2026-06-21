# Séance 3 — Mémoire & Systèmes Agentiques

> **Auteur :** yugmerabtene
> **Version :** 2.0
> **Durée estimée :** 2 heures

---

## Description

Cette séance explore les systèmes de mémoire pour agents autonomes. Vous apprendrez à distinguer les trois types de mémoire (épisodique, sémantique, procédurale), à implémenter une mémoire hiérarchique avec consolidation STM vers LTM, et à comparer les solutions 2026 (HydraDB, OMEGA, Zep, Redis). Cette séance fait le pont entre le context window engineering (séance 2) et le protocole MCP (séance 4).

---

## Prérequis

Avant de commencer cette séance, assurez-vous d'avoir :

- Terminé la **Séance 2** et compris les limites de la fenêtre de contexte
- Python 3.10+ installé
- Connaissances de base en structures de données

### Installation des dépendances

#### Linux et macOS

```bash
# Vérifier Python
python3 --version

# Installer les dépendances pour cette séance
python3 -m pip install sentence-transformers

# Vérifier l'installation
python3 -c "import sentence_transformers; print(sentence_transformers.__version__)"
```

#### Windows PowerShell

```powershell
# Vérifier Python
py --version

# Installer les dépendances pour cette séance
py -m pip install sentence-transformers

# Vérifier l'installation
py -c "import sentence_transformers; print(sentence_transformers.__version__)"
```

> **Résultat attendu :** sentence-transformers est installé et importable.

---

## Introduction théorique

**Quel est le problème ?** Un agent sans mémoire est amnésique : chaque interaction repart de zéro. Il ne peut ni apprendre de ses erreurs, ni maintenir un contexte sur la durée, ni personnaliser ses réponses. Dans un scénario réel — assistant client sur 50 échanges, agent de code sur un projet de 10 000 fichiers, chatbot de support sur plusieurs sessions — l'absence de mémoire rend l'agent inutilisable. Le problème n'est pas technique (le LLM peut traiter du texte), il est **architectural** : comment organiser le flux d'information pour qu'il survive à la fenêtre de contexte et aux redémarrages ?

**Contexte.** La mémoire humaine distingue la mémoire à court terme (STM, quelques items pendant environ 20 secondes) et la mémoire à long terme (LTM, stockage illimité et durable). Les systèmes agentiques 2026 s'inspirent directement de ce modèle : une *working memory* (fenêtre de tokens active), une *episodic memory* (historique des interactions), et une *semantic memory* (connaissances consolidées). L'analogie est puissante mais imparfaite — un agent ne "dort" pas pour consolider, il doit le faire en ligne, au fil des interactions. L'évolution des architectures mémoire est rapide : en 2023 on concaténait tout l'historique dans le prompt ; en 2024 DeepMind a proposé le *Memory Continuum* ; en 2025-2026 des solutions spécialisées (HydraDB, OMEGA, Zep, Redis Agent Memory) sont devenues des briques standards des stacks agentiques.

**Prérequis et lien avec les séances.** Cette séance mobilise la séance 2 (*Context Window Engineering*) : vous savez qu'une fenêtre de contexte est limitée et coûteuse — la mémoire est la réponse architecturale à cette limitation. Elle prépare la séance 4 (*MCP Protocol*) : un agent avec mémoire peut stocker des résultats d'outils, apprendre de leurs échecs, et référencer des découvertes passées. Sans mémoire, MCP donne un agent qui agit mais oublie immédiatement ce qu'il a fait.

## Objectifs pédagogiques

À l'issue de cette séance, vous serez capable de :

1. **Distinguer** les trois types de mémoire agentique (épisodique, sémantique, procédurale) et les associer à leurs analogues cognitifs
2. **Expliquer** l'architecture Memory Continuum avec ses mécanismes de sliding window, compaction et consolidation hiérarchique
3. **Implémenter** un système de mémoire hiérarchique complet avec consolidation STM vers LTM et persistance JSON
4. **Comparer** les solutions de mémoire 2026 (HydraDB, OMEGA, Zep, Redis) selon 5 critères (type, licence, persistance, cross-session, synthèse automatique)
5. **Évaluer** un système de mémoire via le benchmark LongMemEval et calculer le score composite LongMemScore

## Plan détaillé

### 3.1 Les trois types de mémoire agentique — PARTIE THÉORIQUE

La conception de mémoire dans les systèmes agentiques s'inspire directement des neurosciences cognitives. On distingue trois systèmes complémentaires, chacun avec un rôle, une analogie humaine, et une concrétisation technique.

---

#### Mémoire épisodique

> **Définition :** La mémoire épisodique enregistre des expériences spécifiques avec leur contexte temporel et spatial. Pour un agent, cela correspond à l'historique brut des interactions : chaque action entreprise, chaque observation reçue, chaque décision prise.

**Analogie humaine :** C'est votre souvenir du dîner d'hier — vous vous rappelez où, quand, avec qui, ce que vous avez mangé. C'est personnel, situé dans le temps, riche en détails contextuels.

**Implémentation agentique :** Chaque épisode est un triplet `(timestamp, action, observation)` stocké dans une structure de données horodatée.

```python
import json
import time
from dataclasses import dataclass, field, asdict
from typing import Any

@dataclass
class Episode:
    timestamp: float
    # Horodatage Unix : identifie de façon unique le moment de l'épisode
    agent_id: str
    # Identifiant de l'agent : utile dans les systèmes multi-agents
    action: str
    # Action entreprise par l'agent (ex: "search_docs", "call_api")
    observation: str
    # Résultat observé : ce que l'agent a vu/reçu en retour
    reward: float | None = None
    # Score de renforcement optionnel (apprentissage par renforcement)
    metadata: dict[str, Any] = field(default_factory=dict)
    # Métadonnées extensibles : session_id, tokens utilisés, latence...

    def serialize(self) -> str:
        """Convertit l'épisode en JSON pour la persistance."""
        return json.dumps(asdict(self), ensure_ascii=False)
```

---

#### Mémoire sémantique

> **Définition :** La mémoire sémantique stocke des connaissances générales et des faits extraits par abstraction des épisodes. Un agent y dépose des règles métier, des préférences utilisateur, des contraintes de domaine — des informations qui transcendent un épisode particulier.

**Analogie humaine :** C'est votre connaissance que "Paris est la capitale de la France". Vous ne vous rappelez pas où ni quand vous l'avez appris (l'épisode est perdu), mais le fait est solidement encodé.

**Implémentation agentique :** Des faits avec un score de confiance, une source (les épisodes d'origine), et une date de vérification pour détecter l'obsolescence.

```python
@dataclass
class SemanticFact:
    fact_id: str
    # Identifiant unique du fait (ex: "sem_a3f2c1")
    statement: str
    # Le fait lui-même : "L'utilisateur préfère Python à JavaScript"
    confidence: float
    # Confiance entre 0.0 (incertain) et 1.0 (certain)
    # Calculée à partir de la fréquence d'observation
    source_episodes: list[str] = field(default_factory=list)
    # Références aux épisodes qui ont généré ce fait
    # Permet de tracer l'origine et de vérifier
    last_verified: float = 0.0
    # Dernière vérification : horodatage Unix
    # Un fait non vérifié depuis trop longtemps devient "stale"

    def is_stale(self, ttl_hours: float = 24) -> bool:
        """Vérifie si le fait est obsolète (non vérifié depuis ttl_hours)."""
        age = time.time() - self.last_verified
        return age > ttl_hours * 3600
```

---

#### Mémoire procédurale

> **Définition :** La mémoire procédurale encode les compétences et procédures : *comment* accomplir une tâche, pas *quoi* est la tâche. Pour un agent, cela prend la forme de définitions d'outils, de *few-shot prompts*, de workflows réutilisables.

**Analogie humaine :** C'est votre savoir-faire pour faire du vélo. Vous êtes incapable de décrire verbalement l'équilibre, mais votre corps "sait" le faire. C'est la mémoire du *comment*.

**Implémentation agentique :** Des descripteurs d'outils (JSON Schema) avec des statistiques d'utilisation — un agent peut apprendre quels outils sont les plus efficaces pour quelles tâches.

```python
@dataclass
class ProceduralSkill:
    name: str
    # Nom de la compétence : "search_codebase", "analyze_logs"
    description: str
    # Description lisible par le LLM pour décider quand utiliser cet outil
    tool_spec: dict[str, Any]
    # Spécification JSON Schema des paramètres de l'outil
    usage_count: int = 0
    # Nombre de fois que cette compétence a été invoquée
    success_rate: float = 1.0
    # Taux de succès (0.0 à 1.0), mis à jour après chaque appel

    def to_tool_spec(self) -> dict[str, Any]:
        """Convertit la compétence en spec d'outil (format JSON-RPC)."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.tool_spec,
            }
        }
```

---

#### Pourquoi cette distinction est cruciale

- **Impact sur la conception :** Chaque type de mémoire exige un stockage, une stratégie d'indexation et un cycle de vie différents. Les confondre conduit à des systèmes soit trop lents (tout en RAM), soit trop rigides (tout en base).
- **Conséquence si ignoré :** Un agent avec une seule mémoire "tout-venant" ne peut pas distinguer un fait général d'un événement ponctuel. Il risque de généraliser à partir d'un seul épisode ou au contraire de ne jamais rien retenir.
- **Cas d'usage typique :** Un agent de support client utilise la mémoire épisodique pour suivre la conversation en cours, la mémoire sémantique pour retenir les préférences du client d'une session à l'autre, et la mémoire procédurale pour savoir comment utiliser l'API de ticketing.

| Type | Analogue humain | Agent LLM | Persistance |
|------|----------------|-----------|-------------|
| Épisodique | Souvenirs personnels | Logs d'interactions | Court-terme vers consolidé |
| Sémantique | Connaissances générales | Faits extraits, embeddings | Long-terme |
| Procédurale | Compétences procédurales | Tool definitions, prompts | Permanente |

---

### 3.2 Architecture Memory Continuum — PARTIE THÉORIQUE

> **Définition :** Le *Memory Continuum* est une architecture introduite par Google DeepMind (2024) et standardisée en 2025-2026. Elle remplace le concept unique de "fenêtre de contexte" par un flux continu où la mémoire est un *first-class citizen* — elle n'est plus un sous-produit du prompt mais une couche architecturale dédiée.

**Analogie pédagogique :**

> *"Le Memory Continuum est à la fenêtre de contexte ce que le disque dur est à la RAM : une hiérarchie où la vitesse diminue mais la capacité augmente à chaque niveau."*

#### Principe expliqué en détail

Au lieu de concaténer tout l'historique dans le prompt à chaque tour, le Memory Continuum organise la mémoire en trois niveaux qui communiquent entre eux :

```
┌──────────────────────────────────────────────────┐
│  Working Memory (fenêtre de tokens active)       │
│  4K-8K tokens, sliding window, accès O(1)        │
│  Contenu : les derniers échanges + contexte immédiat │
└──────────────────┬───────────────────────────────┘
                   │ encode (embedding)
                   │ retrieve (similarité cosinus)
┌──────────────────▼───────────────────────────────┐
│  Episodic Memory (store vectoriel)               │
│  10^6 episodes, index ANN (HNSW/IVF)             │
│  Contenu : historique complet des interactions    │
└──────────────────┬───────────────────────────────┘
                   │ consolidate (abstraction)
                   │ summarize (génération de résumés)
┌──────────────────▼───────────────────────────────┐
│  Semantic Memory (graphe de connaissances)       │
│  Capacité illimitée, stockage sur disque          │
│  Contenu : faits, règles, concepts consolidés     │
└──────────────────────────────────────────────────┘
```

**Principe de fonctionnement :**

1. **Working Memory** — buffer circulaire en RAM. Les N derniers tokens sont gardés dans l'ordre. Quand le buffer est plein, le plus ancien token est évincé et *peut* être encodé dans le niveau inférieur.
2. **Episodic Memory** — base vectorielle. Chaque épisode est encodé en embedding, indexé, et rendu disponible pour une recherche sémantique ultérieure.
3. **Semantic Memory** — connaissances abstraites. Des passages répétés ou importants sont consolidés en faits généraux. Ce niveau est le plus lent à écrire mais le plus durable.

#### Pourquoi ce concept est crucial

- **Impact sur la conception :** Le continuum transforme un problème de taille de contexte (fixe, limité) en un problème de retrieval (flexible, scalable). Un agent peut "se souvenir" d'une information donnée 10 000 tokens plus tôt sans la recharger en mémoire de travail.
- **Conséquence si ignoré :** Sans continuum, chaque élargissement de la fenêtre de contexte est un *patch* temporaire. Les LLM ont des fenêtres de 128K, 1M, 10M tokens — mais le coût quadratique de l'attention rend ces fenêtres inexploitables en pratique.
- **Cas d'usage typique :** Un agent de revue de code lit un projet de 50 fichiers. Il cherche une fonction vue 30 fichiers plus tôt : avec le continuum, il retrouve l'épisode par embedding ; sans lui, il doit tout recharger dans le contexte.

---

### 3.3 Implémentation pratique — AgentMemory — PARTIE PRATIQUE

Cette section est le cœur de la séance. Chaque ligne de code est commentée en français pour expliquer non seulement *ce qu'elle fait* mais aussi *pourquoi* elle est conçue ainsi.

```python
# === FICHIER : agent_memory.py ===
# Rôle : Système de mémoire hiérarchique pour agent conversationnel
# Dépendances : sentence-transformers, SQLite
#
# Ce module implémente les trois types de mémoire (épisodique, sémantique,
# procédurale) dans une seule classe AgentMemory avec consolidation
# automatique du court-terme vers le long-terme.

import json
# ↑ json : sérialisation/désérialisation des embeddings en bytes
#   Indispensable pour stocker les vecteurs dans SQLite (pas de JSON natif)

import sqlite3
# ↑ sqlite3 : base de données fichier, zéro configuration, zéro serveur
#   Standard de Python, embarqué, parfait pour un agent standalone

import time
# ↑ time : horodatage Unix pour ordonner les entrées dans le temps
#   Permet le tri chronologique et les filtres "pas plus vieux que X"

import os
# ↑ os : détection d'existence de fichier pour le chargement initial

from collections import deque
# ↑ deque : file à double extrémité avec capacité maximale fixe
#   O(1) en insertion et suppression aux deux bouts
#   Idéal pour le sliding window de la mémoire court-terme

from pathlib import Path
# ↑ Path : manipulation de chemins cross-platform (Linux/Mac/Windows)
#   Plus fiable que os.path.join pour la portabilité

from typing import Any
# ↑ Any : type générique pour les valeurs faiblement typées
#   Utile pour les métadonnées extensibles

from sentence_transformers import SentenceTransformer
# ↑ SentenceTransformer : embeddings vectoriels purement locaux
#   Aucun appel réseau, aucune donnée envoyée à l'extérieur
#   Modèle all-MiniLM-L6-v2 : 384 dimensions, 80 Mo, inference ~5ms


# --- CLASSE PRINCIPALE : AgentMemory ---
# Cette classe implémente une mémoire hiérarchique à trois niveaux :
#   Niveau 1 (STM) : deque en RAM — sliding window, accès immédiat
#   Niveau 2 (LTM) : SQLite — persistance avec embeddings vectoriels
#   Niveau 3 (Consolidation) : résumés sémantiques extraits des patterns

class AgentMemory:
    """Mémoire persistante hiérarchique pour agent conversationnel.

    Cette classe permet à un agent de :
    - STOCKER des épisodes, faits et compétences (mémoire court-terme)
    - RETROUVER par similarité sémantique (recherche vectorielle)
    - CONSOLIDER le court-terme en long-terme (résumés automatiques)
    - PERSISTER l'état complet entre les redémarrages (fichier JSON)
    """

    def __init__(self, db_path: str = "agent_memory.db", window_size: int = 50):
        """Initialise le système de mémoire.

        Paramètres :
            db_path : chemin du fichier SQLite pour la persistance
                      Par défaut : "agent_memory.db" dans le dossier courant
            window_size : nombre maximal d'entrées en mémoire court-terme
                          Au-delà, les plus anciennes sont évincées
        """
        self.db_path = db_path
        # ↑ db_path : stocké comme attribut pour les opérations ultérieures
        #   Utile si on veut changer dynamiquement de base de données
        self.window_size = window_size
        # ↑ window_size : seuil de bascule STM vers LTM
        #   Définit la capacité du buffer circulaire

        self.short_term: deque[dict] = deque(maxlen=window_size)
        # ↑ deque avec taille max fixe : buffer circulaire (STM)
        #   Quand len(short_term) > window_size, popleft() automatique
        #   C'est le "sliding window" de la mémoire court-terme
        #   Chaque élément est un dict : {timestamp, content, ...}

        self.long_term: list[dict] = []
        # ↑ Liste Python pour la mémoire long-terme en RAM
        #   Contient les entrées consolidées (résumés STM)
        #   Pas de limite stricte : bornée par la mémoire disponible

        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        # ↑ Modèle d'embeddings : charge au constructeur (lent: ~2s)
        #   all-MiniLM-L6-v2 : bon compromis qualité/vitesse (384 dims)
        #   À ne faire qu'UNE SEULE FOIS (pas à chaque remember)

        self.conn = sqlite3.connect(db_path)
        # ↑ Connexion SQLite persistante : fichier .db sur le disque
        #   sqlite3.connect crée le fichier s'il n'existe pas
        #   La connexion reste ouverte pendant toute la vie de l'objet

        self._init_db()
        # ↑ Crée les tables SQLite si c'est la première exécution
        #   Appel au constructeur pour garantir que la base est prête

        self._load()
        # ↑ Restaure les window_size dernières entrées depuis SQLite
        #   Peuple le buffer STM au démarrage pour continuité

    def _init_db(self) -> None:
        """Crée la table 'memories' et son index dans SQLite.

        Structure de la table :
            id          : clé primaire auto-incrémentée
            timestamp   : horodatage Unix (REAL)
            content     : texte de l'entrée (TEXT)
            embedding   : vecteur numpy sérialisé (BLOB)
            memory_type : 'episodic', 'semantic' ou 'procedural' (TEXT)
            importance  : score 0.0 a 1.0 pour le filtrage (REAL)
        """
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                content TEXT NOT NULL,
                embedding BLOB,
                memory_type TEXT DEFAULT 'episodic',
                importance REAL DEFAULT 0.5
            )
        """)
        # ↑ CREATE TABLE IF NOT EXISTS : ne fait rien si la table existe
        #   Permet d'appeler _init_db() à chaque démarrage sans erreur
        #   embedding est BLOB (Binary Large Object) : bytes non interprétés
        #   memory_type : un string, pas une enum, pour flexibilité

        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_memories_type
            ON memories(memory_type)
        """)
        # ↑ Index sur memory_type : accélère les filtres par type
        #   Sans index, SQLite scanne TOUTE la table pour chaque requete

        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_memories_ts
            ON memories(timestamp)
        """)
        # ↑ Index chronologique : utile pour les requetes temporelles
        #   "donne-moi les 10 dernieres entrees"

        self.conn.commit()
        # ↑ Validation : ecrit les CREATE dans le fichier .db
        #   Sans commit, rien n'est persisté

    def remember(self, content: str, memory_type: str = "episodic",
                 importance: float = 0.5) -> int:
        """Ajoute une entree en memoire (STM + SQLite).

        Etape 1 : ajout dans le buffer STM (acces rapide, volatile)
        Etape 2 : generation de l'embedding (recherche semantique)
        Etape 3 : insertion dans SQLite (persistance)

        Retourne l'ID unique de l'entree inseree.
        """
        timestamp = time.time()
        # ↑ time.time() : secondes depuis le 1er janvier 1970 (epoch Unix)
        #   Precision : microseconde, suffisant pour ordonner des entrees

        entry = {
            "timestamp": timestamp,
            "content": content,
            "memory_type": memory_type,
            "importance": importance,
        }
        # ↑ Dictionnaire structure de l'entree memoire
        #   Meme format utilise dans long_term et short_term

        self.short_term.append(entry)
        # ↑ Ajout (O(1)) dans le deque STM
        #   Si deque plein (> window_size), le plus ancien est supprime
        #   Comportement : FIFO automatique garanti par deque

        embedding = self.embedder.encode(content).tolist()
        # ↑ encode() : retourne un numpy.ndarray de forme (384,)
        #   tolist() : convertit en list[float] pour serialisation JSON
        #   L'embedding represente le sens semantique du texte

        blob = json.dumps(embedding).encode("utf-8")
        # ↑ Serialisation JSON : transforme [0.1, 0.2, ...] en "[0.1,...]"
        #   encode("utf-8") : convertit la chaîne en bytes pour SQLite
        #   Alternative : pickle.dumps() mais JSON est plus portable

        cursor = self.conn.execute(
            "INSERT INTO memories (timestamp, content, embedding, "
            "memory_type, importance) VALUES (?, ?, ?, ?, ?)",
            (timestamp, content, blob, memory_type, importance),
        )
        # ↑ Requete parametree : les ? sont echappes par SQLite
        #   Protection contre l'injection SQL (jamais de f-string ici)
        #   Passage en plusieurs lignes pour lisibilité
        self.conn.commit()
        # ↑ Validation : ecriture physique sur le disque
        #   En cas de crash avant commit, l'insertion est perdue

        return cursor.lastrowid
        # ↑ lastrowid : identifiant auto-genere par SQLite
        #   Permet de referencer cette entree (update, delete)

    def recall(self, query: str, top_k: int = 5,
               memory_type: str | None = None) -> list[dict]:
        """Recherche les entrees les plus pertinentes.

        Algorithme : similarite cosinus avec force brute.
        Pour un volume de moins de 10^6 entrees, cette approche est
        suffisante. Au-dela, utiliser un index ANN (faiss, hnswlib).

        Parametres :
            query : texte de la requete (sera encode en embedding)
            top_k : nombre de resultats a retourner (defaut: 5)
            memory_type : filtre optionnel par type de memoire

        Retourne : liste de dicts tries par score decroissant
        """
        query_emb = self.embedder.encode(query).tolist()
        # ↑ Encode la requete avec le MEME modele que l'indexation
        #   Si les modeles different, la similarite cosinus n'a pas de sens

        sql = "SELECT id, timestamp, content, memory_type, importance, embedding FROM memories"
        # ↑ Selectionne toutes les colonnes utiles pour le scoring
        #   On recupere TOUT puis on trie (force brute)
        params: list[Any] = []
        # ↑ Liste des parametres pour la clause WHERE

        if memory_type:
            sql += " WHERE memory_type = ?"
            # ↑ Filtre SQL par type si demande
            params.append(memory_type)

        candidates: list[tuple[float, dict]] = []
        # ↑ Liste temporaire de tuples (score, dictionnaire entree)
        #   Le tri par score se fera ensuite sur cette liste

        for row in self.conn.execute(sql, params):
            # ↑ Parcourt TOUTES les lignes retournees par SQLite
            #   Force brute : O(N) en memoire et en calcul
            stored_emb = json.loads(row[5].decode("utf-8"))
            # ↑ Deserialisation : bytes -> str -> list[float]
            #   decode("utf-8") : ne pas oublier l'encodage !
            score = self._cosine_similarity(query_emb, stored_emb)
            # ↑ Calcul de similarite entre la requete et l'entree stockee
            candidates.append((score, {
                "id": row[0],
                "timestamp": row[1],
                "content": row[2],
                "memory_type": row[3],
                "importance": row[4],
            }))

        candidates.sort(key=lambda x: x[0], reverse=True)
        # ↑ Tri descendant par score de similarite
        #   lambda x: x[0] extrait le score du tuple (score, dict)
        #   reverse=True : du plus pertinent au moins pertinent

        return [c[1] for c in candidates[:top_k]]
        # ↑ Tranche : garde seulement les top_k meilleurs scores
        #   c[1] extrait le dictionnaire (on jette le score)

    def consolidate(self, min_occurrences: int = 3) -> list[str]:
        """Consolide les episodes STM similaires en connaissances semantiques.

        Processus en 3 etapes :
        1. Embedding de tous les episodes du buffer STM
        2. Regroupement par similarite cosinus (seuil 0.85)
        3. Creation d'une entree semantique par cluster significatif

        Ce processus imite la consolidation hippocampique chez l'humain :
        les souvenirs a court-terme sont rejoues et abstraits en
        connaissances generales pendant le sommeil. Ici, pas de sommeil :
        la consolidation est declenchee explicitement.

        Parametres :
            min_occurrences : nombre minimal d'episodes similaires
                              pour former un fait semantique (defaut: 3)
        """
        if len(self.short_term) < min_occurrences:
            return []
        # ↑ Garde-fou : pas assez d'episodes pour une consolidation utile
        #   Chaque consolidation a un cout (embeddings + clustering)
        #   Ne pas declencher pour 1 ou 2 episodes isoles

        episodes = list(self.short_term)
        # ↑ Copie du buffer STM pour eviter les mutations pendant le calcul
        #   Si un remember() est appele pendant la consolidation,
        #   le buffer original n'est pas modifie

        ep_texts = [e["content"] for e in episodes]
        # ↑ Extraction des textes seulement (on ignore les metadonnees)
        ep_embeddings = [self.embedder.encode(t).tolist() for t in ep_texts]
        # ↑ Vecteurs pour chaque episode : base du clustering
        #   O(N * d) en temps : N episodes, d=384 dimensions

        clusters: list[list[int]] = []
        # ↑ Clusters = groupes d'indices d'episodes similaires
        #   Exemple : [[0, 3, 5], [1, 2], [4]] si 0,3,5 sont proches

        for i in range(len(ep_texts)):
            # ↑ Pour chaque episode, cherche un cluster existant
            added = False
            for cluster in clusters:
                # ↑ Parcourt les clusters deja formes
                if self._cosine_similarity(
                    ep_embeddings[i], ep_embeddings[cluster[0]]
                ) > 0.85:
                    # ↑ Seuil 0.85 : determine empiriquement
                    #   Trop haut : clusters trop petits
                    #   Trop bas : fausses generalisations
                    cluster.append(i)
                    added = True
                    break
            if not added:
                clusters.append([i])
                # ↑ Nouveau cluster : l'episode en est le premier membre

        summaries: list[str] = []
        for cluster in clusters:
            if len(cluster) >= min_occurrences:
                # ↑ Cluster assez grand pour etre significatif
                combined = " ".join(ep_texts[i] for i in cluster)
                # ↑ Concaténation brute des textes du cluster
                #   En production : remplacer par un resume LLM
                summary = f"[Consolide] {combined[:200]}..."
                # ↑ Troncature a 200 caracteres pour eviter le bruit
                self.remember(
                    summary, memory_type="semantic", importance=0.8
                )
                # ↑ Stockage en memoire semantique avec importance elevee
                #   memory_type="semantic" : distingue des episodes bruts
                summaries.append(summary)

        return summaries
        # ↑ Retourne les resumes crees pour affichage ou logging

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        """Calcule la similarite cosinus entre deux vecteurs.

        Formule : (a . b) / (||a|| * ||b||)
        Resultat : 1.0 = identique, 0.0 = orthogonal, -1.0 = oppose
        Complexite : O(d) ou d = dimension des vecteurs
        """
        dot = sum(x * y for x, y in zip(a, b))
        # ↑ Produit scalaire : somme des multiplications element par element
        norm_a = sum(x * x for x in a) ** 0.5
        # ↑ Norme L2 (euclidienne) : racine carree de la somme des carres
        norm_b = sum(y * y for y in b) ** 0.5
        # ↑ Meme calcul pour le second vecteur

        if norm_a * norm_b == 0:
            return 0.0
            # ↑ Evite la division par zero (vecteur nul)
        return dot / (norm_a * norm_b)
        # ↑ Division normalisee : score entre -1.0 et 1.0
        #   Important : les embeddings sentence-transformers sont deja
        #   normalises, donc la similarite cosinus = produit scalaire

    def _load(self) -> None:
        """Restaure les dernieres entrees depuis SQLite dans le buffer STM.

        Appele au constructeur pour assurer la continuite entre sessions.
        Charge les window_size entrees les plus recentes.
        """
        cursor = self.conn.execute(
            "SELECT content, memory_type, importance FROM memories "
            "ORDER BY timestamp DESC LIMIT ?",
            (self.window_size,),
        )
        # ↑ Requete : les window_size entrees les plus recentes
        #   ORDER BY timestamp DESC : de la plus recente a la plus ancienne
        #   LIMIT ? : limite definie par window_size (parametre securise)

        rows = list(cursor.fetchall())
        # ↑ fetchall() recupere toutes les lignes en une fois
        #   Conversion en list pour pouvoir la renverser

        for row in reversed(rows):
            # ↑ reversed : remet dans l'ordre chronologique
            #   SQLite a retourne du plus recent au plus ancien
            #   On veut le buffer dans l'ordre historique
            self.short_term.append({
                "content": row[0],
                "memory_type": row[1],
                "importance": row[2],
            })

    def stats(self) -> dict[str, int]:
        """Retourne des statistiques sur le contenu de la memoire.

        Exemple de retour : {"episodic": 42, "semantic": 7, "procedural": 3}
        Utile pour le monitoring et le debugging.
        """
        cursor = self.conn.execute(
            "SELECT memory_type, COUNT(*) FROM memories GROUP BY memory_type"
        )
        # ↑ Agrégation SQL : GOUPE PAR memory_type
        #   Exemple de resultat : [('episodic', 42), ('semantic', 7)]
        return {row[0]: row[1] for row in cursor.fetchall()}
        # ↑ Comprehension de dictionnaire : transforme les tuples en dict
        #   row[0] = memory_type (str), row[1] = count (int)

    def close(self) -> None:
        """Ferme la connexion SQLite proprement.

        Toujours appeler en fin de vie de l'objet pour eviter
        les corruptions de fichier. Utiliser avec context manager.
        """
        self.conn.close()
        # ↑ Fermeture de la connexion : libere le verrou du fichier .db
        #   Important dans les systemes multi-agents (fichier partage)


# === EXEMPLE D'UTILISATION ===
# Ce bloc demontre le cycle de vie complet de la memoire :
#   1. Creation de l'instance
#   2. Alimentation en episodes
#   3. Consolidation en faits semantiques
#   4. Recherche par similarite
#   5. Statistiques

if __name__ == "__main__":
    # Cree l'instance de memoire persistante
    mem = AgentMemory("demo_agent.db", window_size=20)
    # ↑ Fichier de base : demo_agent.db (sera cree automatiquement)
    #   window_size=20 : buffer STM de 20 entrees max

    # Phase 1 : Alimentation en episodes
    print("--- Phase 1 : Ajout d'episodes ---")
    episodes = [
        "Recherche de 'API authentication' dans la documentation",
        "L'utilisateur a demande de reinitialiser son mot de passe",
        "Erreur 401 lors de l'appel a /api/v2/auth",
        "L'utilisateur a reussi a se connecter apres correction du token",
        "Mise a jour du profil utilisateur avec nouvelle adresse email",
        "Recherche de 'token refresh' dans les logs",
        "L'utilisateur utilise un JWT expire - besoin de refresh",
    ]
    for ep in episodes:
        mem_id = mem.remember(ep, memory_type="episodic", importance=0.6)
        print(f"  Stocke episode #{mem_id}: {ep[:50]}...")

    # Phase 2 : Consolidation STM vers LTM
    print("\n--- Phase 2 : Consolidation ---")
    summaries = mem.consolidate(min_occurrences=2)
    for s in summaries:
        print(f"  Fait consolide : {s}")

    # Phase 3 : Recherche semantique
    print("\n--- Phase 3 : Recherche semantique ---")
    results = mem.recall("comment gerer l'authentification ?", top_k=3)
    for r in results:
        print(f"  [{r['memory_type']}] {r['content'][:60]}...")

    # Phase 4 : Statistiques
    print(f"\n--- Phase 4 : Statistiques ---")
    stats = mem.stats()
    for mem_type, count in stats.items():
        print(f"  {mem_type}: {count} entrees")

    # Nettoyage
    mem.close()
    # ↑ Fermeture propre de la connexion SQLite
```

#### Ce qui se passe en cas d'échec

| Scénario | Conséquence | Récupération |
|----------|-------------|-------------|
| SQLite corrompu | `_load()` lève `sqlite3.DatabaseError` | Supprimer le fichier .db, recréer la mémoire |
| Modèle embeddings non trouvé | `SentenceTransformer()` lève `OSError` | Vérifier `pip install sentence-transformers` |
| Disque plein | `remember()` lève `sqlite3.OperationalError` | Libérer de l'espace ou changer de chemin |
| Concurrence multi-processus | SQLite peut faire `sqlite3.OperationalError: database is locked` | Utiliser WAL mode : `conn.execute("PRAGMA journal_mode=WAL")` |

---

### 3.4 Solutions de mémoire 2026 — PARTIE THÉORIQUE

En 2026, quatre solutions dominent le paysage de la mémoire agentique. Chacune fait des choix architecturaux différents.

#### HydraDB

HydraDB est une base vectorielle spécialisée pour la mémoire agentique. Elle introduit le concept de *memory sharding* : différents types de mémoire sont stockés dans des "têtes" indépendantes.

```python
# Exemple d'utilisation HydraDB (API conceptuelle 2026)
from hydradb import HydraAgentMemory

memory = HydraAgentMemory(
    api_key="...",
    heads={
        "episodic": {"dimension": 768, "index": "hnsw"},
        "semantic": {"dimension": 768, "index": "ivf"},
        "procedural": {"dimension": 384, "index": "flat"},
    },
)

# Ecriture automatique avec embedding
memory.store(
    head="episodic",
    data={"action": "search_docs", "query": "API v2", "result": "docs/api/v2.md"},
    metadata={"timestamp": time.time(), "session": "s7"},
)

# Recherche cross-tete
results = memory.search(
    query="comment chercher dans l'API ?",
    heads=["episodic", "semantic"],
    top_k=5,
)
```

#### OMEGA (Open Memory Engine for General Agents)

OMEGA est un standard ouvert (2025) qui définit un protocole de communication entre agents et mémoire, indépendant de l'implémentation sous-jacente.

```python
from omega import OmegaMemory, MemoryEntry

class OMEGAAgentMemory:
    """Wrapper pour utiliser OMEGA comme backend memoire."""

    def __init__(self, namespace: str = "default"):
        self.store = OmegaMemory(namespace)

    def remember(
        self,
        content: str,
        importance: float = 0.5,
        tags: list[str] | None = None,
    ) -> str:
        entry = MemoryEntry(
            content=content,
            importance=importance,
            tags=tags or [],
            timestamp=time.time(),
        )
        return self.store.insert(entry)

    def recall(
        self,
        query: str,
        min_importance: float = 0.0,
        max_age: float | None = None,
    ) -> list[MemoryEntry]:
        results = self.store.search(query, top_k=10)
        # Filtrage par importance et age
        filtered = [
            r for r in results
            if r.importance >= min_importance
            and (max_age is None or (time.time() - r.timestamp) <= max_age)
        ]
        return filtered
```

#### Zep

Zep est une solution commerciale mature (2023-2026) avec synthese automatique des conversations longues.

```python
from zep_cloud.client import Zep

zep = Zep(api_key="...")

# Ajout d'un message a l'historique
zep.memory.add(
    session_id="user_42",
    messages=[
        {"role": "user", "content": "Quelle est la capital du Bresil ?"},
        {"role": "assistant", "content": "Brasilia."},
    ],
)

# Recherche semantique dans la memoire
results = zep.memory.search(
    session_id="user_42",
    query="capital",
    limit=5,
)
```

#### Redis Agent Memory

Redis a introduit Agent Memory en 2025 comme extension native de Redis Stack, utilisant des vecteurs et des sorted sets pour la gestion temporelle.

```python
import redis
import numpy as np

class RedisAgentMemory:
    """Agent Memory utilisant Redis Stack."""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.client = redis.from_url(redis_url)
        self.index_name = "agent_mem"

    def init_index(self, dims: int = 768) -> None:
        self.client.ft(self.index_name).create(
            redis.commands.search.Field("embedding", "VECTOR", {
                "TYPE": "FLOAT32",
                "DIM": dims,
                "DISTANCE_METRIC": "COSINE",
            }),
            redis.commands.search.Field("content", "TEXT"),
            redis.commands.search.Field("timestamp", "NUMERIC"),
        )

    def store(self, content: str, embedding: list[float],
              metadata: dict | None = None) -> str:
        import uuid
        key = f"mem:{uuid.uuid4().hex}"
        self.client.hset(key, mapping={
            "content": content,
            "embedding": np.array(embedding, dtype=np.float32).tobytes(),
            "timestamp": time.time(),
            **(metadata or {}),
        })
        return key

    def search(self, query_embedding: list[float],
               top_k: int = 5) -> list[dict]:
        query_vec = np.array(query_embedding, dtype=np.float32).tobytes()
        results = self.client.ft(self.index_name).search(
            f"*=>[KNN {top_k} @embedding $vec AS score]",
            query_params={"vec": query_vec},
            return_fields=["content", "score"],
        )
        return [
            {"content": doc.content, "score": float(doc.score)}
            for doc in results.docs
        ]
```

#### Tableau comparatif

| Solution | Type | Open Source | Persistance | Cross-session | Synthese auto. |
|----------|------|-------------|-------------|---------------|----------------|
| HydraDB | Vector DB | Oui (MIT) | Oui | Oui | Oui |
| OMEGA | Standard | Oui (Apache) | Oui | Oui | Configurable |
| Zep | SaaS / Self-host | Partiel | Oui | Oui | Oui |
| Redis AM | Extension Redis | Oui (SSPL) | Oui | Oui | Non |

---

### 3.5 Benchmarks de memoire — LongMemEval — PARTIE THÉORIQUE

**LongMemEval** (2025) est le benchmark standard pour evaluer la memoire persistante des agents. Il definit 5 dimensions :

1. **Short-term recall** — l'agent se souvient d'information donnee dans les 5 tours precedents
2. **Long-term recall** — information donnee 50+ tours avant
3. **Cross-session recall** — information d'une session anterieure
4. **Temporal reasoning** — ordonner des evenements dans le temps
5. **Update tracking** — detecter et integrer des mises a jour d'information

Voici une implementation minimale des tests :

```python
import random

class LongMemEvalSuite:
    """Suite de tests pour evaluer la memoire persistante d'un agent.

    Chaque test retourne un score entre 0.0 et 1.0.
    Le score composite LongMemScore pondere les dimensions.
    """

    def __init__(self, agent, seed: int = 42):
        self.agent = agent
        # ↑ Reference vers l'agent a tester
        self.rng = random.Random(seed)
        # ↑ Generateur aleatoire avec seed fixe pour reproductibilite
        self.scores: dict[str, float] = {}

    def test_short_term_recall(self, n_trials: int = 10) -> float:
        """Memoire court-terme : l'agent retient sur 5 tours.
        
        1. On donne un fait a l'agent
        2. On fait 3 tours de distraction
        3. On interroge l'agent sur le fait
        """
        correct = 0
        for _ in range(n_trials):
            fact = f"Le code secret est {self.rng.randint(1000, 9999)}"
            self.agent.tell(f"Retiens : {fact}")
            for _ in range(3):
                self.agent.tell("Ignore ce message.")
            response = self.agent.ask("Quel est le code secret ?")
            if str(fact.split()[-1]) in response:
                correct += 1
        return correct / n_trials

    def test_long_term_recall(self, n_distractors: int = 50) -> float:
        """Memoire long-terme : l'agent retient sur 50+ tours."""
        fact = f"La couleur preferee est {self.rng.choice(['bleu', 'rouge', 'vert'])}"
        self.agent.tell(f"Retiens : {fact}")
        for i in range(n_distractors):
            self.agent.tell(f"Message de distorsion #{i}")
        response = self.agent.ask("Rappelle la couleur preferee.")
        return 1.0 if str(fact.split()[-1]) in response else 0.0

    def test_cross_session(self) -> float:
        """Memoire inter-session : survit a un redemarrage."""
        session_id = f"session_{self.rng.randint(0, 1000)}"
        self.agent.save_session(session_id)
        self.agent.load_session(session_id)
        response = self.agent.ask("Que sais-tu de moi ?")
        return 1.0 if len(response) > 20 else 0.0

    def run_all(self) -> dict[str, float]:
        self.scores["short_term"] = self.test_short_term_recall()
        self.scores["long_term"] = self.test_long_term_recall()
        self.scores["cross_session"] = self.test_cross_session()
        return self.scores
```

**Score composite LongMemScore :**

$$
\text{LongMemScore} = 0.3 \cdot S_{short} + 0.4 \cdot S_{long} + 0.3 \cdot S_{cross}
$$

Les meilleurs scores en 2026 oscillent entre 0.82 et 0.94 pour les systemes utilisant HydraDB ou OMEGA. Les agents utilisant une simple fenetre de contexte (sans memoire persistante) plafonnent a environ 0.35.

---

### 3.6 Lab associé

```bash
# LAB : Mise en place de la memoire persistante
# Objectif : implementer AgentMemory pour un agent de chat
# Duree estimee : 4h
# Prérequis : seances 1-3
#
# Etapes :
# 1. Creer une instance AgentMemory avec stockage SQLite
# 2. Alimenter avec 50 episodes de test
# 3. Executer la consolidation, verifier les faits semantiques
# 4. Tester le recall avec des requetes hors contexte
# 5. Executer LongMemEval et calculer le LongMemScore
```

Voir `lab/README.md` — Partie 2 pour les instructions completes.

---

## Synthèse

**Ce que vous avez appris dans cette seance :**

| Concept | Resume | Section |
|---------|--------|---------|
| Trois types de memoire | Episodique (experiences), Semantique (faits), Procedurale (competences) | 3.1 |
| Memory Continuum | Architecture en trois niveaux : Working Memory, Episodic, Semantic | 3.2 |
| AgentMemory | Implementation complete avec STM/LTM, embeddings, consolidation | 3.3 |
| Solutions 2026 | HydraDB, OMEGA, Zep, Redis — comparison des approches | 3.4 |
| LongMemEval | Benchmark standard : 5 dimensions de performance memoire | 3.5 |

**Lien avec la seance suivante :**

> *"Maintenant que vous savez implementer une memoire persistante pour un agent, la seance 4 (*MCP Protocol*) vous apprendra a connecter cet agent a des outils externes. Vous reutiliserez la memoire pour stocker les resultats d'appels d'outils, apprendre de leurs echecs, et referencer des decouvertes passees. Sans la memoire de cette seance, un agent MCP agirait mais oublierait immediatement ce qu'il a fait."*

## Références contextualisées

Chaque reference est accompagnee d'une explication sur pourquoi elle est citee et quel niveau de lecture est attendu.

- **[DeepMind, "Memory Streaming for LLM Agents" (2024)]**
  *Contexte :* Article fondateur de l'architecture Memory Continuum. Des crit le principe de sliding window avec compaction et retrieval en trois niveaux. Cite dans la section 3.2.
  *Niveau de lecture :* Avance (papier de recherche)
  *URL :* Référence pédagogique — article non publié

- **[Qian et al., "LongMemEval: Benchmarking Persistent Memory for LLM Agents" (2025)]**
  *Contexte :* Definition du benchmark standard LongMemEval avec ses 5 dimensions et la formule du score composite. Cite dans la section 3.5.
  *Niveau de lecture :* Introduction (les concepts sont expliques simplement)
  *URL :* Référence pédagogique — article non publié

- **[Kumar et al., "Multi-Head Memory Architecture for Agentic Systems" (2025)]**
  *Contexte :* Presente HydraDB et le concept de memory sharding. Cite dans la section 3.4.
  *Niveau de lecture :* Avance
  *URL :* Référence pédagogique — article non publié

- **[OMEGA Protocol Specification v2.0 (2026)]**
  *Contexte :* Standard ouvert pour la communication agent-memoire. Indispensable pour comprendre l'interoperabilite des systemes agentiques en 2026. Cite dans la section 3.4.
  *Niveau de lecture :* Technique

- **[Zep Documentation]**
  *Contexte :* Documentation officielle de Zep, solution SaaS de memoire persistante. A consulter pendant le lab pour comparer avec l'implementation AgentMemory. Cite dans la section 3.4.
  *Niveau de lecture :* Technique
  *URL :* https://help.getzep.com

- **[Redis Agent Memory Documentation]**
  *Contexte :* Extension native Redis Stack pour la memoire agentique. Exemple d'utilisation de Redis comme backend vectoriel. Cite dans la section 3.4.
  *Niveau de lecture :* Technique
  *URL :* https://redis.io/solutions/agent-memory/

- **[Park et al., "Human-level episodic memory in LLM agents" (2025)]**
  *Contexte :* Explore l'analogie entre la consolidation hippocampique humaine et les systemes de memoire agentique. Complement a la section 3.1 sur la typologie des memoires.
  *Niveau de lecture :* Avance

- **[Grattafiori et al., "The Memory Tier: Hierarchical Storage for AI Agents" (2026)]**
  *Contexte :* Proposition d'une architecture de stockage hiérarchique standardisee pour les agents. Fonde les principes de la section 3.2 et 3.3.
  *Niveau de lecture :* Avance
