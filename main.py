# main.py

import os
import time
from dotenv import load_dotenv
from termcolor import colored

from cognitive_layer.cognitive_engine import CognitiveEngine
from planning_layer.planner import GOAPPlanner
from planning_layer.action import get_available_actions
from planning_layer.goal import get_goal_by_name
from execution_layer.action_executor import execute_action
from execution_layer.world_state import WorldState
from memory import Memory
import config
# --- FIX: Corrected import statement to include 'determine_agent_mood' ---
from strategy_layer import get_scenario_world_state, determine_agent_mood
from decision_engine import make_goal_decision
from learning_layer import calculate_reward, update_biases

def run_simulation():
    """
    The main entry point for the Dungeon Guardian agent simulation.
    """
    print("Booting up the Sentient Guardian...")
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print(colored("FATAL: GEMINI_API_KEY not found. Shutting down.", "red"))
        return

    memory = Memory(filepath='agent_memory.json')
    cognitive_engine = CognitiveEngine(api_key=api_key)
    planner = GOAPPlanner()
    
    # >> CHOOSE YOUR SCENARIO HERE BY CHANGING THE ID <<
    world_state = get_scenario_world_state(scenario_id=4)
    
    max_cycles = 10
    current_cycle = 0

    while current_cycle < max_cycles:
        current_cycle += 1
        print(colored(f"\n==================== CYCLE {current_cycle} ====================", "white", "on_blue"))
        
        state_before = world_state.state.copy()
        print("\n--- Current World State ---")
        print(world_state)

        # --- STEP 1: DECIDE ---
        goal_name, justification = make_goal_decision(world_state, memory, cognitive_engine)
        
        if not goal_name:
            print(colored("\nAGENT STATUS: Confused. The decision engine failed to provide a goal.", "red"))
            time.sleep(2)
            continue

        print("\n--- Agent's Internal Monologue ---")
        print(colored(f"Goal Justification: \"{justification}\"", "cyan"))
        print(colored(f"Chosen Goal: {goal_name}", "cyan", attrs=["bold"]))

        selected_goal = get_goal_by_name(goal_name)
        if not selected_goal:
            print(colored(f"\nAGENT STATUS: Goal '{goal_name}' is invalid.", "red"))
            continue

        # --- STEP 2: PLAN ---
        print("\n--- Planning ---")
        plan = planner.find_plan(world_state.state, selected_goal.conditions, get_available_actions())
        
        if not plan:
            print(colored("Could not find a valid plan to achieve the goal. The agent will reconsider.", "red"))
            memory.add_event({
                "type": "failure",
                "reason": f"Could not find a plan for goal '{goal_name}'.",
                "plan": [], "world_state": world_state.state
            })
            time.sleep(2)
            continue
            
        plan_names = [action.name for action in plan]
        print(colored(f"Plan Found: {' -> '.join(plan_names)}", "magenta", attrs=["bold"]))

        # --- STEP 3: ACT ---
        print("\n--- Execution ---")
        plan_succeeded = True
        for action in plan:
            success, reason = execute_action(action, world_state)
            if not success:
                # --- FIX: Restored full error handling and reflection logic ---
                print(colored(f"Plan failed during execution of '{action.name}'.", "red"))
                memory.add_event({
                    "type": "failure", "reason": f"Action '{action.name}' failed: {reason}",
                    "plan": plan_names, "world_state": world_state.state
                })
                plan_succeeded = False
                break # Stop executing the rest of the plan
            time.sleep(1)
        
        # --- STEP 4: LEARN & REFLECT ---
        print("\n--- Learning & Reflection ---")
        reward = calculate_reward(state_before, world_state.state)
        # We need the mood here to correctly categorize the learned experience
        mood = determine_agent_mood(world_state, memory)
        update_biases(mood, plan_names, reward)
        print(colored(f"Outcome analysis complete. Calculated reward: {reward:.2f}", "yellow"))
        
        # Only reflect on failure if an LLM call is available (to save quota)
        if not plan_succeeded:
            reflection = cognitive_engine.reflect_on_failure(world_state, plan_names, "Action failed during execution")
            print(colored(f"\"{reflection}\"", "red"))

        if plan_succeeded:
            print(colored("\nAGENT STATUS: Plan executed successfully. Goal achieved.", "green"))
            break # End simulation on success
        
        print("\nAgent will now re-evaluate the situation.")
        time.sleep(3)

    print(colored("\n==================== SIMULATION END ====================", "white", "on_blue"))

if __name__ == "__main__":
    run_simulation()