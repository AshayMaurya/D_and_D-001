# learning_layer.py

import os
import json
from typing import List, Dict
from config import LEARNING_RATE

BIAS_FILEPATH = 'action_biases.json'

def load_biases() -> Dict:
    """Loads action biases from the JSON file. Returns an empty dict if the file doesn't exist."""
    if not os.path.exists(BIAS_FILEPATH):
        return {}
    try:
        with open(BIAS_FILEPATH, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def save_biases(biases: Dict):
    """Saves the action biases to the JSON file."""
    with open(BIAS_FILEPATH, 'w') as f:
        json.dump(biases, f, indent=4)

def calculate_reward(state_before: Dict, state_after: Dict) -> float:
    """
    Calculates a reward score based on the change between two world states.
    A positive reward is good, a negative reward is bad.
    """
    reward = 0.0

    # Reward/penalize based on health change (most important)
    health_change = state_after.get('health', 0) - state_before.get('health', 0)
    reward += health_change * 1.5

    # Reward for finding potions
    potion_change = state_after.get('potionCount', 0) - state_before.get('potionCount', 0)
    reward += potion_change * 2.0

    # Smaller reward for stamina change
    stamina_change = state_after.get('stamina', 0) - state_before.get('stamina', 0)
    reward += stamina_change * 0.5

    return reward

def update_biases(mood: str, plan: List[str], reward: float):
   
    if not plan: return # Do not learn from empty plans

    biases = load_biases()
    biases.setdefault(mood, {})

    for action_name in plan:
        old_bias = biases[mood].get(action_name, 0.0)
        new_bias = old_bias + (LEARNING_RATE * reward)
        biases[mood][action_name] = round(new_bias, 4) # Round for cleanliness

    save_biases(biases)