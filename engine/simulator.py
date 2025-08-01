from __future__ import annotations

from typing import Dict, Any, List, Optional

from .world_state import WorldState
from .events import Event
from .data_models import NPC
from .tools.base import Tool
from .narrator import Narrator
from rpg import combat_rules


class Simulator:
    def __init__(self, world: WorldState, narrator: Optional[Narrator] = None):
        self.world = world
        self.game_tick = 0
        self.event_queue: List[Event] = []
        self.tools: Dict[str, Tool] = {}
        self.narrator = narrator or Narrator(world)

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

    def tick(self):
        self.game_tick += 1
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
        elif event.event_type == "attack":
            attacker = self.world.get_npc(event.actor_id)
            target = self.world.get_npc(event.target_ids[0])
            result = combat_rules.resolve_attack(self.world, attacker, target)
            if result["hit"]:
                target.hp -= result["damage"]
            msg = self.narrator.render(event, result)
            if msg:
                print(msg)
        elif event.event_type == "talk":
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
        else:
            location_id = self.world.find_npc_location(event.actor_id)

        if not location_id:
            return

        loc_state = self.world.get_location_state(location_id)
        for npc_id in loc_state.occupants:
            if npc_id == event.actor_id:
                continue
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
