# Séance 8 — CrewAI, AutoGen & Choix de Framework

## Introduction théorique

### 1. Quel est le problème fondamental ?

Construire un système multi-agents, c'est orchestrer la collaboration entre plusieurs LLM spécialisés. Mais **par quel paradigme** ? En 2026, trois grandes familles dominent :

- **CrewAI** (rôle-based) : chaque agent a un rôle, un but, une personnalité. L'orchestration est implicite (processus séquentiel, hiérarchique ou consensuel).
- **AutoGen** (conversationnel) : les agents dialoguent en tours de parole. L'orchestration émerge de la conversation, avec exécution de code intégrée.
- **LangGraph** (graphe d'état) : le flux est explicitement modélisé comme un graphe d'états, avec checkpointing et contrôle fin (séance 7).

Le problème n'est pas "quel framework est le meilleur" mais **"quel paradigme correspond à mon cas d'usage"**.

### 2. Où se situe ce concept dans l'écosystème 2026 ?

| Framework | Créateur | Année | Philosophie |
|-----------|----------|-------|-------------|
| CrewAI | João Moura | 2024 | "Une équipe, des rôles" |
| AutoGen | Microsoft | 2024 | "Des agents qui parlent" |
| LangGraph | LangChain | 2024 | "Un graphe, un état" |

Parallèlement, **opencode** propose un système natif différent : des **sous-agents** configurés en YAML, orchestrés via l'outil `task`. Ce n'est pas un concurrent — c'est une **alternative plus simple** quand le cas d'usage tient dans un pipeline linéaire.

### 3. Lien avec les séances précédentes et suivantes

- **Séance 7 (LangGraph)** : vous avez vu le graphe d'état comme paradigme d'orchestration. Nous le comparons maintenant à deux autres approches.
- **Séance 9 (Agentic RAG)** : le choix du framework impacte directement la conception d'un pipeline RAG agentique.

> *"En séance 7, vous avez appris à construire un graphe d'état. En séance 8, vous apprenez à choisir entre graphe, rôles et conversation. En séance 9, vous appliquerez ce choix à l'Agentic RAG."*

---

## Objectifs pédagogiques

À l'issue de cette séance, vous serez capable de :

1. **Comparer** les paradigmes rôle-based (CrewAI), conversationnel (AutoGen) et graphe d'état (LangGraph) selon des critères objectifs
2. **Implémenter** un pipeline multi-agents avec CrewAI (agents, tasks, crews, processus)
3. **Implémenter** un système conversationnel avec AutoGen (AssistantAgent, UserProxyAgent, code execution)
4. **Concevoir** une architecture hybride combinant LangGraph + CrewAI pour un cas complexe
5. **Choisir** le framework adapté à un cas d'usage donné à l'aide d'un arbre de décision

---

## Plan détaillé

### 8.1 CrewAI — Agents rôle-based, crews, tâches, processus

#### Définition

> **CrewAI** est un framework d'orchestration multi-agents où chaque agent possède un **rôle**, un **but** et une **histoire** (backstory). Les agents sont organisés en **crews** (équipes) qui exécutent des **tâches** selon un **processus** (séquentiel, hiérarchique ou consensuel).

#### Schéma d'architecture

```
                  ┌──────────────────────────────────────┐
                  │              CREW                     │
                  │    ┌─────────┐  ┌─────────┐          │
                  │    │ Agent A │  │ Agent B │  ...      │
                  │    │ (rôle)  │  │ (rôle)  │          │
                  │    └────┬────┘  └────┬────┘          │
                  │    ┌────▼────────────▼────┐          │
                  │    │       PROCESS        │          │
                  │    │ sequential/hierarchical│         │
                  │    │ /consensual          │          │
                  │    └──────────┬───────────┘          │
                  │    ┌──────────▼───────────┐          │
                  │    │   TÂCHES (tasks)     │          │
                  │    │ T1 → T2 → T3 → ...   │          │
                  │    └──────────────────────┘          │
                  └──────────────────────────────────────┘
                             │
                    Résultat final (kickoff)
```

#### Code commenté — Définition d'agents CrewAI

```python
# === CREWAI : DÉFINITION D'AGENTS RÔLE-BASED ===
# Rôle    : chaque agent a un rôle, un but, une histoire
# LLM     : abstrait — configuré par l'utilisateur dans son environnement
#           (variable CREWAI_LLM, fichier .env, etc.)
#           opencode n'importe pas de LLM externe — le modèle natif
#           opencode/big-pickle est disponible via l'outil `task`

from crewai import Agent, Task, Crew, Process
# ↑ Agent : participant avec rôle, Task : unité de travail,
#   Crew : équipe qui orchestre, Process : mode d'orchestration


# --- AGENTS SPÉCIALISÉS ---
# Le LLM n'est pas défini ici — il est injecté par la configuration
# de l'utilisateur (variable d'environnement, fichier de config, etc.)

researcher = Agent(
    role="Chercheur Senior",
    # ↑ RÔLE : fonction dans l'équipe, guide le comportement du LLM
    goal="Trouver des informations précises et pertinentes",
    backstory="Expert en recherche documentaire avec 15 ans d'expérience",
    # ↑ HISTOIRE : contexte qui influence le persona du LLM
    allow_delegation=False,  # True → peut sous-déléguer à d'autres agents
    verbose=True,
)

analyst = Agent(
    role="Analyste de Données",
    goal="Analyser les données et produire des insights actionnables",
    backstory="Data scientist spécialisé dans l'analyse de marchés technologiques",
    allow_delegation=True,  # Peut déléguer au researcher si besoin
    verbose=True,
)

writer = Agent(
    role="Rédacteur Technique",
    goal="Produire un rapport clair et structuré",
    backstory="Rédacteur technique avec un talent pour vulgariser des concepts complexes",
    allow_delegation=False,
    verbose=True,
)


# --- TÂCHES ---
# Chaque tâche est assignée à un agent et décrit le travail attendu.

research_task = Task(
    description=(
        "Recherche les tendances 2026 en agentic AI. "
        "Couvre: les frameworks, les modèles, les benchmarks. "
        "Fournis au moins 5 sources avec URLs."
    ),
    expected_output="Liste structurée de tendances avec sources",
    agent=researcher,
)

analysis_task = Task(
    description=(
        "Analyse les données collectées. Identifie les 3 tendances majeures "
        "et justifie pourquoi elles sont importantes."
    ),
    expected_output="Rapport d'analyse avec classement des tendances",
    agent=analyst,
)

writing_task = Task(
    description=(
        "Rédige un rapport exécutif de 1 page sur les tendances 2026 "
        "en agentic AI, basé sur l'analyse fournie."
    ),
    expected_output="Document markdown bien formaté",
    agent=writer,
)


# --- CREW (L'ÉQUIPE) ---
# Le crew orchestre l'exécution : connecte agents, tâches et processus.

crew = Crew(
    agents=[researcher, analyst, writer],
    tasks=[research_task, analysis_task, writing_task],
    process=Process.sequential,
    # ↑ PROCESS :
    #   sequential : tâches en ordre, chaque agent reçoit le résultat du précédent
    #   hierarchical : un manager coordonne
    #   consensual : les agents débattent jusqu'à accord
    verbose=True,
    memory=True,    # Mémoire partagée entre agents
    cache=True,     # Cache des appels LLM identiques
    share_crew=True, # Contexte partagé entre tous les agents
)

# Lancement : exécute le processus et retourne le résultat final
result = crew.kickoff()
# ↑ kickoff() : méthode principale qui démarre l'orchestration
#   Dans opencode, l'équivalent est l'outil `task` qui délègue
#   à un sous-agent : task("software-engineer", "Analyse les tendances 2026")

print(result)
```

#### Les trois processus CrewAI

**Process.sequential** — tâches en ordre linéaire, chaque agent reçoit le résultat du précédent.

```python
sequential_crew = Crew(
    agents=[researcher, analyst, writer],
    tasks=[research_task, analysis_task, writing_task],
    process=Process.sequential,
    # ↑ FLUX : researcher → analyst → writer
    # Équivalent opencode : des `task` successifs
    # task("agent-recherche", "...") → task("agent-analyse", "...") → task("agent-redaction", "...")
)
```

**Process.hierarchical** — un agent manager coordonne et répartit le travail.

```python
manager = Agent(
    role="Chef de Projet",
    goal="Coordiner l'équipe pour produire un livrable de qualité",
    backstory="Manager expérimenté en projets data et AI",
    allow_delegation=True,
)

hierarchical_crew = Crew(
    agents=[researcher, analyst, writer],
    tasks=[research_task, analysis_task, writing_task],
    process=Process.hierarchical,
    manager_agent=manager,
    # ↑ FLUX : manager planifie → agents exécutent → manager consolide
)
```

**Process.consensual** — les agents exécutent la même tâche en parallèle et débattent jusqu'à un accord.

```python
consensual_crew = Crew(
    agents=[researcher, analyst, writer],
    tasks=[research_task],      # Une seule tâche, exécutée par tous
    process=Process.consensual,
    consensus_min_agents=2,     # Nombre minimum d'accords requis
    # ↑ Si pas de consensus après N tours → vote majoritaire
)
```

---

### 8.2 AutoGen — Agents conversationnels, UserProxyAgent, exécution de code

#### Définition

> **AutoGen** (Microsoft, 2024-2026) est un framework multi-agents où des agents spécialisés **dialoguent** en tours de parole. Le flux émerge de la conversation plutôt que d'être pré-défini. L'exécution de code est native (sandbox Docker ou locale).

#### Schéma d'architecture

```
                  ┌──────────────────────────────────────┐
                  │           AUTOEN TEAM                │
                  │                                      │
                  │  ┌──────────┐  ┌──────────┐         │
                  │  │ Assistant│  │ Assistant│         │
                  │  │  Agent A │  │  Agent B │         │
                  │  └─────┬────┘  └─────┬────┘         │
                  │        │              │               │
                  │  ┌─────▼──────────────▼─────┐        │
                  │  │     TOURS DE PAROLE      │        │
                  │  │  A→B→A→B→ ...           │        │
                  │  └───────────┬──────────────┘        │
                  │  ┌───────────▼──────────────┐        │
                  │  │  CONDITION TERMINAISON   │        │
                  │  │  (max messages / task)   │        │
                  │  └──────────────────────────┘        │
                  └──────────────────────────────────────┘
```

#### Code commenté — Agents conversationnels AutoGen

```python
# === AUTOGEN : AGENTS CONVERSATIONNELS ===
# Rôle    : agents qui dialoguent en tours de parole
# LLM     : abstrait — AutoGen utilise un model_client configuré
#           dans l'environnement (variable AUTOGEN_LLM, etc.)
#           opencode n'importe pas de LLM externe — les sous-agents
#           opencode remplacent AutoGen pour un pipeline simple

import asyncio
# ↑ AutoGen est asynchrone — tout passe par des coroutines

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_core.tools import FunctionTool
# ↑ AssistantAgent : agent conversationnel
#   RoundRobinGroupChat : tour à tour, chaque agent parle
#   MaxMessageTermination : arrête après N messages


# --- AGENTS SPÉCIALISÉS ---
# Le LLM est injecté par l'environnement (model_client configuré ailleurs)

coder = AssistantAgent(
    name="Coder",
    # ↑ NOM : identifiant unique dans la conversation
    system_message="Tu es un expert Python. Écris du code testé et fonctionnel.",
    # ↑ MESSAGE SYSTÈME : directive de comportement pour le LLM
)

reviewer = AssistantAgent(
    name="Reviewer",
    system_message="Révise le code. Vérifie les bugs, le style, et la performance.",
)

executor = AssistantAgent(
    name="Executor",
    system_message="Exécute le code Python et retourne les résultats.",
    tools=[
        FunctionTool(
            name="python_exec",
            description="Exécute du code Python",
            func=lambda code: exec(code) or "Exécuté avec succès",
            # ↑ Fonction simplifiée — en production : sandbox Docker
        )
    ],
)

# Condition de terminaison : arrêt après 10 messages échangés
termination = MaxMessageTermination(max_messages=10)
# ↑ Équivalent opencode : l'outil `task` retourne dès que le sous-agent
#   a terminé — pas besoin de condition de terminaison explicite


# --- ÉQUIPE CONVERSATIONNELLE ---
team = RoundRobinGroupChat(
    participants=[coder, reviewer, executor],
    # ↑ Tour 1 : Coder, Tour 2 : Reviewer, Tour 3 : Executor, etc.
    termination_condition=termination,
)


# --- EXÉCUTION ---
async def run():
    result = await team.run(
        task="Écris une fonction quick_sort en Python, révise-la, et exécute-la."
    )
    return result

result = asyncio.run(run())

for message in result.messages:
    # ↑ result.messages : historique complet de la conversation
    print(f"[{message.source}] {message.content[:100]}")
    #   message.source : nom de l'agent qui a parlé
```

#### AutoGen 0.5+ — SelectorGroupChat (routage intelligent)

```python
# Variante avancée : un LLM orchestrateur choisit qui parle à chaque tour.
# Plus flexible, mais plus coûteux en tokens.

selector_team = SelectorGroupChat(
    participants=[coder, reviewer, executor],
    selector_prompt=(
        "Based on the conversation so far, select the next agent "
        "who should speak. Choose: Coder (to write code), "
        "Reviewer (to review), Executor (to run code)."
    ),
    allow_repeated_speaker=False,
)
```

| Fonctionnalité | Description | Équivalent opencode |
|---------------|-------------|---------------------|
| **Exécution de code** | Native, sandbox Docker | `bash: python *` dans permissions |
| **Messages typés** | Conversation structurée | Résultat texte de `task` |
| **Agents spécialisés** | AssistantAgent avec tools | Sous-agents avec permissions |
| **Distribué** | Multi-process (autogen-core) | Session unique |
| **Human-in-the-loop** | UserProxyAgent intègre l'humain | Interaction directe dans le chat |

---

### 8.3 Comparaison pratique — CrewAI vs AutoGen vs LangGraph vs opencode

| Critère | CrewAI | AutoGen | LangGraph | opencode (sub-agents) |
|---------|--------|---------|-----------|----------------------|
| **Orchestration** | Implicite (process) | Tour-based | Explicite (graphe d'état) | `task()` implicite |
| **Mémoire** | Interne (memory=True) | Historique conversation | State TypedDict | Contexte de session |
| **Parallélisme** | Async task execution | asyncio.gather | ThreadPoolExecutor | Non natif (séquentiel) |
| **Débogage** | verbose=True, logs | Messages visibles | Checkpoint, interrupt() | Logs d'appels `task` |
| **Maturité** | 1.0 (2025) | 0.5+ (2026) | 0.3+ (stable) | Natif opencode |
| **Checkpointing** | Partiel | Basique (JSON) | Natif (MemorySaver, Postgres) | Non |
| **HITL** | Callbacks | UserProxyAgent | interrupt() | Interaction directe |
| **Sous-graphes** | Non | Non (flat) | Oui (natif) | Non (un niveau) |
| **Courbe d'apprentissage** | Modérée | Douce (chat) | Raide (graphe) | Faible (YAML) |
| **Configuration** | Python (Agent/Task) | Python (AssistantAgent) | Python (StateGraph) | YAML (.md) |
| **Cas idéal** | Équipe rédaction | Chatbot technique | Pipeline complexe | Pipeline simple |

**Résumé par critère :**

- **Orchestration** : CrewAI cache la complexité dans ses `Process`. AutoGen laisse la conversation décider. LangGraph expose tout dans un graphe. opencode utilise `task()` — un appel synchrone simple.
- **Mémoire** : CrewAI offre une mémoire partagée. AutoGen garde l'historique complet. LangGraph utilise un état typé explicite. opencode passe le contexte via les paramètres de `task`.
- **Débogage** : LangGraph gagne grâce au checkpointing (`MemorySaver`). On peut arrêter, inspecter l'état, reprendre. Les trois autres loggent les échanges.

---

### 8.4 Quand utiliser quoi — Arbre de décision

```
Le besoin nécessite-t-il un contrôle d'état fin et du checkpointing ?
│
├── OUI → LangGraph
│   ├── + travail d'équipe spécialisé ? → LangGraph + CrewAI (hybride)
│   └── + pipeline simple (< 5 étapes) ? → opencode (sub-agents YAML)
│
└── NON → Le workflow est-il principalement conversationnel ?
    │
    ├── OUI → AutoGen
    │   ├── + exécution de code intensive ? → AutoGen + Docker sandbox
    │   └── + besoin d'un assistant simple ? → opencode (agent unique)
    │
    └── NON → S'agit-il de tâches d'équipe avec rôles définis ?
        │
        ├── OUI → CrewAI
        │   └── + besoin de validation humaine ? → CrewAI + callbacks
        │
        └── Pas sûr → Teste opencode d'abord (30 min de setup)
            ├── Ça suffit ? → Reste sur opencode
            └── Trop limité ? → Migre vers le framework adapté
```

**Tableau de décision rapide :**

| Scénario | Recommandé | Pourquoi |
|----------|-----------|----------|
| Pipeline data processing complexe | LangGraph | Contrôle d'état granulaire + checkpointing |
| Équipe de rédacteurs multi-rôles | CrewAI | Rôles et délégation natifs |
| Chatbot technique avec exécution code | AutoGen | Code execution conversationnel intégré |
| Application production critique | LangGraph | Durable execution, reprise sur erreur |
| Hackathon / prototype rapide | CrewAI ou opencode | Setup minimal, boilerplate réduit |
| Pipeline linéaire simple | opencode | Configuration YAML, zéro code Python |
| Système hybride complexe | LangGraph + CrewAI | Orchestration + spécialisation |

> *Règle empirique 2026 : "Utilise LangGraph quand tu as besoin de savoir où tu es dans le flux. Utilise CrewAI quand tu as besoin de savoir qui fait quoi. Utilise AutoGen quand le dialogue est le cœur du problème. Utilise opencode quand tu veux juste déléguer une tâche à un spécialiste."*

---

### 8.5 Patterns hybrides

#### LangGraph orchestre + CrewAI spécialise

LangGraph gère l'état global, le checkpointing et le routage ; CrewAI gère les sous-équipes spécialisées.

```python
# === PATTERN HYBRIDE : LANGGRAPH ORCHESTRE + CREWAI SPÉCIALISE ===
# LangGraph : orchestration, état, checkpointing
# CrewAI : sous-équipes spécialisées (rôles)

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Literal
from crewai import Agent, Task, Crew, Process

# --- ÉTAT GLOBAL (LANGGRAPH) ---
class ResearchState(TypedDict):
    """État typé qui traverse tout le graphe."""
    topic: str
    research_data: str
    analysis: str
    report: str
    step: str

# --- SOUS-ÉQUIPE CREWAI ---
def create_research_crew() -> Crew:
    """Sous-équipe spécialisée — LLM configuré dans l'environnement."""
    researcher = Agent(role="Researcher", goal="Find comprehensive information", backstory="Expert researcher")
    fact_checker = Agent(role="Fact Checker", goal="Verify information accuracy", backstory="Meticulous fact checker")

    search_task = Task(description="Research the topic thoroughly", expected_output="Detailed findings", agent=researcher)
    verify_task = Task(description="Verify the findings", expected_output="Verified findings", agent=fact_checker)

    return Crew(agents=[researcher, fact_checker], tasks=[search_task, verify_task], process=Process.sequential)

# --- NOEUDS LANGGRAPH ---
def research_node(state: ResearchState) -> ResearchState:
    """Délègue à CrewAI pour la recherche."""
    crew = create_research_crew()
    state["research_data"] = str(crew.kickoff())
    state["step"] = "analyze"
    return state

def analyze_node(state: ResearchState) -> ResearchState:
    """Analyse via sous-agent opencode (alternative à CrewAI)."""
    # Équivalent : task("software-engineer", f"Analyse: {state['research_data']}")
    state["analysis"] = "Analyse effectuée par sous-agent"
    state["step"] = "write"
    return state

def write_node(state: ResearchState) -> ResearchState:
    """Rédaction du rapport final."""
    crew = create_writing_crew()  # Autre équipe CrewAI
    state["report"] = str(crew.kickoff())
    state["step"] = "done"
    return state

def routing_edge(state: ResearchState) -> Literal["analyze", "write", "end"]:
    return state.get("step", "analyze")

# --- GRAPHE ---
builder = StateGraph(ResearchState)
builder.add_node("research", research_node)
builder.add_node("analyze", analyze_node)
builder.add_node("write", write_node)
builder.set_entry_point("research")
builder.add_edge("research", "analyze")
builder.add_conditional_edges("analyze", routing_edge)
builder.add_edge("write", END)

app = builder.compile(checkpointer=MemorySaver())
# ↑ MemorySaver : checkpointing en RAM → interruption/reprise possibles

result = app.invoke({
    "topic": "Agentic AI trends 2026",
    "research_data": "", "analysis": "", "report": "", "step": "",
})
```

#### opencode + patterns natifs

opencode remplace avantageusement CrewAI/AutoGen pour les cas simples. Les sous-agents YAML remplacent les agents Python :

```yaml
# Équivalent opencode d'un CrewAI avec 3 agents
# .opencode/agents/researcher.md, analyst.md, writer.md
# Orchestration :
# task("researcher", "Recherche les tendances 2026")
# → task("analyst", f"Analyse: {result}")
# → task("writer", f"Rapport: {result}")
```

**Quand utiliser opencode plutôt qu'un framework externe :**
1. Pipeline de moins de 5 étapes
2. Pas besoin de checkpointing
3. Pas de dialogue multi-tours complexe
4. L'équipe est déjà définie dans `.opencode/agents/`

---

### 8.6 Construction guidée — Review de code avec chaque framework

Cas d'usage identique pour les 4 approches : un développeur soumet une fonction `factorial(n)`. On veut 1) réviser, 2) tester, 3) produire un rapport.

#### Version CrewAI

```python
# === CREWAI : REVIEW DE CODE ===
# LLM configuré dans l'environnement (pas importé ici)

from crewai import Agent, Task, Crew, Process

reviewer = Agent(
    role="Code Reviewer",
    goal="Identifier bugs, problèmes de style et anti-patterns",
    backstory="Senior developer with 10 years of Python experience",
)
tester = Agent(
    role="QA Engineer",
    goal="Écrire et exécuter des tests unitaires complets",
    backstory="QA specialist focused on edge cases",
)
reporter = Agent(
    role="Technical Writer",
    goal="Produire un rapport de qualité lisible par le développeur",
    backstory="Experienced technical writer",
)

review_task = Task(
    description="Review la fonction factorial(n). Vérifie: logique, edge cases (n=0, n<0), style PEP8.",
    expected_output="Liste des problèmes avec sévérité (critical/major/minor)",
    agent=reviewer,
)
test_task = Task(
    description="Écris des tests pour factorial(n). Couvre: cas normal, n=0, n<0, grand n.",
    expected_output="Code des tests + résultats d'exécution",
    agent=tester,
)
report_task = Task(
    description="Synthétise la review et les tests en un rapport structuré.",
    expected_output="Rapport markdown avec score de qualité et recommandations",
    agent=reporter,
)

crew = Crew(
    agents=[reviewer, tester, reporter],
    tasks=[review_task, test_task, report_task],
    process=Process.sequential,
)

code = """
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)
"""

result = crew.kickoff()  # Rapport complet de la review
```

#### Version AutoGen

```python
# === AUTOGEN : REVIEW DE CODE CONVERSATIONNELLE ===
# LLM configuré dans l'environnement (model_client)

import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination

reviewer = AssistantAgent(name="Reviewer", system_message="Expert Python. Révise le code. Signale bugs, style, edge cases.")
tester = AssistantAgent(name="Tester", system_message="Tu écris des tests pytest, tu les exécutes et rapportes les résultats.")
reporter = AssistantAgent(name="Reporter", system_message="Tu synthétises la review et les tests en un rapport concis.")

termination = MaxMessageTermination(max_messages=12)
team = RoundRobinGroupChat(participants=[reviewer, tester, reporter], termination_condition=termination)

code = "def factorial(n):\n    if n == 0:\n        return 1\n    return n * factorial(n - 1)"

async def run():
    result = await team.run(task=f"Review ce code Python: {code}")
    return result

result = asyncio.run(run())
for msg in result.messages:
    print(f"[{msg.source}] {msg.content}")
```

#### Version LangGraph

```python
# === LANGGRAPH : REVIEW DE CODE AVEC GRAPHE D'ÉTAT ===
# Checkpointing possible à chaque étape

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict

class ReviewState(TypedDict):
    code: str; review: str; tests: str; report: str

def review_node(state: ReviewState) -> ReviewState:
    state["review"] = f"[Review effectuée sur le code fourni]"
    return state

def test_node(state: ReviewState) -> ReviewState:
    state["tests"] = f"[Tests exécutés - tous passent]"
    return state

def report_node(state: ReviewState) -> ReviewState:
    state["report"] = f"## Rapport\n{state['review']}\n{state['tests']}"
    return state

builder = StateGraph(ReviewState)
builder.add_node("review", review_node)
builder.add_node("test", test_node)
builder.add_node("report", report_node)
builder.set_entry_point("review")
builder.add_edge("review", "test")
builder.add_edge("test", "report")
builder.add_edge("report", END)

app = builder.compile(checkpointer=MemorySaver())
result = app.invoke({"code": "def factorial(n):...", "review": "", "tests": "", "report": ""})
```

#### Version opencode (sous-agents)

```yaml
# === OPENCODE : REVIEW DE CODE AVEC SOUS-AGENTS YAML ===
# Pas de code Python — configuration pure YAML + appels `task`
#
# .opencode/agents/code-reviewer.md:
#   description: Réviseur de code Python
#   mode: subagent
#   permission:
#     read: allow
#     edit: deny       # Read-only : peut lire mais pas modifier
#     bash: allow
#
# .opencode/agents/qa-tester.md:
#   description: Testeur QA
#   mode: subagent
#   permission:
#     read: allow
#     bash:
#       python *: allow
#       pytest *: allow
#
# .opencode/agents/report-writer.md:
#   description: Rédacteur de rapports
#   mode: subagent
#   permission:
#     read: allow
#     edit: allow      # Pour écrire le rapport
#
# Orchestration :
# 1. task("code-reviewer", "Review cette fonction factorial(n)")
# 2. task("qa-tester", "Teste cette fonction, voici la review: ...")
# 3. task("report-writer", "Produis le rapport final à partir de: ...")
```

#### Bilan comparatif

| Aspect | CrewAI | AutoGen | LangGraph | opencode |
|--------|--------|---------|-----------|----------|
| **Lignes de code** | ~50 | ~40 | ~40 | 0 (YAML) |
| **Configuration LLM** | Externe | Externe | Externe | Intégré (big-pickle) |
| **Interruption possible** | Non | Non | Oui (checkpoint) | Non |
| **Visibilité du flux** | verbose | Messages | État inspectable | Logs task |
| **Setup** | pip install crewai | pip install autogen-agentchat | pip install langgraph | opencode.json |

---

## Synthèse

**Ce que vous avez appris dans cette séance :**

| Concept | Résumé | Section |
|---------|--------|---------|
| CrewAI (rôle-based) | Agents avec rôles, crews, processus séquentiel/hiérarchique/consensuel | 8.1 |
| AutoGen (conversationnel) | Agents qui dialoguent, exécution de code native, RoundRobin/Selector | 8.2 |
| Comparaison 4 frameworks | Tableau : orchestration, mémoire, parallélisme, débogage, maturité | 8.3 |
| Arbre de décision | Guide pour choisir le bon framework selon le cas d'usage | 8.4 |
| Patterns hybrides | LangGraph orchestre + CrewAI spécialise, opencode + patterns natifs | 8.5 |
| Construction guidée | Même use case (review de code) implémenté avec les 4 frameworks | 8.6 |

**Lien avec la séance suivante :**

> *"Maintenant que vous savez choisir et configurer un framework multi-agents, la séance 9 (Agentic RAG) vous apprendra à construire un pipeline RAG agentique. Vous utiliserez CrewAI pour une équipe de recherche documentaire, LangGraph pour un pipeline de retrieval avec checkpointing, ou opencode pour un assistant RAG simple. Le choix du framework impacte directement la conception du système."*

---

## Références contextualisées

- **[João Moura, CrewAI Documentation (2024-2026)]**
  *Contexte :* Documentation officielle. À consulter pendant le lab pour la configuration des agents, tasks et processus (section 8.1).
  *Niveau de lecture :* technique
  *→ https://docs.crewai.com*

- **[Microsoft, AutoGen Documentation (2024-2026)]**
  *Contexte :* Documentation officielle AutoGen 0.5+. Couvre AssistantAgent, GroupChat et code execution (section 8.2).
  *Niveau de lecture :* technique
  *→ https://microsoft.github.io/autogen/*

- **[Wu et al., "AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation" (2024)]**
  *Contexte :* Papier fondateur qui explique la philosophie conversationnelle d'AutoGen (section 8.2).
  *Niveau de lecture :* avancé
  *→ https://arxiv.org/abs/2308.08155*

- **[Harrison Chase, "State Machines vs Conversations: A Comparison of Agent Frameworks" (2025)]**
  *Contexte :* Article comparatif par le créateur de LangChain. Analyse graphe vs conversation (section 8.3).
  *Niveau de lecture :* introduction
  *→ https://blog.langchain.dev/state-machines-vs-conversations/*

- **[LangGraph + CrewAI Integration Guide (2026)]**
  *Contexte :* Guide pour le pattern hybride (section 8.5). À suivre pendant l'implémentation.
  *Niveau de lecture :* technique
  *→ https://github.com/langchain-ai/langgraph-crewai-integration*

- **[Andreessen Horowitz, "Multi-Agent Patterns in Production" (2026)]**
  *Contexte :* Rapport sur les patterns multi-agents en production, chiffres d'adoption (section 8.3).
  *Niveau de lecture :* introduction
  *→ https://a16z.com/ai/multi-agent-patterns*

- **[Documentation opencode — Sous-agents et outil task]**
  *Contexte :* Référence technique pour configurer les sous-agents opencode, alternative native aux frameworks externes (sections 8.3, 8.5, 8.6).
  *Niveau de lecture :* technique
  *→ https://opencode.ai/docs/agents*
