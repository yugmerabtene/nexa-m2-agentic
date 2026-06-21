# Séance 1 — Architecture des LLMs & Genèse Agentique

> **Durée estimée :** 2 heures

---

## Description

Cette séance pose les fondations de l'Agentic AI en retraçant l'évolution des architectures de LLMs de 2017 à 2026. Vous découvrirez comment les modèles de langage sont passés de simples générateurs de texte à des systèmes agentiques capables de raisonnement, d'utilisation d'outils et de planification. Les concepts clés incluent les scaling laws, les architectures MoE/GQA/MLA, et les comportements émergents comme le Chain-of-Thought et ReAct.

---

## Prérequis

Avant de commencer cette séance, assurez-vous d'avoir :

- Connaissances de base en deep learning (transformers, attention, tokens)
- Python 3.10+ installé
- Un environnement de développement configuré

### Installation des dépendances

#### Linux et macOS

```bash
# Vérifier Python et pip
python3 --version
python3 -m pip --version

# Installer les dépendances pour cette séance
python3 -m pip install tiktoken pytest

# Vérifier opencode
opencode --version
```

#### Windows PowerShell

```powershell
# Vérifier Python et pip
py --version
py -m pip --version

# Installer les dépendances pour cette séance
py -m pip install tiktoken pytest

# Vérifier opencode
opencode --version
```

> **Résultat attendu :** Python 3.10+, pip, tiktoken et opencode sont installés et fonctionnels.

---

## Introduction théorique

**Le problème.** En 2020, un modèle de langage comme GPT-3 était une machine à compléter du texte : on lui donnait un prompt, il produisait une suite probabiliste de tokens. Il ne raisonnait pas, n'utilisait pas d'outils, ne planifiait pas. C'était un *oracle statistique*, pas un agent. Pourtant, six ans plus tard, les mêmes architectures fondamentales — transformeurs, attention, décodage auto-régressif — servent de socle à des systèmes capables de rédiger du code, de naviguer sur le web, de décomposer des problèmes complexes en sous-étapes, et d'interagir avec des API en temps réel. Comment une même famille d'architectures a-t-elle produit un saut qualitatif aussi radical ? Cette séance répond à cette question en retraçant l'évolution architecturale et algorithmique qui a transformé des modèles de langage statiques en *agents* dynamiques.

**Contexte : de GPT-3 à 2026.** L'histoire commence avec les *scaling laws* (Kaplan et al., 2020) : plus un modèle est grand, plus il est performant, suivant une loi de puissance prévisible. Cette découverte a déclenché une course à la taille — GPT-3 (175B), PaLM (540B), Llama 3 (405B) — jusqu'à ce qu'on bute sur un mur énergétique et computationnel. La réponse est venue de deux directions : d'une part, des architectures plus efficaces (MoE, GQA, MLA) qui découplent la capacité totale du coût d'inférence ; d'autre part, des *comportements émergents* — raisonnement pas à pas (Chain-of-Thought), boucles action-observation (ReAct), utilisation d'outils — qui transforment le LLM d'un générateur de texte en un *système agentique*. En 2026, la frontière entre "modèle de langage" et "agent" s'est estompée : les modèles les plus récents intègrent nativement le *reasoning* (tokens de raisonnement internes), le *tool calling* structuré, et la planification multi-étapes. Le gap entre modèles frontier (API) et open-source se réduit, mais des différences cruciales persistent en termes de fiabilité, de coût et de sécurité.

**Prérequis et lien avec la séance 2.** Cette séance suppose une familiarité avec les bases du deep learning : transformeurs (attention multi-head, encodeur-décodeur), tokens et embedding, rétropropagation. Si ces concepts ne sont pas maîtrisés, la lecture du papier fondateur "Attention Is All You Need" (Vaswani et al., 2017) est recommandée en prérequis. La séance 2 (*Context Window Engineering*) prolonge directement cette réflexion : une fois qu'on comprend comment les LLMs modernes sont architecturés, la question devient comment maximiser l'utilisation de leur fenêtre de contexte — mémoire de travail, repérage, accès sélectif à l'information. Les architectures que nous détaillons ici (GQA, MLA) déterminent directement la taille de fenêtre réalisable, faisant le pont entre architecture et ingénierie du contexte.

## Objectifs pédagogiques

À l'issue de cette séance, vous serez capable de :

1. **Analyser** l'évolution des architectures de LLMs de 2017 à 2026 en identifiant les ruptures clés (transformers, scaling laws, MoE, reasoning tokens) et en les situant sur une frise chronologique argumentée.
2. **Expliquer** le fonctionnement de Mixture of Experts (MoE), Multi-Head Latent Attention (MLA) et Grouped Query Attention (GQA) avec des schémas et des analogies, en détaillant leur impact sur le coût d'inférence et la fenêtre de contexte.
3. **Distinguer** les mécanismes agentiques fondamentaux — Chain-of-Thought, ReAct, tool use, planification, self-reflection — en donnant pour chacun une définition, une analogie et un exemple concret d'application.
4. **Comparer** l'écosystème 2026 des modèles frontier et open-source sur les axes architecture, performance, coût et cas d'usage, en justifiant le choix d'une solution plutôt qu'une autre selon un cahier des charges donné.
5. **Évaluer** le gap entre modèles frontier et open-source en 2026 à partir de métriques standardisées (SWE-bench, coût par run, latence), et formuler une recommandation argumentée pour un scénario de production concret.

## Plan détaillé

### 1.1 Des transformers aux LLMs agentiques — Timeline 2017→2026

#### Définition

> **Timeline des LLMs agentiques :** frise chronologique raisonnée qui cartographie les innovations architecturales et algorithmiques ayant transformé les modèles de langage statiques (prédiction du prochain token) en systèmes agentiques capables de raisonnement, d'utilisation d'outils et de planification.

#### Analogie pédagogique

> *"L'évolution du LLM est comparable à celle du téléphone : en 2010, un téléphone passait des appels ; en 2025, c'est un ordinateur de poche qui fait tout, du paiement à la photo. Pourtant, les lois physiques sous-jacentes (les ondes radio, le silicium) n'ont pas changé — ce sont les couches logicielles et l'intégration de capteurs qui ont tout changé. De même, l'architecture transformeur de 2017 est toujours là, mais les couches algorithmiques qui l'entourent (reasoning, tool use, mémoire) ont fait le saut."*

#### Frise chronologique détaillée

```
2017 ● "Attention Is All You Need" — Le transformeur naît
     │  Architecture séquence-à-séquence avec attention multi-têtes.
     │  Rupture avec les RNNs : parallélisable, passage à l'échelle.
     │
2018 ● GPT / BERT — Le décodage auto-régressif vs l'encodage bidirectionnel
     │  GPT : prédiction du token suivant (génération).
     │  BERT : masquage aléatoire (compréhension).
     │  Deux philosophies qui convergeront plus tard.
     │
2020 ● GPT-3 (175B) — L'in-context learning émerge
     │  Modèle massif sans fine-tuning spécialisé.
     │  Capacité surprenante à suivre des instructions en contexte.
     │  Publication des scaling laws par Kaplan et al.
     │
2022 ● InstructGPT / RLHF — L'alignement devient crucial
     │  Fine-tuning supervisé + renforcement sur préférences humaines.
     │  Chain-of-Thought prompting (Wei et al.) : raisonnement pas à pas.
     │  Les LLMs commencent à "raisonner" explicitement.
     │
2023 ● GPT-4 / ReAct — La boucle action-observation
     │  ReAct (Yao et al.) : raisonnement + actions + observations.
     │  GPT-4 : multimodalité, raisonnement plus fiable.
     │  Llama ouvre la voie open-source.
     │  Premier boom des agents LLM (AutoGPT, BabyAGI).
     │
2024 ● MoE, GQA, MLA — L'efficacité architecturale
     │  Mixture of Experts : activer seulement les sous-réseaux pertinents.
     │  Grouped Query Attention : réduire le coût du KV cache.
     │  Multi-Head Latent Attention (DeepSeek) : compression latente.
     │  Les fenêtres de contexte explosent (1M+ tokens).
     │
2025 ● Reasoning tokens — Le raisonnement internalisé
     │  Les modèles apprennent à réfléchir avant de répondre.
     │  Tokens de raisonnement (extended thinking).
     │  Vision native : entraînement conjoint texte + image.
     │  Tool calling natif dans l'architecture.
     │
2026 ● Modèles agentiques natifs — La convergence
     │  Les LLMs sont conçus dès le départ pour être des agents.
     │  Planification intégrée, self-reflection, mémoire.
     │  Gap frontier vs open-source se réduit (mais persiste).
     │
```

#### Pourquoi cette timeline est cruciale

- **Impact sur la conception :** chaque étape de cette frise correspond à une décision concrète de design que vous rencontrerez en construisant un système agentique. Par exemple, le choix entre un modèle avec ou sans reasoning tokens natif impacte directement l'architecture de votre boucle agent.
- **Conséquence si ignorée :** sans comprendre cette évolution, on risque de ré-inventer des solutions déjà existantes, ou pire, d'utiliser un modèle de 2023 pour une tâche qui nécessite des capacités de 2026.
- **Cas d'usage typique :** évaluer si un projet nécessite un modèle avec tool calling natif (2025+) ou si une approche plus simple avec prompting ReAct (2023) suffit.

---

### 1.2 Scaling Laws & Architecture Moderne — MoE, MLA, GQA

#### 1.2.1 Scaling Laws : pourquoi plus grand n'est plus la seule réponse

##### Définition formelle

> **Scaling Laws (lois de passage à l'échelle) :** relations mathématiques qui prédisent la performance d'un LLM en fonction de trois variables — nombre de paramètres (N), taille des données d'entraînement (D), et budget computationnel (C). Découvertes par Kaplan et al. (2020) puis affinées par Hoffmann et al. (2022, "Chinchilla"), elles montrent que la performance suit une loi de puissance jusqu'à un point de rendement décroissant.

##### Analogie pédagogique

> *"Les scaling laws sont à l'entraînement des LLMs ce que la loi de Moore est aux processeurs : une prédiction fiable qui guide les investissements. Mais comme la loi de Moore, elle a ses limites. Chinchilla a découvert qu'on peut obtenir les mêmes performances avec un modèle plus petit entraîné sur plus de données — c'est le passage de 'toujours plus de paramètres' à 'la bonne proportion paramètres/données'."*

##### Explication détaillée

Les scaling laws reposent sur une observation empirique : la perte (loss) en entraînement décroît comme une loi de puissance de la forme `L ∝ N^(-α) + D^(-β) + C^(-γ)`. Concrètement :

1. **Kaplan et al. (2020)** — Les premiers à formaliser : doubler la taille du modèle améliore plus la performance que doubler les données. Résultat : tout le monde a entraîné des modèles toujours plus grands (GPT-3 : 175B, Gopher : 280B).
2. **Hoffmann et al. (2022, "Chinchilla")** — Contredisent Kaplan : pour un budget computationnel donné, il faut entraîner un modèle plus petit sur *beaucoup* plus de données. Chinchilla (70B, 1.4T tokens) surpasse Gopher (280B, 300B tokens) avec 4× moins de paramètres.
3. **Conséquence pratique** : en 2024-2026, la course aux paramètres s'arrête. On optimise l'efficacité (MoE, distillation) plutôt que la taille brute.

```
Représentation de la relation paramètres ↔ données :
                     
    Performance      │
        ▲           │   Zone sous-entraînée
        │           │     (trop de params,
        │           │      pas assez de data)
        │           │        ✗ GPT-3 (175B, 300B tokens)
        │           │
        │           │   Zone optimale (Chinchilla)
        │           │        ✓ Chinchilla (70B, 1.4T)
        │           │        ✓ Llama 3 (405B, 15T)
        │           │
        │           │   Zone sous-paramétrée
        │           │     (assez de data,
        │           │      pas assez de params)
        │           │
        └──────────────────────────────► Données
```

##### Pourquoi ce concept est crucial

- **Impact sur la conception :** les scaling laws déterminent le budget compute optimal pour entraîner un modèle. En tant que développeur d'agents, cela influence votre choix de modèle : un modèle plus petit mais bien entraîné peut être plus performant qu'un gros modèle mal entraîné.
- **Conséquence si ignoré :** gaspiller des ressources sur un modèle sur-dimensionné pour la tâche.
- **Cas d'usage :** choisir entre Qwen 2.5 Coder (7B) et DeepSeek V3 (671B) pour un agent de code — le premier, malgré sa taille, peut être plus pertinent pour des tâches spécifiques fine-tunées.

---

#### 1.2.2 Mixture of Experts (MoE) — Activer seulement ce qui est nécessaire

##### Définition formelle

> **Mixture of Experts :** architecture où le modèle est composé de nombreux sous-réseaux ("experts") spécialisés, chacun activé par un routeur (gate) qui détermine quels experts sont pertinents pour chaque token d'entrée. Seule une fraction des experts est activée à chaque pas (top-k routing), ce qui permet d'avoir un nombre total de paramètres très élevé tout en maintenant un coût d'inférence fixe et modéré.

##### Analogie pédagogique

> *"MoE est à un LLM dense ce qu'une équipe médicale est à un médecin généraliste. Le généraliste (modèle dense) doit tout savoir : cardiologie, dermatologie, neurologie. L'équipe médicale (MoE) a des spécialistes : le cardiologue ne voit que les cœurs, le dermatologue que la peau. Pour un patient avec une éruption cutanée, on active le dermatologue et on laisse le cardiologue dormir. Le routeur (gate) joue le rôle de l'infirmière d'accueil qui oriente le patient vers le bon spécialiste."*

##### Explication détaillée avec schéma

```
Architecture MoE (feed-forward) :

    Entrée (token)
         │
         ▼
    ┌─────────────┐
    │   Router    │ ← petit réseau qui décide quel(s) expert(s) activer
    │   (Gate)    │
    └──────┬──────┘
           │ top-2 routing : active les 2 experts les plus pertinents
           │
     ┌─────┴─────┐
     │           │
     ▼           ▼
  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐
  │Exp 1 │  │Exp 2 │  │Exp 3 │  │Exp 4 │  ...  ← N experts au total
  │(code)│  │(math)│  │(lang)│  │(vis) │        (ex: 256 experts)
  └──┬───┘  └──┬───┘  └──────┘  └──────┘
     │         │
     └────┬────┘
          │
          ▼
    Sortie combinée
    (pondérée par les poids du routeur)
```

**Étape par étape :**

1. Un token arrive dans une couche MoE.
2. Le routeur (un petit réseau de neurones) calcule un score de pertinence pour chacun des N experts.
3. Seuls les top-k experts (généralement k=1 ou k=2) sont activés ; les autres ne consomment aucune ressource.
4. La sortie est une combinaison pondérée des sorties des experts activés.
5. Le tout est différentiable : routeur et experts s'entraînent conjointement par rétropropagation.

**Exemples concrets (2026) :**
- **DeepSeek V3** : 671B paramètres totaux, mais seulement 37B activés par token (top-2 sur 256 experts).
- **Llama 4 Maverick** : architecture MoE avec experts spécialisés par domaine.
- **Gemini 2** : MoE propriétaire, spécialisé modalités (texte, image, audio).

##### Pourquoi ce concept est crucial

- **Impact sur la conception :** un agent qui utilise un modèle MoE peut avoir une latence d'inférence prévisible (le nombre d'experts activés est constant) même si la capacité totale du modèle est gigantesque. Idéal pour les systèmes temps réel.
- **Conséquence si ignoré :** choisir un modèle dense de taille équivalente coûterait 5 à 10× plus cher en inférence.
- **Cas d'usage :** assistant de code nécessitant une large connaissance (tous les langages, frameworks, bibliothèques) mais où chaque requête ne concerne qu'un sous-ensemble restreint — parfait pour MoE.

---

#### 1.2.3 Grouped Query Attention (GQA) — Le KV cache optimisé

##### Définition formelle

> **Grouped Query Attention :** variante de l'attention multi-têtes où les têtes de *query* (Q) sont regroupées et partagent les mêmes têtes de *key* (K) et *value* (V). Entre l'attention multi-têtes classique (une tête K/V par tête Q) et l'attention multi-query (une seule tête K/V pour toutes les têtes Q), GQA offre un compromis : G groupes de Q partagent K/V.

##### Analogie pédagogique

> *"Imaginez une bibliothèque avec 32 lecteurs (têtes query) qui veulent tous consulter des livres. En MHA classique, chaque lecteur a son propre bibliothécaire (tête key/value) — 32 bibliothécaires. En MQA, un seul bibliothécaire sert tout le monde — économique mais pas assez adapté. En GQA, on crée 8 groupes de 4 lecteurs, chaque groupe partageant un bibliothécaire. C'est le bon équilibre entre efficacité (moins de bibliothécaires = moins de mémoire) et expressivité (chaque groupe peut se spécialiser)."*

##### Explication détaillée avec schéma

```
Comparaison des architectures d'attention :

MHA (Multi-Head Attention) — Chaque tête Q a sa propre tête K/V
    Q₁ Q₂ Q₃ Q₄    ← 4 têtes query
    │  │  │  │
    K₁ K₂ K₃ K₄    ← 4 têtes key (mémoire = O(n²))
    V₁ V₂ V₃ V₄    ← 4 têtes value

MQA (Multi-Query Attention) — Une seule tête K/V pour toutes les Q
    Q₁ Q₂ Q₃ Q₄    ← 4 têtes query
    │  │  │  │
    K──┴──┴──┘     ← 1 tête key (mémoire réduite, mais perte d'expressivité)
    V─────────┘     ← 1 tête value

GQA (Grouped Query Attention) — G groupes K/V
    Q₁ Q₂│Q₃ Q₄    ← 2 groupes de 2 têtes query
    │  │ │  │
    K₁──┘ K₂──┘    ← 2 têtes key (bon compromis)
    V₁──── V₂────    ← 2 têtes value

    GQA avec G=2 : moitié moins de mémoire que MHA
    GQA avec G=1 : équivalent à MQA
    GQA avec G=H : équivalent à MHA (H = nombre de têtes)
```

**Pourquoi GQA est devenu le standard en 2025+ :**

- **Problème :** le KV cache (mémoire qui stocke les key/value de tous les tokens générés) croît linéairement avec la séquence. Pour une séquence de 1M tokens et 32 têtes d'attention, le KV cache peut occuper plusieurs Go de RAM GPU.
- **Solution GQA :** en réduisant le nombre de têtes K/V (typiquement G=H/4), on divise par 4 la mémoire du KV cache, ce qui permet des fenêtres de contexte beaucoup plus longues.
- **Adoption :** Llama 2/3/4, DeepSeek V2/V3, Gemma, Qwen 2.5 — tous utilisent GQA.

##### Pourquoi ce concept est crucial

- **Impact sur la conception :** GQA détermine la longueur de contexte réalisable. Si votre agent doit traiter des documents longs (codebases entières, livres, logs), GQA est ce qui rend cela possible sans mémoire GPU infinie.
- **Conséquence si ignoré :** un agent avec un modèle MHA classique sera limité à des contextes courts (4K-8K tokens) à moins d'avoir des ressources GPU massives.
- **Cas d'usage :** analyse de codebase entière (100K+ tokens) — GQA + long contexte permettent de charger tout le projet en une seule fois.

---

#### 1.2.4 Multi-Head Latent Attention (MLA) — La compression latente

##### Définition formelle

> **Multi-Head Latent Attention :** architecture d'attention introduite par DeepSeek (2024) qui compresse les têtes key et value dans un espace latent de plus faible dimension, puis les décompresse au moment du calcul de l'attention. MLA atteint une réduction drastique du KV cache (jusqu'à 93%) tout en maintenant la qualité de l'attention.

##### Analogie pédagogique

> *"MLA fonctionne comme la compression audio MP3 : on prend un fichier audio volumineux (WAV), on le comprime en perdant les fréquences inaudibles (MP3), et on peut le décompresser pour l'écouter. Les auditeurs n'entendent pas la différence. De même, MLA comprime les K/V dans un 'espace latent' — une représentation plus compacte — et les décompresse juste assez pour calculer l'attention. L'information importante est préservée, le volume mémoire est réduit."*

#####  MLA schéma

```
MLA — Attention Latente :
    
    Entrée du token
         │
         ▼
    ┌──────────┐
    │ Projection│ ← W_Q, W_K, W_V projectent dans l'espace latent
    │  Latente  │
    └────┬─────┘
         │
    ┌────▼────┐
    │ Vecteurs│ ← Représentation latente (comprimée)
    │ Latents │    ex: 128 dimensions au lieu de 4096
    └────┬────┘
         │
    ┌────▼────┐
    │Décompr. │ ← W_QK, W_UV décompressent pour le calcul d'attention
    └────┬────┘
         │
         ▼
    Calcul d'attention softmax(Q·K^T)·V

Comparaison KV cache (séquence de 1M tokens, 4096 dim.) :

    MHA classique : 1M × 4096 × 2 (K+V) × 4 bytes = 32 Go
    GQA (G=8)  : 1M × 512 × 2 (K+V) × 4 bytes  =  4 Go
    MLA        : 1M × 128 × 2 (K+V) × 4 bytes  =  1 Go

    MLA réduit le KV cache de ~97% par rapport à MHA !
```

**Étapes du mécanisme MLA :**

1. **Compression :** les vecteurs K et V sont projetés dans un espace latent de faible dimension via des matrices de projection apprises.
2. **Stockage :** seuls les vecteurs latents comprimés sont stockés dans le KV cache — c'est la clé de l'économie mémoire.
3. **Décompression :** avant le calcul de l'attention, les vecteurs latents sont projetés vers l'espace original via des matrices de décompression.
4. **Attention :** le produit scalaire Q·K^T est calculé dans l'espace décompressé.

##### Pourquoi ce concept est crucial

- **Impact sur la conception :** MLA permet des fenêtres de contexte massives (DeepSeek V2/V3 : 128K tokens avec un KV cache gérable) sans sacrifier la qualité de l'attention. C'est une rupture comparable au passage de RNN à transformeur en termes d'efficacité mémoire.
- **Conséquence si ignoré :** sans MLA (ou équivalent), les contextes très longs (1M+) sont irréalistes en production pour des raisons de coût GPU.
- **Cas d'usage :** analyse de codebases monolithiques, revue de documentation technique entière, traitement de logs système sur plusieurs jours.

---

### 1.3 L'émergence du comportement agentique

#### 1.3.1 Chain-of-Thought (CoT) — Raisonner pas à pas

##### Définition formelle

> **Chain-of-Thought :** technique de prompting (Wei et al., 2022) qui consiste à guider le LLM pour qu'il produise une séquence d'étapes de raisonnement intermédiaires avant de fournir la réponse finale. Le modèle ne prédit plus directement la sortie, mais une chaîne de déductions qui y mène.

##### Analogie pédagogique

> *"CoT est à un LLM ce que les 'étapes intermédiaires' sont à un problème de maths : montrer votre travail. Un élève qui écrit '1. Je calcule l'aire du rectangle : 5×3=15. 2. Je soustrais l'aire du triangle : 15-4=11. 3. Donc la réponse est 11' a plus de chances d'arriver à la bonne réponse que celui qui répond '11' directement. Le passage par les étapes intermédiaires force le raisonnement à être explicite et vérifiable."*

##### Exemple concret

**Prompt sans CoT :**
```
Q : Paul a 12 pommes. Il donne 3 à Léa et 2 à Tom, puis achète 5 pommes de plus.
Combien de pommes Paul a-t-il maintenant ?

R : 12
```

**Prompt avec CoT :**
```
Q : Paul a 12 pommes. Il donne 3 à Léa et 2 à Tom, puis achète 5 pommes de plus.
Combien de pommes Paul a-t-il maintenant ?

R : Paul commence avec 12 pommes. Il donne 3 à Léa → 12 - 3 = 9. Il donne 2 à Tom
→ 9 - 2 = 7. Il achète 5 pommes → 7 + 5 = 12. Donc Paul a 12 pommes.
```

La différence n'est pas la réponse finale, mais la *robustesse* : sur des problèmes complexes, CoT améliore significativement la précision (Wei et al. rapportent +15-20% sur des benchmarks de raisonnement arithmétique et symbolique).

##### Pourquoi ce concept est crucial pour les agents

- CoT est le socle de tous les mécanismes agentiques plus avancés (ReAct, planification, self-reflection).
- Sans raisonnement explicite, un agent ne peut pas justifier ses actions, ce qui rend le débogage et la confiance impossibles.

---

#### 1.3.2 ReAct — La boucle raisonnement + action + observation

##### Définition formelle

> **ReAct (Reasoning + Acting) :** paradigme agentique (Yao et al., 2023) où le LLM alterne entre des *thoughts* (raisonnements en langage naturel), des *actions* (invocations d'outils ou d'API), et des *observations* (résultats des actions). Cette boucle continue permet à l'agent de raisonner sur ce qu'il observe et d'ajuster ses actions en conséquence.

##### Analogie pédagogique

> *"ReAct est au LLM ce qu'un chercheur en laboratoire est à un livre de chimie. Le livre (LLM sans ReAct) contient toute la connaissance théorique, mais ne peut pas manipuler les éprouvettes. Le chercheur (ReAct) lit le protocole (thought), verse le réactif (action), observe la couleur (observation), et ajuste sa procédure (thought suivant). Sans cette boucle, le livre reste un livre ; avec elle, il devient un scientifique."*

##### Exemple concret : assistant qui vérifie la météo

```
Thought: L'utilisateur me demande s'il doit prendre un parapluie demain à Paris.
         Je dois d'abord obtenir la météo de Paris demain, puis en déduire
         une recommandation.

Action: get_weather(city="Paris", date="2026-05-19")
        ↑ appel d'outil (fonction)

Observation: {"temperature": "14°C", "precipitation": "90%", "condition": "pluie"}
             ↑ résultat structuré de l'API météo

Thought: Il y a 90% de précipitations. Je recommande un parapluie.

Action: send_message("Oui, il est fortement recommandé de prendre un parapluie
                     demain à Paris — 90% de chance de pluie.")
```

##### La boucle ReAct en schéma :

```
                     ┌──────────────────┐
                     │                  │
                     │   Prompt initial │
                     │   (mission)      │
                     │                  │
                     └────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
              ┌────▶│   THOUGHT         │
              │     │   (raisonnement)  │
              │     └────────┬──────────┘
              │              │
              │              ▼
              │     ┌───────────────────┐
              │     │   ACTION          │
              │     │   (appel outil)   │
              │     └────────┬──────────┘
              │              │
              │              ▼
              │     ┌───────────────────┐
              │     │  OBSERVATION      │
              │     │  (résultat outil) │
              │     └────────┬──────────┘
              │              │
              │      ┌───────┴───────┐
              │      │               │
              │    besoin          mission
              │    d'outil         accomplie
              │      │               │
              └──────┘               ▼
                              ┌──────────┐
                              │ Réponse  │
                              │ finale   │
                              └──────────┘
```

##### Pourquoi ce concept est crucial

- **Impact sur la conception :** ReAct est l'architecture de boucle agent la plus répandue en 2026. Tous les frameworks agentiques (LangGraph, CrewAI, opencode) l'implémentent avec des variantes.
- **Conséquence si ignoré :** un agent sans boucle ReAct ne peut pas utiliser d'outils de façon dynamique — il est limité à ce qu'il a appris pendant l'entraînement, sans accès à l'information actualisée.
- **Cas d'usage :** tout scénario où l'agent doit interagir avec des systèmes externes (API, base de données, système de fichiers, navigateur web).

---

#### 1.3.3 Tool use natif — L'agent outillé

##### Définition formelle

> **Tool use natif :** capacité intégrée d'un LLM à déclarer des appels de fonctions structurés dans sa sortie. Plutôt que de générer du texte libre, le modèle peut produire un objet JSON décrivant un appel d'outil (nom de la fonction + paramètres). Le runtime exécute l'outil et retourne le résultat au modèle. Depuis 2024-2025, cette capacité est entraînée directement dans les poids du modèle, et non plus simplement promptée.

##### Analogie pédagogique

> *"Tool use natif est à un LLM ce que les réflexes sont à un humain : quand on vous lance une balle, vous tendez la main sans réfléchir. Le geste est intégré, pas besoin de vous répéter la procédure chaque fois. De même, un modèle avec tool use natif n'a pas besoin qu'on lui explique le format JSON d'appel de fonction à chaque requête — c'est encodé dans ses poids, comme un réflexe."*

##### Exemple technico-pédagogique (format JSON)

Le modèle génère directement ce type de sortie :

```json
{
  "tool_call": {
    "name": "search_web",
    "arguments": {
      "query": "météo Paris 19 mai 2026",
      "max_results": 3
    }
  }
}
```

Le système exécute `search_web("météo Paris 19 mai 2026", 3)`, obtient le résultat, et le repasse au modèle comme observation.

**Différence avec l'approche promptée (2023) :**
- *Promptée :* le modèle doit générer du texte comme `[SEARCH: météo Paris]` qu'un parser extrait — fragile, erreurs de format, tokens gaspillés.
- *Native :* le modèle appelle directement une fonction via une API structurée dans ses poids — fiable, efficace, validé par l'entraînement.

##### Pourquoi ce concept est crucial

- **Impact sur la conception :** le tool calling natif détermine l'architecture de votre agent. Un modèle sans cette capacité nécessite une couche de parsing supplémentaire ; un modèle avec permet des boucles agent plus robustes.
- **Conséquence si ignoré :** utiliser un modèle sans tool calling natif pour un agent complexe, c'est construire une maison sur du sable — le parsing des appels d'outil sera la principale source d'erreurs.
- **Cas d'usage :** tout agent qui interagit avec le monde extérieur (API, web, base de données).

---

#### 1.3.4 Planification — Décomposer pour régner

##### Définition formelle

> **Planification dans les LLMs :** capacité d'un agent à décomposer une mission complexe en sous-objectifs hiérarchisés, à ordonnancer les étapes, et à ajuster le plan en fonction des résultats intermédiaires. Contrairement à une simple séquence ReAct (qui réagit à chaque observation), la planification implique une anticipation et une structure intentionnelle.

##### Analogie pédagogique

> *"La différence entre ReAct et la planification, c'est la différence entre un touriste qui sort de l'hôtel et décide où aller à chaque coin de rue, et un voyageur qui étudie la carte, note les monuments à voir, et prépare un itinéraire optimisé. Le touriste (ReAct) peut être flexible mais risque de tourner en rond. Le voyageur (planification) a une vision d'ensemble mais peut être trop rigide. Les meilleurs agents combinent les deux : un plan général qui s'adapte."*

##### Exemple concret

**Mission :** "Analyse la codebase, trouve les bugs de sécurité, et rédige un rapport."

**Étape 1 — Décomposition :**
```
Plan initial :
  Phase 1: Exploration
    - Lister tous les fichiers Python
    - Identifier les dépendances (requirements.txt, imports)
  Phase 2: Analyse statique
    - Chercher les patterns de vulnérabilité (grep SQL injection, XSS)
    - Vérifier les permissions (chmod, sudo dans le code)
  Phase 3: Exécution contrôlée
    - Lancer un linter de sécurité (bandit)
    - Exécuter des tests ciblés
  Phase 4: Synthèse
    - Prioriser les vulnérabilités (critique/important/mineur)
    - Rédiger le rapport
```

**Étape 2 — Ajustement :** Si la Phase 1 révèle qu'il n'y a que 2 fichiers Python, l'agent saute les phases gourmandes et adapte la profondeur de l'analyse.

##### Pourquoi ce concept est crucial

- **Impact sur la conception :** la planification transforme un agent réactif en agent proactif. Elle permet de gérer des missions qui nécessitent des dizaines d'étapes sans dérive (error propagation).
- **Conséquence si ignoré :** sans planification, un agent ReAct peut entrer dans des boucles infinies ou oublier l'objectif principal après quelques itérations.
- **Cas d'usage :** développement logiciel (analyser → modifier → tester → valider), recherche d'information multi-sources, audit de code.

---

#### 1.3.5 Self-reflection — L'agent critique de lui-même

##### Définition formelle

> **Self-reflection :** mécanisme par lequel un agent LLM examine et évalue ses propres sorties (code, texte, plan) pour détecter des erreurs, des incohérences ou des améliorations possibles, avant de les soumettre comme résultat final. C'est une forme de *critique auto-générée* qui peut être utilisée en simple passe ou en boucle d'amélioration itérative.

##### Analogie pédagogique

> *"Self-reflection, c'est l'équivalent d'un relecteur qui vérifie son propre texte avant de l'envoyer — mais pour l'agent, le 'relecteur' et le 'rédacteur' sont le même modèle. C'est comme si vous écriviez une lettre, puis changiez de casquette pour la relire d'un œil critique : 'Est-ce que ce paragraphe est clair ? Est-ce que cet argument se tient ?' L'agent fait ce changement de perspective de façon systématique."*

##### Exemple concret : agent de code

```
Génération initiale :
  def tri_bulles(liste):
      for i in range(len(liste)):
          for j in range(len(liste)-1):
              if liste[j] > liste[j+1]:
                  liste[j], liste[j+1] = liste[j+1], liste[j]
      return liste

Self-reflection :
  Critique: "L'implémentation est correcte mais pas optimale :
  1. La boucle externe peut être réduite à len(liste)-1 itérations
     car le plus grand élément remonte déjà à la fin.
  2. On peut ajouter un drapeau 'swapped' pour sortir
     prématurément si le tableau est déjà trié."

Amélioration :
  def tri_bulles_optimise(liste):
      n = len(liste)
      for i in range(n-1):
          swapped = False
          for j in range(n-1-i):
              if liste[j] > liste[j+1]:
                  liste[j], liste[j+1] = liste[j+1], liste[j]
                  swapped = True
          if not swapped:
              break
      return liste
```

##### Pourquoi ce concept est crucial

- **Impact sur la conception :** la self-reflection permet d'obtenir des résultats de meilleure qualité sans modèle plus grand — c'est un *compute-time* plutôt qu'un *model-size* trade-off. Particulièrement utile pour les tâches où la précision est critique (code, analyse légale, diagnostic).
- **Conséquence si ignoré :** un agent sans auto-critique peut livrer des résultats incorrects avec une confiance inébranlable (hallucination non détectée).
- **Cas d'usage :** révision de code, génération de rapports, traduction, tout domaine où une erreur a un coût élevé.

---

### 1.4 Écosystème 2026 — Modèles frontier et open-source

#### Définition

> **Écosystème 2026 des LLMs :** paysage des modèles de langage disponibles, classés en deux catégories — *frontier* (modèles propriétaires accessibles via API, à la pointe de la performance) et *open-source* (poids publiés, exécutables localement, généralement moins performants mais gratuits et auditable).

#### Analogie pédagogique

> *"L'écosystème 2026 ressemble au marché de l'automobile : les modèles frontier (API) sont les berlines de luxe — chères, puissantes, tout confort, mais vous ne pouvez pas les réparer vous-même. Les modèles open-source sont les voitures populaires — moins tape-à-l'œil, parfois moins rapides, mais vous ouvrez le capot, vous bricolez, et vous ne payez pas de garage (inférence locale). Selon votre usage — course de F1 (production sensible) ou balade du dimanche (prototypage) — le bon choix diffère."*

#### Tableau comparatif des modèles frontier

| Modèle | Créateur | Architecture | Fenêtre contexte | Points forts | Coût estimé (entrée/sortie pour 1M tokens) |
|--------|----------|-------------|-----------------|--------------|-------------------------------------------|
| Claude Opus 4.5 / Mythos | Anthropic | Transformer dense + reasoning natif | 200K tokens | SWE-bench #1, tool use fiable, sécurité | ~$15/$75 |
| GPT-5 / Codex | OpenAI | MoE propriétaire | 256K tokens | Multimodalité, raisonnement mathématique, API riche | ~$10/$40 |
| Gemini 3 Pro | Google | MoE propriétaire | 2M tokens | Contexte géant, multimodal natif, intégration Google | ~$5/$20 |
| Kimi K2 | Moonshot | MoE + MLA | 512K tokens | Code, long contexte, coût compétitif | ~$3/$12 |

**Explication des colonnes :**
- **Architecture :** dense (tous les paramètres activés) ou MoE (sous-ensemble seulement). Le type d'attention (MHA, GQA, MLA) n'est pas toujours divulgué par les propriétaires.
- **Fenêtre contexte :** nombre maximal de tokens que le modèle peut traiter en une seule fois. Crucial pour les tâches agentiques qui nécessitent de charger des documents longs.
- **Points forts :** domaines où le modèle excelle selon les benchmarks publics. "SWE-bench" est le standard pour les agents de code ; "tool use fiable" signifie que le modèle génère des appels d'outil valides et pertinents de façon consistante.
- **Coût estimé :** prix public par million de tokens en entrée (le prompt) et en sortie (la génération). Les agents consomment beaucoup en sortie (génération de code, raisonnements longs).

#### Tableau comparatif des modèles open-source

| Modèle | Créateur | Architecture | Paramètres (total/actif) | Fenêtre | Points forts |
|--------|----------|-------------|------------------------|---------|--------------|
| Llama 4 Scout | Meta | MoE | 109B/17B | 10M tokens | Contexte record, licence ouverte, bon équilibre |
| Llama 4 Maverick | Meta | MoE | 402B/97B | 1M tokens | Performance proche frontier (Maverick) |
| Qwen 2.5 Coder | Alibaba | Transformer dense | 7B, 14B, 32B | 128K tokens | Meilleur code open-source 2025-26, plusieurs tailles |
| DeepSeek V3.2 | DeepSeek | MoE + MLA | 671B/37B | 128K tokens | Niveau frontier en code/math, complètement ouvert |
| Gemma 4 | Google | Transformer dense | 7B, 27B | 256K tokens | Vision native, tool calling intégré, petit format |
| GLM-4.7-Flash | Zhipu | MoE optimisé | ~100B/~20B | 256K tokens | Optimisé pour les boucles agent (latence faible) |

**Explication :**
- **Paramètres (total/actif) :** pour l'architecture MoE, distinction entre la capacité totale (taille du cerveau complet) et les paramètres activés par token (effort par pensée). Un ratio de ×10 à ×20 est typique.
- **Fenêtre :** longueur de contexte maximale. Les modèles open-source ont fait un bond spectaculaire (Llama 4 Scout : 10M tokens).
- **Points forts :** "Licence ouverte" signifie qu'on peut utiliser, modifier, redistribuer — important pour les projets commerciaux.

---

### 1.5 Le gap frontier vs open-source — Analyse

#### Définition

> **Gap frontier vs open-source :** écart mesurable de performance, de fiabilité et de fonctionnalités entre les meilleurs modèles propriétaires (Claude, GPT, Gemini) et les meilleurs modèles ouverts (Llama, DeepSeek, Qwen). En 2026, cet écart s'est considérablement réduit par rapport à 2024, mais il persiste sur des métriques spécifiques.

#### Analyse des écarts

**1. Performance sur SWE-bench Verified (2026) :**

```
Performance sur les tâches de génie logiciel :

Claude Mythos    ───▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 93.9%
GPT-5 Codex      ───▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  88.2%
DeepSeek V3.2    ───▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓   82.1%
Llama 4 Maverick ───▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓        68.4%
Qwen 2.5 Coder   ───▓▓▓▓▓▓▓▓▓▓▓▓▓          57.3%
Llama 4 Scout    ───▓▓▓▓▓▓▓▓▓▓▓▓            50.1%
GLM-4.7-Flash    ───▓▓▓▓▓▓▓▓▓▓▓▓            50.0%

                0%    20%    40%    60%    80%   100%
```

Analyse : le gap entre Claude (93.9%) et Llama 4 Scout (50.1%) est de 43 points. Mais DeepSeek V3.2 (82.1%) n'est qu'à 12 points de Claude — les modèles open-source haut de gamme rattrapent rapidement leur retard, en particulier sur les tâches de code.

**2. Coût par run (estimation pour une tâche type : générer une fonction Python de 50 lignes avec tests) :**

| Solution | Coût estimé | Temps (inférence locale) | Notes |
|----------|------------|------------------------|-------|
| Claude API | $0.15-0.75 | ~3-5s | Pay-per-token |
| GPT-5 API | $0.10-0.40 | ~2-4s | Pay-per-token |
| DeepSeek V3.2 local | ~$0 | ~15-30s (GPU A100) | Nécessite GPU puissant |
| Llama 4 Scout local | ~$0 | ~10-20s (GPU A100) | Moins de paramètres actifs |
| Qwen 2.5 Coder 7B local | ~$0 | ~1-2s (GPU grand public) | Rapide, moins capable |

**3. Cas d'usage typiques :**

| Scénario | Recommandation | Justification |
|----------|---------------|---------------|
| Production, tâche critique (ex: diagnostic médical, code financier) | Modèle frontier (Claude Mythos) | Fiabilité maximale, hallucinations minimisées |
| Production, coût modéré (ex: chatbot support client) | Frontier ou open-source haut de gamme (DeepSeek V3.2) selon contrainte budget |
| Prototypage / R&D (ex: exploration de concept, test de boucle agent) | Open-source local (Qwen, Llama Scout) | Gratuit, itérations rapides, pas de dépendance API |
| Privacy sensible (ex: code propriétaire, données médicales) | Open-source local obligatoire | Données jamais transmises à un tiers |
| Équipement modeste (GPU ≤ 16Go) | Petit modèle open-source (Qwen 2.5 Coder 7B, Gemma 4 7B) | Tient sur GPU grand public |
| Volume massif (milliards de requêtes/jour) | Frontier optimisé coût (Gemini 3 Pro) | Le coût unitaire le plus bas compense le volume |

#### Pourquoi cette analyse est cruciale

- **Impact sur la conception :** le choix du modèle détermine toute l'architecture de votre agent : boucle de raisonnement, gestion des erreurs, budget, latence.
- **Conséquence si ignoré :** un mauvais choix de modèle peut rendre votre agent inutilisable (trop cher, trop lent, trop peu fiable) ou vous exposer à des risques (fuite de données vers une API externe).
- **Cas d'usage typique :** un logiciel de révision de code pour une entreprise — l'agent doit lire le code en local pour des raisons de confidentialité → pas de frontier API → DeepSeek V3.2 ou Llama 4 en local.

---

## Synthèse

### Ce que vous avez appris dans cette séance

| Concept | Résumé | Section |
|---------|--------|---------|
| Timeline 2017→2026 | Évolution du transformeur au modèle agentique natif, en passant par les scaling laws, MoE et le reasoning | 1.1 |
| Mixture of Experts (MoE) | Architecture où seuls les sous-réseaux pertinents sont activés par token, permettant des modèles massifs à coût d'inférence fixe | 1.2 |
| Grouped Query Attention (GQA) | Optimisation du KV cache par partage de têtes K/V entre groupes de têtes Q — standard 2025+ | 1.2 |
| Multi-Head Latent Attention (MLA) | Compression latente des K/V réduisant la mémoire de >90%, ouvrant la voie aux contextes massifs | 1.2 |
| Chain-of-Thought (CoT) | Raisonnement pas à pas qui améliore la précision sur les tâches complexes | 1.3 |
| ReAct | Boucle Raisonnement → Action → Observation qui transforme le LLM en agent dynamique | 1.3 |
| Tool use natif | Capacité intégrée du modèle à déclarer des appels de fonction structurés — réflexe agentique | 1.3 |
| Planification | Décomposition de missions complexes en sous-objectifs avec ajustement dynamique | 1.3 |
| Self-reflection | Auto-critique des sorties du modèle pour détecter et corriger les erreurs | 1.3 |
| Écosystème 2026 | Paysage des modèles frontier (API) et open-source (locaux) avec leurs forces et faiblesses | 1.4 |
| Gap frontier / open-source | Écart mesurable de performance, coût et fiabilité ; choix dépendant du cas d'usage | 1.5 |

### Lien avec la séance suivante

> *"Maintenant que vous comprenez comment les LLMs modernes sont architecturés (MoE, GQA, MLA) et comment le comportement agentique émerge (CoT, ReAct, planification), la séance 2 — Context Window Engineering — vous apprendra à maîtriser la *mémoire de travail* de l'agent. Vous découvrirez comment optimiser l'utilisation de la fenêtre de contexte (dont la taille est rendue possible par GQA et MLA), comment structurer les informations pour qu'elles soient efficacement récupérées par l'attention, et comment concevoir des stratégies de repérage et de priorisation. En somme : la séance 1 vous a donné la voiture, la séance 2 vous apprendra à conduire."*

---

## Travaux Pratiques — Exploration des architectures LLM

> **Projet fil rouge :** Cette séance pose les fondations pour comprendre les choix architecturaux de votre AI Developer Assistant.

**Objectif :** Visualiser et comprendre les tokens, explorer les architectures MoE, et configurer votre premier agent opencode.
**Durée :** 45 minutes

---

### Énoncé

1. Installer et utiliser `tiktoken` pour visualiser la tokenisation
2. Comparer le nombre de tokens entre différentes formulations
3. Configurer votre premier agent opencode avec `big-pickle`
4. Tester un prompt agentique (ReAct) avec opencode

**Fichiers à créer :**
- `seance-01/tokenizer_exploration.py` — Script d'exploration de la tokenisation
- `seance-01/test_tokenizer.py` — Tests unitaires

---

### Corrigé pas à pas

#### Étape 1 : Créer le dossier du TP

**Point de départ :** ouvrez un terminal dans votre dossier d'exercices.

```bash
mkdir -p ~/agentic-labs/seance-01
cd ~/agentic-labs/seance-01
pwd
```

> **Résultat attendu :** `pwd` affiche un chemin se terminant par `seance-01`.

#### Étape 2 : Créer le script d'exploration

##### Où créer le fichier ?

```
seance-01/
└── tokenizer_exploration.py    ← à créer maintenant
```

```python
"""Exploration de la tokenisation avec tiktoken.

Ce script permet de visualiser comment un texte est découpé en tokens
par le modèle GPT-4. Comprendre la tokenisation est essentiel pour :
- Estimer les coûts d'API (facturation au token)
- Optimiser les prompts (éviter le gaspillage de tokens)
- Comprendre les limites de la fenêtre de contexte
"""

import tiktoken


def compter_tokens(texte: str, modele: str = "gpt-4") -> int:
    """Compte le nombre de tokens dans un texte.

    Args:
        texte: Le texte à analyser
        modele: Le modèle de tokenisation (gpt-4, gpt-3.5-turbo, etc.)

    Returns:
        Le nombre de tokens dans le texte
    """
    # Charger le codec de tokenisation pour le modèle spécifié
    encodage = tiktoken.encoding_for_model(modele)

    # Encoder le texte en tokens
    tokens = encodage.encode(texte)

    return len(tokens)


def visualiser_tokens(texte: str, modele: str = "gpt-4") -> None:
    """Affiche les tokens individuels d'un texte.

    Cette fonction montre comment le texte est découpé,
    ce qui aide à comprendre pourquoi certains textes
    consomment plus de tokens que d'autres.
    """
    encodage = tiktoken.encoding_for_model(modele)
    tokens = encodage.encode(texte)

    print(f"Texte original : {texte}")
    print(f"Nombre de tokens : {len(tokens)}")
    print("\nTokens individuels :")

    for i, token in enumerate(tokens):
        # Décoder chaque token pour voir son contenu
        texte_token = encodage.decode([token])
        print(f"  [{i}] {token} → '{texte_token}'")


def comparer_prompts() -> None:
    """Compare différents styles de prompts en termes de tokens.

    Cette comparaison montre que la formulation d'un prompt
    impacte directement sa consommation de tokens.
    """
    prompts = {
        "Simple": "Qu'est-ce que l'IA ?",
        "Détaillé": "Explique le concept d'intelligence artificielle en 3 phrases.",
        "Technique": "Définis l'IA comme un système capable de percevoir son environnement et d'agir pour atteindre des objectifs.",
        "Avec contexte": "Tu es un expert en IA. Un étudiant en Master 2 te demande : qu'est-ce que l'IA agentique ? Réponds en mentionnant les LLMs et les architectures modernes.",
    }

    print("=== Comparaison des prompts ===\n")

    for nom, prompt in prompts.items():
        nb_tokens = compter_tokens(prompt)
        print(f"{nom} :")
        print(f"  Texte : {prompt[:60]}...")
        print(f"  Tokens : {nb_tokens}")
        print()


if __name__ == "__main__":
    # Exemple 1 : Visualiser les tokens d'un texte simple
    print("=== Visualisation des tokens ===\n")
    visualiser_tokens("L'intelligence artificielle agentique est fascinante !")

    print("\n" + "="*50 + "\n")

    # Exemple 2 : Comparer différents prompts
    comparer_prompts()
```

##### Exécuter le fichier

```bash
python3 tokenizer_exploration.py
```

##### Résultat attendu

```text
=== Visualisation des tokens ===

Texte original : L'intelligence artificielle agentique est fascinante !
Nombre de tokens : 9

Tokens individuels :
  [0] 43 → 'L'
  [1] 3604 → "'intelligence"
  [2] 13679 → ' artificielle'
  ...

=== Comparaison des prompts ===

Simple :
  Texte : Qu'est-ce que l'IA ?...
  Tokens : 8

Détaillé :
  Texte : Explique le concept d'intelligence artificielle en 3 phrases....
  Tokens : 12
...
```

#### Étape 3 : Créer les tests

##### Où créer le fichier ?

```
seance-01/
├── tokenizer_exploration.py
└── test_tokenizer.py    ← à créer maintenant
```

```python
"""Tests pour le script de tokenisation."""

from tokenizer_exploration import compter_tokens


def test_compter_tokens_simple():
    """Test avec un texte simple."""
    texte = "Bonjour le monde"
    nb_tokens = compter_tokens(texte)
    assert nb_tokens > 0
    assert nb_tokens < 10  # Un texte court doit avoir peu de tokens


def test_compter_tokens_vide():
    """Test avec un texte vide."""
    texte = ""
    nb_tokens = compter_tokens(texte)
    assert nb_tokens == 0


def test_compter_tokens_long():
    """Test avec un texte plus long."""
    texte = "L'intelligence artificielle " * 100
    nb_tokens = compter_tokens(texte)
    assert nb_tokens > 100  # Doit avoir beaucoup de tokens
```

##### Exécuter les tests

```bash
python3 -m pytest test_tokenizer.py -v
```

##### Résultat attendu

```text
============================= test session starts ==============================
collected 3 items

test_tokenizer.py::test_compter_tokens_simple PASSED                     [ 33%]
test_tokenizer.py::test_compter_tokens_vide PASSED                       [ 66%]
test_tokenizer.py::test_compter_tokens_long PASSED                       [100%]

============================== 3 passed in 0.12s ===============================
```

---

### Validation

- [ ] `python3 tokenizer_exploration.py` s'exécute sans erreur
- [ ] Le script affiche le nombre de tokens pour différents textes
- [ ] `python3 -m pytest test_tokenizer.py -v` affiche 3 tests passés
- [ ] Vous pouvez expliquer pourquoi "IA" et "intelligence artificielle" n'ont pas le même nombre de tokens
- [ ] Vous comprenez l'impact de la tokenisation sur les coûts et les limites de contexte

---

## Points clés à retenir

1. **Timeline 2017→2026** : Les LLMs sont passés de générateurs de texte à systèmes agentiques grâce aux innovations architecturales (MoE, GQA, MLA) et algorithmiques (CoT, ReAct, tool use).
2. **Mixture of Experts (MoE)** : Architecture où seuls les sous-réseaux pertinents sont activés, permettant des modèles massifs à coût d'inférence fixe.
3. **Comportements agentiques** : Chain-of-Thought, ReAct, tool use et planification transforment le LLM en agent dynamique capable de raisonner et d'agir.
4. **Gap frontier/open-source** : Le choix du modèle dépend du cas d'usage : performance (frontier) vs coût/confidentialité (open-source).

---

## Liens

- [Séance 2 — Context Window Engineering](./02-context-window-engineering.md)

---

## Références contextualisées

- **Vaswani et al., "Attention Is All You Need" (2017)**
  *Contexte :* Papier fondateur qui introduit l'architecture transformeur — le socle de TOUS les LLMs modernes. Cité dans la section 1.1 (timeline) et comme prérequis.
  *Niveau de lecture :* avancé (nécessite des bases en deep learning séquence-à-séquence)
  *→ https://arxiv.org/abs/1706.03762*

- **Kaplan et al., "Scaling Laws for Neural Language Models" (2020)**
  *Contexte :* Premier papier à formaliser les lois de puissance reliant performance, taille du modèle et données. Cité dans la section 1.2.1 (Scaling Laws) pour expliquer la logique derrière la course à la taille des modèles.
  *Niveau de lecture :* avancé (analyse mathématique de régressions)
  *→ https://arxiv.org/abs/2001.08361*

- **Hoffmann et al., "Training Compute-Optimal Large Language Models" (2022) — Chinchilla**
  *Contexte :* Correction des scaling laws de Kaplan : pour un budget compute fixe, mieux vaut un modèle plus petit avec plus de données. Cité en 1.2.1 car c'est la référence pratique pour tout entraînement de LLM depuis 2023.
  *Niveau de lecture :* avancé
  *→ https://arxiv.org/abs/2203.15556*

- **Wei et al., "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models" (2022)**
  *Contexte :* Introduit le raisonnement pas à pas (CoT). Cité en 1.3.1 comme mécanisme fondateur du comportement agentique. Essentiel pour comprendre ReAct et la planification.
  *Niveau de lecture :* intro (concept simple, brillamment exposé)
  *→ https://arxiv.org/abs/2201.11903*

- **Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models" (2023)**
  *Contexte :* Introduit la boucle Raisonnement + Action + Observation. Cité en 1.3.2 comme architecture centrale de tous les agents LLM modernes. Fondamental pour la suite du cours (séances 4, 6, 7, 8).
  *Niveau de lecture :* intro (très pédagogique, avec exemples concrets)
  *→ https://arxiv.org/abs/2210.03629*

- **DeepSeek-AI, "DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts" (2024)**
  *Contexte :* Présente MLA (Multi-Head Latent Attention) et une architecture MoE efficace. Cité en 1.2.4 comme référence majeure pour l'optimisation du KV cache et l'inférence économique.
  *Niveau de lecture :* avancé (détail des formules d'attention)
  *→ https://arxiv.org/abs/2405.04434*

- **Shazeer, "Fast Transformer Decoding: One Write-Head is All You Need" (2019)**
  *Contexte :* Introduit la Multi-Query Attention (MQA), précurseur de GQA. Cité en 1.2.3 comme base historique pour comprendre l'évolution vers GQA et MLA.
  *Niveau de lecture :* avancé
  *→ https://arxiv.org/abs/1911.02150*

- **Ainslie et al., "GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints" (2023)**
  *Contexte :* Formalise GQA comme compromis optimal entre MHA et MQA. Cité en 1.2.3 comme standard d'architecture 2025+.
  *Niveau de lecture :* avancé
  *→ https://arxiv.org/abs/2305.13245*

- **Wang et al., "Plan-and-Solve Prompting" (2023)**
  *Contexte :* Extension de CoT qui intègre explicitement la décomposition en plan. Cité en 1.3.4 comme pont entre CoT et planification agentique.
  *Niveau de lecture :* intro
  *→ https://arxiv.org/abs/2305.04091*

- **Shinn et al., "Reflexion: An Autonomous Agent with Dynamic Memory and Self-Reflection" (2023)**
  *Contexte :* Introduit la self-reflection comme mécanisme agentique. Cité en 1.3.5 comme cadre de référence pour l'auto-critique des agents.
  *Niveau de lecture :* intro
  *→ https://arxiv.org/abs/2303.11366*

- **Rapport d'analyse SWE-bench 2026 (sources multiples)**
  *Contexte :* Benchmarks standardisés pour agents de code. Cité en 1.5 comme métrique de comparaison frontier vs open-source.
  *Niveau de lecture :* intro (les chiffres parlent d'eux-mêmes)
  *→ https://www.swebench.com/*
