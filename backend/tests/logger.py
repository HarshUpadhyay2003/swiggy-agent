"""
Log Interceptor and Telemetry Parser for Recommendation Pipeline Verification Framework.
Captures stdout logs emitted during /chat request execution and extracts structured telemetry blocks for Layers 0-7.
"""

import io
import re
import sys
from typing import Any, Dict, List, Optional


class TelemetryExtractor:
    """Parses captured stdout string for structured layer telemetry blocks."""

    @staticmethod
    def extract_layers(captured_output: str) -> Dict[str, Any]:
        """Parse stdout text and populate layer telemetry dictionary."""
        layers: Dict[str, Any] = {
            "layer_0": None,
            "layer_1": None,
            "layer_2": None,
            "layer_3": None,
            "layer_4": None,
            "layer_5": None,
            "layer_6": None,
            "layer_7": None,
            "candidate_integrity": None,
            "domain_transition": None,
            "pipeline_summary": None,
            "raw_log": captured_output,
        }

        # Layer 0
        l0_match = re.search(r"LAYER 0[^\n]*\n(.*?)(?=\n={10,}|\Z)", captured_output, re.DOTALL)
        if l0_match:
            layers["layer_0"] = l0_match.group(1).strip()

        # Layer 1
        l1_match = re.search(r"LAYER 1:[^\n]*\n(.*?)(?=\n={10,}|\Z)", captured_output, re.DOTALL)
        if l1_match:
            layers["layer_1"] = l1_match.group(1).strip()

        # Layer 2
        l2_match = re.search(r"LAYER 2:[^\n]*\n(.*?)(?=\n={10,}|\Z)", captured_output, re.DOTALL)
        if l2_match:
            layers["layer_2"] = l2_match.group(1).strip()

        # Domain Transition
        dt_match = re.search(r"DOMAIN TRANSITION REPORT\n(.*?)(?=\n={10,}|\Z)", captured_output, re.DOTALL)
        if dt_match:
            layers["domain_transition"] = dt_match.group(1).strip()

        # Layer 3
        l3_match = re.search(r"LAYER 3: Schema Field Matcher\n(.*?)(?=\n={10,}|\Z)", captured_output, re.DOTALL)
        if l3_match:
            layers["layer_3"] = l3_match.group(1).strip()

        # Candidate Integrity
        ci_match = re.search(r"CANDIDATE INTEGRITY\n(.*?)(?=\n={10,}|\Z)", captured_output, re.DOTALL)
        if ci_match:
            layers["candidate_integrity"] = ci_match.group(1).strip()

        # Layer 4
        l4_match = re.search(r"LAYER 4: Candidate Retriever\n(.*?)(?=\n={10,}|\Z)", captured_output, re.DOTALL)
        if l4_match:
            layers["layer_4"] = l4_match.group(1).strip()

        # Layer 5
        l5_match = re.search(r"LAYER 5: Ranking Engine\n(.*?)(?=\n={10,}|\Z)", captured_output, re.DOTALL)
        if l5_match:
            layers["layer_5"] = l5_match.group(1).strip()

        # Layer 6
        l6_match = re.search(r"LAYER 6: Recommendation Validator\n(.*?)(?=\n={10,}|\Z)", captured_output, re.DOTALL)
        if l6_match:
            layers["layer_6"] = l6_match.group(1).strip()

        # Layer 7
        l7_match = re.search(r"LAYER 7: Response Generator\n(.*?)(?=\n={10,}|\Z)", captured_output, re.DOTALL)
        if l7_match:
            layers["layer_7"] = l7_match.group(1).strip()

        # Final Pipeline Summary
        summary_match = re.search(r"FINAL PIPELINE SUMMARY\n(.*?)(?=\n={10,}|\Z)", captured_output, re.DOTALL)
        if summary_match:
            layers["pipeline_summary"] = summary_match.group(1).strip()

        return layers


class LogCapture:
    """Context manager to intercept stdout during API call execution."""

    def __enter__(self):
        self._stdout_buffer = io.StringIO()
        self._original_stdout = sys.stdout
        sys.stdout = self._stdout_buffer
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self._original_stdout
        self.captured_text = self._stdout_buffer.getvalue()

    def get_captured_text(self) -> str:
        return getattr(self, "captured_text", "")
