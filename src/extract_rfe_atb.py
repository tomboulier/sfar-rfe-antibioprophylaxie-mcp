#!/usr/bin/env python3
"""
Extracteur de données structurées des RFE Antibioprophylaxie SFAR.

Ce script extrait les tableaux d'antibioprophylaxie du PDF SFAR
et les convertit en JSON structuré pour une utilisation via API/MCP.

Usage:
    python extract_rfe_atb.py input.pdf output.json

Dépendances:
    pip install pdfplumber pandas

Auteur: Groupe Numérique SFAR
Version: 1.0.0
"""

import json
import re
import sys
from dataclasses import dataclass, asdict
from typing import Optional
from pathlib import Path

import pdfplumber
import pandas as pd


@dataclass
class Antibioprophylaxie:
    """Représentation d'une ligne d'antibioprophylaxie."""
    
    specialite: str
    acte: str
    antibiotique: str
    posologie: str
    alternative_allergie: Optional[str]
    reinjection: Optional[str]
    duree: Optional[str]
    grade: Optional[str]
    commentaire: Optional[str] = None


def normalize_text(text: str) -> str:
    """Normalise le texte extrait du PDF."""
    if not text:
        return ""
    # Supprime les retours à la ligne multiples
    text = re.sub(r'\s+', ' ', text)
    # Supprime les espaces en début/fin
    return text.strip()


def extract_tables_from_pdf(pdf_path: str) -> list[pd.DataFrame]:
    """
    Extrait tous les tableaux du PDF.
    
    Args:
        pdf_path: Chemin vers le fichier PDF
        
    Returns:
        Liste de DataFrames contenant les tableaux extraits
    """
    tables = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            page_tables = page.extract_tables()
            
            for table in page_tables:
                if table and len(table) > 1:  # Au moins une ligne de données
                    # Nettoie les cellules
                    cleaned = [
                        [normalize_text(cell) if cell else "" for cell in row]
                        for row in table
                    ]
                    
                    # Crée le DataFrame
                    df = pd.DataFrame(cleaned[1:], columns=cleaned[0])
                    df['_page'] = page_num + 1
                    tables.append(df)
    
    return tables


def identify_specialty(df: pd.DataFrame, page_num: int) -> str:
    """
    Identifie la spécialité chirurgicale basée sur les en-têtes du tableau.
    
    Args:
        df: DataFrame du tableau
        page_num: Numéro de page
        
    Returns:
        Nom de la spécialité
    """
    # Mapping approximatif page -> spécialité (à ajuster selon le PDF réel)
    specialty_pages = {
        (30, 40): "Neurochirurgie",
        (41, 45): "ORL",
        (46, 50): "Ophtalmologie",
        (51, 55): "Chirurgie maxillo-faciale",
        (56, 60): "Chirurgie cardiaque",
        (61, 65): "Chirurgie vasculaire",
        (66, 70): "Chirurgie thoracique",
        (71, 75): "Chirurgie plastique",
        (76, 80): "Chirurgie gynécologique",
        (81, 85): "Obstétrique",
        (86, 90): "Chirurgie orthopédique",
        (91, 95): "Traumatologie",
        (96, 100): "Chirurgie digestive",
        (101, 105): "Chirurgie urologique",
    }
    
    for (start, end), specialty in specialty_pages.items():
        if start <= page_num <= end:
            return specialty
    
    return "Non classé"


def parse_table_to_records(
    df: pd.DataFrame, 
    specialty: str
) -> list[Antibioprophylaxie]:
    """
    Parse un DataFrame en liste d'enregistrements structurés.
    
    Args:
        df: DataFrame du tableau
        specialty: Spécialité chirurgicale
        
    Returns:
        Liste d'objets Antibioprophylaxie
    """
    records = []
    
    # Mapping des colonnes (à adapter selon le PDF réel)
    column_mapping = {
        'acte': ['Acte', 'Intervention', 'Type de chirurgie', 'Procédure'],
        'antibiotique': ['Antibiotique', 'ATB', 'Molécule'],
        'posologie': ['Posologie', 'Dose', 'Schéma'],
        'alternative': ['Alternative', 'Si allergie', 'Allergie β-lactamines'],
        'reinjection': ['Réinjection', 'Ré-injection', 'Dose supplémentaire'],
        'duree': ['Durée', 'Durée totale'],
        'grade': ['Grade', 'Niveau de preuve', 'Recommandation'],
    }
    
    def find_column(df: pd.DataFrame, aliases: list[str]) -> Optional[str]:
        """Trouve le nom de colonne correspondant aux alias."""
        for alias in aliases:
            for col in df.columns:
                if alias.lower() in col.lower():
                    return col
        return None
    
    # Identifie les colonnes
    col_acte = find_column(df, column_mapping['acte'])
    col_atb = find_column(df, column_mapping['antibiotique'])
    col_poso = find_column(df, column_mapping['posologie'])
    col_alt = find_column(df, column_mapping['alternative'])
    col_reinj = find_column(df, column_mapping['reinjection'])
    col_duree = find_column(df, column_mapping['duree'])
    col_grade = find_column(df, column_mapping['grade'])
    
    for _, row in df.iterrows():
        try:
            record = Antibioprophylaxie(
                specialite=specialty,
                acte=row.get(col_acte, "") if col_acte else "",
                antibiotique=row.get(col_atb, "") if col_atb else "",
                posologie=row.get(col_poso, "") if col_poso else "",
                alternative_allergie=row.get(col_alt) if col_alt else None,
                reinjection=row.get(col_reinj) if col_reinj else None,
                duree=row.get(col_duree) if col_duree else None,
                grade=row.get(col_grade) if col_grade else None,
            )
            
            # Ne garde que les lignes avec des données significatives
            if record.acte and record.antibiotique:
                records.append(record)
                
        except Exception as e:
            print(f"Erreur parsing ligne: {e}", file=sys.stderr)
            continue
    
    return records


def extract_rfe_data(pdf_path: str) -> dict:
    """
    Fonction principale d'extraction.
    
    Args:
        pdf_path: Chemin vers le PDF
        
    Returns:
        Dictionnaire structuré avec métadonnées et données
    """
    tables = extract_tables_from_pdf(pdf_path)
    
    all_records = []
    specialties = set()
    
    for df in tables:
        page_num = df['_page'].iloc[0] if '_page' in df.columns else 0
        specialty = identify_specialty(df, page_num)
        specialties.add(specialty)
        
        records = parse_table_to_records(df, specialty)
        all_records.extend(records)
    
    # Structure finale
    output = {
        "metadata": {
            "source": "SFAR - RFE Antibioprophylaxie 2024",
            "version": "2.0",
            "date_extraction": pd.Timestamp.now().isoformat(),
            "total_records": len(all_records),
            "specialites": sorted(list(specialties)),
        },
        "data": [asdict(r) for r in all_records]
    }
    
    return output


def main():
    """Point d'entrée CLI."""
    if len(sys.argv) < 3:
        print("Usage: python extract_rfe_atb.py <input.pdf> <output.json>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_path = sys.argv[2]
    
    if not Path(pdf_path).exists():
        print(f"Erreur: fichier {pdf_path} introuvable")
        sys.exit(1)
    
    print(f"Extraction de {pdf_path}...")
    data = extract_rfe_data(pdf_path)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ {data['metadata']['total_records']} enregistrements extraits")
    print(f"✓ Spécialités: {', '.join(data['metadata']['specialites'])}")
    print(f"✓ Sauvegardé dans {output_path}")


if __name__ == "__main__":
    main()
