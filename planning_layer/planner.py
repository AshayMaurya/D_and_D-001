# planning_layer/planner.py
import heapq
from typing import Optional, List
from planning_layer.action import Action

class Node:
    """A node in the A* search graph."""
    def __init__(self, state: dict, parent: Optional['Node'], action: Optional[Action], g_cost: int, h_cost: int):
        self.state = state
        self.parent = parent
        self.action = action
        self.g_cost = g_cost
        self.h_cost = h_cost
        self.f_cost = g_cost + h_cost

    def __lt__(self, other):
        return self.f_cost < other.f_cost

class GOAPPlanner:
    """
    A Goal-Oriented Action Planner using the A* search algorithm.
    """
    # --- THIS IS THE CORRECTED, SMARTER HEURISTIC ---
    def _calculate_heuristic(self, state: dict, goal_conditions: dict) -> int:
        """
        Calculates the heuristic cost (h_cost): the number of goal conditions not yet met.
        This version understands complex conditions (tuples).
        """
        cost = 0
        for key, value in goal_conditions.items():
            current_value = state.get(key)
            if isinstance(value, tuple) and len(value) == 2:
                op, operand = value
                if op == '>' and not (current_value is not None and current_value > operand): cost += 1
                elif op == '<' and not (current_value is not None and current_value < operand): cost += 1
                elif op == '>=' and not (current_value is not None and current_value >= operand): cost += 1
                elif op == '<=' and not (current_value is not None and current_value <= operand): cost += 1
                elif op == '==' and not (current_value == operand): cost += 1
                elif op == '!=' and not (current_value != operand): cost += 1
            elif current_value != value:
                cost += 1
        return cost
    # --- END OF FIX ---

    def _reconstruct_plan(self, final_node: Node) -> List[Action]:
        """
        Walks backward from the final node to reconstruct the plan.
        """
        plan = []
        current = final_node
        while current.parent:
            if current.action:
                plan.insert(0, current.action)
            current = current.parent
        return plan

    def find_plan(self, start_state: dict, goal_conditions: dict, actions: List[Action]) -> Optional[List[Action]]:
        """
        Finds a sequence of actions to satisfy the goal conditions.
        """
        closed_set = set()
        open_list = []

        start_node = Node(
            state=start_state,
            parent=None,
            action=None,
            g_cost=0,
            h_cost=self._calculate_heuristic(start_state, goal_conditions)
        )
        
        heapq.heappush(open_list, start_node)

        max_iterations = 1000 # Safety break to prevent true infinite loops
        iterations = 0

        while open_list and iterations < max_iterations:
            iterations += 1
            current_node = heapq.heappop(open_list)

            if self._calculate_heuristic(current_node.state, goal_conditions) == 0:
                return self._reconstruct_plan(current_node)
            
            closed_set.add(frozenset(current_node.state.items()))

            for action in actions:
                if action.is_achievable(current_node.state):
                    successor_state = action.apply(current_node.state)
                    
                    if frozenset(successor_state.items()) in closed_set:
                        continue

                    g_cost = current_node.g_cost + action.cost
                    h_cost = self._calculate_heuristic(successor_state, goal_conditions)
                    
                    successor_node = Node(
                        state=successor_state,
                        parent=current_node,
                        action=action,
                        g_cost=g_cost,
                        h_cost=h_cost
                    )
                    
                    heapq.heappush(open_list, successor_node)
        
        if iterations >= max_iterations:
            print("PLANNER WARNING: Reached max iterations. The state space might be too large or the goal impossible.")

        return None # No plan found