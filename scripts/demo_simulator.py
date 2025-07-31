import sys, os; sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from pathlib import Path

from engine.world_state import WorldState
from engine.simulator import Simulator
from engine.tools.move import MoveTool
from engine.tools.look import LookTool


def main():
    world = WorldState(Path("data"))
    world.load()
    sim = Simulator(world)
    sim.register_tool(MoveTool())
    sim.register_tool(LookTool())

    print("Initial location occupants:")
    for loc_id, loc in world.locations_state.items():
        print(loc_id, loc.occupants)

    command = {"tool": "move", "params": {"target_location": "market_square"}}
    sim.process_command("npc_sample", command)
    for _ in range(6):
        sim.tick()

    print("After move:")
    for loc_id, loc in world.locations_state.items():
        print(loc_id, loc.occupants)


if __name__ == "__main__":
    main()
