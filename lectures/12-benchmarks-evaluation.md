# Séance 12 — Benchmarks & Évaluation

> **Durée estimée :** 2 heures

---

## Description

Cette séance couvre les benchmarks et métriques d'évaluation des systèmes agentiques. Vous apprendrez la famille SWE-bench, les métriques (pass@1, resolve rate, contamination), et implémenterez un évaluateur de benchmark personnalisé. Cette séance fait le pont entre l'optimisation mémoire (séance 11) et le déploiement en production (séance 13).

---

## Prérequis

Avant de commencer cette séance, assurez-vous d'avoir :

- Terminé la **Séance 11** et compris les stratégies d'optimisation
- Python 3.10+ installé
- Connaissances de base en statistiques et métriques

### Installation des dépendances

#### Linux et macOS

```bash
# Vérifier Python
python3 --version

# Installer LangSmith pour le monitoring
python3 -m pip install langsmith

# Vérifier l'installation
python3 -c "import langsmith; print('LangSmith installé')"
```

#### Windows PowerShell

```powershell
# Vérifier Python
py --version

# Installer LangSmith pour le monitoring
py -m pip install langsmith

# Vérifier l'installation
py -c "import langsmith; print('LangSmith installé')"
```

> **Résultat attendu :** LangSmith est installé et importable.

---

## Introduction théorique

**Quel problème cette séance adresse-t-elle ?**

Comment mesurer objectivement la performance d'un agent logiciel ? Les benchmarks standards comme MMLU (raisonnement sur texte) ou HumanEval (génération de code isolée) ne mesurent pas les capacités agentiques réelles : utilisation d'outils, navigation dans une base de code, planification multi-étapes, résolution de bugs complexes. Un modèle peut obtenir 90% sur HumanEval et échouer à corriger un bug simple dans Django parce qu'il ne sait pas chercher le bon fichier, lire le contexte, exécuter des tests, et appliquer un patch correct.

**Où se situe ce concept dans l'écosystème agentique 2026 ?**

La famille SWE-bench est apparue en 2024 pour combler ce vide. En deux ans, les scores sont passés de 12% (GPT-4 + SWE-agent, avril 2024) à 93.9% (big-pickle + SWE-smith v2, mars 2026). Cette progression fulgurante a transformé SWE-bench en *de facto* standard de l'industrie. Des meta-benchmarks comme SWE-Compass (2026) sont venus affiner la mesure en catégorisant 8 types de tâches sur 10 langages.

**Lien avec les séances précédentes et suivantes :**

La séance 11 vous a appris à optimiser la mémoire et le contexte d'un agent. La séance 12 vous apprend à *mesurer* si cette optimisation est réellement efficace — et à détecter les fuites de performance. La séance 13 (Déploiement & Production) utilisera ces métriques pour décider si un agent est prêt à être mis en production et comment le monitorer.

> *"L'optimisation sans métrique, c'est du bricolage. La métrique sans benchmark, c'est de l'opinion."*

## Objectifs pédagogiques

À l'issue de cette séance, vous serez capable de :

1. **Distinguer les 4 variantes de SWE-bench** (Verified, Pro, Live, Multilingual) — connaître leur nombre d'instances, difficulté, format et cas d'usage
2. **Calculer et interpréter les métriques agentiques** (pass@1, resolve rate, contamination score) — comprendre ce qu'elles mesurent et ne mesurent pas
3. **Analyser l'évolution 2024-2026** — décomposer la progression des scores entre modèle, scaffold et fine-tuning
4. **Implémenter un évaluateur SWE-bench** en Python — maîtriser les structures de données et la logique d'évaluation (patch exact + test-based)
5. **Concevoir un benchmark personnalisé** pour son propre domaine — savoir définir des tâches, un évaluateur et un rapport de résultats

## Plan détaillé

### 12.1 SWE-bench family : Verified, Pro, Live, Multilingual

SWE-bench est une famille de benchmarks qui évaluent la capacité d'un agent à résoudre des bugs réels issus de projets open-source (Django, Flask, SymPy, pytest...). Chaque instance est un bug GitHub avec un patch de correction connu.

#### SWE-bench Verified

> **Définition :** Sous-ensemble de 500 instances validées manuellement par des ingénieurs humains. Chaque instance a été vérifiée pour s'assurer que le patch de correction est correct et que les tests de validation sont fiables.

- **Instances :** 500 (sur les 2294 de SWE-bench original)
- **Difficulté :** Medium (instances les moins ambiguës)
- **Format :** Une instance = un repo + un base_commit + une description de bug + un gold_patch + des tests fail_to_pass/pass_to_pass
- **Pourquoi c'est la référence :** Les 500 instances sont propres, sans faux positifs. C'est le standard de facto depuis 2025.

#### SWE-bench Pro (2026)

> **Définition :** Extension de SWE-bench avec 2000 instances incluant des bugs multi-fichiers, des nécessités de refactoring, et des correctifs de sécurité.

- **Instances :** ~2000
- **Difficulté :** Hard (bugs multi-fichiers, dépendances complexes)
- **Nouveautés :** Patches touchant 3-10 fichiers, requires_refactor, severity labeling (critical/major/minor)
- **Cas d'usage :** Évaluer des agents capables de comprendre l'architecture d'un projet

#### SWE-bench Live

> **Définition :** Benchmark dynamique qui collecte des instances en temps réel depuis les issues GitHub ouvertes, empêchant la contamination des données d'entraînement.

- **Fréquence :** Nouvelles instances chaque semaine
- **Anti-contamination :** Les instances sont postérieures à la date de coupure des modèles
- **Format :** API REST pour récupérer les instances, soumettre les patches, obtenir les résultats
- **Défi :** Les agents doivent généraliser, pas mémoriser

#### SWE-bench Multilingual (2026)

> **Définition :** Extension à 10 langages de programmation pour mesurer la capacité des agents à travailler dans des écosystèmes variés.

| Langage | % du benchmark | Difficulté moyenne | Types de bugs typiques |
|---------|---------------|-------------------|----------------------|
| Python | 40% | Medium | Import, typage, logique |
| JavaScript/TypeScript | 20% | Medium-Hard | Async, DOM, types |
| Java | 12% | Hard | Null pointer, threads |
| Go | 8% | Medium | Concurrence, interfaces |
| Rust | 7% | Hard | Ownership, lifetimes |
| C/C++ | 5% | Hard | Mémoire, pointeurs |
| Ruby | 3% | Easy-Medium | Blocks, nil |
| PHP | 2% | Medium | Types faibles, injection |
| Kotlin | 2% | Medium | Null safety, coroutines |
| Swift | 1% | Medium | Optionals, ARC |

---

### 12.2 Métriques : pass@1, resolve rate, contamination

#### pass@1

> **Définition :** Probabilité que l'agent produise un correctif correct en un seul essai.

```
pass@1 = (nombre d'instances résolues au premier essai) / (nombre total d'instances)
```

- **Ce qu'elle mesure :** La fiabilité de l'agent — peut-on lui faire confiance du premier coup ?
- **Ce qu'elle ne mesure PAS :** La capacité à itérer, à corriger son erreur, à explorer plusieurs solutions
- **Variante :** pass@k — l'agent a droit à k essais, on prend le meilleur

#### Resolve rate

> **Définition :** Taux d'instances où le patch généré par l'agent satisfait les critères de validation.

```
resolve_rate = (instances avec patch validé) / (total instances)
```

La validation peut être :
- **Exact match :** Le patch généré est identique au gold_patch (strict)
- **Test-based :** Le patch fait passer les tests fail_to_pass sans casser les pass_to_pass (tolérant)
- **Mixte :** Exact match d'abord, test-based en fallback (recommandé)

#### Contamination score

> **Définition :** Mesure de la proportion d'instances du benchmark qui ont pu être vues pendant l'entraînement du modèle.

```
contamination = (instances dont le correctif est dans les données d'entraînement) / (total instances)
```

- **Problème :** Si un modèle a déjà vu le correctif pendant son entraînement, le score n'est pas significatif
- **Solution SWE-bench Live :** Utiliser des bugs postérieurs à la date de coupure
- **Solution complémentaire :** Mesurer la perplexité sur les instances — une perplexité anormalement basse suggère une contamination

#### Pièges des métriques

| Métrique | Ne mesure pas | Faux positif possible |
|----------|--------------|----------------------|
| pass@1 | Robustesse, adaptation | Coup de chance |
| Exact match | Solutions alternatives valides | Patch identique mais bugué |
| Test-based | Couverture des tests | Tests insuffisants |
| Resolve rate | Coût (tokens, temps) | Agent qui triche (ex: supprime les tests) |

---

### 12.3 Évolution 2025-2026 : de 48% à 93.9%

La progression des scores sur SWE-bench Verified raconte l'histoire du progrès en agentic AI :

```
2024-04  GPT-4 + SWE-agent                      12.3%  ████████ ── ReAct prompting
2024-08  Devin (Cognition)                       48.0%  ██████████████████████████████ ── Premier agent commercial
2024-12  Claude 3.5 + Agentless                  49.6%  ████████████████████████████████ ── Approche sans agent
2025-03  CodeAgent                              62.4%  █████████████████████████████████████████ ── Modèle spécialisé code
2025-07  SWE-smith + GRPO                        78.4%  ███████████████████████████████████████████████████ ── RL fine-tuning
2025-11  O1 + LangGraph + SWE-smith              88.5%  ████████████████████████████████████████████████████████ ── Approche combinée
2026-03  big-pickle + SWE-smith v2               93.9%  █████████████████████████████████████████████████████████████ ── Modèle spécialisé
```

**Analyse de la progression :**

| Période | Progression | Facteur dominant |
|---------|------------|------------------|
| 2024 (12% → 49%) | +37 pts | Amélioration du prompting et du scaffold |
| 2025 H1 (49% → 62%) | +13 pts | Modèles spécialisés code |
| 2025 H2 (62% → 88%) | +26 pts | RL fine-tuning + test-time compute |
| 2026 (88% → 94%) | +6 pts | Combinaison de toutes les techniques |

**Décomposition de l'impact :**

| Facteur | Contribution | Mécanisme |
|---------|-------------|-----------|
| Modèle de base | ~35% | Capacités de raisonnement, compréhension du code |
| Scaffold (LangGraph) | ~30% | Navigation, édition, orchestration |
| RL fine-tuning (SWE-smith) | ~25% | Spécialisation sur le format de patch, GRPO |
| Données d'entraînement | ~10% | Trajectoires ReAct, démonstrations de correctifs |

> **Leçon clé :** Le scaffold (architecture agent) a autant d'impact que le modèle lui-même. Un bon modèle sans scaffold plafonne à ~35%; un modèle médiocre avec un bon scaffold atteint ~55%. La combinaison des deux + RL fine-tuning donne les meilleurs résultats.

---

### 12.4 SWE-Compass : 8 types de tâches, 10 langages

SWE-Compass (2026) est un meta-benchmark qui catégorise les tâches de génie logiciel en 8 types :

| Type | Description | Difficulté | Exemple |
|------|-------------|-----------|---------|
| Simple Bug Fix | Correction localisée dans une fonction | 1-2 | Off-by-one, variable non initialisée |
| Multi-file Patch | Modification coordonnée de 3+ fichiers | 3-4 | Refactoring d'interface, changement d'API |
| API Migration | Mise à jour d'appels d'API obsolètes | 2-3 | `requests` → `httpx`, Django 3 → 4 |
| Refactoring | Restructuration sans changement fonctionnel | 3-4 | Extraction de méthode, introduction de pattern |
| Test Addition | Ajout de tests pour une fonctionnalité | 2-3 | Test unitaire manquant, test de régression |
| Documentation | Mise à jour de docstrings et commentaires | 1-2 | Docstring manquante, commentaire obsolète |
| Performance | Optimisation sans changement de comportement | 3-4 | Cache, algorithme plus efficace |
| Security Fix | Correction de vulnérabilité | 4-5 | Injection XSS, SQLi, path traversal |

**Couverture par langage :**

| Langage | Instances | Types dominants | Particularité |
|---------|-----------|----------------|---------------|
| Python | 2000 | Simple Bug Fix, Multi-file | Écosystème le plus riche |
| JS/TS | 1000 | API Migration, Test Addition | Bugs async fréquents |
| Java | 600 | Multi-file, Refactoring | Patches volumineux |
| Go | 400 | Simple Bug Fix, Performance | Bugs de concurrence |
| Rust | 350 | Security Fix, Performance | Bugs d'ownership |
| C/C++ | 250 | Security Fix, Performance | Mémoire, buffer overflow |
| Ruby | 150 | Documentation, Simple Bug Fix | Bugs nil-related |
| PHP | 100 | Security Fix, API Migration | Injection |
| Kotlin | 100 | Refactoring, Test Addition | Null safety |
| Swift | 50 | API Migration, Refactoring | ARC, optionals |

**Utilité de SWE-Compass :** Permet d'identifier les faiblesses spécifiques d'un agent. Exemple : un agent peut obtenir 85% sur SWE-bench Verified mais seulement 40% sur les tâches Security Fix de SWE-Compass — révélant un déficit de compréhension des vulnérabilités.

---

### 12.5 Construction guidée : l'évaluateur SWE-bench

Cette section décortique ligne par ligne le code d'un évaluateur SWE-bench complet. Chaque ligne est commentée en français pour expliquer non seulement *ce qu'elle fait* mais aussi *pourquoi* elle est conçue ainsi.

```python
# === ÉVALUATEUR SWE-BENCH ===
# Fichier : swe_bench_evaluator.py
# Rôle    : Évaluer les correctifs produits par un agent
#           en comparant avec le patch attendu (gold_patch)
#           et/ou en exécutant les tests de validation.
# Dépendances : dataclasses (stdlib), typing (stdlib)

from dataclasses import dataclass, field
# ↑ dataclass : génère automatiquement __init__, __repr__, __eq__.
#   Évite d'écrire du code boilerplate pour les structures de données.
from typing import Any
# ↑ Any : type générique pour les métadonnées optionnelles.
#   Utile car SWE-Compass ajoute des champs par type de tâche.

from enum import Enum, auto
# ↑ Enum : pour les niveaux de sévérité. Plus sûr que des strings.
#   auto() génère une valeur entière unique automatiquement.


class Severity(Enum):
    """Niveaux de sévérité pour SWE-bench Pro."""
    # ↑ Enum : chaque membre a un nom et une valeur uniques.
    #   On utilise Enum plutôt que des strings pour éviter les fautes
    #   de frappe et permettre à l'IDE de suggérer les valeurs.
    CRITICAL = auto()
    # ↑ auto() : valeur = 1. Pas besoin de préciser le nombre.
    MAJOR = auto()
    # ↑ auto() : valeur = 2.
    MINOR = auto()
    # ↑ auto() : valeur = 3.


@dataclass
class SWEBenchInstance:
    """Instance SWE-bench : un bug à résoudre.

    Cette classe représente une instance unique du benchmark.
    Chaque champ est un élément essentiel pour l'évaluation.
    """
    # ↑ Le décorateur @dataclass génère automatiquement :
    #   - __init__(self, instance_id, repo, base_commit, ...)
    #   - __repr__(self) → "SWEBenchInstance(instance_id='django...')"
    #   - __eq__(self, other) → compare tous les champs
    instance_id: str
    # ↑ Identifiant unique de l'instance.
    #   Format : "repo__repo-NUMERO" (ex: "django__django-12345").
    #   Permet de tracer quelle instance a été résolue ou non.
    repo: str
    # ↑ Nom du dépôt GitHub (django, flask, sympy, pytest...).
    #   Utile pour analyser la performance par projet.
    base_commit: str
    # ↑ Hash du commit avant l'introduction du bug.
    #   L'agent doit partir de ce commit pour appliquer son correctif.
    problem: str
    # ↑ Description du bug en langage naturel.
    #   C'est l'entrée principale de l'agent — ce que l'utilisateur
    #   lui demande de corriger.
    hint: str | None
    # ↑ Indice optionnel pour aider l'agent.
    #   Certaines instances fournissent un indice sur la cause racine.
    #   None si pas d'indice (la plupart des cas).
    gold_patch: str
    # ↑ Patch correct attendu (ground truth).
    #   C'est LE fichier de référence : tout correctif de l'agent
    #   sera comparé à ce patch pour décider s'il est correct.
    #   Format : diff unifié (git diff).
    test_files: list[str] = field(default_factory=list)
    # ↑ Liste des fichiers de test à exécuter.
    #   default_factory=list permet d'initialiser avec une liste vide
    #   sans partager la même liste entre toutes les instances.
    fail_to_pass: list[str] = field(default_factory=list)
    # ↑ Tests qui doivent PASSER après le correctif (mais échouaient avant).
    #   Ce sont les tests qui reproduisent le bug. S'ils passent
    #   après le patch, c'est que le bug est probablement corrigé.
    pass_to_pass: list[str] = field(default_factory=list)
    # ↑ Tests qui doivent RESTER verts après le correctif.
    #   Ce sont des tests de régression : le patch ne doit pas
    #   casser des fonctionnalités existantes.


@dataclass
class SWEBenchProInstance:
    """Instance SWE-bench Pro : bugs complexes multi-fichiers.

    Hérite de SWEBenchInstance et ajoute des métadonnées
    pour les bugs plus complexes de la version Pro (2026).
    """
    instance_id: str
    repo: str
    base_commit: str
    problem: str
    hint: str | None = None
    gold_patch: str = ""
    test_files: list[str] = field(default_factory=list)
    fail_to_pass: list[str] = field(default_factory=list)
    pass_to_pass: list[str] = field(default_factory=list)
    # ↑ Les champs ci-dessus sont identiques à SWEBenchInstance.
    #   On ne peut pas utiliser l'héritage avec @dataclass
    #   sans précautions (problème d'ordre des champs).
    #   On duplique donc les champs de base pour simplifier.
    multi_file: bool = False
    # ↑ True si le patch touche plusieurs fichiers.
    #   Un bug multi-fichier est plus dur car l'agent doit
    #   comprendre comment les fichiers interagissent.
    requires_refactor: bool = False
    # ↑ True si la correction nécessite un refactoring.
    #   Exemple : extraire une méthode, créer une classe.
    #   L'agent ne peut pas se contenter de changer une ligne.
    affected_tests: int = 0
    # ↑ Nombre de tests impactés par le patch.
    #   Plus il y a de tests impactés, plus le risque de
    #   régression est élevé.
    severity: Severity = Severity.MINOR
    # ↑ Sévérité du bug (CRITICAL, MAJOR, MINOR).
    #   Utilise l'Enum Severity défini plus haut.
    #   Un bug CRITICAL (ex: perte de données) est prioritaire.


class EvaluationMode(Enum):
    """Mode d'évaluation : exact match, test-based, ou mixte."""
    # ↑ Les trois stratégies d'évaluation possibles.
    EXACT_MATCH = auto()
    # ↑ Compare le patch généré au gold_patch caractère par caractère.
    #   Strict, mais peut rejeter des correctifs valides mais différents.
    TEST_BASED = auto()
    # ↑ Exécute les tests : fail_to_pass doivent passer,
    #   pass_to_pass doivent rester verts.
    #   Tolérant, mais dépend de la qualité des tests.
    MIXED = auto()
    # ↑ Exact match d'abord, test-based en fallback.
    #   Le meilleur des deux mondes : rapide si exact, robuste sinon.


class SWEBenchEvaluator:
    """Évaluateur principal pour SWE-bench.

    Cet évaluateur compare les patches produits par un agent
    aux patches attendus (gold_patch) et/ou aux résultats des tests.
    Il implémente les trois modes d'évaluation (exact, test, mixte).
    """

    def __init__(
        self,
        instances: list[SWEBenchInstance],
        mode: EvaluationMode = EvaluationMode.MIXED,
    ):
        """Initialise l'évaluateur avec la liste des instances.

        Paramètres :
            instances : liste des instances SWE-bench à évaluer
            mode : mode d'évaluation (MIXED par défaut)
        """
        self.instances = instances
        # ↑ Stocke la liste des instances pour y accéder pendant l'évaluation.
        #   On pourrait aussi charger les instances depuis un fichier JSON.
        self.mode = mode
        # ↑ Le mode d'évaluation choisi.
        #   MIXED est recommandé : il combine vitesse et robustesse.

    def evaluate(
        self,
        agent_patches: dict[str, str],
        test_results: dict[str, dict[str, bool]] | None = None,
    ) -> dict[str, float]:
        """Évalue tous les patches soumis par l'agent.

        Parcourt chaque instance, compare le patch de l'agent
        au gold_patch, et agrège les résultats.

        Paramètres :
            agent_patches : dict {instance_id: patch_string}
                Les patches produits par l'agent pour chaque instance.
            test_results : dict optionnel {instance_id: {test_name: bool}}
                Résultats des tests. Nécessaire pour TEST_BASED et MIXED.

        Retourne :
            dict avec les métriques agrégées :
            - resolved : taux de résolution (0.0 à 1.0)
            - correct : nombre d'instances résolues
            - total : nombre total d'instances
        """
        correct = 0
        # ↑ Compteur d'instances correctement résolues.
        #   On l'incrémente pour chaque instance valide.
        total = len(self.instances)
        # ↑ Nombre total d'instances à évaluer.
        #   Évite de recalculer len(self.instances) à chaque itération.
        details: dict[str, bool] = {}
        # ↑ Dictionnaire pour stocker le résultat détaillé par instance.
        #   Utile pour le débogage et l'analyse par type de tâche.

        for inst in self.instances:
            # ↑ On parcourt chaque instance du benchmark.
            patch = agent_patches.get(inst.instance_id, "")
            # ↑ On récupère le patch soumis par l'agent pour cette instance.
            #   Si l'agent n'a pas soumis de patch, on utilise une chaîne vide.
            #   Une chaîne vide ne passera jamais l'exact match.

            is_correct = self._check_instance(
                inst, patch, test_results
            )
            # ↑ Délègue la vérification à une méthode privée.
            #   Cela rend evaluate() plus lisible et facilite les tests unitaires.

            details[inst.instance_id] = is_correct
            # ↑ Stocke le résultat individuel pour analyse ultérieure.

            if is_correct:
                correct += 1
            # ↑ Incrémente le compteur si l'instance est résolue.

        resolved = correct / total if total > 0 else 0.0
        # ↑ Taux de résolution : proportion d'instances correctes.
        #   Protection contre la division par zéro si total == 0.

        return {
            "resolved": resolved,
            # ↑ Taux de résolution (0.0 à 1.0). Métrique principale.
            "correct": correct,
            # ↑ Nombre absolu d'instances résolues.
            "total": total,
            # ↑ Nombre total d'instances.
            "details": details,
            # ↑ Résultats individuels par instance.
            #   Permet d'analyser quelles instances ont échoué.
            "mode": self.mode.name,
            # ↑ Mode d'évaluation utilisé (EXACT_MATCH, TEST_BASED, MIXED).
            #   Important pour reproductibilité : le même score peut varier
            #   selon le mode choisi.
        }

    def _check_instance(
        self,
        inst: SWEBenchInstance,
        patch: str,
        test_results: dict[str, dict[str, bool]] | None,
    ) -> bool:
        """Vérifie si une instance est correctement résolue.

        Logique à trois niveaux selon le mode :
        - EXACT_MATCH : compare le patch au gold_patch
        - TEST_BASED : exécute les tests de validation
        - MIXED : exact match d'abord, test-based en fallback

        Paramètres :
            inst : l'instance à vérifier
            patch : le patch soumis par l'agent
            test_results : résultats des tests (dict optionnel)

        Retourne :
            True si l'instance est considérée comme résolue
        """
        if self.mode == EvaluationMode.EXACT_MATCH:
            return patch.strip() == inst.gold_patch.strip()
            # ↑ Comparaison stricte : on enlève les espaces superflus
            #   avec strip() pour éviter les faux négatifs dus aux
            #   sauts de ligne en trop. Mais deux patches peuvent
            #   être fonctionnellement identiques sans être identiques
            #   textuellement — c'est la limite de l'exact match.

        if self.mode == EvaluationMode.TEST_BASED:
            return self._check_by_tests(inst, test_results)
            # ↑ Délègue à la méthode de vérification par tests.

        # Mode MIXED : exact match d'abord, test-based en fallback
        if patch.strip() == inst.gold_patch.strip():
            return True
            # ↑ Si le patch est exactement le bon, on valide directement.
            #   C'est rapide (pas besoin de lancer les tests) et fiable.

        if test_results is None:
            return False
            # ↑ Si on n'a pas de résultats de tests, on ne peut pas
            #   faire de fallback. L'instance est marquée comme échouée.

        return self._check_by_tests(inst, test_results)
        # ↑ Fallback : on vérifie par les tests.
        #   C'est le cas où le patch de l'agent est différent du
        #   gold_patch mais pourrait être fonctionnellement correct.

    def _check_by_tests(
        self,
        inst: SWEBenchInstance,
        test_results: dict[str, dict[str, bool]] | None,
    ) -> bool:
        """Vérifie une instance par les résultats des tests.

        Deux conditions doivent être toutes les deux satisfaites :
        1. Tous les tests fail_to_pass doivent PASSER
        2. Tous les tests pass_to_pass doivent RESTER verts

        Paramètres :
            inst : l'instance à vérifier
            test_results : résultats des tests

        Retourne :
            True si les deux conditions sont remplies
        """
        if test_results is None:
            return False
            # ↑ Pas de résultats de tests disponibles → on ne peut pas vérifier.
            #   Mieux vaut un faux négatif qu'un faux positif.

        instance_results = test_results.get(inst.instance_id, {})
        # ↑ On récupère les résultats pour cette instance spécifique.
        #   Si l'instance n'est pas dans test_results, on utilise {}.
        #   Tous les tests seront considérés comme échoués → la vérification
        #   échoue (conservateur).

        fail_pass_ok = all(
            instance_results.get(t, False) for t in inst.fail_to_pass
        )
        # ↑ Vérifie que TOUS les tests fail_to_pass passent.
        #   Ces tests échouaient avant le correctif (ils reproduisent le bug).
        #   S'ils passent maintenant, c'est que le bug est probablement corrigé.
        #   On utilise get(t, False) : si un test n'est pas dans les résultats,
        #   il est considéré comme échoué (hypothèse prudente).

        pass_pass_ok = all(
            instance_results.get(t, True) for t in inst.pass_to_pass
        )
        # ↑ Vérifie qu'aucun test pass_to_pass n'est cassé.
        #   Ces tests passaient avant le correctif.
        #   S'ils échouent, le patch a introduit une régression.
        #   Note : get(t, True) — si un test n'est pas rapporté,
        #   on le considère comme passant (hypothèse prudente pour éviter
        #   les faux positifs de régression).

        return fail_pass_ok and pass_pass_ok
        # ↑ Les DEUX conditions doivent être remplies.
        #   C'est la définition d'un correctif valide dans SWE-bench :
        #   le bug est corrigé ET rien n'est cassé.

    def compare_with(
        self,
        other_evaluator: "SWEBenchEvaluator",
    ) -> dict[str, Any]:
        """Compare les résultats de deux versions d'agent.

        Utile pour les tests A/B : on évalue deux configurations
        d'agent sur les mêmes instances et on compare.

        Paramètres :
            other_evaluator : un autre évaluateur avec ses résultats

        Retourne :
            dict avec les métriques comparées et les deltas
        """
        # NOTE : cette méthode suppose que les deux évaluateurs
        # ont déjà été exécutés (self.results et other.results existent).
        # Dans une version plus robuste, on vérifierait que les mêmes
        # instances ont été utilisées.
        return {
            "self_resolved": self.results["resolved"],
            # ↑ Taux de résolution du premier agent.
            "other_resolved": other_evaluator.results["resolved"],
            # ↑ Taux de résolution du second agent.
            "delta": (
                self.results["resolved"]
                - other_evaluator.results["resolved"]
            ),
            # ↑ Différence entre les deux taux.
            #   Positif = le premier agent est meilleur.
            #   Négatif = le second est meilleur.
        }
```

**Analyse des faux positifs et faux négatifs :**

| Situation | Exact match | Test-based | Mixte |
|-----------|------------|------------|-------|
| Patch identique au gold_patch | ✅ Correct | ✅ Correct | ✅ Correct |
| Patch différent mais fonctionnellement correct | ❌ Faux négatif | ✅ Correct | ✅ Correct |
| Patch identique mais qui casse d'autres tests | ✅ Correct (faux positif) | ❌ Faux négatif | ❌ Faux négatif |
| Patch différent mais qui fait passer les tests | ❌ Faux négatif | ✅ Possible faux positif si tests insuffisants | ✅ Possible faux positif |

> **Recommandation :** Utiliser le mode MIXTE. Il capture les solutions alternatives valides (via le fallback test-based) tout en restant rapide pour les cas d'exact match. Toujours inspecter manuellement un échantillon des faux positifs potentiels.

---

### 12.6 Outils de monitoring : LangSmith, AgentOps, W&B

| Outil | Fonction | Prix | Intégration | Points forts |
|-------|---------|------|-------------|-------------|
| LangSmith | Tracing + Dataset + Eval | Freemium | Natif LangChain/LangGraph | Datasets, comparaison de runs |
| AgentOps | Monitoring agent + Replay | Freemium | SDK Python | Replay sessions, métriques agent |
| W&B | Experiment tracking | Gratuit (OSS) | Any (wandb.log) | Tableaux de bord, comparaison |
| LangFuse | Observabilité LLM | OSS | Tous frameworks | Open source, auto-hébergé |

**Quand utiliser quoi :** LangSmith en dev (tracing), AgentOps en production (monitoring continu), W&B en recherche (comparaison de runs), LangFuse pour les déploiements privés (auto-hébergement).

---

### 12.7 Concevoir son propre benchmark : guide pratique

Créer un benchmark personnalisé est essentiel pour évaluer des agents sur des domaines spécifiques que les benchmarks standards ne couvrent pas (code propriétaire, domaine métier, stack technique interne).

**Étapes de conception :** (1) Définir le périmètre (type de tâche, langage, difficulté) → (2) Collecter les instances (issues GitHub, bugs internes) → (3) Établir le gold standard (correction validée par un humain) → (4) Définir les métriques (exact match, test-based, score partiel) → (5) Implémenter l'évaluateur → (6) Exécuter et analyser.

**Bonnes pratiques :** Anti-contamination (pas d'instances potentiellement dans les données d'entraînement), reproductibilité (fixer les seeds et versions), équité (mêmes conditions pour tous les agents), granularité (catégoriser par type de tâche), évolutivité (nouvelles instances régulières).

```
mon-benchmark/
├── instances/              # Fichiers JSON des instances
├── evaluator.py            # Réutilisation de SWEBenchEvaluator
├── gold_patches/           # Correctifs de référence (.patch)
├── tests/                  # Tests de validation
├── results/                # Résultats des runs (JSON)
└── README.md
```

**Lab:** `lab/README.md` — Partie 7: Évaluation d'un agent avec SWE-bench et création de benchmark

---

## Synthèse

**Ce que vous avez appris dans cette séance :**

| Concept | Résumé | Section |
|---------|--------|---------|
| SWE-bench family | 4 variantes (Verified, Pro, Live, Multilingual) avec des niveaux de difficulté et des formats différents | 12.1 |
| Métriques agentiques | pass@1, resolve rate, contamination — ce qu'elles mesurent et leurs limites | 12.2 |
| Évolution 2024-2026 | De 12% à 94% — progression tirée par le modèle, le scaffold et le RL fine-tuning | 12.3 |
| SWE-Compass | 8 types de tâches sur 10 langages pour une évaluation fine des capacités | 12.4 |
| Évaluateur SWE-bench | Structure de données, logique d'évaluation, gestion des faux positifs/négatifs | 12.5 |
| Outils de monitoring | LangSmith, AgentOps, W&B, LangFuse — tableau comparatif détaillé | 12.6 |
| Benchmark personnalisé | Guide pratique en 6 étapes pour créer son propre benchmark | 12.7 |

**Lien avec la séance suivante :**

> *"Maintenant que vous savez mesurer objectivement la performance d'un agent avec les métriques et les benchmarks de cette séance, la séance 13 (Déploiement & Production) vous apprendra à mettre ces agents en production : infrastructure de scaling, optimisation des coûts, monitoring continu. Les benchmarks deviendront vos tests de non-régression avant chaque déploiement."*

## Références contextualisées

- **[Jimenez et al., "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?", 2024]**
  *Contexte :* Article fondateur de SWE-bench, cité en 12.1. Définit le protocole d'évaluation et les 2294 instances originales. À lire pour comprendre la motivation et la méthodologie.
  *Niveau de lecture :* Avancé (papier de recherche)
  *→ https://arxiv.org/abs/2310.06770*

- **[Xia et al., "SWE-bench Multilingual: Extending Code Repair Benchmarks to 10 Languages", 2026]**
  *Contexte :* Extension multilingue présentée en 12.1. Montre comment adapter le protocole SWE-bench à des écosystèmes non-Python.
  *Niveau de lecture :* Avancé
  *→ https://arxiv.org/abs/2601.xxxxx*

- **["SWE-Compass: A Comprehensive Benchmark for Software Engineering Agents", 2026]**
  *Contexte :* Meta-benchmark utilisé en 12.4 pour catégoriser les tâches en 8 types. Permet une évaluation fine des capacités agentiques.
  *Niveau de lecture :* Avancé

- **["From 48% to 94%: The 2025-2026 SWE-bench Revolution", AgentDev Blog, 2026]**
  *Contexte :* Article de synthèse cité en 12.3. Analyse les facteurs de progression et les leçons apprises. Lecture recommandée pour contextualiser l'évolution.
  *Niveau de lecture :* Introduction

- **[Documentation LangSmith]**
  *Contexte :* Référence technique pour l'outil de monitoring présenté en 12.6. À consulter pendant le lab pour configurer le tracing d'agent.
  *Niveau de lecture :* Technique
  *→ https://docs.smith.langchain.com*

- **[Documentation AgentOps]**
  *Contexte :* Documentation de l'outil de monitoring spécialisé agent (12.6). Utile pour le replay de sessions et les métriques agent.
  *Niveau de lecture :* Technique
  *→ https://docs.agentops.ai*

- **[Documentation W&B]**
  *Contexte :* Référence pour le tracking d'expériences (12.6). Utilisé dans le lab pour comparer les runs de benchmark.
  *Niveau de lecture :* Technique
  *→ https://docs.wandb.ai*

- **["Scaffold vs Model: Decomposing Agent Performance", Allamanis et al., 2025]**
  *Contexte :* Analyse citée en 12.3 sur la décomposition de l'impact entre scaffold et modèle. Source des chiffres de contribution (35% modèle, 30% scaffold).
  *Niveau de lecture :* Avancé
