---
name: cybersecurity
description: Compétences en cybersécurité — audit de code, OWASP LLM, permissions, injections, bonnes pratiques de sécurisation des agents. Skill du cybersecurity-engineer.
---

# Skill: cybersecurity

## Périmètre
- Audit de sécurité des agents et du code
- Détection de vulnérabilités (prompt injection, data leakage)
- Vérification des permissions et isolation
- Conformité OWASP Top 10 for LLM Applications
- Documentation des bonnes pratiques

## OWASP LLM Top 10 (résumé)
| # | Risque | Description |
|---|--------|-------------|
| LLM01 | Prompt Injection | Entrée utilisateur manipule le LLM |
| LLM02 | Data Leakage | Fuite de données sensibles |
| LLM03 | Insecure Output Handling | Sortie non filtrée exécutée |
| LLM04 | Model Denial of Service | Attaque par consommation excessive |
| LLM05 | Supply Chain | Vulnérabilités des dépendances |
| LLM06 | Permission Issues | Mauvaise isolation des agents |
| LLM07 | Data Poisoning | Entraînement corrompu |
| LLM08 | Excessive Agency | Agent trop permissif |
| LLM09 | Overreliance | Confiance excessive dans le LLM |
| LLM10 | Model Theft | Vol du modèle |

## Checklist sécurité
- [ ] Pas de secrets hardcodés (API keys, tokens)
- [ ] Prompt injection mitigée (input validation, sandboxing)
- [ ] Permissions least-privilege pour chaque agent
- [ ] Input validation sur tous les tool calls
- [ ] Rate limiting et quotas configurés
- [ ] Audit logging des actions agent
- [ ] Isolation des contextes entre sessions
- [ ] Sanitization des sorties LLM avant exécution
- [ ] Conformité OWASP LLM vérifiée

## Règles
- Mode read-only — auditer et rapporter, ne pas modifier
- Signaler tout risque avec sévérité (critical/high/medium/low)
- Proposer des corrections sans les appliquer
