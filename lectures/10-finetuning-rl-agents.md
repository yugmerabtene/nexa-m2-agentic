# Séance 10 — Fine-tuning & RL pour Agents

## Introduction théorique

**Quel est le problème ?** Les modèles de base, même les plus performants, sont entraînés sur un vaste corpus textuel généraliste. Ils excellent dans la compréhension du langage naturel et la génération de texte, mais ils ne sont pas optimisés pour les tâches agentiques spécifiques : appeler des outils avec une syntaxe précise, suivre un plan d'action sur plusieurs tours, respecter des formats de réponse stricts. Un agent qui formate mal un appel d'outil casse le pipeline ; un agent qui ignore le format ReAct attendu ne peut pas être parsé ; un agent qui boucle sur la même action gaspille des ressources. Le fine-tuning avec renforcement (RL) sur des environnements agentiques permet de combler ce fossé en exposant le modèle à des situations réelles d'interaction.

**Contexte 2026 :** Trois approches dominent le paysage du fine-tuning agentique. **ATLAS** (Reinforcement Finetuning for Tool Spaces) propose une méthode combinant SFT et RL pour apprendre à un modèle à utiliser des outils. **GRPO** (Group Relative Policy Optimization) est devenu l'algorithme RL de référence car il évite le coût d'un modèle critique séparé. **SWE-smith** applique ces principes au domaine du software engineering avec des récompenses programmatiques. Les gains sur SWE-bench Verified atteignent +29% après fine-tuning RL, portant les meilleurs modèles de 49% à 78% de résolution.

**Lien avec les séances précédentes et suivantes :** La séance 9 (Agentic RAG) a montré comment un agent enrichit ses connaissances par récupération contextuelle. Mais connaître ne suffit pas : l'agent doit aussi apprendre à agir avec précision. Cette séance 10 passe de la récupération passive à l'action optimisée par renforcement. La séance 11 (Optimisation mémoire et contexte) montrera comment appliquer ces techniques RL pour produire des modèles plus petits et plus efficaces en mémoire, en utilisant les principes de GRPO et curriculum learning.

## Objectifs pédagogiques

À l'issue de cette séance, vous serez capable de :

1. **Analyser** les limitations des modèles de base pour les tâches agentiques et décider, selon cinq critères, quand un fine-tuning RL est nécessaire
2. **Concevoir** une boucle de reinforcement finetuning avec ATLAS incluant SFT, exploration RL, et fonction de récompense multi-critères
3. **Implémenter** une grille d'évaluation rubric-based RL avec pondération dynamique des critères (tool correctness, format, complétion, efficacité)
4. **Expliquer** le principe de GRPO, sa différence avec PPO (absence de modèle critique, normalisation par groupe), et l'appliquer à un cas concret
5. **Construire** un pipeline complet de fine-tuning RL : préparation des données ReAct → environnement d'interaction → boucle d'entraînement GRPO → évaluation sur benchmark

## Plan détaillé

### 10.1 Pourquoi fine-tuner pour les tâches agentiques

#### Définition

> **Fine-tuning agentique :** processus d'adaptation d'un modèle de langage pré-entraîné à des tâches spécifiques d'interaction avec un environnement (appels d'outils, planification, respect de formats) par apprentissage supervisé puis par renforcement.

#### Analogie

> *"Un modèle de base est comme un étudiant brillant qui a lu tous les manuels mais n'a jamais passé d'examen pratique. Le fine-tuning RL, c'est l'entraînement aux examens blancs avec correction : il apprend non seulement la théorie, mais aussi la stratégie d'exécution."*

#### Analyse des gaps des modèles de base

Un modèle générique présente cinq limitations structurelles pour les tâches agentiques :

1. **Tool calling mal formaté** — le modèle oublie des paramètres, inverse l'ordre des arguments, ou produit du JSON invalide. Un outil qui attend `{"query": "..."}` reçoit `{"q": "..."}`.
2. **Format de réponse non respecté** — le modèle s'écarte du schéma ReAct ou JSON attendu, ce qui casse le parsing. Exemple : il répond en texte libre au lieu du format `Action: ...\nAction Input: ...`.
3. **Raisonnement multi-tour incohérent** — le modèle planifie une action (Thought) mais en exécute une autre (Action), ou boucle infiniment sur le même outil sans progresser.
4. **Connaissance du domaine absente** — le modèle ignore la syntaxe spécifique d'une API, les conventions d'un framework, ou la structure d'un codebase existant.
5. **Latence et coût élevés** — le modèle nécessite des prompts longs incluant la liste complète des outils, leurs descriptions et des exemples d'utilisation. Un modèle fine-tuné peut fonctionner avec un prompt minimal.

#### Gains observés

| Modèle | Avant RL | Après RL | Delta |
|--------|----------|----------|-------|
| opencode/big-pickle | 38.2% | 67.8% | +29.6% |
| Modèle générique 7B | 22.1% | 51.4% | +29.3% |
| Modèle générique 70B | 49.6% | 78.4% | +28.8% |

### 10.2 ATLAS : Reinforcement Finetuning pour tool spaces

#### Définition

> **ATLAS** (Agent Training with Language-model Alignment Scores) : méthode hybride qui combine fine-tuning supervisé (SFT) sur des démonstrations de tool use, puis reinforcement learning sur un environnement d'outils, avec un scoring d'alignement pour la sécurité et le format.

#### Principe expliqué

ATLAS procède en trois phases :

**Phase 1 — SFT (Supervised Fine-Tuning) :** Le modèle apprend par imitation sur des trajectoires démonstrées. Chaque exemple est une paire (instruction utilisateur → séquence d'appels d'outils optimale). Le modèle apprend à reproduire le schéma : Thought → Action → Action Input → Observation → Thought...

**Phase 2 — RL (Reinforcement Learning) :** Le modèle explore l'environnement par ses propres moyens. Il génère des trajectoires, certaines bonnes, d'autres mauvaises. Une fonction de récompense évalue chaque trajectoire. GRPO met à jour le modèle pour favoriser les trajectoires les plus récompensées.

**Phase 3 — Alignment :** Un scoring secondaire pénalise les formats dangereux ou non conformes. Par exemple : une action qui exécute une commande shell `rm -rf /` reçoit une récompense négative même si la tâche est réussie.

#### Schéma ASCII — Boucle RL complète

```
                            ┌─────────────────────────────┐
                            │       ENVIRONNEMENT         │
                            │     (Tool Space)            │
                            │                              │
                            │  ┌──────┐  ┌──────┐  ┌───┐  │
                            │  │search│  │write │  │...│  │
                            │  └──────┘  └──────┘  └───┘  │
                            └────────────┬────────────────┘
                                         │ observation
                                         │ (résultat outil)
                                         ▼
        ┌─────────────────────────────────────────────────────┐
        │                    AGENT (LLM)                       │
        │                                                     │
        │  état actuel + historique → Thinking → Action choice │
        │                                                     │
        │  1. Observation : résultat du tool précédent        │
        │  2. Raisonnement : que faire ensuite ?              │
        │  3. Action : nom_outil + arguments formatés         │
        │  4. Boucle jusqu'à "final_answer" ou limite         │
        └──────────────────────┬──────────────────────────────┘
                               │ trajectoire complète
                               ▼
        ┌─────────────────────────────────────────────────────┐
        │              BOUCLE DE RENFORCEMENT                  │
        │                                                     │
        │  Trajectoire → Rubric Reward → GRPO Advantage       │
        │                                                     │
        │  1. Évaluer la trajectoire (rubric multi-critères)  │
        │  2. Normaliser par rapport au groupe (GRPO)         │
        │  3. Mettre à jour les poids du modèle               │
        │  4. Répéter pour N épisodes                        │
        └─────────────────────────────────────────────────────┘
```

#### Quand utiliser ATLAS

- **Cas idéal :** Vous avez un ensemble d'outils bien défini (5-50 outils) et des démonstrations de leur utilisation correcte
- **Nécessite :** Un environnement simulé pour l'exploration RL, des données SFT de qualité
- **Gain typique :** +15% à +30% sur le taux de succès des tâches agentiques

---

### 10.3 Rubric-based RL

#### Définition

> **Rubric-based RL :** méthode de renforcement où la récompense n'est pas binaire (succès/échec) mais calculée par une grille d'évaluation multi-critères pondérée. Chaque aspect de la trajectoire (correction des outils, respect du format, complétion de la tâche, efficacité) reçoit un score partiel.

#### Analogie

> *"Une récompense binaire, c'est un examen noté uniquement sur le résultat final (admis/recalé). Une rubric, c'est une grille avec des points pour chaque compétence : la justesse du raisonnement, la clarté de l'explication, l'efficacité de la méthode. L'étudiant sait exactement sur quoi il est évalué et peut s'améliorer critère par critère."*

#### Implémentation commentée

```python
# === RUBRIC-BASED RL ===
# Chaque critère est pondéré. Le score total est la moyenne pondérée.
# Cela permet à l'agent d'apprendre progressivement : d'abord le format,
# puis la correction des outils, puis l'efficacité.

class Rubric:
    """Grille d'évaluation multi-critères pour le RL agentique.

    Chaque trajectoire est notée sur 4 axes :
    - tool_correctness : l'outil existe et les arguments sont valides
    - format_compliance : le format ReAct/JSON est respecté
    - task_completion : le résultat final correspond à l'objectif
    - efficiency : nombre d'étapes minimal pour réussir
    """

    def __init__(self, criteria: dict[str, float]):
        """
        criteria: dictionnaire {nom_critère: poids}
        Exemple:
        {
            "tool_correctness": 0.3,   # 30% de la note
            "format_compliance": 0.2,   # 20%
            "task_completion": 0.4,     # 40% (critère principal)
            "efficiency": 0.1,          # 10%
        }
        Les poids n'ont pas besoin de sommer à 1 (normalisation auto).
        """
        self.criteria = criteria
        self.total_weight = sum(criteria.values())

    def total(self, trajectory: list[dict], task: str) -> float:
        """Calcule la récompense totale = moyenne pondérée des scores."""
        scores = {}
        for criterion in self.criteria:
            if criterion == "tool_correctness":
                # Proportion d'appels d'outils sans erreur
                if not trajectory:
                    scores[criterion] = 0.0
                else:
                    valid = sum(1 for s in trajectory
                                if "error" not in str(s.get("result", "")).lower())
                    scores[criterion] = valid / len(trajectory)

            elif criterion == "format_compliance":
                # Proportion d'étapes avec les champs obligatoires
                if not trajectory:
                    scores[criterion] = 0.0
                else:
                    valid = sum(1 for s in trajectory
                                if "action" in s and "args" in s)
                    scores[criterion] = valid / len(trajectory)

            elif criterion == "task_completion":
                # Le dernier résultat contient-il l'objectif ?
                if not trajectory:
                    scores[criterion] = 0.0
                else:
                    last = str(trajectory[-1].get("result", ""))
                    # task contient le résultat attendu après ":"
                    target = task.split(":")[-1].strip()
                    scores[criterion] = 1.0 if target in last else 0.0

            elif criterion == "efficiency":
                # Pénalité si trop d'étapes (optimal = 3)
                if not trajectory:
                    scores[criterion] = 0.0
                else:
                    scores[criterion] = max(0.0, 1.0 - (len(trajectory) - 3) / 10)

        return sum(scores[c] * self.criteria[c] for c in self.criteria) / self.total_weight
```

---

### 10.4 GRPO (Group Relative Policy Optimization)

#### Définition

> **GRPO :** algorithme d'optimisation de politique qui, pour une tâche donnée, génère un groupe de N trajectoires, calcule leurs récompenses, normalise par la moyenne et l'écart-type du groupe, et utilise cet avantage relatif pour mettre à jour le modèle. Contrairement à PPO, aucun modèle critique (value function) séparé n'est nécessaire.

#### Différence avec PPO

| Aspect | PPO | GRPO |
|--------|-----|------|
| Modèle critique | Oui — value model séparé (2× les paramètres) | Non — moyenne du groupe suffit |
| Occupation mémoire | Élevée (actor + critic) | Réduite (~40% de VRAM en moins) |
| Stabilité | Clip objective | Normalisation par groupe |
| Bruit d'estimation | Value function approximée | Moyenne empirique du groupe |
| Adaptation agentique | Correcte | Excellente (exploration parallèle) |

#### Formule expliquée

L'avantage GRPO pour une trajectoire i dans un groupe de taille N :

$$A_i = \frac{r_i - \mu_r}{\sigma_r + \epsilon}$$

- $r_i$ : récompense de la trajectoire i
- $\mu_r = \frac{1}{N}\sum_{j=1}^{N} r_j$ : moyenne des récompenses du groupe
- $\sigma_r = \sqrt{\frac{1}{N}\sum_{j=1}^{N} (r_j - \mu_r)^2}$ : écart-type
- $\epsilon$ : petite constante (typiquement 1e-8) pour éviter la division par zéro

> **Interprétation :** $A_i > 0$ signifie que la trajectoire i est meilleure que la moyenne du groupe. Son poids dans la mise à jour du modèle est augmenté. $A_i < 0$ signifie qu'elle est moins bonne que la moyenne. Son poids est réduit. Pas besoin d'un modèle critique externe : le groupe sert de baseline naturelle.

#### Schéma ASCII — GRPO en action

```
Tâche : "Corriger le bug dans le fichier src/utils.py"

Trajectoire 1 ──> cherche → lit → patch → tests OK     → r=0.85
Trajectoire 2 ──> cherche → lit → patch → tests FAIL   → r=0.30
Trajectoire 3 ──> cherche → boucle → timeout           → r=0.10
Trajectoire 4 ──> lit → patch → tests OK               → r=0.65

Calcul : μ = (0.85 + 0.30 + 0.10 + 0.65) / 4 = 0.475
         σ = sqrt(((0.85-0.475)² + (0.30-0.475)² + (0.10-0.475)² + (0.65-0.475)²) / 4)
         σ = 0.28

Normalisation :
  T1 : A = (0.85 - 0.475) / 0.28 = +1.34  ← FORT RENFORCEMENT
  T2 : A = (0.30 - 0.475) / 0.28 = -0.63  ← ATTÉNUATION
  T3 : A = (0.10 - 0.475) / 0.28 = -1.34  ← IGNORÉ
  T4 : A = (0.65 - 0.475) / 0.28 = +0.63  ← RENFORCEMENT MODÉRÉ
```

---

### 10.5 Curriculum learning pour agents

#### Définition

> **Curriculum learning :** stratégie d'entraînement qui présente les exemples par difficulté croissante, en commençant par des tâches simples (appel d'outil unique) pour progresser vers des compositions complexes (résolution de bugs complets).

#### Principe

Un agent apprend mieux quand la difficulté augmente graduellement. Le curriculum suit quatre niveaux :

**Niveau 1 — Prompts simples :** appels d'outil uniques, format guidé, outil unique disponible.
- *Exemple :* "Cherche le fichier config.json" → un seul appel à `search`
- *Récompense :* binaire (appel correct ou non)

**Niveau 2 — Séquences linéaires :** 2-3 appels d'outils en séquence, outils multiples.
- *Exemple :* "Lis le fichier, modifie la ligne 42, sauvegarde" → `read` → `edit` → `write`
- *Récompense :* pondérée (bonus si séquence complète sans erreur)

**Niveau 3 — Tâches composées :** branchements conditionnels, choix d'outils, planification.
- *Exemple :* "Trouve tous les fichiers .py qui importent os, remplace os.path par pathlib" → `search` itératif + `edit` multiples
- *Récompense :* rubric (tool_correctness + completion + efficiency)

**Niveau 4 — Environnements complets :** résolution de bugs réels (SWE-bench), codebase inconnu.
- *Exemple :* Issue GitHub avec reproduction → diagnostic → patch → tests unitaires
- *Récompense :* programmatique (patch correct, tests passent, style valide)

---

### 10.6 SWE-smith : entraînement pour le software engineering

#### Architecture

SWE-smith est un système d'entraînement RL spécialisé pour les agents de résolution de bugs logiciels. Sa particularité : les récompenses sont programmatiques, calculées automatiquement à partir du patch généré et des résultats des tests.

```python
# === SYSTÈME DE RÉCOMPENSE SWE-SMITH ===
# La récompense n'est pas binaire (patch correct/incorrect) mais
# comporte plusieurs niveaux qui guident l'apprentissage progressif.

class SWESmithReward:
    """Récompense programmatique pour l'entraînement d'agents SWE.

    Cinq critères pondérés, du plus important au plus mineur :
    - patch_correct  (5.0) : patch identique à la solution attendue
    - patch_applies  (2.0) : patch syntaxiquement valide
    - tests_pass     (3.0) : proportion de tests réussis
    - edit_efficiency(1.0) : ni trop court ni trop long
    - format_valid   (0.5) : respecte le format diff/unified
    """

    def __init__(self, weights: dict[str, float] = None):
        self.weights = weights or {
            "patch_correct": 5.0,
            "patch_applies": 2.0,
            "tests_pass": 3.0,
            "edit_efficiency": 1.0,
            "format_valid": 0.5,
        }

    def __call__(self, patch: str, ground_truth: str,
                 test_results: dict[str, bool]) -> float:
        reward = 0.0

        # 1. Patch exactement correct → bonus maximal
        if patch.strip() == ground_truth.strip():
            reward += self.weights["patch_correct"]

        # 2. Patch syntaxiquement valide (contient des marqueurs diff)
        if bool(patch) and ("---" in patch or "+++" in patch):
            reward += self.weights["patch_applies"]

        # 3. Tests : récompense proportionnelle au taux de réussite
        if test_results:
            pass_rate = sum(test_results.values()) / len(test_results)
            reward += self.weights["tests_pass"] * pass_rate

        return reward
```

#### Résultats SWE-smith sur SWE-bench Verified (2026)

| Modèle | Avant RL | Après RL | Delta |
|--------|----------|----------|-------|
| opencode/big-pickle (8B) | 38.2% | 67.8% | +29.6% |
| Modèle 7B générique | 22.1% | 51.4% | +29.3% |
| Modèle 70B générique | 49.6% | 78.4% | +28.8% |

Les résultats montrent une constance remarquable du gain (+29% quel que soit le modèle de base), ce qui indique que le fine-tuning RL apporte des compétences agentiques qui sont indépendantes de la taille du modèle.

---

### 10.7 Construction guidée — pipeline complet de fine-tuning RL

Ce pipeline relie toutes les sections précédentes en une séquence opérationnelle.

#### 10.7.1 Préparation des données ReAct

```python
# === ÉTAPE 1 : CRÉATION D'UN DATASET D'ENTRAÎNEMENT AU FORMAT ReAct ===
# Chaque exemple est une interaction complète : question utilisateur + séquence d'actions.
# Format compatible avec SFTTrainer (TRL) et les frameworks de fine-tuning.

import json


def make_react_example(
    question: str,
    actions: list[dict],
    final_answer: str,
) -> dict:
    """Construit un exemple d'entraînement au format ReAct.

    Structure des messages :
    - user : la question posée à l'agent
    - assistant : Thought + Action + Action Input
    - tool : le résultat retourné par l'outil
    - assistant (final) : Thought + Final Answer
    """
    messages = [{"role": "user", "content": question}]

    for step in actions:
        # Étape de raisonnement + action
        messages.append({
            "role": "assistant",
            "content": (
                f"Thought: {step.get('thought', '')}\n"
                f"Action: {step['name']}\n"
                f"Action Input: {json.dumps(step.get('args', {}))}"
            ),
        })
        # Résultat de l'outil
        messages.append({
            "role": "tool",
            "content": str(step.get("result", "")),
            "name": step["name"],
        })

    # Réponse finale
    messages.append({
        "role": "assistant",
        "content": f"Thought: Objectif atteint.\nFinal Answer: {final_answer}",
    })

    return {"messages": messages}
```

#### 10.7.2 Environnement d'interaction RL

```python
# === ÉTAPE 2 : ENVIRONNEMENT SIMULÉ POUR L'ENTRAÎNEMENT RL ===
# L'agent appelle step(action, args) et reçoit (observation, reward, done).
# L'environnement valide les appels et calcule les récompenses.

class ToolEnv:
    """Environnement d'outils pour l'entraînement RL.

    step() gère trois cas :
    1. Outil valide, exécution réussie → reward positive
    2. Outil inexistant → pénalité et fin d'épisode
    3. Erreur d'exécution → pénalité légère et fin d'épisode
    """

    def __init__(self, tools: dict[str, callable]):
        self.tools = tools
        self.history = []

    def step(self, action: str, args: dict) -> tuple[str, float, bool]:
        if action not in self.tools:
            return ("Outil introuvable", -1.0, True)

        try:
            result = self.tools[action](**args)
            reward = 1.0   # Récompense de base pour action réussie
            done = (action == "final_answer")
            self.history.append({"action": action, "reward": reward})
            return (str(result), reward, done)

        except Exception as e:
            return (f"Erreur: {e}", -0.5, True)
```

#### 10.7.3 Boucle d'entraînement GRPO

```python
# === ÉTAPE 3 : ENTRAÎNEMENT PAR GROUPE AVEC GRPO ===
# Pour chaque tâche, on génère N trajectoires en parallèle,
# on normalise les récompenses par groupe, on met à jour le modèle.

class GRPOTrainer:
    """Entraînement Group Relative Policy Optimization.

    Boucle pour chaque tâche :
    1. Générer un groupe de N trajectoires via model(task)
    2. Évaluer chaque trajectoire avec reward_func
    3. Normaliser : A_i = (r_i - mean) / std
    4. Mettre à jour le modèle sur les trajectoires avec A_i > 0

    Contrairement à PPO, pas de modèle critique (value function).
    La normalisation se fait sur les récompenses observées.
    """

    def __init__(self, model_func, reward_func, group_size: int = 8):
        self.model = model_func
        self.reward = reward_func
        self.group_size = group_size

    def train_step(self, task: str, ground_truth: str) -> dict:
        # 1. Génération du groupe de trajectoires
        trajectories = [self.model(task) for _ in range(self.group_size)]

        # 2. Calcul des récompenses
        rewards = [self.reward(traj, ground_truth) for traj in trajectories]

        # 3. Normalisation GRPO
        mean_r = sum(rewards) / len(rewards)
        variance = sum((r - mean_r) ** 2 for r in rewards) / len(rewards)
        std_r = variance ** 0.5 + 1e-8
        advantages = [(r - mean_r) / std_r for r in rewards]

        # 4. Mise à jour : gradient ascent sur les bonnes trajectoires
        for traj, adv in zip(trajectories, advantages):
            if adv > 0:
                # En pratique : loss = -adv * log_prob(trajectoire)
                # TRL/Unsloth gèrent cette étape
                self._update(traj, adv)

        return {
            "mean_reward": mean_r,
            "best_reward": max(rewards),
            "n_positive": sum(1 for a in advantages if a > 0),
            "group_std": std_r - 1e-8,
        }

    def _update(self, trajectory: list[dict], advantage: float) -> None:
        """Mise à jour du modèle.
        L'implémentation réelle utilise GRPOTrainer de TRL ou une boucle PyTorch.
        """
        pass
```

#### 10.7.4 Évaluation sur benchmark

```python
# === ÉTAPE 4 : ÉVALUATION DU MODÈLE FINE-TUNÉ ===
# On compare les performances avant/après sur un benchmark standardisé.

def benchmark_agent(model, tasks: list[dict]) -> dict:
    """Évalue un modèle agentique sur un ensemble de tâches.

    tasks : liste de {
        "task": str,          # Description de la tâche
        "tools": list[str],   # Outils autorisés
        "expected": str,      # Résultat attendu
    }
    """
    results = {"success": 0, "total": len(tasks), "details": []}

    for task in tasks:
        trajectory = model(task["task"])
        last_result = str(trajectory[-1].get("result", "")) if trajectory else ""
        success = task["expected"] in last_result

        results["success"] += int(success)
        results["details"].append({
            "task_id": task.get("id", ""),
            "success": success,
            "steps": len(trajectory),
        })

    results["accuracy"] = results["success"] / results["total"]
    return results


# Utilisation :
# base_results = benchmark_agent(base_model, benchmark)
# ft_results = benchmark_agent(finetuned_model, benchmark)
# gain = ft_results["accuracy"] - base_results["accuracy"]
# print(f"Gain après fine-tuning RL: {gain * 100:.1f}%")
```

**Lab associé :** `lab/README.md` — Partie 5 : Fine-tuning d'un modèle pour tool calling avec Unsloth. Mettez en pratique ce pipeline sur un dataset ReAct de 500 trajectoires.

---

## Synthèse

**Ce que vous avez appris dans cette séance :**

| Concept | Résumé | Section |
|---------|--------|---------|
| Pourquoi fine-tuner | Les modèles de base échouent sur 5 aspects : tool calling, format, raisonnement multi-tour, domaine, latence | 10.1 |
| ATLAS | SFT → RL → Alignment : les trois phases pour adapter un modèle à des outils | 10.2 |
| Rubric-based RL | Récompense multi-critères pondérée : apprentissage plus stable et plus interprétable | 10.3 |
| GRPO | Optimisation sans modèle critique : normalisation des récompenses par groupe | 10.4 |
| Curriculum learning | 4 niveaux de difficulté : prompts simples → séquences → tâches composées → environnements | 10.5 |
| SWE-smith | RL appliqué au software engineering avec récompenses programmatiques | 10.6 |
| Pipeline complet | Data ReAct → Environnement RL → Boucle GRPO → Évaluation benchmark | 10.7 |

**Lien avec la séance suivante :**

> *"Maintenant que vous savez entraîner un modèle par renforcement pour des tâches agentiques, la séance 11 (Optimisation mémoire et contexte) vous apprendra à appliquer ces techniques pour réduire l'empreinte mémoire des agents. Vous réutiliserez GRPO et le curriculum learning pour produire des modèles plus petits et plus rapides, en distillant les compétences agentiques dans des architectures légères, sans sacrifier la qualité des réponses."*

---

## Références contextualisées

- **[Mishra et al., "ATLAS: Reinforcement Finetuning for Agent Tool Spaces" (2025)]**
  *Contexte :* Article fondateur cité en section 10.2. Définit l'architecture ATLAS et détaille la boucle RL pour l'entraînement d'agents.
  *Niveau de lecture :* Avancé (nécessite des bases en RL)

- **[Shao et al., "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning" (2025)]**
  *Contexte :* Présente GRPO, l'algorithme utilisé en section 10.4. Explique pourquoi le group-based advantage surpasse PPO pour l'entraînement des LLM.
  *Niveau de lecture :* Avancé

- **[Yang et al., "Training SWE Agents with Programmatic Rewards" (2025)]**
  *Contexte :* Détaille SWE-smith (section 10.6). Montre la conception de récompenses programmatiques pour le software engineering et les résultats sur SWE-bench.
  *Niveau de lecture :* Intermédiaire

- **[Documentation TRL (Hugging Face)]**
  *Contexte :* Référence technique pour implémenter GRPOTrainer et RewardTrainer (section 10.7.3). À consulter pendant le lab.
  *Niveau de lecture :* Technique
  *→ https://huggingface.co/docs/trl*

- **[Documentation Unsloth]**
  *Contexte :* Optimisation mémoire pour le fine-tuning LoRA/QLoRA. Utilisé dans le lab pour réduire la consommation VRAM de moitié.
  *Niveau de lecture :* Technique
  *→ https://github.com/unslothai/unsloth*

- **[Databricks, "The Art of Data Preparation for Agent Fine-Tuning" (2026)]**
  *Contexte :* Guide pratique sur la création de datasets ReAct et tool calling. Référence pour la section 10.7.1.
  *Niveau de lecture :* Intermédiaire

- **[Google DeepMind, "RL for Tool-Using Agents: Best Practices" (2026)]**
  *Contexte :* Rapport technique couvrant l'ensemble des sections 10.1 à 10.7. Synthèse des meilleures pratiques issues de plusieurs équipes de recherche.
  *Niveau de lecture :* Intermédiaire
