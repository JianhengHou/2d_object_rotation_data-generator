# 2D Object Rotation Data Generator

This generator produces datasets for models that reason about 2D object rotation around geometric centers. Each task shows 1-5 random 2D objects rotating independently around their respective centroids.

## Overview

- Domain: `2d_object_rotation` — multiple objects rotate around their own centroids.
- Goal: Each object rotates by a specified angle (clockwise or counterclockwise) at uniform speed.

## Quick Start

```bash
git clone https://github.com/your-org/2d_object_rotation_data-generator.git
cd 2d_object_rotation_data-generator

python -m pip install -r requirements.txt
pip install -e .

python examples/generate.py --num-samples 10
```

## Output Format

```
data/questions/2d_object_rotation_task/{task_id}/
├── first_frame.png
├── final_frame.png
├── prompt.txt
└── ground_truth.mp4 (optional)
```

## Task Description

- Initial frame (`first_frame.png`): 1-5 random 2D geometric objects (circle, square, triangle, ellipse, or irregular polygon) arranged in a grid layout. Each object is shown with a rotation arc, arrowhead indicating direction, and degree label.
- Prompt (`prompt.txt`): "The {N} 2D object(s) in the image rotate around their respective centroids at a uniform speed as shown in the diagram."
- Final frame (`final_frame.png`): Each object rotated by the specified degrees around its own geometric center.
- Video (`ground_truth.mp4`): Smooth animation showing each object rotating independently around its centroid.
- Title overlay: Large centered text showing rotation direction (Clockwise/Counterclockwise) and angle.

## Randomness Factors

- Number of objects (1-5)
- Object types: circle, square, triangle, ellipse, irregular polygon (4-8 vertices, possibly concave)
- Object size, color, and position within grid cells
- Rotation direction: clockwise or counterclockwise
- Rotation angle: 10-180 degrees
- All objects rotate by the same angle in the same direction

## Configuration

Edit `src/config.py` to control dataset behavior:

- `domain` (default `2d_object_rotation`)
- `image_size` (default `(512, 512)`)
- `generate_videos` (default `True`)
- `video_fps` (default `30`)

Ensure consistent results by passing a fixed `seed`.

## Project Structure

```
2d_object_rotation_data-generator/
├── core/                # framework utilities (do not modify)
├── src/                 # task: generator.py, prompts.py, config.py
├── examples/            # CLI entry point
├── data/questions/      # generated dataset
├── requirements.txt
└── README.md
```

## Implementation Notes

- Objects are arranged in a grid layout (1x1, 2x1, 2x2, or 3x2) to prevent overlap
- Each object rotates around its own geometric center (centroid)
- Rotation uses precise mathematical transformation: `(x', y') = (cx + (x-cx)cos(θ) - (y-cy)sin(θ), cy + (x-cx)sin(θ) + (y-cy)cos(θ))`
- Irregular polygons maintain consistent shape across frames by pre-generating vertices
- Arc visualization shows rotation path with arrowhead indicating direction
- Videos are generated using OpenCV when available (gracefully degrades if not installed)

## License

MIT


Replace chess prompts with yours:

```python
PROMPTS = {
    "default": [
        "Animate a path from start to goal through the maze.",
        "Show the solution route navigating through corridors.",
    ]
}

def get_prompt(task_type: str = "default") -> str:
    prompts = PROMPTS.get(task_type, PROMPTS["default"])
    return random.choice(prompts)
```

### 3. Update `src/config.py`

**All hyperparameters go here** - both general and task-specific:

```python
from core import GenerationConfig
from pydantic import Field

class TaskConfig(GenerationConfig):
    """Your task-specific configuration."""
    # Inherits: num_samples, domain, seed, output_dir, image_size
    
    # Override defaults
    domain: str = Field(default="maze")
    image_size: tuple[int, int] = Field(default=(512, 512))
    
    # Task-specific hyperparameters
    grid_size: int = Field(default=10, description="Maze grid size")
    wall_thickness: int = Field(default=2, description="Wall thickness")
    difficulty: str = Field(default="medium", description="easy/medium/hard")
```

**Single entry point:** `python examples/generate.py --num-samples 50`