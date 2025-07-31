from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class NPC:
    id: str
    name: str
    inventory: List[str] = field(default_factory=list)
    slots: Dict[str, Optional[str]] = field(default_factory=dict)
    hp: int = 0
    memories: List[dict] = field(default_factory=list)
    goals: List[dict] = field(default_factory=list)
    relationships: Dict[str, str] = field(default_factory=dict)
    tags: Dict[str, List[str]] = field(default_factory=lambda: {"inherent": [], "dynamic": []})
    short_term_memory: List[dict] = field(default_factory=list)
    known_locations: Dict[str, str] = field(default_factory=dict)
    next_available_tick: int = 0
    attributes: Dict[str, int] = field(
        default_factory=lambda: {"strength": 10, "dexterity": 10, "constitution": 10}
    )
    skills: Dict[str, str] = field(default_factory=dict)


@dataclass
class LocationStatic:
    id: str
    description: str
    tags: Dict[str, List[str]] = field(default_factory=lambda: {"inherent": []})
    hex_connections: Dict[str, str] = field(default_factory=dict)


@dataclass
class LocationState:
    id: str
    occupants: List[str] = field(default_factory=list)
    items: List[str] = field(default_factory=list)
    sublocations: List[str] = field(default_factory=list)
    transient_effects: List[str] = field(default_factory=list)
    connections_state: Dict[str, dict] = field(default_factory=dict)

@dataclass
class ItemBlueprint:
    id: str
    name: str
    weight: int = 0
    damage_dice: str = "1d4"
    damage_type: str = "bludgeoning"
    armour_rating: int = 0
    skill_tag: str = "unarmed_combat"
    properties: List[str] = field(default_factory=list)

@dataclass
class ItemInstance:
    id: str
    blueprint_id: str
    current_location: Optional[str] = None
    owner_id: Optional[str] = None
    item_state: Dict[str, Any] = field(default_factory=dict)
    inventory: List[str] = field(default_factory=list)
    tags: Dict[str, List[str]] = field(default_factory=lambda: {"inherent": [], "dynamic": []})
