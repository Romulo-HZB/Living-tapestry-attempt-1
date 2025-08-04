from typing import Dict, Any, List

from .base import Tool
from ..events import Event
from ..world_state import WorldState
from ..data_models import NPC


class CloseDoorTool(Tool):
    def __init__(self, time_cost: int = 1):
        super().__init__(name="close", time_cost=time_cost)

    def validate_intent(self, intent: Dict[str, Any], world: WorldState, actor: NPC) -> bool:
        target = intent.get("target_location")
        if not target or target not in world.locations_static:
            return False
        current = world.find_npc_location(actor.id)
        if not current:
            return False
        static = world.get_location_static(current)
        if target not in static.hex_connections.values():
            return False
        loc_state = world.get_location_state(current)
        conn = loc_state.connections_state.get(target, {})
        return conn.get("status", "open") == "open"

    def generate_events(self, intent: Dict[str, Any], world: WorldState, actor: NPC, tick: int) -> List[Event]:
        return [
            Event(
                event_type="close_connection",
                tick=tick,
                actor_id=actor.id,
                target_ids=[intent["target_location"]],
            )
        ]
