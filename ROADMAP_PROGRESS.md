# Roadmap Progress

This document tracks the implementation status of the engine against the design roadmap in `Follow this`.

## Completed Work

- **Phase 1 – Data Schemas and WorldState**
  - Dataclasses for NPCs, locations and items are defined in `engine/data_models.py`.
  - `engine/world_state.py` loads all JSON data from the `data/` directory.
  - A loader test script (`scripts/test_loader.py`) confirms that the world can be loaded.

- **Phase 2 – Basic Event Loop**
  - `engine/simulator.py` implements a simple event queue and tick system.
  - Tools exist for looking, moving and grabbing items (`engine/tools`).
  - `scripts/demo_simulator.py` demonstrates moving an actor and picking up an item.
  - Actors have `next_available_tick` and tools have `time_cost`, providing the
    beginnings of the Action‑Time system.
  - `scripts/cli_game.py` implements an interactive command loop.

## Outstanding Tasks

- Integrate an LLM command parser (Phase 3). A basic `LLMClient` stub and optional
  LLM mode for the CLI game are next.
- Add more tools (attack, talk, etc.) and deterministic combat handling (Phase 4).
- Implement NPC AI with memory and conversation systems (Phase 5).
- Build polish features such as the narrator, fallback system and tag rules.

