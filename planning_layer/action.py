# planning_layer/action.py

from config import LOW_HEALTH_THRESHOLD, ATTACK_STAMINA_COST, HEAL_AMOUNT

class Action:
    """
    A base class for all actions in the GOAP system.
    """
    def __init__(self):
        """Initializes the action, setting its name and default cost."""
        self.name = self.__class__.__name__
        self.preconditions = {}
        self.effects = {}
        self.cost = 1  # Default cost for performing an action

    def is_achievable(self, world_state: dict) -> bool:
        """
        Checks if the action's preconditions are met by the world state.
        This method can handle both simple equality and complex tuple-based comparisons.
        """
        for key, value in self.preconditions.items():
            current_value = world_state.get(key)
            
            # This block handles complex preconditions like ('<', 30) or ('>=', 0)
            if isinstance(value, tuple) and len(value) == 2:
                op, operand = value
                if current_value is None: return False # Cannot compare if the state key doesn't exist
                if op == '>' and not (current_value > operand): return False
                if op == '<' and not (current_value < operand): return False
                if op == '>=' and not (current_value >= operand): return False
                if op == '<=' and not (current_value <= operand): return False
                if op == '==' and not (current_value == operand): return False
                if op == '!=' and not (current_value != operand): return False
            # This handles simple preconditions like {"enemyNearby": True}
            elif current_value != value:
                return False
        return True

    def apply(self, state: dict) -> dict:
        """
        Applies the action's effects to a given state dictionary, returning a new state.
        This is used by the planner to simulate the future.
        """
        new_state = state.copy()
        for key, value in self.effects.items():
            # This block handles relative effects like ('+', 10) or ('-', 1)
            if isinstance(value, tuple) and len(value) == 2:
                op, operand = value
                current_val = new_state.get(key, 0) # Default to 0 if key doesn't exist
                if op == '+':
                    new_state[key] = current_val + operand
                elif op == '-':
                    new_state[key] = current_val - operand
            # This handles absolute effects like {"enemyNearby": False}
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
        self.preconditions = {} # Can always attempt to retreat
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

class Rest(Action):
    """
    A low-cost, guaranteed action to recover health and stamina when safe.
    This provides a fallback for the planner when no potions are available,
    preventing planning loops where the goal is achievable but not guaranteed.
    """
    def __init__(self):
        super().__init__()
        self.preconditions = {"isInSafeZone": True}
        self.effects = {"health": ('+', 10), "stamina": ('+', 5)}
        self.cost = 1 # It's an easy, low-cost action to take.


def get_available_actions() -> list[Action]:
    """
    Returns a list containing an instance of every available action for the agent.
    """
    return [
        HealSelf(),
        AttackEnemy(),
        Retreat(),
        DefendTreasure(),
        CallBackup(),
        SearchForPotion(),
        Rest(),
    ]