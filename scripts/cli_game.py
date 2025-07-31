import sys, os
from pathlib import Path

# Allow running from repository root
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from engine.world_state import WorldState
from engine.simulator import Simulator
from engine.tools.move import MoveTool
from engine.tools.look import LookTool
from engine.tools.grab import GrabTool
from engine.tools.attack import AttackTool


def main():
    world = WorldState(Path("data"))
    world.load()

    sim = Simulator(world)
    sim.register_tool(MoveTool())
    sim.register_tool(LookTool())
    sim.register_tool(GrabTool())
    sim.register_tool(AttackTool())

    actor_id = "npc_sample"  # temporary player actor
    print("Type 'look', 'move <location_id>', 'grab <item_id>', 'attack <npc_id>' or 'quit'.")
    while True:
        cmd = input("-> ").strip()
        if not cmd:
            continue
        if cmd in {"quit", "exit"}:
            break
        if cmd == "look":
            command = {"tool": "look", "params": {}}
        elif cmd.startswith("move "):
            target = cmd.split(" ", 1)[1]
            command = {"tool": "move", "params": {"target_location": target}}
        elif cmd.startswith("grab "):
            item = cmd.split(" ", 1)[1]
            command = {"tool": "grab", "params": {"item_id": item}}
        elif cmd.startswith("attack "):
            target = cmd.split(" ", 1)[1]
            command = {"tool": "attack", "params": {"target_id": target}}
        else:
            print("Unknown command")
            continue
        try:
            sim.process_command(actor_id, command)
        except ValueError as e:
            print("Error:", e)
            continue
        # Process events until queue is empty
        while sim.event_queue:
            sim.tick()
        # Advance time until actor is ready again
        while sim.world.get_npc(actor_id).next_available_tick > sim.game_tick:
            sim.tick()


if __name__ == "__main__":
    main()
