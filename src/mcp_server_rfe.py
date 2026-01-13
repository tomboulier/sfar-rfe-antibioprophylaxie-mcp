#!/usr/bin/env python3
"""
Serveur MCP pour les RFE Antibioprophylaxie SFAR.

Ce serveur expose les données d'antibioprophylaxie via le Model Context Protocol,
permettant à Claude et autres LLMs d'accéder aux recommandations de manière structurée.

Installation:
    pip install mcp

Usage:
    python mcp_server_rfe.py

Configuration Claude Desktop (claude_desktop_config.json):
    {
      "mcpServers": {
        "rfe-antibioprophylaxie": {
          "command": "python",
          "args": ["/chemin/vers/mcp_server_rfe.py"]
        }
      }
    }

Auteur: Groupe Numérique SFAR
Version: 1.0.0
"""

import json
from pathlib import Path
from typing import Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Chemin vers le fichier JSON des RFE
RFE_DATA_PATH = Path(__file__).parent / "rfe_antibioprophylaxie.json"

# Initialisation du serveur MCP
server = Server("rfe-antibioprophylaxie")


def load_rfe_data() -> dict:
    """Charge les données RFE depuis le fichier JSON."""
    if not RFE_DATA_PATH.exists():
        return {"metadata": {}, "data": []}
    
    with open(RFE_DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


@server.list_tools()
async def list_tools() -> list[Tool]:
    """Liste les outils disponibles."""
    return [
        Tool(
            name="rechercher_antibioprophylaxie",
            description="Recherche l'antibioprophylaxie recommandée pour un acte chirurgical donné",
            inputSchema={
                "type": "object",
                "properties": {
                    "acte": {
                        "type": "string",
                        "description": "L'acte chirurgical (ex: 'prothèse de hanche', 'appendicectomie')"
                    },
                    "specialite": {
                        "type": "string",
                        "description": "La spécialité chirurgicale (optionnel, ex: 'orthopédie', 'digestif')"
                    }
                },
                "required": ["acte"]
            }
        ),
        Tool(
            name="lister_specialites",
            description="Liste toutes les spécialités chirurgicales couvertes par les RFE",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="lister_actes_specialite",
            description="Liste tous les actes pour une spécialité donnée",
            inputSchema={
                "type": "object",
                "properties": {
                    "specialite": {
                        "type": "string",
                        "description": "La spécialité chirurgicale"
                    }
                },
                "required": ["specialite"]
            }
        ),
        Tool(
            name="recommandations_generales",
            description="Retourne les recommandations générales sur l'antibioprophylaxie (timing, réinjection, durée)",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Exécute un outil."""
    data = load_rfe_data()
    
    if name == "rechercher_antibioprophylaxie":
        return await rechercher_antibioprophylaxie(
            data,
            arguments.get("acte", ""),
            arguments.get("specialite")
        )
    
    elif name == "lister_specialites":
        return await lister_specialites(data)
    
    elif name == "lister_actes_specialite":
        return await lister_actes_specialite(
            data,
            arguments.get("specialite", "")
        )
    
    elif name == "recommandations_generales":
        return await get_recommandations_generales(data)
    
    return [TextContent(type="text", text=f"Outil inconnu: {name}")]


async def rechercher_antibioprophylaxie(
    data: dict,
    acte: str,
    specialite: Optional[str] = None
) -> list[TextContent]:
    """
    Recherche l'antibioprophylaxie pour un acte donné.
    
    La recherche est fuzzy sur le nom de l'acte.
    """
    acte_lower = acte.lower()
    resultats = []
    
    for record in data.get("data", []):
        # Filtre par spécialité si spécifiée
        if specialite:
            if specialite.lower() not in record.get("specialite", "").lower():
                continue
        
        # Recherche fuzzy sur l'acte
        record_acte = record.get("acte", "").lower()
        if acte_lower in record_acte or record_acte in acte_lower:
            resultats.append(record)
    
    if not resultats:
        return [TextContent(
            type="text",
            text=f"Aucune recommandation trouvée pour '{acte}'. "
                 f"Vérifiez l'orthographe ou consultez la liste des actes avec 'lister_actes_specialite'."
        )]
    
    # Formate les résultats
    output = []
    for r in resultats:
        output.append(f"""
## {r['acte']} ({r['specialite']})

- **Antibiotique**: {r['antibiotique']}
- **Posologie**: {r['posologie']}
- **Alternative si allergie**: {r.get('alternative_allergie', 'Non spécifié')}
- **Réinjection**: {r.get('reinjection', 'Non applicable')}
- **Durée**: {r.get('duree', 'Dose unique')}
- **Grade**: {r.get('grade', 'Non précisé')}
{f"- **Note**: {r['commentaire']}" if r.get('commentaire') else ""}
""")
    
    return [TextContent(type="text", text="\n".join(output))]


async def lister_specialites(data: dict) -> list[TextContent]:
    """Liste les spécialités disponibles."""
    specialites = data.get("metadata", {}).get("specialites", [])
    
    if not specialites:
        # Extrait des données si pas dans les métadonnées
        specialites = sorted(set(
            r.get("specialite", "") 
            for r in data.get("data", [])
            if r.get("specialite")
        ))
    
    return [TextContent(
        type="text",
        text="## Spécialités couvertes par les RFE Antibioprophylaxie\n\n" + 
             "\n".join(f"- {s}" for s in specialites)
    )]


async def lister_actes_specialite(data: dict, specialite: str) -> list[TextContent]:
    """Liste les actes pour une spécialité."""
    specialite_lower = specialite.lower()
    
    actes = [
        r.get("acte", "")
        for r in data.get("data", [])
        if specialite_lower in r.get("specialite", "").lower()
    ]
    
    if not actes:
        return [TextContent(
            type="text",
            text=f"Aucun acte trouvé pour la spécialité '{specialite}'. "
                 f"Utilisez 'lister_specialites' pour voir les spécialités disponibles."
        )]
    
    return [TextContent(
        type="text",
        text=f"## Actes - {specialite}\n\n" + 
             "\n".join(f"- {a}" for a in sorted(set(actes)))
    )]


async def get_recommandations_generales(data: dict) -> list[TextContent]:
    """Retourne les recommandations générales."""
    reco = data.get("recommandations_generales", {})
    
    if not reco:
        # Valeurs par défaut basées sur les RFE 2024
        reco = {
            "timing": {
                "description": "Administration au plus tôt 60 min avant, au plus tard avant l'incision",
                "grade": "GRADE 1"
            },
            "reinjection": {
                "intervalles": {
                    "céfoxitine": "2h (1g)",
                    "céfuroxime": "2h (0.75g)",
                    "amoxicilline/clavulanate": "2h (1g)",
                    "céfazoline": "4h (1g)",
                    "clindamycine": "4h (450mg)",
                    "vancomycine": "8h (10mg/kg)"
                },
                "grade": "GRADE 2"
            },
            "duree": {
                "description": "Pas de prolongation au-delà de la fin de chirurgie",
                "grade": "GRADE 1"
            }
        }
    
    output = """## Recommandations générales - Antibioprophylaxie

### Timing d'administration (GRADE 1)
Administration au plus tôt 60 min avant, au plus tard avant l'incision chirurgicale.

Pour la vancomycine: début perfusion 60-30 min avant incision (durée 60 min).

### Réinjection peropératoire (GRADE 2)
Réadministrer en cas de chirurgie prolongée, toutes les 2 demi-vies:

| Antibiotique | Intervalle | Dose |
|--------------|------------|------|
| Céfoxitine | 2h | 1g |
| Céfuroxime | 2h | 0.75g |
| Amoxicilline/clavulanate | 2h | 1g |
| Céfazoline | 4h | 1g |
| Clindamycine | 4h | 450mg |
| Vancomycine | 8h | 10mg/kg |

*Gentamicine, métronidazole, teicoplanine: pas de réinjection (demi-vie longue)*

### Durée (GRADE 1)
Pas de prolongation au-delà de la fin de chirurgie (sauf exceptions spécifiques).
"""
    
    return [TextContent(type="text", text=output)]


async def main():
    """Point d'entrée principal."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
