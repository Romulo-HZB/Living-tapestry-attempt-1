from typing import Dict, Any, List

from .base import Tool
from ..events import Event
from ..world_state import WorldState
from ..data_models import NPC


class AttackTool(Tool):
    def __init__(self, time_cost: int = 3):
        super().__init__(name="attack", time_cost=time_cost)

    def validate_intent(self, intent: Dict[str, Any], world: WorldState, actor: NPC) -> bool:
        target_id = intent.get("target_id")
        if not target_id or target_id not in world.npcs:
            return False
        attacker_loc = world.find_npc_location(actor.id)
        target_loc = world.find_npc_location(target_id)
        return attacker_loc is not None and attacker_loc == target_loc

    def generate_events(self, intent: Dict[str, Any], world: WorldState, actor: NPC, tick: int) -> List[Event]:
        return [
            Event(
                event_type="attack_attempt",
                tick=tick,
                actor_id=actor.id,
                target_ids=[intent["target_id"]],
            )
        ]
