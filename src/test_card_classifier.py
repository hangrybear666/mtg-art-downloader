"""
CARD CLASSIFIER TEST SUITE

Comprehensive tests for the card classification system, covering:
- Type precedence rules
- Color identity classification
- Edge cases and multi-type cards
- Integration with existing Card classes
"""

import os
import sys
from pathlib import Path

# Add cwd to path (following existing test pattern)
sys.path.append(str(Path(os.getcwd())))
os.chdir(str(Path(os.getcwd()).resolve()))

import pytest
from src.card_classifier import CardClassifier, get_classified_folder_path


class TestTypePrecedence:
    """Test the type precedence system: Token > Land > Planeswalker > Enchantment > Artifact"""

    def test_token_precedence_over_all(self):
        """Token should take precedence over all other types"""
        # Token Artifact Enchantment Land (all types combined)
        card = {
            "name": "Test Card",
            "type_line": "Token Artifact Enchantment Land",
            "color_identity": ["W"],
        }
        classifier = CardClassifier(card)
        assert classifier.get_primary_type() == "Token"
        assert classifier.get_classified_folder_path() == "Token/White/"

    def test_land_precedence_over_enchantment_artifact(self):
        """Land should take precedence over Enchantment and Artifact"""
        card = {
            "name": "Artifact Land",
            "type_line": "Artifact Land",
            "color_identity": [],
        }
        classifier = CardClassifier(card)
        assert classifier.get_primary_type() == "Land"
        assert classifier.get_classified_folder_path() == "Land/"

        # Enchantment Land
        card["type_line"] = "Enchantment Land"
        classifier = CardClassifier(card)
        assert classifier.get_primary_type() == "Land"
        assert classifier.get_classified_folder_path() == "Land/"

    def test_enchantment_precedence_over_artifact(self):
        """Enchantment should take precedence over Artifact"""
        card = {
            "name": "Artifact Enchantment",
            "type_line": "Legendary Artifact Enchantment",
            "color_identity": ["U", "B"],
        }
        classifier = CardClassifier(card)
        assert classifier.get_primary_type() == "Enchantment"
        assert classifier.get_classified_folder_path() == "Enchantment/Multicolor/"

    def test_artifact_alone(self):
        """Artifact without higher precedence types"""
        card = {
            "name": "Artifact",
            "type_line": "Artifact — Equipment",
            "color_identity": [],
        }
        classifier = CardClassifier(card)
        assert classifier.get_primary_type() == "Artifact"
        assert classifier.get_classified_folder_path() == "Artifact/"

    def test_no_priority_type(self):
        """Cards without priority types go to root color folders"""
        # Creature
        card = {
            "name": "Creature",
            "type_line": "Creature — Human Wizard",
            "color_identity": ["R"],
        }
        classifier = CardClassifier(card)
        assert classifier.get_primary_type() is None
        assert classifier.get_classified_folder_path() == "Red/"

        # Sorcery
        card["type_line"] = "Sorcery"
        card["color_identity"] = ["G"]
        classifier = CardClassifier(card)
        assert classifier.get_primary_type() is None
        assert classifier.get_classified_folder_path() == "Green/"

        # Instant
        card["type_line"] = "Instant"
        card["color_identity"] = ["U"]
        classifier = CardClassifier(card)
        assert classifier.get_primary_type() is None
        assert classifier.get_classified_folder_path() == "Blue/"


class TestBasicLands:
    """Test Basic Land special handling"""

    def test_basic_land_folder(self):
        """Basic Lands should go to Basic/ folder"""
        card = {
            "name": "Forest",
            "type_line": "Basic Land — Forest",
            "color_identity": ["G"],
        }
        classifier = CardClassifier(card)
        assert classifier.is_basic_land() is True
        assert classifier.get_classified_folder_path() == "Basic/"

    def test_non_basic_land_folder(self):
        """Non-basic Lands should go to Land/ folder"""
        card = {
            "name": "Dual Land",
            "type_line": "Land",
            "color_identity": ["U", "B"],
        }
        classifier = CardClassifier(card)
        assert classifier.is_basic_land() is False
        assert classifier.get_classified_folder_path() == "Land/"


class TestColorIdentity:
    """Test color identity classification"""

    def test_monocolor_white(self):
        """White monocolor cards"""
        card = {
            "name": "White Card",
            "type_line": "Enchantment",
            "color_identity": ["W"],
        }
        classifier = CardClassifier(card)
        assert classifier.get_color_identity_folder() == "White"
        assert classifier.get_classified_folder_path() == "Enchantment/White/"

    def test_monocolor_blue(self):
        """Blue monocolor cards"""
        card = {
            "name": "Blue Card",
            "type_line": "Creature — Wizard",
            "color_identity": ["U"],
        }
        classifier = CardClassifier(card)
        assert classifier.get_color_identity_folder() == "Blue"
        assert classifier.get_classified_folder_path() == "Blue/"

    def test_monocolor_black(self):
        """Black monocolor cards"""
        card = {
            "name": "Black Card",
            "type_line": "Sorcery",
            "color_identity": ["B"],
        }
        classifier = CardClassifier(card)
        assert classifier.get_color_identity_folder() == "Black"
        assert classifier.get_classified_folder_path() == "Black/"

    def test_monocolor_red(self):
        """Red monocolor cards"""
        card = {
            "name": "Red Card",
            "type_line": "Instant",
            "color_identity": ["R"],
        }
        classifier = CardClassifier(card)
        assert classifier.get_color_identity_folder() == "Red"
        assert classifier.get_classified_folder_path() == "Red/"

    def test_monocolor_green(self):
        """Green monocolor cards"""
        card = {
            "name": "Green Card",
            "type_line": "Creature — Elf",
            "color_identity": ["G"],
        }
        classifier = CardClassifier(card)
        assert classifier.get_color_identity_folder() == "Green"
        assert classifier.get_classified_folder_path() == "Green/"

    def test_multicolor_two_colors(self):
        """Two-color cards should be Multicolor"""
        card = {
            "name": "Multicolor Card",
            "type_line": "Creature — Human Wizard",
            "color_identity": ["U", "R"],
        }
        classifier = CardClassifier(card)
        assert classifier.get_color_identity_folder() == "Multicolor"
        assert classifier.get_classified_folder_path() == "Multicolor/"

    def test_multicolor_three_colors(self):
        """Three-color cards should be Multicolor"""
        card = {
            "name": "Tricolor Card",
            "type_line": "Legendary Creature",
            "color_identity": ["W", "U", "B"],
        }
        classifier = CardClassifier(card)
        assert classifier.get_color_identity_folder() == "Multicolor"
        assert classifier.get_classified_folder_path() == "Multicolor/"

    def test_multicolor_five_colors(self):
        """Five-color cards should be Multicolor"""
        card = {
            "name": "Five Color Card",
            "type_line": "Creature — God",
            "color_identity": ["W", "U", "B", "R", "G"],
        }
        classifier = CardClassifier(card)
        assert classifier.get_color_identity_folder() == "Multicolor"
        assert classifier.get_classified_folder_path() == "Multicolor/"

    def test_colorless_empty_list(self):
        """Cards with empty color_identity array"""
        card = {
            "name": "Colorless Card",
            "type_line": "Artifact Creature",
            "color_identity": [],
        }
        classifier = CardClassifier(card)
        assert classifier.get_color_identity_folder() == "Colorless"
        assert classifier.get_classified_folder_path() == "Artifact/"

    def test_colorless_missing_field(self):
        """Cards without color_identity field"""
        card = {
            "name": "Missing Color Identity",
            "type_line": "Creature — Eldrazi",
        }
        classifier = CardClassifier(card)
        assert classifier.get_color_identity_folder() == "Colorless"
        assert classifier.get_classified_folder_path() == "Colorless/"


class TestTokens:
    """Test Token classification with all color identities"""

    def test_token_white(self):
        card = {
            "name": "White Token",
            "type_line": "Token Creature — Soldier",
            "color_identity": ["W"],
        }
        classifier = CardClassifier(card)
        assert classifier.get_classified_folder_path() == "Token/White/"

    def test_token_multicolor(self):
        card = {
            "name": "Multicolor Token",
            "type_line": "Token Artifact Creature",
            "color_identity": ["U", "R"],
        }
        classifier = CardClassifier(card)
        assert classifier.get_classified_folder_path() == "Token/Multicolor/"

    def test_token_colorless(self):
        card = {
            "name": "Colorless Token",
            "type_line": "Token Artifact",
            "color_identity": [],
        }
        classifier = CardClassifier(card)
        assert classifier.get_classified_folder_path() == "Token/Colorless/"


class TestEnchantments:
    """Test Enchantment classification with color identities"""

    def test_enchantment_white(self):
        card = {
            "name": "White Enchantment",
            "type_line": "Enchantment — Aura",
            "color_identity": ["W"],
        }
        classifier = CardClassifier(card)
        assert classifier.get_classified_folder_path() == "Enchantment/White/"

    def test_enchantment_creature(self):
        """Enchantment Creatures should use color subfolders"""
        card = {
            "name": "Enchantment Creature",
            "type_line": "Enchantment Creature — God",
            "color_identity": ["W", "U"],
        }
        classifier = CardClassifier(card)
        assert classifier.get_classified_folder_path() == "Enchantment/Multicolor/"

    def test_enchantment_colorless(self):
        card = {
            "name": "Colorless Enchantment",
            "type_line": "Enchantment",
            "color_identity": [],
        }
        classifier = CardClassifier(card)
        assert classifier.get_classified_folder_path() == "Enchantment/Colorless/"


class TestPlaneswalkers:
    """Test Planeswalker classification with all color identities"""

    def test_planeswalker_white(self):
        """White Planeswalkers (e.g., Gideon)"""
        card = {
            "name": "Gideon, Ally of Zendikar",
            "type_line": "Legendary Planeswalker — Gideon",
            "color_identity": ["W"],
        }
        classifier = CardClassifier(card)
        assert classifier.get_primary_type() == "Planeswalker"
        assert classifier.get_classified_folder_path() == "Planeswalker/White/"

    def test_planeswalker_blue(self):
        """Blue Planeswalkers (e.g., Jace)"""
        card = {
            "name": "Jace, the Mind Sculptor",
            "type_line": "Legendary Planeswalker — Jace",
            "color_identity": ["U"],
        }
        classifier = CardClassifier(card)
        assert classifier.get_primary_type() == "Planeswalker"
        assert classifier.get_classified_folder_path() == "Planeswalker/Blue/"

    def test_planeswalker_black(self):
        """Black Planeswalkers (e.g., Liliana)"""
        card = {
            "name": "Liliana of the Veil",
            "type_line": "Legendary Planeswalker — Liliana",
            "color_identity": ["B"],
        }
        classifier = CardClassifier(card)
        assert classifier.get_primary_type() == "Planeswalker"
        assert classifier.get_classified_folder_path() == "Planeswalker/Black/"

    def test_planeswalker_red(self):
        """Red Planeswalkers (e.g., Chandra)"""
        card = {
            "name": "Chandra, Torch of Defiance",
            "type_line": "Legendary Planeswalker — Chandra",
            "color_identity": ["R"],
        }
        classifier = CardClassifier(card)
        assert classifier.get_primary_type() == "Planeswalker"
        assert classifier.get_classified_folder_path() == "Planeswalker/Red/"

    def test_planeswalker_green(self):
        """Green Planeswalkers (e.g., Nissa, Garruk)"""
        card = {
            "name": "Nissa, Who Shakes the World",
            "type_line": "Legendary Planeswalker — Nissa",
            "color_identity": ["G"],
        }
        classifier = CardClassifier(card)
        assert classifier.get_primary_type() == "Planeswalker"
        assert classifier.get_classified_folder_path() == "Planeswalker/Green/"

    def test_planeswalker_multicolor(self):
        """Multicolor Planeswalkers (e.g., Wrenn and Six, Dack Fayden)"""
        card = {
            "name": "Wrenn and Six",
            "type_line": "Legendary Planeswalker — Wrenn",
            "color_identity": ["R", "G"],
        }
        classifier = CardClassifier(card)
        assert classifier.get_primary_type() == "Planeswalker"
        assert classifier.get_classified_folder_path() == "Planeswalker/Multicolor/"

    def test_planeswalker_colorless(self):
        """Colorless Planeswalkers (e.g., Ugin, Karn)"""
        card = {
            "name": "Ugin, the Spirit Dragon",
            "type_line": "Legendary Planeswalker — Ugin",
            "color_identity": [],
        }
        classifier = CardClassifier(card)
        assert classifier.get_primary_type() == "Planeswalker"
        assert classifier.get_classified_folder_path() == "Planeswalker/Colorless/"

    def test_planeswalker_precedence_over_enchantment(self):
        """Planeswalker takes precedence over Enchantment (hypothetical card)"""
        card = {
            "name": "Enchantment Planeswalker",
            "type_line": "Legendary Enchantment Planeswalker",
            "color_identity": ["G"],
        }
        classifier = CardClassifier(card)
        assert classifier.get_primary_type() == "Planeswalker"
        assert classifier.get_classified_folder_path() == "Planeswalker/Green/"

    def test_land_precedence_over_planeswalker(self):
        """Land takes precedence over Planeswalker (hypothetical card)"""
        card = {
            "name": "Planeswalker Land",
            "type_line": "Legendary Land Planeswalker",
            "color_identity": ["W"],
        }
        classifier = CardClassifier(card)
        # Land takes precedence over Planeswalker
        assert classifier.get_primary_type() == "Land"
        assert classifier.get_classified_folder_path() == "Land/"


class TestEdgeCases:
    """Test edge cases and unusual scenarios"""

    def test_missing_type_line(self):
        """Cards without type_line should default to root color folder"""
        card = {
            "name": "Missing Type",
            "color_identity": ["B"],
        }
        classifier = CardClassifier(card)
        assert classifier.get_primary_type() is None
        assert classifier.get_classified_folder_path() == "Black/"

    def test_empty_type_line(self):
        """Empty type_line should default to root color folder"""
        card = {
            "name": "Empty Type",
            "type_line": "",
            "color_identity": ["G"],
        }
        classifier = CardClassifier(card)
        assert classifier.get_primary_type() is None
        assert classifier.get_classified_folder_path() == "Green/"

    def test_whitespace_in_type_line(self):
        """Type_line with extra whitespace should be normalized"""
        card = {
            "name": "Whitespace Card",
            "type_line": "  Enchantment   Artifact  ",
            "color_identity": ["R"],
        }
        classifier = CardClassifier(card)
        assert classifier.get_primary_type() == "Enchantment"
        assert classifier.get_classified_folder_path() == "Enchantment/Red/"

    def test_dual_faced_card_type_line(self):
        """Dual-faced cards should use front face type_line"""
        card = {
            "name": "Front // Back",
            "card_faces": [
                {
                    "name": "Front",
                    "type_line": "Enchantment",
                },
                {
                    "name": "Back",
                    "type_line": "Land",
                },
            ],
            "color_identity": ["W"],
        }
        classifier = CardClassifier(card)
        # Should classify based on front face (Enchantment)
        assert classifier.get_primary_type() == "Enchantment"
        assert classifier.get_classified_folder_path() == "Enchantment/White/"

    def test_planeswalker(self):
        """Planeswalkers should go to Planeswalker/{color} folders"""
        card = {
            "name": "Jace",
            "type_line": "Legendary Planeswalker — Jace",
            "color_identity": ["U"],
        }
        classifier = CardClassifier(card)
        assert classifier.get_primary_type() == "Planeswalker"
        assert classifier.get_classified_folder_path() == "Planeswalker/Blue/"

    def test_saga(self):
        """Sagas are Enchantments and should use color subfolders"""
        card = {
            "name": "Saga Card",
            "type_line": "Enchantment — Saga",
            "color_identity": ["G"],
        }
        classifier = CardClassifier(card)
        assert classifier.get_primary_type() == "Enchantment"
        assert classifier.get_classified_folder_path() == "Enchantment/Green/"

    def test_case_sensitivity(self):
        """Type checking should be case-sensitive (as Scryfall uses title case)"""
        # Scryfall always uses title case for types
        card = {
            "name": "Test",
            "type_line": "enchantment",  # lowercase (should still match)
            "color_identity": ["B"],
        }
        classifier = CardClassifier(card)
        # Current implementation is case-sensitive - "enchantment" won't match "Enchantment"
        # This is correct as Scryfall always returns title case
        assert classifier.get_primary_type() is None

    def test_convenience_function(self):
        """Test the convenience function get_classified_folder_path"""
        card = {
            "name": "Test",
            "type_line": "Artifact",
            "color_identity": [],
        }
        path = get_classified_folder_path(card)
        assert path == "Artifact/"


class TestComplexRealWorldCards:
    """Test real-world complex card scenarios"""

    def test_theros_gods(self):
        """Theros Gods are Enchantment Creatures"""
        card = {
            "name": "Thassa, God of the Sea",
            "type_line": "Legendary Enchantment Creature — God",
            "color_identity": ["U"],
        }
        classifier = CardClassifier(card)
        assert classifier.get_classified_folder_path() == "Enchantment/Blue/"

    def test_urza_saga(self):
        """Urza's Saga is an Enchantment Land"""
        card = {
            "name": "Urza's Saga",
            "type_line": "Enchantment Land — Saga",
            "color_identity": [],
        }
        classifier = CardClassifier(card)
        # Land takes precedence over Enchantment
        assert classifier.get_primary_type() == "Land"
        assert classifier.get_classified_folder_path() == "Land/"

    def test_dryad_arbor(self):
        """Dryad Arbor is a Land Creature"""
        card = {
            "name": "Dryad Arbor",
            "type_line": "Land Creature — Forest Dryad",
            "color_identity": ["G"],
        }
        classifier = CardClassifier(card)
        # Land takes precedence
        assert classifier.get_primary_type() == "Land"
        assert classifier.get_classified_folder_path() == "Land/"

    def test_mishra_bauble(self):
        """Artifact without color identity"""
        card = {
            "name": "Mishra's Bauble",
            "type_line": "Artifact",
            "color_identity": [],
        }
        classifier = CardClassifier(card)
        assert classifier.get_classified_folder_path() == "Artifact/"

    def test_gingerbrute(self):
        """Artifact Creature should be Artifact folder (no color subfolders)"""
        card = {
            "name": "Gingerbrute",
            "type_line": "Artifact Creature — Food Golem",
            "color_identity": [],
        }
        classifier = CardClassifier(card)
        assert classifier.get_classified_folder_path() == "Artifact/"

    def test_esika_god_pharaoh(self):
        """MDFC with different types on each face"""
        card = {
            "name": "Esika, God of the Tree // The Prismatic Bridge",
            "card_faces": [
                {
                    "name": "Esika, God of the Tree",
                    "type_line": "Legendary Creature — God",
                },
                {
                    "name": "The Prismatic Bridge",
                    "type_line": "Legendary Enchantment",
                },
            ],
            "color_identity": ["W", "U", "B", "R", "G"],
        }
        classifier = CardClassifier(card)
        # Front face is Creature (no priority type), so goes to Multicolor
        assert classifier.get_primary_type() is None
        assert classifier.get_classified_folder_path() == "Multicolor/"


class TestClassificationInfo:
    """Test the classification info method for debugging"""

    def test_classification_info_structure(self):
        """Ensure classification info returns correct structure"""
        card = {
            "name": "Test Card",
            "type_line": "Enchantment Artifact",
            "color_identity": ["U", "B"],
        }
        classifier = CardClassifier(card)
        info = classifier.get_classification_info()

        assert "type_line" in info
        assert "color_identity" in info
        assert "primary_type" in info
        assert "color_folder" in info
        assert "full_path" in info

        assert info["type_line"] == "Enchantment Artifact"
        assert info["color_identity"] == ["U", "B"]
        assert info["primary_type"] == "Enchantment"
        assert info["color_folder"] == "Multicolor"
        assert info["full_path"] == "Enchantment/Multicolor/"


# Run tests with: pytest src/test_card_classifier.py -v
