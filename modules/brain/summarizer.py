# modules/brain/summarizer.py
import config
from providers import PROVIDERS

SUMMARIZATION_PROMPT = """
Summarize the following conversation history into a concise paragraph. 
Focus on the key topics discussed and any decisions made. 
Keep the summary under 100 words.

Conversation:
{history_text}

Summary:
"""

def summarize_history(history_items):
    """
    Summarizes a list of history items into a single string.
    """
    if not history_items:
        return ""
        
    history_text = ""
    for item in history_items:
        role = item['role']
        content = item['content']
        prefix = "User" if role == 'user' else "Assistant"
        history_text += f"{prefix}: {content}\n"
    
    prompt = SUMMARIZATION_PROMPT.format(history_text=history_text)
    
    try:
        provider_func = PROVIDERS.get(config.AI_PROVIDER)
        if not provider_func:
            return "History summary unavailable."
            
        summary = provider_func(prompt)
        return summary.strip()
    except Exception as e:
        print(f"[Summarizer] Summarization failed: {e}")
        return "History summary unavailable."
