import json
from pathlib import Path
from typing import Dict, Optional

from .data_models import NPC, LocationStatic, LocationState


class WorldState:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.npcs: Dict[str, NPC] = {}
        self.locations_static: Dict[str, LocationStatic] = {}
        self.locations_state: Dict[str, LocationState] = {}

    def load(self):
        self._load_npcs()
        self._load_locations()

    def _load_npcs(self):
        npcs_dir = self.data_dir / "npcs"
        for path in npcs_dir.glob("*.json"):
            with open(path, "r") as f:
                data = json.load(f)
            if "next_available_tick" not in data:
                data["next_available_tick"] = 0
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

    def get_npc(self, npc_id: str) -> NPC:
        return self.npcs[npc_id]

    def get_location_static(self, loc_id: str) -> LocationStatic:
        return self.locations_static[loc_id]

    def get_location_state(self, loc_id: str) -> LocationState:
        return self.locations_state[loc_id]

    def find_npc_location(self, npc_id: str) -> Optional[str]:
        for loc_id, loc in self.locations_state.items():
            if npc_id in loc.occupants:
                return loc_id
        return None

    def apply_event(self, event):
        if event.event_type == "move":
            actor_id = event.actor_id
            target = event.target_ids[0]
            current_loc = self.find_npc_location(actor_id)
            if current_loc:
                self.locations_state[current_loc].occupants.remove(actor_id)
            self.locations_state[target].occupants.append(actor_id)
