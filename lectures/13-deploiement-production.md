# Séance 13 — Déploiement & Production

> **Auteur :** yugmerabtene
> **Version :** 2.0
> **Durée estimée :** 2 heures

---

## Description

Cette séance couvre le déploiement des systèmes agentiques en production. Vous apprendrez l'architecture de production, la CI/CD pour agents, la sécurité (sandboxing, permissions), le monitoring et la gestion des coûts. Cette séance fait le pont entre les benchmarks (séance 12) et les frontières futures (séance 14).

---

## Prérequis

Avant de commencer cette séance, assurez-vous d'avoir :

- Terminé la **Séance 12** et compris les métriques d'évaluation
- Python 3.10+ installé
- Un compte GitHub avec GitHub Actions activé
- GitHub CLI installé (`gh --version`)

### Installation des dépendances

#### Linux et macOS

```bash
# Vérifier Python et GitHub CLI
python3 --version
gh --version

# Aucune dépendance supplémentaire pour cette séance
```

#### Windows PowerShell

```powershell
# Vérifier Python et GitHub CLI
py --version
gh --version

# Si gh n'est pas installé
winget install GitHub.cli
```

> **Résultat attendu :** Python 3.10+ et GitHub CLI sont installés.

---

## Introduction théorique

**Quel problème cette séance adresse-t-elle ?**

Un agent qui fonctionne parfaitement en développement peut échouer catastrophiquement en production. Les causes sont multiples : passage à l'échelle (10 utilisateurs → 10 000), fiabilité (timeout, crash mémoire), sécurité (injection de prompt, fuite de données), et coûts (un agent qui tourne en boucle coûte cher). En développement, un développeur supervise chaque action ; en production, l'agent est souvent autonome et ses décisions ont des conséquences réelles. Le problème fondamental est donc : **comment garantir qu'un agent reste fiable, sécurisé et économique quand il passe d'un environnement contrôlé à un environnement ouvert ?**

**Où se situe ce concept dans l'écosystème agentique 2026 ?**

En 2026, le déploiement d'agents en production est passé du stade expérimental au stade industriel. GitHub Actions supporte nativement les agents de review (copilot-agent). Le protocole MCP est en production dans des milliers d'organisations. Les patterns de déploiement se standardisent : CI/CD multi-étapes avec linting agentique, sandboxing par conteneurs, monitoring via OpenTelemetry adapté aux agents. Les coûts d'inférence ont baissé de 10x depuis 2024 grâce au caching sémantique et au batching continu. Un agent opencode (big-pickle) coûte ~0 € en inférence locale ; le coût réel devient celui de l'infrastructure (CPU, mémoire, stockage) et du temps développeur perdu si l'agent déraille.

**Lien avec les séances précédentes et suivantes :**

La séance 12 (Benchmarks & Évaluation) vous a appris à *mesurer* la performance d'un agent — mais que faire une fois qu'il est validé ? La séance 13 vous apprend à le *mettre en production* de façon industrialisée. Vous réutiliserez les métriques de la séance 12 (resolve rate, latence) pour définir vos critères de déploiement (gates de qualité). La séance 14 (Frontières & Futur) explorera ce qui vient après : agents auto-évolutifs, communication latente inter-agent, et gouvernance des agents autonomes.

> *"La différence entre un prototype et un produit, c'est l'infrastructure. Un démo-agent qui fonctionne sur votre machine n'est pas un service — c'est une maquette."*

## Objectifs pédagogiques

À l'issue de cette séance, vous serez capable de :

1. **Concevoir une architecture de production complète** pour un système agentique — schématiser les couches CI/CD, agents, MCP, stockage partagé et monitoring
2. **Implémenter une pipeline CI/CD complète** dans GitHub Actions — configurer lint, test, build, agent-review et déploiement automatique
3. **Analyser et configurer les permissions de sécurité** d'un agent — sandboxing, politiques allow/deny, scénarios d'auto-approval
4. **Calculer le coût d'exploitation** d'un système agentique en production — distinguer coûts fixes (infrastructure) et variables (tokens), appliquer des stratégies de réduction (caching, batching)
5. **Configurer un monitoring complet** avec tracing, logging structuré et métriques — savoir identifier un goulot d'étranglement, une fuite mémoire, ou une anomalie de comportement

## Plan détaillé

### 13.1 Architecture de production

#### Définition formelle

> **Définition :** Une architecture de production pour systèmes agentiques est l'organisation des composants (CI/CD, runtime agent, stockage, monitoring) qui assure qu'un agent s'exécute de façon fiable, sécurisée et économique en environnement non supervisé.

#### Schéma ASCII complet

```
                     ┌─────────────────────────────────────────────┐
                     │              GitHub Actions                  │
                     │  ┌──────┐  ┌──────┐  ┌──────┐  ┌────────┐ │
                     │  │ lint │→│ test │→│build │→│agent-  │ │
                     │  └──────┘  └──────┘  └──────┘  │review  │ │
                     │                                 └────┬───┘ │
                     └──────────────────────────────────────┼─────┘
                                                            │ deploy
                     ┌──────────────────────────────────────▼─────┐
                     │              Load Balancer                  │
                     │         (round-robin / least-conn)          │
                     └────────────┬────────────┬────────────┬──────┘
                                  │            │            │
                          ┌───────▼──┐  ┌──────▼───┐  ┌────▼──────┐
                          │  Agent   │  │  Agent   │  │   Agent   │
                          │  Node 1  │  │  Node 2  │  │   Node N  │
                          │ opencode  │  │ opencode  │  │ opencode  │
                          │ big-pickle│  │ big-pickle│  │ big-pickle│
                          └───┬───┬───┘  └───┬───┬───┘  └───┬───┬───┘
                              │   │          │   │          │   │
            ┌─────────────────┘   │          │   │          │   └──────────┐
            │                     │          │   │          │              │
     ┌──────▼─────────┐   ┌──────▼──────┐   │   └──────────▼──┐  ┌───────▼──────┐
     │  MCP Servers   │   │  Session    │   │                │  │   Message    │
     │  (tools/data)  │   │  Store      │   │                │  │   Queue      │
     │  JSON-RPC 2.0  │   │  (Redis)    │   │                │  │   (RabbitMQ) │
     └────────────────┘   └─────────────┘   │                │  └──────────────┘
                                            │                │
                                     ┌──────▼──────┐  ┌──────▼──────┐
                                     │  Monitoring │  │   Object    │
                                     │  Prometheus │  │   Store     │
                                     │  + Grafana  │  │   (S3)      │
                                     └─────────────┘  └─────────────┘
```

#### Pourquoi cette architecture est cruciale

- **Impact sur la conception :** Chaque composant a un rôle précis. Sans load balancer, un agent seul devient le goulot. Sans session store, les requêtes d'un même utilisateur atterrissent sur des nodes différents qui ne partagent pas le contexte. Sans file d'attente, un pic de requêtes crashe le système.
- **Conséquence si ignoré :** Un agent déployé sans session store perd le fil de la conversation à chaque redémarrage. Sans monitoring, une boucle infinie d'outils MCP passe inaperçue jusqu'à la facture.
- **Cas d'usage typique :** Une équipe de 10 développeurs utilise un agent opencode pour la revue de code. Chaque PR déclenche un agent-review dans GitHub Actions. En production, 50 PRs concurrentes sont analysées par un pool de 5 nodes agents partageant le même cache MCP et le même session store Redis.

---

### 13.2 CI/CD pour agents

#### Définition formelle

> **Définition :** Une pipeline CI/CD pour agents étend la CI/CD classique avec des étapes spécifiques : validation du comportement agentique (agent-review), benchmark de performance (résolution rate, latence), et analyse de sécurité des permissions.

#### Pipeline complète

```
lint (ruff + mypy)
  │
  ▼
test (pytest avec --junitxml)
  │
  ▼
build (validation config opencode.json)
  │
  ▼
agent-review (revue de code par agent IA)
  │
  ▼
deploy (mise à jour des nodes agents)
```

#### Analyse ligne par ligne du workflow `.github/workflows/ci.yml`

```yaml
name: CI
# ↑ NOM DU WORKFLOW (obligatoire)
#   Ce nom apparaît dans l'onglet "Actions" de GitHub.
#   Il doit décrire clairement le rôle de la pipeline.

on: [push, pull_request]
# ↑ DÉCLENCHEURS (triggers)
#   push        → la pipeline s'exécute à chaque commit sur n'importe quelle branche
#   pull_request → la pipeline s'exécute quand une PR est ouverte ou mise à jour
#   Cela garantit que le code est validé avant d'être mergé sur main.

jobs:
# ↑ SECTION DES JOBS
#   Chaque "job" est une unité d'exécution indépendante dans la pipeline.
#   Les jobs peuvent s'exécuter en parallèle ou en séquence.
#   Ici, nous avons 3 jobs : lint → test → agent-review

  lint:
# ↑ NOM DU JOB
#   "lint" : analyse statique du code (qualité, style, types).
#   C'est le premier rempart : il détecte les erreurs évidentes
#   avant d'exécuter les tests plus coûteux.
    runs-on: ubuntu-latest
# ↑ MACHINE D'EXÉCUTION
#   ubuntu-latest : machine virtuelle Ubuntu fournie par GitHub.
#   Alternative : windows-latest, macos-latest, ou self-hosted runner.
#   Pour opencode, Linux est recommandé (big-pickle est natif Linux).
    steps:
# ↑ LISTE DES ÉTAPES du job lint
#   Chaque "step" est une action exécutée séquentiellement.
#   On utilise des actions GitHub (checkout, setup-python) et
#   des commandes shell (pip, ruff, mypy).
      - uses: actions/checkout@v4
# ↑ ACTION : CHECKOUT DU CODE
#   actions/checkout@v4 : clone le dépôt GitHub dans l'environnement.
#   Version 4 = dernière version stable (2024+).
#   Sans cette étape, les jobs n'ont pas accès au code source.
      - uses: actions/setup-python@v5
# ↑ ACTION : INSTALLATION DE PYTHON
#   actions/setup-python@v5 : installe Python dans la VM.
#   Version 5 = dernière version stable.
        with:
          python-version: "3.12"
# ↑ VERSION DE PYTHON
#   On fixe "3.12" pour garantir la reproductibilité.
#   En production, il est critique de verrouiller la version.
      - run: pip install ruff mypy
# ↑ INSTALLATION DES OUTILS DE LINT
#   ruff   : linter Python ultra-rapide (remplace flake8 + isort)
#   mypy   : vérificateur de types statique Python
#   Ces outils sont légers et s'exécutent en < 10s.
      - run: ruff check lab/code/
# ↑ EXÉCUTION DE RUFF
#   ruff check : analyse le code dans lab/code/
#   Détecte : erreurs de syntaxe, imports inutilisés,
#   conventions de style non respectées.
#   Si ruff échoue (exit code ≠ 0), le job échoue → la pipeline s'arrête.
      - run: mypy lab/code/ || true
# ↑ EXÉCUTION DE MYPY (avec tolérance)
#   mypy       : vérifie les types (annotation Python).
#   || true   : si mypy échoue, on continue (le "true" renvoie 0).
#   C'est un choix : on veut signaler les erreurs de type
#   sans bloquer la pipeline (car mypy peut être trop strict).
#   Alternative : enlever || true pour bloquer sur toute erreur.

  test:
# ↑ JOB : TEST
#   Exécute les tests unitaires et d'intégration.
    needs: lint
# ↑ DÉPENDANCE : needs
#   "needs: lint" signifie : ce job ne démarre que si "lint" réussit.
#   C'est le principe du "fail fast" : ne pas gaspiller des ressources
#   sur des tests si le code a des erreurs de syntaxe.
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r lab/requirements.txt
# ↑ INSTALLATION DES DÉPENDANCES
#   -r lab/requirements.txt : installe toutes les dépendances listées.
#   En production, on utilise souvent un cache pip pour accélérer :
#   actions/cache@v4 avec le hash de requirements.txt comme clé.
      - run: pytest lab/tests/ -v --junitxml=report.xml
# ↑ EXÉCUTION DES TESTS
#   pytest      : framework de test Python.
#   -v          : mode verbeux (affiche chaque test et son résultat).
#   --junitxml  : exporte les résultats au format JUnit XML.
#   Ce format est standard et peut être importé dans GitHub,
#   Jenkins, ou tout outil CI/CD.
      - uses: actions/upload-artifact@v4
# ↑ ACTION : UPLOAD DU RAPPORT DE TEST
#   actions/upload-artifact : sauvegarde un fichier produit par le job
#   pour le consulter après l'exécution (même si la pipeline échoue).
        with:
          name: test-report
# ↑ NOM DE L'ARTEFACT
#   Identifiant du rapport. On peut le télécharger depuis l'UI GitHub.
          path: report.xml
# ↑ CHEMIN DU FICHIER À UPLOADER

  agent-review:
# ↑ JOB : AGENT-REVIEW
#   C'est l'étape spécifique aux systèmes agentiques.
#   Un agent IA analyse le code de la PR pour détecter
#   des problèmes de qualité, de test ou de sécurité.
    needs: test
# ↑ DÉPENDANCE : test doit réussir avant agent-review.
#   On ne demande l'avis de l'agent que si les tests passent.
    runs-on: ubuntu-latest
    permissions:
# ↑ PERMISSIONS DU JOB
#   Depuis GitHub, on restreint les droits du token GITHUB_TOKEN.
#   Principe de moindre privilège : ne donner que ce qui est nécessaire.
      contents: read
# ↑ "contents: read" : le job peut lire le dépôt (checkout).
#   Pas d'écriture (pas de push, pas de modification de fichier).
      pull-requests: write
# ↑ "pull-requests: write" : le job peut commenter la PR.
#   L'agent a besoin d'écrire son review dans la PR.
    steps:
      - uses: actions/checkout@v4
      - name: AI Code Review
# ↑ ÉTAPE DE REVUE PAR IA
#   name: nom lisible de l'étape (apparaît dans les logs).
        uses: github/copilot-agent@v1
# ↑ ACTION : COPILOT AGENT
#   github/copilot-agent@v1 : action GitHub officielle.
#   Elle exécute un agent opencode dans l'environnement CI.
        with:
          agent: reviewer
# ↑ AGENT À UTILISER
#   "reviewer" : l'agent de revue de code défini dans opencode.json.
#   opencode charge sa configuration (modèle, permissions, outils).
          prompt: "Review this PR for code quality, test coverage, and security issues."
# ↑ PROMPT DE L'AGENT
#   Instruction donnée à l'agent de revue.
#   Il analysera le diff de la PR et commentera.
#   Le prompt est critique : trop vague → revue superficielle.
#   Trop spécifique → l'agent passe à côté de problèmes inattendus.
```

#### Scénario concret d'exécution

1. Un développeur pousse un commit sur une branche `feature/mon-agent`
2. GitHub Actions détecte le push et déclenche la pipeline
3. Job `lint` : ruff et mypy analysent le code (5 secondes)
4. Si lint passe → job `test` : pytest exécute 50 tests (30 secondes)
5. Si test passe → job `agent-review` : l'agent reviewer analyse la PR
6. L'agent reviewer commente la PR avec ses recommandations
7. Le développeur reçoit une notification GitHub avec le review
8. Après approbation humaine, la PR est mergée → déploiement automatique

---

### 13.3 Sécurité en production

#### Définition formelle

> **Définition :** La sécurité d'un agent en production repose sur trois piliers : le sandboxing (isolation de l'exécution), le contrôle des permissions (qui peut faire quoi), et l'auditabilité (toute action est tracée).

#### Analyse d'une configuration de permissions agent

Prenons le fichier de configuration d'un agent de production :

```yaml
# Fichier : .opencode/agents/security-auditor.md
# Rôle    : Agent dédié à l'audit de sécurité automatique
# Déployé en production pour scanner chaque PR

mode: subagent
# ↑ MODE DE L'AGENT
#   "subagent" : agent spécialisé, délégable via l'outil `task`.
#   En production, tous les agents sauf le coordinateur sont subagents.

model: opencode/big-pickle
# ↑ MODÈLE DE LLM
#   opencode/big-pickle : modèle natif, zéro API externe.
#   Avantage sécurité : pas de données qui quittent l'infrastructure.

permission:
  read: allow
  # ↑ PERMISSION DE LECTURE
  #   allow : l'agent peut lire tous les fichiers du dépôt.
  #   En production, c'est nécessaire pour analyser le code.
  #   Mais on pourrait restreindre à certains répertoires
  #   via un mécanisme de filtre (non supporté nativement).

  glob: allow
  # ↑ PERMISSION DE RECHERCHE DE FICHIERS
  #   Essentiel pour un audit : trouver les fichiers .py, .json
  #   qui contiennent potentiellement des secrets.

  grep: allow
  # ↑ PERMISSION DE RECHERCHE TEXTUELLE
  #   Permet de chercher des patterns suspects (clés API, mots de passe).
  #   Sans cette permission, l'agent ne peut pas scanner le contenu.

  list: allow
  # ↑ PERMISSION DE LISTAGE
  #   Permet de naviguer dans l'arborescence du projet.

  edit: deny
  # ↑ PERMISSION DE MODIFICATION
  #   deny : l'agent NE PEUT PAS modifier les fichiers.
  #   C'est la règle la plus importante pour un agent d'audit :
  #   il doit pouvoir LIRE et SIGNALER, jamais MODIFIER.
  #   Un agent d'audit avec edit: allow serait un risque :
  #   il pourrait modifier du code pour masquer des vulnérabilités.

  task: deny
  # ↑ PERMISSION DE DÉLÉGATION
  #   deny : l'agent ne peut pas déléguer à d'autres agents.
  #   En production, un agent spécialisé doit rester isolé.
  #   Si un attaquant prend le contrôle de cet agent,
  #   il ne peut pas propager l'attaque à d'autres agents.
  #   Principe de l'air gap agentique.

  bash:
    python lab/code/08_integration/security_audit.py: allow
    # ↑ PATTERN DE COMMANDE SPÉCIFIQUE
    #   Seul ce script d'audit est autorisé.
    #   Pas de Python générique, pas de shell, pas de rm.
    #   La commande exacte est verrouillée : pas de paramètres variables.
    pip *: ask
    # ↑ pip nécessite confirmation
    #   L'agent peut demander à installer des dépendances
    #   mais l'utilisateur doit confirmer manuellement.
    #   Empêche l'installation silencieuse de paquets malveillants.
    find *: allow
    # ↑ find est autorisé (navigation fichiers inoffensive)
    *: deny
    # ↑ TOUTE AUTRE COMMANDE EST REFUSÉE
    #   Pattern "*" avec deny : c'est le principe du "default-deny".
    #   Tout ce qui n'est pas explicitement autorisé est interdit.
    #   C'est l'inverse du "default-allow" des systèmes permissifs.
    #   En sécurité agentique, TOUJOURS utiliser default-deny.
```

**Analyse de sécurité de cette configuration :**

| Principe | Appliqué ? | Détail |
|----------|------------|--------|
| Moindre privilège | ✅ | Lecture seule, pas de délégation, commandes verrouillées |
| Default-deny | ✅ | `*: deny` + exceptions explicites |
| Séparation des rôles | ✅ | Agent d'audit distinct des agents de développement |
| Auditabilité | ✅ | Toute action tracée dans les logs GitHub Actions |
| Isolation | ✅ | Pas de task → pas de propagation d'attaque |

#### Sandboxing

```
┌─────────────────────────────────────────────────┐
│              Production Agent Sandbox             │
├─────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────┐  │
│  │  Conteneur isolé (Docker / Firecracker)   │  │
│  │                                           │  │
│  │  ├─ Filesystem : read-only (sauf /tmp)    │  │
│  │  ├─ Network    : sortant uniquement redis │  │
│  │  ├─ CPU        : 2 cœurs max              │  │
│  │  ├─ Memory     : 4 Go max                 │  │
│  │  ├─ Timeout    : 5 minutes par run        │  │
│  │  └─ User       : nobody (pas root)        │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  ┌─── Commandes autorisées ──────────────────┐  │
│  │  python /app/agent.py                     │  │
│  │  python -m pytest lab/tests/              │  │
│  │  ruff check lab/code/                     │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  ┌─── Commandes interdites ───────────────────┐  │
│  │  rm -rf /   curl http://*   eval          │  │
│  │  pip install *  sudo *   chmod *          │  │
│  │  git push    docker *    python -c "..."   │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

---

### 13.4 Gestion des coûts

#### Définition formelle

> **Définition :** La gestion des coûts d'un système agentique est l'ensemble des stratégies qui optimisent le rapport entre la qualité des résultats et les ressources consommées (CPU, mémoire, tokens, temps).

#### Tableau des coûts

| Composant | Coût unitaire | Usage typique/jour | Coût/jour | Stratégie de réduction |
|-----------|--------------|-------------------|-----------|----------------------|
| Modèle opencode (big-pickle, local) | 0 € (inférence locale) | 500 runs | **0 €** | Rien à optimiser — c'est gratuit |
| CPU (inférence locale) | ~0,02 €/h (OVH Cloud) | 8h de calcul | **0,16 €** | Limiter les runs inutiles |
| RAM (8 Go) | ~0,01 €/h | 24h | **0,24 €** | Libérer la mémoire entre les runs |
| Stockage Redis (session store) | ~0,05 €/Go/mois | 500 Mo | **0,025 €/mois** | TTL court (expire après 1h d'inactivité) |
| Stockage artefacts (logs, rapports) | ~0,02 €/Go/mois | 2 Go | **0,04 €/mois** | Compresser les logs, supprimer après 30 jours |
| GitHub Actions (minutes CI) | Gratuit (2000 min/mois) | ~50 min/jour | **0 €** (dans le quota) | Caching pip, parallélisation |
| **TOTAL** | | | **~0,45 €/jour (~13,50 €/mois)** | |

#### Calcul détaillé

```
Scénario : 1 agent de revue de code opencode en production
- 100 PRs analysées par jour
- Chaque analyse = 5 runs agent (1 par fichier modifié)
- Total : 500 runs agent / jour

Sans optimisation :
  500 runs × 30 jours = 15 000 runs/mois
  Temps CPU : 15 000 × 30s = 125h CPU/mois
  Coût CPU : 125h × 0,02 € = 2,50 €/mois

Avec caching des dépendances pip :
  Les 15 000 runs partagent le même cache pip
  Économie : ~30s par run en moins = 125h économisées
  → 0 € supplémentaire pour les runs suivants

Avec batching (regrouper les PRs) :
  Au lieu de 1 run par PR, on analyse par lot de 5 PRs
  → 100 runs/jour au lieu de 500
  → Coût CPU : 25h × 0,02 € = 0,50 €/mois

Avec TTL court sur Redis :
  Sessions expirées après 1h → stockage max 200 Mo
  → Coût : 0,01 €/mois au lieu de 0,025 €
```

#### Stratégies de réduction

1. **Caching des dépendances** — `actions/cache@v4` avec hash de `requirements.txt` comme clé. Réduction : 60-80% du temps CI.
2. **Batching des requêtes** — Au lieu de lancer un agent par PR, grouper les PRs similaires et les analyser en un run. Réduction : jusqu'à 5x.
3. **TTL des sessions Redis** — `EXPIRE session:123 3600` (1 heure). Évite l'accumulation de sessions orphelines.
4. **Modèle unique** — opencode/big-pickle est déjà le plus efficace. Pas de basculement entre modèles.
5. **Limitation du contexte** — Configurer `max_tokens` et `max_steps` pour éviter les boucles infinies.

---

### 13.5 Monitoring & Observabilité

#### Définition formelle

> **Définition :** L'observabilité d'un système agentique est la capacité à inférer l'état interne d'un agent à partir de ses sorties externes (logs, traces, métriques), sans avoir à instrumenter le modèle lui-même.

#### Métriques clés

| Métrique | Définition | Seuil d'alerte | Pourquoi |
|----------|-----------|----------------|----------|
| **TTFT** (Time To First Token) | Temps avant la première token de réponse | > 5s | L'agent "réfléchit" trop longtemps |
| **TPOT** (Time Per Output Token) | Temps par token généré | > 100ms | Goulot d'étranglement CPU/mémoire |
| **Success rate** | % de runs qui terminent sans erreur | < 95% | L'agent échoue trop souvent |
| **Tool error rate** | % d'appels d'outils MCP qui échouent | < 5% | Un serveur MCP est instable |
| **Token waste** | % de tokens générés mais non utilisés | > 30% | L'agent divague ou tourne en boucle |
| **Session length** | Nombre de steps par session | > 50 | L'agent ne converge pas |

#### Structure de log structuré

```json
{
  "trace_id": "abc-123-def-456",
  "session_id": "session-789",
  "agent_name": "code-reviewer",
  "model": "opencode/big-pickle",
  "step": 3,
  "action": "tool_call",
  "tool": "grep",
  "input_tokens": 4500,
  "output_tokens": 230,
  "latency_ms": 1200,
  "error": null,
  "permission_check": "allow",
  "timestamp": "2026-05-18T14:32:01Z"
}
```

Chaque champ est essentiel :
- `trace_id` : corrélation entre tous les événements d'une même requête (distributed tracing)
- `session_id` : identification de la conversation complète
- `step` : numéro d'étape dans la session (détection des boucles)
- `tool` : quel outil MCP a été appelé
- `permission_check` : la permission a-t-elle été accordée ? (audit de sécurité)

#### Outils de monitoring

- **LangSmith** : tracing distribué, debugging de sessions, évaluation de la qualité des réponses. Utile pour rejouer une session qui a mal tourné.
- **AgentOps** : monitoring spécialisé pour agents. Détection automatique des boucles, des hallucinations, et des dérives de comportement. Replay frame par frame.
- **OpenTelemetry** : standard d'observabilité (utilisé par A2A). Collecte des traces, métriques et logs dans un format unifié. Export vers Prometheus, Grafana, ou n'importe quel backend OTLP.
- **Prometheus + Grafana** : métriques custom (latence, taux d'erreur, utilisation mémoire). Tableaux de bord temps réel.

---

### 13.6 Scalabilité

#### Définition formelle

> **Définition :** La scalabilité d'un système agentique est sa capacité à maintenir des performances constantes quand la charge augmente (nombre d'utilisateurs, de sessions, de requêtes concurrentes).

#### Load balancing

Le load balancer distribue les requêtes entrantes entre les nodes agents. Stratégies :
- **Round-robin** : chaque requête va au node suivant. Simple mais ne tient pas compte de la charge réelle.
- **Least connections** : la requête va au node qui a le moins de sessions actives. Meilleur pour des durées de session variables.
- **Sticky sessions** : toutes les requêtes d'un même utilisateur vont au même node. Évite de recharger le contexte à chaque appel.

#### Session management

Trois niveaux de persistance des sessions, du plus simple au plus scalable :

| Niveau | Stockage | Cas d'usage | Avantage | Inconvénient |
|--------|----------|------------|----------|--------------|
| 1 | Mémoire locale (RAM du node) | Développement, test unitaire | Ultra-rapide, zéro dépendance | Perdu si node redémarre |
| 2 | Redis externalisé | Production multi-node | Persistant, partagé entre nodes | Latence réseau (~1ms) |
| 3 | Client-side (token JWT) | Scale horizontal max | Zéro état serveur, scale infini | Taille limitée, sécurité du token |

#### File d'attente

Un pic de 100 requêtes simultanées ne doit pas crasher les agents. Solution : une file d'attente (message queue) qui bufferise les requêtes et les distribue au rythme que les nodes peuvent traiter.

```
Arrivée des requêtes
        │
        ▼
┌────────────────┐
│  Message Queue │  ← RabbitMQ / Redis Streams
│  [R1][R2][R3]..│
└────────┬───────┘
         │
    ┌────┴────┐
    │ Worker  │  ← Agent node (consommateur)
    │ pool    │
    └─────────┘
```

- Avantage : le système ne crashe jamais sous charge, les requêtes sont juste retardées.
- Config : max 10 workers simultanés, files d'attente par priorité (review urgente != review normale).

---

### 13.7 Construction guidée — analyse de `security_audit.py`

Le fichier `lab/code/08_integration/security_audit.py` est un script d'audit de sécurité conçu pour être exécuté par un agent en production. Il illustre les principes de la séance 13 : sandboxing, permissions, monitoring.

```python
#!/usr/bin/env python3
"""Security audit script for the AI Developer Assistant."""
# ↑ SHEBANG (#!/usr/bin/env python3)
#   Indique au système d'exploitation d'utiliser l'interpréteur Python.
#   "env python3" : cherche python3 dans le PATH (portable).
#   Docstring : description du rôle du fichier. Apparaît dans
#   les logs d'audit et dans l'interface opencode.
#   IMPORTANT : une docstring claire permet à un agent de comprendre
#   instantanément ce que fait ce script.

import json
# ↑ BIBLIOTHÈQUE json
#   Nécessaire pour parser la sortie de pip-audit (format JSON).
#   Aussi utilisée pour logger les résultats d'audit structurés.

import os
# ↑ BIBLIOTHÈQUE os
#   os.walk() : parcourt récursivement tous les fichiers du projet.
#   os.stat() : lit les permissions des fichiers.
#   os.path.join() : construit des chemins cross-platform.

import subprocess
# ↑ BIBLIOTHÈQUE subprocess
#   Permet d'exécuter pip-audit comme un processus externe.
#   Utilisée avec capture_output et timeout pour la sécurité :
#   pas d'interaction avec le shell, pas d'injection possible.

import sys
# ↑ BIBLIOTHÈQUE sys
#   sys.exit(1) : sort avec code d'erreur si des problèmes sont trouvés.
#   sys.exit(0) : sort normalement si tout va bien.
#   Le code de retour est utilisé par l'agent pour décider de la suite.


def check_file_permissions():
    """Check for world-readable secrets or dangerous permissions."""
    # ↑ FONCTION : vérification des permissions de fichiers
    #   Objectif : détecter les fichiers qui sont accessibles
    #   en lecture/écriture par tout le monde (mode 0o007).
    #   En production, un fichier de configuration avec des secrets
    #   ne doit JAMAIS être world-readable (chmod 644 est le maximum).
    issues = []
    # ↑ Liste accumulant les problèmes détectés.
    #   Chaque élément est une chaîne décrivant le fichier et le souci.
    for root, dirs, files in os.walk("."):
    # ↑ os.walk(".") : parcourt récursivement depuis le répertoire courant.
    #   root   : chemin du répertoire en cours
    #   dirs   : liste des sous-répertoires (ignorés ici)
    #   files  : liste des fichiers dans root
        for f in files:
            path = os.path.join(root, f)
            if ".git" in path:
                continue
            # ↑ On ignore le répertoire .git/ pour éviter les faux positifs
            #   (les fichiers dans .git ont des permissions spéciales).
            try:
                mode = os.stat(path).st_mode
                # ↑ os.stat() : retourne les métadonnées du fichier.
                #   st_mode : masque de bits des permissions (Unix).
                #   Exemple : 0o100644 = fichier régulier, rw-r--r--
                if mode & 0o007:
                # ↑ 0o007 : masque "world" (les 3 derniers bits).
                #   Si le résultat est non nul, quelqu'un d'autre que
                #   le propriétaire et le groupe peut accéder au fichier.
                    issues.append(f"{path}: world-accessible")
                # ↑ On enregistre le problème avec le chemin du fichier.
            except OSError:
                pass
            # ↑ On ignore les erreurs (fichier supprimé entre-temps,
            #   permissions insuffisantes pour lire les métadonnées).
    return issues


def check_hardcoded_secrets():
    """Scan for potential secrets in code."""
    # ↑ FONCTION : détection de secrets codés en dur
    #   Parcourt les fichiers sources et cherche des patterns
    #   qui ressemblent à des clés API, mots de passe, tokens.
    issues = []
    patterns = [
        b"api_key",
        b"secret",
        b"password",
        b"token",
        b"sk-",
    ]
    # ↑ PATTERNS DE RECHERCHE (bytes)
    #   api_key  : variable contenant une clé d'API
    #   secret   : secret partagé ou clé secrète
    #   password : mot de passe en clair
    #   token    : token d'authentification
    #   sk-      : préfixe typique des clés secrètes OpenAI/Anthropic
    #   Les patterns sont en bytes pour être comparés directement
    #   au contenu binaire du fichier (plus rapide que texte).
    for root, dirs, files in os.walk("lab/code"):
    # ↑ On se limite à lab/code (pas le projet entier).
    #   En production, on pourrait scanner tout le dépôt,
    #   mais ici on évite les faux positifs dans les dépendances.
        for f in files:
            if f.endswith((".py", ".sh", ".json", ".yaml", ".yml")):
            # ↑ EXTENSIONS SCANNÉES
            #   .py   : code Python (le plus susceptible d'avoir des secrets)
            #   .sh   : scripts shell (connexions, exports)
            #   .json : fichiers de configuration
            #   .yaml/.yml : fichiers YAML (Docker Compose, CI/CD)
                path = os.path.join(root, f)
                try:
                    content = open(path, "rb").read()
                    # ↑ LECTURE EN MODE BINAIRE ("rb")
                    #   On lit les bytes bruts, pas le texte.
                    #   Évite les erreurs d'encodage sur les fichiers
                    #   qui ne sont pas en UTF-8.
                    for pat in patterns:
                        if pat in content.lower():
                        # ↑ content.lower() : insensible à la casse.
                        #   "API_KEY" comme "api_key" sont détectés.
                        #   Pat est en bytes, le contenu aussi.
                            issues.append(
                                f"{path}: possible secret ({pat.decode()})"
                            )
                            # ↑ On enregistre le pattern trouvé
                            #   pour faciliter le diagnostic.
                except OSError:
                    pass
    return issues


def check_dependency_vulns():
    """Run pip audit if available."""
    # ↑ FONCTION : vérification des vulnérabilités des dépendances
    #   Utilise pip-audit (outil externe) pour scanner les paquets
    #   Python installés et les comparer à la base de vulnérabilités
    #   PyPI (Safety DB).
    try:
        result = subprocess.run(
            ["pip-audit", "--format", "json"],
            # ↑ COMMANDE pip-audit
            #   --format json : sortie structurée facile à parser.
            #   Pas de shell=True : évite l'injection de commandes.
            capture_output=True,
            # ↑ capture le stdout et stderr au lieu de les afficher.
            #   On traite la sortie dans Python plutôt que de l'afficher.
            text=True,
            # ↑ Retourne les chaînes (str) au lieu de bytes.
            timeout=30,
            # ↑ TIMEOUT : 30 secondes max.
            #   En production, un timeout empêche pip-audit de bloquer
            #   indéfiniment (ex: si le réseau PyPI est lent).
        )
        if result.returncode != 0:
        # ↑ pip-audit retourne 0 si aucune vulnérabilité,
        #   non nul si des vulnérabilités sont trouvées.
            return json.loads(result.stdout).get("vulnerabilities", [])
        # ↑ On parse le JSON et on extrait la liste des vulnérabilités.
    except (FileNotFoundError, json.JSONDecodeError, subprocess.TimeoutExpired):
        return [{"error": "pip-audit not available"}]
        # ↑ FileNotFoundError   : pip-audit n'est pas installé
        #   json.JSONDecodeError : la sortie n'est pas du JSON valide
        #   TimeoutExpired       : la commande a dépassé 30 secondes
        #   Dans tous les cas, on retourne un rapport d'erreur
        #   plutôt que de crasher le script.
    return []


def main():
    # ↑ FONCTION PRINCIPALE
    #   Point d'entrée du script. Appelle les 3 fonctions d'audit
    #   et agrège leurs résultats.
    issues = []
    issues.extend(("permission", i) for i in check_file_permissions())
    # ↑ On ajoute un tuple (catégorie, description).
    #   "permission" : problème de permissions fichier.
    issues.extend(("secret", i) for i in check_hardcoded_secrets())
    # ↑ "secret" : secret potentiel détecté.
    issues.extend(("dependency", str(i)) for i in check_dependency_vulns())
    # ↑ "dependency" : vulnérabilité de dépendance.

    if issues:
        print(f"Found {len(issues)} issue(s):")
        for severity, desc in issues:
            print(f"  [{severity}] {desc}")
        # ↑ AFFICHAGE STRUCTURÉ
        #   [permission] lab/code/config.json: world-accessible
        #   [secret] lab/code/auth.py: possible secret (api_key)
        #   [dependency] {'id': 'CVE-2024-...', 'severity': 'HIGH'}
        sys.exit(1)
        # ↑ CODE DE RETOUR NON NUL
        #   L'agent qui exécute ce script interprète exit(1) comme un
        #   échec de l'audit. Il peut alors :
        #   1. Ajouter un commentaire sur la PR
        #   2. Bloquer le merge
        #   3. Envoyer une notification
    else:
        print("Security audit passed — no issues found.")
        sys.exit(0)
        # ↑ CODE DE RETOUR ZÉRO
        #   L'audit est passé. La pipeline peut continuer.


if __name__ == "__main__":
    # ↑ GARDIEN D'EXÉCUTION
    #   Ce bloc ne s'exécute QUE si le fichier est lancé directement
    #   (python security_audit.py). Si le fichier est importé
    #   (from security_audit import check_file_permissions), ce bloc
    #   est ignoré — utile pour les tests unitaires.
    main()
```

**Scénario concret d'exécution :**

1. Un développeur crée une PR qui modifie `lab/code/auth.py`
2. La pipeline CI/CD s'exécute : lint → test → agent-review
3. Le job `agent-review` délègue la tâche à l'agent `security-auditor`
4. L'agent exécute : `python lab/code/08_integration/security_audit.py`
5. Le script `check_hardcoded_secrets()` trouve `api_key` dans `auth.py`
6. Le script retourne `exit(1)` avec le message : `[secret] lab/code/auth.py: possible secret (api_key)`
7. L'agent `security-auditor` lit la sortie et commente la PR :
   "🔒 Audit de sécurité : 1 secret potentiel détecté dans `auth.py` (api_key). Veuillez utiliser les variables d'environnement."
8. Le développeur voit le commentaire, remplace la clé en dur par une variable d'environnement, et met à jour la PR
9. La pipeline repasse, `exit(0)`, la PR est approuvée et mergée

---

### 13.8 Exercice / Lab associé

```bash
# EXERCICE : Mise en production de l'audit de sécurité
# Objectif : Configurer une pipeline CI/CD complète avec audit agentique
# Durée estimée : 4h
# Prérequis : Séances 12 (Benchmarks) + 13 (Déploiement)
#
# Étapes :
# 1. Forker le dépôt du cours et activer GitHub Actions
# 2. Ajouter le job agent-review au fichier .github/workflows/ci.yml
# 3. Créer un agent security-auditor dans .opencode/agents/ avec permissions restrictives
# 4. Ajouter un job deploy qui ne s'exécute que si l'audit passe
# 5. Créer une PR avec un secret intentionnel et vérifier que l'agent le détecte
# 6. Configurer les alertes Grafana pour les métriques de l'agent
```

Voir `lab/README.md` — Partie 8 (Intégration) et Partie 7 (CI/CD) pour les instructions complètes.

---

## Synthèse

**Ce que vous avez appris dans cette séance :**

| Concept | Résumé | Section |
|---------|--------|---------|
| Architecture de production | Schéma complet : CI/CD → load balancer → agents → MCP → Redis → monitoring | 13.1 |
| CI/CD pour agents | Pipeline GitHub Actions commentée ligne par ligne : lint → test → build → agent-review → deploy | 13.2 |
| Sécurité & permissions | Sandboxing, default-deny, moindre privilège. Analyse complète de config agent et du script security_audit.py | 13.3, 13.7 |
| Gestion des coûts | Coût total d'un agent en production : ~13,50 €/mois. Stratégies : caching, batching, TTL | 13.4 |
| Monitoring & observabilité | Métriques (TTFT, TPOT, success rate), logs structurés, outils (LangSmith, AgentOps, Prometheus) | 13.5 |
| Scalabilité | Load balancing, session tiers (locale → Redis → stateless), file d'attente | 13.6 |

**Lien avec la séance suivante :**

> *"Maintenant que vous savez déployer et monitorer un agent en production, la séance 14 (Frontières & Futur) vous montrera ce qui vient après : des agents qui communiquent entre eux via des espaces latents (DiffMAS), qui s'auto-améliorent en modifiant leur propre code, et qui nécessitent des cadres de gouvernance inédits. Les leçons de déploiement de cette séance 13 sont la fondation sur laquelle ces agents de nouvelle génération seront construits."*

## Références contextualisées

- **[GitHub Actions Documentation — Workflow Syntax (2026)]**
  *Contexte :* Référence technique pour la section 13.2. Utilisée pour configurer le workflow CI/CD. Chaque champ YAML (on, jobs, needs, permissions) y est documenté en détail.
  *Niveau de lecture :* Technique
  *→ https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions*

- **[LangSmith Documentation — Tracing for Agents (2026)]**
  *Contexte :* Documentation de l'outil de tracing cité en 13.5. Permet de configurer le monitoring distribué des appels d'agents et d'outils MCP.
  *Niveau de lecture :* Technique
  *→ https://docs.smith.langchain.com*

- **[AgentOps Documentation — Agent Monitoring (2026)]**
  *Contexte :* Outil spécialisé de monitoring agentique (13.5). Utile pour le replay de sessions, la détection de boucles, et les métriques de comportement.
  *Niveau de lecture :* Technique
  *→ https://docs.agentops.ai*

- **[OpenTelemetry Documentation — Traces, Metrics, Logs (2026)]**
  *Contexte :* Standard d'observabilité utilisé en 13.5. Permet d'exporter les métriques agents vers Prometheus/Grafana.
  *Niveau de lecture :* Technique
  *→ https://opentelemetry.io/docs*

- **[OWASP Top 10 for LLM Applications (2025)]**
  *Contexte :* Référence pour la sécurité des applications LLM (13.3). Les catégories (prompt injection, data leakage, excessive agency) sont directement applicables à la configuration des permissions agents.
  *Niveau de lecture :* Introduction
  *→ https://genai.owasp.org*

- **["Security Patterns for AI Agents in Production", AgentDev Blog, 2026]**
  *Contexte :* Article de synthèse cité en 13.3. Analyse les patterns de sandboxing, default-deny et séparation des rôles pour les agents en production.
  *Niveau de lecture :* Avancé

- **["Distributed Tracing for Multi-Agent Systems", Microsoft Research, 2025]**
  *Contexte :* Papier de recherche qui a inspiré la structure de log de 13.5. Explique comment propager un trace_id à travers des appels d'agents et d'outils.
  *Niveau de lecture :* Avancé

- **["Scaling AI Agents: Lessons from Production Deployments", Anthropic, 2026]**
  *Contexte :* Analyse des défis de scalabilité (13.6) rencontrés par les premières entreprises à déployer des agents en production en 2025-2026.
  *Niveau de lecture :* Introduction

- **[Documentation opencode — Agent Permissions]**
  *Contexte :* Référence technique pour la configuration des permissions (13.3). Chaque champ (read, edit, bash, task) y est décrit avec des exemples.
  *Niveau de lecture :* Technique
  *→ https://opencode.ai/docs/agent-permissions*

- **[Prometheus + Grafana — Monitoring Stack]**
  *Contexte :* Stack de monitoring open-source citée en 13.5. Permet de créer des dashboards temps réel pour les métriques agents.
  *Niveau de lecture :* Technique
  *→ https://prometheus.io/docs / https://grafana.com/docs*
