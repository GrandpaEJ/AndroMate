# modules/brain/fact_extractor.py
import json
import config
from providers import PROVIDERS
import brain.store as store

FACT_EXTRACTION_PROMPT = """
You are a memory module for an AI assistant. Your task is to extract permanent facts about the user from the following conversation exchange.

Rules:
1. Only extract facts that are likely to be useful for future interactions (e.g., names, preferences, relationships, important locations).
2. Ignore temporary information (e.g., "I'm hungry now").
3. Output ONLY a JSON object where keys are the fact categories and values are the facts.
4. If no new facts are found, return an empty JSON object: {}.

User said: "{user_input}"
Assistant replied: "{assistant_response}"

Extract facts:
"""

def extract_and_save_facts(user_input, assistant_response):
    """
    Calls the AI to extract facts from the exchange and saves them to the DB.
    """
    prompt = FACT_EXTRACTION_PROMPT.format(
        user_input=user_input,
        assistant_response=assistant_response
    )
    
    try:
        # Use a cheaper model if possible, but for now use the default AI_PROVIDER
        provider_func = PROVIDERS.get(config.AI_PROVIDER)
        if not provider_func:
            return
            
        content = provider_func(prompt)
        
        # Extract JSON from response
        start = content.find('{')
        end = content.rfind('}') + 1
        if start != -1 and end > start:
            json_str = content[start:end]
            facts = json.loads(json_str)
            
            for key, value in facts.items():
                store.update_fact(key, value)
                print(f"[Brain] Learned new fact: {key} = {value}")
                
    except Exception as e:
        # Fail silently for fact extraction to avoid interrupting the main flow
        print(f"[Brain] Fact extraction failed: {e}")
