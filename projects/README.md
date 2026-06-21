# Projets — Agentic Development M2 Nexa 2026

## Projet 1: DevOps Agent Autonome

**Difficulté:** Avancé
**Binômes:** 2 étudiants

**Objectif:** Construire un agent autonome qui déploie, surveille et répare une infrastructure cloud.

**Spécifications:**
- Utilise LangGraph pour l'orchestration
- MCP pour l'interaction avec les APIs locales et services open-source
- GitHub Agents pour l'intégration CI/CD
- Mémoire persistante pour l'historique des incidents

**Fonctionnalités clés:**
1. Déploiement automatique à partir d'une PR
2. Surveillance des métriques (CPU, mémoire, erreurs)
3. Détection et diagnostic d'incidents
4. Auto-réparation (rollback, scale-up, restart)
5. Rapport post-mortem généré par agent

**Livrables:**
- Code source (graphe LangGraph, serveurs MCP, agents GitHub)
- Documentation README avec architecture
- Démo vidéo (5 min)
- Rapport d'analyse: choix architecturaux, coûts, performances

---

## Projet 2: Code Reviewer Multi-Agent

**Difficulté:** Intermédiaire
**Binômes:** 2 étudiants

**Objectif:** Système multi-agent pour la revue de code avec MCP + GitHub API.

**Spécifications:**
- CrewAI pour l'équipe d'agents (Security, Style, Performance, Tests)
- MCP pour l'accès aux outils (linters, scanners, analyseurs)
- GitHub Custom Agent pour l'intégration PR
- Mémoire des revues précédentes

**Fonctionnalités clés:**
1. Analyse statique du code (ESLint, PyLint, Ruff, etc.)
2. Scan de sécurité (Semgrep, Bandit)
3. Analyse de performance (profilage suggéré)
4. Génération de suggestions de correction
5. Apprentissage des préférences de l'équipe

**Livrables:**
- Code source (Crew, serveurs MCP, outils personnalisés)
- Documentation README
- Stats d'utilisation sur un repo test
- Rapport: précision, faux positifs, temps de revue

---

## Projet 3: Research Assistant Agent

**Difficulté:** Intermédiaire
**Binômes:** 2 étudiants

**Objectif:** Agent de recherche bibliographique avec RAG, extraction et synthèse.

**Spécifications:**
- RAG avec ChromaDB ou Weaviate
- MCP pour l'accès aux sources (ArXiv, Semantic Scholar, web)
- LangGraph pour le workflow de recherche
- A2A-ready pour interaction avec d'autres agents

**Fonctionnalités clés:**
1. Recherche multi-source avec dédup
2. Extraction structurée (méthodes, résultats, citations)
3. Synthèse avec cartographie des idées
4. Génération de revue de littérature
5. Mémoire des recherches précédentes

**Livrables:**
- Code source (pipeline RAG, serveurs MCP, graphe)
- Documentation README
- Démo: "Research a topic and produce a survey"
- Rapport: qualité des réponses, coûts LLM, latence

---

## Projet 4: Sujet Libre

**Difficulté:** Variable
**Binômes:** 2 étudiants

**Processus:**
1. Proposition d'1 page (problème, solution, architecture, faisabilité)
2. Validation par l'enseignant
3. Implémentation
4. Soutenance

**Critères d'évaluation:**
- Utilisation d'au moins 2 technologies du cours (MCP, LangGraph, CrewAI, GitHub Agents)
- Architecture claire et documentée
- Tests et évaluation
- Originalité et pertinence

---

## Calendrier

| Date | Étape |
|------|-------|
| Séance 8 | Annonce et formation des binômes |
| Séance 10 | Proposition / validation du sujet |
| Séance 12 | Revue de mi-parcours |
| Séance 14 | Soutenance finale |

## Barème d'évaluation

| Critère | Poids |
|---------|-------|
| Fonctionnalité et robustesse | 30% |
| Architecture et design | 25% |
| Qualité du code | 15% |
| Documentation et README | 15% |
| Présentation et démo | 15% |
