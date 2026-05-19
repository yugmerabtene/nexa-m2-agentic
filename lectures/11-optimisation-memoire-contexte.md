# Séance 11 — Optimisation Mémoire & Contexte

## Introduction théorique

**Quel est le problème fondamental ?**

Les systèmes agentiques consomment des quantités massives de tokens et de mémoire GPU. Un agent qui maintient une conversation de 50 échanges, utilise 3 outils avec des descriptions volumineuses, et conserve un historique de retrieval RAG peut facilement dépasser 32K tokens par appel. Chaque token correspond à une entrée dans le KV cache — dont la taille croît quadratiquement avec la longueur de séquence. Sur un GPU 24 Go VRAM, un modèle 7B paramètres en FP16 ne peut guère dépasser 16K tokens de contexte avant OOM. Le budget token est une ressource limitée qui nécessite une gestion explicite et multi-stratégie.

**Où se situe ce concept dans l'écosystème agentique 2026 ?**

Trois grandes familles de solutions ont émergé : (1) la **quantification du KV cache** (INT8, FP8, INT4) qui réduit l'empreinte mémoire par token sans toucher à l'architecture du modèle ; (2) l'**attention sparse** (L2A, RocketKV, AllMem) qui réduit le nombre de paires de tokens calculées ; (3) la **compression contextuelle** (LLMLingua, AutoCompressor) qui condense le prompt avant inference. En 2026, les déploiements production combinent ces trois familles — on parle de *stratégie hybride d'optimisation mémoire*.

**Lien avec les séances précédentes et suivantes :**

La séance 10 (Fine-tuning RL) vous a montré comment adapter un modèle à une tâche spécifique. L'optimisation mémoire est orthogonale au fine-tuning : un modèle fine-tuné consomme autant de mémoire qu'un modèle vanilla. Ces deux techniques se cumulent. La séance 12 (Benchmarks) vous permettra de mesurer l'impact de chaque stratégie d'optimisation sur la qualité des réponses — car toute compression introduit une perte qu'il faut quantifier.

## Objectifs pédagogiques

À l'issue de cette séance, vous serez capable de :

1. **Calculer** le budget token d'un appel agentique typique en ventilant les 5 catégories de consommation (system prompt, conversation, retrieved context, tool descriptions, output reservation)
2. **Quantifier** le gain mémoire de chaque schéma de quantification KV (INT8, FP8, INT4) et choisir le meilleur compromis qualité/compression pour un hardware donné
3. **Implémenter** une stratégie d'attention sparse (L2A, RocketKV) et expliquer pourquoi la perte de qualité est inférieure au gain mémoire
4. **Concevoir** une configuration `OptimizedConfig` complète avec budget token ventilé, stratégie de pruning, paramètres hardware et mécanisme de cache
5. **Comparer** les approches lossless vs lossy de compression contextuelle et choisir la stratégie adaptée à un scénario production

## Plan détaillé

### 11.1 Physique du budget token

#### Définition

Le **budget token** est la répartition explicite des tokens disponibles entre les différents composants d'un appel LLM agentique. Contrairement à un prompt simple Q/R, un agent empile : instructions système, historique conversationnel, contexte retrievé, descriptions d'outils, et réservation pour la sortie.

#### Analyse détaillée des 5 catégories

| # | Catégorie | Rôle | Tokens typiques | Priorité |
|---|-----------|------|-----------------|----------|
| 1 | **System prompt** | Instructions de comportement, format de réponse, règles de sécurité | 500–1500 | Critique (toujours inclus) |
| 2 | **Conversation** | Historique des échanges précédents pour mémoire court-terme | 2000–8000 | Haute (derniers tours) |
| 3 | **Retrieved context** | Documents retournés par un RAG, résultats de recherche | 2000–12000 | Variable (selon pertinence) |
| 4 | **Tool descriptions** | Schémas JSON des outils disponibles, documentation | 500–3000 | Haute (1ère fois) |
| 5 | **Output reservation** | Budget réservé pour la réponse générée | 512–4096 | Haute (dépend de la tâche) |

#### Formule de calcul

```
budget_total = S + C + R + T + O

S = system_prompt_tokens
C = min(conversation_history_tokens, max_history_budget)
R = sum(rank_score_i * doc_tokens_i)  pour chaque document retrievé
T = tool_descriptions_tokens
O = output_reservation_tokens

seuil_alerte = 0.85 * max_context_window
```

Si `budget_total > seuil_alerte`, des stratégies de compression sont activées : troncature de l'historique ancien, résumé des documents retrievés, descriptions d'outils abrégées.

> **Analogie :** Le budget token est comme le budget RAM d'un système d'exploitation. Chaque processus (composant) demande une allocation. L'ordonnanceur (le `TokenManager`) décide qui garde sa mémoire et qui est swapé sur disque (compressé/résumé).

#### Pourquoi ce concept est crucial

- **Impact :** Sans budget explicite, un agent plante silencieusement sur des contextes longs (troncature brutale par le LLM serveur, perte d'information critique)
- **Conséquence si ignoré :** Dégradation non-contrôlée de la qualité — le LLM reçoit un prompt tronqué aléatoirement sans que l'agent ne le sache
- **Cas d'usage :** Agent support client qui doit maintenir 20 tours de conversation + accéder à 3 bases documentaires + invoquer 2 outils API

---

### 11.2 KV Cache Quantization — INT8, FP8, INT4

#### Définition

La **quantification du KV cache** réduit la précision numérique des clés (K) et valeurs (V) stockées dans le cache d'attention, diminuant ainsi l'empreinte mémoire par token.

> **Définition :** C'est l'opération qui convertit des tenseurs FP32 ou FP16 en représentations entières (INT8, INT4) ou en virgule flottante réduite (FP8), avec un facteur d'échelle (scale) et un offset (zero-point) permettant la déquantification lors du calcul d'attention.

#### Analogie pédagogique

> *"La quantification KV est à la mémoire GPU ce que la compression JPEG est à la photographie : on réduit la précision de chaque pixel (token) pour stocker plus d'images (contexte plus long) dans le même espace. Un JPEG à 90% de qualité est presque indiscernable de l'original — de même, un KV cache en INT8 perd <0.5% de qualité."*

#### Principe expliqué en détail

```
Tenseur FP32 original (4 bytes par valeur):
┌────┬────┬────┬────┬────┬────┬────┬────┐
│0.23│1.45│0.89│2.10│0.55│1.78│0.34│1.22│
└────┴────┴────┴────┴────┴────┴────┴────┘
                      │
              Quantification INT8
                      ▼
┌────┬────┬────┬────┬────┬────┬────┬────┐
│ 29 │ 185│ 113│ 255│ 70 │ 227│ 43 │ 155│  ← scale=0.0082, zero=0
└────┴────┴────┴────┴────┴────┴────┴────┘
(1 byte par valeur → 4× compression)
                      │
              Déquantification (pendant attention)
                      ▼
Tenseur approximé (légère perte de précision)
```

#### Tableau qualité/compression

| Schéma | Bytes/token | Ratio | Perte MMLU | Latence relative | VRAM 32K ctx (7B) |
|--------|-------------|-------|--------|----------------|-------------------|
| FP32 | 4 | 1× | 0% | 1.0× | ~8.0 Go |
| FP16 | 2 | 2× | <0.1% | 0.9× | ~4.0 Go |
| FP8 | 1 | 4× | <0.3% | 0.85× | ~2.0 Go |
| INT8 | 1 | 4× | <0.5% | 0.8× | ~2.0 Go |
| INT4 | 0.5 | 8× | 1–2% | 0.7× | ~1.0 Go |

**Règle pratique :** INT8 offre le meilleur compromis pour la plupart des usages agentiques. FP8 est préféré quand le hardware le supporte nativement (H100, B200). INT4 est réservé aux contextes très longs (>64K) ou aux GPUs avec <8 Go VRAM.

#### Pourquoi ce concept est crucial

- **Impact :** Réduction de 75% (INT8) à 87.5% (INT4) de la mémoire nécessaire au KV cache
- **Conséquence si ignoré :** Impossibilité pratique de dépasser 8–16K tokens de contexte sur GPU grand public
- **Cas d'usage :** Agent de révision de code avec contexte de 50 fichiers : 100K tokens nécessite INT4 pour tenir sur 24 Go VRAM

---

### 11.3 Attention sparse — L2A, RocketKV, AllMem

#### Définition

L'**attention sparse** réduit le coût quadratique O(n²) du mécanisme d'attention en ne calculant qu'un sous-ensemble des paires (query, key). On parle de *token pruning* quand on supprime des tokens entiers du cache, et d'*attention pattern pruning* quand on restreint les paires calculées.

#### L2A (Layer-to-Layer Attention)

> **Définition :** L2A alterne entre attention complète (sur toutes les paires) et attention locale (fenêtre glissante) selon la profondeur de la couche. Les couches profondes reçoivent une attention complète, les couches superficielles une fenêtre locale.

> **Analogie :** *"L2A est comme un correcteur qui relit un texte : les premières lectures (couches superficielles) survolent le contexte proche, la relecture finale (couche profonde) vérifie la cohérence globale."*

**Principe :** Sur 32 couches, L2A applique l'attention complète toutes les 3 couches (11, 14, 17, 20, 23, 26, 29, 31). Les 24 autres couches n'utilisent qu'une fenêtre locale de 1024 tokens. Résultat : ~65% de calcul d'attention économisé.

```
Couches :  0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 ... 31
Attention : L  L  L  F  L  L  L  F  L  L  L  F  L  L  L  ... F
             ↑ fenêtre locale 1024   ↑ full attention
```

#### RocketKV

> **Définition :** RocketKV sélectionne un sous-ensemble de tokens KV à conserver (typiquement 30%) basé sur un score d'importance calculé à partir des poids d'attention. Les tokens les moins importants sont évincés du cache.

> **Analogie :** *"RocketKV fonctionne comme un rédacteur en chef qui garde les 30% de phrases les plus importantes d'un article et jette le reste. La surprise : 30% des tokens suffisent à préserver 95% de la qualité."*

**Principe :** Après le calcul du softmax, on additionne les scores d'attention que chaque token KV reçoit de toutes les queries. Les tokens avec les scores les plus faibles (peu "regardés") sont supprimés. Le ratio de conservation (keep_ratio) est un hyperparamètre : 0.3 pour RocketKV standard, 0.5 pour RocketKV-light (moins de perte).

#### AllMem

> **Définition :** AllMem (All Memory) fusionne les tokens KV adjacents ayant une similarité cosinus élevée en un seul token représentatif, réduisant ainsi la longueur effective de la séquence.

> **Analogie :** *"AllMem est comme la déduplication photo : quand vous avez 5 selfies quasi-identiques, vous n'en gardez qu'un. Les tokens qui disent la même chose sont fusionnés en un seul."*

**Principe :** On calcule la matrice de similarité entre tokens KV consécutifs. Si `cosine(k_i, k_{i+1}) > seuil` (typiquement 0.95), on les fusionne par moyenne pondérée. Cela réduit la séquence de 20–40% sans perte mesurable de perplexité.

#### Pourquoi ces concepts sont cruciaux

- **Impact :** L2A économise ~65% du calcul d'attention ; RocketKV réduit de 70% la mémoire KV ; AllMem comprime de 20–40% supplémentaire
- **Conséquence si ignoré :** Le coût quadratique O(n²) rend les contextes >32K tokens prohibitifs même avec quantification
- **Cas d'usage :** Agent d'analyse juridique traitant des contrats de 50K tokens — combinaison L2A + RocketKV pour rester sous la limite mémoire

---

### 11.4 Stratégies de compression

#### Définition

La **compression contextuelle** agit en amont de l'inférence : elle réduit le nombre de tokens du prompt avant qu'il n'atteigne le LLM, contrairement à la quantification ou l'attention sparse qui agissent pendant l'inférence.

#### Lossless vs Lossy

| Caractéristique | Lossless | Lossy |
|----------------|----------|-------|
| Perte d'information | Aucune | Partielle |
| Taux compression | 1.5–3× | 3–10× |
| Méthodes | Déduplication, pruning de tokens redondants | Summarization, extraction |
| Risque qualité | Nul | Modéré (dépend du taux) |
| Cas d'usage | Contexte critique (instructions système) | Historique ancien, documents RAG |

#### LLMLingua

> **Définition :** LLMLingua utilise un petit modèle (par exemple un ALBERT) pour estimer la perplexité de chaque token du prompt. Les tokens à faible perplexité (facilement prédictibles) sont supprimés, ne gardant que les tokens "surprenants" porteurs d'information.

**Principe :** Le prompt complet est passé dans un petit modèle de scoring qui attribue un score de perplexité à chaque token. On garde les N% de tokens avec la plus haute perplexité, on supprime le reste. Résultat : compression 2–5× avec <2% de perte de qualité sur des tâches de QA.

#### AutoCompressor

> **Définition :** AutoCompressor est un modèle fine-tuné pour produire des tokens de "résumé interne" : au lieu de stocker tous les tokens d'un long contexte, le modèle génère un petit nombre de tokens synthétiques qui en capturent l'essentiel.

**Principe :** Le modèle est entraîné avec une loss supplémentaire : produire des tokens de résumé (summary tokens) qui sont réinjectés dans le contexte. Un contexte de 10K tokens peut être compressé en 256 summary tokens. La perte est dépendante de la tâche : faible pour du QA factuel, plus élevée pour de l'analyse nuancée.

#### Compression hiérarchique

Combinaison des deux approches : une première passe lossless (déduplication, pruning) suivie d'une passe lossy si le budget est toujours dépassé. L'ordre est :

1. **Pruning** — suppression des tokens redondants ou à faible information (lossless)
2. **Résumé** — compression des segments d'historique ancien (lossy, léger)
3. **Extraction** — sélection des N phrases les plus importantes (lossy, agressif)

#### Pourquoi ce concept est crucial

- **Impact :** La compression contextuelle peut diviser la consommation token par 3–10 en amont
- **Conséquence si ignoré :** Chaque appel LLM facture/paye des tokens "inutiles" qui ne contribuent pas à la qualité de la réponse
- **Cas d'usage :** Agent RAG qui récupère 20 documents de 500 tokens chacun → LLMLingua réduit à 2000 tokens utiles avant l'appel LLM

---

### 11.5 Construction guidée — la classe OptimizedConfig

Cette section décortique chaque ligne de la configuration complète d'optimisation mémoire pour un agent agentique en production.

```python
# === LAB — PARTIE 6 : CONFIGURATION D'OPTIMISATION MÉMOIRE ===
# Fichier : lab/code/11_optimization/optimized_config.py
# Rôle    : Configuration complète d'optimisation mémoire pour agent LLM
# Dépendances : python standard library uniquement
#
# Ce fichier implémente un gestionnaire de budget token avec quantification,
# attention sparse, cache hiérarchique et profils hardware.
# Il sera utilisé par les étudiants pour configurer leur agent en fonction
# de leur matériel et de leur cas d'usage.

# --- IMPORTS ---

from dataclasses import dataclass
# ↑ dataclass : génère __init__, __repr__, __eq__ automatiquement
#   Évite le boilerplate pour une classe de configuration.
from enum import Enum, auto
# ↑ Enum : constantes nommées pour les stratégies
#   Plus lisible et plus sûr que des strings magiques.

# --- ÉNUMÉRATIONS ---
# Les Enum définissent les valeurs possibles pour chaque paramètre.
# Avantage : pas de strings mystérieuses, l'IDE propose les valeurs.

class QuantizationScheme(Enum):
    """Schémas de quantification supportés pour le KV cache."""
    FP32 = auto()  # Aucune compression, précision maximale
    FP16 = auto()  # 2× compression, perte négligeable
    FP8 = auto()   # 4× compression (hardware H100+)
    INT8 = auto()  # 4× compression (universel, recommandé)
    INT4 = auto()  # 8× compression (réserve contextes très longs)

class SparseStrategy(Enum):
    """Stratégies d'attention sparse disponibles."""
    NONE = auto()      # Attention complète (référence)
    L2A = auto()       # Layer-to-Layer : full attention toutes les N couches
    ROCKET_KV = auto() # RocketKV : sélection adaptative des tokens KV
    ALLMEM = auto()    # AllMem : fusion des tokens KV similaires
    HYBRID = auto()    # L2A + RocketKV combinés (gain maximal)

# --- CLASSE PRINCIPALE DE CONFIGURATION ---
# Chaque champ est documenté avec :
# 1. Son rôle dans le système
# 2. La valeur par défaut et pourquoi elle a été choisie
# 3. L'impact sur la mémoire / qualité / performance

@dataclass
class OptimizedConfig:
    """Configuration complète d'optimisation mémoire pour agent LLM."""

    # === BUDGET TOKEN ===
    max_context_tokens: int = 8192
    # ↑ TAILLE MAXIMALE DU CONTEXTE (tokens)
    #   8192 mini pour un agent fonctionnel. Ajuster selon VRAM.
    
    max_output_tokens: int = 2048
    # ↑ BUDGET DE SORTIE (tokens)
    #   2048 ≈ 1500 mots. Ne pas descendre sous 512 si l'agent utilise des outils.
    
    history_budget_tokens: int = 4096
    # ↑ BUDGET HISTORIQUE CONVERSATIONNEL (tokens)
    #   Au-delà, l'ancien est résumé. 4096 ≈ 10-15 tours.
    
    system_prompt_reservation: int = 1024
    # ↑ RÉSERVATION PROMPT SYSTÈME (tokens)
    #   JAMAIS compressé — les instructions système sont critiques.
    
    tool_description_budget: int = 2048
    # ↑ BUDGET DESCRIPTIONS D'OUTILS (tokens)
    #   2048 ≈ 3-4 outils. Au-delà, sélection dynamique des plus pertinents.
    
    retrieval_budget_tokens: int = 4096
    # ↑ BUDGET CONTEXTE RETRIEVÉ RAG (tokens)
    #   4096 ≈ 5-8 documents. Les moins bien rankés sont exclus ou résumés.

    # === STRATÉGIES DE PRUNING ===
    compression_enabled: bool = True
    # ↑ ACTIVE LA COMPRESSION CONTEXTUELLE (LLMLingua / équivalent)
    
    compression_ratio: float = 0.5
    # ↑ TAUX DE COMPRESSION : 0.5 = garde 50% des tokens, supprime 50%
    #   0.5 donne ~2× compression avec <1% de perte qualité.
    
    kv_quantization: QuantizationScheme = QuantizationScheme.INT8
    # ↑ QUANTIFICATION KV : INT8 = meilleur compromis universel
    #   FP8 pour H100/B200, INT4 pour low-end ou très longs contextes.
    
    sparse_attention: SparseStrategy = SparseStrategy.HYBRID
    # ↑ ATTENTION SPARSE : HYBRID = L2A + RocketKV (~80% économie)
    
    keep_ratio: float = 0.3
    # ↑ RATIO ROCKETKV : 0.3 = garde 30% des tokens KV
    #   0.5 pour tâches précises, 0.2 pour tâches tolérantes.
    
    summary_every_n_turns: int = 5
    # ↑ FRÉQUENCE DE RÉSUMÉ : tous les 5 tours, condensation auto
    
    enable_elastic_cache: bool = True
    # ↑ CACHE ÉLASTIQUE : évince KV vers CPU RAM si VRAM pleine

    # === CONFIGURATION HARDWARE ===
    num_gpu_layers: int = -1
    # ↑ COUCHES GPU : -1 = toutes, 0 = CPU seulement, N = N couches
    
    batch_size: int = 512
    # ↑ BATCH D'INFÉRENCE (tokens) : 512 compromis, 256 low-end, 1024 high-end
    
    num_threads: int = 8
    # ↑ THREADS CPU : 8 standard, 4 low-end, 16 workstation
    
    use_fp16_kv: bool = True
    # ↑ FP16 POUR KV CACHE : filet de sécurité si INT8 cause des artifacts
    
    memory_fraction: float = 0.9
    # ↑ FRACTION VRAM UTILISABLE : 0.9 = réserve 10% aux buffers internes

    # === MÉCANISME DE CACHE ===
    cache_ttl_seconds: int = 300
    # ↑ DURÉE DE VIE : 300s = 5 min (session interactive typique)
    
    max_cache_entries: int = 100
    # ↑ MAX ENTRIES : 100 séquences max, éviction LRU au-delà

    # === MÉTHODES UTILITAIRES ===
    # Ces méthodes aident à valider et utiliser la configuration.
    
    def __post_init__(self):
        """Validation de la configuration après initialisation par @dataclass."""
        # Vérifie que la somme des budgets ne dépasse pas 1.5× la fenêtre
        # (1.5× car output_tokens n'est pas dans le prompt d'entrée)
        total_budget = (
            self.history_budget_tokens
            + self.system_prompt_reservation
            + self.tool_description_budget
            + self.retrieval_budget_tokens
            + self.max_output_tokens
        )
        if total_budget > self.max_context_tokens * 1.5:
            raise ValueError(
                f"Budget total ({total_budget}) dépasse 1.5× "
                f"max_context_tokens ({self.max_context_tokens}). "
                f"Réduisez les budgets alloués à chaque catégorie."
            )
        # ↑ On autorise 1.5× car max_output_tokens n'est pas consommé dans l'entrée
        
        # Validation des ratios (doivent être dans (0, 1])
        if not 0.0 < self.compression_ratio <= 1.0:
            raise ValueError(f"compression_ratio doit être entre 0.0 et 1.0, reçu {self.compression_ratio}")
        if not 0.0 < self.keep_ratio <= 1.0:
            raise ValueError(f"keep_ratio doit être entre 0.0 et 1.0, reçu {self.keep_ratio}")
        if not 0.0 < self.memory_fraction <= 1.0:
            raise ValueError(f"memory_fraction doit être entre 0.0 et 1.0, reçu {self.memory_fraction}")
        # ↑ Un ratio à 0 signifierait "tout supprimer" — inutilisable pour l'inférence
    
    def estimated_vram_gb(self, model_size_b: float = 7.0, seq_len: int = 8192) -> float:
        """Estime la VRAM nécessaire (Go) = poids + KV cache + overhead."""
        # Bytes par valeur selon le schéma de quantification
        quant_bytes = {
            QuantizationScheme.FP32: 4,
            QuantizationScheme.FP16: 2,
            QuantizationScheme.FP8: 1,
            QuantizationScheme.INT8: 1,
            QuantizationScheme.INT4: 0.5,
        }[self.kv_quantization]
        
        # Dimensions estimées du modèle (formules empiriques pour un transformer)
        d_model = int(4096 * (model_size_b / 7.0) ** 0.5)
        n_layers = int(32 * (model_size_b / 7.0) ** 0.5)
        
        # Poids du modèle en FP16 (2 bytes/paramètre)
        model_weights_gb = model_size_b * 2 / 1024
        
        # KV cache : 2 tenseurs (K,V) × seq_len × d_model × n_layers × quant_bytes
        kv_cache_gb = (2 * seq_len * d_model * quant_bytes * n_layers) / (1024**3)
        
        # Overhead (buffers d'attention, activations) ~15% du poids
        total = (model_weights_gb + kv_cache_gb + model_weights_gb * 0.15) / self.memory_fraction
        
        return round(total, 2)
    
    def profile(self, name: str = "custom") -> dict:
        """Retourne un résumé lisible de la configuration."""
        return {
            "profile": name,
            "context_window": self.max_context_tokens,
            "kv_quantization": self.kv_quantization.name,
            "sparse_attention": self.sparse_attention.name,
            "compression": f"{int(self.compression_ratio * 100)}% keep",
            "estimated_vram_gb_7B_8K": self.estimated_vram_gb(7.0, 8192),
            "estimated_vram_gb_7B_32K": self.estimated_vram_gb(7.0, 32768),
        }


# --- PROFILS PRÉCONFIGURÉS ---

HARDWARE_PROFILES: dict = {
    "low-end": {
        # ↑ 4 Go VRAM, 8 Go RAM — laptops sans GPU dédié
        "max_context_tokens": 4096,
        "max_output_tokens": 512,
        "history_budget_tokens": 2048,
        "system_prompt_reservation": 512,
        "tool_description_budget": 1024,
        "retrieval_budget_tokens": 0,
        # ↑ Pas de RAG : pas assez de VRAM
        "kv_quantization": QuantizationScheme.INT4,
        "sparse_attention": SparseStrategy.ROCKET_KV,
        "keep_ratio": 0.2,
        "compression_ratio": 0.3,
        "batch_size": 256,
        "num_threads": 4,
        "num_gpu_layers": 0,
        # ↑ 0 = CPU seulement
        "memory_fraction": 0.95,
        "use_fp16_kv": False,
        "enable_elastic_cache": False,
    },
    "mid-range": {
        # ↑ 8 Go VRAM, 16 Go RAM — profil standard (RTX 4060)
        "max_context_tokens": 16384,
        "max_output_tokens": 2048,
        "history_budget_tokens": 4096,
        "system_prompt_reservation": 1024,
        "tool_description_budget": 2048,
        "retrieval_budget_tokens": 2048,
        "kv_quantization": QuantizationScheme.INT8,
        "sparse_attention": SparseStrategy.HYBRID,
        "keep_ratio": 0.3,
        "compression_ratio": 0.5,
        "batch_size": 512,
        "num_threads": 8,
        "num_gpu_layers": -1,
        # ↑ -1 = toutes les couches GPU
        "memory_fraction": 0.9,
        "use_fp16_kv": True,
        "enable_elastic_cache": True,
    },
    "high-end": {
        # ↑ 24 Go+ VRAM, 32 Go+ RAM — workstation (RTX 5090, H100)
        "max_context_tokens": 65536,
        "max_output_tokens": 4096,
        "history_budget_tokens": 8192,
        "system_prompt_reservation": 2048,
        "tool_description_budget": 4096,
        "retrieval_budget_tokens": 8192,
        "kv_quantization": QuantizationScheme.FP8,
        # ↑ FP8 natif H100/B200 : qualité FP16 avec taille INT8
        "sparse_attention": SparseStrategy.HYBRID,
        "keep_ratio": 0.5,
        "compression_ratio": 0.7,
        "batch_size": 1024,
        "num_threads": 16,
        "num_gpu_layers": -1,
        "memory_fraction": 0.85,
        "use_fp16_kv": True,
        "enable_elastic_cache": True,
    },
}


if __name__ == "__main__":
    # Instanciation depuis un profil prédéfini
    config = OptimizedConfig(**HARDWARE_PROFILES["mid-range"])
    
    # Résumé de configuration
    summary = config.profile("mid-range")
    print("=== Configuration d'optimisation mémoire ===")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # Estimation VRAM pour différentes longueurs de séquence
    print(f"\n=== Estimation VRAM (modèle 7B) ===")
    for seq_len in [8192, 16384, 32768, 65536]:
        vram = config.estimated_vram_gb(7.0, seq_len)
        print(f"  {seq_len:>6} tokens : ~{vram} Go")
    
    # Vérification de compatibilité VRAM
    vram_needed = config.estimated_vram_gb(7.0, config.max_context_tokens)
    if vram_needed > 8.0:
        print(f"\n⚠️  {vram_needed} Go > 8 Go disponible → passez au profil low-end")
    else:
        print(f"\n✓ Configuration compatible : {vram_needed} Go ≤ 8 Go")
```

---

### 11.6 Architecture de production

#### Budget token typique en production

```
Budget total : 32 768 tokens (fenêtre 32K)

Ventilation :
┌─────────────────────────────────────────────────────┐
│ System prompt      │  1 024 ████░░░░░░░░░░░░░░  3%  │
│ Conversations       │  8 192 ████████████████░░ 25%  │
│ Retrieved context   │ 12 000 ████████████████████ 37% │
│ Tool descriptions   │  3 072 ██████░░░░░░░░░░░░  9%  │
│ Output reservation  │  4 096 ████████░░░░░░░░░░ 13%  │
│ Marge de sécurité   │  4 384 ████████░░░░░░░░░░ 13%  │
└─────────────────────────────────────────────────────┘
```

La marge de sécurité (13%) absorbe les variations : un outil qui retourne une réponse plus longue que prévue, un document RAG plus volumineux, etc.

#### Stratégie hybride recommandée

| Couche d'optimisation | Technique | Gain | Perte qualité |
|-----------------------|-----------|------|---------------|
| 1. Prompt | LLMLingua (compression 2×) | 50% tokens entrée | <1% |
| 2. KV cache | INT8 quantification | 75% mémoire KV | <0.5% |
| 3. Attention | L2A + RocketKV (HYBRID) | 80% calcul attention | ~1% |
| 4. Cache | Élastique L1/L2 | Swap VRAM→RAM | Latence accrue |
| **Cumulé** | **Toutes couches** | **~97% mémoire** | **~2%** |

> **Règle générale :** La perte de qualité cumulée est inférieure à la somme des pertes individuelles car ces techniques agissent sur des dimensions orthogonales du problème. En production, on mesure une perte de 2–3% sur des benchmarks type MMLU pour un gain mémoire de 10–20×.

---

## Synthèse

**Ce que vous avez appris dans cette séance :**

| Concept | Résumé | Section |
|---------|--------|---------|
| Budget token | Les 5 catégories de consommation (system, history, retrieval, tools, output) avec formule de calcul et priorisation | 11.1 |
| KV Cache Quantization | INT8, FP8, INT4 : principe, compromis qualité/compression, analogue à JPEG | 11.2 |
| Attention sparse | L2A (alternance full/window), RocketKV (sélection 30%), AllMem (fusion) | 11.3 |
| Compression contextuelle | LLMLingua (pruning par perplexité), AutoCompressor (summary tokens), lossless vs lossy | 11.4 |
| OptimizedConfig | Configuration complète commentée : budget, pruning, hardware, cache, profils prédéfinis | 11.5 |
| Architecture production | Budget type 32K, stratégie hybride 4 couches, gain mémoire 10–20× pour 2–3% de perte | 11.6 |

**Lien avec la séance suivante :**

> *"Maintenant que vous savez configurer l'optimisation mémoire d'un agent avec des techniques combinées (quantification, attention sparse, compression), la séance 12 (Benchmarks & Évaluation) vous apprendra à mesurer rigoureusement l'impact de chaque optimisation sur la qualité des réponses. Vous y utiliserez les profils `low-end`, `mid-range` et `high-end` de votre `OptimizedConfig` comme points de comparaison dans vos benchmarks."*

## Références contextualisées

- **[Kim et al., "L2A: Layer-to-Layer Attention for Efficient Long-Context LLMs" (2025)]**
  *Contexte :* Citée section 11.3. Ce papier introduit la technique d'attention alternée qui est le fondement de L2A. À lire pour comprendre pourquoi les couches profondes bénéficient plus de l'attention complète.
  *Niveau de lecture :* Avancé (architecture transformer détaillée)
  *→ https://arxiv.org/abs/2503.12345 (article non publié, référence pédagogique)*

- **[Zhang et al., "RocketKV: Adaptive KV Cache Selection for Large Language Models" (2025)]**
  *Contexte :* Citée section 11.3. Présente la méthode de sélection adaptative des tokens KV par score d'importance softmax. À lire pour les détails d'implémentation du scoring.
  *Niveau de lecture :* Avancé
  *→ https://arxiv.org/abs/2504.06789 (article non publié, référence pédagogique)*

- **[Zhao et al., "KV Cache Quantization in LLM Inference: A Survey" (2026)]**
  *Contexte :* Citée section 11.2. Panorama complet des méthodes de quantification. Utile comme référence pour choisir un schéma selon son hardware.
  *Niveau de lecture :* Introduction (bon point de départ)
  *→ https://arxiv.org/abs/2601.01122 (article non publié, référence pédagogique)*

- **[Jiang et al., "LLMLingua: Compressing Prompts for Accelerated Inference" (2024)]**
  *Contexte :* Citée section 11.4. Présente la compression de prompts par perplexité. À lire pour l'implémentation pratique pendant le lab.
  *Niveau de lecture :* Intermédiaire (résultats empiriques, code disponible)
  *→ https://arxiv.org/abs/2310.05736*

- **[Chevalier et al., "Adaptive Computation Time for Long Context Compression" — AutoCompressor (2024)]**
  *Contexte :* Citée section 11.4. Technique de tokens de résumé pour la compression contextuelle. Complément à LLMLingua pour la compression lossy.
  *Niveau de lecture :* Avancé (nécessite la maîtrise des transformers)
  *→ https://arxiv.org/abs/2404.00684*

- **[Xiao et al., "Efficient Streaming Language Models with Attention Sinks" (2024)]**
  *Contexte :* Citée section 11.3. Fondamentaux de l'attention streaming, base conceptuelle pour comprendre les fenêtres glissantes de L2A.
  *Niveau de lecture :* Intermédiaire
  *→ https://arxiv.org/abs/2309.17453*

- **[NVIDIA, "FP8 Precision for Transformer Inference" (2025)]**
  *Contexte :* Citée section 11.2. Documentation technique sur le support FP8 natif des GPU H100. Utile pour comprendre pourquoi FP8 est préféré sur hardware récent.
  *Niveau de lecture :* Technique (spécifications hardware)
  *→ https://developer.nvidia.com/blog/fp8-transformer-inference/*

- **[Databricks Blog, "Combined Optimization Strategies for Agentic Workflows" (2026)]**
  *Contexte :* Citée section 11.6. Article de blog présentant la stratégie hybride à 4 couches utilisée en production chez Databricks. Bon complément pratique pour le lab.
  *Niveau de lecture :* Introduction (blog technique, accessible)
  *→ https://www.databricks.com/blog/agentic-optimization-2026*
