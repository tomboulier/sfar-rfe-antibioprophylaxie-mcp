# RFE Antibioprophylaxie - SFAR

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Outils pour digitaliser et exploiter les **Recommandations Formalisées d'Experts (RFE)** sur l'antibioprophylaxie en chirurgie et médecine interventionnelle de la [SFAR](https://sfar.org).

## 🎯 Objectif

Rendre les RFE antibioprophylaxie accessibles et automatisables :
- **Extraction** des tableaux PDF vers JSON structuré
- **API REST** pour intégration dans les SI hospitaliers
- **Serveur MCP** pour les assistants IA (Claude, etc.)

## 📁 Structure

```
rfe-antibioprophylaxie/
├── src/
│   ├── extract_rfe_atb.py    # Extraction PDF → JSON
│   └── mcp_server_rfe.py     # Serveur MCP
├── data/
│   └── exemple_structure.json # Exemple de données structurées
├── docs/
│   ├── architecture.md        # Architecture technique
│   └── sources_rag_vs_mcp.md  # Argumentaire RAG vs MCP
└── tests/
    └── test_extraction.py     # Tests unitaires
```

## 🚀 Installation

```bash
# Cloner le dépôt
git clone https://github.com/VOTRE_USERNAME/rfe-antibioprophylaxie.git
cd rfe-antibioprophylaxie

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
```

## 📖 Usage

### 1. Extraire les données du PDF

```bash
# Télécharger le PDF source
wget "https://sfar.org/download/antibioprophylaxie-en-chirurgie-et-medecine-interventionnelle/?wpdmdl=68362" -O rfe_2024.pdf

# Extraire les données
python src/extract_rfe_atb.py rfe_2024.pdf data/rfe_antibioprophylaxie.json
```

### 2. Utiliser le serveur MCP (pour Claude Desktop)

```bash
# Lancer le serveur
python src/mcp_server_rfe.py
```

Configuration dans `~/.claude/claude_desktop_config.json` :
```json
{
  "mcpServers": {
    "rfe-antibioprophylaxie": {
      "command": "python",
      "args": ["/chemin/vers/src/mcp_server_rfe.py"]
    }
  }
}
```

### 3. Requêter les données

```python
import json

with open("data/rfe_antibioprophylaxie.json") as f:
    data = json.load(f)

# Rechercher l'ATB pour une PTH
for record in data["data"]:
    if "hanche" in record["acte"].lower():
        print(f"{record['acte']}: {record['antibiotique']} {record['posologie']}")
```

## 🔧 Outils MCP disponibles

| Outil | Description |
|-------|-------------|
| `rechercher_antibioprophylaxie` | Recherche l'ATB pour un acte chirurgical |
| `lister_specialites` | Liste les spécialités couvertes |
| `lister_actes_specialite` | Liste les actes d'une spécialité |
| `recommandations_generales` | Timing, réinjection, durée |

## 📊 Pourquoi pas RAG ?

Pour des données **structurées et critiques** (doses d'antibiotiques), nous avons choisi une approche base de données + API/MCP plutôt que RAG :

| Critère | RAG | BDD + API/MCP |
|---------|-----|---------------|
| Type de données | Texte non structuré | Données structurées |
| Risque hallucination | Présent | Nul |
| Précision des doses | Variable | Exacte |
| Mise à jour | Re-embedding | Modification BDD |

Voir [docs/sources_rag_vs_mcp.md](docs/sources_rag_vs_mcp.md) pour l'argumentaire complet avec sources.

## 🏥 Source des données

- **Document** : RFE Antibioprophylaxie SFAR/SPILF 2024 (v2.0)
- **URL** : https://sfar.org/antibioprophylaxie-en-chirurgie-et-medecine-interventionnelle/
- **Sociétés savantes** : SFAR, SPILF, AFU, SFR, SFCR, SFO, SFORL, SOFCOT, etc.

## ⚠️ Avertissement

Ces outils sont fournis à titre d'aide à la décision. **Les données extraites doivent être validées** avant utilisation clinique. En cas de doute, référez-vous toujours au document source officiel.

## 🤝 Contribution

Contributions bienvenues ! Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour les guidelines.

## 📄 Licence

MIT License - voir [LICENSE](LICENSE)

## 👥 Auteurs

- Groupe Numérique SFAR

---

*Projet initié dans le cadre de la digitalisation des recommandations médicales françaises.*
