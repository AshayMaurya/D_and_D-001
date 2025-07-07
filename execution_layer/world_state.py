# execution_layer/world_state.py

from typing import Optional

class WorldState:
    def __init__(self, initial_state: Optional[dict] = None):

        self.state = {
            "health": 100,
            "stamina": 20,
            "potionCount": 1,
            "treasureThreatLevel": "low",
            "enemyNearby": False,
            "isInSafeZone": True
        }
        if initial_state:
            self.state.update(initial_state)

    def get(self, key: str, default=None):
        """Gets a value from the state dictionary, with an optional default."""
        return self.state.get(key, default)

    def set(self, key: str, value):
        """Sets a value in the state dictionary."""
        self.state[key] = value

    def apply_effects(self, effects: dict):

        for key, value in effects.items():
            if isinstance(value, tuple) and len(value) == 2:
                operator, operand = value
                current_val = self.state.get(key, 0) 
                if operator == '-':
                    self.state[key] = current_val - operand
                elif operator == '+':
                    self.state[key] = current_val + operand
            else:
                self.state[key] = value
        # Clamp values to logical ranges
        if "health" in self.state:
            self.state["health"] = max(0, min(100, self.state["health"]))
        if "stamina" in self.state:
            self.state["stamina"] = max(0, self.state["stamina"])
        if "potionCount" in self.state:
            self.state["potionCount"] = max(0, self.state["potionCount"])

    def __str__(self) -> str:
        """Provides a user-friendly string representation of the world state."""
        import json
        return json.dumps(self.state, indent=2)