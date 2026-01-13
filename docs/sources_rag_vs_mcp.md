# RAG vs MCP : Sources pour l'argumentaire

## Résumé de la recommandation

Pour des données **structurées et critiques** (comme les RFE antibioprophylaxie), **MCP > RAG** car :
1. Réponses déterministes (pas d'hallucinations sur les doses)
2. Accès direct aux données structurées
3. Intégrable dans des workflows cliniques

---

## Sources officielles

### 1. Anthropic - Introduction officielle du MCP
**URL** : https://www.anthropic.com/news/model-context-protocol

> "The Model Context Protocol is an open standard that enables developers to build secure, two-way connections between their data sources and AI-powered tools."

**Point clé** : MCP est conçu pour un accès **direct et standardisé** aux données, pas pour de la recherche sémantique.

---

### 2. Google Cloud - Comparaison RAG vs MCP
**URL** : https://cloud.google.com/discover/what-is-model-context-protocol

> "RAG finds and uses information for creating text, while MCP is a wider system for interaction and action."
>
> "Standardize two-way communication for LLMs to access and interact with external tools, data sources, and services to perform actions alongside information retrieval."

**Point clé** : RAG = recherche sémantique dans du texte. MCP = interaction bidirectionnelle avec des systèmes structurés.

---

### 3. Airbyte - MCP vs RAG technique
**URL** : https://airbyte.com/agentic-data/mcp-vs-rag

> "RAG focuses on grounding model responses in pre-indexed knowledge. It retrieves relevant documents at query time and injects them into the prompt, making it well suited for semantic search across large, mostly static corpora."
>
> "MCP takes a different approach. It gives agents a standardized way to query and act on live systems during inference, pulling current data directly from APIs and services."

**Point clé essentiel** :
> "RAG excels at grounding responses in static, unstructured knowledge while MCP allows secure access to **structured, dynamic data**."

---

### 4. Limitations du RAG en contexte médical

#### 4.1 Nature - Étude sur RAG en médecine
**URL** : https://www.nature.com/articles/s41746-025-01519-z

> "Although RAG significantly reduces hallucinations [...] occasional inaccuracies persist. For instance, ChatGPT sometimes includes diagnostic tests not listed in clinical guidelines."

#### 4.2 PMC - Revue systématique RAG en santé
**URL** : https://pmc.ncbi.nlm.nih.gov/articles/PMC12157099/

> "Retrieval inaccuracies can result in irrelevant chunk selection, directly impacting response quality. The generation phase remains susceptible to hallucinations where models produce information not substantiated by retrieved content."

#### 4.3 PMC - MEGA-RAG pour réduire les hallucinations
**URL** : https://pmc.ncbi.nlm.nih.gov/articles/PMC12540348/

> "LLM + RAG reduces outright fabrication but still presents speculative antiviral mechanisms lacking rigorous support."

**Point clé** : Même avec RAG, les LLM peuvent générer des informations **non vérifiées** - inacceptable pour des posologies d'antibiotiques.

---

### 5. K2View - RAG et données structurées
**URL** : https://www.k2view.com/blog/rag-hallucination/

> "Although regular RAG grounds LLMs with **unstructured data** from internal sources, hallucinations still occur. Add **structured data** to the mix to reduce them."

**Point clé** : Le RAG est optimisé pour du texte non structuré. Pour des tableaux structurés (ATB/dose/réinjection), une BDD + API est plus adaptée.

---

## Synthèse pour votre argumentaire

| Critère | RAG | MCP / API directe |
|---------|-----|-------------------|
| **Type de données** | Texte non structuré | Données structurées (tableaux) |
| **Risque d'hallucination** | Présent (même réduit) | Nul (réponses déterministes) |
| **Précision des doses** | Variable | Exacte |
| **Mise à jour** | Re-embedding nécessaire | Modification BDD uniquement |
| **Intégration DxCare/SI** | Complexe | API REST standard |
| **Traçabilité** | Limitée | Complète |

### Conclusion

Pour les RFE antibioprophylaxie :
- Les données sont **structurées** (tableaux acte → ATB → dose)
- La précision des doses est **critique** (risque patient)
- Les mises à jour sont **fréquentes** (révisions RFE)

→ **Architecture recommandée** : BDD structurée + API REST + MCP server (optionnel pour assistants IA)

---

## Références complémentaires

- MCP Official Docs : https://docs.anthropic.com/en/docs/build-with-claude/mcp
- MCP GitHub : https://github.com/modelcontextprotocol
- Annonce donation Linux Foundation : https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation
