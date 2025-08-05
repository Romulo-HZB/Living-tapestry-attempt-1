from typing import Dict, Any, List

from .base import Tool
from ..events import Event
from ..world_state import WorldState
from ..data_models import NPC


class WaitTool(Tool):
    """Tool allowing an actor to deliberately pass time."""

    def __init__(self):
        super().__init__(name="wait", time_cost=1)

    def validate_intent(self, intent: Dict[str, Any], world: WorldState, actor: NPC) -> bool:
        ticks = intent.get("ticks", 1)
        return isinstance(ticks, int) and ticks >= 1

    def generate_events(self, intent: Dict[str, Any], world: WorldState, actor: NPC, tick: int) -> List[Event]:
        ticks = intent.get("ticks", 1)
        # Update time_cost so process_command sets next_available_tick correctly
        self.time_cost = ticks
        return [
            Event(
                event_type="wait",
                tick=tick + ticks,
                actor_id=actor.id,
                payload={"ticks": ticks},
            )
        ]
