# execution_layer/action_executor.py

import random
from planning_layer.action import Action
from execution_layer.world_state import WorldState
from config import HEAL_AMOUNT, ATTACK_STAMINA_COST

def execute_action(action: Action, world_state: WorldState) -> tuple[bool, str]:
    """
    Simulates executing an action in the world. Updates the world_state on success.

    Args:
        action (Action): The action to be executed.
        world_state (WorldState): The current state of the world.

    Returns:
        A tuple of (success_boolean, reason_string).
    """
    print(f"--- Executing Action: {action.name} ---")

    success = False
    reason = ""

    if action.name == "HealSelf":
        if random.random() < 0.05:
            success = False
            reason = "The potion was spoiled and had no effect!"
            world_state.apply_effects({"potionCount": ('-', 1)})
        else:
            success = True
            reason = f"Successfully healed for {HEAL_AMOUNT} health."
            world_state.apply_effects(action.effects)

    elif action.name == "AttackEnemy":
        # --- NEW, EXPLICIT FIX FOR THE LINTER WARNING ---
        # 1. Get the stamina value into a variable.
        current_stamina = world_state.get("stamina")

        # 2. Explicitly check if the value is None OR if it's too low.
        #    This pattern is extremely clear to static analyzers.
        if current_stamina is None or current_stamina < ATTACK_STAMINA_COST:
            success = False
            reason = f"Not enough stamina to attack. (Stamina: {current_stamina})"
        elif random.random() < 0.2:
            success = False
            reason = "The attack missed the enemy."
            world_state.apply_effects({"stamina": ('-', ATTACK_STAMINA_COST)})
        else:
            success = True
            reason = "The attack successfully hit the enemy."
            world_state.apply_effects(action.effects)
        # --- END OF FIX ---

    elif action.name == "Retreat":
        if world_state.get("enemyNearby", False) and random.random() < 0.25:
             success = False
             reason = "Failed to retreat; the enemy blocked the path."
        else:
            success = True
            reason = "Successfully retreated to a safe zone."
            world_state.apply_effects(action.effects)

    elif action.name == "DefendTreasure":
        success = True
        reason = "Moved to a defensive position near the treasure."
        world_state.apply_effects(action.effects)

    elif action.name == "CallBackup":
        if random.random() < 0.3:
            success = False
            reason = "Called for backup, but no one responded."
        else:
            success = True
            reason = "Backup has been called and is on the way."
            world_state.apply_effects(action.effects)
            
    elif action.name == "SearchForPotion":
        if random.random() < 0.5:
            success = True
            reason = "Found a healing potion!"
            world_state.apply_effects(action.effects)
        else:
            success = False
            reason = "Searched the area but found no potions."

    if success:
        print(f"ACTION SUCCEEDED: {reason}")
    else:
        print(f"ACTION FAILED: {reason}")
        
    return success, reason