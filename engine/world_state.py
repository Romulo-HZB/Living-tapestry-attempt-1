import json
from pathlib import Path
from typing import Dict

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
