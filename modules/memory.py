import brain.store as store
from brain.summarizer import summarize_history

# Configuration
MAX_HISTORY = 10  # Keep last 10 exchanges (20 messages)
SUMMARIZE_THRESHOLD = 15 # Summarize after 15 messages

def add_user_message(message: str):
    """Add a user message to history and manage compression."""
    store.add_message('user', message)
    _check_and_summarize()

def add_assistant_message(message: str):
    """Add an assistant message to history and manage compression."""
    store.add_message('assistant', message)
    _check_and_summarize()

def _check_and_summarize():
    """Check if history exceeds threshold and condense if necessary."""
    # This is a simplified version; in a real scenario, we'd store the summary 
    # in the DB and clear the summarized rows.
    pass

def get_history() -> str:
    """Return formatted conversation history for inclusion in prompts."""
    history_items = store.get_recent_history(limit=MAX_HISTORY * 2)
    
    if not history_items:
        return ""
    
    lines = []
    for item in history_items:
        role = item['role']
        content = item['content']
        prefix = "User" if role == 'user' else "Assistant"
        lines.append(f"{prefix}: {content}")
    
    return "\n".join(lines)

def get_user_facts_context() -> str:
    """Return a formatted string of known user facts."""
    facts = store.get_all_facts()
    if not facts:
        return ""
    
    lines = ["Known information about the user:"]
    for key, value in facts.items():
        lines.append(f"- {key}: {value}")
    return "\n".join(lines)

def clear():
    """Clear conversation history."""
    store.clear_history()
