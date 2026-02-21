"""
Template Selection System

This module provides functions to select appropriate event templates based on
context parameters. Templates can have metadata indicating compatibility with
specific contexts (e.g., requires_recent_combat, required_spaces).

The selection system filters templates by compatibility and randomly selects
from compatible options, falling back to all templates if none are compatible.
"""

import random
from typing import List, Dict, Any
from event_context import EventContext


def is_compatible(template: Dict[str, Any], context: EventContext) -> bool:
    """
    Check if template is compatible with context.
    
    Templates can specify compatibility requirements:
    - required_spaces: List of space types where template is appropriate
    - requires_recent_combat: Whether template requires recent combat
    - requires_new_area: Whether template requires unfamiliar area
    
    Args:
        template: Event template dictionary with optional metadata
        context: Context parameters
    
    Returns:
        True if template is compatible with context, False otherwise
    """
    # Check space type compatibility
    if 'required_spaces' in template:
        required_spaces = template['required_spaces']
        if context.space_type not in required_spaces:
            return False
    
    # Check combat requirement
    if template.get('requires_recent_combat', False):
        if not context.recent_combat:
            return False
    
    # Check discovery/new area requirement
    if template.get('requires_new_area', False):
        if not context.new_area:
            return False
    
    return True


def select_template(
    templates: List[Dict[str, Any]], 
    context: EventContext,
    floor: int = None
) -> Dict[str, Any]:
    """
    Select appropriate event template based on context and floor.
    
    Filters templates by compatibility with context parameters and floor,
    then randomly selects from compatible options. If no templates are 
    compatible, falls back to random selection from all templates.
    
    Args:
        templates: List of event template dictionaries
        context: Context parameters
        floor: Floor number (1-10). If provided, only returns events for 
               that floor or generic events (floor=0)
    
    Returns:
        Selected event template dictionary
    
    Raises:
        ValueError: If templates list is empty
    """
    if not templates:
        raise ValueError("Cannot select from empty template list")
    
    # Filter by floor first (if specified)
    if floor is not None:
        # Events with floor=0 are generic (appear on all floors)
        # Events with floor=1-10 only appear on that specific floor
        templates = [t for t in templates if t.get('floor', 0) == 0 or t.get('floor', 0) == floor]
    
    # Filter templates by context compatibility
    compatible = [t for t in templates if is_compatible(t, context)]
    
    # Select random compatible template, or fallback to any template
    if compatible:
        return random.choice(compatible)
    else:
        return random.choice(templates) if templates else {'error': 'No templates available'}
