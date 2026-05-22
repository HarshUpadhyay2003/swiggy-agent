from typing import Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class TelemetryRequest(BaseModel):
    event: str = Field(..., min_length=1, description="Telemetry event name")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Additional telemetry payload")


@router.post("")
async def receive_telemetry(request: TelemetryRequest) -> Dict[str, str]:
    """Receive lightweight telemetry events from the frontend."""
    # No-op telemetry endpoint; useful for frontend diagnostics without failing UX.
    return {"status": "accepted", "event": request.event}
