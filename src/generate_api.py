#!/usr/bin/env python3
"""
Script de génération d'une API statique JSON à partir des données structurées.
Ce script crée une structure d'API REST-like avec des endpoints statiques
déployables sur GitHub Pages.
"""

import json
import os
import unicodedata
from pathlib import Path
from typing import Any, Dict, List


def slugify(text: str) -> str:
    """
    Convertit un texte en slug URL-friendly.
    Gère les accents français et autres caractères spéciaux.
    
    Args:
        text: Le texte à convertir en slug
        
    Returns:
        Le slug URL-friendly
        
    Examples:
        >>> slugify("Chirurgie orthopédique")
        'chirurgie-orthopedique'
        >>> slugify("Œsophage et estomac")
        'oesophage-et-estomac'
    """
    # Normaliser les caractères Unicode (NFD = décomposition)
    text = unicodedata.normalize('NFD', text)
    # Supprimer les accents
    text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')
    # Convertir en minuscules
    text = text.lower()
    # Remplacer les espaces et caractères spéciaux par des tirets
    text = ''.join(char if char.isalnum() else '-' for char in text)
    # Supprimer les tirets multiples et les tirets en début/fin
    text = '-'.join(filter(None, text.split('-')))
    return text


def get_base_url() -> str:
    """
    Retourne l'URL de base de l'API.
    Utilise une variable d'environnement ou une valeur par défaut pour GitHub Pages.
    """
    return os.getenv(
        'API_BASE_URL',
        'https://tomboulier.github.io/sfar-rfe-antibioprophylaxie-mcp'
    )


def generate_hateoas_links(endpoint: str, additional_links: Dict[str, str] = None) -> Dict[str, Any]:
    """
    Génère les liens HATEOAS pour un endpoint donné.
    
    Args:
        endpoint: Le chemin de l'endpoint actuel (ex: "specialites.json")
        additional_links: Liens additionnels spécifiques à l'endpoint
        
    Returns:
        Dictionnaire de liens HATEOAS
    """
    base_url = get_base_url()
    links = {
        "self": f"{base_url}/api/v1/{endpoint}",
        "home": f"{base_url}/",
        "recommandations": f"{base_url}/api/v1/recommandations.json",
        "specialites": f"{base_url}/api/v1/specialites.json",
        "generales": f"{base_url}/api/v1/generales.json",
        "search": f"{base_url}/api/v1/search-index.json"
    }
    
    if additional_links:
        links.update(additional_links)
    
    return links


def generate_recommandations_endpoint(data: Dict[str, Any], output_dir: Path) -> None:
    """
    Génère l'endpoint recommandations.json avec toutes les données et métadonnées.
    """
    endpoint_data = {
        "metadata": data["metadata"],
        "recommandations": data["data"],
        "recommandations_generales": data["recommandations_generales"],
        "_links": generate_hateoas_links("recommandations.json")
    }
    
    output_file = output_dir / "recommandations.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(endpoint_data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Généré: {output_file}")


def generate_specialites_endpoint(data: Dict[str, Any], output_dir: Path) -> None:
    """
    Génère l'endpoint specialites.json avec la liste des spécialités.
    """
    specialites_list = []
    
    for specialite_name in data["metadata"]["specialites"]:
        slug = slugify(specialite_name)
        # Compter le nombre de recommandations pour cette spécialité
        count = len([
            rec for rec in data["data"]
            if rec["specialite"] == specialite_name
        ])
        
        specialites_list.append({
            "nom": specialite_name,
            "slug": slug,
            "count": count,
            "url": f"{get_base_url()}/api/v1/specialite/{slug}.json"
        })
    
    endpoint_data = {
        "specialites": specialites_list,
        "total": len(specialites_list),
        "_links": generate_hateoas_links("specialites.json")
    }
    
    output_file = output_dir / "specialites.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(endpoint_data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Généré: {output_file}")


def generate_specialite_endpoints(data: Dict[str, Any], output_dir: Path) -> None:
    """
    Génère les endpoints par spécialité (specialite/{slug}.json).
    """
    specialite_dir = output_dir / "specialite"
    specialite_dir.mkdir(parents=True, exist_ok=True)
    
    for specialite_name in data["metadata"]["specialites"]:
        slug = slugify(specialite_name)
        
        # Filtrer les recommandations pour cette spécialité
        recommandations = [
            rec for rec in data["data"]
            if rec["specialite"] == specialite_name
        ]
        
        endpoint_data = {
            "specialite": {
                "nom": specialite_name,
                "slug": slug
            },
            "recommandations": recommandations,
            "total": len(recommandations),
            "_links": generate_hateoas_links(
                f"specialite/{slug}.json",
                {"specialites_list": f"{get_base_url()}/api/v1/specialites.json"}
            )
        }
        
        output_file = specialite_dir / f"{slug}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(endpoint_data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Généré: {output_file}")


def generate_generales_endpoint(data: Dict[str, Any], output_dir: Path) -> None:
    """
    Génère l'endpoint generales.json avec les recommandations générales.
    """
    endpoint_data = {
        "recommandations_generales": data["recommandations_generales"],
        "metadata": {
            "source": data["metadata"]["source"],
            "version": data["metadata"]["version"]
        },
        "_links": generate_hateoas_links("generales.json")
    }
    
    output_file = output_dir / "generales.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(endpoint_data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Généré: {output_file}")


def generate_search_index(data: Dict[str, Any], output_dir: Path) -> None:
    """
    Génère l'index de recherche pour faciliter les recherches côté client.
    """
    search_entries = []
    
    for idx, rec in enumerate(data["data"]):
        entry = {
            "id": idx,
            "specialite": rec["specialite"],
            "specialite_slug": slugify(rec["specialite"]),
            "acte": rec["acte"],
            "antibiotique": rec["antibiotique"],
            "posologie": rec["posologie"],
            "grade": rec["grade"],
            "searchable_text": f"{rec['specialite']} {rec['acte']} {rec['antibiotique']}".lower()
        }
        search_entries.append(entry)
    
    endpoint_data = {
        "index": search_entries,
        "total": len(search_entries),
        "fields": ["specialite", "acte", "antibiotique", "posologie", "grade"],
        "_links": generate_hateoas_links("search-index.json")
    }
    
    output_file = output_dir / "search-index.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(endpoint_data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Généré: {output_file}")


def generate_index_html(data: Dict[str, Any], output_dir: Path) -> None:
    """
    Génère la page index.html avec la documentation de l'API.
    """
    base_url = get_base_url()
    metadata = data["metadata"]
    
    # Liste des endpoints
    endpoints = [
        {
            "path": "/api/v1/recommandations.json",
            "description": "Toutes les recommandations avec métadonnées",
            "example_field": "recommandations"
        },
        {
            "path": "/api/v1/specialites.json",
            "description": "Liste des spécialités avec leur slug et count",
            "example_field": "specialites"
        },
        {
            "path": "/api/v1/generales.json",
            "description": "Recommandations générales (timing, réinjection, durée)",
            "example_field": "recommandations_generales"
        },
        {
            "path": "/api/v1/search-index.json",
            "description": "Index de recherche pour faciliter les recherches",
            "example_field": "index"
        }
    ]
    
    # Ajouter les endpoints par spécialité
    for specialite_name in metadata["specialites"]:
        slug = slugify(specialite_name)
        endpoints.append({
            "path": f"/api/v1/specialite/{slug}.json",
            "description": f"Recommandations pour {specialite_name}",
            "example_field": "recommandations"
        })
    
    endpoints_html = "\n".join([
        f"""
        <tr>
          <td><code>{ep['path']}</code></td>
          <td>{ep['description']}</td>
          <td><a href="{base_url}{ep['path']}" target="_blank">Voir JSON</a></td>
        </tr>
        """
        for ep in endpoints
    ])
    
    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Antibioprophylaxie SFAR - Documentation</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 3rem 2rem;
            text-align: center;
        }}
        
        header h1 {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }}
        
        header p {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 3rem 2rem;
        }}
        
        .section {{
            margin-bottom: 3rem;
        }}
        
        h2 {{
            color: #667eea;
            font-size: 1.8rem;
            margin-bottom: 1rem;
            border-bottom: 3px solid #667eea;
            padding-bottom: 0.5rem;
        }}
        
        h3 {{
            color: #764ba2;
            font-size: 1.4rem;
            margin: 1.5rem 0 1rem;
        }}
        
        .metadata {{
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        
        .metadata-item {{
            display: flex;
            margin-bottom: 0.75rem;
        }}
        
        .metadata-label {{
            font-weight: bold;
            min-width: 140px;
            color: #667eea;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
            background: white;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
            overflow: hidden;
        }}
        
        thead {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        th, td {{
            padding: 1rem;
            text-align: left;
        }}
        
        tbody tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        
        tbody tr:hover {{
            background: #e9ecef;
        }}
        
        code {{
            background: #f4f4f4;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            color: #d63384;
        }}
        
        pre {{
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 8px;
            overflow-x: auto;
            border-left: 4px solid #764ba2;
        }}
        
        pre code {{
            background: none;
            padding: 0;
            color: #333;
        }}
        
        a {{
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }}
        
        a:hover {{
            color: #764ba2;
            text-decoration: underline;
        }}
        
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.875rem;
            font-weight: 500;
            margin-left: 0.5rem;
        }}
        
        .badge-info {{
            background: #d1ecf1;
            color: #0c5460;
        }}
        
        .badge-success {{
            background: #d4edda;
            color: #155724;
        }}
        
        footer {{
            background: #f8f9fa;
            padding: 2rem;
            text-align: center;
            color: #666;
            border-top: 1px solid #dee2e6;
        }}
        
        @media (max-width: 768px) {{
            body {{
                padding: 1rem;
            }}
            
            header h1 {{
                font-size: 2rem;
            }}
            
            .content {{
                padding: 2rem 1rem;
            }}
            
            table {{
                font-size: 0.9rem;
            }}
            
            th, td {{
                padding: 0.75rem 0.5rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏥 API Antibioprophylaxie SFAR</h1>
            <p>API statique REST-like pour les recommandations d'antibioprophylaxie</p>
        </header>
        
        <div class="content">
            <section class="section">
                <h2>📋 Métadonnées</h2>
                <div class="metadata">
                    <div class="metadata-item">
                        <span class="metadata-label">Source:</span>
                        <span>{metadata['source']}</span>
                    </div>
                    <div class="metadata-item">
                        <span class="metadata-label">Version:</span>
                        <span>{metadata['version']}</span>
                    </div>
                    <div class="metadata-item">
                        <span class="metadata-label">Total records:</span>
                        <span class="badge badge-info">{metadata['total_records']}</span>
                    </div>
                    <div class="metadata-item">
                        <span class="metadata-label">Date extraction:</span>
                        <span>{metadata['date_extraction']}</span>
                    </div>
                    <div class="metadata-item">
                        <span class="metadata-label">Spécialités:</span>
                        <span>{', '.join(metadata['specialites'])}</span>
                    </div>
                    <div class="metadata-item">
                        <span class="metadata-label">Source URL:</span>
                        <span><a href="{metadata['url_source']}" target="_blank">Documentation SFAR</a></span>
                    </div>
                </div>
            </section>
            
            <section class="section">
                <h2>🔗 Endpoints disponibles</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Endpoint</th>
                            <th>Description</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {endpoints_html}
                    </tbody>
                </table>
            </section>
            
            <section class="section">
                <h2>💻 Exemple d'utilisation</h2>
                <h3>Avec JavaScript (Fetch API)</h3>
                <pre><code>// Récupérer toutes les recommandations
fetch('{base_url}/api/v1/recommandations.json')
  .then(response => response.json())
  .then(data => {{
    console.log('Métadonnées:', data.metadata);
    console.log('Recommandations:', data.recommandations);
    console.log('Liens:', data._links);
  }})
  .catch(error => console.error('Erreur:', error));

// Récupérer les spécialités
fetch('{base_url}/api/v1/specialites.json')
  .then(response => response.json())
  .then(data => {{
    data.specialites.forEach(spec => {{
      console.log(`${{spec.nom}} (${{spec.count}} recommandations)`);
      console.log(`URL: ${{spec.url}}`);
    }});
  }});

// Récupérer une spécialité spécifique
fetch('{base_url}/api/v1/specialite/chirurgie-orthopedique.json')
  .then(response => response.json())
  .then(data => {{
    console.log('Spécialité:', data.specialite.nom);
    console.log('Recommandations:', data.recommandations);
  }});
</code></pre>
                
                <h3>Avec cURL</h3>
                <pre><code># Récupérer toutes les recommandations
curl {base_url}/api/v1/recommandations.json

# Récupérer les spécialités
curl {base_url}/api/v1/specialites.json

# Récupérer une spécialité spécifique
curl {base_url}/api/v1/specialite/chirurgie-orthopedique.json
</code></pre>
            </section>
            
            <section class="section">
                <h2>🔍 Structure des réponses</h2>
                <h3>HATEOAS Links</h3>
                <p>Tous les endpoints incluent un objet <code>_links</code> avec des liens hypermedia pour faciliter la navigation dans l'API:</p>
                <pre><code>{{
  "_links": {{
    "self": "URL de l'endpoint actuel",
    "home": "URL de la page d'accueil",
    "recommandations": "URL des recommandations",
    "specialites": "URL des spécialités",
    "generales": "URL des recommandations générales",
    "search": "URL de l'index de recherche"
  }}
}}</code></pre>
                
                <h3>Format des données</h3>
                <p>Les données sont encodées en UTF-8 avec support complet des caractères français (accents, cédilles, etc.).</p>
            </section>
            
            <section class="section">
                <h2>📝 Notes techniques</h2>
                <ul style="list-style-position: inside; line-height: 2;">
                    <li>API statique générée automatiquement via GitHub Actions</li>
                    <li>Hébergée sur GitHub Pages</li>
                    <li>CORS activé (accessible depuis n'importe quel domaine)</li>
                    <li>Format JSON avec encodage UTF-8</li>
                    <li>Support des liens HATEOAS pour la navigation</li>
                    <li>Index de recherche pour faciliter les recherches côté client</li>
                </ul>
            </section>
        </div>
        
        <footer>
            <p>Généré automatiquement depuis <a href="https://github.com/tomboulier/sfar-rfe-antibioprophylaxie-mcp" target="_blank">sfar-rfe-antibioprophylaxie-mcp</a></p>
            <p style="margin-top: 0.5rem; color: #999;">Données basées sur les recommandations SFAR RFE Antibioprophylaxie 2024</p>
        </footer>
    </div>
</body>
</html>
"""
    
    output_file = output_dir.parent.parent / "index.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ Généré: {output_file}")


def main():
    """
    Point d'entrée principal du script.
    """
    print("🚀 Génération de l'API statique...")
    print()
    
    # Chemins
    base_dir = Path(__file__).parent.parent
    data_file = base_dir / "data" / "exemple_structure.json"
    output_dir = base_dir / "public" / "api" / "v1"
    
    # Créer le dossier de sortie
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Lire les données source
    print(f"📖 Lecture de {data_file}")
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"   - {data['metadata']['total_records']} recommandations")
    print(f"   - {len(data['metadata']['specialites'])} spécialités")
    print()
    
    # Générer les endpoints
    print("📝 Génération des endpoints JSON...")
    generate_recommandations_endpoint(data, output_dir)
    generate_specialites_endpoint(data, output_dir)
    generate_specialite_endpoints(data, output_dir)
    generate_generales_endpoint(data, output_dir)
    generate_search_index(data, output_dir)
    print()
    
    # Générer la page HTML
    print("🌐 Génération de la documentation HTML...")
    generate_index_html(data, output_dir)
    print()
    
    print("✅ Génération terminée avec succès!")
    print(f"📁 Fichiers générés dans: {output_dir.parent.parent}")


if __name__ == "__main__":
    main()
