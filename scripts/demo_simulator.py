import sys, os; sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from pathlib import Path

from engine.world_state import WorldState
from engine.simulator import Simulator
from engine.narrator import Narrator
from engine.tools.move import MoveTool
from engine.tools.look import LookTool
from engine.tools.grab import GrabTool
from engine.tools.drop import DropTool


def main():
    world = WorldState(Path("data"))
    world.load()
    narrator = Narrator(world)
    sim = Simulator(world, narrator=narrator)
    sim.register_tool(MoveTool())
    sim.register_tool(LookTool())
    sim.register_tool(GrabTool())
    sim.register_tool(DropTool())

    print("Initial location occupants:")
    for loc_id, loc in world.locations_state.items():
        print(loc_id, loc.occupants)

    command = {"tool": "move", "params": {"target_location": "market_square"}}
    sim.process_command("npc_sample", command)
    for _ in range(6):
        sim.tick()

    grab_cmd = {"tool": "grab", "params": {"item_id": "item_rusty_sword_1"}}
    sim.process_command("npc_sample", grab_cmd)
    sim.tick()

    drop_cmd = {"tool": "drop", "params": {"item_id": "item_rusty_sword_1"}}
    sim.process_command("npc_sample", drop_cmd)
    sim.tick()

    print("After move:")
    for loc_id, loc in world.locations_state.items():
        print(loc_id, loc.occupants)

    print("Inventory after drop:", world.get_npc("npc_sample").inventory)
    print("Location items after drop:", world.get_location_state("market_square").items)


if __name__ == "__main__":
    main()
