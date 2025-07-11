# cognitive_layer/cognitive_engine.py

import json
from typing import Dict, Tuple
from google import genai
from execution_layer.world_state import WorldState
from memory import Memory
import config

class CognitiveEngine:
    def __init__(self, api_key: str):
        if not api_key: raise ValueError("API key for Gemini is not set.")
        self.client = genai.Client(api_key=api_key)
        self.model_name = config.GEMINI_MODEL_NAME
        print("Cognitive Engine (LLM Expert) initialized successfully.")

    def _create_goal_prompt(self, world_state: WorldState, mood: str, local_proposal: Tuple | None) -> str:
        
        local_recommendation = "My local simulation could not find a valid course of action."
        if local_proposal:
            local_goal, local_justification, _ = local_proposal
            local_recommendation = (
                f"My internal simulation has analyzed all immediate options. Here is my data-driven recommendation:\n"
                f"- Recommended Goal: {local_goal}\n"
                f"- Reasoning: {local_justification}"
            )

        prompt = f"""
        
        
        You are the strategic advisor for an autonomous agent. I am the agent's local logic core. I have compiled a detailed report for your review.

        **Intelligence Briefing:**

        *   **Resource Status:** {thought_from_analyze_health}
        *   **Threat Assessment:** {thought_from_analyze_threats}
        *   **Lessons from Past Failures:** {thought_from_analyze_failures}
        *   **Local Simulation Proposal:** {thought_from_analyze_simulation}
        *   **Strategic Alert:** {thought_from_detect_repetition}

        **Your Task:**
        Synthesize all the points in this briefing. Your job is not just to pick the most obvious action, but to find the best long-term strategy. If you see a 'Strategic Alert', give it special consideration.

        Choose the best goal and provide your reasoning. Respond with a JSON object: {"goal": "...", "justification": "..."}
                You are the strategic advisor for an agent that is about to get stuck in a repetitive loop.


        **Current World State:**
        {json.dumps(world_state.state, indent=2)}

        **My Local Simulation's Proposal:**
        {local_recommendation}

        **Your Task:**
        Review my proposal and the world state. Do you agree with my data-driven choice, or do you see a superior long-term strategy?
        Respond with a JSON object containing your chosen "goal" and a "justification" explaining your reasoning. If you agree with me, feel free to adopt my reasoning.
        """
        return prompt

    def generate_goal(self, world_state: WorldState, memory: Memory, mood: str, biases: Dict, local_proposal: Tuple | None) -> Tuple[str, str]:
        prompt = self._create_goal_prompt(world_state, mood, local_proposal)
        try:
            response = self.client.models.generate_content(model=self.model_name, contents=prompt)
            if not hasattr(response, 'text') or not response.text:
                return "PrepareForBattle", "LLM response was empty. Defaulting to a safe goal."
            cleaned_text = response.text.strip().replace("```json", "").replace("```", "")
            data = json.loads(cleaned_text)
            return data.get("goal", "PrepareForBattle"), data.get("justification", "LLM response was malformed.")
        except Exception as e:
            return "PrepareForBattle", f"LLM Error: {e}. Defaulting to a safe goal."

    def _create_reflection_prompt(self, world_state: WorldState, failed_plan: list[str], reason: str) -> str:
        """
        Constructs the prompt for reflecting on a failure. This method is unchanged.
        """
        return f"""
        You are the Sentient Guardian. Your plan has just failed.
        **Current World State:** {json.dumps(world_state.state, indent=2)}
        **The Plan that Failed:** {failed_plan}
        **Reason for Failure:** {reason}
        **Your Task:**
        Provide a short, first-person internal monologue reflecting on why the plan failed and what you might do differently.
        """

    def reflect_on_failure(self, world_state: WorldState, failed_plan: list[str], reason: str) -> str:
        """
        Asks the LLM to analyze a failure. This method is unchanged.
        """
        prompt = self._create_reflection_prompt(world_state, failed_plan, reason)
        print("\n----- Asking LLM to reflect on failure... -----")
        try:
            response = self.client.models.generate_content(model=self.model_name, contents=prompt)
            if not hasattr(response, 'text') or not response.text:
                return "I have failed, and my mind is blank. I cannot reflect."
            return response.text.strip()
        except Exception as e:
            return f"I have failed, and an error prevents reflection: {e}"