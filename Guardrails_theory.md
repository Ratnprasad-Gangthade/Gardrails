# 🛡️ Guardrails with LangChain

This project demonstrates how to implement **Guardrails in LangChain agents** using the middleware system.

Guardrails help build safer, more reliable, and compliant AI applications by validating, filtering, and controlling inputs, model execution, tool calls, and outputs.

---

## 📚 Topics Covered

1. What are Guardrails and why do they matter?
2. Deterministic vs. Model-Based Guardrails
3. Built-in PII Detection Middleware
4. Built-in Human-in-the-Loop Middleware
5. Custom Before-Agent Guardrail — Input Filtering
6. Custom After-Agent Guardrail — Output Safety
7. Layered / Combined Guardrails
8. Real-World Use Case — Healthcare Chatbot

---

## 📖 Documentation

* [LangChain Guardrails Documentation](https://docs.langchain.com/oss/python/langchain/guardrails)

---

# 🧠 1. What Are Guardrails?

**Guardrails** are safety and validation mechanisms used to control how an AI application handles inputs, model responses, and tool operations.

In LangChain, guardrails can be implemented using **middleware** that intercepts the agent execution at different stages.

### Guardrails can run:

* **Before the agent starts** — validate or filter user input
* **After the agent completes** — validate the final response
* **Around model calls** — inspect model inputs and outputs
* **Around tool calls** — control sensitive operations

### Common Use Cases

| Use Case                  | Example                                   |
| ------------------------- | ----------------------------------------- |
| PII leakage prevention    | Redact emails or credit card numbers      |
| Prompt injection blocking | Detect adversarial inputs                 |
| Harmful content filtering | Block dangerous requests                  |
| Business rule enforcement | Require approval for financial operations |
| Output validation         | Ensure responses meet safety standards    |

---

# ⚖️ 2. Two Approaches to Guardrails

Guardrails can generally be implemented using two approaches.

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

---

## Model-Based Guardrails

Model-based guardrails use an LLM or classifier to understand the semantic meaning of content.

### Advantages

* ✅ Can detect subtle or contextual issues
* ✅ Better semantic understanding
* ✅ Useful for complex safety policies

### Limitations

* ❌ Additional latency
* ❌ Higher cost
* ❌ Model output itself can be imperfect

### General Strategy

A practical architecture is often:

```text
User Input
    ↓
Deterministic Checks
    ↓
Model-Based Validation
    ↓
LLM / Agent
    ↓
Output Validation
    ↓
User
```

---

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

# 👤 4. Built-in Guardrail — Human-in-the-Loop Middleware

**Human-in-the-Loop (HITL)** middleware pauses agent execution before sensitive operations and waits for human approval.

This is particularly useful when an AI agent can perform actions with real-world consequences.

### Best Use Cases

* 💰 Financial transactions
* 📧 Sending emails to external parties
* 🗑️ Deleting production data
* 📅 Booking appointments
* 🔐 Changing sensitive account information
* ⚠️ Other high-impact operations

### Example Flow

```text
User Request
     ↓
AI Agent
     ↓
Sensitive Tool Call
     ↓
Human Approval Required
     ↓
 ┌───────────────┐
 │   Approve?    │
 └───────┬───────┘
         │
    ┌────┴────┐
   YES        NO
    ↓          ↓
Execute      Stop
Tool
```

### Important Requirement

Human-in-the-loop workflows require a **checkpointer** so that agent state can be persisted across interruptions.

For development, an in-memory checkpointer such as `InMemorySaver` can be used. Production systems should generally use a persistent storage solution.

---

# 🛡️ 5. Custom Guardrail — Before-Agent Hook

The `before_agent()` hook can be used to validate or block requests **before the agent begins processing them**.

This is useful for preventing unwanted requests from reaching the LLM.

### Best Use Cases

* Keyword filtering
* Content filtering
* Authentication checks
* Rate limiting
* Blocking specific categories of requests
* Input validation
* Prompt injection detection

### Example Flow

```text
User Input
     ↓
before_agent()
     ↓
 ┌──────────────┐
 │ Input Valid? │
 └──────┬───────┘
        │
   ┌────┴────┐
  YES        NO
   ↓          ↓
Agent       Block
Execution   Request
```

---

# 🔍 6. Custom Guardrail — After-Agent Hook

The `after_agent()` hook can be used to validate the agent's final response **before it is returned to the user**.

This provides a final safety layer.

### Best Use Cases

* Model-based safety evaluation
* Compliance checks
* Medical/legal/financial disclaimers
* Output quality validation
* Detecting sensitive information
* Removing or blocking unsafe content

### Example Flow

```text
User Request
     ↓
Agent
     ↓
Agent Response
     ↓
after_agent()
     ↓
Safety / Quality Check
     ↓
 ┌───────────────┐
 │ Response Safe?│
 └───────┬───────┘
         │
    ┌────┴────┐
   YES        NO
    ↓          ↓
 User       Block /
Response    Modify
```

---

# 🧱 7. Layered / Combined Guardrails

Multiple guardrails can be combined using the `middleware=[]` configuration.

This creates a **layered defense system**, where different guardrails protect different stages of the agent execution.

### Example Architecture

```text
                    User Input
                        │
                        ▼
        ┌─────────────────────────────┐
        │ Layer 1: Content Filter     │
        │ Deterministic Input Check   │
        └──────────────┬──────────────┘
                       │
                       ▼
        ┌─────────────────────────────┐
        │ Layer 2: PII Middleware      │
        │ Input PII Detection/Redact  │
        └──────────────┬──────────────┘
                       │
                       ▼
        ┌─────────────────────────────┐
        │ Layer 3: Human-in-the-Loop  │
        │ Sensitive Tool Approval     │
        └──────────────┬──────────────┘
                       │
                       ▼
                    AI Agent
                       │
                       ▼
        ┌─────────────────────────────┐
        │ Layer 4: PII Middleware      │
        │ Output PII Detection        │
        └──────────────┬──────────────┘
                       │
                       ▼
        ┌─────────────────────────────┐
        │ Layer 5: Safety Guardrail   │
        │ Model-Based Output Check    │
        └──────────────┬──────────────┘
                       │
                       ▼
                  User Response
```

### Defense in Depth

The idea is to avoid relying on a single safety mechanism.

```text
Input Protection
       +
Privacy Protection
       +
Human Approval
       +
Output Protection
       +
Safety Validation
       ↓
Layered AI Safety
```

---

# 🏥 8. Real-World Use Case — Healthcare Chatbot

A healthcare chatbot is a good example of an application where multiple guardrails may be required.

### Example Requirements

The chatbot could:

* Block harmful or unrelated requests
* Detect and redact patient PII
* Require human approval before booking appointments
* Validate generated responses against predefined safety rules
* Prevent sensitive information from being exposed
* Apply additional compliance checks before returning responses

### Example Architecture

```text
Patient
   ↓
Input Guardrail
   ↓
PII Detection
   ↓
Healthcare AI Agent
   ↓
 ┌─────────────────────┐
 │ Sensitive Operation?│
 └──────────┬──────────┘
            │
           YES
            ↓
     Human Approval
            ↓
      Tool Execution
            │
            ▼
     Output Guardrail
            ↓
    Safety Validation
            ↓
      Patient Response
```

> ⚠️ In real healthcare systems, additional legal, regulatory, security, privacy, and clinical requirements must be considered. Guardrails are one part of the overall safety architecture.

---

# 📝 Guardrail Types Summary

| Guardrail Type    | Hook / Level        | When It Runs              | Best For                    |
| ----------------- | ------------------- | ------------------------- | --------------------------- |
| PII Middleware    | Input / Output      | Around model execution    | Data privacy and compliance |
| Human-in-the-Loop | Tool level          | Before sensitive tools    | High-impact operations      |
| Content Filter    | `before_agent`      | Start of invocation       | Blocking unwanted inputs    |
| Safety Validator  | `after_agent`       | End of invocation         | Output quality and safety   |
| Custom Logic      | Any applicable hook | Depends on implementation | Business-specific rules     |

---

# 🔑 Key Takeaways

### 1. Guardrails = Middleware

In LangChain, guardrails can be implemented through middleware and configured using the:

```python
middleware=[]
```

parameter when creating an agent.

### 2. Layer Your Guardrails

Do not depend on a single validation mechanism.

Use multiple layers for defense in depth:

```text
Input → Privacy → Agent → Tools → Output → Safety
```

### 3. Use Deterministic Checks Early

Rule-based checks are generally:

* Faster
* Cheaper
* Predictable

They can be used to reject obvious invalid or unwanted requests before making expensive LLM calls.

### 4. Use Model-Based Checks for Semantic Safety

LLM-based validation can help identify issues that simple rules may not detect.

### 5. Human-in-the-Loop for High-Impact Actions

When an agent can perform sensitive operations, human approval can provide an additional control layer.

### 6. Checkpointing Matters

Human-in-the-loop workflows need state persistence across interruptions.

For development:

```python
InMemorySaver
```

can be useful.

For production, a persistent checkpointer should generally be considered.

### 7. Custom Middleware Provides Flexibility

Custom hooks such as:

```python
before_agent()
```

and:

```python
after_agent()
```

allow developers to implement application-specific safety and business rules.

---

# 📚 Additional Resources

* [LangChain Guardrails](https://docs.langchain.com/oss/python/langchain/guardrails)
* [LangChain Middleware](https://docs.langchain.com/oss/python/langchain/middleware)
* [LangChain Human-in-the-Loop](https://docs.langchain.com/oss/python/langchain/human-in-the-loop)
* [LangSmith](https://smith.langchain.com/) — Observability and monitoring for LangChain applications

---

## 🚀 Project Goal

The goal of this project is to understand how **guardrails can be integrated into LangChain agents** and how multiple safety mechanisms can be combined to build more controlled and reliable AI applications.

```text
                 ┌───────────────────┐
                 │    User Input     │
                 └─────────┬─────────┘
                           ↓
                 ┌───────────────────┐
                 │ Input Guardrails  │
                 └─────────┬─────────┘
                           ↓
                 ┌───────────────────┐
                 │   AI Agent / LLM  │
                 └─────────┬─────────┘
                           ↓
                 ┌───────────────────┐
                 │ Tool Guardrails   │
                 └─────────┬─────────┘
                           ↓
                 ┌───────────────────┐
                 │ Output Guardrails │
                 └─────────┬─────────┘
                           ↓
                 ┌───────────────────┐
                 │  Safe Response    │
                 └───────────────────┘
```
