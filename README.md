# Grid Shift Task Data Generator 🎲

A data generator for creating grid shift reasoning tasks. Generates 6x6 grids with 3 colored blocks that shift 1-2 steps in a random direction (up, down, left, right).

This task generator follows the [template-data-generator](https://github.com/vm-dataset/template-data-generator.git) format and is compatible with [VMEvalKit](https://github.com/Video-Reason/VMEvalKit.git).

Repository: [O_36_grid_shift_data_generator](https://github.com/vm-dataset/O_36_grid_shift_data_generator)

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/vm-dataset/O_36_grid_shift_data_generator.git
cd O_36_grid_shift_data_generator

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# 4. Generate tasks
python examples/generate.py --num-samples 50
```

---

## 📁 Structure

```
grid-shift-task-data-generator/
├── core/                    # ✅ Framework utilities (DO NOT MODIFY)
│   ├── base_generator.py   # Abstract base class
│   ├── schemas.py          # Pydantic models
│   ├── image_utils.py      # Image helpers
│   ├── video_utils.py      # Video generation
│   └── output_writer.py    # File output
├── src/                     # Grid Shift task implementation
│   ├── generator.py        # Grid shift task generator
│   ├── prompts.py          # Grid shift prompt templates
│   └── config.py           # Grid shift configuration
├── examples/
│   └── generate.py         # Entry point
└── data/questions/         # Generated output
```

---

## 📦 Output Format

Every generator produces:

```
data/questions/{domain}_task/{task_id}/
├── first_frame.png          # Initial state (REQUIRED)
├── final_frame.png          # Goal state (or goal.txt)
├── prompt.txt               # Instructions (REQUIRED)
└── ground_truth.mp4         # Solution video (OPTIONAL)
```

---

## 📋 Task Description

The Grid Shift task evaluates spatial reasoning by requiring models to shift all blocks uniformly in a specified direction:

- **Grid**: 6x6 grid
- **Blocks**: 3 colored blocks (same color per task)
- **Movement**: All blocks shift 1-2 steps in a random direction (up, down, left, right)
- **Constraint**: Blocks must remain within grid boundaries

## 🎯 Task Configuration

### Grid Shift Parameters

The task is configured in `src/config.py`:

```python
class TaskConfig(GenerationConfig):
    domain: str = Field(default="grid_shift")
    image_size: tuple[int, int] = Field(default=(512, 512))
    
    # Grid shift specific parameters
    grid_size: int = Field(default=6, description="Size of the grid (6x6)")
    num_blocks: int = Field(default=3, description="Number of blocks to place")
```

### Prompt Templates

Prompts are defined in `src/prompts.py` and automatically format based on direction and steps:

- "Move all blocks {steps} {step_word} to the {direction}."
- "Shift every block {steps} {step_word} {direction}."
- "Translate all blocks {steps} {step_word} toward the {direction}."

## 🚀 Usage

**Generate tasks:**
```bash
python examples/generate.py --num-samples 50
```

**Generate without videos (faster):**
```bash
python examples/generate.py --num-samples 100 --no-videos
```

**With custom output and seed:**
```bash
python examples/generate.py --num-samples 50 --output data/my_output --seed 42
```