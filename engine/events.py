from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Event:
    event_type: str
    tick: int
    actor_id: str
    target_ids: List[str] = field(default_factory=list)
    payload: Dict[str, Any] = field(default_factory=dict)
