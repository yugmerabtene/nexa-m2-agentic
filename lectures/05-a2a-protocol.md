# Séance 5 — Agent-to-Agent Protocol (A2A)

> **Auteur :** yugmerabtene
> **Version :** 2.0
> **Durée estimée :** 2 heures

---

## Description

Cette séance explore le Agent-to-Agent Protocol (A2A), le standard de communication inter-agents proposé par Google DeepMind. Vous apprendrez à créer des Agent Cards, gérer le cycle de vie des tâches, et comprendre la complémentarité avec MCP. Cette séance fait le pont entre MCP (séance 4) et GitHub Agents (séance 6).

---

## Prérequis

Avant de commencer cette séance, assurez-vous d'avoir :

- Terminé la **Séance 4** et compris le protocole MCP
- Python 3.10+ installé
- Connaissances de base en APIs REST

### Installation des dépendances

#### Linux et macOS

```bash
# Vérifier Python
python3 --version

# Installer le SDK A2A
python3 -m pip install a2a-sdk

# Vérifier l'installation
python3 -c "import a2a; print('A2A SDK installé')"
```

#### Windows PowerShell

```powershell
# Vérifier Python
py --version

# Installer le SDK A2A
py -m pip install a2a-sdk

# Vérifier l'installation
py -c "import a2a; print('A2A SDK installé')"
```

> **Résultat attendu :** Le SDK A2A est installé et importable.

---

## Introduction théorique

**Quel est le problème fondamental ?**

Un agent isolé ne peut que raisonner sur son contexte local. Dès qu'une tâche dépasse son périmètre — accéder à un système de billing chez un partenaire, commander une API SaaS externe, déléguer une analyse longue à un spécialiste — il doit collaborer avec d'autres agents. Sans standard inter-agent, chaque collaboration est un couplage rigide : API REST propriétaire, format de message ad-hoc, négociation manuelle des capacités. Le problème se généralise en **n × m inter-agents** : n agents clients × m agents fournisseurs = n × m intégrations à coder, documenter, maintenir.

Le **Agent-to-Agent Protocol (A2A)** résout ce problème en définissant un protocole standardisé que tout agent peut implémenter pour découvrir les capacités d'autres agents, leur déléguer des tâches, et suivre leur exécution — indépendamment du framework, du langage, ou de l'hébergeur de chaque agent.

**Contexte 2026 :**

A2A a été proposé par Google DeepMind début 2025 et a rapidement rassemblé une coalition de **50+ partenaires** (Salesforce, SAP, Atlassian, ServiceNow, LangChain, CrewAI, MongoDB, Elastic). En 2026, le protocole est hébergé par la **Linux Foundation** (AI & Data Foundation), garantissant sa gouvernance ouverte et neutre. La spécification A2A v1.0 est prévue pour juin 2026. Google ADK intègre déjà nativement MCP + A2A, et LangGraph/CrewAI préparent le support. Le protocole répond à un besoin pressant : passer d'agents isolés à des **écosystèmes d'agents interopérables**.

**Liens avec les séances :**

| Séance | Lien |
|--------|------|
| Séance 4 — MCP | MCP standardise agent ↔ outil (communication verticale). A2A standardise agent ↔ agent (communication horizontale). Les deux sont complémentaires : un agent A2A utilise MCP en interne pour ses outils, et expose via A2A ses capacités à d'autres agents. |
| **→ Séance 5 (celle-ci)** | **A2A : standard de communication agent ↔ agent** |
| Séance 6 — GitHub Agents | GitHub Agents peut jouer le rôle d'agent A2A dans un workflow CI/CD : un agent de review délègue une analyse de vulnérabilité à un agent spécialisé via A2A. |

> **Exemple fil rouge :** "Dans la séance 4, vous avez appris à donner des outils à un agent via MCP. Dans cette séance, vous allez apprendre à faire collaborer des agents entre eux — y compris entre organisations différentes. MCP, c'est la communication agent ↔ outil. A2A, c'est la communication agent ↔ agent."

## Objectifs pédagogiques

À l'issue de cette séance, vous serez capable de :

1. **Analyser** le problème n × m de l'interopérabilité inter-agents et expliquer en quoi A2A le résout par un protocole standardisé de découverte et de délégation de tâches
2. **Schématiser** l'architecture A2A (Client Agent / Remote Agent) et décrire le rôle de chaque composant (Agent Card, Task lifecycle, Messages & Parts)
3. **Interpréter** une Agent Card JSON en commentant chaque champ (name, capabilities, auth, endpoints, pricing) et expliquer son rôle dans la découverte d'agents
4. **Distinguer** les cas d'usage de MCP vs A2A et justifier le choix du protocole (ou de leur combinaison) selon le contexte : agent local, cross-org, tâche longue, même runtime

## Plan détaillé

### 5.1 Pourquoi A2A ? — Le problème n × m inter-agents

#### Définition formelle

> **Définition :** Le Agent-to-Agent Protocol (A2A) est un protocole standardisé de communication entre agents, basé sur HTTP + SSE (Server-Sent Events) + JSON, qui permet à un agent client de découvrir les capacités d'un agent distant via une **Agent Card**, de lui soumettre des tâches, et d'en suivre le cycle de vie — le tout sans couplage fort entre les implémentations.

#### Analogie pédagogique

> *"Si MCP est USB-C pour brancher des outils sur un agent, A2A est TCP/IP pour faire communiquer des agents entre eux. USB-C connecte un périphérique à un ordinateur. TCP/IP connecte des ordinateurs entre eux sur le réseau. Les deux sont nécessaires : un ordinateur branché à une imprimante via USB (MCP) peut envoyer un document à un autre ordinateur via TCP/IP (A2A)."*

#### Le problème n × m inter-agents en détail

```
SANS A2A — Intégrations point-à-point :
                                    ┌──────────────────┐
        ┌──────────────────────────►│  Agent Billing   │
        │                           │  (API REST custom)│
        │                           └──────────────────┘
        │                           ┌──────────────────┐
        ├──────────────────────────►│  Agent Recherche │
        │                           │  (API GraphQL)   │
        │                           └──────────────────┘
   ┌────┴────┐                      ┌──────────────────┐
   │  Agent  │─────────────────────►│  Agent Support   │
   │  Client │                      │  (API SOAP)      │
   │         │                      └──────────────────┘
   └─────────┘                      ┌──────────────────┐
        ├──────────────────────────►│  Agent Traduction│
        │                           │  (WebSocket)     │
        │                           └──────────────────┘
        │                           ┌──────────────────┐
        └──────────────────────────►│  Agent Planning  │
                                    │  (gRPC)          │
                                    └──────────────────┘
   Chaque flèche = intégration propriétaire différente
   Coût : n × m combinaisons à coder, documenter, maintenir
   Résultat : aucune interopérabilité spontanée

AVEC A2A — Découverte et délégation standardisée :
                                    ┌──────────────────┐
        ┌──────────────────────────►│  Agent Billing   │
        │                           │  A2A endpoint    │
        │                           └──────────────────┘
        │                           ┌──────────────────┐
        ├──────────────────────────►│  Agent Recherche │
        │                           │  A2A endpoint    │
        │                           └──────────────────┘
   ┌────┴────┐   A2A over HTTP+SSE  ┌──────────────────┐
   │  Agent  │─────────────────────►│  Agent Support   │
   │  Client │                      │  A2A endpoint    │
   │ (A2A)   │                      └──────────────────┘
   └─────────┘                      ┌──────────────────┐
        ├──────────────────────────►│  Agent Traduction│
        │                           │  A2A endpoint    │
        │                           └──────────────────┘
        │                           ┌──────────────────┐
        └──────────────────────────►│  Agent Planning  │
                                    │  A2A endpoint    │
                                    └──────────────────┘
   Chaque flèche = même protocole (HTTP + SSE + JSON)
   Découverte automatique via Agent Card (.well-known/agent.json)
   Coût : n + m (une implémentation A2A par agent)
```

**La différence fondamentale :** Sans A2A, chaque paire d'agents négocie son format de message, son système d'authentification, son cycle de vie de tâche. Avec A2A, tout est standardisé : l'Agent Card pour la découverte, le Task lifecycle pour le suivi, les Messages & Parts pour le contenu.

---

### 5.2 Architecture A2A — Client Agent, Remote Agent et découverte

#### Définition formelle

> **Définition :** L'architecture A2A est symétrique et asynchrone. Un **Client Agent** découvre un **Remote Agent** via son **Agent Card** (fichier JSON hébergé sur le serveur de l'agent distant), puis lui envoie des tâches via des requêtes HTTP. Le Remote Agent répond avec des messages JSON et notifie le client des changements d'état via SSE (Server-Sent Events).

#### Schéma d'architecture générale

```
                            DÉCOUVERTE
                            (Agent Card)

   ┌──────────────────┐    GET /.well-known/agent.json    ┌──────────────────┐
   │                  │──────────────────────────────────►│                  │
   │   CLIENT AGENT   │◄──────────────────────────────────│   REMOTE AGENT   │
   │                  │    JSON : Agent Card              │                  │
   │  ┌────────────┐  │                                   │  ┌────────────┐  │
   │  │ A2A Client │  │         COMMUNICATION              │  │ A2A Server │  │
   │  │ Library    │  │◄══════════════════════════════════►│  │ Endpoint   │  │
   │  └─────┬──────┘  │     HTTP POST + SSE (tasks/send,  │  └─────┬──────┘  │
   │        │         │     tasks/get, tasks/cancel)       │        │         │
   │  ┌─────▼──────┐  │                                   │  ┌─────▼──────┐  │
   │  │ Orchestr.  │  │                                   │  │ Specialist │  │
   │  │ LLM        │  │                                   │  │ LLM        │  │
   │  └────────────┘  │                                   │  └────────────┘  │
   └──────────────────┘                                   └──────────────────┘
           │                                                     │
           │ MCP                                                 │ MCP
           ▼                                                     ▼
   ┌──────────────────┐                                   ┌──────────────────┐
   │    Tools         │                                   │    Tools         │
   │  (fichier, shell,│                                   │  (API, DB, web)  │
   │   web search)    │                                   │                  │
   └──────────────────┘                                   └──────────────────┘
```

#### Comparaison MCP vs A2A — architectures

| Aspect | MCP (Séance 4) | A2A (cette séance) |
|--------|----------------|-------------------|
| Direction | Agent → Outil | Agent ↔ Agent |
| Découverte | `tools/list` (JSON-RPC) | Agent Card (HTTP GET /.well-known/agent.json) |
| Transport | stdio / Streamable HTTP | HTTP + SSE |
| Format | JSON-RPC 2.0 | JSON (pas RPC, messages orientés tâche) |
| Paradigme | Requête-réponse synchrone | Tâche asynchrone avec notifications |
| Sessions | Sans état (stateless) | Avec session (session_id) |
| Auth | OAuth 2.1 + PKCE + DPoP | OAuth 2.1 + API keys |
| Usage typique | LLM → base de données, fichiers | Agent orchestrateur → agent spécialiste |

---

### 5.3 Agent Cards — La fiche d'identité d'un agent

#### Définition formelle

> **Définition :** Une **Agent Card** est un fichier JSON, hébergé à l'URL `/.well-known/agent.json` sur le domaine de l'agent, qui décrit ses capacités, son authentification, ses endpoints, et ses tarifs. C'est l'équivalent du `manifest.json` pour une Progressive Web App — un agent client la lit pour décider s'il peut déléguer sa tâche.

#### Agent Card complète commentée

```json
{
  "agent_card_version": "1.0",
  // ↑ VERSION DE LA SPÉCIFICATION AGENT CARD
  //   Permet la rétrocompatibilité : un client A2A peut lire
  //   des cartes de versions antérieures et adapter son comportement.
  //   Actuellement : "1.0".

  "name": "Research Specialist",
  // ↑ NOM DE L'AGENT (obligatoire)
  //   Identifiant lisible par un humain. Apparaît dans l'interface
  //   de découverte. Doit être unique dans l'écosystème de l'org.

  "description": "Deep research on technical topics: web search, data analysis, summarization",
  // ↑ DESCRIPTION FONCTIONNELLE (obligatoire)
  //   Texte libre que l'agent client lit pour comprendre le domaine
  //   de compétence. C'est le "pitch" de vente de l'agent.
  //   Le LLM de l'agent client peut analyser ce texte pour décider
  //   si cet agent est adapté à la tâche courante.

  "capabilities": {
    // ↑ CAPACITÉS (obligatoire)
    //   Objet décrivant ce que l'agent peut faire et ses limites.
    "skills": ["web_search", "data_analysis", "summarization"],
    // ↑ LISTE DES COMPÉTENCES (obligatoire)
    //   Tableau de chaînes décrivant les domaines d'expertise.
    //   Un client peut filtrer les agents par skill.
    //   Convention : noms en snake_case, en anglais.
    "max_tasks": 5,
    // ↑ NOMBRE MAXIMUM DE TÂCHES SIMULTANÉES (optionnel, défaut: 1)
    //   L'agent peut traiter jusqu'à 5 tâches en parallèle.
    //   Au-delà, il rejette les nouvelles tâches avec une erreur
    //   "capacity_exceeded". Le client doit alors attendre ou
    //   trouver un autre agent.
    "streaming": true
    // ↑ SUPPORT DU STREAMING (optionnel, défaut: false)
    //   true  → l'agent envoie des mises à jour partielles SSE
    //           pendant l'exécution de la tâche.
    //   false → le client doit faire du polling (tasks/get).
    //   Le streaming réduit la latence perçue pour les tâches longues.
  },

  "auth": {
    // ↑ AUTHENTIFICATION (optionnel)
    //   Si absent, l'agent est public (anonyme).
    //   Si présent, décrit comment le client doit s'authentifier.
    "type": "oauth2",
    // ↑ TYPE D'AUTH (obligatoire si auth présent)
    //   "oauth2"  → OAuth 2.1 avec PKCE (recommandé pour production)
    //   "apikey"  → clé API dans l'entête Authorization
    //   "none"    → pas d'authentification (usage interne)
    //   "mtls"    → mutual TLS (certificat client et serveur)
    "endpoint": "https://auth.example.com/token"
    // ↑ URL DU FOURNISSEUR D'AUTH (obligatoire pour oauth2)
    //   Le client redirige l'utilisateur vers cette URL pour
    //   obtenir un token d'accès. Le token est ensuite passé
    //   dans l'entête Authorization de chaque requête A2A.
  },

  "endpoints": {
    // ↑ ENDPOINTS DE COMMUNICATION (obligatoire)
    "base": "https://research.example.com/a2a",
    // ↑ URL DE BASE A2A (obligatoire)
    //   Tous les appels A2A (tasks/send, tasks/get, tasks/cancel)
    //   sont envoyés à cette URL. Le client concatène le chemin
    //   de la méthode : tasks/send → https://.../a2a/tasks/send.
    "card": "/.well-known/agent.json"
    // ↑ CHEMIN DE L'AGENT CARD (optionnel, défaut: "/.well-known/agent.json")
    //   URL (absolue ou relative) où trouver l'Agent Card.
    //   La découverte standardisée utilise .well-known/agent.json
    //   (convention inspirée de RFC 8615).
  },

  "pricing": {
    // ↑ TARIFICATION (optionnel)
    //   Permet la transparence économique entre organisations.
    //   Un client peut choisir l'agent le moins cher ou respecter
    //   un budget.
    "per_task": 0.05,
    // ↑ COÛT PAR TÂCHE (optionnel)
    //   0.05 USD par tâche soumise. La tâche est facturée
    //   quel que soit son résultat (succès ou échec).
    "currency": "USD"
    // ↑ DEVISE (optionnel, défaut: "USD")
    //   Code ISO 4217 de la devise utilisée.
  }
}
```

#### Découverte d'agents via `.well-known/agent.json`

La découverte suit une convention standardisée :

```
Étape 1 : Un agent client a besoin d'un agent spécialisé en analyse de données
          → Il interroge son registre ou explore un annuaire d'agents

Étape 2 : Le registre lui retourne l'URL d'un agent distant :
          https://research.partenariat.com/.well-known/agent.json

Étape 3 : Le client lit l'Agent Card et vérifie :
          - Les compétences correspondent (data_analysis dans skills)
          - La capacité est disponible (max_tasks pas atteint)
          - L'authentification est compatible (OAuth 2.1)
          - Le prix est acceptable (0.05 USD/tâche)

Étape 4 : Le client s'authentifie et commence à soumettre des tâches
```

---

### 5.4 Task Lifecycle — Le cycle de vie d'une tâche inter-agent

#### Définition formelle

> **Définition :** Une **Task A2A** représente une unité de travail déléguée par un Client Agent à un Remote Agent. Elle traverse un cycle d'états défini, avec des transitions explicites. Chaque changement d'état peut être notifié au client via SSE.

#### Schéma des états

```
                    ┌──────────────────────────────────────────────────┐
                    │                   TASK STATES                    │
                    │                                                  │
                    │   submitted ─────► working ─────► completed     │
                    │       │               │               │         │
                    │       │               │               │         │
                    │       ▼               ▼               ▼         │
                    │   canceled ◄────── failed ◄───────────┘         │
                    │                         │                       │
                    │                         ▼                       │
                    │                    error                        │
                    └──────────────────────────────────────────────────┘
```

#### Détail des transitions

| État | Description | Transition entrante | Transition sortante |
|------|-------------|-------------------|-------------------|
| **submitted** | La tâche a été reçue et acceptée par le Remote Agent. Le client reçoit un `task_id` unique. | Création via `tasks/send` | → `working` (traitement commencé) → `canceled` (annulation client) |
| **working** | Le Remote Agent exécute activement la tâche. Des mises à jour partielles peuvent être envoyées (streaming). | `submitted` → validation des prérequis | → `completed` (succès) → `failed` (échec) |
| **completed** | La tâche a abouti. Le résultat est disponible dans le message final. | `working` → résultat produit | Terminal |
| **failed** | La tâche a échoué pour une raison métier (données invalides, timeout, erreur interne). Le message contient le détail de l'erreur. | `working` → erreur métier | Terminal |
| **canceled** | La tâche a été annulée par le client (via `tasks/cancel`). Le Remote Agent interrompt le traitement si possible. | `submitted` ou `working` → `tasks/cancel` | Terminal |
| **error** | Erreur protocolaire ou technique. Distinct de `failed` : `failed` est une erreur métier, `error` est une erreur système. | Tout état → problème technique | Terminal |

#### Exemple de cycle complet

```
Client Agent                    Remote Agent
      │                              │
      │  POST /a2a/tasks/send        │
      │  {id, session_id, message}   │
      │─────────────────────────────►│
      │                              │  validation de la tâche
      │  202 Accepted                │
      │  {id, status: "submitted"}   │
      │◄─────────────────────────────│
      │                              │
      │                              │  début du traitement
      │  SSE: {status: "working"}    │
      │◄─────────────────────────────│
      │                              │
      │  SSE: {status: "working",    │  mise à jour partielle
      │        parts: [{...}]}       │
      │◄─────────────────────────────│
      │                              │
      │  SSE: {status: "completed",  │  résultat final
      │        parts: [{...}]}       │
      │◄─────────────────────────────│
```

#### Pourquoi le Task Lifecycle est crucial

- **Impact sur la conception :** Permet la délégation asynchrone. Le Client Agent peut soumettre plusieurs tâches en parallèle et attendre les résultats — comme un orchestrateur de microservices.
- **Conséquence si ignoré :** Les agents sont forcés à un modèle synchrone requête-réponse, bloquant le client pendant toute la durée de la tâche distante (impossible pour des tâches longues de plusieurs minutes/heures).
- **Cas d'usage typique :** Un agent orchestrateur délègue une recherche documentaire à un agent spécialisé (durée estimée : 2 minutes). Il soumet la tâche, reçoit `submitted`, puis `working`, puis `completed` avec le résultat. Pendant ce temps, il peut traiter d'autres tâches.

---

### 5.5 Messages & Parts — Le format de communication

#### Définition formelle

> **Définition :** Un **Message A2A** est une unité de communication structurée contenant un ou plusieurs **Parts** (fragments de contenu). Chaque part a un type spécifique : `text`, `file`, ou `data`. Les messages sont échangés dans le cadre d'une tâche, avec un `role` indiquant l'émetteur.

#### Structure JSON d'un message

```json
{
  "jsonrpc": "2.0",
  // ↑ VERSION DU PROTOCOLE JSON-RPC (constant)
  //   A2A utilise JSON-RPC 2.0 pour l'enveloppe des requêtes,
  //   mais le format interne des paramètres est spécifique à A2A
  //   (pas les mêmes méthodes que MCP).

  "method": "tasks/send",
  // ↑ MÉTHODE A2A (obligatoire)
  //   Les méthodes principales sont :
  //   - tasks/send     : soumettre une nouvelle tâche
  //   - tasks/get      : récupérer l'état d'une tâche (polling)
  //   - tasks/cancel   : annuler une tâche
  //   - tasks/notification : notification SSE d'un changement d'état

  "params": {
    // ↑ PARAMÈTRES DE LA REQUÊTE (obligatoire)

    "id": "task-789",
    // ↑ IDENTIFIANT DE LA TÂCHE (obligatoire)
    //   Généré par le client. Doit être unique dans la session.
    //   Format libre (UUID recommandé). Le Remote Agent utilise
    //   cet ID pour toutes les références futures.

    "session_id": "session-456",
    // ↑ IDENTIFIANT DE SESSION (optionnel)
    //   Permet de grouper plusieurs tâches dans une même session.
    //   Le Remote Agent peut maintenir un contexte de session
    //   entre les tâches. Si absent, chaque tâche est isolée.

    "message": {
      // ↑ MESSAGE CONTENANT LA REQUÊTE (obligatoire)

      "role": "agent",
      // ↑ RÔLE DE L'ÉMETTEUR (obligatoire)
      //   "agent"   : message envoyé par un agent
      //   "user"    : message provenant d'un utilisateur humain
      //   "system"  : message système (instructions, configuration)

      "parts": [
        // ↑ LISTE DE PARTS (obligatoire, au moins une)
        //   Chaque part est un fragment du message. Un message peut
        //   contenir plusieurs parts de types différents.

        {
          "type": "text",
          // ↑ TYPE DE LA PART (obligatoire)
          //   "text" : contenu textuel simple
          //   "file" : fichier (binaire ou texte) avec métadonnées
          //   "data" : données structurées (JSON)

          "text": "Analyse les logs applicatifs et résume les erreurs critiques"
          // ↑ CONTENU TEXTE (obligatoire pour type: "text")
          //   Instructions en langage naturel adressées à l'agent distant.
          //   Le Remote Agent utilise ce texte comme prompt utilisateur.
        }
      ]
    }
  }
}
```

#### Exemple de réponse avec plusieurs Parts

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "id": "task-789",
    "status": "completed",
    // ↑ ÉTAT DE LA TÂCHE (obligatoire)
    //   Un des six états du lifecycle (section 5.4).

    "message": {
      "role": "agent",
      "parts": [
        {
          "type": "text",
          // ↑ PART TEXTE
          "text": "Analyse terminée. 3 erreurs critiques trouvées.\n"
        },
        {
          "type": "file",
          // ↑ PART FICHIER
          "mime_type": "text/csv",
          //   Type MIME du fichier. Permet au client d'afficher
          //   ou traiter le fichier correctement.
          "data": "severity,count,component\ncritical,3,auth-service\nwarning,12,api-gateway\ninfo,45,cache-layer",
          //   Contenu du fichier (encodé en base64 pour les binaires).
          //   Pour les fichiers texte, le contenu peut être en clair.
          "name": "error-summary.csv"
          //   Nom de fichier suggéré pour le téléchargement.
        },
        {
          "type": "data",
          // ↑ PART DONNÉES STRUCTURÉES
          "data": {
            //   Objet JSON structuré. Pas de schéma imposé — le
            //   contenu est libre mais doit être compréhensible
            //   par l'agent client.
            "total_errors": 60,
            "critical": 3,
            "top_components": ["auth-service", "api-gateway", "cache-layer"],
            "recommendation": "Restart auth-service and investigate connection pool"
          }
        }
      ]
    }
  }
}
```

#### Les trois types de Parts en détail

| Type | Usage | Contenu | Cas d'usage typique |
|------|-------|---------|---------------------|
| `text` | Instructions, résultats textuels, résumés | Chaîne de caractères | Prompt initial, réponse LLM, description de résultat |
| `file` | Fichiers attachés (logs, rapports, images) | `data` + `mime_type` + `name` | Envoi de logs à analyser, réception de rapport CSV |
| `data` | Données structurées machine-readable | Objet JSON | Résultats d'analyse structurés, métriques, configuration |

---

### 5.6 MCP vs A2A — Complémentarité et choix architectural

#### Définition formelle

> **Définition :** MCP et A2A sont deux protocoles complémentaires, pas concurrents. MCP standardise la communication **verticale** (agent ↔ outil). A2A standardise la communication **horizontale** (agent ↔ agent). Un système agentique complet utilise les deux.

#### Schéma de la stack complète

```
                    ┌──────────────────────────────────────────────────┐
                    │               ÉCOSYSTÈME AGENTIQUE               │
                    │                                                  │
                    │  ┌────────────────────────────────────────────┐  │
                    │  │          COUCHE INTER-AGENT (A2A)          │  │
                    │  │                                            │  │
                    │  │  Agent A ◄──── A2A (HTTP+SSE) ────► Agent B│  │
                    │  │  (Client)                               (Remote)│
                    │  └──────────────────┬─────────────────────────┘  │
                    │                     │                            │
                    │                     │ A2A ou MCP                 │
                    │                     ▼                            │
                    │  ┌────────────────────────────────────────────┐  │
                    │  │          COUCHE OUTIL (MCP)                │  │
                    │  │                                            │  │
                    │  │  Agent ◄──── MCP (stdio/HTTP) ────► Tools  │  │
                    │  │                                            │  │
                    │  │  ┌────────┐ ┌────────┐ ┌────────────────┐  │  │
                    │  │  │Fichiers│ │  Base  │ │API Externe     │  │  │
                    │  │  │        │ │Données │ │(REST, GraphQL) │  │  │
                    │  │  └────────┘ └────────┘ └────────────────┘  │  │
                    │  └────────────────────────────────────────────┘  │
                    │                                                  │
                    │  ┌────────────────────────────────────────────┐  │
                    │  │       COUCHE COMMUNICATION (JSON-RPC)       │  │
                    │  │       MCP = JSON-RPC 2.0 (RPC pur)         │  │
                    │  │       A2A = JSON-RPC 2.0 (enveloppe) + SSE │  │
                    │  └────────────────────────────────────────────┘  │
                    └──────────────────────────────────────────────────┘
```

#### Tableau de complémentarité

| Critère | MCP | A2A |
|---------|-----|-----|
| **Relation** | Agent → Serveur (hiérarchique) | Agent ↔ Agent (pair-à-pair) |
| **Découverte** | `tools/list` (requête RPC) | Agent Card (HTTP GET) |
| **Modèle** | Synchrone (requête/réponse) | Asynchrone (tâche + notifications) |
| **Transport** | stdio (local), Streamable HTTP | HTTP + SSE |
| **Format** | JSON-RPC 2.0 pur | JSON-RPC 2.0 + messages orientés tâche |
| **Sessions** | Sans état | Avec session_id |
| **Streaming** | Réponse unique | Parts multiples + SSE progressif |
| **Auth** | OAuth 2.1 (distant) | OAuth 2.1 ou API key |
| **Tarification** | Pas de standard | Agent Card (pricing) |
| **Gouvernance** | Anthropic → open source | Google DeepMind → Linux Foundation |

#### Quand utiliser quel protocole

| Scénario | Protocole | Raison |
|----------|-----------|--------|
| Mon agent a besoin de lire un fichier | **MCP** | C'est agent ↔ outil, synchrone, local |
| Mon agent doit interroger une API REST | **MCP** | L'API est un outil, pas un agent |
| Mon agent doit déléguer une recherche à un spécialiste | **A2A** | C'est agent ↔ agent, asynchrone |
| Mon agent doit collaborer avec un agent d'une autre entreprise | **A2A** | Découverte standardisée, auth, pricing |
| Mon agent a besoin de ses outils internes (shell, grep) | **MCP** | Outils système classiques |
| Mon agent doit coordonner 3 agents spécialisés en parallèle | **A2A** | Orchestration multi-agents |
| Un agent expose un outil de recherche à d'autres agents | **Les deux** | MCP pour ses outils internes, A2A pour se faire découvrir |

---

### 5.7 Patterns d'utilisation 2026

| Pattern | MCP | A2A | Exemple concret |
|---------|-----|-----|-----------------|
| **Agent → Tool (environnement trusté)** | ✓ | — | Un agent opencode lit un fichier via le MCP Server `dev-assistant`. Le serveur tourne en local, pas de risque d'interception. |
| **Agent → Tool (cross-organisation)** | ✓ (avec auth) | — | Un agent interroge l'API d'un partenaire via un serveur MCP distant avec OAuth 2.1. L'API est un outil, pas un agent autonome. |
| **Agent → Agent (même runtime)** | — | ✓ | Foreman Agent (orchestrateur) délègue une tâche de recherche à un Specialist Agent. Les deux tournent dans le même processus opencode. |
| **Agent → Agent (cross-organisation)** | — | ✓ | Agent Support (entreprise A) découvre et délègue une facturation à Agent Billing (entreprise B) via A2A. Découverte via Agent Card. |
| **Agent → Agent (tâche longue, heures)** | — | ✓ | Agent Recherche soumet une tâche d'analyse de logs (durée : 30 min). Il reçoit des notifications SSE partielles. Le cycle de vie asynchrone permet de ne pas bloquer. |
| **Agent hybride (MCP + A2A)** | ✓ | ✓ | Un Agent Expert expose ses outils via MCP (en interne) et se fait découvrir via A2A (en externe). Les clients A2A lui délèguent des tâches qu'il exécute avec ses outils MCP. |

#### Pattern hybride détaillé

Le pattern le plus puissant est la **combinaison MCP + A2A** :

```
                    ┌────────────────────────────────────────────┐
                    │            AGENT SPÉCIALISTE                │
                    │                                            │
                    │  ┌────────────────────┐                    │
                    │  │  A2A Endpoint      │                    │
                    │  │  (Agent Card,      │                    │
                    │  │   tasks/send,      │                    │
                    │  │   SSE notifications)│                    │
                    │  └────────┬───────────┘                    │
                    │           │                                 │
                    │  ┌────────▼───────────┐                    │
                    │  │  Agent LLM         │                     │
                    │  │  (big-pickle)      │                     │
                    │  └────────┬───────────┘                    │
                    │           │                                 │
                    │  ┌────────▼───────────┐                    │
                    │  │  MCP Client        │                     │
                    │  │  tools/list        │                     │
                    │  │  tools/call        │                     │
                    │  └────────┬───────────┘                    │
                    │           │                                 │
                    └───────────┼─────────────────────────────────┘
                                │
                    ┌───────────▼─────────────────────────────────┐
                    │         MCP SERVERS                         │
                    │  ┌──────────┐ ┌──────────┐ ┌────────────┐  │
                    │  │Base de   │ │API       │ │File System │  │
                    │  │Données   │ │Externe   │ │            │  │
                    │  └──────────┘ └──────────┘ └────────────┘  │
                    └────────────────────────────────────────────┘

  Fonctionnement :
  1. Un Client Agent découvre l'Agent Spécialiste via A2A (Agent Card)
  2. Le client soumet une tâche via tasks/send (A2A)
  3. L'Agent Spécialiste reçoit la tâche et la traite avec son LLM
  4. Pendant le traitement, il utilise MCP pour accéder à ses outils
  5. Il envoie des notifications SSE partielles (A2A)
  6. Une fois terminé, il retourne le résultat via SSE (A2A)
```

---

### 5.8 Convergence 2026-2027 — L'avenir des protocoles agentiques

| Initiative | Acteur | État 2026 | Impact |
|-----------|--------|-----------|--------|
| **ADK (Agent Development Kit)** | Google | Intègre nativement MCP + A2A | Premier framework unifié : les agents ADK découvrent des outils via MCP et collaborent via A2A |
| **LangGraph A2A support** | LangChain | En développement | Les graphes LangGraph pourront exposer des endpoints A2A et appeler des agents distants |
| **CrewAI A2A integration** | CrewAI | Roadmap 2026 Q3 | Les équipes CrewAI pourront intégrer des agents externes via A2A |
| **A2A v1.0 specification** | Linux Foundation | Juin 2026 | Version stable du protocole, gel des breaking changes |
| **Agent registries** | Multiples | Émergence | Annuaires d'agents avec recherche par skills, notation, tarifs |
| **MCP → A2A bridge** | Communauté | Prototypes | Un serveur MCP qui expose ses outils comme un agent A2A (bridge automatique) |

**Tendance clé :** La frontière entre MCP et A2A s'estompe. Un agent A2A utilise MCP pour ses outils internes. Un serveur MCP peut être enveloppé dans une interface A2A pour être découvert par d'autres agents. À terme, les frameworks agentiques intégreront les deux protocoles nativement, rendant la distinction transparente pour le développeur.

---

## Synthèse

**Ce que vous avez appris dans cette séance :**

| Concept | Résumé | Section |
|---------|--------|--------|
| Problème n × m inter-agents | Sans A2A, chaque paire d'agents nécessite une intégration propriétaire. A2A standardise la découverte, la délégation et le suivi. | 5.1 |
| Architecture A2A | Client Agent découvre un Remote Agent via Agent Card, puis communique par tâches asynchrones (HTTP + SSE). | 5.2 |
| Agent Card | Fichier JSON décrivant nom, compétences, auth, endpoints, tarifs. Hébergé à `/.well-known/agent.json`. | 5.3 |
| Task Lifecycle | Six états : submitted → working → completed/failed/canceled/error. Notifications SSE à chaque transition. | 5.4 |
| Messages & Parts | Format JSON avec trois types de parts : text (instructions), file (fichiers), data (données structurées). | 5.5 |
| MCP vs A2A | MCP = agent ↔ outil (vertical). A2A = agent ↔ agent (horizontal). Complémentaires, pas concurrents. | 5.6 |
| Patterns 2026 | Du simple tool local aux équipes cross-organisation avec tâches longues. Le pattern hybride MCP + A2A est le plus puissant. | 5.7 |
| Convergence | Google ADK, LangGraph, CrewAI intègrent les deux protocoles. A2A v1.0 prévue pour juin 2026. | 5.8 |

**Lien avec la séance suivante :**

> *"Maintenant que vous savez faire collaborer des agents entre eux via A2A, la séance 6 (GitHub Agents & Platform) vous montrera comment intégrer ces concepts dans un environnement de développement concret. GitHub Agents peut jouer le rôle de client A2A dans un workflow CI/CD, découvrant des agents spécialisés pour la revue de code, les tests de sécurité, ou l'analyse de performance. Les agents que vous configurerez dans GitHub utiliseront MCP en interne et A2A pour la coordination inter-agents."*

**Lab associé :** `lab/README.md` — Partie 5 (CrewAI) et Partie 8 (Intégration finale). Le lab vous guidera dans la construction d'un agent et l'intégration complète de tous les composants.

## Références contextualisées

- **[Specification A2A — a2aprotocol.org (2026)]**
  *Contexte :* Spécification officielle du protocole, maintenue par la Linux Foundation (AI & Data Foundation). Document de référence pour tous les détails d'implémentation : Agent Card schema, Task lifecycle, Messages & Parts, endpoints API. Source principale des sections 5.2 à 5.5.
  *Niveau de lecture :* technique
  *→ https://a2aprotocol.org*

- **[Google DeepMind, "A2A: A New Era of Agent Interoperability" (2025)]**
  *Contexte :* Annonce fondatrice du protocole par Google DeepMind. Explique la vision, les 50+ partenaires fondateurs, et le positionnement par rapport à MCP. Cité en section 5.1 pour le contexte historique.
  *Niveau de lecture :* introduction
  *→ https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/*

- **[Linux Foundation AI & Data — A2A Governance (2026)]**
  *Contexte :* Détail de la gouvernance ouverte du protocole. Décrit le processus de contribution, les working groups, et le calendrier de release. Source des informations sur A2A v1.0 (section 5.8).
  *Niveau de lecture :* introduction
  *→ https://aianddata.linuxfoundation.org/*

- **[Google ADK Documentation — A2A + MCP Integration (2026)]**
  *Contexte :* Documentation technique du Google Agent Development Kit, premier framework à intégrer nativement MCP et A2A. Montre comment un même agent peut utiliser MCP pour ses outils et A2A pour la collaboration. Référence pour la section 5.8.
  *Niveau de lecture :* avancé
  *→ https://google.github.io/adk/*

- **[LangGraph Documentation — Agent-to-Agent (2026)]**
  *Contexte :* Documentation LangGraph sur les patterns multi-agents. Explique comment orchestrer des sous-graphes qui peuvent être exposés comme des agents A2A. Utile pour comprendre comment A2A s'intègre dans LangGraph (section 5.8).
  *Niveau de lecture :* avancé
  *→ https://langchain-ai.github.io/langgraph/*

- **[OWASP LLM Top 10 (2025)]**
  *Contexte :* Guide de sécurité pour les applications LLM. Les risques spécifiques aux systèmes multi-agents (délégation non autorisée, empoisonnement d'Agent Card, exfiltration de données via Parts) sont couverts respectivement par LLM06 (Excessive Agency) et LLM02 (Data Poisoning). À consulter avant de déployer des agents A2A en production.
  *Niveau de lecture :* avancé
  *→ https://owasp.org/www-project-top-10-for-llm-applications/*
