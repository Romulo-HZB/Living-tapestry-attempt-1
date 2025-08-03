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

- **Phase 3 – LLM Command Parser**
  - `engine/llm_client.py` connects to an OpenAI-compatible endpoint.
  - `scripts/cli_game.py` can use the LLM to parse free text when `--llm` is supplied.

- **Phase 4 – Additional Tools**
  - A basic `attack` tool allows damaging other actors.
  - A `talk` tool enables simple speech output.
  - A `talk_loud` tool lets actors shout to adjacent locations if passages are open.
  - Item instances now store `current_location`, `owner_id`, `item_state`,
    `inventory` and `tags` fields. The `WorldState` assigns locations to items on
    load and updates ownership when items are grabbed.
  - NPCs now record simple perception events in `short_term_memory` whenever
    actions occur in their location.
  - `cli_game.py` has a `mem` command to inspect the player's recent memories.
  - Combat resolution now follows the ATTACK_ATTEMPT -> ATTACK_HIT/MISSED ->
    DAMAGE_APPLIED event chain with deterministic rules in `rpg/combat_rules.py`.
  - A `drop` tool lets actors place carried items in their current location.
  - A `stats` tool reports an actor's hit points, attributes and skills.
  - `equip` and `unequip` tools let actors manage equipment slots.
  - `look` now reports visible items and other actors in the location.
  - An `analyze` tool reports item details.
  - A `scream` tool lets actors broadcast messages; nearby NPCs record the event in their memories.

## Outstanding Tasks

- Expand the toolset and improve combat handling (Phase 4).
- Implement NPC AI with memory and conversation systems (Phase 5).
- Build polish features such as the narrator, fallback system and tag rules.

