# Séance 4 — Model Context Protocol (MCP)

## Introduction théorique

**Quel est le problème fondamental ?**

Un agent LLM isolé ne peut que générer du texte. Pour agir sur le monde réel — lire un fichier, interroger une base de données, exécuter du code, envoyer un message — il doit communiquer avec des outils externes. Sans standard, chaque intégration est un prototype artisanal : API REST custom, parsing ad-hoc, documentation périssable. Le problème se généralise en **n × m combinaisons** : n fournisseurs de LLM × m outils = n × m intégrations à écrire et maintenir. Le Model Context Protocol (MCP) réduit cette complexité à **n + m** via un protocole unique que tout LLM et tout outil peut implémenter une fois.

**Contexte 2025-2026 :**

Annoncé par Anthropic fin 2024, MCP a connu une adoption fulgurante en 2025-2026. Les SDKs MCP dépassent **97 millions de téléchargements par mois**. OpenAI, Google, Microsoft, et des centaines d'éditeurs (GitHub, GitLab, Notion, Figma) ont adopté le protocole. En 2026, MCP est devenu le standard de facto pour l'intégration LLM-outils, au point que les trois quarts des nouveaux outils SaaS proposent nativement un endpoint MCP.

**Liens avec les séances :**

| Séance | Lien |
|--------|------|
| Séance 3 — Mémoire agentique | MCP étend les capacités de l'agent au-delà de la mémoire interne vers des outils externes. L'agent peut stocker/récupérer des données via un serveur MCP plutôt que dans son seul contexte. |
| **→ Séance 4 (celle-ci)** | **MCP : standard de communication agent ↔ outils** |
| Séance 5 — A2A Protocol | MCP standardise agent↔outil, A2A standardise agent↔agent. Les deux protocoles sont complémentaires : un agent MCP peut exposer des outils qu'un autre agent découvre via A2A. |
| Séance 6 — GitHub Agents | GitHub Actions supporte nativement MCP. Les workflows CI/CD peuvent déclencher des serveurs MCP locaux, ouvrant la voie à des agents de review, test et déploiement. |

> **Exemple fil rouge :** "Dans la séance 3, vous avez appris à donner une mémoire à un agent. Dans cette séance, vous allez lui donner des outils : lire des fichiers, chercher du code, exécuter Python. MCP est le protocole qui rend cette communication possible, standardisée et sécurisée."

## Objectifs pédagogiques

À l'issue de cette séance, vous serez capable de :

1. **Analyser** le problème n × m des intégrations LLM-outils et expliquer comment MCP le résout en **une phrase d'analogie** (USB pour LLM)
2. **Schématiser** l'architecture MCP (Host/Client/Server) et ses trois modes de transport (stdio, HTTP+SSE, Streamable HTTP) avec leurs cas d'usage respectifs
3. **Distinguer** les trois primitives MCP (Resources, Prompts, Tools) et **associer** chacune à un cas d'usage concret dans un assistant de développement
4. **Implémenter** un serveur MCP fonctionnel en Python avec le SDK officiel, en commentant chaque ligne en français
5. **Configurer** l'intégration MCP dans `opencode.json` et **décortiquer** chaque champ JSON avec son rôle et ses implications de sécurité

## Plan détaillé

### 4.1 Pourquoi MCP ? — Du chaos n × m à l'interopérabilité standardisée

#### Définition formelle

> **Définition :** Le Model Context Protocol (MCP) est un protocole standardisé de type JSON-RPC 2.0 qui permet à un agent LLM (le *host*) de découvrir et d'invoquer des outils, ressources et prompts exposés par des serveurs externes, via un canal de communication bidirectionnel.

#### Analogie pédagogique

> *"MCP est au LLM ce que USB-C est à l'ordinateur : avant USB, chaque périphérique avait son câble et son driver propriétaire. Avec USB, un seul port, un seul protocole, des milliers de périphériques interchangeables. MCP fait la même chose pour les outils des LLMs."*

#### Le problème n × m en détail

```
SANS MCP :                       AVEC MCP :
n LLMs × m outils               n LLMs + m outils
= n×m intégrations              = n+m intégrations

LLM A ──API₁──► Outil 1         LLM A ──┐
LLM A ──API₂──► Outil 2                 ├──MCP──► Outil 1
LLM A ──API₃──► Outil 3                 │        Outil 2
LLM B ──API₁──► Outil 1         LLM B ──┘        Outil 3
LLM B ──API₂──► Outil 2
LLM B ──API₃──► Outil 3
```

Chaque case du tableau de gauche est une intégration à écrire, documenter, tester, maintenir. MCP remplace les n×m connexions propriétaires par n+l connexions standardisées.

#### Adoption et acteurs

| Acteur | Rôle | Adoption MCP |
|--------|------|--------------|
| Anthropic | Créateur du standard | Claude Desktop, SDKs officiels |
| OpenAI | Adoptant majeur | Compatible ChatGPT (2025) |
| Google | Adoptant majeur | Gemini, Vertex AI |
| Microsoft | Intégrateur plateforme | VS Code, GitHub Copilot, Azure AI |
| Éditeurs SaaS | Fournisseurs d'outils | Notion, Figma, GitLab, Linear, Supabase |
| Communauté OSS | Développeurs de serveurs | 3000+ serveurs MCP open source |

**Chiffres clés 2026 :**
- **97M+** téléchargements/mois des SDKs MCP (PyPI + npm cumulés)
- **3000+** serveurs MCP open source répertoriés
- Support natif dans VS Code, JetBrains, GitHub Copilot

---

### 4.2 Architecture détaillée — Host, Client, Server & Transports

#### Définition formelle

> **Définition :** L'architecture MCP est triadique : un **Host** (l'application LLM) héberge un **Client** MCP qui se connecte à un **Server** MCP exposant des primitives. La communication suit JSON-RPC 2.0 sur un transport bidirectionnel.

#### Schéma d'architecture générale

```
┌─────────────────────────────────────────────────────────┐
│                       HOST                               │
│  (Application LLM : opencode, Claude Desktop, VS Code)  │
│                                                          │
│  ┌────────────────────┐    ┌────────────────────────┐   │
│  │       LLM          │    │    MCP Client          │   │
│  │  (big-pickle)      │◄──►│  - Découverte outils   │   │
│  │  Génère réponses   │    │  - Invoque tools       │   │
│  │  Planifie actions  │    │  - Lit resources       │   │
│  └────────────────────┘    │  - Gère notifications  │   │
│                            └───────────┬────────────┘   │
└────────────────────────────────────────┼────────────────┘
                                         │
                          JSON-RPC 2.0   │
                     (requête/réponse)   │
                                         │
                    ┌────────────────────▼──────────────┐
                    │          MCP SERVER                │
                    │                                   │
                    │  ┌─────────┐ ┌───────┐ ┌──────┐  │
                    │  │  Tools  │ │Resources│ │Prompts│ │
                    │  │ read_file│ │docs://  │ │review │ │
                    │  │search_cd│ │db://    │ │debug  │ │
                    │  │run_pythn│ │file://  │ │refact │ │
                    │  └─────────┘ └───────┘ └──────┘  │
                    └──────────────────────────────────┘
```

#### Les trois modes de transport

MCP définit trois transports, chacun adapté à un contexte d'exécution :

**1. stdio — Serveurs locaux (développement)**

```
┌──────HOST──────┐    Processus unique     ┌───MCP SERVER───┐
│  opencode CLI  │◄──────stdin/stdout─────►│  server.py     │
│  (big-pickle)  │    JSON-RPC 2.0 ligne   │  (subprocess)  │
└────────────────┘    (lecture/écriture)    └────────────────┘

Fonctionnement :
1. opencode lance `python server.py` (fork d'un subprocess)
2. opencode écrit des requêtes JSON sur stdin du serveur
3. Le serveur lit stdin, traite, écrit la réponse sur stdout
4. opencode lit stdout, parse la réponse JSON
5. Le cycle continue jusqu'à l'arrêt du serveur

Avantages : zéro réseau, zéro latence réseau, isolation process
Cas d'usage : développement local, outils système (fichiers, shell)
```

**2. HTTP + SSE — Serveurs distants (production — en dépréciation)**

```
┌──────HOST──────┐                     ┌───MCP SERVER───┐
│  Client MCP    │   POST /messages    │  Serveur HTTP  │
│                │◄────────────────────│  (FastAPI/Express)
│  Écoute SSE    │   SSE stream        │                │
│  /events       │────────────────────►│                │
└────────────────┘                     └────────────────┘

Fonctionnement :
1. Client envoie requête HTTP POST au serveur
2. Serveur répond via Server-Sent Events (SSE)
3. Canal unidirectionnel pour les notifications

Problème : nécessite deux connexions, scaling complexe
État 2026 : déprécié au profit de Streamable HTTP
```

**3. Streamable HTTP — Nouveau standard remote**

```
┌──────HOST──────┐   HTTP POST/GET      ┌───MCP SERVER───┐
│  Client MCP    │◄────────────────────►│  Serveur HTTP  │
│                │   Stateless          │  (Fastify/axum)│
│                │   Sessions via header │                │
└────────────────┘                     └────────────────┘

Fonctionnement :
1. Requête HTTP unique = un échange MCP
2. Session identifiée par entête `mcp-session-id`
3. Support streaming via chunked transfer encoding
4. Pas de connexion persistante → scaling horizontal facile

Avantages : stateless, scalable, compatible CDN
Cas d'usage : production, microservices, edge computing
```

#### Pourquoi MCP est crucial

- **Impact sur la conception :** Un agent n'est plus limité à son contexte textuel. Il peut interagir avec le système de fichiers, le réseau, les bases de données, les APIs — le tout via un protocole unique.
- **Conséquence si ignoré :** Chaque intégration est un cas spécial. L'architecture devient un plateau de spaghetti impossible à maintenir. L'agent est confiné à la génération de texte.
- **Cas d'usage typique :** Un assistant de développement qui lit des fichiers, cherche du code, exécute des tests, commit du code — tout cela via des serveurs MCP.

---

### 4.3 Les primitives MCP en détail — Resources, Prompts, Tools

MCP définit trois primitives fondamentales. Chacune répond à un besoin différent de l'interaction LLM↔monde extérieur.

---

#### Primitive 1 : Resources — Données contextuelles

##### Définition formelle

> **Définition :** Une Resource MCP est une source de données identifiée par une URI, qui expose du contenu textuel ou binaire au host. Le LLM peut lire ces données pour enrichir son contexte. Les resources sont **lecture seule**.

##### Schéma conceptuel

```
┌──────────┐   "dis-moi ce que tu as"    ┌──────────────┐
│          │────────────────────────────►│              │
│   LLM    │   resources/list            │  MCP Server  │
│          │◄────────────────────────────│              │
│          │   ["docs://guide",          │  ┌─────────┐ │
│          │    "file:///logs/app.log"]  │  │ Resource │ │
│          │                             │  │  Store   │ │
│          │   "donne-moi docs://guide"  │  └─────────┘ │
│          │────────────────────────────►│              │
│          │   resources/read            │              │
│          │◄────────────────────────────│              │
│          │   "# MCP Guide\nJSON-RPC..."│              │
└──────────┘                             └──────────────┘
```

##### API JSON-RPC

| Méthode | Description |
|---------|-------------|
| `resources/list` | Liste les resources disponibles (avec métadonnées) |
| `resources/read` | Lit le contenu d'une resource par son URI |
| `resources/subscribe` | S'abonne aux changements d'une resource |
| `resources/unsubscribe` | Se désabonne |

##### Exemple JSON complet — resources/list

```json
// Requête : le host demande la liste des resources
{
  "jsonrpc": "2.0",
  "method": "resources/list",
  "params": {},
  "id": 1
}

// Réponse : le serveur retourne les resources disponibles
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "resources": [
      {
        "uri": "docs://agent-patterns",
        // ↑ URI unique de la resource. Le host utilise cet URI
        //   dans resources/read pour récupérer le contenu.
        "name": "Agent Design Patterns",
        // ↑ Nom lisible par un humain. Sert d'étiquette dans l'interface.
        "description": "Common agent architecture patterns",
        // ↑ Description courte. Le LLM peut s'en servir pour décider
        //   si cette resource est pertinente pour sa tâche.
        "mimeType": "text/markdown"
        // ↑ Type MIME optionnel. Par défaut text/plain.
        //   Permet au host d'afficher correctement le contenu.
      },
      {
        "uri": "docs://mcp-guide",
        "name": "MCP Quick Reference",
        "description": "MCP protocol summary",
        "mimeType": "text/markdown"
      }
    ]
  }
}
```

##### Cas d'usage concret

Un serveur MCP expose des fichiers de documentation. Le LLM les lit au besoin pour répondre à une question sur l'architecture :

```python
# Le LLM demande : "quel est le pattern ReAct ?"
# Le host appelle resources/read("docs://agent-patterns")
# Le serveur retourne le contenu markdown
# Le LLM lit la description du pattern et peut répondre
```

---

#### Primitive 2 : Prompts — Templates de messages

##### Définition formelle

> **Définition :** Un Prompt MCP est un template de message pré-construit, stocké côté serveur, que l'utilisateur (ou le LLM) peut invoquer pour générer rapidement un message structuré. C'est l'équivalent des "snippets" pour les conversations LLM.

##### API JSON-RPC

| Méthode | Description |
|---------|-------------|
| `prompts/list` | Liste les prompts disponibles |
| `prompts/get` | Récupère un prompt avec ses arguments résolus |

##### Exemple JSON complet — prompts/get

```json
// Requête : le host demande un template de revue de code
{
  "jsonrpc": "2.0",
  "method": "prompts/get",
  "params": {
    "name": "review-code",
    "arguments": {
      "language": "python",
      "file_path": "src/main.py"
    }
  },
  "id": 2
}

// Réponse : le serveur retourne un message pré-construit
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "description": "Template de revue de code Python",
    "messages": [
      {
        "role": "user",
        "content": {
          "type": "text",
          "text": "Tu es un reviewer de code Python expert.\n"
                  "Analyse le fichier src/main.py et cherche :\n"
                  "1. Bugs potentiels\n"
                  "2. Violations PEP 8\n"
                  "3. Suggestions de refactoring\n"
                  "4. Problèmes de sécurité\n\n"
                  "Fichier à analyser : src/main.py"
        }
      }
    ]
  }
}
```

##### Cas d'usage

Les prompts MCP évitent de répéter des instructions complexes. Un serveur MCP pour assistant de développement peut exposer : `review-code`, `debug-error`, `write-test`, `refactor-module`. Chaque prompt est un template paramétré, maintenu à jour au niveau du serveur.

---

#### Primitive 3 : Tools — Fonctions exécutables

##### Définition formelle

> **Définition :** Un Tool MCP est une fonction exécutable exposée par le serveur, découvrable via `tools/list` et invocable via `tools/call`. Le LLM décide d'appeler un tool pendant sa génération, sur la base de sa description et de son schéma de paramètres.

##### Schéma conceptuel

```
┌──────────┐                           ┌──────────────┐
│          │   "quels outils as-tu ?"   │              │
│   LLM    │──────────────────────────►│  MCP Server  │
│          │   tools/list              │              │
│          │◄──────────────────────────│  ┌─────────┐ │
│          │   ["read_file(path)",     │  │  Tools   │ │
│          │    "search_code(pattern)"]│  │   Registry│ │
│          │                           │  └─────────┘ │
│          │   tools/call("read_file", │              │
│          │    {path:"main.py"})      │              │
│          │──────────────────────────►│              │
│          │◄──────────────────────────│              │
│          │   "def hello():\n ..."   │              │
└──────────┘                           └──────────────┘
```

##### API JSON-RPC

| Méthode | Description |
|---------|-------------|
| `tools/list` | Liste les outils avec leurs schémas de paramètres |
| `tools/call` | Invoque un outil avec des arguments |

##### Exemple JSON complet — tools/list

```json
// Requête : le host découvre les outils disponibles
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "params": {},
  "id": 3
}

// Réponse : le serveur décrit ses outils avec JSON Schema
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "tools": [
      {
        "name": "read_file",
        // ↑ Nom de l'outil. C'est ce que le LLM utilise dans
        //   tools/call pour l'invoquer. Doit être unique.
        "description": "Read a file from disk",
        // ↑ Description libre. Le LLM lit ce texte pour comprendre
        //   ce que fait l'outil. Crucial pour le choix de l'outil.
        "inputSchema": {
          // ↑ JSON Schema décrivant les paramètres attendus.
          "type": "object",
          "properties": {
            "path": {
              "type": "string",
              "description": "Chemin absolu ou relatif du fichier"
            }
          },
          "required": ["path"]
          // ↑ Liste des champs obligatoires.
          //   Sans "path", l'outil ne peut pas fonctionner.
        }
      }
    ]
  }
}
```

##### Exemple JSON complet — tools/call

```json
// Requête : le LLM décide d'invoquer read_file
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "read_file",
    "arguments": {
      "path": "main.py"
    }
  },
  "id": 4
}

// Réponse : le serveur exécute et retourne le résultat
{
  "jsonrpc": "2.0",
  "id": 4,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "def hello():\n    print(\"Hello, World!\")"
      }
    ],
    "isError": false
    // ↑ Drapeau indiquant si l'exécution a échoué.
    //   Le LLM peut adapter sa réponse en fonction.
  }
}
```

##### Nouveauté 2026 : outputSchema

```json
{
  "name": "search_code",
  "description": "Search for patterns in code",
  "inputSchema": {
    "type": "object",
    "properties": {
      "pattern": { "type": "string", "description": "Regex pattern" }
    },
    "required": ["pattern"]
  },
  "outputSchema": {
    // ↑ NOUVEAU 2026 : décrit la structure de la sortie.
    //   Permet au LLM de parser le résultat automatiquement.
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "file": { "type": "string" },
        "line": { "type": "integer" },
        "content": { "type": "string" }
      }
    }
  }
}
```

---

### 4.4 Construction guidée — Serveur MCP pas à pas

Cette section analyse **chaque ligne** du fichier `lab/code/02_mcp_server/server.py`. Lisez le fichier dans son ensemble d'abord, puis chaque bloc commenté.

```python
# === LAB — PARTIE 2 : SERVEUR MCP ===
# Fichier : lab/code/02_mcp_server/server.py
# Rôle    : Serveur MCP qui expose des outils de développement
#           (lecture fichier, recherche code, exécution Python)
#           à un agent opencode via le transport stdio.
# Dépendances :
#   - mcp>=1.0.0  (SDK officiel MCP)
#   - anyio>=4.0  (runtime asynchrone pour MCP)
#
# Ce serveur implémente un serveur MCP "local" : il est lancé
# par opencode en tant que subprocess et communique via stdin/stdout.
# L'agent opencode peut ainsi lire des fichiers, chercher du code
# et exécuter Python — comme s'il avait un terminal.

# --- IMPORTS ---

import subprocess
# ↑ module standard Python pour lancer des processus shell.
#   Utilisé par l'outil "search_code" (grep) et "run_python" (python3).
#   subprocess.run() est l'API moderne (remplace os.system()).

from mcp.server import Server
# ↑ Classe principale du SDK MCP. On crée une instance de Server
#   qui enregistre nos outils, resources et prompts.
#   Le server gère automatiquement le protocole JSON-RPC 2.0 :
#   - Réception des requêtes sur stdin
#   - Dispatch vers la bonne méthode (list_tools, call_tool...)
#   - Envoi des réponses sur stdout

from mcp.types import Tool, Resource, TextContent
# ↑ Types du SDK MCP :
#   - Tool        : définit un outil (nom, description, inputSchema)
#   - Resource    : définit une resource (uri, name, description)
#   - TextContent : wrapper pour le contenu textuel des réponses.
#                  MCP peut retourner plusieurs types (text, image,
#                  embedded resource). TextContent est le plus courant.

# --- INSTANCIATION DU SERVEUR ---

app = Server("dev-assistant")
# ↑ On crée une instance de Server avec le nom "dev-assistant".
#   Ce nom est l'identifiant du serveur. Il apparaît dans les logs
#   et dans la configuration opencode.json (champ "dev-assistant"
#   dans "mcp").

# --- OUTIL 1 : read_file ---

@app.list_tools()
async def list_tools():
    # ↑ DÉCORATEUR @app.list_tools()
    #   Enregistre une fonction qui sera appelée par MCP quand
    #   le host (opencode) envoie une requête "tools/list".
    #   La fonction DOIT être asynchrone (async def).
    #
    #   Ce décorateur transforme la méthode en "gestionnaire de
    #   découverte". opencode appelle cette méthode au démarrage
    #   pour savoir quels outils sont disponibles.
    return [
        Tool(
            # ↑ Tool est un tuple nommé du SDK MCP.
            #   Chaque outil a : name, description, inputSchema.
            name="read_file",
            # ↑ Identifiant unique de l'outil.
            description="Read a file from disk",
            # ↑ Description en langage naturel. Le LLM lit ce texte
            #   pour décider si cet outil correspond à sa tâche.
            inputSchema={
                # ↑ JSON Schema (draft-07) qui décrit les paramètres.
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Chemin du fichier à lire"
                    }
                },
                "required": ["path"],
            },
            #   Le LLM voit ce schéma et génère automatiquement
            #   des arguments valides au format JSON.
        ),
        Tool(
            name="search_code",
            description="Search for patterns in code",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern": {"type": "string"},
                    # ↑ Paramètre obligatoire : le motif à chercher.
                    "path": {
                        "type": "string",
                        "default": "."
                    },
                    # ↑ Paramètre optionnel : où chercher.
                    #   Par défaut, le répertoire courant.
                },
                "required": ["pattern"],
            },
        ),
        Tool(
            name="run_python",
            description="Execute Python code safely",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Code Python à exécuter"
                    }
                },
                "required": ["code"],
            },
        ),
    ]

# --- GESTIONNAIRE D'APPEL D'OUTILS ---

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    # ↑ DÉCORATEUR @app.call_tool()
    #   Enregistre la fonction qui sera appelée par MCP quand
    #   le host envoie une requête "tools/call".
    #
    #   Paramètres :
    #     - name      : le nom de l'outil à invoquer
    #     - arguments : dict des paramètres (selon inputSchema)
    #
    #   Retour : list[TextContent] — un ou plusieurs contenus texte.
    #   Chaque TextContent a un champ "type" (ici "text") et un
    #   champ "text" avec le résultat.
    #
    #   IMPORTANT : cette fonction est appelée par opencode quand
    #   un agent décide (via son LLM) d'utiliser un outil. Par ex. :
    #   1. L'agent a besoin de lire "main.py"
    #   2. Le LLM génère : tools/call("read_file", {path:"main.py"})
    #   3. Le host envoie la requête JSON-RPC au serveur
    #   4. Cette fonction est invoquée avec name="read_file"
    #   5. On exécute la logique et on retourne le résultat
    #   6. Le LLM reçoit le texte et peut continuer sa génération

    if name == "read_file":
        # ↑ On vérifie quel outil est demandé.
        #   Chaque outil a sa propre logique métier.
        with open(arguments["path"]) as f:
            # ↑ open() en lecture. arguments["path"] vient du LLM.
            #   ATTENTION : pas de validation de chemin ici.
            #   Un agent malveillant pourrait lire /etc/passwd.
            #   → Voir section 4.6 Sécurité pour les bonnes pratiques.
            return [TextContent(type="text", text=f.read())]
        # ↑ On retourne le contenu du fichier dans un TextContent.
        #   Le LLM reçoit ce texte et l'utilise comme contexte.

    elif name == "search_code":
        # ↑ Outil de recherche : exécute grep dans un subprocess.
        result = subprocess.run(
            ["grep", "-rn", arguments["pattern"], arguments.get("path", ".")],
            # ↑ Commande : grep -rn <pattern> <path>
            #   -r : récursif
            #   -n : affiche les numéros de ligne
            #   arguments.get("path", ".") : chemin par défaut = "."
            capture_output=True,
            # ↑ Capture stdout et stderr au lieu de les afficher.
            text=True,
            # ↑ Retourne des chaînes (pas des bytes).
            timeout=10,
            # ↑ Timeout de 10s. Sans ça, un pattern foireux pourrait
            #   bloquer le serveur indéfiniment.
        )
        return [
            TextContent(
                type="text",
                text=result.stdout[:3000] or "No matches"
            )
        ]
        # ↑ On tronque à 3000 caractères pour éviter de noyer
        #   le contexte du LLM. Si pas de résultat, on retourne
        #   "No matches".

    elif name == "run_python":
        # ↑ Outil d'exécution Python : lance python3 -c <code>.
        result = subprocess.run(
            ["python3", "-c", arguments["code"]],
            # ↑ -c : execute le code Python passé en argument.
            #   ATTENTION : c'est une exécution arbitraire !
            #   Un agent pourrait faire :
            #   run_python("import os; os.remove('important.db')")
            #   → Voir section 4.6 pour les sandboxing.
            capture_output=True,
            text=True,
            timeout=10,
        )
        return [
            TextContent(
                type="text",
                text=result.stdout + result.stderr
            )
        ]
        # ↑ On concatène stdout et stderr. Le LLM reçoit les deux
        #   pour comprendre ce qui s'est passé (succès ou erreur).

    raise ValueError(f"Unknown tool: {name}")
    # ↑ Si le nom de l'outil ne correspond à aucun cas connu,
    #   on lève une exception. MCP transforme ça en réponse
    #   d'erreur JSON-RPC (code -32602).

# --- GESTIONNAIRE DE RESSOURCES ---

@app.list_resources()
async def list_resources():
    # ↑ DÉCORATEUR @app.list_resources()
    #   Enregistre la fonction pour les requêtes "resources/list".
    #   Ici, on expose des documents d'aide en lecture seule.
    return [
        Resource(
            uri="docs://agent-patterns",
            # ↑ URI unique. Suit le format scheme://path.
            #   Le host utilise cet URI dans resources/read.
            name="Agent Design Patterns",
            description="Common agent architecture patterns",
        ),
        Resource(
            uri="docs://mcp-guide",
            name="MCP Quick Reference",
            description="MCP protocol summary",
        ),
    ]

@app.read_resource()
async def read_resource(uri: str):
    # ↑ DÉCORATEUR @app.read_resource()
    #   Gère les requêtes "resources/read". Reçoit un URI
    #   et retourne le contenu correspondant.
    docs = {
        "docs://agent-patterns": (
            "# Patterns\n1. ReAct Loop\n2. Plan-Execute\n"
            "3. Supervisor\n4. Reflection\n5. Tool-use"
        ),
        "docs://mcp-guide": (
            "# MCP\n- JSON-RPC 2.0\n"
            "- Primitives: Tools, Resources, Prompts\n"
            "- Transports: stdio, HTTP+SSE"
        ),
    }
    return TextContent(type="text", text=docs.get(uri, ""))
    # ↑ docs.get(uri, "") : si l'URI n'existe pas, on retourne
    #   une chaîne vide plutôt que de lever une erreur.

# --- POINT D'ENTRÉE ---

if __name__ == "__main__":
    # ↑ Condition Python standard : ce bloc s'exécute UNIQUEMENT
    #   quand le fichier est lancé directement (python server.py),
    #   PAS quand il est importé comme module.
    from mcp.server.stdio import stdio_server
    # ↑ Import du transport stdio : un adaptateur qui lit les
    #   requêtes JSON-RPC sur stdin et écrit les réponses sur stdout.
    #   C'est le transport par défaut pour les serveurs locaux.
    import anyio
    # ↑ Bibliothèque d'async/await. MCP utilise anyio pour le
    #   runtime asynchrone (compatible asyncio et trio).

    anyio.run(stdio_server, app)
    # ↑ anyio.run() démarre la boucle d'événements asynchrone.
    #   stdio_server(app) est une coroutine qui :
    #   1. Lit les lignes JSON-RPC sur stdin
    #   2. Les parse et les dispatche vers les décorateurs
    #   3. Écrit les réponses JSON-RPC sur stdout
    #   4. Continue jusqu'à EOF sur stdin (quand opencode arrête
    #      le serveur ou ferme le subprocess)
    #
    #   Concrètement, après cette ligne, le serveur écoute en
    #   boucle, comme un serveur HTTP mais sur stdio :
    #
    #   ┌─────────────────────────────────────────────────┐
    #   │  opencode (host)          server.py (subprocess) │
    #   │                                                │
    #   │  Étape 1 : Découverte                           │
    #   │  ─────────────────                              │
    #   │  ──stdin──► {"jsonrpc":"2.0",                   │
    #   │              "method":"tools/list","id":1}      │
    #   │  ◄─stdout── {"jsonrpc":"2.0","id":1,            │
    #   │              "result":{"tools":[...]}}          │
    #   │                                                │
    #   │  Étape 2 : Utilisation                          │
    #   │  ─────────────────                              │
    #   │  ──stdin──► {"jsonrpc":"2.0",                   │
    #   │              "method":"tools/call",             │
    #   │              "params":{"name":"read_file",      │
    #   │              "arguments":{"path":"main.py"}},   │
    #   │              "id":2}                            │
    #   │  ◄─stdout── {"jsonrpc":"2.0","id":2,            │
    #   │              "result":{"content":[...]}}        │
    #   └─────────────────────────────────────────────────┘
```

#### Comment le serveur se connecte à opencode

Le mécanisme est simple :

1. opencode lit la section `mcp` de `opencode.json`
2. Pour chaque serveur avec `"enabled": true`, opencode lance la commande (`"command": ["python", "lab/code/02_mcp_server/server.py"]`)
3. opencode écrit des messages JSON-RPC 2.0 sur le **stdin** du subprocess
4. Le serveur lit stdin, traite la requête, écrit la réponse JSON sur **stdout**
5. opencode lit stdout, parse la réponse, et donne le résultat au LLM
6. À l'arrêt, opencode envoie un signal au subprocess (SIGTERM)

Le transport stdio est **synchrone du point de vue du host** : chaque requête attend une réponse. Mais le serveur peut traiter plusieurs requêtes en séquence.

---

### 4.5 Configuration opencode.json pour MCP — Analyse ligne par ligne

La section MCP de `opencode.json` déclare les serveurs MCP à lancer et leurs modes de connexion. Voici une analyse complète :

```json
{
  "mcp": {
    // ↑ SECTION MCP (optionnelle)
    //   Déclare les serveurs MCP qu'opencode doit lancer.
    //   Si absente, aucun serveur MCP n'est démarré.
    //   Chaque clé est un identifiant unique de serveur.

    "dev-assistant": {
      // ↑ NOM DU SERVEUR (obligatoire, unique)
      //   Identifiant utilisé par opencode pour :
      //   - Lancer le serveur (subprocess)
      //   - Le référencer dans les logs et les messages d'erreur
      //   - Lui associer les permissions (si configuré)
      //   Doit correspondre au nom passé à Server() dans le code.

      "type": "local",
      // ↑ TYPE DE TRANSPORT (obligatoire)
      //   "local"  → transport stdio (subprocess local).
      //              opencode fork le processus et communique
      //              via stdin/stdout. Recommandé pour le dev.
      //   "remote" → transport HTTP (serveur distant).
      //              opencode se connecte à une URL distante.
      //              Nécessite une URL dans la config.
      //   "streamable-http" → transport HTTP stateless (nouveau 2026).
      //   Voir section 4.2 pour les différences détaillées.

      "command": ["python", "lab/code/02_mcp_server/server.py"],
      // ↑ COMMANDE DE LANCEMENT (obligatoire pour type: "local")
      //   Tableau JSON : ["exécutable", "arg1", "arg2", ...]
      //   opencode exécute cette commande avec subprocess.
      //   Le PATH shell est disponible (on peut écrire "python"
      //   sans chemin absolu si Python est dans le PATH).
      //   Le working directory est la racine du projet.
      //
      //   Attention : Ne PAS mettre de shell pipes/redirections ici
      //   (pas de "|", ">", "&&"). opencode lance la commande
      //   directement, sans shell intermédiaire. Utilisez un
      //   script shell wrapper si nécessaire.

      "enabled": true
      // ↑ ACTIVATION (booléen, optionnel, défaut: true)
      //   true  → opencode lance le serveur au démarrage de la
      //           session et le maintient en vie.
      //   false → le serveur est configuré mais pas lancé.
      //           Utile pour désactiver temporairement un serveur
      //           sans perdre sa configuration.
    },

    "remote-db-assistant": {
      // ↑ Exemple de serveur distant (type: "remote")
      "type": "remote",
      "url": "https://mcp.monentreprise.com",
      // ↑ URL du serveur distant (obligatoire pour type: "remote")
      //   opencode se connecte à cette URL via HTTP+SSE ou
      //   Streamable HTTP (selon le support du serveur).
      "headers": {
        // ↑ En-têtes HTTP optionnels.
        //   Utile pour passer des tokens d'authentification.
        "Authorization": "Bearer ${MCP_TOKEN}"
        // ↑ Utilisation de variables d'environnement.
        //   opencode résout ${MCP_TOKEN} depuis l'environnement.
        //   NE JAMAIS écrire le token en dur dans le JSON.
      },
      "enabled": false
    }
  }
}
```

**Scénario concret d'exécution :**

1. L'utilisateur lance `opencode` dans le répertoire du projet
2. opencode lit `opencode.json` et trouve la section `mcp`
3. Pour chaque serveur avec `"enabled": true` :
   - Si `type: "local"` → opencode lance la commande en subprocess
   - Si `type: "remote"` → opencode tente une connexion HTTP
4. opencode envoie `tools/list` à chaque serveur pour découvrir les outils
5. Les outils découverts sont ajoutés à l'espace d'outils de l'agent
6. Quand le LLM décide d'utiliser un outil, opencode route l'appel vers le bon serveur

---

### 4.6 Sécurité & Auth

MCP expose des outils potentiellement dangereux (lecture fichier, exécution de code). La sécurité est donc critique.

#### OAuth 2.1 + PKCE

Pour les serveurs distants, l'authentification suit OAuth 2.1 avec PKCE (Proof Key for Code Exchange) :

```
┌──────┐  Auth Request  ┌──────────┐  Token Request  ┌────────┐
│ Host │───────────────►│  Auth    │───────────────►│ Server │
│(MCP) │◄───────────────│  Server  │◄───────────────│  MCP   │
│      │  Auth Code     │(OAuth)   │  Access Token   │        │
└──────┘                └──────────┘                └────────┘

Étapes :
1. Host génère un code_verifier aléatoire + code_challenge (SHA256)
2. Host envoie l'utilisateur vers le serveur d'autorisation
3. L'utilisateur s'authentifie et approuve les permissions
4. Le serveur retourne un code d'autorisation
5. Le host échange le code + code_verifier contre un access token
6. Le host utilise l'access token pour les appels MCP
```

#### Resource Indicators (RFC 8707)

Le token d'accès est lié à un serveur MCP spécifique via l'entête `resource` : un token volé pour un serveur ne fonctionne pas sur un autre serveur.

#### Dynamic Client Registration

Les clients MCP peuvent s'enregistrer dynamiquement auprès des serveurs, évitant la configuration manuelle des client_id/client_secret.

#### DPoP (Demonstration of Proof of Possession)

Les tokens incluent une preuve cryptographique (DPoP) que le client possède bien la clé privée associée au token. Même si le token est intercepté, il ne peut pas être réutilisé.

#### Bonnes pratiques pour les serveurs stdio locaux

| Risque | Mitigation |
|--------|------------|
| Path traversal dans `read_file` | Valider que le chemin est dans un répertoire autorisé (`Path(...).resolve()`, vérifier le préfixe) |
| Exécution arbitraire dans `run_python` | Sandboxing via Docker, ou liste blanche d'opérations autorisées |
| Injection de commandes | Utiliser `subprocess.run()` avec des arguments (pas `shell=True`), valider les entrées |
| Déni de service | Timeouts (10s dans l'exemple), limite de taille de réponse (3000 chars), rate limiting |

#### Audit trails

MCP recommande la journalisation standardisée de tous les appels d'outils :

```json
{
  "timestamp": "2026-05-18T14:30:00Z",
  "method": "tools/call",
  "tool": "run_python",
  "arguments": {"code": "print('hello')"},
  "user": "agent-scrum-master",
  "session_id": "ses_abc123",
  "result_size": 42
}
```

Ces logs permettent la conformité (SOC 2, ISO 27001) et le debugging.

---

### 4.7 Roadmap 2026

| Priorité | Initiative | Statut | Impact |
|----------|------------|--------|--------|
| P0 | **Transport Evolution** — Streamable HTTP comme seul transport remote | En migration | Supprime la complexité SSE, scaling horizontal |
| P0 | **Agent Communication** — Standard inter-agent basé sur MCP | Spécification | MCP → A2A : complémentarité native |
| P1 | **Governance Maturation** — Contributor ladder, spécification formelle | En cours | Stabilité du standard, adoption enterprise |
| P1 | **Enterprise Readiness** — Auth (OAuth 2.1), audit, SSO, RBAC | En cours | Conformité, déploiement grandes org |
| P2 | **Output Schema** — Structure typée pour les retours d'outils | Spec finalisée | Meilleur parsing LLM, réduit les erreurs |
| P2 | **Streaming tools** — Résultats partiels avant complétion | Recherche | UX temps réel, longs traitements |

---

## Synthèse

**Ce que vous avez appris dans cette séance :**

| Concept | Résumé | Section |
|---------|--------|--------|
| Problème n × m | Sans standard, chaque intégration LLM-outil est un cas spécial coûteux | 4.1 |
| Architecture MCP | Host héberge un Client MCP qui se connecte à un Server via JSON-RPC 2.0 | 4.2 |
| Transports | stdio (local), HTTP+SSE (distant/déprécié), Streamable HTTP (nouveau standard) | 4.2 |
| Primitives | Resources (données), Prompts (templates), Tools (exécutables) | 4.3 |
| Construction serveur | Décorateurs `@app.list_tools`, `@app.call_tool`, transport stdio, `anyio.run()` | 4.4 |
| Configuration | Section `mcp` dans `opencode.json` : type, command, enabled | 4.5 |
| Sécurité | OAuth 2.1, PKCE, DPoP, audit trails, validation d'entrées | 4.6 |

**Lien avec la séance suivante :**

> *"Maintenant que vous savez faire communiquer un agent avec des outils via MCP, la séance 5 (A2A Protocol) vous apprendra à faire communiquer des agents entre eux. MCP et A2A sont complémentaires : un agent peut découvrir via A2A qu'un autre agent expose un outil de recherche documentaire — outil qui est lui-même implémenté via MCP. Vous réutiliserez le serveur MCP de cette séance comme brique de base pour construire des équipes d'agents."*

## Références contextualisées

- **[Specification officielle MCP (2026)]**
  *Contexte :* Document de référence complet du protocole. À consulter pendant les labs pour les détails d'implémentation. Section critique : "Transports" et "Primitives".
  *Niveau de lecture :* technique
  *→ https://modelcontextprotocol.io/specification/latest*

- **[MCP Python SDK — GitHub (2026)]**
  *Contexte :* SDK officiel Python pour construire des serveurs et clients MCP. Utilisé dans la section 4.4 pour le serveur d'exemple. Les décorateurs (`@app.list_tools`, `@app.call_tool`) sont documentés ici.
  *Niveau de lecture :* technique
  *→ https://github.com/modelcontextprotocol/python-sdk*

- **[MCP Roadmap 2026]**
  *Contexte :* Feuille de route officielle couvrant les évolutions planifiées : Streamable HTTP, Agent Communication, Enterprise Readiness. Source des informations de la section 4.7.
  *Niveau de lecture :* introduction
  *→ https://modelcontextprotocol.io/development/roadmap*

- **[Anthropic, Introducing MCP (2024)]**
  *Contexte :* Article fondateur qui a introduit le protocole. Explique la vision : "MCP is to LLMs what USB-C is to peripherals". Cité en section 4.1 pour l'analogie pédagogique.
  *Niveau de lecture :* introduction
  *→ https://www.anthropic.com/news/model-context-protocol*

- **[OAuth 2.1 — RFC 6749 bis (Draft)]**
  *Contexte :* Standard d'authentification utilisé par MCP pour les serveurs distants. Les concepts de PKCE et DPoP (section 4.6) sont définis dans ce cadre.
  *Niveau de lecture :* avancé
  *→ https://oauth.net/2.1/*

- **[OWASP LLM Top 10 (2025)]**
  *Contexte :* Guide de sécurité pour les applications LLM. Les risques de path traversal et d'exécution de code arbitraire (section 4.6) sont couverts respectivement par LLM02 (Data Poisoning) et LLM06 (Excessive Agency).
  *Niveau de lecture :* avancé
  *→ https://owasp.org/www-project-top-10-for-llm-applications/*
