#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    GRID SHIFT TASK GENERATION SCRIPT                         ║
║                                                                               ║
║  Run this to generate grid shift task datasets with fully randomized params.  ║
║  Generates tasks with random grid sizes, block counts, and steps.             ║
╚══════════════════════════════════════════════════════════════════════════════╝

Usage:
    python examples/generate.py --num-samples 100
    python examples/generate.py --num-samples 100 --output data/my_task --seed 42
    python examples/generate.py --num-samples 50 --no-videos
    python examples/generate.py --num-samples 1000 --grid-min 4 --grid-max 10 --steps-max 4
"""

import argparse
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import OutputWriter
from src import TaskGenerator, TaskConfig


def main():
    parser = argparse.ArgumentParser(
        description="Generate grid shift task dataset with fully randomized parameters",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Generate 100 tasks with default random scaling
    python examples/generate.py --num-samples 100
    
    # Generate 10000 tasks without videos (faster for large scale)
    python examples/generate.py --num-samples 10000 --no-videos
    
    # Customize random ranges
    python examples/generate.py --num-samples 1000 --grid-min 4 --grid-max 10 --steps-max 4
    
    # Generate millions with seed for reproducibility
    python examples/generate.py --num-samples 100000 --seed 42 --no-videos
        """
    )
    parser.add_argument(
        "--num-samples",
        type=int,
        required=True,
        help="Number of task samples to generate (supports millions)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/questions",
        help="Output directory (default: data/questions)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility"
    )
    parser.add_argument(
        "--no-videos",
        action="store_true",
        help="Disable video generation (much faster for large scale generation)"
    )
    
    # Random scaling parameters
    parser.add_argument(
        "--grid-min",
        type=int,
        default=4,
        help="Minimum grid size (default: 4)"
    )
    parser.add_argument(
        "--grid-max",
        type=int,
        default=12,
        help="Maximum grid size (default: 12)"
    )
    parser.add_argument(
        "--blocks-min",
        type=int,
        default=2,
        help="Minimum number of blocks (default: 2)"
    )
    parser.add_argument(
        "--blocks-max-ratio",
        type=float,
        default=0.4,
        help="Maximum blocks as ratio of grid cells (default: 0.4 = 40%%)"
    )
    parser.add_argument(
        "--steps-min",
        type=int,
        default=1,
        help="Minimum movement steps (default: 1)"
    )
    parser.add_argument(
        "--steps-max",
        type=int,
        default=3,
        help="Maximum movement steps (default: 3, auto-limited by grid size)"
    )
    
    args = parser.parse_args()
    
    print(f"🎲 Generating {args.num_samples:,} grid shift tasks with fully randomized parameters...")
    print(f"   Grid size range: {args.grid_min}x{args.grid_min} to {args.grid_max}x{args.grid_max}")
    print(f"   Blocks range: {args.blocks_min} to ~{int(args.grid_max * args.grid_max * args.blocks_max_ratio)}")
    print(f"   Steps range: {args.steps_min} to {args.steps_max}")
    print(f"   Videos: {'Enabled' if not args.no_videos else 'Disabled (faster)'}")
    print()
    
    # ──────────────────────────────────────────────────────────────────────────
    #  Configure grid shift task with random scaling
    # ──────────────────────────────────────────────────────────────────────────
    
    config = TaskConfig(
        num_samples=args.num_samples,
        random_seed=args.seed,
        output_dir=Path(args.output),
        generate_videos=not args.no_videos,
        grid_size_min=args.grid_min,
        grid_size_max=args.grid_max,
        num_blocks_min=args.blocks_min,
        num_blocks_max_ratio=args.blocks_max_ratio,
        steps_min=args.steps_min,
        steps_max=args.steps_max,
    )
    
    # Generate tasks
    generator = TaskGenerator(config)
    tasks = generator.generate_dataset()
    
    # Write to disk
    writer = OutputWriter(Path(args.output))
    writer.write_dataset(tasks)
    
    print()
    print(f"✅ Done! Generated {len(tasks):,} unique tasks in {args.output}/{config.domain}_task/")
    print(f"   Each task has randomized: grid size, block count, steps, direction, color, and positions.")
    print(f"   Prompts contain 50-100 words with detailed instructions.")


if __name__ == "__main__":
    main()
