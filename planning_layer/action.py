# planning_layer/action.py
from config import LOW_HEALTH_THRESHOLD, ATTACK_STAMINA_COST, HEAL_AMOUNT

class Action:
    """
    A base class for all actions in the GOAP system.
    """
    def __init__(self):
        self.name = self.__class__.__name__
        self.preconditions = {}
        self.effects = {}
        self.cost = 1  # Default cost for performing an action

    def is_achievable(self, world_state: dict) -> bool:
        """Checks if the action's preconditions are met by the world state."""
        for key, value in self.preconditions.items():
            if isinstance(value, tuple) and len(value) == 2:
                op, operand = value
                current_value = world_state.get(key)
                if op == '>' and not (current_value > operand): return False
                if op == '<' and not (current_value < operand): return False
                if op == '==' and not (current_value == operand): return False
                if op == '!=' and not (current_value != operand): return False
            elif world_state.get(key) != value:
                return False
        return True

    def apply(self, state: dict) -> dict:
        """Applies the action's effects to a state, returning a new state."""
        new_state = state.copy()
        for key, value in self.effects.items():
            if isinstance(value, tuple) and len(value) == 2:
                op, operand = value
                if op == '+':
                    new_state[key] = new_state.get(key, 0) + operand
                elif op == '-':
                    new_state[key] = new_state.get(key, 0) - operand
            else:
                new_state[key] = value
        return new_state


# --- Define all specific actions for the agent ---

class HealSelf(Action):
    def __init__(self):
        super().__init__()
        self.preconditions = {"potionCount": ('>', 0)}
        self.effects = {"health": ('+', HEAL_AMOUNT), "potionCount": ('-', 1)}

class AttackEnemy(Action):
    def __init__(self):
        super().__init__()
        self.preconditions = {"enemyNearby": True, "stamina": ('>=', ATTACK_STAMINA_COST)}
        self.effects = {"enemyNearby": False, "stamina": ('-', ATTACK_STAMINA_COST)}
        self.cost = 2 # Attacking is more costly than other actions

class Retreat(Action):
    def __init__(self):
        super().__init__()
        # Can retreat if an enemy is nearby or not
        self.preconditions = {}
        self.effects = {"isInSafeZone": True, "enemyNearby": False}
        
class DefendTreasure(Action):
    def __init__(self):
        super().__init__()
        self.preconditions = {} # Can always choose to defend
        self.effects = {"treasureThreatLevel": "low"}
        self.cost = 1

class CallBackup(Action):
    def __init__(self):
        super().__init__()
        self.preconditions = {"enemyNearby": True}
        # Calling backup reduces immediate threat but might not eliminate it
        self.effects = {"treasureThreatLevel": "low"} 
        self.cost = 3 # Calling backup is a high-cost, last-resort action

class SearchForPotion(Action):
    def __init__(self):
        super().__init__()
        self.preconditions = {"isInSafeZone": True} # Only search when it's safe
        self.effects = {"potionCount": ('+', 1)}
        self.cost = 2

# Helper function to get all available actions
def get_available_actions() -> list[Action]:
    return [
        HealSelf(),
        AttackEnemy(),
        Retreat(),
        DefendTreasure(),
        CallBackup(),
        SearchForPotion(),
    ]