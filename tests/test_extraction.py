"""
Tests unitaires pour l'extraction des RFE Antibioprophylaxie.
"""

import json
from pathlib import Path

import pytest


DATA_DIR = Path(__file__).parent.parent / "data"


class TestDataStructure:
    """Tests sur la structure des données JSON."""
    
    def test_exemple_structure_exists(self):
        """Vérifie que le fichier exemple existe."""
        exemple_path = DATA_DIR / "exemple_structure.json"
        assert exemple_path.exists(), "Le fichier exemple_structure.json doit exister"
    
    def test_exemple_structure_valid_json(self):
        """Vérifie que le fichier exemple est un JSON valide."""
        exemple_path = DATA_DIR / "exemple_structure.json"
        with open(exemple_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert isinstance(data, dict)
    
    def test_exemple_has_required_fields(self):
        """Vérifie que le fichier exemple contient les champs requis."""
        exemple_path = DATA_DIR / "exemple_structure.json"
        with open(exemple_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Champs de premier niveau
        assert "metadata" in data
        assert "data" in data
        
        # Métadonnées
        assert "source" in data["metadata"]
        assert "version" in data["metadata"]
    
    def test_data_records_have_required_fields(self):
        """Vérifie que chaque enregistrement a les champs requis."""
        exemple_path = DATA_DIR / "exemple_structure.json"
        with open(exemple_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        required_fields = ["specialite", "acte", "antibiotique", "posologie"]
        
        for i, record in enumerate(data["data"]):
            for field in required_fields:
                assert field in record, f"Record {i} manque le champ '{field}'"


class TestAntibioprophylaxieData:
    """Tests sur la cohérence des données d'antibioprophylaxie."""
    
    def test_posologie_format(self):
        """Vérifie que les posologies sont au bon format."""
        exemple_path = DATA_DIR / "exemple_structure.json"
        with open(exemple_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for record in data["data"]:
            poso = record.get("posologie", "")
            if poso and poso != "-":
                # Doit contenir une unité (g, mg, mg/kg)
                assert any(unit in poso.lower() for unit in ["g", "mg"]), \
                    f"Posologie '{poso}' sans unité valide"
    
    def test_grade_values(self):
        """Vérifie que les grades sont valides."""
        exemple_path = DATA_DIR / "exemple_structure.json"
        with open(exemple_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        valid_grades = ["GRADE 1", "GRADE 2", "Avis d'experts", None]
        
        for record in data["data"]:
            grade = record.get("grade")
            assert grade in valid_grades, f"Grade invalide: {grade}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
