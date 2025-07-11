# The Dungeon Guardian: An Autonomous AI Agent

This project implements the **Sentient Guardian**, an intelligent autonomous NPC agent designed to protect a dungeon. It showcases a modern cognitive architecture that combines deterministic, symbolic planning (GOAP) with advanced, LLM-based reasoning for goal setting, justification, and reflection.

The agent operates in a simulated environment where it must manage its health, contend with threats, and protect treasure. It thinks, justifies its actions, creates complex plans, and learns from both its successes and failures.

### Core Features

*   🧠 **Hybrid Cognition:** Employs a unique two-tier thinking process. A fast, local simulator proposes an immediate action, while a strategic LLM (Google Gemini) provides a long-term goal. The agent arbitrates between the two to make the best decision.
*   🛠️ **GOAP Planner:** A robust Goal-Oriented Action Planner using the A* algorithm creates efficient, multi-step plans to achieve the agent's chosen goals.
*   🎮 **Dynamic World Simulation:** The agent acts in a world with non-deterministic outcomes. Actions can fail unexpectedly, forcing the agent to adapt and re-plan.
*   📝 **Learning & Reflection:** The agent learns from experience. A reward system updates action biases based on outcomes. When a plan fails, the agent uses its LLM to reflect on the failure, creating a "lesson learned" to avoid repeating mistakes. It can even detect when it's stuck in a loop and force a change in strategy.

---

## Project Architecture

The agent's logic is separated into distinct layers, each with a clear responsibility.

#### 1. 🧠 Cognitive Layer (`cognitive_layer/`)
The agent's "strategic brain," responsible for high-level reasoning.
*   **`cognitive_engine.py`**: Connects to the Google Gemini API to analyze the world state (informed by the local simulation's proposal) and generate a high-level goal with a natural language justification. It also handles reflection on failures.

#### 2. 🎯 Strategy & Decision Layer (`strategy_layer.py`, `decision_engine.py`)
The agent's "tactical core," responsible for making the final call on what to do next.
*   **`strategy_layer.py`**: Analyzes the world state to determine the agent's current "mood" (e.g., `DESPERATE`, `AGGRESSIVE_DEFENDER`, `STUCK`), which influences its choices.
*   **`decision_engine.py`**: The **Arbiter**. It runs a local simulation to find the best immediate action, then presents this to the `CognitiveEngine`. It makes the final goal decision by comparing the local proposal with the LLM's strategic advice.

#### 3. 🛠️ Planning Layer (`planning_layer/`)
The "tactician" that creates concrete plans.
*   **`action.py`**: Defines the agent's capabilities (e.g., `HealSelf`, `AttackEnemy`). Each action has a cost, preconditions (what must be true to perform it), and effects (how it changes the world).
*   **`goal.py`**: Defines possible objectives (e.g., `Survive`, `ProtectTreasure`) as a set of desired world conditions.
*   **`planner.py`**: Implements the **A* search algorithm** to find the most efficient sequence of actions to achieve a goal.

#### 4. 🎮 Execution & Learning Layer (`execution_layer/`, `learning_layer.py`)
The agent's "body" and "muscle memory."
*   **`world_state.py`**: Manages the agent's understanding of the environment.
*   **`action_executor.py`**: Simulates action execution, including random chances of failure.
*   **`learning_layer.py`**: Calculates a reward for the outcome of a plan and uses it to update `action_biases.json`, allowing the agent to learn which actions are most effective in certain moods.

---

## Getting Started

Follow these instructions to run the Dungeon Guardian simulation on your own machine.

### 1. Prerequisites
*   Python 3.9+
*   Git

### 2. Clone the Repository
git clone https://github.com/AshayMaurya/D_and_D-001.git
cd D_and_D-001