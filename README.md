# Template Data Generator 🎲

A template for creating synthetic reasoning task data generators. Fork this repository and customize it to generate your own task data (mazes, sudoku, rotations, board games, etc.).

---

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Output Format](#-output-format)
- [Customization Guide](#-customization-guide)
  - [Step 1: Configure Task Parameters](#step-1-configure-task-parameters-srcconfigpy)
  - [Step 2: Implement Generation Logic](#step-2-implement-generation-logic-srcgeneratorpy)
  - [Step 3: Define Prompts](#step-3-define-prompts-srcpromptspy)
  - [Step 4: Define Rubrics](#step-4-define-rubrics)
- [Usage Examples](#-usage-examples)
- [Core Concepts](#-core-concepts)
- [Common Task Types](#-common-task-types)
- [Best Practices](#-best-practices)
- [Troubleshooting](#-troubleshooting)

---

## 🚀 Quick Start

### 1. Clone and Setup Environment

```bash
# Clone the repository
git clone <your-repo-url>
cd template-data-generator-3

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

### 2. Generate Test Data

```bash
# Generate 10 samples (without videos, faster)
python examples/generate.py --num-samples 10 --no-videos

# Generate 100 samples (with videos)
python examples/generate.py --num-samples 100

# Specify output directory and random seed
python examples/generate.py --num-samples 50 --output data/my_output --seed 42
```

### 3. View Generated Results

Generated data will be saved in `data/questions/{domain}_task/` directory, with each task in its own folder.

---

## 📁 Project Structure

```
template-data-generator-3/
├── core/                          # ✅ Core framework code (DO NOT MODIFY)
│   ├── __init__.py               # Export core classes and functions
│   ├── base_generator.py         # Abstract base generator class
│   ├── schemas.py                # Data models (TaskPair)
│   ├── image_utils.py            # Image processing utilities
│   ├── video_utils.py            # Video generation utilities
│   └── output_writer.py          # File output utilities
│
├── src/                           # ⚠️ Your task code (NEEDS CUSTOMIZATION)
│   ├── __init__.py               # Export task-related classes
│   ├── config.py                 # Task configuration (TaskConfig)
│   ├── generator.py             # Task generator (TaskGenerator)
│   └── prompts.py               # Prompt and rubric templates
│
├── examples/
│   └── generate.py               # Data generation entry script
│
├── data/
│   └── questions/                # Generated data output directory
│       └── {domain}_task/
│           └── {task_id}/
│               ├── first_frame.png
│               ├── final_frame.png
│               ├── prompt.txt
│               ├── rubric.txt
│               └── ground_truth.mp4 (optional)
│
├── requirements.txt               # Python dependencies
├── setup.py                       # Package installation configuration
└── README.md                      # This document
```

### File Descriptions

**Core Framework (`core/`)** - Do not modify these files:
- `base_generator.py`: Defines the `BaseGenerator` abstract base class and `GenerationConfig` configuration class
- `schemas.py`: Defines the `TaskPair` data model containing all task information
- `image_utils.py`: Provides image rendering and processing utility functions
- `video_utils.py`: Provides video generation functionality (optional)
- `output_writer.py`: Responsible for saving generated tasks to disk

**Your Task Code (`src/`)** - Needs customization:
- `config.py`: Define your task-specific configuration parameters
- `generator.py`: Implement your task generation logic
- `prompts.py`: Define prompt and rubric templates

---

## 📦 Output Format

Each generated task contains the following files:

```
data/questions/{domain}_task/{task_id}/
├── first_frame.png      # Initial state image (REQUIRED)
├── final_frame.png      # Target state image (OPTIONAL but recommended)
├── prompt.txt           # Task prompt (REQUIRED)
├── rubric.txt           # Scoring rubric (REQUIRED)
└── ground_truth.mp4     # Solution video (OPTIONAL)
```

### File Descriptions

- **`first_frame.png`**: The initial state image of the task. This is the starting point for model reasoning.
- **`final_frame.png`**: The final/target state image of the task. Shows the expected result.
- **`prompt.txt`**: Instruction text for the model, describing what task needs to be completed.
- **`rubric.txt`**: Scoring rubric for evaluating model output quality. Contains detailed evaluation criteria.
- **`ground_truth.mp4`**: (Optional) Animation video showing the transition from initial to final state.

---

## 🎨 Customization Guide

To create your own task generator, you need to modify three files in the `src/` directory. Follow these steps:

### Step 1: Configure Task Parameters (`src/config.py`)

Define your task-specific parameters in the `TaskConfig` class:

```python
from core import GenerationConfig
from pydantic import Field

class TaskConfig(GenerationConfig):
    """Your task configuration"""
    
    # 1. Override defaults
    domain: str = Field(default="maze")  # Task domain name
    image_size: tuple[int, int] = Field(default=(512, 512))  # Image dimensions
    
    # 2. Video settings (optional)
    generate_videos: bool = Field(default=True)
    video_fps: int = Field(default=10)
    
    # 3. Add your task-specific parameters
    grid_size: int = Field(default=10, description="Maze grid size")
    wall_thickness: int = Field(default=2, description="Wall thickness")
    difficulty: str = Field(default="medium", description="Difficulty level")
```

**Inherited attributes** (from `GenerationConfig`):
- `num_samples`: Number of samples to generate
- `random_seed`: Random seed (for reproducibility)
- `output_dir`: Output directory path
- `difficulty`: General difficulty level (optional)

### Step 2: Implement Generation Logic (`src/generator.py`)

Implement the `TaskGenerator` class, inheriting from `BaseGenerator`:

```python
from core import BaseGenerator, TaskPair, ImageRenderer
from .config import TaskConfig
from .prompts import get_prompt, get_rubric

class TaskGenerator(BaseGenerator):
    """Your task generator"""
    
    def __init__(self, config: TaskConfig):
        super().__init__(config)
        self.renderer = ImageRenderer(image_size=config.image_size)
        # Initialize your task-specific resources
    
    def generate_task_pair(self, task_id: str) -> TaskPair:
        """Generate one task pair - this is the core method"""
        
        # 1. Generate task data (problem, solution, etc.)
        task_data = self._generate_task_data()
        
        # 2. Render images
        first_image = self._render_initial_state(task_data)
        final_image = self._render_final_state(task_data)
        
        # 3. Generate video (optional)
        video_path = None
        if self.config.generate_videos:
            video_path = self._generate_video(task_data, task_id)
        
        # 4. Get prompt and rubric
        task_type = task_data.get("type", "default")
        prompt = get_prompt(task_type)
        rubric = get_rubric(task_type)
        
        # 5. Return TaskPair
        return TaskPair(
            task_id=task_id,
            domain=self.config.domain,
            prompt=prompt,
            rubric=rubric,
            first_image=first_image,
            final_image=final_image,
            ground_truth_video=video_path
        )
    
    # Implement your helper methods
    def _generate_task_data(self) -> dict:
        """Generate task data"""
        # Your logic
        pass
    
    def _render_initial_state(self, task_data: dict):
        """Render initial state image"""
        # Your logic
        pass
    
    def _render_final_state(self, task_data: dict):
        """Render final state image"""
        # Your logic
        pass
```

**Key Points**:
- Must implement `generate_task_pair(task_id: str) -> TaskPair`
- Use `ImageRenderer` to create images
- Use `get_prompt()` and `get_rubric()` to get text content
- Video generation is optional

### Step 3: Define Prompts (`src/prompts.py`)

Define your prompt templates in the `PROMPTS` dictionary:

```python
PROMPTS = {
    "default": [
        "Animate a path from start to goal through the maze.",
        "Show the solution route navigating through corridors.",
        "Demonstrate the shortest path from entrance to exit.",
    ],
    
    "easy": [
        "Find and animate the path through this simple maze.",
    ],
    
    "hard": [
        "Navigate through this complex maze, showing the optimal route.",
    ],
}

def get_prompt(task_type: str = "default") -> str:
    """Randomly select a prompt for the given task type"""
    prompts = PROMPTS.get(task_type, PROMPTS["default"])
    return random.choice(prompts)
```

**Tips**:
- You can define different prompts for different task types
- Each type can have multiple variants, the system will randomly select
- Prompts should be clear, specific, and describe what the model needs to do

### Step 4: Define Rubrics

Add the `RUBRICS` dictionary in `src/prompts.py`:

```python
RUBRICS = {
    "default": [
        """Check if the solution correctly finds a path from start to goal. Verify that the path reaches the goal and the animation smoothly shows the route through the maze. Ensure the path is reasonably efficient and the visualization clearly shows both the start and end points.""",
        
        """Verify that the solution identifies a valid path through the maze and reaches the goal. The animation should show smooth path progression, and the final visualization should clearly demonstrate the complete route from entrance to exit.""",
        
        """Confirm the solution shows a correct path that reaches the goal. Check that the animation is smooth and the path visualization is clear and understandable throughout.""",
    ],
    
    "easy": [
        """Check if the solution correctly navigates through the simple maze structure. Verify the path reaches the goal and the animation clearly shows the route.""",
    ],
    
    "hard": [
        """Verify that the solution finds an optimal or near-optimal path through the complex maze. Check that the path correctly reaches the goal, the animation is smooth, and the visualization clearly shows the efficient route taken.""",
    ],
}

def get_rubric(task_type: str = "default") -> str:
    """Randomly select a rubric for the given task type"""
    rubrics = RUBRICS.get(task_type, RUBRICS["default"])
    return random.choice(rubrics)
```

**Rubric Format Requirements**:
- ✅ **Use natural language descriptions** that align with human intuition, describing checkpoints like a human evaluator would
- ✅ **Example style**:
  - "Check if the final rotation angle and position match the expected result."
  - "Verify that the solution correctly identifies the checkmating move."
  - "Ensure the animation smoothly transitions from initial to final state."
- ❌ **Do NOT use**:
  - Numbered lists (e.g., "1. 2. 3.")
  - Points or percentages (e.g., "1 point", "40%", "Award 1 point if...")
  - Structured scoring tables
- You can define different rubrics for different difficulty levels
- Rubrics should be objective and actionable, using natural language to describe what needs to be checked

---

## 💡 Usage Examples

### Basic Usage

```bash
# Generate 50 samples
python examples/generate.py --num-samples 50

# Generate 100 samples, specify output directory
python examples/generate.py --num-samples 100 --output data/my_dataset

# Use random seed for reproducibility
python examples/generate.py --num-samples 50 --seed 42

# Don't generate videos (faster)
python examples/generate.py --num-samples 100 --no-videos
```

### View Help

```bash
python examples/generate.py --help
```

---

## 🧠 Core Concepts

### TaskPair

`TaskPair` is the core data structure for task data, containing:

- `task_id`: Unique task identifier (e.g., `"chess_0001"`)
- `domain`: Task domain (e.g., `"chess"`, `"maze"`)
- `prompt`: Task prompt text
- `rubric`: Scoring rubric text
- `first_image`: Initial state image (PIL Image)
- `final_image`: Final state image (PIL Image, optional)
- `ground_truth_video`: Solution video path (optional)

### BaseGenerator

All task generators inherit from `BaseGenerator`, which provides:

- `generate_dataset()`: Method for batch generating tasks
- `config`: Configuration object
- Random seed management

You only need to implement the `generate_task_pair(task_id: str) -> TaskPair` method.

### ImageRenderer

Utility class for creating and manipulating images:

```python
from core import ImageRenderer

renderer = ImageRenderer(image_size=(512, 512))
img = renderer.create_image()  # Create blank image
# Use PIL for drawing...
```

---

## 🎯 Common Task Types

### 1. Board Games (e.g., Chess)

- Use `python-chess` library to generate legal positions
- Render board and pieces
- Generate move animations

### 2. Mazes

- Use graph algorithms to generate mazes (e.g., depth-first search)
- Find solution paths
- Render maze and path animations

### 3. Sudoku

- Generate sudoku puzzles
- Ensure unique solutions
- Render initial and completed states

### 4. Image Transformations

- Generate original images
- Apply transformations (rotation, scaling, color adjustments, etc.)
- Create transformation animations

### 5. Logical Reasoning

- Generate logical problems
- Create visual representations
- Show reasoning processes

---

## ✨ Best Practices

### 1. Code Organization

- Break complex logic into small methods (e.g., `_generate_task_data()`, `_render_initial_state()`)
- Use type hints to improve code readability
- Add docstrings to explain method purposes

### 2. Configuration Management

- Put all adjustable parameters in `TaskConfig`
- Use meaningful default values
- Add descriptions for parameters

### 3. Prompt Design

- Clear, specific, unambiguous
- Prepare different prompts for different difficulty levels
- Maintain consistent prompt style

### 4. Rubrics

- Use natural language descriptions that align with human intuition, describing checkpoints like a human evaluator would
- Do not use numbered lists or points; use fluent natural language
- Rubrics should cover all important aspects of the task (correctness, quality, visual effects, etc.)
- Rubrics should be objective and actionable, clearly stating what needs to be checked
- Example: Use natural language descriptions starting with "Check if..." or "Verify that..."

### 5. Image Quality

- Use sufficiently high resolution (at least 512x512)
- Ensure text and details are clearly visible
- Maintain consistent visual style

### 6. Reproducibility

- Use random seeds
- Record configuration parameters used
- Save generation scripts and parameters

---

## 🔧 Troubleshooting

### Issue 1: Import Error

**Error**: `ModuleNotFoundError: No module named 'core'`

**Solution**: Ensure the package is installed:
```bash
pip install -e .
```

### Issue 2: Image Generation Failure

**Error**: PIL-related errors

**Solution**: 
- Check if image dimensions are reasonable
- Ensure all images are converted to RGB mode
- Use `ImageRenderer.ensure_rgb()` to ensure correct format

### Issue 3: Video Generation Failure

**Error**: OpenCV or video encoding errors

**Solution**:
- Check if `opencv-python` is installed
- Try using `--no-videos` to skip video generation
- Check if output directory has write permissions

### Issue 4: Out of Memory

**Error**: Out of memory when generating large numbers of samples

**Solution**:
- Reduce `num_samples` and generate in batches
- Use `--no-videos` to reduce memory usage
- Reduce `image_size`

### Issue 5: Task Generation Too Slow

**Solution**:
- Optimize image rendering logic
- Use `--no-videos` to skip video generation
- Consider parallelization (requires additional implementation)

---

## 📝 Checklist

Before starting data generation, ensure:

- [ ] All dependencies are installed (`pip install -r requirements.txt`)
- [ ] Package is installed (`pip install -e .`)
- [ ] Configuration in `src/config.py` is customized
- [ ] Generation logic in `src/generator.py` is implemented
- [ ] Prompts in `src/prompts.py` are defined
- [ ] Rubrics in `src/prompts.py` are defined
- [ ] Tested generating a small number of samples (e.g., 2-5)
- [ ] Verified generated file formats are correct

---

## 🤝 Contributing

If you've improved this template, please submit a Pull Request!

---

## 📄 License

See the `LICENSE` file for details.

---

## 💬 Support

If you have questions, please:
1. Check the troubleshooting section in this document
2. Check comments in the code
3. Review example code (currently chess task)

---

**Happy Generating! 🎉**
