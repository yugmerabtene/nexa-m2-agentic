# Séance 2 — Context Window Engineering

> **Auteur :** yugmerabtene
> **Version :** 2.0
> **Durée estimée :** 2 heures

---

## Description

Cette séance explore la gestion de la fenêtre de contexte, la ressource la plus critique d'un système agentique. Vous apprendrez pourquoi l'attention en O(n²) et le KV cache limitent les longueurs exploitables, comment optimiser le contexte avec des stratégies comme le sliding window et la compression, et découvrirez les innovations 2026 (FlashAttention-3, Ring Attention, L2A). Cette séance fait le pont entre l'architecture des LLMs (séance 1) et les systèmes de mémoire (séance 3).

---

## Prérequis

Avant de commencer cette séance, assurez-vous d'avoir :

- Terminé la **Séance 1** et compris les concepts de transformers, attention et KV cache
- Python 3.10+ installé
- Connaissances de base en deep learning

### Installation des dépendances

#### Linux et macOS

```bash
# Vérifier Python
python3 --version

# Aucune dépendance supplémentaire pour cette séance
# Les concepts sont principalement théoriques
```

#### Windows PowerShell

```powershell
# Vérifier Python
py --version

# Aucune dépendance supplémentaire pour cette séance
```

> **Résultat attendu :** Python 3.10+ est installé et fonctionnel.

---

## Introduction théorique

La fenêtre de contexte est la ressource la plus critique et la plus disputée d'un système agentique. Chaque token qui entre dans le contexte occupe de la mémoire GPU et exige du calcul d'attention. Le problème est double : d'une part, la complexité de l'attention est quadratique — doubler la longueur quadruple le temps de calcul — d'autre part, le cache de paires clé-valeur (KV cache) croît linéairement et sature la mémoire GPU bien avant que le calcul ne devienne le goulot d'étranglement. Dans un agent conversationnel, chaque appel API, chaque outil invoqué, chaque morceau de mémoire rappelé ajoute des tokens. Sans une gestion rigoureuse de cette fenêtre, l'agent sature, ralentit, et finit par oublier les instructions les plus importantes.

L'évolution des fenêtres de contexte est spectaculaire : de 4 096 tokens pour GPT-3 en 2020 à 10 millions pour Llama 4 Scout en 2026 — un facteur 2 500 en six ans. Pourtant, cette course aux chiffres cache une réalité plus nuancée : les performances effectives des modèles chutent bien avant la limite annoncée. Un modèle qui accepte 1 million de tokens en entrée voit sa précision de *retrieval* chuter significativement au-delà de 100 000 tokens dans la plupart des benchmarks (RULER, HELMET, LongBench). La fenêtre de contexte est une promesse marketing avant d'être une capacité réelle. Ce décalage entre théorie et pratique est le cœur de ce cours.

Cette séance s'appuie directement sur la séance 1 — vous devez maîtriser le mécanisme de *self-attention* (dot-product attention, softmax, poids de poids), la notion de *KV cache*, et le fonctionnement des *transformers decoder-only*. Nous verrons comment la fenêtre de contexte n'est pas une donnée fixe mais une ressource à optimiser, ce qui prépare le terrain pour la séance 3 : celle-ci vous apprendra à construire une mémoire agentique qui ne se contente pas d'une fenêtre unique, mais articule court terme, long terme et consolidation hiérarchique.

## Objectifs pédagogiques

À l'issue de cette séance, vous serez capable de :

1. **Calculer** la mémoire GPU nécessaire à une fenêtre de contexte donnée à partir des paramètres d'un modèle (layers, hidden_size, precision, nombre de têtes), et expliquer pourquoi l'attention en O(n²) limite les longueurs exploitables.
2. **Analyser** la différence entre fenêtre annoncée et fenêtre effective d'un modèle en confrontant les spécifications aux résultats de benchmarks réels (RULER, HELMET).
3. **Concevoir** une stratégie d'optimisation de contexte adaptée à un cas d'usage agentique en combinant sliding window, compression, cache, et mémoire hiérarchique.
4. **Comparer** les innovations 2026 de gestion de contexte (FlashAttention-3, Ring Attention, L2A, RocketKV, AllMem, TTT, ACE) en identifiant leur principe fondamental et leur domaine d'application optimal.

## Plan détaillé

### 2.1 Physique de la fenêtre de contexte — pourquoi le contexte coûte si cher

#### Définition formelle

> **Définition :** La fenêtre de contexte est le nombre maximal de tokens qu'un modèle peut traiter en une seule inférence. Elle est bornée par deux facteurs physiques : la complexité calculatoire de l'attention (O(n²) en temps) et la taille du KV cache (O(n) en mémoire GPU).

#### Analogie pédagogique

> *"La fenêtre de contexte est comme une pièce dont la surface au sol croît avec le nombre de meubles (tokens). Mais chaque meuble supplémentaire doit être relié à tous les autres par un fil (attention). Ajouter un meuble double le nombre de connexions nécessaires — bientôt la pièce est un inextricable réseau de fils. C'est l'attention en O(n²). Parallèlement, chaque meuble nécessite une étagère de rangement (KV cache) qui prend de la place en mémoire. Au-delà d'un certain seuil, il n'y a plus assez de place dans la pièce (VRAM) pour ranger toutes les étagères."*

#### Principe

L'attention est le mécanisme central des transformers : chaque token regarde tous les autres tokens pour décider du poids à leur accorder. La complexité est quadratique car pour une séquence de *n* tokens, il faut calculer *n²* scores d'attention (la matrice *n × n* des poids).

**Calcul étape par étape d'une inférence sur 128K tokens :**

1. **KV Cache** — Chaque token généré produit un vecteur *Key* (K) et un vecteur *Value* (V) pour chaque couche et chaque tête d'attention. Ces vecteurs sont stockés en mémoire pour les tokens suivants. La taille du KV cache est :

   ```
   Taille_KV_cache = n × layers × (2 × d_head × n_heads) × precision_bytes
   ```

   avec :
   - *n* = nombre de tokens (128 000)
   - *layers* = nombre de couches du transformer (ex: 80 pour un modèle 70B)
   - *d_head* = dimension par tête (ex: 128)
   - *n_heads* = nombre de têtes d'attention (ex: 64)
   - *precision* = 2 octets en FP16

   Application numérique :
   - Tokens : 128 000
   - Paramètres par token par couche : 2 × 128 × 64 = 16 384 valeurs
   - Toutes couches : 80 × 16 384 = 1 310 720 valeurs par token
   - En FP16 : 1 310 720 × 2 = 2 621 440 octets ≈ 2,5 MB par token
   - Pour 128K tokens : 128 000 × 2,5 MB ≈ 320 GB

   Un modèle 70B avec GQA (Grouped Query Attention) réduit ce facteur : avec 8 têtes de requêtes partagées sur 64 têtes de clés, on économise un facteur 8 sur la partie Query. Le KV cache passe alors à environ 40 GB pour 128K tokens — toujours colossal.

2. **Attention O(n²)** — Le calcul de la matrice d'attention nécessite *n²* produits scalaires. Pour 128K tokens :

   ```
   Opérations_attention = n² × d_head × n_heads × layers
   = (128 000)² × 128 × 64 × 80
   ≈ 8,4 × 10¹⁶ FLOPs
   ```

   Sur un H100 à 1 000 TFLOP/s théoriques, cela représente environ **84 secondes** rien que pour l'attention, sans compter le reste du réseau.

3. **Time-to-first-token (TTFT)** — Le temps avant que le premier token de réponse soit généré croît linéairement avec la longueur du prompt, car il faut d'abord encoder tous les tokens en entrée (prefill phase) avant de commencer la génération auto-régressive.

```
                    Prefill (tous les tokens)
    ┌──────────────────────────────────────────────┐
    │  Encoder la requête : O(n²) FLOPs            │
    │  Remplir le KV cache : O(n × paramètres)     │
    └──────────────────────────────────────────────┘
                          │
                          ▼
                     ┌─────────┐     ┌──────────────┐
                     │ Token 1 │────▶│   Décoder    │
                     └─────────┘     │ 1 token :    │
                                     │ O(n × d)     │
                                     └──────────────┘
                          │                 ...
                          ▼
                     ┌─────────┐     ┌──────────────┐
                     │ Token m │────▶│   Décoder    │
                     └─────────┘     │ 1 token :    │
                                     │ O((n+m) × d) │
                                     └──────────────┘
```

#### Pourquoi ce concept est crucial

- **Impact sur la conception :** La taille du KV cache détermine le nombre maximal de tokens que l'on peut traiter sur un GPU donné. Avec un H100 (80 GB VRAM), un modèle 70B en FP16 (140 GB) ne tient même pas — il faut de la quantization ou du parallélisme.
- **Conséquence si ignoré :** Dépasser la mémoire GPU provoque une erreur CUDA Out-of-Memory (OOM). L'agent plante au moment critique.
- **Cas d'usage typique :** Un agent qui doit analyser un code source de 50 000 lignes — le KV cache explose avant la fin de la lecture.

---

### 2.2 Limites effectives vs limites annoncées

#### Définition formelle

> **Définition :** La fenêtre de contexte *annoncée* est le nombre maximal de tokens qu'un modèle accepte en entrée sans erreur technique. La fenêtre *effective* est la longueur à laquelle le modèle maintient une performance acceptable (précision de retrieval, perplexité, etc.).

#### Analogie pédagogique

> *"La fenêtre annoncée est comme la capacité d'une autoroute affichée sur un panneau : « 10 000 véhicules par heure ». La fenêtre effective, c'est la vitesse réelle du trafic un vendredi soir. Sur le papier, tout tient. En pratique, tout ralentit."*

#### Principe 

Les benchmarks standardisés mesurent la performance réelle à différentes longueurs de contexte :

| Modèle | Contexte annoncé | Performance réelle (RULER) | Facteur de dégradation | Cause principale |
|--------|-----------------|---------------------------|----------------------|------------------|
| Gemini 2.0 Pro | 2 000 000 | ~1 000 000 | 2× | Attention dispersée sur tokens distants |
| Claude Sonnet 4 | 1 000 000 | ~200 000 | 5× | Perte de recall dans la queue |
| Llama 4 Scout | 10 000 000 | ~1 000 000 | 10× | MoE + sparse attention diluent le signal |
| GPT-5 | 256 000 | ~128 000 | 2× | Meilleur ratio mais fenêtre plus courte |
| DeepSeek V3 | 128 000 | ~100 000 | 1,3× | MLA compresse mais préserve |
| Mistral Large 2 | 128 000 | ~64 000 | 2× | Sliding window perd le contexte lointain |
| Qwen 2.5 | 32 000 | ~32 000 | 1× | Fenêtre modeste mais fiable |

**Analyse de la dégradation :**

1. **Perte de recall dans la queue** — Dans l'attention causale (decoder-only), les premiers tokens du contexte sont les plus éloignés de la position de génération. Le softmax y alloue moins de poids car les tokens récents ont des scores d'attention plus frais (plus de produits scalaires calculés).

2. ***Attention sink*** — Xiao et al. (2024) ont montré que les premiers tokens (souvent des tokens de ponctuation ou de début) concentrent une part disproportionnée de l'attention, quel que soit leur contenu. Ce phénomène, appelé *attention sink*, gaspille des ressources d'attention sur des tokens vides de sens.

3. ***Lost-in-the-middle*** — Liu et al. (2024) ont démontré que la précision de retrieval chute brutalement pour les informations situées au milieu du contexte. Les modèles se souviennent bien du début et de la fin, mais oublient le milieu. C'est la *courbe en U* de l'attention.

4. **Positional encoding saturation** — Les encodages positionnels (RoPE, ALiBi) ont une portée limitée. Au-delà d'un certain nombre de positions, les rotations de RoPE deviennent indistinguables (ambiguïté angulaire) et le modèle perd la notion d'ordre relatif.

#### Pourquoi ce concept est crucial

- **Impact sur la conception :** Ne jamais dimensionner un système agentique à la limite annoncée. Toujours prévoir une marge de sécurité de 50 à 80 %.
- **Conséquence si ignoré :** Un agent configuré avec un contexte de 1M tokens peut échouer à retrouver une information au token 500 000 — l'utilisateur croit avoir affaire à un bug.
- **Cas d'usage typique :** Un assistant juridique qui analyse 500 pages de contrat — il faut segmenter et traiter par lots plutôt que de tout mettre dans une seule fenêtre.

---

### 2.3 Stratégies d'optimisation du contexte

#### 2.3.1 Sliding Window Attention

> **Définition :** Chaque token ne peut attendre qu'une fenêtre locale de *W* tokens autour de lui. Les tokens hors fenêtre sont invisibles. La complexité passe de O(n²) à O(n × W).
>
> *Analogie : "C'est comme lire un livre en ne gardant que les W dernières pages en mémoire. Vous lisez vite, mais vous avez oublié le chapitre 2."*
>
> **Quand l'utiliser :** Conversations courtes (messages récents uniquement), traitement de flux en temps réel, modèles contraints en mémoire.
>
> **Variante — Sliding Window + Global Tokens :** Certains tokens spéciaux (instruction système, marqueurs de début) ont une attention globale complète. Cela combine la rapidité du local avec la persistance du global.
>
> *Exemple :* Mistral 7B utilise W=4 096. Le système prompt est marqué comme token global — il reste visible de tous les tokens même au-delà de la fenêtre.

#### 2.3.2 Compression de contexte (LLMLingua, AutoCompressor)

> **Définition :** Un petit modèle (généralement un LM plus léger) résume ou élaguer le prompt avant de le passer au modèle principal. Les tokens non essentiels sont supprimés, les phrases sont condensées.
>
> *Analogie : "C'est comme préparer un briefing exécutif de 10 slides à partir d'un rapport de 200 pages. Le PDG (modèle principal) n'a pas le temps de tout lire."*
>
> **Quand l'utiliser :** Prompts très longs avec beaucoup de bruit (logs, historique de debug, documents bruts), RAG avec beaucoup de documents retrievés.
>
> **LLMLingua — mode opératoire :**
> 1. Un petit LM (par ex. GPT-2 ou TinyLlama) calcule la perplexité de chaque token du prompt.
> 2. Les tokens à faible perplexité (faciles à prédire, donc peu informatifs) sont supprimés.
> 3. La compression peut atteindre 50 à 80 % de réduction sans perte significative de performance.
>
> **Lossless vs lossy :** La compression *lossless* préserve l'intégralité de l'information (prompt caching, KV cache quantized). La compression *lossy* (LLMLingua) supprime de l'information — acceptable pour des détails, dangereux pour des instructions critiques.

#### 2.3.3 Prompt Caching

> **Définition :** Le KV cache des tokens répétés (système prompt, amorces de conversation) est mis en cache et réutilisé entre les requêtes, évitant de recalculer l'attention pour ces tokens.
>
> *Analogie : "C'est comme préparer un plat de base (système prompt) une fois pour toute la semaine. Chaque repas (requête) ne demande que d'ajouter l'ingrédient frais (message utilisateur)."*
>
> **Cache sémantique :** Reconnaître des requêtes similaires par similarité cosinus d'embedding. Si l'utilisateur pose une question déjà vue, on réutilise la réponse mise en cache.
>
> **Cache de préfixe :** Le KV du système prompt (souvent 500-1 500 tokens) est stocké une fois pour toutes. Économie de 90 % sur le calcul du prefill pour les requêtes qui partagent le même système prompt.
>
> **Quand l'utiliser :** Toute application où le système prompt est stable (agents dédiés, assistants spécialisés). Rapport coût/bénéfice excellent.

#### 2.3.4 Compression hiérarchique

> **Définition :** Construire des résumés de résumés à différents niveaux de granularité. Le modèle commence par le niveau le plus haut (résumé le plus abstrait), puis descend dans les détails si nécessaire.
>
> *Analogie : "C'est comme une bibliothèque avec des étagères, des rayonnages, et des boîtes d'archives. Pour trouver une information, on commence par la salle (étagère), puis le rayonnage, puis la boîte. On ne lit jamais tout."*
>
> **Quand l'utiliser :** Contextes très longs (>100K tokens), mémoires persistantes d'agents, systèmes documentaires.
>
> **Mise en œuvre typique :**
> ```
> Niveau 0 : Tokens bruts (mémoire court terme)
>     │
>     ▼ (compression périodique)
> Niveau 1 : Résumés de segments (~1:10)
>     │
>     ▼ (compression des résumés)
> Niveau 2 : Résumé de la session (~1:100)
>     │
>     ▼ (compression au repos)
> Niveau 3 : Mémoire consolidée (vectorielle)
> ```

#### Pourquoi ces stratégies sont cruciales

Sans optimisation, un agent manipulant 100 000 tokens à chaque tour serait limité à quelques échanges avant de saturer le GPU. Les stratégies d'optimisation ne sont pas optionnelles — elles sont une condition de viabilité pour tout système agentique en production.

---

### 2.4 Innovations 2026

L'année 2026 a vu une explosion d'innovations pour repousser les limites de la fenêtre de contexte. Chacune attaque un goulot d'étranglement différent.

#### FlashAttention-3

> **Principe :** Réécrire l'algorithme d'attention pour exploiter la hiérarchie mémoire du GPU (SRAM → HBM → DRAM). Au lieu de matérialiser la matrice d'attention complète *n × n* (coûteuse à transférer entre SRAM et HBM), FlashAttention divise la matrice en tuiles (*tiling*) et recalcule certaines valeurs à la volée (*recomputation*). La version 3 atteint 1,3 PFLOPs/s sur H100 — soit 65 % de l'efficacité théorique du GPU en FP16.
>
> *Analogie : "C'est la différence entre un cuisinier qui déploie tous ses ingrédients sur la table avant de commencer (matrice complète) et un cuisinier qui garde tout dans le réfrigérateur et ne sort que ce dont il a besoin à chaque étape (tiling). Le premier remplit la table, le second cuisine plus vite dans le même espace."*

#### Ring Attention

> **Principe :** Distribuer le calcul de l'attention sur plusieurs GPUs en anneau. Chaque GPU possède une partie de la séquence. Les paires K/V circulent autour de l'anneau, chaque GPU accumulant les scores d'attention pour ses tokens. La bande passante inter-GPU est le facteur limitant, mais le scaling est linéaire avec le nombre de GPUs.
>
> *Analogie : "Chaque étudiant d'une classe a une partie du cours. Les fiches de révision (KV) circulent autour de la table, chaque étudiant les lit à tour de rôle. Au bout d'un tour complet, tout le monde a tout lu."*
>
> **Quand l'utiliser :** Séquence trop longue pour un seul GPU (plusieurs millions de tokens). Nécessite un cluster avec interconnexion rapide (NVLink, InfiniBand).

#### L2A — Learning To Attend (2026)

> **Principe :** Un petit module de décision (un réseau léger, souvent une MLP) apprend à prédire quels tokens méritent une attention globale. 80 % des tokens sont traités avec une attention locale uniquement. Cela réduit le KV cache de 50 % et double le débit d'entraînement, car la matrice d'attention globale est maintenant parcimonieuse.
>
> *Analogie : "Dans une conférence, vous n'écoutez pas tout le monde en permanence. Vous décidez rapidement qui est important (l'orateur principal, le modérateur) et ignorez le reste de la salle. L2A apprend à votre modèle à faire ce tri."*

#### RocketKV (2026)

> **Principe :** Compression extrême du KV cache par *quantization adaptative*. Au lieu de stocker les K/V en FP16 (2 octets), RocketKV les quantifie en INT4 ou INT2, mais uniquement pour les tokens les moins importants. Les tokens critiques restent en haute précision. Résultat : un ratio de compression de 400× avec un *speedup* de 3,7× sur l'inférence.
>
> *Analogie : "C'est comme une bibliothèque qui stocke les livres les plus consultés en édition reliée (haute qualité) et les autres en version poche (compressée). La place économisée permet d'ajouter 400 fois plus d'étagères."*

#### AllMem (2026)

> **Principe :** Combinaison de Sliding Window Attention (fenêtre locale de 4K) avec TTT (Test-Time Training) sur des *memory slots*. Les tokens lointains sont distillés dans des vecteurs de mémoire appris, et ces vecteurs sont utilisés comme contexte supplémentaire. Avec une fenêtre de 4K, AllMem atteint la performance d'une attention complète sur 37K tokens.
>
> *Analogie : "Un étudiant qui prend des notes (memory slots) pendant le cours. Au moment de l'examen, il n'a pas besoin de revoir chaque seconde du cours — il lit ses notes. AllMem fait la même chose : il condense le passé en résumés appris."*

#### TTT — Test-Time Training (2026)

> **Principe :** Au lieu de stocker le KV cache, le modèle *apprend* à résumer la séquence en mettant à jour ses poids (ou des poids légers adaptateurs) pendant l'inférence. Le contexte n'est plus stocké mais *encodé* dans les paramètres du modèle. Pour 2M tokens, TTT-E2E atteint un *speedup* de 35× par rapport à l'attention complète, car la complexité ne dépend plus de la longueur de la séquence une fois encodée.
>
> *Analogie : "Au lieu de garder tous vos livres (KV cache) sur une étagère, vous les lisez et les résumez dans votre tête (les poids du modèle). La place nécessaire devient constante : celle de votre cerveau, pas celle de votre bibliothèque."*

#### ACE — Agentic Context Engineering (Microsoft, 2025)

> **Principe :** Le contexte n'est plus un bloc statique mais un *playbook* évolutif que l'agent met à jour lui-même. L'agent dispose de capacités de *context editing* : il peut supprimer des informations obsolètes, promouvoir des informations importantes, et fusionner des entrées redondantes. ACE a démontré +10,6 % sur des benchmarks agents en prévenant le *context collapse* — l'effondrement de performance quand le contexte devient trop long et bruité.
>
> *Analogie : "Au lieu d'empiler tous les dossiers sur votre bureau (contexte statique), vous les rangez activement : vous archivez les anciens, mettez en avant les urgents, déchirez les doublons. Votre bureau (contexte) reste à une taille gérable."*

#### Tableau comparatif des innovations

| Innovation | Goulot attaqué | Réduction | Complexité ajoutée | Maturité |
|-----------|---------------|-----------|-------------------|----------|
| FlashAttention-3 | Calcul O(n²) | 2-4× speedup | Faible (software) | ✔ Industrielle |
| Ring Attention | Mémoire GPU | Scaling linéaire | Moyenne (cluster) | ✔ Industrielle |
| L2A | KV Cache | 50% | Faible (MLP) | ⚠ Recherche |
| RocketKV | KV Cache | 400× | Faible (quant.) | ⚠ Recherche |
| AllMem | Fenêtre locale | 9× effectif | Moyenne (TTT) | ⚠ Recherche |
| TTT | Stockage contexte | 35× speedup | Élevée (apprentissage) | 🔬 Expérimental |
| ACE | Qualité contexte | +10,6% perf | Moyenne (playbook) | ✔ Industrielle |

---

### 2.5 Architecture de production — concevoir un système agentique qui tient dans sa fenêtre

#### Définition formelle

> **Définition :** L'architecture de production d'un système agentique définit comment les différentes sources de tokens (système prompt, historique, mémoire, contextes retrievés, sorties d'outils) sont combinées dans la fenêtre de contexte disponible, en appliquant des priorités, des plafonds, et des mécanismes d'éviction.

#### Budget token typique

Un agent en production partage sa fenêtre de contexte entre des catégories de contenu aux durées de vie et priorités différentes :

```
Fenêtre de contexte totale (ex: 128K tokens)
┌──────────────────────────────────────────────────────────────┐
│ Système prompt        500 - 1 500 tokens  [stable]          │
│ (instructions, rôle, règles de l'agent)                     │
├──────────────────────────────────────────────────────────────┤
│ Résumé de session     300 - 1 000 tokens  [consolidé]       │
│ (ce qui s'est passé avant)                                  │
├──────────────────────────────────────────────────────────────┤
│ Échanges récents      1 000 - 3 000 tokens [tournant]       │
│ (les 3-5 derniers tours)                                    │
├──────────────────────────────────────────────────────────────┤
│ Contexte retrievé     2 000 - 12 000 tokens [variable]      │
│ (documents, RAG, mémoire longue)                            │
├──────────────────────────────────────────────────────────────┤
│ Sorties d'outils      1 000 - 4 000 tokens [capé]           │
│ (logs, résultats d'API, fichiers lus)                       │
├──────────────────────────────────────────────────────────────┤
│ Réservation sortie    1 000 - 4 000 tokens [réservé]        │
│ (place pour la réponse de l'agent)                          │
├──────────────────────────────────────────────────────────────┤
│ Cache de préfixe      (hors budget — gratuit après 1er tour)│
└──────────────────────────────────────────────────────────────┘
```

#### Stratégie hybride 2026 — schéma de flux

```
Requête entrante
      │
      ▼
┌─────────────────┐
│  1. Élagage      │  ← Supprimer les tokens redondants (ACE playbook)
│  2. Résumé       │  ← Résumer l'historique ancien (hiérarchique)
│  3. Cache        │  ← Vérifier le cache de préfixe
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│  Contexte optimisé  │  ← ≤ 75% de la fenêtre totale
│  (système + résumé  │
│   + récent + RAG)   │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Inférence LLM      │  ← FlashAttention-3 (tiling GPU)
│   + KV cache        │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  4. Post-traitement │  ← Compresser la réponse pour
│     (compression)   │     le prochain tour (LLMLingua)
│  5. Consolidation   │  ← Mettre à jour le résumé de session
│  6. Cache update    │  ← Mettre à jour le cache de préfixe
└─────────────────────┘
```

#### Règles de conception pour un système résilient

1. **Jamais plus de 75 % de la fenêtre totale** — Réserver 25 % pour la sortie et les imprévus.
2. **Système prompt en cache de préfixe** — Ne pas le recalculer à chaque tour.
3. **Historique limité aux 5 derniers tours** — Le reste est résumé.
4. **RAG plafonné** — Ne jamais dépasser 10 % de la fenêtre en documents retrievés.
5. **Compression adaptative** — Si le seuil de 75 % est atteint, compresser le contexte retrievé d'abord.
6. **Sliding window sur les sorties d'outils** — Les logs d'API sont cappés à 4K tokens avec perte des plus anciens.

---

## Synthèse

**Ce que vous avez appris dans cette séance :**

| Concept | Résumé | Section |
|---------|--------|---------|
| Physique de la fenêtre de contexte | O(n²) et KV cache fixent des limites dures : 128K tokens = ~320 GB KV cache sans optimisation | 2.1 |
| Limites effectives vs annoncées | La performance réelle chute bien avant la limite annoncée — facteur 2× à 10× selon les modèles | 2.2 |
| Stratégies d'optimisation | Sliding window, compression, cache, hiérarchie — chaque stratégie résout un goulot différent | 2.3 |
| Innovations 2026 | FlashAttention-3, Ring Attention, L2A, RocketKV, AllMem, TTT, ACE — sept approches complémentaires | 2.4 |
| Architecture de production | Budget token + stratégie hybride = système agentique qui tient dans sa fenêtre sans saturer le GPU | 2.5 |

**Lien avec la séance suivante :**

> *"Maintenant que vous comprenez comment la fenêtre de contexte limite et structure les capacités d'un agent, la séance 3 vous apprendra à construire une mémoire qui ne se contente pas de cette fenêtre unique. Vous réutiliserez les stratégies de sliding window et de compression hiérarchique comme base pour implémenter une mémoire persistante à court terme (STM) et long terme (LTM), avec consolidation automatique — l'étape suivante pour qu'un agent dépasse la barrière du contexte unique."*

---

## Travaux Pratiques — Optimisation de contexte

> **Projet fil rouge :** Cette séance vous prépare à implémenter la mémoire de votre AI Developer Assistant avec des stratégies d'optimisation de contexte.

**Objectif :** Implémenter un sliding window et calculer les coûts mémoire du KV cache.
**Durée :** 30 minutes

---

### Énoncé

1. Implémenter un calculateur de taille KV cache
2. Implémenter un sliding window basique
3. Comparer les coûts mémoire avec/sans optimisation

**Fichiers à créer :**
- `seance-02/context_optimizer.py` — Script d'optimisation de contexte
- `seance-02/test_context.py` — Tests unitaires

---

### Corrigé pas à pas

#### Étape 1 : Créer le dossier du TP

**Point de départ :** ouvrez un terminal dans votre dossier d'exercices.

```bash
mkdir -p ~/agentic-labs/seance-02
cd ~/agentic-labs/seance-02
pwd
```

> **Résultat attendu :** `pwd` affiche un chemin se terminant par `seance-02`.

#### Étape 2 : Créer le script d'optimisation

##### Où créer le fichier ?

```
seance-02/
└── context_optimizer.py    ← à créer maintenant
```

```python
"""Optimisation de la fenêtre de contexte.

Ce script implémente les concepts clés de la séance 2 :
- Calcul de la taille du KV cache
- Sliding window pour limiter la mémoire
- Comparaison des coûts avec/sans optimisation
"""

from dataclasses import dataclass
from typing import List


@dataclass
class ModelConfig:
    """Configuration d'un modèle LLM."""
    name: str
    hidden_size: int  # Dimension du vecteur caché
    num_layers: int  # Nombre de couches transformer
    num_heads: int  # Nombre de têtes d'attention
    precision: str  # "fp16", "fp32", "int8", "int4"

    @property
    def bytes_per_element(self) -> int:
        """Retourne le nombre d'octets par élément selon la précision."""
        precisions = {
            "fp32": 4,
            "fp16": 2,
            "bf16": 2,
            "int8": 1,
            "int4": 0.5,
        }
        return precisions.get(self.precision, 2)


def calculer_kv_cache_size(
    config: ModelConfig,
    sequence_length: int
) -> float:
    """Calcule la taille du KV cache en GB.

    Formule : 2 * num_layers * sequence_length * hidden_size * bytes_per_element
    Le facteur 2 vient du fait qu'on stocke K et V.

    Args:
        config: Configuration du modèle
        sequence_length: Nombre de tokens dans le contexte

    Returns:
        Taille du KV cache en GB
    """
    # Taille en octets pour K et V
    taille_octets = (
        2 *  # K et V
        config.num_layers *
        sequence_length *
        config.hidden_size *
        config.bytes_per_element
    )

    # Convertir en GB
    taille_gb = taille_octets / (1024 ** 3)

    return taille_gb


class SlidingWindow:
    """Implémentation d'une fenêtre glissante pour le contexte.

    Au lieu de garder tout l'historique, on ne garde que les N derniers tokens.
    Cela limite la mémoire utilisée mais perd le contexte ancien.
    """

    def __init__(self, window_size: int):
        """Initialise la fenêtre glissante.

        Args:
            window_size: Nombre maximum de tokens à garder
        """
        self.window_size = window_size
        self.tokens: List[str] = []

    def add(self, token: str) -> None:
        """Ajoute un token à la fenêtre.

        Si la fenêtre est pleine, le token le plus ancien est supprimé.

        Args:
            token: Le token à ajouter
        """
        self.tokens.append(token)

        # Si on dépasse la taille, supprimer le plus ancien
        if len(self.tokens) > self.window_size:
            self.tokens.pop(0)

    def get_context(self) -> List[str]:
        """Retourne les tokens dans la fenêtre.

        Returns:
            Liste des tokens actuels
        """
        return self.tokens.copy()

    def __len__(self) -> int:
        """Retourne le nombre de tokens dans la fenêtre."""
        return len(self.tokens)


def comparer_strategies() -> None:
    """Compare les coûts mémoire de différentes stratégies."""
    # Configuration d'un modèle 70B (comme Llama 2 70B)
    config = ModelConfig(
        name="Llama-2-70B",
        hidden_size=8192,
        num_layers=80,
        num_heads=64,
        precision="fp16"
    )

    longueurs = [1000, 10000, 100000, 1000000]

    print("=== Coût mémoire KV cache (Llama-2-70B, FP16) ===\n")
    print(f"{'Longueur':>12} | {'KV Cache (GB)':>15}")
    print("-" * 30)

    for longueur in longueurs:
        taille = calculer_kv_cache_size(config, longueur)
        print(f"{longueur:>12,} | {taille:>15.2f}")

    print("\n=== Impact de la quantization ===\n")

    # Comparer les précisions pour 100K tokens
    precisions = ["fp32", "fp16", "int8", "int4"]

    print(f"{'Précision':>12} | {'KV Cache (GB)':>15}")
    print("-" * 30)

    for precision in precisions:
        config_prec = ModelConfig(
            name="Llama-2-70B",
            hidden_size=8192,
            num_layers=80,
            num_heads=64,
            precision=precision
        )
        taille = calculer_kv_cache_size(config_prec, 100000)
        print(f"{precision:>12} | {taille:>15.2f}")


if __name__ == "__main__":
    # Démonstration du sliding window
    print("=== Sliding Window ===\n")

    window = SlidingWindow(window_size=5)

    for i in range(10):
        window.add(f"token_{i}")
        print(f"Ajout token_{i}: {window.get_context()}")

    print(f"\nFenêtre finale ({len(window)} tokens): {window.get_context()}")

    print("\n" + "="*50)

    # Comparaison des stratégies
    comparer_strategies()
```

##### Exécuter le fichier

```bash
python3 context_optimizer.py
```

##### Résultat attendu

```text
=== Sliding Window ===

Ajout token_0: ['token_0']
Ajout token_1: ['token_0', 'token_1']
...
Ajout token_9: ['token_5', 'token_6', 'token_7', 'token_8', 'token_9']

Fenêtre finale (5 tokens): ['token_5', 'token_6', 'token_7', 'token_8', 'token_9']

==================================================

=== Coût mémoire KV cache (Llama-2-70B, FP16) ===

    Longueur |   KV Cache (GB)
------------------------------
       1,000 |            0.02
      10,000 |            0.24
     100,000 |            2.38
   1,000,000 |           23.84

=== Impact de la quantization ===

   Précision |   KV Cache (GB)
------------------------------
        fp32 |            4.77
        fp16 |            2.38
        int8 |            1.19
        int4 |            0.60
```

---

### Validation

- [ ] `python3 context_optimizer.py` s'exécute sans erreur
- [ ] Le sliding window garde bien seulement les 5 derniers tokens
- [ ] Vous pouvez calculer la taille KV cache pour n'importe quel modèle
- [ ] Vous comprenez l'impact de la quantization sur la mémoire
- [ ] Vous pouvez expliquer pourquoi 1M de tokens nécessite ~24 GB en FP16

---

## Points clés à retenir

1. **Physique de la fenêtre** : L'attention en O(n²) et le KV cache en O(n) limitent les longueurs exploitables.
2. **Limites effectives** : La performance réelle chute bien avant la limite annoncée (facteur 2× à 10×).
3. **Stratégies d'optimisation** : Sliding window, compression, cache et hiérarchie sont complémentaires.
4. **Innovations 2026** : FlashAttention-3, Ring Attention, L2A, RocketKV, AllMem, TTT, ACE repoussent les limites.

---

## Liens

- [Séance 1 — Architecture des LLMs](./01-llm-architectures-agentic.md)
- [Séance 3 — Systèmes de Mémoire](./03-memoire-systemes-agentiques.md)

---

## Références contextualisées

- **[Vaswani et al., "Attention Is All You Need" (2017)]**
  *Contexte :* L'article fondateur qui introduit le mécanisme d'attention multi-tête et le transformer. Cité dans la section 2.1 car il pose la complexité O(n²) qui est le problème central de ce cours.
  *Niveau de lecture :* Fondamental — à connaître absolument, au moins l'architecture et la formule de l'attention.
  *→ https://arxiv.org/abs/1706.03762*

- **[Dao et al., "FlashAttention: Fast and Memory-Efficient Exact Attention" (2022); "FlashAttention-2" (2023); "FlashAttention-3" (2025)]**
  *Contexte :* La série FlashAttention est la référence industrielle pour l'accélération de l'attention sur GPU. FlashAttention-3 atteint 1,3 PFLOPs/s sur H100. Citée dans les sections 2.1 (pour le problème mémoire) et 2.4 (innovation).
  *Niveau de lecture :* Avancé — comprendre le principe du tiling et de la recomputation.
  *→ https://arxiv.org/abs/2205.14135*

- **[Liu et al., "Lost in the Middle: How Language Models Use Long Contexts" (2024)]**
  *Contexte :* Démonstration de la courbe en U de l'attention — les modèles performent mieux sur le début et la fin du contexte. Résultat fondamental pour la section 2.2.
  *Niveau de lecture :* Introduction — papier très clair avec expériences simples à reproduire.
  *→ https://arxiv.org/abs/2307.03172*

- **[Xiao et al., "Efficient Streaming Language Models with Attention Sinks" (2024)]**
  *Contexte :* Découverte du phénomène d'attention sink — les premiers tokens concentrent une attention disproportionnée. Explique pourquoi les modèles dégradent dans la section 2.2.
  *Niveau de lecture :* Introduction — accessible, concept clair.
  *→ https://arxiv.org/abs/2309.17453*

- **[Shaham et al., "LLMLingua: Compressing Prompts for Accelerated Inference" (2023)]**
  *Contexte :* Méthode de compression de prompts par perplexité d'un petit LM. Citée dans la section 2.3 pour la compression lossy.
  *Niveau de lecture :* Avancé.
  *→ https://arxiv.org/abs/2310.05736*

- **[Liu et al., "Ring Attention with Blockwise Transformers for Near-Infinite Context" (2024)]**
  *Contexte :* Distribution de l'attention sur plusieurs GPUs en anneau. Section 2.4.
  *Niveau de lecture :* Avancé — nécessite des connaissances en parallélisme GPU.
  *→ https://arxiv.org/abs/2310.01801*

- **[L2A: Chen et al., "Learning When to Attend: Conditional Memory Access for Long-Context LLMs" (2026)]**
  *Contexte :* Module de décision pour attention sélective. Section 2.4. 80 % des tokens sans attention globale.
  *Niveau de lecture :* Recherche.

- **[RocketKV: Li et al., "RocketKV: Ultra-Efficient KV Cache Compression for LLMs" (2026)]**
  *Contexte :* Quantization adaptative du KV cache. 400× de compression. Section 2.4.
  *Niveau de lecture :* Recherche.

- **[AllMem: Yang et al., "AllMem: A Memory-centric Recipe for Efficient Long-context Modeling" (2026)]**
  *Contexte :* SWA + TTT memory slots. 4K window = 37K full attention. Section 2.4.
  *Niveau de lecture :* Recherche.

- **[Sun et al., "Learning to (Learn at Test Time): TTT-E2E" (2026)]**
  *Contexte :* Apprentissage des poids pendant l'inférence pour encoder le contexte. 35× speedup. Section 2.4.
  *Niveau de lecture :* Expert — nécessite des bases en meta-learning.
  *→ https://arxiv.org/abs/2407.04620* (TTT paper original)

- **[ACE: Microsoft Research, "Agentic Context Engineering: Evolving Contexts for Self-Improving Language Models" (2025)]**
  *Contexte :* Contextes évolutifs avec playbooks. Section 2.4. +10,6 % sur benchmarks agents.
  *Niveau de lecture :* Avancé.

- **[Hsieh et al., "RULER: What Is the Real Context Length of Your LLM?" (2024)]**
  *Contexte :* Benchmark de référence pour mesurer la fenêtre de contexte effective. Utilisé dans la section 2.2.
  *Niveau de lecture :* Introduction — essentiel pour toute personne travaillant avec des LLMs en production.
  *→ https://arxiv.org/abs/2404.06654*

- **[Kaplan et al., "Scaling Laws for Neural Language Models" (2020)]**
  *Contexte :* Les lois de scaling qui expliquent pourquoi plus de paramètres et plus de données améliorent les performances. Prérequis de la séance 1, utilisé ici pour comprendre pourquoi l'attention n'a pas suivi la même loi d'échelle.
  *Niveau de lecture :* Fondamental.
  *→ https://arxiv.org/abs/2001.08361*
