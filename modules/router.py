# modules/router.py
import json
import config
from providers import PROVIDERS

ROUTING_PROMPT = """
Categorize the following user input into one or more relevant tool categories.
Possible categories: communication, device, information, media, advanced, general.

User input: "{user_input}"

Output ONLY a JSON list of categories, e.g., ["communication", "information"].
"""

def route_intent(user_input):
    """
    Classifies the user input to determine which tools/examples are needed.
    """
    prompt = ROUTING_PROMPT.format(user_input=user_input)
    
    try:
        # Use a fast model for routing
        provider_func = PROVIDERS.get(config.AI_PROVIDER)
        if not provider_func:
            return ["general"]
            
        content = provider_func(prompt)
        
        # Extract JSON list
        start = content.find('[')
        end = content.rfind(']') + 1
        if start != -1 and end > start:
            categories = json.loads(content[start:end])
            return categories
        return ["general"]
    except Exception as e:
        print(f"[Router] Routing failed: {e}")
        return ["general"]
