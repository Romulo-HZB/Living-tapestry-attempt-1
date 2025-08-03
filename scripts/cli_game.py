import sys
import os
from pathlib import Path
import argparse


# Allow running from repository root
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from engine.world_state import WorldState
from engine.simulator import Simulator
from engine.narrator import Narrator
from engine.tools.move import MoveTool
from engine.tools.look import LookTool
from engine.tools.grab import GrabTool
from engine.tools.attack import AttackTool
from engine.tools.talk import TalkTool
from engine.tools.inventory import InventoryTool
from engine.llm_client import LLMClient


SYSTEM_PROMPT = (
    "You are a command parser for a text game. "
    "Return a JSON object describing the player's intended action. "
    "Available tools: look, move(target_location), grab(item_id), attack(target_id), talk(content, target_id), inventory()."
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--llm", action="store_true", help="Use LLM to parse commands")
    args = parser.parse_args()

    world = WorldState(Path("data"))
    world.load()

    narrator = Narrator(world)
    sim = Simulator(world, narrator=narrator)
    sim.register_tool(MoveTool())
    sim.register_tool(LookTool())
    sim.register_tool(GrabTool())
    sim.register_tool(AttackTool())
    sim.register_tool(TalkTool())
    sim.register_tool(InventoryTool())

    actor_id = "npc_sample"  # temporary player actor
    if args.llm:
        llm = LLMClient(Path("config/llm.json"))
        print("Type text commands. Say 'quit' to exit.")
    else:
        print("Type 'look', 'move <loc>', 'grab <item>', 'attack <npc>', 'talk <msg>' or 'talk <target> <msg>', 'inventory', 'mem' to review memories, or 'quit'.")

    while True:
        cmd = input("-> ").strip()
        if not cmd:
            continue
        if cmd in {"quit", "exit"}:
            break

        if args.llm:
            command = llm.parse_command(cmd, SYSTEM_PROMPT)
            if not command:
                print("Failed to parse command")
                continue
        else:
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
            elif cmd.startswith("talk "):
                parts = cmd.split(" ", 2)
                if len(parts) == 2:
                    content = parts[1]
                    command = {"tool": "talk", "params": {"content": content}}
                elif len(parts) == 3:
                    if parts[1] in world.npcs:
                        target = parts[1]
                        content = parts[2]
                        command = {
                            "tool": "talk",
                            "params": {"target_id": target, "content": content},
                        }
                    else:
                        content = f"{parts[1]} {parts[2]}"
                        command = {"tool": "talk", "params": {"content": content}}
                else:
                    print("Unknown command")
                    continue
            elif cmd in {"inventory", "inv"}:
                command = {"tool": "inventory", "params": {}}
            elif cmd == "mem":
                npc = world.get_npc(actor_id)
                for mem in npc.short_term_memory:
                    print(mem)
                continue
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
