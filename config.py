# config.py

GEMINI_MODEL_NAME = "gemini-2.0-flash"
LOW_HEALTH_THRESHOLD = 40
LOW_STAMINA_THRESHOLD = 5
ATTACK_STAMINA_COST = 5
HEAL_AMOUNT = 50

# Controls how quickly the agent's biases change. A smaller number means slower, more stable learning.
LEARNING_RATE = 0.1
# The confidence level the local decision engine must have to AVOID calling the LLM.
CONFIDENCE_THRESHOLD = 0.5