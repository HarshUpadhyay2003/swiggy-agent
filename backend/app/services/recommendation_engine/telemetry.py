"""
Centralized Telemetry Logger for Recommendation Engine (Stage 3.1).
Exposes TelemetryLogger helper to centralize layer logging and emit FINAL PIPELINE SUMMARY.
"""

import time
from typing import Any, Dict, Optional


class TelemetryLogger:
    """Centralized logging helper for layer traces and final pipeline summary."""

    @staticmethod
    def log_layer(layer_num: int, name: str, details: str) -> None:
        """Prints a standardized layer execution telemetry block."""
        print("\n========================================")
        print(f"LAYER {layer_num}: {name}")
        print(details)
        print("========================================\n")

    @staticmethod
    def log_pipeline_summary(
        request_query: str,
        retrieved_count: int,
        ranked_count: int,
        validated_count: int,
        returned_count: int,
        llm_calls: int,
        execution_time_ms: float,
    ) -> None:
        """Prints the final structured execution telemetry summary block."""
        print("\n========================================")
        print("FINAL PIPELINE SUMMARY")
        print(f"Request        : {request_query}")
        print(f"Retrieved      : {retrieved_count}")
        print(f"Ranked         : {ranked_count}")
        print(f"Validated      : {validated_count}")
        print(f"Returned       : {returned_count}")
        print(f"LLM Calls      : {llm_calls}")
        print(f"Execution Time : {execution_time_ms:.1f} ms")
        print("========================================\n")
