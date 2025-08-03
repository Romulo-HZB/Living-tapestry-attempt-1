from __future__ import annotations

from typing import Optional, Dict, Any

from .events import Event
from .world_state import WorldState
from rpg import combat_rules


class Narrator:
    """Simple component turning events into plain text descriptions."""

    def __init__(self, world: WorldState):
        self.world = world

    def render(self, event: Event, extra: Optional[Dict[str, Any]] = None) -> str:
        if event.event_type == "describe_location":
            return event.payload.get("description", "")
        elif event.event_type == "move":
            actor = self.world.get_npc(event.actor_id)
            loc = self.world.get_location_static(event.target_ids[0])
            return f"{actor.name} moves to {loc.description}"
        elif event.event_type == "grab":
            actor = self.world.get_npc(event.actor_id)
            item = self.world.get_item_instance(event.target_ids[0])
            bp = self.world.get_item_blueprint(item.blueprint_id)
            return f"{actor.name} picks up {bp.name}."
        elif event.event_type == "attack_attempt":
            attacker = self.world.get_npc(event.actor_id)
            target = self.world.get_npc(event.target_ids[0])
            weapon = combat_rules.get_weapon(self.world, attacker)
            return f"{attacker.name} attacks {target.name} with {weapon.name}."
        elif event.event_type == "attack_hit":
            attacker = self.world.get_npc(event.actor_id)
            target = self.world.get_npc(event.target_ids[0])
            return (
                f"{attacker.name} hits {target.name} "
                f"(roll {event.payload['to_hit']} vs AC {event.payload['target_ac']})"
            )
        elif event.event_type == "attack_missed":
            attacker = self.world.get_npc(event.actor_id)
            target = self.world.get_npc(event.target_ids[0])
            return (
                f"{attacker.name} misses {target.name} "
                f"(roll {event.payload['to_hit']} vs AC {event.payload['target_ac']})"
            )
        elif event.event_type == "damage_applied":
            target = self.world.get_npc(event.target_ids[0])
            amount = event.payload.get("amount", 0)
            dmg_type = event.payload.get("damage_type", "")
            return f"{target.name} takes {amount} {dmg_type} damage (HP: {target.hp})"
        elif event.event_type == "talk":
            speaker = self.world.get_npc(event.actor_id)
            content = event.payload.get("content", "")
            if event.target_ids:
                target = self.world.get_npc(event.target_ids[0])
                return f"{speaker.name} to {target.name}: {content}"
            return f"{speaker.name} says: {content}"
        elif event.event_type == "inventory":
            actor = self.world.get_npc(event.actor_id)
            items = event.payload.get("items", [])
            if items:
                return f"{actor.name} carries: {', '.join(items)}"
            return f"{actor.name} carries nothing."
        return ""
