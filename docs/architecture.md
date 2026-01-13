# Architecture technique

## Vue d'ensemble

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│   PDF Source    │────▶│  Script Python   │────▶│    JSON structuré   │
│   (SFAR 2024)   │     │  (extraction)    │     │  (base de données)  │
└─────────────────┘     └──────────────────┘     └──────────┬──────────┘
                                                            │
                         ┌──────────────────────────────────┼──────────────────────────────────┐
                         │                                  │                                  │
                         ▼                                  ▼                                  ▼
                ┌─────────────────┐              ┌─────────────────┐              ┌─────────────────┐
                │   API REST      │              │   MCP Server    │              │   Web App       │
                │   (intégration  │              │   (assistants   │              │   (recherche    │
                │   SI hôpital)   │              │   IA)           │              │   rapide)       │
                └─────────────────┘              └─────────────────┘              └─────────────────┘
```

## Composants

### 1. Extraction (`src/extract_rfe_atb.py`)

**Rôle** : Transformer le PDF SFAR en données JSON structurées.

**Technologie** : 
- `pdfplumber` pour l'extraction de tableaux
- `pandas` pour la manipulation des données

**Entrée** : PDF des RFE Antibioprophylaxie
**Sortie** : JSON structuré avec :
- Métadonnées (source, version, date)
- Recommandations générales
- Données par acte (spécialité, ATB, dose, alternative, réinjection, grade)

### 2. Serveur MCP (`src/mcp_server_rfe.py`)

**Rôle** : Exposer les données aux assistants IA via le Model Context Protocol.

**Outils exposés** :
- `rechercher_antibioprophylaxie` : recherche par acte
- `lister_specialites` : liste des spécialités
- `lister_actes_specialite` : actes d'une spécialité
- `recommandations_generales` : timing, réinjection, durée

**Intégration** : Claude Desktop, Claude Code, ou tout client MCP.

### 3. API REST (optionnel, à développer)

**Rôle** : Intégration avec les SI hospitaliers (DxCare, etc.)

**Endpoints suggérés** :
```
GET /api/v1/antibioprophylaxie?acte={acte}
GET /api/v1/specialites
GET /api/v1/specialites/{specialite}/actes
GET /api/v1/recommandations-generales
```

## Schéma de données

```json
{
  "metadata": {
    "source": "SFAR - RFE Antibioprophylaxie 2024",
    "version": "2.0",
    "date_extraction": "2026-01-13T00:00:00"
  },
  "recommandations_generales": {
    "timing": { ... },
    "reinjection": { ... },
    "duree": { ... }
  },
  "data": [
    {
      "specialite": "Chirurgie orthopédique",
      "acte": "Prothèse totale de hanche",
      "antibiotique": "Céfazoline",
      "posologie": "2g IV",
      "alternative_allergie": "Vancomycine 15mg/kg",
      "reinjection": "1g toutes les 4h",
      "duree": "Dose unique",
      "grade": "GRADE 1"
    }
  ]
}
```

## Flux de mise à jour

1. Nouvelle version RFE publiée par la SFAR
2. Téléchargement du PDF
3. Exécution du script d'extraction
4. Validation manuelle des données extraites
5. Commit et push sur le dépôt
6. Les services (MCP, API) utilisent automatiquement les nouvelles données

## Considérations de sécurité

- Pas de données patient
- Données publiques (recommandations officielles)
- Validation obligatoire avant usage clinique
- Traçabilité via versioning git

## Évolutions possibles

1. **Base de données** : Migration vers SQLite/PostgreSQL pour requêtes complexes
2. **Versioning des RFE** : Garder l'historique des recommandations
3. **Multi-langues** : Traductions des recommandations
4. **Alertes** : Notification lors de mises à jour des RFE
5. **Intégration FHIR** : Format standard d'interopérabilité santé
