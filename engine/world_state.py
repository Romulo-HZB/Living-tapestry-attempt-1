import json
from pathlib import Path
from typing import Dict, Optional, Any

from .data_models import (
    NPC,
    LocationStatic,
    LocationState,
    ItemBlueprint,
    ItemInstance,
)
from .events import Event


class WorldState:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.npcs: Dict[str, NPC] = {}
        self.locations_static: Dict[str, LocationStatic] = {}
        self.locations_state: Dict[str, LocationState] = {}
        self.item_blueprints: Dict[str, ItemBlueprint] = {}
        self.item_instances: Dict[str, ItemInstance] = {}

    def load(self):
        self._load_npcs()
        self._load_locations()
        self._load_items()
        # assign current_location for items based on location state
        for loc_id, state in self.locations_state.items():
            for item_id in state.items:
                inst = self.item_instances.get(item_id)
                if inst and inst.current_location is None:
                    inst.current_location = loc_id

    def _load_npcs(self):
        npcs_dir = self.data_dir / "npcs"
        for path in npcs_dir.glob("*.json"):
            with open(path, "r") as f:
                data = json.load(f)
            if "next_available_tick" not in data:
                data["next_available_tick"] = 0
            if "last_meal_tick" not in data:
                data["last_meal_tick"] = 0
            if "hunger_stage" not in data:
                data["hunger_stage"] = "sated"
            npc = NPC(**data)
            self.npcs[npc.id] = npc

    def _load_locations(self):
        loc_dir = self.data_dir / "locations"
        for path in loc_dir.glob("*_static.json"):
            with open(path, "r") as f:
                data = json.load(f)
            loc = LocationStatic(**data)
            self.locations_static[loc.id] = loc
        for path in loc_dir.glob("*_state.json"):
            with open(path, "r") as f:
                data = json.load(f)
            loc = LocationState(**data)
            self.locations_state[loc.id] = loc

    def _load_items(self):
        items_dir = self.data_dir / "items"
        catalog_path = items_dir / "catalog.json"
        if catalog_path.exists():
            with open(catalog_path, "r") as f:
                catalog = json.load(f)
            for item_id, data in catalog.items():
                blueprint = ItemBlueprint(id=item_id, **data)
                self.item_blueprints[blueprint.id] = blueprint

        instances_dir = items_dir / "instances"
        if instances_dir.exists():
            for path in instances_dir.glob("*.json"):
                with open(path, "r") as f:
                    data = json.load(f)
                instance = ItemInstance(**data)
                self.item_instances[instance.id] = instance

    def get_npc(self, npc_id: str) -> NPC:
        return self.npcs[npc_id]

    def get_location_static(self, loc_id: str) -> LocationStatic:
        return self.locations_static[loc_id]

    def get_location_state(self, loc_id: str) -> LocationState:
        return self.locations_state[loc_id]

    def get_item_instance(self, item_id: str) -> ItemInstance:
        return self.item_instances[item_id]

    def get_item_blueprint(self, blueprint_id: str) -> ItemBlueprint:
        return self.item_blueprints[blueprint_id]

    def find_npc_location(self, npc_id: str) -> Optional[str]:
        for loc_id, loc in self.locations_state.items():
            if npc_id in loc.occupants:
                return loc_id
        return None

    def update_hunger(self, current_tick: int) -> list[Event]:
        HUNGRY_THRESHOLD = 20
        STARVING_THRESHOLD = 40
        events: list[Event] = []
        for npc in self.npcs.values():
            ticks_since = current_tick - npc.last_meal_tick
            if ticks_since >= STARVING_THRESHOLD:
                npc.hunger_stage = "starving"
                events.append(
                    Event(
                        event_type="damage_applied",
                        tick=current_tick,
                        actor_id=npc.id,
                        target_ids=[npc.id],
                        payload={"amount": 1, "damage_type": "starvation"},
                    )
                )
            elif ticks_since >= HUNGRY_THRESHOLD:
                npc.hunger_stage = "hungry"
            else:
                npc.hunger_stage = "sated"
        return events

    def apply_event(self, event):
        if event.event_type == "move":
            actor_id = event.actor_id
            target = event.target_ids[0]
            current_loc = self.find_npc_location(actor_id)
            if current_loc:
                self.locations_state[current_loc].occupants.remove(actor_id)
            self.locations_state[target].occupants.append(actor_id)
        elif event.event_type == "grab":
            actor_id = event.actor_id
            item_id = event.target_ids[0]
            loc_id = self.find_npc_location(actor_id)
            if loc_id and item_id in self.locations_state[loc_id].items:
                self.locations_state[loc_id].items.remove(item_id)
                self.npcs[actor_id].inventory.append(item_id)
                inst = self.item_instances.get(item_id)
                if inst:
                    inst.owner_id = actor_id
                    inst.current_location = None
        elif event.event_type == "drop":
            actor_id = event.actor_id
            item_id = event.target_ids[0]
            loc_id = self.find_npc_location(actor_id)
            if loc_id and item_id in self.npcs[actor_id].inventory:
                self.npcs[actor_id].inventory.remove(item_id)
                self.locations_state[loc_id].items.append(item_id)
                inst = self.item_instances.get(item_id)
                if inst:
                    inst.owner_id = None
                    inst.current_location = loc_id
        elif event.event_type == "eat":
            actor_id = event.actor_id
            item_id = event.target_ids[0]
            npc = self.npcs.get(actor_id)
            if npc and item_id in npc.inventory:
                npc.inventory.remove(item_id)
                self.item_instances.pop(item_id, None)
                npc.last_meal_tick = event.tick
                npc.hunger_stage = "sated"
        elif event.event_type == "damage_applied":
            target_id = event.target_ids[0]
            amount = event.payload.get("amount", 0)
            npc = self.npcs.get(target_id)
            if npc:
                npc.hp -= amount
        elif event.event_type == "equip":
            actor_id = event.actor_id
            item_id = event.target_ids[0]
            slot = event.payload.get("slot")
            npc = self.npcs.get(actor_id)
            if npc and slot in npc.slots and item_id in npc.inventory:
                current = npc.slots.get(slot)
                if current:
                    npc.inventory.append(current)
                npc.inventory.remove(item_id)
                npc.slots[slot] = item_id
        elif event.event_type == "unequip":
            actor_id = event.actor_id
            slot = event.payload.get("slot")
            npc = self.npcs.get(actor_id)
            if npc and slot in npc.slots and npc.slots.get(slot):
                item_id = npc.slots[slot]
                npc.inventory.append(item_id)
                npc.slots[slot] = None
        elif event.event_type == "give":
            actor_id = event.actor_id
            item_id, target_id = event.target_ids
            giver = self.npcs.get(actor_id)
            receiver = self.npcs.get(target_id)
            if giver and receiver and item_id in giver.inventory:
                giver.inventory.remove(item_id)
                receiver.inventory.append(item_id)
                inst = self.item_instances.get(item_id)
                if inst:
                    inst.owner_id = target_id
        elif event.event_type == "open_connection":
            actor_loc = self.find_npc_location(event.actor_id)
            target = event.target_ids[0]
            if actor_loc:
                self.locations_state[actor_loc].connections_state.setdefault(target, {})["status"] = "open"
                self.locations_state[target].connections_state.setdefault(actor_loc, {})["status"] = "open"
        elif event.event_type == "close_connection":
            actor_loc = self.find_npc_location(event.actor_id)
            target = event.target_ids[0]
            if actor_loc:
                self.locations_state[actor_loc].connections_state.setdefault(target, {})["status"] = "closed"
                self.locations_state[target].connections_state.setdefault(actor_loc, {})["status"] = "closed"
