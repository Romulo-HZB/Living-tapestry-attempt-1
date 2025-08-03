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
            description = event.payload.get("description", "")
            occupants = event.payload.get("occupants", [])
            items = event.payload.get("items", [])
            parts = [description]
            if occupants:
                parts.append("You see: " + ", ".join(occupants))
            if items:
                parts.append("Items here: " + ", ".join(items))
            return " ".join(parts).strip()
        elif event.event_type == "move":
            actor = self.world.get_npc(event.actor_id)
            loc = self.world.get_location_static(event.target_ids[0])
            return f"{actor.name} moves to {loc.description}"
        elif event.event_type == "grab":
            actor = self.world.get_npc(event.actor_id)
            item = self.world.get_item_instance(event.target_ids[0])
            bp = self.world.get_item_blueprint(item.blueprint_id)
            return f"{actor.name} picks up {bp.name}."
        elif event.event_type == "drop":
            actor = self.world.get_npc(event.actor_id)
            item = self.world.get_item_instance(event.target_ids[0])
            bp = self.world.get_item_blueprint(item.blueprint_id)
            return f"{actor.name} drops {bp.name}."
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
        elif event.event_type == "scream":
            speaker = self.world.get_npc(event.actor_id)
            content = event.payload.get("content", "")
            return f"{speaker.name} screams: {content}"
        elif event.event_type == "inventory":
            actor = self.world.get_npc(event.actor_id)
            items = event.payload.get("items", [])
            if items:
                return f"{actor.name} carries: {', '.join(items)}"
            return f"{actor.name} carries nothing."
        elif event.event_type == "stats":
            actor = self.world.get_npc(event.actor_id)
            hp = event.payload.get("hp", 0)
            attrs = event.payload.get("attributes", {})
            skills = event.payload.get("skills", {})
            parts = [f"HP: {hp}"]
            if attrs:
                attr_str = ", ".join(f"{k}: {v}" for k, v in attrs.items())
                parts.append(f"Attributes: {attr_str}")
            if skills:
                skill_str = ", ".join(f"{k} ({v})" for k, v in skills.items())
                parts.append(f"Skills: {skill_str}")
            return f"{actor.name} stats - " + "; ".join(parts)
        elif event.event_type == "equip":
            actor = self.world.get_npc(event.actor_id)
            item = self.world.get_item_instance(event.target_ids[0])
            bp = self.world.get_item_blueprint(item.blueprint_id)
            slot = event.payload.get("slot", "")
            return f"{actor.name} equips {bp.name} to {slot}."
        elif event.event_type == "unequip":
            actor = self.world.get_npc(event.actor_id)
            item = self.world.get_item_instance(event.target_ids[0])
            bp = self.world.get_item_blueprint(item.blueprint_id)
            slot = event.payload.get("slot", "")
            return f"{actor.name} removes {bp.name} from {slot}."
        elif event.event_type == "analyze":
            name = event.payload.get("name", "")
            weight = event.payload.get("weight")
            damage = event.payload.get("damage_dice")
            dmg_type = event.payload.get("damage_type")
            armour = event.payload.get("armour_rating")
            props = event.payload.get("properties", [])
            parts = [f"{name} (weight {weight})"]
            if damage:
                parts.append(f"Damage: {damage} {dmg_type}")
            if armour:
                parts.append(f"Armour rating: {armour}")
            if props:
                parts.append("Properties: " + ", ".join(props))
            return " ".join(parts)
        return ""
