"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                      GRID SHIFT TASK CONFIGURATION                            ║
║                                                                               ║
║  Configuration for grid shift task generation.                                ║
║  Inherits common settings from core.GenerationConfig                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from pydantic import Field
from core import GenerationConfig


class TaskConfig(GenerationConfig):
    """
    Grid shift task configuration.
    
    Inherited from GenerationConfig:
        - num_samples: int          # Number of samples to generate
        - domain: str               # Task domain name (default: "grid_shift")
        - difficulty: Optional[str] # Difficulty level
        - random_seed: Optional[int] # For reproducibility
        - output_dir: Path          # Where to save outputs
        - image_size: tuple[int, int] # Image dimensions
    """
    
    # ══════════════════════════════════════════════════════════════════════════
    #  OVERRIDE DEFAULTS
    # ══════════════════════════════════════════════════════════════════════════
    
    domain: str = Field(default="grid_shift")
    image_size: tuple[int, int] = Field(default=(512, 512))
    
    # ══════════════════════════════════════════════════════════════════════════
    #  VIDEO SETTINGS
    # ══════════════════════════════════════════════════════════════════════════
    
    generate_videos: bool = Field(
        default=True,
        description="Whether to generate ground truth videos"
    )
    
    video_fps: int = Field(
        default=10,
        description="Video frame rate"
    )
    
    # ══════════════════════════════════════════════════════════════════════════
    #  TASK-SPECIFIC SETTINGS (Random Scaling)
    # ══════════════════════════════════════════════════════════════════════════
    
    # Grid size will be randomly selected from this range for each task
    grid_size_min: int = Field(
        default=4,
        description="Minimum grid size (e.g., 4 for 4x4 grid)"
    )
    
    grid_size_max: int = Field(
        default=12,
        description="Maximum grid size (e.g., 12 for 12x12 grid)"
    )
    
    # Number of blocks will be randomly selected based on grid size
    num_blocks_min: int = Field(
        default=2,
        description="Minimum number of blocks"
    )
    
    # Maximum blocks will be calculated as a fraction of grid size
    num_blocks_max_ratio: float = Field(
        default=0.4,
        description="Maximum blocks as ratio of total grid cells (e.g., 0.4 = 40% of grid)"
    )
    
    # Step size will be randomly selected from this range
    steps_min: int = Field(
        default=1,
        description="Minimum number of steps to move"
    )
    
    steps_max: int = Field(
        default=3,
        description="Maximum number of steps to move (auto-limited by grid size)"
    )
