import os
import time
from dotenv import load_dotenv

# --- Import Core Components ---
from cognitive_layer.cognitive_engine import CognitiveEngine
from planning_layer.planner import GOAPPlanner
from planning_layer.action import get_available_actions
from planning_layer.goal import get_goal_by_name
from execution_layer.world_state import WorldState
from execution_layer.action_executor import execute_action
from memory import Memory
import config

def run_simulation():
    """
    The main entry point for the Dungeon Guardian agent simulation.
    """
    # --- 1. Initialization ---
    print("Booting up the Sentient Guardian...")

    # Load API Key from .env file
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("FATAL: GEMINI_API_KEY not found in .env file. The agent cannot think. Shutting down.")
        return

    # Initialize agent components
    memory = Memory(filepath='agent_memory.json')
    # cognitive_engine = CognitiveEngine(api_key=api_key, model_name=config.GEMINI_MODEL_NAME)
    cognitive_engine = CognitiveEngine(api_key=api_key)
    planner = GOAPPlanner()
    all_actions = get_available_actions()
    
    # --- Set up the initial scenario ---
    # DESC: Low health, no potion, enemy nearby. Should retreat or call for backup.
    scenario_1 = {
        "health": 20, "enemyNearby": True, "potionCount": 0,
        "treasureThreatLevel": "medium", "stamina": 5, "isInSafeZone": False
    }
    # DESC: Healthy, treasure under high threat. Should be aggressive.
    scenario_2 = {
        "health": 85, "enemyNearby": True, "potionCount": 1,
        "treasureThreatLevel": "high", "stamina": 15, "isInSafeZone": False
    }
    # DESC: Healthy but low stamina, no enemy. Should prepare.
    scenario_3 = {
        "health": 70, "enemyNearby": False, "potionCount": 1,
        "treasureThreatLevel": "low", "stamina": 2, "isInSafeZone": True
    }
    
    # >> CHOOSE YOUR SCENARIO HERE <<
    world_state = WorldState(initial_state=scenario_1)
    
    # You can also clear memory for a fresh run
    # memory.clear_memory()

    max_cycles = 10
    current_cycle = 0

    # --- 2. Main Simulation Loop ---
    while current_cycle < max_cycles:
        current_cycle += 1
        print(f"\n==================== CYCLE {current_cycle} ====================")
        
        # --- PERCEIVE ---
        print("\n--- Current World State ---")
        print(world_state)

        # --- THINK ---
        goal_name, justification = cognitive_engine.generate_goal(world_state, memory)
        
        if not goal_name:
            print("\nAGENT STATUS: Confused. The cognitive engine failed to provide a goal. Waiting for next cycle.")
            time.sleep(2)
            continue
            
        print(f"\n--- Agent's Internal Monologue ---")
        print(f"Goal Justification: \"{justification}\"")
        print(f"Chosen Goal: {goal_name}")

        selected_goal = get_goal_by_name(goal_name)
        if not selected_goal:
            print(f"\nAGENT STATUS: Hallucinating. The cognitive engine chose a goal '{goal_name}' that doesn't exist.")
            time.sleep(2)
            continue

        # --- PLAN ---
        print("\n--- Planning ---")
        plan = planner.find_plan(world_state.state, selected_goal.conditions, all_actions)
        
        if not plan:
            print("Could not find a valid plan to achieve the goal. The agent will reconsider on the next cycle.")
            # Log this as a planning failure
            memory.add_event({
                "type": "failure",
                "reason": f"Could not find a plan for goal '{goal_name}'.",
                "plan": [],
                "world_state": world_state.state
            })
            time.sleep(2)
            continue
            
        plan_names = [action.name for action in plan]
        print(f"Plan Found: {' -> '.join(plan_names)}")

        # --- ACT ---
        print("\n--- Execution ---")
        plan_succeeded = True
        for action in plan:
            if not action.is_achievable(world_state.state):
                print(f"Action '{action.name}' preconditions not met! Aborting plan.")
                plan_succeeded = False
                break

            success, reason = execute_action(action, world_state)
            if not success:
                print(f"Plan failed during execution of '{action.name}'.")
                
                # Log the failure to memory
                memory.add_event({
                    "type": "failure",
                    "reason": f"Action '{action.name}' failed: {reason}",
                    "plan": plan_names,
                    "world_state": world_state.state
                })
                
                # REFLECT on the failure
                reflection = cognitive_engine.reflect_on_failure(world_state, plan_names, reason)
                print("\n--- Agent's Reflection on Failure ---")
                print(f"\"{reflection}\"")

                plan_succeeded = False
                break
            
            # Small delay between actions
            time.sleep(1.5)
        
        if plan_succeeded:
            print("\nAGENT STATUS: Plan executed successfully. The goal has been achieved.")
            break # Exit the loop if the plan was a success

        print("\nAgent will now re-evaluate the situation.")
        time.sleep(3) # Pause before the next cycle

    print("\n==================== SIMULATION END ====================")


if __name__ == "__main__":
    run_simulation()