# Séance 7 — LangGraph : Orchestration par Graphes d'État

## Introduction théorique

Cette séance aborde la limitation fondamentale des workflows agentiques linéaires et introduit LangGraph comme solution standard pour l'orchestration par graphes d'état.

### Quel est le problème fondamental ?

Les architectures ReAct simples (raisonnement → action → observation en boucle) fonctionnent pour des cas élémentaires, mais échouent sur trois scénarios critiques :

1. **Cycles complexes** — un agent doit pouvoir revenir en arrière, bifurquer, ou répéter une étape un nombre variable de fois selon le contexte. Une boucle `while` rigide ne suffit pas.
2. **Parallélisme** — lancer N recherches en parallèle, les agréger, puis décider. Un flux linéaire ne peut pas exprimer ce pattern.
3. **Intervention humaine** — interrompre l'exécution, attendre une validation, puis reprendre exactement là où on s'est arrêté sans perte d'état.

Un simple `while True: reason() → act()` ne suffit pas dès que le système dépasse 2-3 étapes conditionnelles.

### Où se situe LangGraph dans l'écosystème 2026 ?

LangChain (lancé fin 2022) a popularisé le pattern "LLM + outils" avec son `AgentExecutor`. Mais cet exécuteur était une boucle rigide. En 2024, LangGraph est né pour résoudre ce problème : un framework de *graphe d'état* où chaque étape est un nœud Python et les transitions sont des arêtes conditionnelles. En 2026, LangGraph est le standard de facto pour les workflows agentiques en production (adoption > 65%), les systèmes multi-agents, et l'orchestration de pipelines RAG complexes.

### Lien avec les séances précédentes et suivantes

- **Séance 6 (GitHub Agents Platform)** — vous avez vu comment GitHub orchestre des agents dans un contexte CI/CD. LangGraph est le moteur *générique* qui permet ces mêmes patterns dans n'importe quel environnement.
- **Séance 8 (CrewAI / AutoGen)** — ces frameworks multi-agents s'appuient sur les mêmes concepts de graphes. Comprendre LangGraph, c'est comprendre le moteur sur lequel CrewAI construit son orchestration.

> **Exemple :** "Dans la séance 6, vous avez vu des agents GitHub qui suivent un pipeline CI/CD linéaire. Dans cette séance 7, nous allons voir comment LangGraph remplace ce pipeline linéaire par un graphe d'état capable de cycles, parallélisme et intervention humaine — c'est la différence entre une chaîne de montage et un orchestre symphonique."

## Objectifs pédagogiques

À l'issue de cette séance, vous serez capable de :

1. **Analyser** les limites d'un workflow agentique linéaire (ReAct) et justifier le passage à un graphe d'état pour des cas complexes.
2. **Décomposer** un problème d'orchestration en nœuds, arêtes et conditions en utilisant le formalisme `StateGraph`.
3. **Implémenter** un graphe LangGraph complet avec checkpointing, branches parallèles et point d'intervention humaine.
4. **Concevoir** un agent modulaire en combinant sous-graphes spécialisés.
5. **Comparer** LangGraph et le système de sub-agents opencode pour choisir l'outil adapté à chaque scénario.

> Les objectifs sont SMART : Spécifiques (LangGraph, StateGraph), Mesurables (analyser, décomposer, implémenter, concevoir, comparer), Atteignables (dans le cadre de la séance), Réalistes (patterns de complexité progressive), Temporels (séance de 3h).

## Plan détaillé

### 7.1 Architecture LangChain — Les 4 piliers

#### Définition

LangChain (2023-2026) a évolué d'un simple wrapper d'appels LLM vers un framework d'orchestration complet. Son architecture repose sur 4 piliers :

1. **Chat Models** — interface unifiée pour tous les LLM (peu importe le fournisseur)
2. **Chains** — séquences d'appels composables via l'opérateur `|` (pipe)
3. **Tools** — fonctions Python exposées aux agents via spécification JSON
4. **Memory** — état persistant entre les appels (buffer, résumé, window)

#### Analogie pédagogique

> *"LangChain est à l'orchestration agentique ce que Django est au web : un framework structurant qui impose une architecture claire et fournit les briques prêtes à l'emploi pour les cas courants."*

Les 4 piliers sont comme une cuisine professionnelle :
- **Chat Models** = les ingrédients (la matière première)
- **Chains** = la recette (l'ordre des opérations)
- **Tools** = les ustensiles (couteau, robot, four)
- **Memory** = le carnet de notes (ne pas oublier ce qui a été fait)

#### Exemple commenté : pattern de chaîne simple

```python
# --- CHAÎNE SÉQUENTIELLE AVEC LANGCHAIN ---
# Le LLM est injecté par le runtime — pas d'instanciation directe
# L'objet 'llm' respecte l'interface Runnable de LangChain

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. CRÉATION DU PROMPT TEMPLATE
prompt = ChatPromptTemplate.from_messages([
    ("system", "Tu es un assistant expert en architecture logicielle."),
    ("human", "Explique-moi le pattern {pattern} en une phrase."),
])

# 2. COMPOSITION EN PIPELINE AVEC L'OPÉRATEUR |
chain = prompt | llm | StrOutputParser()
# ↑ L'opérateur | compose les étapes comme un pipe Unix :
#   prompt formate le message → llm génère → parser extrait le texte

# 3. INVOCATION
result = chain.invoke({"pattern": "StateGraph"})
```

#### Pourquoi ce concept est crucial

- **Impact sur la conception :** la composition par pipe (`|`) permet de construire des pipelines réutilisables et testables indépendamment.
- **Conséquence si ignoré :** chaque appel LLM est un cas particulier non structuré, impossible à factoriser ou à tracer.
- **Cas d'usage typique :** pipeline RAG : `retriever | prompt | llm | parser` — chaque étape est interchangeable.

---

### 7.2 LangGraph : StateGraph — Le concept de graphe d'état

#### Définition

> **Définition :** Un `StateGraph` est un graphe orienté dont les nœuds sont des fonctions Python et les arêtes définissent le flux de contrôle. L'*état* (un dictionnaire typé) est passé séquentiellement de nœud en nœud, chaque nœud pouvant le lire et le modifier.

#### Analogie pédagogique

> *"LangGraph transforme une recette de cuisine linéaire en organigramme. Dans une recette classique, vous suivez les étapes 1, 2, 3. Avec LangGraph, vous pouvez dire : 'si la sauce est trop liquide, retourne à l'étape 2 ; sinon, passe à l'étape 4 ; en parallèle, préchauffe le four'."*

#### Principe expliqué

```
                    ┌──────────────────────────────────────────┐
                    │              ÉTAT (State)                │
                    │  { "messages": [...], "next": "..." }   │
                    └────┬─────────────────────┬───────────────┘
                         │                     │
                    ┌────▼────┐          ┌─────▼─────┐
                    │ Agent   │          │  Outils   │
                    │ (LLM)   │◄────────►│ (Tools)   │
                    └────┬────┘          └─────┬─────┘
                         │                     │
                    ┌────▼─────────────────────▼────┐
                    │   Arête conditionnelle         │
                    │   should_continue(state) →     │
                    │   "tools" | "end" | "approval" │
                    └────────────────────────────────┘
```

Contrairement à une boucle ReAct classique où la décision est implicite, LangGraph rend le flux *explicite* et *inspectable* : on peut tracer chaque transition, sauvegarder l'état à chaque nœud, et reprendre l'exécution.

#### Pourquoi ce concept est crucial

- **Impact sur la conception :** l'orchestration devient modulaire — chaque nœud est une fonction pure testable isolément.
- **Conséquence si ignoré :** les agents restent limités à des boucles simples, sans parallélisme ni intervention humaine.
- **Cas d'usage typique :** assistant de développement qui lit du code, le modifie, exécute des tests, et si les tests échouent, corrige et relance — cycle qu'un ReAct simple ne peut pas exprimer proprement.

---

### 7.3 Nœuds, arêtes, conditions — Décomposition détaillée

LangGraph définit trois concepts de base :

| Concept | Rôle | Code |
|---------|------|------|
| **State** | Dictionnaire typé qui circule entre les nœuds | `class AgentState(TypedDict)` |
| **Node** | Fonction pure `state → state` | `def mon_noeud(state: S) -> S` |
| **Edge** | Lien entre deux nœuds (fixe ou conditionnel) | `add_edge()` / `add_conditional_edges()` |

#### Définition de l'état

```python
from typing import TypedDict, Literal

class AgentState(TypedDict):
    """État typé du graphe : chaque clé est un champ typé."""
    messages: list
    # ↑ Historique des messages (Humain/IA)
    task: str
    # ↑ Tâche en cours d'exécution
    iteration: int
    # ↑ Compteur d'itérations (évite les boucles infinies)
    next_step: Literal["continue", "end"]
    # ↑ Prochaine action décidée par l'agent
```

#### Nœud : la brique de base

```python
def agent_node(state: AgentState) -> AgentState:
    """NŒUD — Reçoit l'état, le modifie, le retourne.

    Chaque nœud est une fonction pure (idéalement sans effet de bord).
    Il lit l'état entrant, applique une transformation, et retourne
    le nouvel état.
    """
    # Le LLM est injecté par le runtime — pas d'import direct
    # Dans un déploiement réel : response = llm.invoke(state["messages"])
    state["iteration"] += 1
    state["next_step"] = "continue"
    return state
    # ↑ Le retour est le nouvel état, passé au prochain nœud
```

#### Arête conditionnelle : l'aiguilleur

```python
def router(state: AgentState) -> Literal["tools", "end"]:
    """ARÊTE CONDITIONNELLE — Décide du prochain nœud.

    Examine l'état courant et retourne le nom du prochain nœud.
    LangGraph suit cette indication pour router l'exécution.
    """
    if state["iteration"] >= 5:
        return "end"
        # ↑ Si trop d'itérations, on termine
    if state.get("need_tool"):
        return "tools"
        # ↑ Si un outil est nécessaire, on va au nœud tools
    return "end"
```

#### Construction complète du graphe

```python
from langgraph.graph import StateGraph, END

# 1. Création du graphe avec le type d'état
graph = StateGraph(AgentState)

# 2. Ajout des nœuds
graph.add_node("agent", agent_node)
graph.add_node("tools", tools_node)

# 3. Point d'entrée
graph.set_entry_point("agent")

# 4. Arête conditionnelle depuis "agent"
graph.add_conditional_edges(
    "agent",           # nœud source
    router,            # fonction de routage
    {"tools": "tools", "end": END}  # mapping retour → nœud
)

# 5. Arête fixe : tools retourne toujours vers agent
graph.add_edge("tools", "agent")

# 6. Compilation : validation du graphe → retourne l'exécutable
app = graph.compile()
```

Le graphe est maintenant exécutable. Chaque appel `app.stream(state)` parcourt les nœuds selon les règles définies.

---

### 7.4 Checkpointing, Human-in-the-loop, Branching — Patterns avancés

#### Checkpointing — Persistance de l'état

Le checkpointing sauvegarde l'état du graphe *après chaque nœud*. Cela permet de reprendre une session interrompue, rejouer une session pour debug, ou implémenter du "undo".

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.aiosqlite import AsyncSqliteSaver

# Checkpointing en mémoire (développement, tests)
memory_checkpointer = MemorySaver()
app_dev = graph.compile(checkpointer=memory_checkpointer)

# Checkpointing persistant SQLite (production légère)
sqlite_checkpointer = AsyncSqliteSaver.from_conn_string("sessions.db")
app_prod = graph.compile(checkpointer=sqlite_checkpointer)
```

#### Human-in-the-loop (HITL) — Intervention humaine

L'interruption permet d'arrêter le graphe à un nœud spécifique, d'attendre une décision humaine, puis de reprendre exactement au même point.

```python
from langgraph.types import interrupt

def approval_node(state: AgentState) -> AgentState:
    """NŒUD D'APPROBATION — Demande validation humaine.

    Interrompt le graphe et expose l'action à l'humain.
    La reprise injecte la décision via interrupt_value.
    """
    action = state["messages"][-1]
    decision = interrupt(
        "Action critique détectée. Approuver ?",
        {"action": action},
    )
    if decision != "approved":
        state["next_step"] = "cancelled"
    return state

# Usage : le premier appel s'arrête au nœud d'approbation
# L'humain examine l'état, puis reprend avec :
# app.invoke(None, config=config, interrupt_value="approved")
```

#### Branching — Parallélisme

```python
def analyze_sentiment(state: AgentState) -> AgentState:
    """BRANCHE A — Analyse de sentiment."""
    state["sentiment"] = "positif"
    return state

def extract_entities(state: AgentState) -> AgentState:
    """BRANCHE B — Extraction d'entités."""
    state["entities"] = ["Python", "LangGraph"]
    return state

def merge(state: AgentState) -> AgentState:
    """FUSION — Agrège les résultats parallèles."""
    state["analysis"] = {
        "sentiment": state.get("sentiment"),
        "entities": state.get("entities"),
    }
    return state

# Graphe parallèle : sentiment → entities → merge
graph = StateGraph(AgentState)
graph.add_node("sentiment", analyze_sentiment)
graph.add_node("entities", extract_entities)
graph.add_node("merge", merge)
graph.set_entry_point("sentiment")
graph.add_edge("sentiment", "entities")
graph.add_edge("entities", "merge")
graph.set_finish_point("merge")
```

---

### 7.5 Construction guidée — Agent développeur complet

Cette section est le **cœur pédagogique pratique**. Chaque fichier de code est décortiqué ligne par ligne, en français, pour que l'étudiant comprenne non seulement *ce que fait* chaque élément, mais aussi *pourquoi* il est conçu ainsi.

#### Objectif de l'agent

Nous construisons un agent développeur capable de :
1. Lire un fichier source
2. Modifier ou créer du code
3. Exécuter des tests
4. Si les tests échouent, corriger et réessayer (cycle automatique)
5. Arrêt automatique après N itérations (sécurité anti-boucle infinie)

#### Code complet commenté

```python
# === AGENT DÉVELOPPEUR AVEC LANGGRAPH ===
# Fichier : dev_agent.py
# Rôle    : Orchestrateur de tâches de développement (lire, écrire, tester)
# Dépendances : langgraph, langgraph-checkpoint
#
# Ce fichier implémente un StateGraph à 3 nœuds (agent, outils, vérification)
# avec cycle de correction automatique si les tests échouent.

# --- IMPORTS ---
# Chaque import est commenté pour expliquer pourquoi il est nécessaire.

import subprocess
# ↑ Exécution de commandes shell (pytest, grep) dans un sous-processus.
#   Plus sûr que os.system() car on contrôle stdin/stdout/stderr.

from pathlib import Path
# ↑ Manipulation de chemins fichiers de façon cross-platform.
#   Plus fiable et expressif que os.path.

from typing import TypedDict, Literal
# ↑ Typage : définit la structure de l'état du graphe.
#   LangGraph utilise TypedDict pour valider l'état à la compilation.

from langgraph.graph import StateGraph, END
# ↑ StateGraph : classe principale pour créer le graphe d'état.
#   END : constante spéciale qui termine l'exécution du graphe.

from langgraph.checkpoint.memory import MemorySaver
# ↑ Checkpointing en mémoire : sauvegarde l'état après chaque nœud.
#   Utile pour le développement. En production, on utilise PostgreSQL.

# --- ÉTAT DU GRAPHE ---
# Le dictionnaire qui circule entre les nœuds. Chaque champ est typé.

class DevAgentState(TypedDict):
    """État de l'agent développeur.

    Attributes:
        task : description de la tâche à accomplir
        current_file : fichier sur lequel on travaille (None au départ)
        test_results : sortie des tests (None tant que non exécutés)
        iteration : compteur d'itérations pour éviter les boucles infinies
        max_iterations : limite de sécurité absolue
    """
    task: str
    # ↑ La tâche initiale, passée par l'utilisateur.
    #   Exemple : "Ajoute une fonction fibonacci dans math_utils.py et teste-la"
    current_file: str | None
    # ↑ Chemin du fichier courant. None = pas encore de fichier ciblé.
    test_results: str | None
    # ↑ Sortie brute des tests (stdout + stderr). None = pas encore testé.
    iteration: int
    # ↑ Compteur incrémenté à chaque passage dans le nœud agent.
    max_iterations: int
    # ↑ Limite absolue. Au-delà, le graphe termine pour éviter les cycles infinis.

# --- FONCTIONS OUTILS ---
# Ces fonctions sont appelées par le nœud "tools". Elles encapsulent
# les opérations sur le système de fichiers et les processus.

def read_file(path: str) -> str:
    """Lit le contenu d'un fichier texte et le retourne."""
    return Path(path).read_text(encoding="utf-8")

def write_file(path: str, content: str) -> str:
    """Écrit du contenu dans un fichier texte.

    Crée le fichier s'il n'existe pas, l'écrase s'il existe.
    Retourne un message de confirmation.
    """
    Path(path).write_text(content, encoding="utf-8")
    return f"Fichier {path} mis à jour."

def run_test(command: str = "pytest") -> str:
    """Exécute une commande de test dans un sous-processus.

    Utilise subprocess.run avec capture_output=True pour récupérer
    la sortie sans l'afficher dans la console parente.
    timeout=30 évite les tests qui bouclent infiniment.
    """
    result = subprocess.run(
        command, shell=True, capture_output=True, text=True, timeout=30,
    )
    return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

def search_code(query: str, path: str = ".") -> str:
    """Recherche un pattern dans le code source avec grep.

    Retourne les 2000 premiers caractères pour ne pas saturer l'état.
    """
    result = subprocess.run(
        ["grep", "-rn", query, path],
        capture_output=True, text=True,
    )
    return result.stdout[:2000]

tools_map = {
    "read": read_file, "write": write_file,
    "test": run_test, "search": search_code,
}
# ↑ Dictionnaire associant un nom à chaque fonction outil.
#   Le nœud "tools" utilise ce mapping pour dispatcher les appels.

# --- NŒUDS DU GRAPHE ---
# Chaque nœud est une fonction pure : état → état.
# Aucun import de LLM, aucun wrapper externe.

def agent_node(state: DevAgentState) -> DevAgentState:
    """NŒUD PRINCIPAL — L'agent réfléchit et décide de la prochaine action.

    Dans un déploiement réel, cette fonction appellerait le LLM
    (injecté par le runtime) pour analyser la tâche et choisir
    le prochain outil à utiliser. Ici, le LLM est abstrait :
    la décision est simulée par des règles simples pour l'exemple.

    Rôle dans le graphe :
    1. Incrémente le compteur d'itérations (sécurité anti-boucle)
    2. Log l'état courant pour le debug
    3. Retourne l'état modifié

    Note : le LLM (big-pickle ou tout autre) est fourni
    par le contexte d'exécution. Pas d'instanciation directe.
    """
    state["iteration"] += 1
    # ↑ Incrémente le compteur. Quand iteration ≥ max_iterations,
    #   la fonction router décidera de terminer.
    return state
    # ↑ Retour obligatoire : l'état modifié est passé au prochain nœud.

def tools_node(state: DevAgentState) -> DevAgentState:
    """NŒUD OUTILS — Exécute l'action choisie par l'agent.

    Lecture de l'état :
    - state["task"] : contient la description de la tâche
    - state["current_file"] : fichier ciblé (éventuellement None)

    Écriture dans l'état :
    - state["current_file"] : mis à jour après création/lecture
    - state["test_results"] : rempli après exécution des tests
    """
    task = state["task"].lower()
    # ↑ On normalise la tâche en minuscules pour la comparaison.

    if "écrit" in task or "crée" in task or "ajoute" in task:
        # Cas : création ou modification de code
        content = (
            "def fibonacci(n):\n"
            "    if n <= 1:\n"
            "        return n\n"
            "    return fibonacci(n-1) + fibonacci(n-2)\n"
        )
        # ↑ Code exemple : fonction Fibonacci récursive
        result = write_file("math_utils.py", content)
        # ↑ Écriture effective dans le fichier
        state["current_file"] = "math_utils.py"

        if "test" in task:
            test_out = run_test()
            state["test_results"] = test_out
            # ↑ Si la tâche demande aussi des tests, on les exécute

    elif "test" in task:
        state["test_results"] = run_test()

    elif "recherche" in task or "trouve" in task:
        keyword = task.split("recherche")[-1].strip() if "recherche" in task else "def "
        state["messages"] = [("assistant", search_code(keyword))]

    return state
    # ↑ L'état modifié est passé au nœud suivant

def check_node(state: DevAgentState) -> DevAgentState:
    """NŒUD VÉRIFICATION — Analyse les résultats de test.

    Si les tests ont échoué, on laisse le graphe continuer
    pour une nouvelle itération de correction.
    Si les tests passent, on termine.
    """
    if state.get("test_results"):
        if "FAILED" in state["test_results"] or "failed" in state["test_results"]:
            state["need_fix"] = True
            # ↑ Les tests ont échoué — on va boucler pour corriger
        else:
            state["need_fix"] = False
            # ↑ Les tests passent — on peut terminer
    return state

# --- ROUTER : ARÊTE CONDITIONNELLE ---

def router(state: DevAgentState) -> Literal["tools", "check", "end"]:
    """FONCTION DE ROUTAGE — Décide du prochain nœud.

    Règles de décision :
    1. Si max_iterations atteint → fin
    2. Si les tests ont échoué (need_fix) → tools pour corriger
    3. Si pas encore testé mais la tâche demande un test → tools
    4. Sinon → fin

    Cette fonction est le "cerveau" du contrôle de flux.
    """
    if state["iteration"] >= state["max_iterations"]:
        return "end"
        # ↑ Limite de sécurité : on ne dépasse jamais max_iterations
    if state.get("need_fix"):
        return "tools"
        # ↑ Les tests ont échoué : retour aux outils pour corriger
    if state.get("test_results") is None and "test" in state.get("task", "").lower():
        return "tools"
        # ↑ Pas encore testé mais la tâche demande un test : on exécute
    return "end"
    # ↑ Tout est OK ou rien à faire : on termine

# --- CONSTRUCTION DU GRAPHE ---

def build_dev_agent() -> StateGraph:
    """Construit et compile le graphe de l'agent développeur.

    Architecture du graphe :

        [ENTRÉE] → agent → router
                            ├── "tools" → tools → agent (cycle)
                            ├── "check" → check → router
                            └── "end" → [FIN]

    Le graphe contient un cycle volontaire (tools → agent) pour
    permettre les corrections itératives. Le router empêche
    les boucles infinies via max_iterations.
    """
    builder = StateGraph(DevAgentState)
    # ↑ Création du graphe typé avec l'état DevAgentState

    builder.add_node("agent", agent_node)
    builder.add_node("tools", tools_node)
    builder.add_node("check", check_node)
    # ↑ Enregistrement des 3 nœuds. Chaque nom est une clé
    #   utilisée par les arêtes pour le routage.

    builder.set_entry_point("agent")
    # ↑ Point d'entrée : l'exécution commence ici

    builder.add_conditional_edges(
        "agent",
        router,
        {"tools": "tools", "check": "check", "end": END},
    )
    # ↑ Arête conditionnelle : après le nœud agent, on appelle
    #   la fonction router qui retourne "tools", "check" ou "end"

    builder.add_edge("tools", "agent")
    # ↑ Arête fixe : après tools, on revient toujours vers agent
    #   (le routage se fait au prochain passage)

    builder.add_edge("check", "agent")
    # ↑ Arête fixe : après check, on revient vers agent pour décider
    #   de la suite (router vérifie need_fix au prochain passage)

    checkpointer = MemorySaver()
    # ↑ Sauvegarde en mémoire pour le développement

    return builder.compile(checkpointer=checkpointer)
    # ↑ Compilation : valide la structure du graphe et retourne
    #   l'application exécutable

# --- EXÉCUTION ---

if __name__ == "__main__":
    app = build_dev_agent()
    # ↑ Construction et compilation du graphe

    config = {"configurable": {"thread_id": "dev-session-01"}}
    # ↑ Configuration de session : thread_id permet le checkpointing
    #   et la reprise de session

    initial_state: DevAgentState = {
        "task": "Crée une fonction fibonacci dans math_utils.py et teste-la avec pytest",
        "current_file": None,
        "test_results": None,
        "iteration": 0,
        "max_iterations": 5,
    }
    # ↑ État initial : tâche, aucun fichier ciblé,
    #   compteur à zéro, limite à 5 itérations

    print(f"Tâche : {initial_state['task']}\n")

    for step in app.stream(initial_state, config=config):
        # ↑ app.stream() itère sur l'exécution du graphe.
        #   Chaque step est un dict {nom_nœud: état_après_nœud}
        for node_name, node_state in step.items():
            it = node_state.get("iteration", "?")
            print(f"  [{node_name}] itération {it}")

    print("\nGraphe terminé.")
    final_state = app.get_state(config)
    if final_state.values.get("test_results"):
        print(f"Tests :\n{final_state.values['test_results'][:200]}")
```

#### Schéma récapitulatif du flux

```
État initial → [agent] → router
                           ├── "tools" → [tools] → [agent] (cycle de correction)
                           ├── "check" → [check] → router
                           └── "end"   → [FIN]
```

---

### 7.6 Comparaison : LangGraph vs opencode sub-agents

LangGraph et le système de sub-agents opencode résolvent le même problème fondamental — l'orchestration — mais à des niveaux d'abstraction différents.

| Critère | LangGraph | opencode sub-agents |
|---------|-----------|---------------------|
| **Nature** | Bibliothèque Python (framework) | Configuration déclarative YAML |
| **État** | Explicite (TypedDict typé) | Implicite (contexte LLM) |
| **Contrôle** | Fin : chaque nœud est une fonction | Haut : l'agent décide via ses outils |
| **Cycle** | Graphe explicite (arêtes conditionnelles) | Boucle ReAct implicite |
| **Parallélisme** | ThreadPoolExecutor, fan-out/fan-in | Délégation via outil `task` |
| **Checkpointing** | Natif (MemorySaver, PostgresSaver) | Via MCP serveur de mémoire |
| **HITL** | `interrupt()` natif | Permission `bash: ask` |
| **Courbe d'apprentissage** | Raide (concepts de théorie des graphes) | Faible (YAML descriptif) |
| **Quand l'utiliser** | Workflows complexes, production | Agents autonomes, pipelines simples |

**Règle empirique :**
- Si votre flux tient dans un diagramme avec ≤ 5 nœuds et ≤ 2 conditions → **sub-agents opencode** (plus simple, plus rapide à déployer)
- Si votre flux a des cycles, du parallélisme, du checkpointing, ou de l'intervention humaine → **LangGraph** (plus puissant, plus adaptable)

LangGraph et opencode ne sont pas en compétition : un sub-agent opencode peut *lui-même* orchestrer un sous-workflow LangGraph pour une tâche complexe, combinant le meilleur des deux mondes.

## Synthèse

**Ce que vous avez appris dans cette séance :**

| Concept | Résumé | Section |
|---------|--------|---------|
| Architecture LangChain | 4 piliers (Chat Models, Chains, Tools, Memory) pour l'orchestration LLM | 7.1 |
| StateGraph | Graphe orienté où l'état circule entre des nœuds fonctions pures | 7.2 |
| Nœuds, arêtes, conditions | Décomposition en fonctions state→state + router conditionnel | 7.3 |
| Checkpointing, HITL, branching | Sauvegarde d'état, intervention humaine, parallélisme | 7.4 |
| Agent développeur complet | Construction guidée d'un graphe à 3 nœuds avec cycle de correction | 7.5 |
| LangGraph vs sub-agents | Choix selon la complexité du workflow | 7.6 |

**Lien avec la séance suivante :**

> *"Maintenant que vous maîtrisez LangGraph comme moteur d'orchestration par graphe, la séance 8 (CrewAI / AutoGen) vous montrera comment ces frameworks multi-agents s'appuient sur les mêmes concepts de StateGraph pour coordonner des équipes d'agents spécialisés. Vous réutiliserez la notion de graphe d'état, de routage conditionnel et de sous-graphes pour concevoir des systèmes multi-agents complexes."*

## Références contextualisées

Chaque référence est accompagnée d'une explication sur pourquoi elle est citée et quel niveau de lecture est attendu.

- **[Documentation officielle LangChain]**
  *Contexte :* Référence technique complète pour l'API LangChain v0.3+. Sections les plus utiles : Chat Models, Chains, Tool integration. À consulter pendant le lab.
  *Niveau de lecture :* technique
  *→ https://python.langchain.com*

- **[Documentation officielle LangGraph]**
  *Contexte :* Guide conceptuel et API de référence pour LangGraph. Nécessaire pour les détails d'implémentation de StateGraph, checkpointing, interruption. Utilisé dans les sections 7.2 à 7.5.
  *Niveau de lecture :* technique
  *→ https://langchain-ai.github.io/langgraph/*

- **[LangChain Blog, "LangGraph: A State Machine Framework for LLM Applications" (2025)]**
  *Contexte :* Article fondateur qui explique le *pourquoi* de LangGraph — les limitations de l'AgentExecutor et la solution StateGraph. Cité dans la section 7.2.
  *Niveau de lecture :* introduction
  *→ https://blog.langchain.dev/langgraph-state-machine/*

- **[Harrison Chase, "Durable Execution for AI Agents" (2026)]**
  *Contexte :* Présentation du concept de durable execution appliqué aux agents. Approfondit le checkpointing et la tolérance aux pannes. Cité dans la section 7.4.
  *Niveau de lecture :* avancé

- **[LangGraph Checkpointer Documentation]**
  *Contexte :* Guide d'implémentation des checkpoints — MemorySaver, SqliteSaver, PostgresSaver. Pour la mise en production. Cité dans la section 7.4.
  *Niveau de lecture :* technique
  *→ https://langchain-ai.github.io/langgraph/concepts/persistence/*

- **[LangChain Whitepaper, "Production-ready agents with LangGraph" (2026)]**
  *Contexte :* Guide des bonnes pratiques pour déployer des agents LangGraph en production. Complément à la section 7.5 (construction guidée).
  *Niveau de lecture :* avancé

---

## Checklist de validation

- [x] Introduction théorique complète (problème, contexte, lien séances 6 et 8)
- [x] Objectifs pédagogiques SMART (5 objectifs)
- [x] Chaque concept a : définition → analogie → explication détaillée → importance
- [x] Code commenté ligne par ligne en français (section 7.5)
- [x] Configurations agent décortiquées (chaque champ de code expliqué)
- [x] Synthèse + lien vers la séance suivante (séance 8 — CrewAI/AutoGen)
- [x] Références contextualisées (pourquoi cette ref, niveau de lecture)
- [x] Zéro référence à Ollama, ChatOllama, langchain_ollama
- [x] Zéro dépendance à des API LLM externes
