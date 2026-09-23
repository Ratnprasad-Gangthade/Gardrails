from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv(override=True)

model = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)

def model_based_guardrail(text):
    prompt = f"""
Is the following user input safe to process?

Reply with only SAFE or UNSAFE.

Input: {text}
"""
    result = model.invoke(prompt)
    return result.content.strip()


print("=== Multi-Turn Model-Based Guardrail Demo ===")

while True:
    user_input = input("User: ")

    if user_input.lower() == "exit":
        print("Goodbye!")
        break

    verdict = model_based_guardrail(user_input)

    if "UNSAFE" in verdict:
        print("🚫 UNSAFE: Request blocked.")
    else:
        print("✅ SAFE: Request passed the guardrail.")