"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           YOUR TASK PROMPTS                                   ║
║                                                                               ║
║  CUSTOMIZE THIS FILE to define prompts/instructions for your task.            ║
║  Prompts are selected based on task type and returned to the model.           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import random


# ══════════════════════════════════════════════════════════════════════════════
#  DEFINE YOUR PROMPTS
# ══════════════════════════════════════════════════════════════════════════════

PROMPTS = {
    "default": [
        "Animate the chess pieces to show white delivering checkmate in one move. The winning piece should move smoothly to its destination square, capturing if necessary, resulting in the opponent's king being in checkmate.",
        "Show white making the winning move that checkmates black. The piece should move clearly from its starting position to deliver mate, with smooth animation.",
        "Demonstrate white's checkmate in one. Move the attacking piece to its final square, showing the decisive blow that ends the game.",
    ],
    
    "back_rank": [
        "Show the rook or queen delivering a back-rank checkmate. The attacking piece should slide horizontally along the back rank to trap the enemy king.",
        "Animate a classic back-rank mate. The attacking piece moves along the eighth rank to checkmate the trapped king behind its own pawns.",
    ],
    
    "queen_mate": [
        "Show the queen delivering checkmate. The queen should move decisively to its final square, supported by the king, to trap the opponent's king.",
        "Animate the queen administering checkmate. She should glide to her destination, working with the friendly king to corner the enemy monarch.",
    ],
    
    "rook_mate": [
        "Show the rook delivering checkmate. The rook should move cleanly along its file or rank to trap the enemy king.",
        "Animate the rook administering mate. It should slide smoothly to its destination square, cutting off the king's escape.",
    ],
}


def get_prompt(task_type: str = "default") -> str:
    """
    Select a random prompt for the given task type.
    
    Args:
        task_type: Type of task (key in PROMPTS dict)
        
    Returns:
        Random prompt string from the specified type
    """
    prompts = PROMPTS.get(task_type, PROMPTS["default"])
    return random.choice(prompts)


def get_all_prompts(task_type: str = "default") -> list[str]:
    """Get all prompts for a given task type."""
    return PROMPTS.get(task_type, PROMPTS["default"])


# ══════════════════════════════════════════════════════════════════════════════
#  DEFINE YOUR RUBRICS
# ══════════════════════════════════════════════════════════════════════════════
#
# Rubrics are used to evaluate the quality of model outputs.
# 
# Important format requirements:
#   - Use natural language descriptions that align with human intuition
#   - Do NOT use numbered lists (e.g., "1. 2. 3.")
#   - Do NOT include points or percentages (e.g., "1 point", "40%")
#   - Should describe checkpoints like a human evaluator would
#
# Example style:
#   ✓ "Check if the final rotation angle and position match the expected result."
#   ✓ "Verify that the solution correctly identifies the checkmating move."
#   ✓ "Ensure the animation smoothly transitions from initial to final state."
#
#   ✗ "1. Correctness (4 points): ..."
#   ✗ "Award 1 point if counts match, 0 otherwise."
#   ✗ "Move Accuracy (40%): ..."
#
# You can define different rubrics for different task types.
# ══════════════════════════════════════════════════════════════════════════════

RUBRICS = {
    "default": [
        """Check if the solution correctly identifies and executes the checkmating move. Verify that the final position results in a valid checkmate where the opponent's king cannot escape. Ensure the animation shows smooth piece movement from the starting square to the destination, with proper handling of piece capture if applicable. The final board state should clearly show the checkmate position with all pieces visible and correctly positioned.""",
        
        """Verify that the winning move is correctly identified and the piece moves to the right square to deliver checkmate. Check that the animation smoothly transitions from the initial position to the final checkmate position. Ensure the board visualization is clear throughout the animation, making it easy to see the decisive move and the resulting checkmate.""",
        
        """Confirm the solution shows the correct checkmating move with accurate piece positioning. The animation should demonstrate smooth piece movement and clearly show how the move results in checkmate. Check that the final position is a valid checkmate and the board state is clearly visible.""",
    ],
    
    "back_rank": [
        """Check if the solution correctly identifies the back-rank weakness and executes the horizontal checkmating move along the rank. Verify that the attacking piece moves smoothly to trap the enemy king behind its own pawns. Ensure the animation clearly demonstrates the back-rank mate pattern and the final position shows a valid checkmate.""",
        
        """Verify that the solution recognizes the trapped king pattern and performs the correct horizontal move to deliver checkmate. The animation should show smooth piece sliding along the rank, and the final position should clearly demonstrate the back-rank mate concept with the king unable to escape.""",
    ],
    
    "queen_mate": [
        """Check if the queen moves to the correct square to deliver checkmate, with proper coordination with the friendly king. Verify that the animation shows smooth queen movement and the final position demonstrates effective queen-king teamwork in trapping the opponent's king. Ensure the checkmate is valid and clearly visible.""",
        
        """Confirm the solution shows the queen moving decisively to the right position for checkmate, working together with the king. The animation should demonstrate fluid queen movement, and the final position should clearly show how the queen and king cooperate to corner the enemy monarch.""",
    ],
    
    "rook_mate": [
        """Verify that the rook moves correctly along its file or rank to deliver checkmate. Check that the solution demonstrates understanding of rook mating patterns and shows smooth rook sliding to the destination square. Ensure the final position clearly shows the rook cutting off the king's escape and resulting in checkmate.""",
        
        """Check if the solution correctly places the rook to deliver checkmate, showing proper file or rank control. The animation should show smooth rook movement, and the final position should clearly demonstrate how the rook traps the enemy king with a valid checkmate.""",
    ],
}


def get_rubric(task_type: str = "default") -> str:
    """
    Select a random rubric for the given task type.
    
    Args:
        task_type: Type of task (key in RUBRICS dict)
        
    Returns:
        Random rubric string from the specified type
    """
    rubrics = RUBRICS.get(task_type, RUBRICS["default"])
    return random.choice(rubrics)
