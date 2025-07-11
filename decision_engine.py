# decision_engine.py

from typing import Tuple, Dict
from termcolor import colored

from execution_layer.world_state import WorldState
from memory import Memory
from cognitive_layer.cognitive_engine import CognitiveEngine
from strategy_layer import determine_agent_mood
from learning_layer import load_biases, calculate_reward
from planning_layer.action import get_available_actions

def _get_goal_from_action(action_name: str) -> str:
    """Maps a recommended action back to a high-level goal."""
    if action_name in ["HealSelf", "Rest", "SearchForPotion"]:
        return "PrepareForBattle"
    if action_name in ["AttackEnemy", "CallBackup"]:
        return "EliminateThreat"
    if action_name == "Retreat":
        return "Survive"
    return "ProtectTreasure"

def choose_goal_via_simulation(mood: str, world_state: WorldState, biases: Dict) -> Tuple[str, str, float] | None:
    """
    The 'Master Tactician' brain. It simulates one step into the future for all
    achievable actions and chooses the one with the best predicted outcome.
    """
    current_state_dict = world_state.state
    achievable_actions = [action for action in get_available_actions() if action.is_achievable(current_state_dict)]

    if not achievable_actions:
        return None

    simulation_results = []
    for action in achievable_actions:
        # Simulate the action's effect
        hypothetical_next_state = action.apply(current_state_dict)
        # Calculate the reward for this hypothetical outcome
        reward = calculate_reward(current_state_dict, hypothetical_next_state)
        # Use learned biases as a tie-breaker or small influence
        # A small multiplier ensures simulation reward is more important than old biases
        reward += biases.get(mood, {}).get(action.name, 0.0) * 0.1 
        
        simulation_results.append({"action": action.name, "reward": reward})

    # Sort results to find the best simulated outcome
    simulation_results.sort(key=lambda x: x['reward'], reverse=True)
    best_simulation = simulation_results[0]
    
    # Confidence is no longer the primary mechanism, but we can keep it for logging
    confidence = 1.0 

    goal = _get_goal_from_action(best_simulation["action"])
    justification = (
        f"Local simulation recommends '{goal}' because action '{best_simulation['action']}' "
        f"is predicted to yield the highest immediate reward of {best_simulation['reward']:.2f}."
    )
    
    return goal, justification, confidence

def make_goal_decision(world_state: WorldState, memory: Memory, cognitive_engine: CognitiveEngine) -> Tuple[str, str]:
    """
    The Arbiter. Gets proposals from both the local simulator and the LLM,
    then makes a final, justified decision.
    """
    mood = determine_agent_mood(world_state, memory)
    biases = load_biases()
    
    # --- Path 1: Get the Local Simulation's Proposal ---
    print(colored("--- Running Local Simulation... ---", "yellow"))
    local_proposal = choose_goal_via_simulation(mood, world_state, biases)

    if not local_proposal:
        print(colored("Local simulation found no possible actions. Escalating to LLM.", "red"))
        # Pass None to indicate no local proposal was possible
        return cognitive_engine.generate_goal(world_state, memory, mood, biases, None)

    local_goal, local_justification, _ = local_proposal
    print(colored(f"Local Proposal: Goal '{local_goal}' | Reason: {local_justification}", "green"))
    
    # --- Path 2: Get the LLM's Proposal, informed by the local one ---
    print(colored("--- Consulting LLM Expert... ---", "yellow"))
    llm_goal, llm_justification = cognitive_engine.generate_goal(world_state, memory, mood, biases, local_proposal)

    # --- Path 3: Arbitrate and Decide ---
    # Simple Case: Both models agree on the goal
    if local_goal == llm_goal:
        print(colored("--- Decision: Unanimous. Both models agree. ---", "green", attrs=["bold"]))
        # Use the LLM's more eloquent justification
        return llm_goal, llm_justification
    
    # Complex Case: Disagreement. For now, we will trust the LLM's strategic view.
    # A more advanced version could use a third LLM call to resolve the conflict.
    print(colored("--- Decision: Disagreement. Prioritizing LLM's strategic insight. ---", "cyan", attrs=["bold"]))
    final_justification = (
        f"There was a disagreement. My local simulation suggested '{local_goal}', but the "
        f"LLM provided a compelling strategic reason for '{llm_goal}'. I will follow the LLM's advice: \"{llm_justification}\""
    )
    return llm_goal, final_justification