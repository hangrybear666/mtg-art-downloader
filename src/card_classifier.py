"""
CARD CLASSIFICATION SYSTEM

This module provides card type classification and color identity organization
for MTG Art Downloader. It extends the existing Card class hierarchy by adding
folder path logic based on card type precedence and color identity.

Type Precedence (IMMUTABLE):
    Token > Land > Enchantment > Artifact

Folder Organization:
    - Tokens: Token/{color_identity}/
    - Lands: Land/ (or Basic/ for basic lands)
    - Enchantments: Enchantment/{color_identity}/
    - Artifacts: Artifact/
    - Others: {color_identity}/ (root level)

Color Identity Subfolders:
    - White, Blue, Black, Red, Green (monocolor)
    - Multicolor (2+ colors)
    - Colorless (no colors or missing field)
"""

from typing import Optional


class CardClassifier:
    """
    Provides classification logic for MTG cards based on type_line and color_identity.

    This class implements a strict type precedence system and color identity
    organization without making any API requests - it only analyzes existing
    Scryfall data already present in card dictionaries.
    """

    # Type precedence constants (higher number = higher precedence)
    TYPE_PRECEDENCE = {
        "Token": 4,
        "Land": 3,
        "Enchantment": 2,
        "Artifact": 1,
    }

    # Color identity mapping
    COLOR_NAMES = {
        "W": "White",
        "U": "Blue",
        "B": "Black",
        "R": "Red",
        "G": "Green",
    }

    def __init__(self, card_data: dict) -> None:
        """
        Initialize the classifier with Scryfall card data.

        Args:
            card_data: Dictionary containing Scryfall card information,
                      including 'type_line' and 'color_identity' fields.
        """
        self.card_data = card_data
        self._type_line = self._get_type_line()
        self._color_identity = card_data.get("color_identity", [])

    def _get_type_line(self) -> str:
        """
        Extract type_line from card data, handling multi-faced cards.

        For dual-faced cards (MDFC, Transform, etc.), we use the front face
        type_line for classification purposes.

        Returns:
            The type_line string, or empty string if not found.
        """
        # Check for direct type_line first
        if "type_line" in self.card_data:
            return self.card_data["type_line"]

        # Check card_faces for multi-faced cards (use front face)
        card_faces = self.card_data.get("card_faces", [])
        if card_faces and len(card_faces) > 0:
            return card_faces[0].get("type_line", "")

        return ""

    def _normalize_type_line(self, type_line: str) -> str:
        """
        Normalize type_line for consistent comparison.

        Args:
            type_line: Raw type_line string from Scryfall.

        Returns:
            Normalized type_line (stripped whitespace, consistent spacing).
        """
        # Strip whitespace and normalize multiple spaces to single space
        return " ".join(type_line.strip().split())

    def _has_type(self, type_name: str) -> bool:
        """
        Check if a specific type appears in the card's type_line.

        Args:
            type_name: The type to search for (e.g., "Token", "Land", "Enchantment").

        Returns:
            True if type_name appears in type_line, False otherwise.
        """
        normalized = self._normalize_type_line(self._type_line)
        return type_name in normalized

    def get_primary_type(self) -> Optional[str]:
        """
        Determine the primary type for folder organization based on precedence.

        Applies strict precedence rules:
        1. Token (if "Token" appears anywhere)
        2. Land (if "Land" appears, excluding Tokens)
        3. Enchantment (if "Enchantment" appears, excluding Tokens/Lands)
        4. Artifact (if "Artifact" appears, excluding Tokens/Lands/Enchantments)
        5. None (all other cards go to root-level color folders)

        Returns:
            The primary type string ("Token", "Land", "Enchantment", "Artifact"),
            or None for cards that don't match any priority type.
        """
        # Check in order of precedence (highest to lowest)
        if self._has_type("Token"):
            return "Token"

        if self._has_type("Land"):
            return "Land"

        if self._has_type("Enchantment"):
            return "Enchantment"

        if self._has_type("Artifact"):
            return "Artifact"

        # No priority type found - will go to root-level color folder
        return None

    def is_basic_land(self) -> bool:
        """
        Check if this card is a Basic Land.

        Returns:
            True if type_line contains "Basic Land", False otherwise.
        """
        normalized = self._normalize_type_line(self._type_line)
        return "Basic Land" in normalized

    def get_color_identity_folder(self) -> str:
        """
        Determine the color identity folder name.

        Returns:
            One of: "White", "Blue", "Black", "Red", "Green", "Multicolor", "Colorless"
        """
        # Handle missing or empty color_identity
        if not self._color_identity or len(self._color_identity) == 0:
            return "Colorless"

        # Multicolor (2+ colors)
        if len(self._color_identity) > 1:
            return "Multicolor"

        # Monocolor - map single color code to name
        color_code = self._color_identity[0]
        return self.COLOR_NAMES.get(color_code, "Colorless")

    def requires_color_subfolder(self, primary_type: Optional[str]) -> bool:
        """
        Determine if this card type requires color identity subfolders.

        Args:
            primary_type: The primary type from get_primary_type()

        Returns:
            True if color subfolders should be used, False otherwise.
        """
        # Token, Enchantment, and root-level cards use color subfolders
        # Land and Artifact do NOT use color subfolders
        if primary_type is None:
            # Root-level cards always use color folders
            return True

        return primary_type in ["Token", "Enchantment"]

    def get_classified_folder_path(self) -> str:
        """
        Generate the complete folder path based on classification rules.

        This is the main method to call for determining where a card should be saved.

        Returns:
            Relative folder path string (e.g., "Enchantment/Multicolor/", "Land/", "Token/Colorless/")
        """
        primary_type = self.get_primary_type()

        # Special case: Basic Lands go to "Basic/" folder
        if primary_type == "Land" and self.is_basic_land():
            return "Basic/"

        # Land and Artifact go directly to their folder (no color subfolders)
        if primary_type == "Land":
            return "Land/"

        if primary_type == "Artifact":
            return "Artifact/"

        # Token, Enchantment, and root-level cards use color subfolders
        color_folder = self.get_color_identity_folder()

        if primary_type == "Token":
            return f"Token/{color_folder}/"

        if primary_type == "Enchantment":
            return f"Enchantment/{color_folder}/"

        # Root-level cards (creatures, sorceries, instants, etc.)
        return f"{color_folder}/"

    def get_classification_info(self) -> dict:
        """
        Get detailed classification information for debugging/logging.

        Returns:
            Dictionary containing classification details:
                - type_line: The card's type_line
                - color_identity: The card's color codes
                - primary_type: The determined primary type
                - color_folder: The color identity folder name
                - full_path: The complete folder path
        """
        primary_type = self.get_primary_type()

        return {
            "type_line": self._type_line,
            "color_identity": self._color_identity,
            "primary_type": primary_type or "None (Root)",
            "color_folder": self.get_color_identity_folder(),
            "full_path": self.get_classified_folder_path(),
        }


def get_classified_folder_path(card_data: dict) -> str:
    """
    Convenience function to get folder path for a card without instantiating classifier.

    Args:
        card_data: Dictionary containing Scryfall card information.

    Returns:
        Relative folder path string for the card.
    """
    classifier = CardClassifier(card_data)
    return classifier.get_classified_folder_path()
