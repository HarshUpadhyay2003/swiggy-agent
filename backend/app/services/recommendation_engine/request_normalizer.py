"""
Layer 0 — Request Normalizer
Normalizes user query text into canonical terms (e.g. 'veg' -> 'veg', 'non veg' -> 'non-veg', '100 rs' -> '100').
Does NOT perform intent classification, candidate retrieval, ranking, or validation.
"""

import re


class RequestNormalizer:
    """Layer 0: Pure text normalization for incoming user queries."""

    def normalize(self, message: str) -> str:
        """Applies deterministic regex string normalization."""
        text = str(message or "").strip()
        text_lower = text.lower()

        # Diet normalization
        text_lower = re.sub(r"\bnon\s*veg\b", "non-veg", text_lower)
        text_lower = re.sub(r"\bvegetarian\b", "veg", text_lower)

        # Currency normalization
        text_lower = re.sub(r"(\d+)\s*(?:rs|rupees|inr)\b", r"\1", text_lower)
        text_lower = re.sub(r"₹\s*(\d+)", r"\1", text_lower)

        # Category normalization
        text_lower = re.sub(r"\bdrinks\b", "beverages", text_lower)

        status = "EXECUTED"
        print("\n========================================")
        print("LAYER 0: Request Normalizer")
        print(f"Status    : {status}")
        print(f"Original  : \"{message}\"")
        print(f"Normalized: \"{text_lower}\"")
        print("========================================\n")

        return text_lower
