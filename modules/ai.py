# modules/ai.py
import json
import config
from providers import PROVIDERS
from prompt_manager import get_prompt
import error_handler
import memory
from brain.fact_extractor import extract_and_save_facts
from router import route_intent
import cache
from context_provider import get_smart_context

def ask_ai(text, context="general"):
    """
    Send user input to selected AI provider and return structured action.
    Includes a reasoning loop (Phase 3) for multi-step tasks and self-correction.
    """
    max_steps = 2  # Maximum number of internal reasoning steps
    current_step = 0
    loop_context = "" # Additional context generated during the loop

    while current_step < max_steps:
        # 1. Routing & Planning
        categories = route_intent(text)
        
        # 2. Memory & Context
        # Only add user message once
        if current_step == 0:
            memory.add_user_message(text)
            
        auto_context = get_smart_context(categories)
        user_facts = memory.get_user_facts_context()

        # 3. Build Modular Prompt
        prompt = get_prompt(
            user_input=text + ("\n" + loop_context if loop_context else ""),
            context=context,
            history=memory.get_history(),
            auto_context=auto_context,
            user_facts=user_facts,
            categories=categories
        )
        
        # 4. Check Cache
        if current_step == 0:
            cached = cache.get_cached_response(prompt)
            if cached:
                print("[Cache] Using cached response.")
                return cached

        try:
            provider_func = PROVIDERS.get(config.AI_PROVIDER)
            if not provider_func:
                error_handler.log_error(f"Unknown AI provider: {config.AI_PROVIDER}", notify_user=True)
                return {"action": "none"}
            
            content = provider_func(prompt)

            # 5. JSON Extraction & Thought Processing
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end > start:
                json_str = content[start:end]
                decision = json.loads(json_str)

                thought = decision.get('thought', 'No explicit thought provided.')
                print(f"[Thought] {thought}")

                assistant_response = decision.get('response', '')
                action = decision.get('action', 'none')

                # 6. Post-Processing
                if action == 'reply' and assistant_response:
                    memory.add_assistant_message(assistant_response)
                
                # Extract facts
                extract_and_save_facts(text, assistant_response)
                
                # Cache the initial decision
                if current_step == 0:
                    cache.set_cached_response(prompt, decision)
                
                # Self-Correction / Multi-step logic (Placeholder)
                # If we had a way to execute and get results here, we could add to loop_context
                # For now, we return the decision to let the calling system execute it.
                return decision
            else:
                print("No JSON found in response. Retrying...")
                loop_context = "Your previous response was not a valid JSON. Please try again using the correct format."
                current_step += 1
                
        except Exception as e:
            error_handler.log_error(e, f"AI call failed (step {current_step})", notify_user=True)
            return {"action": "none"}
    
    return {"action": "none"}
