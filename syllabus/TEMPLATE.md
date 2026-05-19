# Template de Séance — Cours M2 Nexa Agentic Dev 2026

Ce fichier définit la **structure canonique** que chaque séance de cours doit suivre. Il sert à la fois de guide de rédaction et de checklist de validation.

## Structure obligatoire d'une séance

```markdown
# Séance N — Titre de la séance

## Introduction théorique

Cette section plante le décor. Elle répond à trois questions :

1. **Quel est le problème fondamental que cette séance adresse ?**
   - Pourquoi existe-t-il un besoin pour ce concept dans un système agentique ?
   - Quel scénario réel motive son existence ? (ex: "un agent ne peut pas accéder
     à une base de données sans un protocole standardisé")

2. **Où se situe ce concept dans l'écosystème agentique 2026 ?**
   - Contexte historique : d'où vient cette idée, quelle évolution ?
   - Acteurs clés, standards, adoption actuelle
   - Chiffres clés (adoption, performances, coûts)

3. **Quel est le lien avec les séances précédentes et suivantes ?**
   - Prérequis techniques : "vous devez maîtriser [concept de la séance N-1]"
   - Compétences déjà acquises que vous allez mobiliser
   - Ce que cette séance prépare pour la suite

> **Exemple :** "Dans la séance 3, nous avons vu comment la mémoire permet
> à un agent de conserver un état à long terme. Dans cette séance 4, nous
> allons voir comment un agent peut accéder à des outils externes via le
> protocole MCP — c'est la différence entre un agent qui parle et un agent
> qui agit."

## Objectifs pédagogiques

À l'issue de cette séance, vous serez capable de :

1. **[Objectif 1]** — verbe d'action mesurable (analyser, concevoir,
   implémenter, configurer, évaluer...)
2. **[Objectif 2]**
3. **[Objectif 3]**

> Les objectifs doivent être SMART : Spécifiques, Mesurables, Atteignables,
> Réalistes, Temporels (dans le cadre de la séance).

## Plan détaillé

### N.1 [Premier concept fondamental] — PARTIE THÉORIQUE

#### Définition formelle

> **Définition :** [une phrase claire et complète du concept]
>
> *Exemple :* "Le Model Context Protocol (MCP) est un protocole standardisé
> de type JSON-RPC 2.0 qui permet à un agent LLM de découvrir et d'invoquer
> des outils, ressources et prompts exposés par des serveurs externes."

#### Analogie pédagogique

> *"MCP est au LLM ce que USB est à l'ordinateur : un standard universel
> qui permet de brancher n'importe quel périphérique (outil) sans
> configuration spécifique."*

#### Principe expliqué en détail

[Explication détaillée du principe, avec schéma ASCII si pertinent.
Décomposer en sous-points numérotés.]

```
Schéma illustrant le principe :
                            ┌─────────────────┐
                            │     Agent       │
                            │    (LLM/Host)   │
                            └────────┬────────┘
                                     │
                            Protocole standardisé
                            (JSON-RPC 2.0)
                                     │
                            ┌────────▼────────┐
                            │   Serveur MCP   │
                            │  (Tools/Data)   │
                            └─────────────────┘
```

#### Pourquoi ce concept est crucial

- **Impact sur la conception :** [ce que ça change concrètement]
- **Conséquence si ignoré :** [ce qui se passe sans ce concept]
- **Cas d'usage typique :** [scénario réel]

---

### N.2 [Deuxième concept] — PARTIE THÉORIQUE

[Même structure que N.1]

---

### N.3 [Construction guidée] — PARTIE PRATIQUE

Cette section est le **cœur pédagogique pratique**. Chaque fichier de
configuration ou de code est décortiqué ligne par ligne, en français,
pour que l'étudiant comprenne non seulement *ce que fait* chaque élément,
mais aussi *pourquoi* il est conçu ainsi.

#### 3.1 Analyse d'une configuration d'agent

Prenons le fichier `.opencode/agents/mon-agent.md` :

```yaml
---
description: Mon assistant de révision de code
# ↑ DESCRIPTION (obligatoire)
#   Phrase courte décrivant le rôle de l'agent.
#   Apparaît dans l'interface opencode et dans les logs de délégation.
mode: subagent
# ↑ MODE DE L'AGENT
#   - "subagent" : agent délégable via l'outil `task`.
#     C'est un agent spécialisé qui attend qu'on lui confie une mission.
#   - "primary" : agent principal qui démarre la session.
#     Un seul primary par projet (généralement le scrum-master).
#   - "custom" : agent sans mode prédéfini, utilisé ponctuellement.
model: opencode/big-pickle
# ↑ MODÈLE DE LLM
#   Ici, le modèle natif opencode (big-pickle).
#   IMPORTANT : Pas de LLM externe, pas d'API key, pas de serveur distant.
#   opencode gère le modèle automatiquement dans son runtime.
permission:
  read: allow
  # ↑ PERMISSION DE LECTURE (allow / deny)
  #   allow  → l'agent peut lire tous les fichiers du projet
  #   deny   → l'agent ne peut rien lire (très restrictif)
  #   Scénario : sans cette permission, un agent de review ne peut
  #   même pas inspecter le code qu'il doit évaluer. Inutilisable.
  glob: allow
  # ↑ PERMISSION DE RECHERCHE DE FICHIERS
  #   Permet d'utiliser l'outil `glob` pour trouver des fichiers
  #   par pattern, ex: glob("**/*.py") → tous les fichiers Python.
  grep: allow
  # ↑ PERMISSION DE RECHERCHE TEXTUELLE
  #   Permet d'utiliser l'outil `grep` pour chercher du texte
  #   dans le contenu des fichiers. Essentiel pour comprendre le code.
  list: allow
  # ↑ PERMISSION DE LISTAGE
  #   Permet de lister le contenu des répertoires.
  edit: allow
  # ↑ PERMISSION DE MODIFICATION (allow / deny)
  #   allow  → l'agent peut créer/modifier/supprimer des fichiers
  #   deny   → l'agent est en read-only (recommandé pour les reviewers)
  #   ATTENTION : action destructive ! Un agent mal configuré avec
  #   edit: allow + bash: allow peut causer des dégâts.
  task: allow
  # ↑ PERMISSION DE DÉLÉGATION
  #   allow  → l'agent peut déléguer des sous-tâches à d'autres agents
  #   C'est la CLÉ de l'orchestration multi-agents : un scrum-master
  #   peut appeler un software-engineer, qui peut appeler un test-writer.
  #   Sans task: allow, l'agent est isolé et ne peut pas coordonner.
  bash:
    python *: allow  # Python autorisé sans confirmation
    # ↑ Pattern de commande shell.
    #   "python *" signifie : toute commande commençant par "python"
    #   est autorisée sans demander à l'utilisateur.
    pip *: ask       # pip demande confirmation
    # ↑ "ask" signifie : opencode demande à l'utilisateur avant
    #   d'exécuter. Utile pour les commandes à risque (installation).
    find *: allow    # find autorisé
    *: ask           # TOUTE autre commande demande confirmation
    # ↑ Le pattern "*" est le fallback. Tout ce qui n'est pas
    #   explicitement listé tombe sur cette règle.
```

**Scénario concret d'exécution :**

1. Le `scrum-master` (agent primary) reçoit une mission : "revois le code
   et exécute les tests"
2. Il utilise l'outil `task` avec `agent: mon-agent` et `prompt: "..."``
3. opencode charge le fichier `.opencode/agents/mon-agent.md`
4. opencode vérifie les permissions : l'agent est-il autorisé à faire
   ce qu'on lui demande ?
5. L'agent reçoit sa mission comme une nouvelle session
6. Il lit les fichiers (`read`), cherche du code (`grep`), exécute
   Python (`bash: python *`) et modifie si nécessaire (`edit`)
7. Il retourne le résultat au `scrum-master`

#### 3.2 Analyse d'un fichier de code Python

```python
# === LAB — PARTIE X : [NOM DU MODULE] ===
# Fichier : lab/code/XX_nom/server.py
# Rôle    : [description du rôle de ce fichier dans le système]
# Dépendances : [bibliothèques externes nécessaires]
#
# Ce fichier implémente [concept] en suivant le pattern [design pattern].
# Il sera utilisé par [qui] pour [quoi].

# --- IMPORTS ---
# Chaque import est commenté pour expliquer pourquoi il est nécessaire.

import json
# ↑ Nécessaire pour sérialiser/désérialiser les données en JSON.
#   Les agents communiquent souvent en JSON (config, mémoire, MCP).

from pathlib import Path
# ↑ Manipulation de chemins fichiers de façon cross-platform.
#   Plus fiable que os.path.

from typing import TypedDict
# ↑ Typage : définit la structure des dictionnaires pour la mémoire.


# --- CLASSE PRINCIPALE ---
# Le nom de la classe reflète son rôle dans le système.
# On utilise le pattern [nom du pattern] pour [raison].

class AgentMemory:
    """Mémoire persistante pour agent opencode.

    Cette classe implémente une mémoire hiérarchique avec :
    - Une mémoire à court terme (STM) : buffer circulaire
    - Une mémoire à long terme (LTM) : liste consolidée
    - Un mécanisme de compactage : STM → LTM

    Le tout est persisté dans un fichier JSON pour survivre
    aux redémarrages de session opencode.
    """

    def __init__(self, path: str, window_size: int = 50):
        """Initialise la mémoire.

        Paramètres :
            path : chemin du fichier JSON de persistence
            window_size : nombre max d'entrées en mémoire court terme
        """
        self.path = path
        self.window_size = window_size
        self.short_term: deque = deque(maxlen=window_size)
        # ↑ deque : file à double extrémité avec taille max fixe.
        #   Quand on dépasse window_size, les plus anciennes entrées
        #   sont automatiquement supprimées (sliding window).
        self.long_term: list = []
        # ↑ Liste consolidée : contient les résumés des anciennes STM.
        self._load()
        # ↑ Restaure l'état depuis le fichier JSON s'il existe.

    # --- MÉTHODES PRIVÉES ---
    # (préfixe _) : utilisées en interne, pas exposées à l'extérieur.

    def _load(self):
        """Charge la mémoire depuis le fichier JSON."""
        if os.path.exists(self.path):
            # ↑ On vérifie que le fichier existe avant de lire.
            with open(self.path) as f:
                data = json.load(f)
                # ↑ json.load() parse le fichier en dictionnaire Python.
                self.short_term = deque(...)
                self.long_term = data.get("long_term", [])

    def _save(self):
        """Sauvegarde la mémoire dans le fichier JSON."""
        with open(self.path, "w") as f:
            json.dump({...}, f, indent=2)
        # ↑ indent=2 rend le fichier lisible par un humain.

    # ... suite des méthodes ...
```

#### 3.3 Analyse d'une configuration JSON/YAML

```json
{
  "mcp": {
    "dev-assistant": {
      // ↑ NOM DU SERVEUR MCP
      //   Identifiant unique utilisé par opencode pour se connecter.
      "type": "local",
      // ↑ TYPE DE TRANSPORT
      //   "local" : le serveur tourne sur la même machine (stdio)
      //   "remote" : serveur distant (HTTP+SSE)
      "command": ["python", "lab/code/02_mcp_server/server.py"],
      // ↑ COMMANDE DE LANCEMENT
      //   opencode exécute cette commande pour démarrer le serveur.
      //   Le serveur communique via stdio (JSON-RPC 2.0).
      "enabled": true
      // ↑ ACTIVÉ/DÉSACTIVÉ
      //   true  → opencode lance le serveur au démarrage
      //   false → serveur configuré mais pas lancé
    }
  }
}
```

---

### N.4 [Exercice / Lab associé]

```bash
# EXERCICE : [nom de l'exercice]
# Objectif : [compétence visée]
# Durée estimée : [X]h
# Prérequis : [séances ou concepts nécessaires]
#
# Étapes :
# 1. [étape 1] — [quoi faire et pourquoi]
# 2. [étape 2]
# 3. ...
```

Voir `lab/README.md` — Partie [X] pour les instructions complètes.

---

## Synthèse

**Ce que vous avez appris dans cette séance :**

| Concept | Résumé | Section |
|---------|--------|---------|
| [Concept 1] | [résumé en une phrase] | N.1 |
| [Concept 2] | [résumé en une phrase] | N.2 |
| [Compétence pratique] | [résumé] | N.3 |

**Lien avec la séance suivante :**

> *"Maintenant que vous savez configurer [concept de cette séance],
> la séance N+1 vous apprendra à [concept suivant]. Vous réutiliserez
> [élément de cette séance] comme base pour [compétence suivante]."*

## Références contextualisées

Chaque référence est accompagnée d'une explication sur pourquoi elle est
citée et quel niveau de lecture est attendu.

- **[Auteur, Titre (Année)]**
  *Contexte :* Ce papier/framework est cité dans la section N.1 car il
  pose les bases du concept X. Il explique [lien avec le cours].
  *Niveau de lecture :* [introduction / avancé / expert]
  *→ URL*

- **[Documentation officielle]**
  *Contexte :* Référence technique pour implémenter le concept de la
  section N.3. À consulter pendant le lab.
  *Niveau de lecture :* technique
  *→ URL*

---

## Checklist de validation

Avant de livrer une séance, vérifier :

- [ ] Introduction théorique complète (problème, contexte, lien séances)
- [ ] Objectifs pédagogiques SMART (3-5 objectifs)
- [ ] Chaque concept a : définition → analogie → explication détaillée → importance
- [ ] Code commenté ligne par ligne en français (pas de blocs sans explication)
- [ ] Configurations agent décortiquées (chaque champ YAML/JSON expliqué)
- [ ] Permissions agent expliquées avec scénario concret
- [ ] Synthèse + lien vers la séance suivante
- [ ] Références contextualisées (pourquoi cette ref, niveau de lecture)
- [ ] Zéro référence à Ollama, ChatOllama, langchain_ollama
- [ ] Zéro dépendance à des API LLM externes
