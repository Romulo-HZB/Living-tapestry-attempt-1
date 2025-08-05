import sys
import os
from pathlib import Path

# Allow running from repository root
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from engine.world_state import WorldState
from engine.simulator import Simulator
from engine.narrator import Narrator
from engine.tools.attack import AttackTool
from engine.tools.talk import TalkTool
from engine.tools.move import MoveTool


def main():
    world = WorldState(Path("data"))
    world.load()
    narrator = Narrator(world)
    sim = Simulator(world, narrator=narrator, player_id="npc_sample")
    sim.register_tool(AttackTool())
    sim.register_tool(TalkTool())
    sim.register_tool(MoveTool())

    print("Initial HP:", world.get_npc("npc_sample").hp)
    for _ in range(5):
        sim.tick()
    print("HP after a few ticks:", world.get_npc("npc_sample").hp)


if __name__ == "__main__":
    main()
