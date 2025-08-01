import sys, os; sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from pathlib import Path

from engine.world_state import WorldState


def main():
    world = WorldState(Path("data"))
    world.load()
    sample_npc = world.get_npc("npc_sample")
    print(f"Loaded NPC: {sample_npc.name}")
    for loc_id, loc in world.locations_state.items():
        print(loc_id, loc.occupants)


if __name__ == "__main__":
    main()
