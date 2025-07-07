import json
import os
from typing import List, Dict, Any

class Memory:

    def __init__(self, filepath: str = 'agent_memory.json'):
        """
        Initializes the Memory system.

        Args:
            filepath (str): The path to the JSON file where memory will be stored.
        """
        self.filepath = filepath
        self.history: List[Dict[str, Any]] = []
        self.load()

    def add_event(self, event_data: Dict[str, Any]):
        """
        Adds a new event to the agent's history and saves it.

        An event should be a dictionary containing details about what happened.
        Example for a failure:
        {
            "type": "failure",
            "plan": ["HealSelf", "AttackEnemy"],
            "reason": "Action 'HealSelf' failed: No potions available.",
            "world_state": { ... }
        }

        Args:
            event_data (dict): The dictionary containing event details.
        """
        print(f"--- MEMORY: Recording new event of type '{event_data.get('type')}' ---")
        self.history.append(event_data)
        self.save()

    def save(self):
        try:
            with open(self.filepath, 'w') as f:
                json.dump(self.history, f, indent=4)
        except IOError as e:
            print(f"ERROR: Could not save memory file to {self.filepath}: {e}")

    def load(self):
        if not os.path.exists(self.filepath):
            print(f"--- MEMORY: No memory file found at {self.filepath}. Starting fresh. ---")
            self.history = []
            return

        try:
            with open(self.filepath, 'r') as f:
                self.history = json.load(f)
            print(f"--- MEMORY: Successfully loaded {len(self.history)} events from {self.filepath}. ---")
        except (IOError, json.JSONDecodeError) as e:
            print(f"ERROR: Could not load or parse memory file {self.filepath}. Starting with empty memory. Error: {e}")
            self.history = []

    def get_recent_failures(self, n: int = 3) -> List[Dict[str, Any]]:
 
        failures = [event for event in self.history if event.get('type') == 'failure']
        return failures[-n:]

    def clear_memory(self):
        print("--- MEMORY: Clearing all memories. ---")
        self.history = []
        if os.path.exists(self.filepath):
            os.remove(self.filepath)