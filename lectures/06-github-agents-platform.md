# Séance 6 — GitHub Agents & Platform

> **Auteur :** yugmerabtene
> **Version :** 2.0
> **Durée estimée :** 3 heures

---

## Description

Cette séance couvre l'intégration des agents dans la plateforme GitHub. Vous apprendrez à configurer des custom agents, utiliser les hooks de cycle de vie, gérer les sessions, et intégrer MCP dans les workflows GitHub Actions. Cette séance fait le pont entre A2A (séance 5) et LangGraph (séance 7).

---

## Prérequis

Avant de commencer cette séance, assurez-vous d'avoir :

- Terminé la **Séance 5** et compris le protocole A2A
- Python 3.10+ installé
- Un compte GitHub
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

### 1. Quel est le problème fondamental ?

Les agents de code autonomes — comme ceux que nous avons vus avec opencode dans les séances précédentes — doivent s'intégrer dans le **workflow GitHub** existant : ouvrir des issues, créer des pull requests, passer la CI/CD, solliciter des reviews, merger. Sans cette intégration, un agent reste un outil isolé : il génère du code que l'humain doit manuellement transformer en PR. Le problème est donc : **comment brancher un agent directement dans le cycle de vie d'un dépôt GitHub** (issue → PR → review → merge → déploiement) ?

Un second problème est celui de la **coordination multi-agent**. Un agent seul ne peut pas tout faire : coder, tester, reviewer, déployer, monitorer. GitHub Agents introduit une plateforme où des agents spécialisés collaborent, avec un système de mémoire partagée, de hooks de cycle de vie, et de gouvernance centralisée. C'est le passage d'un agent isolé à une **équipe agentique** intégrée dans la plateforme de développement.

### 2. Contexte dans l'écosystème 2026

GitHub Copilot a connu une évolution rapide entre 2024 et 2026 :

| Phase | 2024 | 2025 | 2026 |
|-------|------|------|------|
| Capacité | Autocomplétion | Chat + Agent | Plateforme multi-agent |
| Modèle | Codex / GPT-4 | GPT-4o / Claude 3.5 | Model picker (auto/premium) |
| Review | Manuelle | Copilot Code Review | Self-review automatique |
| Custom agents | — | Beta | `.github/agents/` stable |
| Session | Locale | Cloud + CLI | Cloud ↔ CLI handoff |
| Memory | Aucune | Session | Session + Agent + Plan |
| MCP | — | — | `.github/mcp.json` |
| Concurrence | — | — | Multi-session + fork |

En 2026, GitHub Agents n'est plus un simple outil de complétion : c'est une **plateforme agentique complète** avec des agents customisables, de la mémoire partagée, des serveurs MCP, et une gouvernance enterprise. Des organisations comme Shopify, Airbnb, et Mercedes-Benz déploient des flottes de 50+ agents GitHub pour automatiser leur cycle de développement.

### 3. Lien avec les séances précédentes et suivantes

- **Séance 4 (MCP)** : Les serveurs MCP configurés dans `.github/mcp.json` sont les outils que les GitHub Agents invoquent. Vous avez appris à construire un serveur MCP — vous allez maintenant le brancher sur la plateforme GitHub.
- **Séance 5 (A2A)** : A2A définit comment des agents communiquent entre organisations. GitHub Agents utilise un modèle similaire pour la communication entre agents GitHub via les `sub_agents` et le handoff cloud↔CLI. La différence : A2A est un standard inter-organisation, GitHub Agents est une plateforme unifiée intra-organisation.
- **Séance 7 (LangGraph)** : GitHub Agents orchestre des workflows linéaires (issue → PR → merge). LangGraph ajoutera des graphes d'état cycliques, des boucles de rétroaction, et du branching conditionnel. La plateforme GitHub est le cas d'usage pratique ; LangGraph en est la généralisation théorique.

> *"Dans la séance 5, vous avez vu comment des agents peuvent collaborer via le protocole A2A. Dans cette séance 6, vous allez déployer ces agents directement dans GitHub — issues, PRs, CI/CD. Dans la séance 7, vous orchestrerez ces mêmes workflows avec LangGraph."*

---

## Objectifs pédagogiques

À l'issue de cette séance, vous serez capable de :

1. **Analyser** l'architecture de la plateforme GitHub Agents 2026 et expliquer le flux complet issue → PR → review → merge avec ses composants.
2. **Configurer** un Custom Agent complet dans `.github/agents/<name>/agent.md` en maîtrisant chaque champ (name, model, tools, mcp_servers, hooks, sub_agents).
3. **Implémenter** le handoff cloud↔CLI et la gestion multi-session avec fork de conversation.
4. **Déployer** un serveur MCP dans `.github/mcp.json` et l'intégrer aux hooks d'un agent.
5. **Appliquer** les règles de sécurité et de gouvernance enterprise (sandboxing, allowlist, audit logs).

> Ces objectifs sont SMART : spécifiques (configurer un fichier YAML, implémenter un handoff), mesurables (chaque objectif produit un artefact vérifiable), atteignables (documentation GitHub accessible), réalistes (dans le cadre du lab), temporels (durée de la séance + lab).

---

## Plan détaillé

### 6.1 GitHub Copilot Coding Agent — Évolution 2025 → 2026

#### Définition

> **Définition :** Le GitHub Copilot Coding Agent est l'agent cloud natif de GitHub qui transforme une issue ou un prompt en pull request complète — code, tests, review, et déploiement — sans intervention humaine.

#### Évolution 2025 → 2026

| Fonctionnalité | 2025 | 2026 | Impact |
|----------------|------|------|--------|
| Modèle | Fixe (GPT-4o) | **Model picker** : `auto` ou `premium` | Choix du rapport qualité/coût par tâche |
| Review | Manuelle | **Self-review** automatique | PR mergée sans review humaine pour les tâches simples |
| Planification | Aucune | **Implementation plan** avant le code | L'agent explique sa stratégie avant d'écrire du code |
| Custom agents | — | `.github/agents/` (stable) | Agents spécialisés par équipe |
| Session | Locale uniquement | **Cloud ↔ CLI handoff** | Passage transparent GitHub ↔ terminal |
| Contexte | Limité à l'éditeur | **Copilot Memory** partagée | Mémoire persistante entre sessions et agents |
| MCP | — | `.github/mcp.json` | Serveurs MCP propriétaires branchés |
| Sub-agents | — | Délégation hiérarchique | Un agent de code appelle un agent QA |
| Concurrence | 1 session | **Multi-session** (fork, parallèle) | Plusieurs agents simultanés |

#### Model picker

Le model picker permet de choisir entre :
- **`auto`** : GitHub choisit le meilleur modèle selon la tâche (coût optimisé)
- **`premium`** : Modèle le plus capable (meilleure qualité, coût plus élevé)
- **`opencode/big-pickle`** : Modèle natif opencode pour les déploiements sur site

Le choix se fait dans le fichier agent :

```yaml
model: auto
# ↑ GitHub sélectionne le modèle optimal selon la complexité de la tâche
```

```yaml
model: premium
# ↑ Force l'utilisation du modèle le plus capable (pour les tâches critiques)
```

#### Self-review

Le Coding Agent effectue une **self-review** automatique avant de soumettre la PR :
1. Vérification syntaxique (lint)
2. Exécution des tests unitaires
3. Analyse de sécurité (code scanning)
4. Vérification de couverture de code

Si la self-review échoue, l'agent corrige et recommence. Si elle réussit, la PR est créée avec le statut "approved by Copilot".

#### Pourquoi ce concept est crucial

- **Productivité** : Un développeur peut décrire une feature en langage naturel et recevoir une PR prête à merger.
- **Qualité** : La self-review attrape les erreurs avant la soumission, réduisant le nombre de cycles de review humains.
- **Tracabilité** : Chaque étape est loggée dans la PR (plan → code → tests → review).

---

### 6.2 Architecture GitHub Agents

#### Schéma complet

```
                        ┌─────────────────────────────────────┐
                        │           Déclencheurs              │
                        │  Issue  │  PR  │  Comment  │  Chat  │
                        └────┬────┴──┬───┴─────┬─────┴───┬────┘
                             │       │         │         │
                             ▼       ▼         ▼         ▼
                        ┌─────────────────────────────────────┐
                        │          Copilot Cloud              │
                        │        ┌───────────────┐            │
                        │        │  Model Picker  │            │
                        │        │  (auto/premium)│            │
                        │        └───────┬───────┘            │
                        │                │                    │
                        │        ┌───────▼───────┐            │
                        │        │   Agent Core   │            │
                        │        │  ┌─────────┐  │            │
                        │        │  │ Plan    │  │  ▲         │
                        │        │  ├─────────┤  │  │         │
                        │        │  │ Code    │  │  │ Outils  │
                        │        │  ├─────────┤  │  │ MCP    │
                        │        │  │ Test    │  │  │ Memory │
                        │        │  ├─────────┤  │  │        │
                        │        │  │ Review  │  │  ▼        │
                        │        │  └─────────┘  │            │
                        │        └───────┬───────┘            │
                        └────────────────┼────────────────────┘
                                         │
                                         ▼
                        ┌─────────────────────────────────────┐
                        │         Draft PR créée              │
                        │  ┌─────────────────────────────┐    │
                        │  │ Commits automatiques        │    │
                        │  │ Session logs (plan + code)  │    │
                        │  │ Self-review status          │    │
                        │  │ Code scanning results       │    │
                        │  │ Sub-agent contributions     │    │
                        │  └─────────────────────────────┘    │
                        └────────────────┬────────────────────┘
                                         │
                                         ▼
                        ┌─────────────────────────────────────┐
                        │           Cycle de review            │
                        │  ┌──────┐   ┌───────┐   ┌────────┐ │
                        │  │Human │◄─►│Custom │◄─►│CI/CD   │ │
                        │  │Review│   │Agent  │   │Checks  │ │
                        │  └──────┘   └───────┘   └────────┘ │
                        └────────────────┬────────────────────┘
                                         │
                                         ▼
                        ┌─────────────────────────────────────┐
                        │              Merge                   │
                        │    (avec branch protection)          │
                        └─────────────────────────────────────┘
```

#### Flux détaillé

1. **Déclenchement** : Un événement GitHub (issue, PR, commentaire, chat) active l'agent.
2. **Planification** : L'agent génère un implementation plan (étapes, fichiers modifiés, tests).
3. **Exécution** : L'agent écrit le code, exécute les outils MCP, appelle les sub-agents.
4. **Self-review** : L'agent vérifie son propre travail (lint, tests, sécurité).
5. **Draft PR** : GitHub crée une Pull Request avec commits, logs, et status de review.
6. **Review cycle** : Review humaine, custom agents, CI/CD checks en parallèle.
7. **Merge** : La PR est mergée si toutes les conditions sont remplies (branch protection).

#### Cas d'usage concret

> Un développeur crée une issue : "Ajouter un endpoint `/api/health` qui retourne le statut de la DB". Le Coding Agent planifie, code, teste, et soumet une PR. Un agent `qa-engineer` (sub-agent) ajoute des tests d'intégration. Un agent `security-reviewer` scanne le code. La PR est mergée en 12 minutes.

#### Pourquoi ce concept est crucial

- **Automatisation du cycle complet** : De l'idée à la prod, sans friction.
- **Collaboration agent-humain** : Les agents font le travail préparatoire, les humains valident.
- **Extensibilité** : Chaque étape peut être remplacée par un custom agent ou un hook MCP.

---

### 6.3 Custom Agents — Configuration ligne par ligne

#### Définition

> **Définition :** Un Custom Agent GitHub est un agent spécialisé défini dans un fichier Markdown avec frontmatter YAML, stocké dans `.github/agents/<name>/agent.md`. Il peut être invoqué par les développeurs, par d'autres agents, ou par des événements GitHub.

#### Structure complète commentée

Chaque Custom Agent est un fichier Markdown avec deux sections : un **frontmatter YAML** (configuration) et un **body Markdown** (instructions).

```yaml
---
name: PR Reviewer
# ↑ NAME (obligatoire)
#   Nom d'affichage de l'agent. Apparaît dans l'interface GitHub,
#   dans le sélecteur d'agents, et dans les logs d'audit.
#   Scénario : un développeur clique sur "PR Reviewer" dans
#   le menu déroulant des agents pour lancer une review.
#   Maximum 64 caractères.

description: Automated code review on pull requests
# ↑ DESCRIPTION (obligatoire)
#   Phrase décrivant le rôle de l'agent. Apparaît dans le
#   GitHub Agents Panel et dans les résultats de recherche.
#   Scénario : dans la liste des 50 agents d'une organisation,
#   la description permet de trouver rapidement celui qui
#   correspond au besoin ("Automated code review...").

model: opencode/big-pickle
# ↑ MODEL (obligatoire)
#   Modèle LLM utilisé par cet agent. Valeurs possibles :
#   - "auto"        : GitHub sélectionne le modèle optimal
#   - "premium"     : modèle le plus capable disponible
#   - "opencode/big-pickle" : modèle natif opencode
#   Scénario : un agent de review utilise "opencode/big-pickle"
#   pour garantir des résultats reproductibles cohérents avec
#   l'environnement de développement opencode.

tools:
# ↑ TOOLS (optionnel, liste)
#   Outils GitHub intégrés auxquels l'agent a accès.
#   Liste des outils disponibles :
#   - code_scanning  : analyse de sécurité statique
#   - code_review    : review de code automatisée
#   - actions        : déclenchement de workflows GitHub Actions
#   - issues         : création/lecture d'issues
#   - search         : recherche dans le code du dépôt
#   Scénario : un agent PR Reviewer active code_scanning pour
#   détecter les vulnérabilités automatiquement.

  - code_scanning

mcp_servers:
# ↑ MCP SERVERS (optionnel, liste)
#   Serveurs MCP additionnels auxquels l'agent peut se connecter.
#   Référence les serveurs définis dans .github/mcp.json.
#   Scénario : un agent de review se connecte à un serveur MCP
#   interne qui expose les règles de linting spécifiques à
#   l'organisation.

  - dev-assistant

hooks:
# ↑ HOOKS (optionnel)
#   Scripts exécutés automatiquement avant/après chaque action
#   de l'agent. Permet d'injecter de la validation, de la
#   transformation, ou du logging à chaque étape.

  preToolUse: "ruff check {file}"
  # ↑ PRE-TOOL USE HOOK
  #   Commande exécutée AVANT que l'agent n'utilise un outil.
  #   {file} est remplacé par le fichier cible de l'action.
  #   Si la commande échoue (exit code != 0), l'outil n'est
  #   pas utilisé et l'erreur est loggée.
  #   Scénario : avant de modifier un fichier Python, l'agent
  #   vérifie que le code existant passe ruff. Si le lint
  #   échoue, l'agent corrige d'abord le style.

  postToolUse: "python -m pytest {dir} -x"
  # ↑ POST-TOOL USE HOOK
  #   Commande exécutée APRÈS que l'agent a utilisé un outil.
  #   {dir} est remplacé par le répertoire du fichier modifié.
  #   Si la commande échoue, l'agent peut annuler la
  #   modification ou la corriger.
  #   Scénario : après avoir modifié un fichier dans tests/,
  #   l'agent exécute pytest en mode fail-fast (-x). Si un
  #   test échoue, l'agent sait que sa modification est
  #   problématique.

sub_agents:
# ↑ SUB-AGENTS (optionnel, liste)
#   Liste des agents spécialisés que cet agent peut déléguer.
#   Chaque sub-agent est défini dans un autre fichier
#   .github/agents/<name>/agent.md.
#   Scénario : l'agent PR Reviewer délègue l'analyse de
#   sécurité à l'agent security-scanner, et les tests
#   d'intégration à l'agent qa-engineer.

  - qa-engineer
---
```

#### Body Markdown — Instructions spécifiques

Le corps du fichier (après le `---`) contient les **instructions système** de l'agent :

```markdown
Review every PR for:
1. Code style violations (ruff)
2. Test coverage
3. Security issues
```

Chaque instruction est un comportement attendu. L'agent les interprète comme des règles impératives. Plus elles sont précises, meilleur est le résultat.

**Bonnes pratiques pour les instructions :**
- Utiliser des verbes d'action (review, check, verify, generate)
- Prioriser avec des listes numérotées
- Ajouter des contraintes mesurables ("coverage > 80%")
- Référencer les hooks par leur nom pour la traçabilité

#### Scénario complet d'exécution

1. Un développeur pousse une PR sur `feature/add-health-endpoint`
2. GitHub détecte l'événement PR et déclenche l'agent `PR Reviewer`
3. L'agent charge sa configuration : `model: opencode/big-pickle`, `tools: [code_scanning]`
4. Pour chaque fichier modifié, le `preToolUse` hook exécute `ruff check {file}`
5. Si ruff passe, l'agent analyse le code (sécurité, style, coverage)
6. Après l'analyse, `postToolUse` exécute `python -m pytest {dir} -x`
7. L'agent peut déléguer à `qa-engineer` (sub_agent) pour les tests d'intégration
8. Résultat : commentaire sur la PR avec les violations, suggestions, et statut des tests

#### Types d'agents par domaine

| Type | Exemple | Outils typiques | Hooks |
|------|---------|-----------------|-------|
| **Code** | Feature Implementer | search, issues | pre: lint, post: test |
| **Review** | PR Reviewer | code_scanning, code_review | pre: ruff, post: pytest |
| **DevOps** | Deploy Manager | actions | pre: dry-run, post: monitor |
| **Documentation** | Doc Generator | search | pre: read, post: spell-check |
| **Security** | Security Auditor | code_scanning | pre: bandit, post: report |
| **QA** | Test Engineer | actions | pre: coverage, post: pytest |

#### Pourquoi ce concept est crucial

- **Spécialisation** : Chaque agent est expert dans un domaine, pas un généraliste.
- **Réutilisabilité** : Un agent `security-scanner` est utilisé par toutes les équipes.
- **Gouvernance** : Les hooks et les permissions sont définis dans le fichier, pas dans le code.
- **Découverte** : Les agents sont catalogués dans le GitHub Agents Panel.

---

### 6.4 Session Management

#### Cloud ↔ CLI Handoff

Le handoff permet de démarrer une session sur GitHub.com et de la continuer dans le terminal (ou l'inverse).

**Flux GitHub → Terminal :**

```
1. Développeur clique "Continue in CLI" sur GitHub.com
   │
   ▼
2. GitHub copie une commande `gh` dans le presse-papier :
   $ gh copilot continue --session abc123
   │
   ▼
3. Terminal : la commande charge la session depuis le cloud
   - Branche git restaurée
   - Logs de session récupérés
   - Historique du contexte chargé
   - Modèle et outils configurés
   │
   ▼
4. Développeur travaille dans le terminal
   - Appuie sur `&` pour renvoyer au cloud
   - La session est synchronisée
```

**Scénario concret :** Un développeur démarre une session de refactoring sur GitHub.com, se rend compte qu'il a besoin d'accéder à des fichiers locaux, utilise "Continue in CLI", termine le refactoring dans le terminal, puis renvoie la session sur GitHub pour créer la PR.

#### Multi-session

```ascii
┌──────────────────────────────────────────────────┐
│              GitHub Agents Panel                 │
│                                                   │
│  Agent 1 : Feature A (coding agent)    ┌──────┐  │
│  Agent 2 : Feature B (coding agent)    │  ✅  │  │
│  Agent 3 : PR Review (review agent)    └──────┘  │
│  Agent 4 : Bug fix (coding agent)      ┌──────┐  │
│  Agent 5 : Security scan (sec agent)   │ ▶ ▶ │  │
│  Agent 6 : Deploy (devops agent)       └──────┘  │
└──────────────────────────────────────────────────┘
```

Caractéristiques du multi-session :
- **Sessions parallèles** : Jusqu'à 10 agents simultanés par organisation
- **Status indicator** : running ✅ / completed ⏳ / failed ❌ / waiting
- **Resource allocation** : GitHub alloue les ressources selon la priorité configurée

#### Conversation Fork

Le fork de conversation permet de **brancher une session à partir d'un checkpoint**.

```ascii
                         ┌────────────────────┐
                         │  Session originale  │
                         │  Étape 1 → 2 → 3   │
                         └────────┬───────────┘
                                  │
                    Fork au checkpoint
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │ Fork A          │ │ Fork B          │ │ Fork C          │
    │ Continue voie 1 │ │ Continue voie 2 │ │ Continue voie 3 │
    │ → Résultat A    │ │ → Résultat B    │ │ → Résultat C    │
    └─────────────────┘ └─────────────────┘ └─────────────────┘
```

**Scénario :** Un agent propose 3 approches pour résoudre un bug. Le développeur fork à l'étape 2 pour explorer les 3 voies en parallèle, puis choisit la meilleure.

#### Pourquoi ce concept est crucial

- **Flexibilité** : Le développeur choisit son environnement (cloud ou terminal) sans perte de contexte.
- **Parallélisme** : Plusieurs agents travaillent simultanément sur des tâches indépendantes.
- **Exploration** : Le fork permet d'explorer des alternatives sans risquer la session principale.

---

### 6.5 Copilot Memory

#### Types de mémoire

GitHub Agents dispose de **trois niveaux de mémoire**, chacun avec un cycle de vie et un scope différent :

```ascii
                    ┌─────────────────────────────────────┐
                    │         COPILOT MEMORY              │
                    │                                     │
                    │  ┌─────────────────────────────┐    │
                    │  │  1. Session Memory          │    │
                    │  │  Durée : session courante   │    │
                    │  │  Scope : agent unique       │    │
                    │  │  Contenu : historique chat,  │    │
                    │  │  fichiers modifiés, décisions│    │
                    │  └─────────────────────────────┘    │
                    │                                     │
                    │  ┌─────────────────────────────┐    │
                    │  │  2. Agent Memory            │    │
                    │  │  Durée : plusieurs sessions │    │
                    │  │  Scope : tous les agents    │    │
                    │  │  Contenu : préférences,     │    │
                    │  │  patterns, décisions récentes│    │
                    │  └─────────────────────────────┘    │
                    │                                     │
                    │  ┌─────────────────────────────┐    │
                    │  │  3. Plan Memory             │    │
                    │  │  Durée : persistante        │    │
                    │  │  Scope : tous les agents    │    │
                    │  │  Contenu : implementation   │    │
                    │  │  plans, objectifs en cours   │    │
                    │  └─────────────────────────────┘    │
                    └─────────────────────────────────────┘
```

#### 1. Session Memory

Mémoire à court terme attachée à une session unique :

- Stocke l'historique complet des échanges
- Contient les fichiers ouverts et modifiés
- Enregistre les décisions prises (pourquoi tel choix plutôt qu'un autre)
- **Durée de vie** : supprimée à la fin de la session (sauf export)

**Scénario :** Un développeur demande "ajoute un middleware d'authentification". L'agent se souvient des modifications précédentes dans la session (structure du projet, dépendances installées).

#### 2. Agent Memory

Mémoire partagée entre **tous les agents** de l'organisation :

- Rassemble les patterns de code préférés de l'équipe
- Stocke les décisions architecturales récentes
- Mémorise les conventions de nommage
- **Durée de vie** : persistante (configurable, par défaut 30 jours)

**Scénario :** L'agent `PR Reviewer` apprend que l'équipe préfère les compréhensions de liste aux boucles `for`. Cette préférence est partagée avec l'agent `Feature Developer`.

#### 3. Plan Memory

Mémoire dédiée aux **implementation plans** :

- Stocke les plans générés par les agents
- Permet de reprendre un plan interrompu
- Maintient la cohérence entre les étapes d'un plan multi-session
- **Durée de vie** : jusqu'à complétion ou annulation explicite

**Scénario :** Un plan "Migrer de Flask à FastAPI" est généré par un agent, mais le projet est interrompu. Deux semaines plus tard, un autre agent reprend le plan là où il s'était arrêté.

#### Context Compaction

Mécanisme de **réduction du contexte** pour éviter le dépassement de fenêtre :

```bash
/compact  # Commande manuelle : résume l'historique et supprime le détail
```

- **Manuel (`/compact`)** : Le développeur déclenche manuellement le compactage
- **Automatique** : GitHub compacte automatiquement quand la fenêtre de contexte atteint 80%
- **Algorithme** : Résumé hiérarchique — les échanges les plus anciens sont résumés, les plus récents sont conservés intacts

#### Pourquoi ce concept est crucial

- **Continuité** : Un agent ne repart pas de zéro à chaque session.
- **Cohérence** : Tous les agents partagent la même connaissance de l'organisation.
- **Performance** : Le compactage évite la dégradation due à un contexte trop long.

---

### 6.6 Sécurité

#### Terminal Sandboxing

GitHub Agents exécute les commandes dans un **sandbox isolé** du système hôte.

```ascii
┌──────────────────────────────────────────────────┐
│                  HÔTE                             │
│                                                    │
│  ┌─────────────────────┐  ┌──────────────────┐    │
│  │  Sandbox Agent 1    │  │  Sandbox Agent 2 │    │
│  │  /tmp/sandbox/001/  │  │  /tmp/sandbox/002/│    │
│  │  Réseau isolé       │  │  Réseau isolé     │    │
│  │  Pas d'accès home   │  │  Pas d'accès home │    │
│  │  Filesystem virtuel │  │  Filesystem virt. │    │
│  └─────────────────────┘  └──────────────────┘    │
│                              │                     │
│                              ▼                     │
│                    ┌──────────────────┐            │
│                    │  GitHub Actions  │            │
│                    │  Runner (proxy)  │            │
│                    └──────────────────┘            │
└──────────────────────────────────────────────────┘
```

**Disponibilité :** macOS et Linux (experimental en 2026). Windows en 2027.

#### Auto-Approval Rules

Les règles d'auto-approval définissent quelles actions l'agent peut exécuter sans confirmation humaine :

| Niveau | Actions autorisées | Cas d'usage |
|--------|-------------------|-------------|
| `none` | Aucune automatique | Audit de sécurité |
| `safe` | Lint, read, search, test | Review de code |
| `standard` | Edit, commit, push sur branche feature | Développement |
| `full` | Merge, déploiement staging | DevOps CI/CD |

Configuration dans le fichier agent :

```yaml
permission:
  auto_approval: standard
  # ↑ Niveau d'auto-approval
  #   - none     : chaque action demande une confirmation
  #   - safe     : actions read-only + tests
  #   - standard : édition et commit sur feature branches
  #   - full     : merge et déploiement (risqué !)
```

#### Command Allow/Deny Patterns

Les patterns de commande définissent précisément ce qu'un agent peut exécuter :

```yaml
permission:
  bash:
    ruff *: allow
    # ↑ Toute commande commençant par "ruff" est autorisée
    pytest *: allow
    # ↑ pytest est autorisé
    pip install *: ask
    # ↑ Toute installation pip demande confirmation
    rm -rf *: deny
    # ↑ Suppression récursive INTERDITE
    *: ask
    # ↑ Fallback : tout le reste demande confirmation
```

#### Secret Scanning

GitHub Agents intègre le **secret scanning** directement dans le workflow :

1. **Pré-commit** : L'agent scanne les diffs avant chaque commit
2. **Pattern matching** : Détection des patterns connus (clés API, tokens, mots de passe)
3. **Blocage** : Si un secret est détecté, le commit est bloqué et un avertissement est émis
4. **Rotation** : GitHub peut suggérer (ou automatiser) la rotation du secret compromis

**Scénario :** Un agent de feature écrit du code avec une clé API en dur. Le secret scanning détecte le pattern `sk-...` (clé OpenAI), bloque le commit, et avertit le développeur.

#### Branch Protection

GitHub Agents honore les **branch protection rules** existantes :

- **Required reviews** : L'agent ne peut pas merger sans le nombre requis de reviews
- **Status checks** : Tous les checks CI/CD doivent passer
- **Linear history** : Pas de merge commits si le dépôt exige l'historique linéaire
- **Force push** : Interdit sur les branches protégées, même pour un agent

#### Pourquoi ce concept est crucial

- **Prévention des incidents** : Le sandboxing empêche un agent malveillant de compromettre le système.
- **Conformité** : Les rules d'auto-approval garantissent que les actions critiques sont validées par un humain.
- **Protection des secrets** : Le secret scanning évite les fuites accidentelles.

---

### 6.7 Intégration MCP

#### Définition

> **Définition :** L'intégration MCP (Model Context Protocol) permet aux GitHub Agents d'invoquer des outils externes (bases de données, APIs, services internes) via le protocole JSON-RPC 2.0 standardisé.

#### Configuration `.github/mcp.json` commentée ligne par ligne

```json
{
  "mcpServers": {
    // ↑ SECTION mcpServers (obligatoire, racine)
    //   Objet contenant la configuration de tous les serveurs MCP
    //   auxquels les GitHub Agents peuvent se connecter.
    //   Chaque clé est un nom unique de serveur.

    "dev-assistant": {
      // ↑ NOM DU SERVEUR (clé unique)
      //   Identifiant utilisé dans le champ mcp_servers de la
      //   configuration des agents (.github/agents/*/agent.md).
      //   Scénario : l'agent "PR Reviewer" référence
      //   "dev-assistant" dans sa liste mcp_servers.
      //   Maximum 64 caractères, uniquement des
      //   lettres minuscules, chiffres et tirets.

      "type": "local",
      // ↑ TYPE DE TRANSPORT (obligatoire)
      //   - "local"  : le serveur tourne sur le GitHub Actions runner
      //                (communication via stdio, JSON-RPC 2.0)
      //   - "remote" : serveur distant hébergé par l'organisation
      //                (communication via HTTP + SSE)
      //   Scénario : un serveur de linting interne est déployé
      //   localement sur chaque runner (type: local) tandis qu'un
      //   serveur de base de données est hébergé sur un serveur
      //   dédié (type: remote).

      "command": "python",
      // ↑ COMMANDE DE LANCEMENT (obligatoire pour type: local)
      //   Commande exécutée pour démarrer le serveur MCP.
      //   Le serveur doit communiquer via stdin/stdout en
      //   JSON-RPC 2.0 (conforme à la spécification MCP).
      //   Scénario : "python" suivi du chemin du script serveur.

      "args": ["mcp-servers/dev-assistant.py"],
      // ↑ ARGUMENTS DE LA COMMANDE (optionnel)
      //   Liste des arguments passés à la commande.
      //   Scénario : le script Python a besoin du chemin
      //   de configuration ou d'un mode de débogage.

      "env": {
        // ↑ VARIABLES D'ENVIRONNEMENT (optionnel)
        //   Variables transmises au serveur MCP.
        //   ATTENTION : ne pas stocker de secrets en clair ici.
        //   Utiliser GitHub Secrets à la place.

        "LOG_LEVEL": "debug",
        "CONFIG_PATH": "/etc/mcp/dev-assistant.yaml"
      },

      "enabled": true
      // ↑ ACTIVATION (obligatoire)
      //   - true  : le serveur est démarré au début de la session
      //   - false : le serveur est configuré mais pas actif
      //   Scénario : un serveur est configuré pour la prod mais
      //   désactivé en dev pour économiser les ressources.
    },

    "production-db": {
      "type": "remote",
      // ↑ Serveur distant : pas de command/args, juste une URL.
      "url": "https://mcp.internal.company.com/db"
      // ↑ URL DU SERVEUR (obligatoire pour type: remote)
      //   Endpoint HTTP du serveur MCP distant.
      //   La communication se fait via Server-Sent Events (SSE)
      //   pour le streaming et HTTP POST pour les requêtes.
      //   Scénario : un serveur MCP centralisé hébergé dans
      //   le datacenter de l'entreprise expose des outils
      //   de requêtage base de données.
    }
  }
}
```

#### Utilisation par les agents

Une fois le serveur MCP configuré, un Custom Agent l'utilise via le champ `mcp_servers` :

```yaml
name: DB Assistant
description: Assistant de requêtage base de données
model: opencode/big-pickle
mcp_servers:
  - production-db
  # ↑ Référence la clé "production-db" définie dans .github/mcp.json
  #   L'agent peut maintenant invoquer les outils exposés par
  #   ce serveur (ex: query_db, get_schema, run_migration).
```

#### Scénario concret

1. Un développeur demande : "Quels sont les utilisateurs inactifs depuis 90 jours ?"
2. L'agent `DB Assistant` consulte son MCP `production-db`
3. Le serveur MCP expose l'outil `query_db` avec paramètres (sql, params)
4. L'agent invoque `query_db` avec `SELECT * FROM users WHERE last_login < NOW() - INTERVAL '90 days'`
5. Le serveur exécute la requête, retourne les résultats
6. L'agent formate la réponse pour le développeur

#### Pourquoi ce concept est crucial

- **Accès aux données** : Un agent peut interroger des systèmes internes sans API spécifique.
- **Sécurité** : Les accès sont centralisés et audités via le serveur MCP.
- **Standardisation** : Tous les outils suivent le même protocole indépendamment de leur implémentation.

---

### 6.8 Agents Panel

#### Définition

> **Définition :** Le GitHub Agents Panel est une interface de contrôle (mission control) accessible depuis toutes les pages GitHub qui permet de visualiser, superviser, et interagir avec l'ensemble des agents actifs de l'organisation.

#### Interface

```ascii
┌──────────────────────────────────────────────────────────────────┐
│  GitHub │ Dashboard │ Agents Panel                      [Docs]  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Active Agents (6)       │  ⏱  Today                     │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │                                                         │    │
│  │  Agent              │ Status   │ Duration │ Repository  │    │
│  │  ───────────────────────────────────────────────────── │    │
│  │  Feature A (v2.3)   │ ▶▶ 45%   │ 12m 30s  │ frontend/  │    │
│  │  Security Audit     │ ⏳ 75%   │ 8m 12s   │ backend/   │    │
│  │  PR #142 Review     │ ✅ Done  │ 3m 45s   │ core/      │    │
│  │  Deploy to prod     │ ❌ Fail  │ 2m 10s   │ infra/     │    │
│  │  Doc Generator      │ ▶▶ 30%   │ 15m 00s  │ docs/      │    │
│  │  DB Migration       │ ⏸ Paused │ 0m 05s   │ data/      │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Agent Detail: PR #142 Review                             │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │                                                         │    │
│  │  Steps:                                                  │    │
│  │  ✅ Code style check        (3 violations found)         │    │
│  │  ✅ Security scan           (0 vulnerabilities)          │    │
│  │  ▶ Running tests            (45/120 tests passed)        │    │
│  │  ⏸ Coverage analysis        (waiting for tests)          │    │
│  │                                                         │    │
│  │  [View PR] [Cancel Agent] [Retry] [View Logs]           │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Quick Actions                                            │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │  [New Agent] [Fork Session] [Share Logs] [Export]      │    │
│  └─────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

#### Fonctionnalités clés

1. **Real-time status** : Chaque agent affiche sa progression en temps réel
2. **Jump to PR** : Lien direct vers la PR associée à l'agent
3. **Logs détaillés** : Historique complet des actions de l'agent
4. **Contrôle** : Cancel, Retry, Pause depuis le panel
5. **Fork** : Créer un fork de session depuis n'importe quel checkpoint
6. **Export** : Exporter les logs au format JSON pour analyse

#### Accès

Le panel est accessible :
- Depuis le header GitHub (icône agents)
- Depuis chaque PR (lien "View Agent")
- Depuis chaque issue (lien "Track Agent")
- Via `github.com/agents` (page dédiée)

#### Pourquoi ce concept est crucial

- **Visibilité** : Les développeurs savent ce que les agents font en temps réel.
- **Contrôle** : Possibilité d'interrompre un agent qui dérive.
- **Débogage** : Les logs détaillés permettent de comprendre pourquoi un agent a échoué.

---

### 6.9 Enterprise & Governance

#### Enterprise MCP Governance

Les organisations peuvent restreindre les serveurs MCP autorisés via une **allowlist** :

```json
{
  "enterprise": {
    "mcp": {
      "allowlist": [
        // ↑ Liste blanche des serveurs MCP autorisés.
        //   Tout serveur non listé est bloqué.
        //   Définie par l'admin GitHub Enterprise.
        "dev-assistant",
        "production-db",
        "monitoring",
        "deploy-engine"
      ],
      "blockUnknownServers": true
      // ↑ BLOQUAGE DES SERVEURS INCONNUS
      //   true  : les agents ne peuvent utiliser que les serveurs
      //          de l'allowlist
      //   false : les agents peuvent utiliser n'importe quel
      //          serveur MCP (dangereux pour la production)
    }
  }
}
```

#### Custom Agents partageables

Les Custom Agents peuvent être partagés au niveau de l'organisation :

| Scope | Visibilité | Usage |
|-------|-----------|-------|
| `private` | Agent uniquement | Personnel, test |
| `repository` | Dépôt actuel | Équipe |
| `organization` | Toute l'orga | Standardisation |
| `enterprise` | Toute l'entreprise | Gouvernance centralisée |

```yaml
name: Security Auditor
scope: organization
# ↑ PORTÉE DE L'AGENT
#   Un agent "organization" est disponible dans tous les
#   dépôts de l'organisation. Les modifications sont
#   centralisées dans le dépôt .github de l'org.
```

#### Audit Logs

Chaque action de chaque agent est loggée dans les **audit logs** GitHub :

| Champ | Description |
|-------|-------------|
| `timestamp` | Date et heure de l'action |
| `agent` | Nom de l'agent |
| `actor` | Déclencheur (humain ou événement) |
| `action` | Type d'action (read, edit, commit, merge) |
| `target` | Fichier, branche, ou PR ciblé |
| `status` | Succès ou échec |
| `duration` | Temps d'exécution |
| `model` | Modèle LLM utilisé |

**Scénario :** Un incident de production survient. L'équipe de sécurité consulte les audit logs pour déterminer quel agent a mergé le code problématique, quand, et avec quels paramètres.

#### Policy Enforcement via Agent Hooks

Les hooks (preToolUse / postToolUse) sont le mécanisme de **policy enforcement** :

```yaml
# Exemple : Politique de sécurité obligatoire
hooks:
  preToolUse: |
    # ↑ AVANT chaque outil, l'organisation impose :
    # 1. Vérifier que le fichier n'est pas dans la liste noire
    # 2. Vérifier que le développeur a les droits
    # 3. Logger l'action dans le SIEM
    bash -c "python /etc/github/security-check.py {file}"
```

Les politiques peuvent imposer :
- **Vérification de signature** : Tout commit doit être signé (GPG)
- **Scan obligatoire** : Tout nouveau fichier .py doit passer ruff
- **Review obligatoire** : Certains fichiers critiques (config, secrets) requirent une review humaine
- **Délai de sécurité** : Pas de merge avant X minutes (temps de réaction)

#### Pourquoi ce concept est crucial

- **Conformité réglementaire** : Les audit logs prouvent la conformité (SOC2, ISO 27001).
- **Sécurité centralisée** : L'admin contrôle ce que les agents peuvent faire.
- **Traçabilité** : Chaque action est attribuable à un agent et un déclencheur spécifiques.

---

## Synthèse

**Ce que vous avez appris dans cette séance :**

| Concept | Résumé | Section |
|---------|--------|---------|
| GitHub Copilot Coding Agent | Agent cloud qui transforme une issue en PR complète avec self-review | 6.1 |
| Architecture GitHub Agents | Flux complet issue → plan → code → test → review → merge | 6.2 |
| Custom Agents | Configuration YAML ligne par ligne : name, model, tools, hooks, sub_agents | 6.3 |
| Session Management | Handoff cloud↔CLI, multi-session parallèle, conversation fork | 6.4 |
| Copilot Memory | Trois niveaux de mémoire (session, agent, plan) + compactage | 6.5 |
| Sécurité | Sandboxing, auto-approval, command patterns, secret scanning | 6.6 |
| Intégration MCP | `.github/mcp.json` commenté ligne par ligne | 6.7 |
| Agents Panel | Mission control temps réel avec supervision centralisée | 6.8 |
| Enterprise & Governance | Allowlist MCP, audit logs, policy enforcement via hooks | 6.9 |

**Lien avec la séance suivante :**

> *"Maintenant que vous savez configurer des agents GitHub customisés avec des hooks, de la mémoire, et des sub-agents, la séance 7 (LangGraph) vous apprendra à orchestrer ces mêmes workflows sous forme de **graphes d'état cycliques**. Là où GitHub Agents gère un pipeline linéaire (issue → PR → merge), LangGraph permet des boucles de rétroaction, du branching conditionnel, et de l'orchestration distribuée entre agents. Vous réutiliserez les concepts de Custom Agents et de sub_agents comme **nœuds** dans vos graphes LangGraph."*

---

## Références contextualisées

- **[GitHub, GitHub Copilot Blog (2024-2026)]**
  *Contexte :* Source officielle sur l'évolution de Copilot, les annonces de fonctionnalités (Copilot Coding Agent, Custom Agents, Copilot Memory). Sections concernées : 6.1, 6.2.
  *Niveau de lecture :* introduction (articles de blog)
  *→ https://github.blog/category/product/copilot/*

- **[GitHub, GitHub Agents Documentation (2026)]**
  *Contexte :* Documentation technique officielle pour la configuration des Custom Agents, l'intégration MCP, et la gouvernance enterprise. Sections concernées : 6.3, 6.7, 6.9.
  *Niveau de lecture :* technique (documentation)
  *→ https://docs.github.com/en/copilot/using-github-copilot/using-github-copilot-code-review*

- **[GitHub, MCP Servers Configuration Reference (2026)]**
  *Contexte :* Spécification complète du fichier `.github/mcp.json` avec tous les paramètres disponibles. Section concernée : 6.7.
  *Niveau de lecture :* technique (référence)
  *→ https://docs.github.com/en/copilot/customizing-copilot/configuring-mcp-servers*

- **[GitHub, Enterprise Agent Governance Guide (2026)]**
  *Contexte :* Guide pour configurer la gouvernance des agents au niveau organisation : allowlist MCP, audit logs, policy enforcement. Section concernée : 6.9.
  *Niveau de lecture :* avancé
  *→ https://docs.github.com/en/enterprise-cloud@latest/admin/copilot/managing-copilot-agent-policies*

- **[Anthropic, Building effective agents (2024)]**
  *Contexte :* Guide conceptuel sur la conception d'agents, utilisé comme référence pour la section 6.3 (patterns de configuration agent). Aide à comprendre *pourquoi* chaque champ existe.
  *Niveau de lecture :* avancé
  *→ https://docs.anthropic.com/en/docs/build-with-claude/agentic*

- **[openmode, opencode Documentation (2026)]**
  *Contexte :* Documentation du framework opencode utilisé dans les exemples de code. Le modèle `opencode/big-pickle` et le format des agents opencode sont le socle des exemples de cette séance.
  *Niveau de lecture :* technique
  *→ https://opencode.ai/docs*

- **[Séance 4 — MCP Protocol]**
  *Contexte :* Prérequis pour comprendre l'intégration MCP (section 6.7). Revoir la configuration des serveurs MCP et le protocole JSON-RPC 2.0.
  *Niveau de lecture :* révision
  *→ lectures/04-mcp-protocol.md*

- **[Séance 5 — A2A Protocol]**
  *Contexte :* Prérequis pour comprendre la communication entre agents (section 6.3, sub_agents). L'A2A et les sub_agents partagent le même principe de délégation.
  *Niveau de lecture :* révision
  *→ lectures/05-a2a-protocol.md*
