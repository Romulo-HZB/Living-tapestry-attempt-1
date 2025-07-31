from __future__ import annotations

from typing import Dict, Any, List

from .world_state import WorldState
from .events import Event
from .data_models import NPC
from .tools.base import Tool


class Simulator:
    def __init__(self, world: WorldState):
        self.world = world
        self.game_tick = 0
        self.event_queue: List[Event] = []
        self.tools: Dict[str, Tool] = {}

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
            print(event.payload.get("description", ""))
        elif event.event_type == "move":
            self.world.apply_event(event)
            loc_id = event.target_ids[0] if event.target_ids else None
            if loc_id:
                loc = self.world.get_location_static(loc_id)
                print(loc.description)
        elif event.event_type == "grab":
            self.world.apply_event(event)
            item = self.world.get_item_instance(event.target_ids[0])
            bp = self.world.get_item_blueprint(item.blueprint_id)
            print(f"Picked up {bp.name}.")
        else:
            self.world.apply_event(event)
