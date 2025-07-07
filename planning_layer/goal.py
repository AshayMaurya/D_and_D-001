# planning_layer/goal.py
from config import LOW_HEALTH_THRESHOLD

class Goal:
    """A class representing a desired state of the world."""
    def __init__(self, name: str, priority: int, conditions: dict):
        self.name = name
        self.priority = priority
        self.conditions = conditions # The desired state dict for the planner

    def is_fulfilled(self, world_state: dict) -> bool:
        """Checks if the goal's conditions are met by the world state."""
        for key, value in self.conditions.items():
            if world_state.get(key) != value:
                return False
        return True

# --- Define all goals the agent can have ---

def get_available_goals() -> list[Goal]:
    return [
        Goal(
            name="Survive",
            priority=100,
            conditions={"health": ('>', LOW_HEALTH_THRESHOLD)} # This is a soft goal; planner seeks a state where this is true.
                                                             # For simplicity, we'll aim for a state reachable by actions.
                                                             # A better approach is a "soft goal" planner, but for this project,
                                                             # we can define survival as 'being in a safe zone'.
                                                             # Let's redefine Survive for our planner.
        ),
        Goal( # Simplified goal for planner
            name="Survive",
            priority=100,
            conditions={"isInSafeZone": True}
        ),
        Goal(
            name="EliminateThreat",
            priority=80,
            conditions={"enemyNearby": False}
        ),
        Goal(
            name="ProtectTreasure",
            priority=90,
            conditions={"treasureThreatLevel": "low"}
        ),
        Goal(
            name="PrepareForBattle",
            priority=50,
            conditions={"health": 100, "potionCount": ('>', 0)} # Similar to survive, let's simplify for the planner.
        ),
        Goal( # Simplified goal for planner
            name="PrepareForBattle",
            priority=50,
            conditions={"potionCount": ('>=', 1)}
        )
    ]

def get_goal_by_name(name: str) -> Goal | None:
    for goal in get_available_goals():
        if goal.name == name:
            return goal
    return None