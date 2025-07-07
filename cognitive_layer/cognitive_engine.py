# cognitive_layer/cognitive_engine.py

import os
import json
from google import genai
from execution_layer.world_state import WorldState
from memory import Memory
import config

class CognitiveEngine:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key for Gemini is not set. Please check your .env file.")
        self.client = genai.Client(api_key=api_key)
        self.model_name = config.GEMINI_MODEL_NAME
        print("Cognitive Engine initialized successfully with the new GenAI SDK.")

    def _create_goal_prompt(self, world_state: WorldState, memory: Memory) -> str:
        available_goals = [
            "Survive (Priority when health is low or overwhelmed)",
            "EliminateThreat (Priority when an enemy is nearby and health is adequate)",
            "ProtectTreasure (Priority when treasure is under high threat)",
            "PrepareForBattle (Priority when no immediate threats exist; focuses on healing, resting)"
        ]
        recent_failures = memory.get_recent_failures(n=3)
        failure_log = "No recent failures."
        if recent_failures:
            failure_log = "Here are my recent failures:\n"
            for failure in recent_failures:
                failure_log += f"- Plan '{failure['plan']}' failed because '{failure['reason']}'.\n"

        prompt = f"""
        You are the Sentient Guardian of a dungeon. Your purpose is to protect it intelligently.
        Analyze your current situation and choose the most critical goal to pursue right now.
        **Current World State:**
        {json.dumps(world_state.state, indent=2)}
        **Memory of Past Events:**
        {failure_log}
        **Available Goals:**
        - {', '.join(available_goals)}
        **Your Task:**
        Respond with a JSON object containing two keys:
        1. "goal": A string with the name of the single most important goal to adopt from the list.
        2. "justification": A short, first-person explanation for your choice.
        """
        return prompt

    def generate_goal(self, world_state: WorldState, memory: Memory) -> tuple[str | None, str | None]:
        prompt = self._create_goal_prompt(world_state, memory)
        print("\n----- Asking LLM for a new goal... -----")
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            
            # --- FIX: Check for a valid text response before processing ---
            if not hasattr(response, 'text') or not response.text:
                print("ERROR: LLM response did not contain text. It may have been blocked or empty.")
                # You can optionally log response.prompt_feedback for more details on safety blocks
                return None, "LLM response was empty or blocked."

            cleaned_response_text = response.text.strip().replace("```json", "").replace("```", "")
            response_json = json.loads(cleaned_response_text)
            
            goal = response_json.get("goal")
            justification = response_json.get("justification")

            if not goal or not justification:
                print("ERROR: LLM response JSON was missing 'goal' or 'justification'.")
                return None, "LLM response was malformed."

            return goal, justification
        except Exception as e:
            print(f"ERROR: Failed to get or parse LLM response for goal generation: {e}")
            return None, f"An error occurred: {e}"

    def _create_reflection_prompt(self, world_state: WorldState, failed_plan: list[str], reason: str) -> str:
        prompt = f"""
        You are the Sentient Guardian of a dungeon. Your plan has just failed.
        You must reflect on this failure to learn from it.
        **Current World State (at the moment of failure):**
        {json.dumps(world_state.state, indent=2)}
        **The Plan that Failed:**
        {failed_plan}
        **Reason for Failure:**
        {reason}
        **Your Task:**
        In a single, short paragraph, provide a first-person internal monologue reflecting on this failure.
        """
        return prompt

    def reflect_on_failure(self, world_state: WorldState, failed_plan: list[str], reason: str) -> str:
        prompt = self._create_reflection_prompt(world_state, failed_plan, reason)
        print("\n----- Asking LLM to reflect on failure... -----")
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            
            # --- FIX: Check for a valid text response here as well ---
            if not hasattr(response, 'text') or not response.text:
                print("ERROR: LLM reflection response was empty or blocked.")
                return "I have failed, and my mind is blank. I cannot reflect."

            return response.text.strip()
        except Exception as e:
            print(f"ERROR: Failed to get LLM response for reflection: {e}")
            return "I have failed, and the error in my own mind prevents even reflection."