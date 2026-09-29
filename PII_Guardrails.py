"""

# 🔒 3. Built-in Guardrail — PII Detection Middleware

LangChain provides `PIIMiddleware` for detecting and handling **Personally Identifiable Information (PII)**.

PII refers to information that can identify or potentially identify an individual.

### Examples of PII

| Type          | Example                   |
| ------------- | ------------------------- |
| `email`       | `user@example.com`        |
| `credit_card` | `5105-1051-0510-5100`     |
| `ip`          | `192.168.1.1`             |
| `mac_address` | `00:1A:2B:3C:4D:5E`       |
| `url`         | `https://secret-site.com` |

### PII Handling Strategies

| Strategy | Result                |
| -------- | --------------------- |
| `redact` | `[REDACTED_EMAIL]`    |
| `mask`   | `****-****-****-1234` |
| `hash`   | `a8f5f167...`         |
| `block`  | Raises an exception   |

### Why PII Guardrails Matter

PII can accidentally appear in:

* User prompts
* LLM inputs
* Logs
* Agent responses
* Tool calls
* Databases

PII middleware provides a mechanism for detecting and controlling this information.

---
"""
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv(override=True)


model=ChatGroq(
    model="openai/gpt-oss-120b"
)
# Define a simple dummy tool
@tool
def customer_lookup(query: str) -> str:
    """Look up customer information."""
    return f"Customer record found for query: {query}"

# Create agent with PII Middleware
agent = create_agent(
    model="groq:openai/gpt-oss-120b",
    tools=[customer_lookup],
    middleware=[
        # Redact emails in user input before sending to model
        PIIMiddleware(
            "email",
            strategy="redact",
            apply_to_input=True,
        ),
        # Mask credit cards in user input
        PIIMiddleware(
            "credit_card",
            strategy="mask",
            apply_to_input=True,
        ),
        # Block API keys - raise error if detected
        PIIMiddleware(
            "api_key",
            detector=r"sk-[a-zA-Z0-9]{32}",
            strategy="block",
            apply_to_input=True,
        ),
    ],
)

print("Agent with PII middleware created successfully!")


print()


# Test PII Redaction
# Multi-turn chat loop with user input
messages = []

while True:
    user_input = input("You: ")

    if user_input.lower() in ("exit", "quit"):
        break

    messages.append({"role": "user", "content": user_input})
    result = agent.invoke({"messages": messages})
    messages = result["messages"]

    print("Agent:", messages[-1].content)
    print()

print(result)