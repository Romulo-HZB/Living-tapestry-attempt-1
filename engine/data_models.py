from dataclasses import dataclass, field
from typing import Dict, List, Optional


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
    known_locations: Dict[str, str] = field(default_factory=dict)
    next_available_tick: int = 0


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
