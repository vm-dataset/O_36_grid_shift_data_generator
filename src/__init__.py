"""
Grid Shift Task implementation.

This module contains the grid shift task generator:
    - config.py   : Grid shift task configuration (TaskConfig)
    - generator.py: Grid shift task generation logic (TaskGenerator)
    - prompts.py  : Grid shift task prompts/instructions (get_prompt)
"""

from .config import TaskConfig
from .generator import TaskGenerator
from .prompts import get_prompt

__all__ = ["TaskConfig", "TaskGenerator", "get_prompt"]
