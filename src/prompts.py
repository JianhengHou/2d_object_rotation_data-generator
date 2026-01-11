"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           YOUR TASK PROMPTS                                   ║
║                                                                               ║
║  CUSTOMIZE THIS FILE to define prompts/instructions for your task.            ║
║  Prompts are selected based on task type and returned to the model.           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random
from typing import List


# Simple English prompt template for the rotation task.
# Calling code will pass: objects (list), direction ("clockwise"/"counterclockwise"), degrees (int)
PROMPT_TEMPLATES: List[str] = [
    "The {num_objects} 2D object(s) in the image rotate around their respective centroids at a uniform speed as shown in the diagram.",
]


def get_prompt(objects: list[dict], direction: str, degrees: int) -> str:
    """Return a concise English prompt describing the rotation task."""
    template = random.choice(PROMPT_TEMPLATES)
    num_objects = len(objects)
    return template.format(num_objects=num_objects)


def get_all_prompts() -> List[str]:
    return PROMPT_TEMPLATES
