"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           GRID SHIFT TASK GENERATOR                           ║
║                                                                               ║
║  Generates grid shift tasks: 6x6 grid with 3 blocks that shift 1-2 steps     ║
║  in a random direction (up, down, left, right).                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random
import tempfile
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from PIL import Image, ImageDraw

from core import BaseGenerator, TaskPair, ImageRenderer
from core.video_utils import VideoGenerator
from .config import TaskConfig
from .prompts import get_prompt

# Grid Shift Task Constants
DIRECTIONS = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
}
COLORS = ["red", "green", "blue", "yellow", "orange", "purple"]


class TaskGenerator(BaseGenerator):
    """
    Grid Shift Task Generator with full randomization.
    
    Each task randomly selects:
    - Grid size (from grid_size_min to grid_size_max)
    - Number of blocks (from num_blocks_min to max based on grid size)
    - Movement steps (from steps_min to steps_max, limited by grid size)
    - Direction (up, down, left, right)
    - Color (from available colors)
    - Initial positions (valid positions within grid)
    
    Supports generating millions of unique tasks.
    """
    
    def __init__(self, config: TaskConfig):
        super().__init__(config)
        self.renderer = ImageRenderer(image_size=config.image_size)
        
        # Initialize video generator if enabled (using mp4 format)
        self.video_generator = None
        if config.generate_videos and VideoGenerator.is_available():
            self.video_generator = VideoGenerator(fps=config.video_fps, output_format="mp4")
        
        # Store config for random scaling
        self.grid_size_min = config.grid_size_min
        self.grid_size_max = config.grid_size_max
        self.num_blocks_min = config.num_blocks_min
        self.num_blocks_max_ratio = config.num_blocks_max_ratio
        self.steps_min = config.steps_min
        self.steps_max = config.steps_max
    
    def generate_task_pair(self, task_id: str) -> TaskPair:
        """Generate one grid shift task pair."""
        
        # Generate task data
        task_data = self._generate_task_data()
        
        # Render images
        first_image = self._render_initial_state(task_data)
        final_image = self._render_final_state(task_data)
        
        # Generate video (optional)
        video_path = None
        if self.config.generate_videos and self.video_generator:
            video_path = self._generate_video(first_image, final_image, task_id, task_data)
        
        # Select prompt
        prompt = get_prompt(task_data.get("type", "default"), task_data)
        
        return TaskPair(
            task_id=task_id,
            domain=self.config.domain,
            prompt=prompt,
            first_image=first_image,
            final_image=final_image,
            ground_truth_video=video_path
        )
    
    # ══════════════════════════════════════════════════════════════════════════
    #  TASK-SPECIFIC METHODS
    # ══════════════════════════════════════════════════════════════════════════
    
    def _generate_task_data(self) -> dict:
        """Generate grid shift task data with fully randomized parameters."""
        max_attempts = 100  # Limit retry attempts to avoid infinite loops
        
        for attempt in range(max_attempts):
            # 1. Randomly select grid size
            grid_size = random.randint(self.grid_size_min, self.grid_size_max)
            
            # 2. Randomly select number of blocks (limited by grid size)
            max_blocks_by_size = max(
                self.num_blocks_min,
                int(grid_size * grid_size * self.num_blocks_max_ratio)
            )
            num_blocks = random.randint(
                self.num_blocks_min,
                min(max_blocks_by_size, grid_size * grid_size - 1)  # Leave at least 1 empty cell
            )
            
            # 3. Randomly select direction and color
            direction = random.choice(list(DIRECTIONS.keys()))
            color = random.choice(COLORS)
            
            # 4. Randomly select steps (limited by grid size and direction)
            # Maximum steps cannot exceed grid_size - 1 (to ensure valid positions exist)
            max_valid_steps = min(self.steps_max, grid_size - 2)  # Leave room for blocks
            if max_valid_steps < self.steps_min:
                max_valid_steps = self.steps_min
            
            steps = random.randint(self.steps_min, max_valid_steps)
            
            # 5. Get valid starting positions (positions that won't go out of bounds)
            valid_positions = self._get_valid_positions(grid_size, direction, steps)
            
            # 6. Check if we have enough valid positions
            if len(valid_positions) < num_blocks:
                # Try again with different parameters
                continue
            
            # 7. Randomly sample positions
            positions = random.sample(valid_positions, num_blocks)
            
            # 8. Calculate shifted positions
            dr, dc = DIRECTIONS[direction]
            shifted_positions = [(r + dr * steps, c + dc * steps) for r, c in positions]
            
            # 9. Determine difficulty based on multiple factors
            difficulty = self._calculate_difficulty(grid_size, num_blocks, steps)
            
            return {
                "type": "grid_shift",
                "grid_size": grid_size,
                "num_blocks": num_blocks,
                "color": color,
                "direction": direction,
                "steps": steps,
                "positions": positions,
                "shifted_positions": shifted_positions,
                "difficulty": difficulty,
            }
        
        # If we exhausted attempts, fall back to safe defaults
        raise ValueError(
            f"Could not generate valid task after {max_attempts} attempts. "
            f"Try adjusting grid_size or num_blocks ranges."
        )
    
    def _calculate_difficulty(self, grid_size: int, num_blocks: int, steps: int) -> str:
        """Calculate difficulty level based on task parameters."""
        # Simple difficulty scoring
        score = 0
        
        # Larger grid = harder
        if grid_size >= 10:
            score += 2
        elif grid_size >= 8:
            score += 1
        
        # More blocks = harder
        if num_blocks >= 5:
            score += 2
        elif num_blocks >= 4:
            score += 1
        
        # More steps = harder
        if steps >= 3:
            score += 2
        elif steps >= 2:
            score += 1
        
        if score <= 1:
            return "easy"
        elif score <= 3:
            return "medium"
        elif score <= 5:
            return "hard"
        else:
            return "expert"
    
    def _get_valid_positions(self, grid_size: int, direction: str, steps: int) -> List[Tuple[int, int]]:
        """Get valid starting positions that won't go out of bounds when shifted."""
        dr, dc = DIRECTIONS[direction]
        
        # Calculate valid row range
        if dr == -1:  # up
            row_range = range(steps, grid_size)
        elif dr == 1:  # down
            row_range = range(0, grid_size - steps)
        else:
            row_range = range(0, grid_size)
        
        # Calculate valid column range
        if dc == -1:  # left
            col_range = range(steps, grid_size)
        elif dc == 1:  # right
            col_range = range(0, grid_size - steps)
        else:
            col_range = range(0, grid_size)
        
        return [(r, c) for r in row_range for c in col_range]
    
    def _render_initial_state(self, task_data: dict) -> Image.Image:
        """Render initial grid state with blocks."""
        return self._render_grid(
            task_data["positions"], 
            task_data["color"],
            task_data["grid_size"]
        )
    
    def _render_final_state(self, task_data: dict) -> Image.Image:
        """Render final grid state with shifted blocks."""
        return self._render_grid(
            task_data["shifted_positions"], 
            task_data["color"],
            task_data["grid_size"]
        )
    
    def _generate_video(
        self,
        first_image: Image.Image,
        final_image: Image.Image,
        task_id: str,
        task_data: dict
    ) -> str:
        """Generate ground truth video with blocks sliding smoothly."""
        temp_dir = Path(tempfile.gettempdir()) / f"{self.config.domain}_videos"
        temp_dir.mkdir(parents=True, exist_ok=True)
        video_path = temp_dir / f"{task_id}_ground_truth.mp4"
        
        # Create animation frames with blocks sliding
        frames = self._create_grid_shift_animation_frames(task_data)
        
        result = self.video_generator.create_video_from_frames(
            frames,
            video_path
        )
        
        return str(result) if result else None
    
    def _create_grid_shift_animation_frames(
        self,
        task_data: dict,
        hold_frames: int = 5,
        transition_frames: int = 25
    ) -> list:
        """
        Create animation frames where all blocks slide smoothly from start to end positions.
        
        All blocks move together in the same direction with the same speed.
        """
        frames = []
        positions = task_data["positions"]
        shifted_positions = task_data["shifted_positions"]
        color = task_data["color"]
        
        grid_size = task_data["grid_size"]
        
        # Hold initial position
        first_frame = self._render_grid(positions, color, grid_size)
        for _ in range(hold_frames):
            frames.append(first_frame)
        
        # Create transition frames with blocks sliding
        image_size = self.config.image_size[0]
        cell_size = image_size / grid_size
        
        for i in range(transition_frames):
            progress = i / (transition_frames - 1) if transition_frames > 1 else 1.0
            
            # Interpolate positions for each block
            intermediate_positions = []
            for (r1, c1), (r2, c2) in zip(positions, shifted_positions):
                r = r1 + (r2 - r1) * progress
                c = c1 + (c2 - c1) * progress
                intermediate_positions.append((r, c))
            
            # Render frame with blocks at intermediate positions
            frame = self._render_grid(intermediate_positions, color, grid_size)
            frames.append(frame)
        
        # Hold final position
        final_frame = self._render_grid(shifted_positions, color, grid_size)
        for _ in range(hold_frames):
            frames.append(final_frame)
        
        return frames
    
    # ══════════════════════════════════════════════════════════════════════════
    #  GRID RENDERING
    # ══════════════════════════════════════════════════════════════════════════
    
    def _render_grid(self, positions: List[Tuple[float, float]], color: str, grid_size: int) -> Image.Image:
        """
        Render a grid with blocks at specified positions.
        
        Args:
            positions: List of (row, col) tuples (can be float for animation)
            color: Color name (e.g., "red", "blue")
            grid_size: Size of the grid (e.g., 6 for 6x6)
        """
        image_size = self.config.image_size[0]
        cell_size = image_size / grid_size
        
        # Create image with white background
        img = Image.new("RGB", (image_size, image_size), color="white")
        draw = ImageDraw.Draw(img)
        
        # Draw grid lines
        grid_color = (51, 51, 51)  # Dark gray
        for i in range(grid_size + 1):
            x = int(i * cell_size)
            draw.line([(x, 0), (x, image_size)], fill=grid_color, width=1)
            draw.line([(0, x), (image_size, x)], fill=grid_color, width=1)
        
        # Color mapping
        color_map = {
            "red": (220, 53, 69),
            "green": (40, 167, 69),
            "blue": (0, 123, 255),
            "yellow": (255, 193, 7),
            "orange": (255, 152, 0),
            "purple": (108, 117, 125),
        }
        block_color = color_map.get(color.lower(), (0, 123, 255))  # Default to blue
        
        # Draw blocks
        padding = 0.08  # Padding inside each cell (8% of cell size)
        block_size = cell_size * (1 - 2 * padding)
        
        for row, col in positions:
            # Convert grid coordinates to pixel coordinates
            # Note: row 0 is at the top, row increases downward
            x = col * cell_size + cell_size * padding
            y = row * cell_size + cell_size * padding
            
            # Draw block with black border
            x0, y0 = int(x), int(y)
            x1, y1 = int(x + block_size), int(y + block_size)
            
            # Draw block
            draw.rectangle(
                [(x0, y0), (x1, y1)],
                fill=block_color,
                outline=(0, 0, 0),
                width=2
            )
        
        return img
