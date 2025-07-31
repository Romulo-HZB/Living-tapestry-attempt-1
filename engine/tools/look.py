from typing import Dict, Any, List

from .base import Tool
from ..events import Event
from ..world_state import WorldState
from ..data_models import NPC


class LookTool(Tool):
    def __init__(self, time_cost: int = 1):
        super().__init__(name="look", time_cost=time_cost)

    def validate_intent(self, intent: Dict[str, Any], world: WorldState, actor: NPC) -> bool:
        return True

    def generate_events(self, intent: Dict[str, Any], world: WorldState, actor: NPC, tick: int) -> List[Event]:
        loc_id = world.find_npc_location(actor.id)
        if not loc_id:
            return []
        loc = world.get_location_static(loc_id)
        return [Event(
            event_type="describe_location",
            tick=tick,
            actor_id=actor.id,
            payload={"description": loc.description},
        )]
