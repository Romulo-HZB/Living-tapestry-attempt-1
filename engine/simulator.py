from __future__ import annotations

from typing import Dict, Any, List, Optional
import random

from .world_state import WorldState
from .events import Event
from .data_models import NPC
from .tools.base import Tool
from .narrator import Narrator
from rpg import combat_rules


class Simulator:
    def __init__(
        self,
        world: WorldState,
        narrator: Optional[Narrator] = None,
        player_id: Optional[str] = None,
    ):
        self.world = world
        self.game_tick = 0
        self.event_queue: List[Event] = []
        self.tools: Dict[str, Tool] = {}
        self.narrator = narrator or Narrator(world)
        self.player_id = player_id
        self.starvation_enabled = True

    def register_tool(self, tool: Tool):
        self.tools[tool.name] = tool

    def process_command(self, actor_id: str, command: Dict[str, Any]):
        tool = self.tools.get(command["tool"])
        actor = self.world.get_npc(actor_id)
        if not tool:
            raise ValueError(f"Unknown tool {command['tool']}")
        if actor.next_available_tick > self.game_tick:
            raise ValueError("Actor is busy")
        if not tool.validate_intent(command.get("params", {}), self.world, actor):
            raise ValueError("Invalid intent")
        events = tool.generate_events(command.get("params", {}), self.world, actor, self.game_tick)
        self.event_queue.extend(events)
        actor.next_available_tick = self.game_tick + tool.time_cost

    def npc_think(self, npc: NPC) -> Optional[Dict[str, Any]]:
        """Produce a simple command for a non-player actor."""
        current_loc = self.world.find_npc_location(npc.id)
        if not current_loc:
            return None
        loc_static = self.world.get_location_static(current_loc)
        loc_state = self.world.get_location_state(current_loc)
        options = []
        for neighbor_id in loc_static.hex_connections.values():
            conn = loc_state.connections_state.get(neighbor_id, {})
            if conn.get("status", "open") == "open":
                options.append(neighbor_id)
        if options:
            target = random.choice(options)
            return {"tool": "move", "params": {"target_location": target}}
        if random.random() < 0.3:
            return {"tool": "talk", "params": {"content": "looks around."}}
        return None

    def tick(self):
        self.game_tick += 1
        if self.starvation_enabled:
            hunger_events = self.world.update_hunger(self.game_tick)
            self.event_queue.extend(hunger_events)
        for npc_id, npc in self.world.npcs.items():
            if npc_id == self.player_id or "dead" in npc.tags.get("dynamic", []):
                continue
            if npc.next_available_tick <= self.game_tick:
                command = self.npc_think(npc)
                if command:
                    self.process_command(npc_id, command)
        ready_events = [e for e in self.event_queue if e.tick <= self.game_tick]
        self.event_queue = [e for e in self.event_queue if e.tick > self.game_tick]
        for event in ready_events:
            self.handle_event(event)

    def handle_event(self, event: Event):
        if event.event_type == "describe_location":
            msg = self.narrator.render(event)
            if msg:
                print(msg)
        elif event.event_type == "move":
            self.world.apply_event(event)
            msg = self.narrator.render(event)
            if msg:
                print(msg)
        elif event.event_type == "grab":
            self.world.apply_event(event)
            msg = self.narrator.render(event)
            if msg:
                print(msg)
        elif event.event_type == "drop":
            self.world.apply_event(event)
            msg = self.narrator.render(event)
            if msg:
                print(msg)
        elif event.event_type == "eat":
            self.world.apply_event(event)
            msg = self.narrator.render(event)
            if msg:
                print(msg)
        elif event.event_type == "attack_attempt":
            attacker = self.world.get_npc(event.actor_id)
            target = self.world.get_npc(event.target_ids[0])
            result = combat_rules.resolve_attack(self.world, attacker, target)
            payload = {
                "to_hit": result["to_hit"],
                "target_ac": result["target_ac"],
            }
            if result["hit"]:
                payload["damage"] = result["damage"]
                self.event_queue.append(
                    Event(
                        event_type="attack_hit",
                        tick=self.game_tick,
                        actor_id=event.actor_id,
                        target_ids=event.target_ids,
                        payload=payload,
                    )
                )
                self.event_queue.append(
                    Event(
                        event_type="damage_applied",
                        tick=self.game_tick,
                        actor_id=event.actor_id,
                        target_ids=event.target_ids,
                        payload={
                            "amount": result["damage"],
                            "damage_type": combat_rules.get_weapon(self.world, attacker).damage_type,
                        },
                    )
                )
            else:
                self.event_queue.append(
                    Event(
                        event_type="attack_missed",
                        tick=self.game_tick,
                        actor_id=event.actor_id,
                        target_ids=event.target_ids,
                        payload=payload,
                    )
                )
            msg = self.narrator.render(event)
            if msg:
                print(msg)
        elif event.event_type == "attack_hit":
            msg = self.narrator.render(event)
            if msg:
                print(msg)
        elif event.event_type == "attack_missed":
            msg = self.narrator.render(event)
            if msg:
                print(msg)
        elif event.event_type == "damage_applied":
            self.world.apply_event(event)
            msg = self.narrator.render(event)
            if msg:
                print(msg)
            target = self.world.get_npc(event.target_ids[0])
            if target.hp <= 0 and "dead" not in target.tags.get("dynamic", []):
                loc_id = self.world.find_npc_location(target.id)
                self.event_queue.append(
                    Event(
                        event_type="npc_died",
                        tick=self.game_tick,
                        actor_id=target.id,
                        target_ids=[loc_id] if loc_id else [],
                    )
                )
        elif event.event_type == "talk":
            msg = self.narrator.render(event)
            if msg:
                print(msg)
        elif event.event_type == "talk_loud":
            msg = self.narrator.render(event)
            if msg:
                print(msg)
        elif event.event_type == "scream":
            msg = self.narrator.render(event)
            if msg:
                print(msg)
        elif event.event_type == "inventory":
            msg = self.narrator.render(event)
            if msg:
                print(msg)
        elif event.event_type == "stats":
            msg = self.narrator.render(event)
            if msg:
                print(msg)
        elif event.event_type == "equip":
            self.world.apply_event(event)
            msg = self.narrator.render(event)
            if msg:
                print(msg)
        elif event.event_type == "unequip":
            self.world.apply_event(event)
            msg = self.narrator.render(event)
            if msg:
                print(msg)
        elif event.event_type == "analyze":
            msg = self.narrator.render(event)
            if msg:
                print(msg)
        elif event.event_type == "give":
            self.world.apply_event(event)
            msg = self.narrator.render(event)
            if msg:
                print(msg)
        elif event.event_type == "toggle_starvation":
            self.starvation_enabled = event.payload.get("enabled", True)
            if not self.starvation_enabled:
                for npc in self.world.npcs.values():
                    npc.hunger_stage = "sated"
                    npc.last_meal_tick = self.game_tick
            msg = self.narrator.render(event)
            if msg:
                print(msg)
        elif event.event_type in {"open_connection", "close_connection"}:
            self.world.apply_event(event)
            msg = self.narrator.render(event)
            if msg:
                print(msg)
        elif event.event_type == "npc_died":
            self.world.apply_event(event)
            msg = self.narrator.render(event)
            if msg:
                print(msg)
        else:
            self.world.apply_event(event)
        # After applying and narrating, record perception for nearby actors
        self.record_perception(event)

    def record_perception(self, event: Event):
        """Add a simplified perception entry to actors in the same location."""
        if event.event_type == "describe_location":
            return

        if event.event_type == "move":
            location_id = event.target_ids[0]
        elif event.event_type == "npc_died":
            location_id = event.target_ids[0] if event.target_ids else None
        else:
            location_id = self.world.find_npc_location(event.actor_id)

        if not location_id:
            return

        recipients = set()
        loc_state = self.world.get_location_state(location_id)
        for npc_id in loc_state.occupants:
            if npc_id != event.actor_id:
                recipients.add(npc_id)

        if event.event_type == "scream":
            loc_static = self.world.get_location_static(location_id)
            for neighbor_id in loc_static.hex_connections.values():
                neighbor_state = self.world.get_location_state(neighbor_id)
                for npc_id in neighbor_state.occupants:
                    recipients.add(npc_id)
        elif event.event_type == "talk_loud":
            loc_static = self.world.get_location_static(location_id)
            loc_state = self.world.get_location_state(location_id)
            for neighbor_id in loc_static.hex_connections.values():
                conn = loc_state.connections_state.get(neighbor_id, {})
                if conn.get("status", "open") == "open":
                    neighbor_state = self.world.get_location_state(neighbor_id)
                    for npc_id in neighbor_state.occupants:
                        recipients.add(npc_id)

        for npc_id in recipients:
            npc = self.world.get_npc(npc_id)
            npc.short_term_memory.append(
                {
                    "tick": self.game_tick,
                    "event_type": event.event_type,
                    "actor_id": event.actor_id,
                    "payload": event.payload,
                }
            )
            if len(npc.short_term_memory) > 20:
                npc.short_term_memory.pop(0)
