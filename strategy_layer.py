# strategy_layer.py

from typing import List
from execution_layer.world_state import WorldState
from memory import Memory
import config

# --- 1. Scenario Definitions (Unchanged) ---
SCENARIOS = {
    1: {
        "description": "Low Health, No Potions, Enemy Nearby.",
        "state": {
            "health": 20, "enemyNearby": True, "potionCount": 0,
            "treasureThreatLevel": "medium", "stamina": 5, "isInSafeZone": False
        }
    },
    2: {
        "description": "Healthy, Treasure Under High Threat, Enemy Nearby.",
        "state": {
            "health": 85, "enemyNearby": True, "potionCount": 1,
            "treasureThreatLevel": "high", "stamina": 15, "isInSafeZone": False
        }
    },
    3: {
        "description": "No Enemy, Low Stamina, Potion Available.",
        "state": {
            "health": 70, "enemyNearby": False, "potionCount": 1,
            "treasureThreatLevel": "low", "stamina": 2, "isInSafeZone": True
        }
    },
    4: {
        "description": "Out of Potions, Moderate Health, Enemy Near.",
        "state": {
            "health": 60, "enemyNearby": True, "potionCount": 0,
            "treasureThreatLevel": "low", "stamina": 10, "isInSafeZone": False
        }
    }
}

def get_scenario_world_state(scenario_id: int) -> WorldState:
    """
    Initializes a WorldState object based on a predefined scenario ID.
    """
    scenario = SCENARIOS.get(scenario_id)
    if not scenario:
        print(f"WARNING: Scenario ID {scenario_id} not found. Using default world state.")
        return WorldState()
    
    print(f"--- Loading Scenario {scenario_id}: {scenario['description']} ---")
    return WorldState(initial_state=scenario['state'])

# --- 2. ROBUST Mood Determination ---
def determine_agent_mood(world_state: WorldState, memory: Memory) -> str:
    """
    Analyzes the world state and memory to determine a strategic mood.
    This version uses explicit 'is not None' checks to satisfy linters.
    """
    health = world_state.get("health")
    potion_count = world_state.get("potionCount")
    enemy_is_near = world_state.get("enemyNearby")
    stamina = world_state.get("stamina")
    treasure_threat = world_state.get("treasureThreatLevel")

    recent_failures = memory.get_recent_failures(n=2)
    if len(recent_failures) == 2 and recent_failures[0].get('reason') == recent_failures[1].get('reason'):
        return "STUCK"

    # --- FIX: Explicitly check that values are not None before comparing ---
    if health is not None and health < config.LOW_HEALTH_THRESHOLD:
        if enemy_is_near and (potion_count is not None and potion_count == 0):
            return "DESPERATE"

    if treasure_threat == "high":
        return "AGGRESSIVE_DEFENDER"

    is_not_full_health = health is not None and health < 100
    is_not_full_stamina = stamina is not None and stamina < 20
    if not enemy_is_near and (is_not_full_health or is_not_full_stamina):
        return "PREPARING"
    
    return "PATROLLING"

# --- 3. DYNAMIC Advice Generation ---
def generate_dynamic_advice(mood: str, world_state: WorldState) -> str:
    """
    Generates a string of dynamic advice for the LLM based on the mood and current stats.
    """
    advice_parts: List[str] = []
    health = world_state.get("health")
    potion_count = world_state.get("potionCount")
    stamina = world_state.get("stamina")
    
    if mood == "DESPERATE":
        advice_parts.append("My situation is dire.")
        if health is not None: advice_parts.append(f"My health is critically low at {health}.")
        if potion_count == 0: advice_parts.append("I have no potions.")
        advice_parts.append("A direct confrontation is likely fatal. Unconventional tactics are required. Perhaps protecting the treasure via 'CallBackup' could save me.")
    
    elif mood == "STUCK":
        advice_parts.append("My previous strategy has failed repeatedly. I must think differently and choose a new, achievable goal to break this loop.")
        
    elif mood == "AGGRESSIVE_DEFENDER":
        advice_parts.append("The treasure is under maximum threat! I must act decisively and aggressively to eliminate the danger immediately.")
        
    elif mood == "PREPARING":
        advice_parts.append("There is no immediate danger.")
        if health is not None and health < 100: advice_parts.append(f"My health ({health}) is not full.")
        if stamina is not None and stamina < 20: advice_parts.append("I am low on stamina.")
        advice_parts.append("This is a chance to recover and prepare for the next battle.")
        
    elif mood == "PATROLLING":
        advice_parts.append("The situation is stable. I will remain vigilant and patrol the area.")

    return " ".join(advice_parts)