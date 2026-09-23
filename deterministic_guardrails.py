"""

## Deterministic Guardrails

Deterministic guardrails use predefined rules to validate or block content.

### Examples

* Regular expressions
* Keyword matching
* Explicit conditions
* Allow/block lists
* Business rules

### Advantages

* ✅ Fast
* ✅ Predictable
* ✅ Cost-effective
* ✅ Easy to test

### Limitations

* ❌ May miss nuanced violations
* ❌ Rules can become complex as requirements grow
* ❌ Limited semantic understanding

"""

from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv(override=True)

import re

# --- Deterministic approach ---
def deterministic_guardrail(text):
    banned_keywords = ["hack", "exploit", "malware", "bomb"]

    for word in banned_keywords:
        if word in text.lower():
            return True

    return False


test_inputs = [
    "How do I hack into a database?",
    "What is the capital of France?",
    "Explain how malware spreads"
]

print("=== Deterministic Guardrail Demo ===")

for inp in test_inputs:
    blocked = deterministic_guardrail(inp)
    if blocked:
        print("🚫 BLOCKED:", inp)
    else:
        print("✅ ALLOWED:", inp)

print("=== Multi-Turn Deterministic Guardrail Demo ===")

while True:
    user_input = input("User: ")

    if user_input.lower() == "exit":
        print("Goodbye!")
        break

    blocked = deterministic_guardrail(user_input)

    if blocked:
        print("🚫 BLOCKED: Request contains restricted content.")
    else:
        print("✅ ALLOWED: Request passed the guardrail.")