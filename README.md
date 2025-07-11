# 🛡️ The Dungeon Guardian: An Autonomous AI Agent

This project implements the **Sentient Guardian**, an intelligent autonomous NPC agent designed to protect a dungeon. It showcases a modern cognitive architecture that combines deterministic, symbolic planning (**GOAP**) with advanced, LLM-based reasoning for goal setting, justification, and reflection.

The agent operates in a simulated environment where it must manage its health, contend with threats, and protect treasure. It thinks, justifies its actions, creates complex plans, and learns from both its successes and failures.

---

## ✨ Core Features

- 🧠 **Hybrid Cognition:** Fast, local simulation + long-term LLM strategic advice (Google Gemini).
- 🛠️ **GOAP Planner:** A* algorithm for efficient, multi-step action planning.
- 🎮 **Dynamic World Simulation:** Non-deterministic outcomes and real-time replanning.
- 📝 **Learning & Reflection:** Adaptive behavior via reward system and failure reflection.

---

## 🧱 Project Architecture

The agent's logic is modular and layered:

### 1. 🧠 Cognitive Layer (`cognitive_layer/`)
The agent’s “strategic brain”:
- `cognitive_engine.py`: Interfaces with Google Gemini to determine high-level goals and reflect on failures.

### 2. 🎯 Strategy & Decision Layer (`strategy_layer.py`, `decision_engine.py`)
The agent’s “tactical core”:
- `strategy_layer.py`: Determines the agent's current **mood** (`DESPERATE`, `AGGRESSIVE_DEFENDER`, etc.).
- `decision_engine.py`: Arbitrates between the local simulator’s proposal and the LLM’s strategy.

### 3. 🛠️ Planning Layer (`planning_layer/`)
The “tactician” that builds plans:
- `action.py`: Defines actions with preconditions, effects, and costs.
- `goal.py`: Defines possible world-state goals.
- `planner.py`: A* algorithm for pathfinding through action space.

### 4. 🎮 Execution & Learning Layer (`execution_layer/`, `learning_layer.py`)
The agent’s “body” and “muscle memory”:
- `world_state.py`: Maintains world context.
- `action_executor.py`: Runs actions with a chance of failure.
- `learning_layer.py`: Rewards/penalizes actions and stores biases in `action_biases.json`.

---

## 🚀 Getting Started

Follow these steps to run the Dungeon Guardian simulation:

### 1. Clone the Repository

```bash
git clone https://github.com/AshayMaurya/D_and_D-001.git
cd D_and_D-001
```

### 2. Set Up the Environment

Create and activate a virtual environment:

```bash
# Create the virtual environment
python -m venv venv

# Activate it:
# On macOS or Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Your API Key

The agent uses the **Google Gemini API** for strategic reasoning.

1. [Get your API key here](https://aistudio.google.com/app/apikey).
2. In the root folder, create a `.env` file.
3. Add the following line (replace `<my key>` with your actual key):

```env
GEMINI_API_KEY = '<my key>'
```

⚠️ Make sure the variable name and file format match exactly.

---

## 🎮 Customize Your Scenario

The console will display the agent's full thought process:

- 🧠 **World Analysis**
- 🎯 **Chosen Goal**
- 🗺️ **Generated Plan**
- ✅ **Action Results**

### 5. Choose a Scenario

To simulate different starting conditions, open `main.py` and find this line:

```python
# >> CHOOSE YOUR SCENARIO HERE BY CHANGING THE ID <<
world_state = get_scenario_world_state(scenario_id=4)
```

You can change `scenario_id` to any of these options:

| Scenario ID | Description                                                   |
|-------------|---------------------------------------------------------------|
| `1`         | ❤️ Low Health, 🧪 No Potions, ⚔️ Enemy Nearby                  |
| `2`         | 💪 Healthy, 💰 Treasure Under Threat, ⚔️ Enemy Nearby           |
| `3`         | 💤 No Enemy, ⚡ Low Stamina, 🧪 Potion Available                |
| `4`         | 🧪 Out of Potions, 💛 Moderate Health, ⚔️ Enemy Near           |

---

### 6. Run the Simulation

Save the file and run the agent:

```bash
python main.py
```

Watch how the agent adapts to challenges, plans actions, and learns from the results.

---

## 📌 Notes

- This project is experimental and blends deterministic planning with generative AI.
- The Google Gemini API is used only for strategic reasoning; all planning is symbolic and deterministic.
- Logs are printed directly to the console for full visibility into the agent's behavior.


