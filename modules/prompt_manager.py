# modules/prompt_manager.py
import os

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')

def load_template(filename, subdirectory=""):
    """Load a template file from the templates directory."""
    path = os.path.join(TEMPLATE_DIR, subdirectory, filename)
    if os.path.exists(path):
        with open(path, 'r') as f:
            return f.read()
    return ""

def get_prompt(user_input, context, history="", auto_context="", user_facts="", categories=None):
    """
    Build the prompt for the AI by assembling modular components.
    """
    # Load consolidated components
    base_instructions = load_template('base.txt')
    tools = load_template('tools.txt')
    examples = load_template('examples.txt')
    
    # Assemble the final prompt
    prompt = f"""
{base_instructions}

{auto_context}
{user_facts}
{history}

---

{tools}

---

Current context: {context}
User input: "{user_input}"

Decide the best action and output ONLY a JSON object.

{examples}
"""
    return prompt.strip()
