"""
Event Context Data Model

This module defines the EventContext dataclass used to provide situational
context parameters to the dungeon turn event generator. Context parameters
allow the generator to create events that fit naturally into the current
game state rather than generating generic events.

Context parameters include:
- space_type: The physical environment (hallway, large_room, etc.)
- recent_combat: Whether the party just finished combat
- new_area: Whether the party is exploring an unfamiliar area
- party_status: The party's current condition (healthy, injured, low_resources)
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class EventContext:
    """
    Context parameters for event generation.
    
    Attributes:
        space_type: Type of physical space where event occurs.
            Valid values: "hallway", "large_room", "small_room", "outside",
            "vertical_space", "water", "unknown"
            Default: "unknown"
        
        recent_combat: Whether the party just finished combat.
            When True, allows combat-related events (fleeing enemies, etc.)
            When False, filters out events that assume prior combat.
            Default: False
        
        new_area: Whether the party is exploring an unfamiliar area.
            When True, favors discovery and exploration events.
            When False, reduces discovery-based events.
            Default: True
        
        party_status: Current condition of the party.
            Valid values: "healthy", "injured", "low_resources"
            Affects narrative flavor but not mechanical difficulty.
            Default: "healthy"
    """
    space_type: str = "unknown"
    recent_combat: bool = False
    new_area: bool = True
    party_status: str = "healthy"
    
    def validate(self) -> None:
        """
        Validate context parameters.
        
        Raises:
            ValueError: If space_type or party_status contains invalid value.
        """
        valid_spaces = [
            "hallway",
            "large_room",
            "small_room",
            "outside",
            "vertical_space",
            "water",
            "unknown"
        ]
        valid_statuses = ["healthy", "injured", "low_resources"]
        
        if self.space_type not in valid_spaces:
            raise ValueError(
                f"Invalid space_type: '{self.space_type}'. "
                f"Valid values: {', '.join(valid_spaces)}"
            )
        
        if self.party_status not in valid_statuses:
            raise ValueError(
                f"Invalid party_status: '{self.party_status}'. "
                f"Valid values: {', '.join(valid_statuses)}"
            )
