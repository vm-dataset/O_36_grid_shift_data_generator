"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           GRID SHIFT TASK PROMPTS                              ║
║                                                                               ║
║  Prompts for grid shift tasks - blocks moving in a direction.                ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random


# ══════════════════════════════════════════════════════════════════════════════
#  PROMPT TEMPLATES
# ══════════════════════════════════════════════════════════════════════════════

PROMPT_TEMPLATES = [
    """The scene shows a {grid_size}x{grid_size} grid with {num_blocks} {color} square blocks, each with a black outline, positioned at various locations. All blocks must move simultaneously {direction_description} by exactly {steps} {step_word}. Each block shifts one grid cell per step toward the {direction_name}, and all blocks must remain within the grid boundaries throughout the movement. After the movement, all blocks should be positioned exactly {steps} {step_word} {direction_description} from their original positions.""",
    
    """The scene displays a {grid_size}x{grid_size} grid containing {num_blocks} {color} square blocks with black borders, distributed across different cells. Move every block {direction_description} by precisely {steps} {step_word}. All blocks move together at the same time, shifting {steps} grid {cell_word} in the {direction_name} direction, and each block must stay within the grid's boundaries. The final configuration shows all blocks in their new positions, each exactly {steps} {step_word} {direction_description} from where it started.""",
    
    """In the scene, there is a {grid_size}x{grid_size} grid with {num_blocks} {color} square blocks, each outlined in black, placed at different positions. Translate all blocks {direction_description} by exactly {steps} {step_word}, moving simultaneously and uniformly. Each block shifts {steps} {cell_word} toward the {direction_name} direction, and all blocks must remain completely within the grid boundaries. The goal is to achieve a configuration where every block has been moved exactly {steps} {step_word} {direction_description} to reach its final position.""",
]

# Direction descriptions for more natural language
DIRECTION_DESCRIPTIONS = {
    "up": ("upward", "top"),
    "down": ("downward", "bottom"),
    "left": ("leftward", "left"),
    "right": ("rightward", "right"),
}


# ══════════════════════════════════════════════════════════════════════════════
#  PROMPT DICTIONARY (for backward compatibility)
# ══════════════════════════════════════════════════════════════════════════════

PROMPTS = {
    "default": PROMPT_TEMPLATES,
    "grid_shift": PROMPT_TEMPLATES,
}


def get_prompt(task_type: str = "default", task_data: dict = None) -> str:
    """
    Select a prompt for the grid shift task.
    
    Args:
        task_type: Type of task (should be "grid_shift" or "default")
        task_data: Task data dictionary containing direction, steps, grid_size, num_blocks, color, etc.
        
    Returns:
        Formatted prompt string
    """
    if task_data and "direction" in task_data and "steps" in task_data:
        # Format prompt with task-specific values
        template = random.choice(PROMPT_TEMPLATES)
        steps = task_data["steps"]
        step_word = "step" if steps == 1 else "steps"
        cell_word = "cell" if steps == 1 else "cells"
        direction = task_data["direction"]
        
        # Get direction descriptions
        direction_description, direction_name = DIRECTION_DESCRIPTIONS.get(
            direction, ("unknown", "unknown")
        )
        
        # Extract additional task data with defaults
        grid_size = task_data.get("grid_size", 6)
        num_blocks = task_data.get("num_blocks", 3)
        color = task_data.get("color", "colored")
        
        return template.format(
            grid_size=grid_size,
            num_blocks=num_blocks,
            color=color,
            steps=steps,
            step_word=step_word,
            cell_word=cell_word,
            direction=direction,
            direction_description=direction_description,
            direction_name=direction_name
        )
    else:
        # Fallback to default prompts
        prompts = PROMPTS.get(task_type, PROMPTS["default"])
        return random.choice(prompts)


def get_all_prompts(task_type: str = "default") -> list[str]:
    """Get all prompts for a given task type."""
    return PROMPTS.get(task_type, PROMPTS["default"])
