# Guide d'Installation — Cours M2 Nexa Agentic Development


---

## Prérequis matériel

| Composant | Minimum | Recommandé |
|-----------|---------|------------|
| RAM | 8 Go | 16+ Go |
| CPU | 2 cœurs | 4+ cœurs |
| Disque | 10 Go libres | 20+ Go |
| OS | Windows 10, macOS 12, Ubuntu 20.04 | Dernière version |

---

## Installation par système d'exploitation

### Linux (Ubuntu/Debian)

```bash
# 1. Mettre à jour les paquets
sudo apt update && sudo apt upgrade -y

# 2. Installer Python 3.10+, pip, venv, Git et Docker
sudo apt install python3 python3-pip python3-venv git docker.io -y

# 3. Autoriser l'utilisateur courant à utiliser Docker sans sudo
sudo usermod -aG docker "$USER"

# 4. Déconnectez-vous puis reconnectez-vous, puis vérifier Docker
docker --version
docker run hello-world

# 5. Installer opencode
python3 -m pip install --user opencode

# 6. Vérifier tous les outils
python3 --version    # Python 3.10+
python3 -m pip --version
git --version
docker --version
opencode --version

# 7. Tester le modèle gratuit big-pickle
opencode -m opencode/big-pickle -t "Bonjour, quel est ton rôle ?"
```

> **Résultat attendu :** Chaque commande affiche une version. Docker exécute `hello-world` avec succès. L'agent opencode répond avec une présentation.

---

### macOS

```bash
# 1. Installer Homebrew si nécessaire : https://brew.sh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Installer Python, Git et Docker Desktop
brew install python git
brew install --cask docker

# 3. Ouvrir Docker Desktop une première fois
open -a Docker
# Attendre que Docker démarre (icône baleine dans la barre de menu)

# 4. Vérifier Docker
docker --version
docker run hello-world

# 5. Installer opencode
python3 -m pip install --user opencode

# 6. Vérifier tous les outils
python3 --version
python3 -m pip --version
git --version
docker --version
opencode --version

# 7. Tester le modèle gratuit big-pickle
opencode -m opencode/big-pickle -t "Bonjour, quel est ton rôle ?"
```

> **Résultat attendu :** Chaque commande affiche une version. Docker exécute `hello-world` avec succès. L'agent opencode répond avec une présentation.

---

### Windows 10/11 (PowerShell)

Ouvrez **PowerShell** en mode normal (pas en administrateur), puis exécutez :

```powershell
# 1. Installer Python 3.12, Git et Docker Desktop avec winget
winget install Python.Python.3.12
winget install Git.Git
winget install Docker.DockerDesktop

# 2. Redémarrer Windows
# (Nécessaire pour que Python et Git soient dans le PATH)

# 3. Ouvrir Docker Desktop
# (Cliquer sur l'icône Docker dans le menu Démarrer)
# Attendre que Docker démarre (icône baleine dans la barre des tâches)

# 4. Vérifier Docker dans un nouveau PowerShell
docker --version
docker run hello-world

# 5. Installer opencode
py -m pip install --user opencode

# 6. Vérifier tous les outils
py --version
py -m pip --version
git --version
docker --version
opencode --version

# 7. Tester le modèle gratuit big-pickle
opencode -m opencode/big-pickle -t "Bonjour, quel est ton rôle ?"
```

> **Résultat attendu :** Chaque commande affiche une version. Docker exécute `hello-world` avec succès. L'agent opencode répond avec une présentation.

---

## Installation des dépendances par séance

### Séance 1-2 : Fondamentaux

```bash
# Linux/macOS
python3 -m pip install tiktoken pytest

# Windows PowerShell
py -m pip install tiktoken pytest
```

### Séance 3 : Mémoire

```bash
# Linux/macOS
python3 -m pip install sentence-transformers

# Windows PowerShell
py -m pip install sentence-transformers
```

### Séance 4 : MCP

```bash
# Linux/macOS
python3 -m pip install mcp anyio

# Windows PowerShell
py -m pip install mcp anyio
```

### Séance 5 : A2A

```bash
# Linux/macOS
python3 -m pip install a2a-sdk

# Windows PowerShell
py -m pip install a2a-sdk
```

### Séance 7 : LangGraph

```bash
# Linux/macOS
python3 -m pip install langgraph langchain-core

# Windows PowerShell
py -m pip install langgraph langchain-core
```

### Séance 8 : CrewAI & AutoGen

```bash
# Linux/macOS
python3 -m pip install crewai autogen-agentchat

# Windows PowerShell
py -m pip install crewai autogen-agentchat
```

### Séance 9 : RAG

```bash
# Linux/macOS
python3 -m pip install chromadb

# Windows PowerShell
py -m pip install chromadb
```

### Séance 12 : Benchmarks

```bash
# Linux/macOS
python3 -m pip install langsmith

# Windows PowerShell
py -m pip install langsmith
```

---

## Convention de commandes

| Usage | Linux/macOS | Windows PowerShell |
|---|---|---|
| Lancer Python | `python3 script.py` | `py script.py` |
| Installer un paquet | `python3 -m pip install paquet` | `py -m pip install paquet` |
| Lancer pytest | `python3 -m pytest tests/ -v` | `py -m pytest tests/ -v` |
| Lancer ruff | `python3 -m ruff check .` | `py -m ruff check .` |
| Commandes Git | `git ...` | `git ...` |
| Commandes Docker | `docker ...` | `docker ...` |
| Commandes opencode | `opencode ...` | `opencode ...` |

---

## Convention de dossiers pour les TPs

### Linux/macOS

```bash
# Créer le dossier de travail principal
mkdir -p ~/agentic-labs
cd ~/agentic-labs

# Pour chaque TP, créer un sous-dossier
mkdir seance-01 && cd seance-01
pwd
```

### Windows PowerShell

```powershell
# Créer le dossier de travail principal
mkdir $HOME\agentic-labs
cd $HOME\agentic-labs

# Pour chaque TP, créer un sous-dossier
mkdir seance-01
cd seance-01
pwd
```

> **Résultat attendu :** `pwd` affiche le chemin du dossier du TP courant.

---

## Vérification finale

Après avoir suivi toutes les étapes, vérifiez que :

- [ ] `python3 --version` affiche Python 3.10+
- [ ] `pip --version` affiche une version
- [ ] `git --version` affiche une version
- [ ] `docker --version` affiche une version
- [ ] `docker run hello-world` affiche "Hello from Docker!"
- [ ] `opencode --version` affiche une version
- [ ] `opencode -m opencode/big-pickle -t "Bonjour"` reçoit une réponse

---

## Dépannage

### Docker ne démarre pas

**Linux :** Vérifiez que le service Docker est actif :
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

**Windows :** Si Docker Desktop ne démarre pas, vérifiez que l'hyper-v est activé :
```powershell
# PowerShell en administrateur
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
```

### opencode n'est pas trouvé

**Linux/macOS :** Ajoutez le chemin utilisateur au PATH :
```bash
export PATH="$HOME/.local/bin:$PATH"
# Ajoutez cette ligne à ~/.bashrc ou ~/.zshrc
```

**Windows :** Redémarrez PowerShell après l'installation de opencode.

### Problèmes de permissions

**Linux :** Si Docker demande sudo à chaque fois :
```bash
sudo usermod -aG docker "$USER"
# Déconnectez-vous et reconnectez-vous
```
