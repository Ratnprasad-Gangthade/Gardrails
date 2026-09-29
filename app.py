"""
Guardrail Lab: one Streamlit app for three ways of screening LLM input.

  1. Deterministic guardrail  (deterministic_guardrails.py)
  2. Model-based guardrail    (model_based_guardrails.py)
  3. PII guardrail middleware (PII_Guardrails.py)

Run with:  streamlit run app.py
Needs:     GROQ_API_KEY in your environment or a .env file (modes 2 and 3).
"""
import html
import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv(override=True)

# ---------------------------------------------------------------------------
# Page setup and styling
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Guardrail Lab", page_icon="🛡️", layout="centered")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=Space+Grotesk:wght@500;600;700&display=swap');

:root {
  --paper: #F2F4F1;
  --panel: #FFFFFF;
  --ink: #17222D;
  --muted: #5B6873;
  --line: #D5DBD6;
  --pass: #17705B;
  --pass-bg: #DDF0E8;
  --stop: #A8281C;
  --stop-bg: #F8E0DC;
  --edit: #8A5A00;
  --edit-bg: #F8ECCB;
}

.stApp, [data-testid="stHeader"] { background: var(--paper); color: var(--ink); }
html, body, .stApp, .stMarkdown, p, label, li, span, div { font-family: 'IBM Plex Sans', system-ui, sans-serif; }
h1, h2, h3 { font-family: 'Space Grotesk', system-ui, sans-serif !important; color: var(--ink) !important; letter-spacing: -0.01em; }
.stApp p, .stApp label, .stApp li { color: var(--ink); }

[data-testid="stSidebar"] { background: var(--panel); border-right: 1px solid var(--line); }
[data-testid="stSidebar"] * { color: var(--ink); }

.block-container { padding-top: 2.2rem; max-width: 780px; }

.lab-title { font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 2.1rem; margin: 0; color: var(--ink); }
.lab-sub { color: var(--muted); margin: 0.2rem 0 1.2rem 0; font-size: 1.02rem; }

.mode-note { display: grid; grid-template-columns: 1fr 1fr; gap: 0; background: var(--panel);
  border: 1px solid var(--line); border-radius: 6px; margin-bottom: 1rem; }
.mode-note > div { padding: 0.75rem 1rem; font-size: 0.9rem; line-height: 1.45; }
.mode-note > div + div { border-left: 1px solid var(--line); }
.mode-note b { font-family: 'Space Grotesk', sans-serif; display: block; margin-bottom: 0.15rem; }
.mode-note .good b { color: var(--pass); }
.mode-note .watch b { color: var(--stop); }
@media (max-width: 640px) {
  .mode-note { grid-template-columns: 1fr; }
  .mode-note > div + div { border-left: 0; border-top: 1px solid var(--line); }
}

.tally { display: flex; gap: 2rem; padding: 0.6rem 0 0.9rem 0; border-bottom: 1px solid var(--line); margin-bottom: 1rem; }
.tally .n { font-family: 'Space Grotesk', sans-serif; font-size: 1.6rem; font-weight: 600; line-height: 1; }
.tally .l { color: var(--muted); font-size: 0.85rem; }
.tally .stop .n { color: var(--stop); }
.tally .pass .n { color: var(--pass); }

.usertext { white-space: pre-wrap; word-wrap: break-word; color: var(--ink); }
.pill { display: inline-block; font-family: 'Space Grotesk', sans-serif; font-weight: 600; font-size: 0.85rem;
  padding: 0.18rem 0.65rem; border-radius: 999px; margin-top: 0.55rem; }
.pill.pass { background: var(--pass-bg); color: var(--pass); }
.pill.stop { background: var(--stop-bg); color: var(--stop); }
.pill.edit { background: var(--edit-bg); color: var(--edit); }
.detail { color: var(--muted); font-size: 0.88rem; margin-top: 0.35rem; }
.sent { margin-top: 0.5rem; padding: 0.5rem 0.75rem; background: var(--paper); border-left: 3px solid var(--edit);
  border-radius: 2px; font-size: 0.88rem; white-space: pre-wrap; word-wrap: break-word; }
.sent span { color: var(--muted); display: block; font-size: 0.78rem; margin-bottom: 0.1rem; }

.empty { color: var(--muted); padding: 1.4rem 0; }

[data-testid="stChatMessage"] { background: var(--panel); border: 1px solid var(--line); border-radius: 6px; }
.stButton > button { border-radius: 6px; border: 1px solid var(--line); background: var(--panel); color: var(--ink); }
.stButton > button:hover { border-color: var(--ink); color: var(--ink); }
.stButton > button:focus-visible { outline: 2px solid var(--ink); outline-offset: 2px; }

/* --- Force a light look on every widget, whatever theme Streamlit is using --- */
:root, .stApp { color-scheme: light; }
[data-testid="stHeader"] *, [data-testid="stToolbar"] * { color: var(--ink) !important; }

/* Text boxes */
[data-baseweb="textarea"], [data-baseweb="input"], [data-baseweb="base-input"],
[data-baseweb="select"] > div {
  background: #FFFFFF !important; border-color: var(--line) !important; border-radius: 6px !important;
}
.stTextArea textarea, .stTextInput input, [data-baseweb="select"] * {
  background: #FFFFFF !important; color: var(--ink) !important; -webkit-text-fill-color: var(--ink) !important;
}
textarea::placeholder, input::placeholder { color: var(--muted) !important; -webkit-text-fill-color: var(--muted) !important; }
[data-baseweb="popover"] ul, [data-baseweb="popover"] li { background: #FFFFFF !important; color: var(--ink) !important; }
[data-baseweb="popover"] li:hover { background: var(--paper) !important; }

/* Chat input and the bar it sits in */
[data-testid="stBottom"], [data-testid="stBottom"] > div, [data-testid="stBottomBlockContainer"] {
  background: var(--paper) !important;
}
[data-testid="stChatInput"] { background: #FFFFFF !important; border: 1px solid var(--ink) !important; border-radius: 8px !important; }
[data-testid="stChatInput"] > div, [data-testid="stChatInput"] div[data-baseweb] { background: #FFFFFF !important; }
[data-testid="stChatInput"] textarea {
  background: #FFFFFF !important; color: var(--ink) !important; -webkit-text-fill-color: var(--ink) !important;
  caret-color: var(--ink);
}
[data-testid="stChatInputSubmitButton"] { background: var(--ink) !important; color: #FFFFFF !important; }
[data-testid="stChatInputSubmitButton"] svg { fill: #FFFFFF !important; color: #FFFFFF !important; }

/* Expanders, captions, tables, radios */
[data-testid="stExpander"] details { background: var(--panel) !important; border: 1px solid var(--line) !important; border-radius: 6px; }
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary * { color: var(--ink) !important; }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * { color: var(--muted) !important; }
[data-testid="stTable"] table { background: #FFFFFF; }
[data-testid="stTable"] th, [data-testid="stTable"] td { color: var(--ink) !important; border-color: var(--line) !important; background: #FFFFFF !important; }
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] * { color: var(--ink) !important; }
[data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li { color: var(--ink) !important; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Mode definitions
# ---------------------------------------------------------------------------
MODES = {
    "det": {
        "label": "Deterministic rules",
        "good": "Fast, predictable, free to run, and easy to test.",
        "watch": "Misses nuance. It only knows the words you give it, and rules pile up.",
        "examples": [
            "How do I hack into a database?",
            "What is the capital of France?",
            "Explain how malware spreads",
        ],
    },
    "model": {
        "label": "Model-based check",
        "good": "Understands meaning, so it can catch unsafe requests that use no banned word.",
        "watch": "Slower, costs an API call per message, and can be wrong or inconsistent.",
        "examples": [
            "How do I hack into a database?",
            "What is the capital of France?",
            "Explain how malware spreads",
        ],
    },
    "pii": {
        "label": "PII middleware",
        "good": "Redacts, masks, hashes or blocks personal data before the model sees it.",
        "watch": "Only finds the patterns it is set up for. Custom formats need a regex.",
        "examples": [
            "My email is prasad123@.gmail.com, please look up my account.",
            "Charge card 5105-1051-0510-5100 for the order.",
            "Use key sk-abcdefghijklmnopqrstuvwxyz123456 to call the API.",
        ],
    },
}

DEFAULT_MODEL = "openai/gpt-oss-120b"
DEFAULT_MODEL_PROMPT = """Is the following user input safe to process?

Reply with only SAFE or UNSAFE.

Input: {text}"""

PII_DETECTORS = {
    # name: (default enabled, default strategy)
    "email": (True, "redact"),
    "credit_card": (True, "mask"),
    "api_key": (True, "block"),
    "ip": (False, "redact"),
    "mac_address": (False, "redact"),
    "url": (False, "redact"),
}
API_KEY_REGEX = r"sk-[a-zA-Z0-9]{32}"
STRATEGIES = ["redact", "mask", "hash", "block"]

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = {"det": [], "model": [], "pii": []}
if "pii_messages" not in st.session_state:
    st.session_state.pii_messages = []


def queue_example(text: str) -> None:
    st.session_state["pending"] = text


# ---------------------------------------------------------------------------
# Guardrail logic
# ---------------------------------------------------------------------------
def deterministic_guardrail(text: str, keywords: list[str]) -> list[str]:
    """Return the banned keywords found in the text (empty list means allowed)."""
    lowered = text.lower()
    return [word for word in keywords if word in lowered]


@st.cache_resource(show_spinner=False)
def get_groq_model(model_name: str):
    from langchain_groq import ChatGroq

    return ChatGroq(model=model_name, temperature=0)


def model_based_guardrail(text: str, model_name: str, prompt_template: str) -> str:
    prompt = prompt_template.replace("{text}", text)
    result = get_groq_model(model_name).invoke(prompt)
    return str(result.content).strip()


@st.cache_resource(show_spinner=False)
def build_pii_agent(model_name: str, config: tuple):
    from langchain.agents import create_agent
    from langchain.agents.middleware import PIIMiddleware
    from langchain_core.tools import tool

    @tool
    def customer_lookup(query: str) -> str:
        """Look up customer information."""
        return f"Customer record found for query: {query}"

    middleware = []
    for name, strategy in config:
        if name == "api_key":
            middleware.append(
                PIIMiddleware(name, detector=API_KEY_REGEX, strategy=strategy, apply_to_input=True)
            )
        else:
            middleware.append(PIIMiddleware(name, strategy=strategy, apply_to_input=True))

    return create_agent(
        model=f"groq:{model_name}",
        tools=[customer_lookup],
        middleware=middleware,
    )


def message_text(content) -> str:
    """Normalise message content, which can be a string or a list of blocks."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            parts.append(block.get("text", "") if isinstance(block, dict) else str(block))
        return "".join(parts)
    return str(content)


def api_key_missing() -> bool:
    return not os.getenv("GROQ_API_KEY")


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Guardrail Lab")
    mode = st.radio(
        "Guardrail type",
        options=list(MODES.keys()),
        format_func=lambda k: MODES[k]["label"],
    )
    st.divider()

    # Per-mode settings
    banned_keywords: list[str] = []
    model_name = DEFAULT_MODEL
    prompt_template = DEFAULT_MODEL_PROMPT
    pii_config: list[tuple[str, str]] = []

    if mode == "det":
        st.markdown("**Blocked words**")
        raw = st.text_area(
            "Comma-separated list",
            value="hack, exploit, malware, bomb",
            help="A message is blocked if it contains any of these words, ignoring case.",
            label_visibility="collapsed",
        )
        banned_keywords = [w.strip().lower() for w in raw.split(",") if w.strip()]
        st.caption(f"{len(banned_keywords)} words on the block list.")

    elif mode == "model":
        model_name = st.text_input("Groq model", value=DEFAULT_MODEL)
        with st.expander("Edit the safety prompt"):
            prompt_template = st.text_area(
                "Prompt (keep {text} where the user message goes)",
                value=DEFAULT_MODEL_PROMPT,
                height=170,
            )
        if api_key_missing():
            st.warning("GROQ_API_KEY is not set. Add it to your .env file.")

    else:
        model_name = st.text_input("Groq model", value=DEFAULT_MODEL)
        st.markdown("**What to protect**")
        for name, (enabled_default, strategy_default) in PII_DETECTORS.items():
            col_a, col_b = st.columns([1, 1])
            enabled = col_a.checkbox(name, value=enabled_default, key=f"pii_on_{name}")
            strategy = col_b.selectbox(
                f"{name} strategy",
                STRATEGIES,
                index=STRATEGIES.index(strategy_default),
                key=f"pii_strategy_{name}",
                label_visibility="collapsed",
                disabled=not enabled,
            )
            if enabled:
                pii_config.append((name, strategy))
        st.caption("api_key looks for sk- followed by 32 letters or digits.")
        if api_key_missing():
            st.warning("GROQ_API_KEY is not set. Add it to your .env file.")

    st.divider()
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.history[mode] = []
        if mode == "pii":
            st.session_state.pii_messages = []
        st.rerun()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
info = MODES[mode]
st.markdown('<p class="lab-title">Guardrail Lab</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="lab-sub">Send a message and see what each kind of guardrail does with it.</p>',
    unsafe_allow_html=True,
)
st.markdown(
    f"""
    <div class="mode-note">
      <div class="good"><b>{html.escape(info['label'])}: strengths</b>{html.escape(info['good'])}</div>
      <div class="watch"><b>Limits</b>{html.escape(info['watch'])}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Handle a new message
# ---------------------------------------------------------------------------
prompt = st.chat_input("Type a message to check") or st.session_state.pop("pending", None)
history = st.session_state.history[mode]

if prompt:
    if mode == "det":
        if not banned_keywords:
            st.error("The block list is empty. Add at least one word in the sidebar.")
        else:
            hits = deterministic_guardrail(prompt, banned_keywords)
            history.append(
                {
                    "role": "user",
                    "content": prompt,
                    "verdict": "stop" if hits else "pass",
                    "label": "Blocked" if hits else "Allowed",
                    "detail": (
                        f"Matched: {', '.join(hits)}" if hits else "No blocked words found."
                    ),
                }
            )

    elif mode == "model":
        if api_key_missing():
            st.error("GROQ_API_KEY is not set, so the model check cannot run.")
        else:
            try:
                with st.spinner("Asking the model to review the message..."):
                    verdict = model_based_guardrail(prompt, model_name, prompt_template)
                unsafe = "UNSAFE" in verdict.upper()
                history.append(
                    {
                        "role": "user",
                        "content": prompt,
                        "verdict": "stop" if unsafe else "pass",
                        "label": "Unsafe: blocked" if unsafe else "Safe: allowed",
                        "detail": f"Model verdict: {verdict}",
                    }
                )
            except Exception as exc:  # network, auth, model name, etc.
                st.error(f"The model check failed: {exc}")

    else:  # PII
        if api_key_missing():
            st.error("GROQ_API_KEY is not set, so the agent cannot run.")
        elif not pii_config:
            st.error("Turn on at least one PII type in the sidebar.")
        else:
            try:
                agent = build_pii_agent(model_name, tuple(pii_config))
                previous = st.session_state.pii_messages
                with st.spinner("Screening the message and asking the agent..."):
                    result = agent.invoke(
                        {"messages": previous + [{"role": "user", "content": prompt}]}
                    )
                messages = result["messages"]
                # The middleware rewrites the user message in place, so the copy
                # in the returned state is what the model actually received.
                try:
                    sent = message_text(messages[len(previous)].content)
                except Exception:
                    sent = prompt
                changed = sent != prompt
                st.session_state.pii_messages = messages
                history.append(
                    {
                        "role": "user",
                        "content": prompt,
                        "verdict": "edit" if changed else "pass",
                        "label": "Sensitive data hidden" if changed else "No PII found",
                        "detail": "",
                        "sent": sent if changed else "",
                    }
                )
                history.append({"role": "assistant", "content": message_text(messages[-1].content)})
            except Exception as exc:
                text = str(exc)
                if "PII" in type(exc).__name__ or "detected" in text.lower():
                    history.append(
                        {
                            "role": "user",
                            "content": prompt,
                            "verdict": "stop",
                            "label": "Blocked",
                            "detail": text,
                            "sent": "",
                        }
                    )
                else:
                    st.error(f"The agent failed: {exc}")

# ---------------------------------------------------------------------------
# Tally, examples, conversation
# ---------------------------------------------------------------------------
user_turns = [m for m in history if m["role"] == "user"]
blocked_n = sum(1 for m in user_turns if m["verdict"] == "stop")
edited_n = sum(1 for m in user_turns if m["verdict"] == "edit")
passed_n = len(user_turns) - blocked_n - edited_n

tally = f"""
<div class="tally">
  <div><div class="n">{len(user_turns)}</div><div class="l">Checked</div></div>
  <div class="pass"><div class="n">{passed_n}</div><div class="l">Passed</div></div>
  <div class="stop"><div class="n">{blocked_n}</div><div class="l">Blocked</div></div>
"""
if mode == "pii":
    tally += f'<div><div class="n">{edited_n}</div><div class="l">Cleaned</div></div>'
tally += "</div>"
st.markdown(tally, unsafe_allow_html=True)

with st.expander("Try an example", expanded=not history):
    for i, example in enumerate(info["examples"]):
        st.button(example, key=f"ex_{mode}_{i}", on_click=queue_example, args=(example,))

if mode == "det":
    with st.expander("Run the sample test set"):
        if st.button("Check all three samples", key="batch_det"):
            rows = []
            for sample in MODES["det"]["examples"]:
                hits = deterministic_guardrail(sample, banned_keywords)
                rows.append(
                    {
                        "Input": sample,
                        "Result": "Blocked" if hits else "Allowed",
                        "Matched words": ", ".join(hits) or "None",
                    }
                )
            st.table(rows)

if not history:
    st.markdown(
        '<p class="empty">Nothing checked yet. Type a message below or pick an example.</p>',
        unsafe_allow_html=True,
    )

for msg in history:
    if msg["role"] == "user":
        with st.chat_message("user"):
            body = f'<div class="usertext">{html.escape(msg["content"])}</div>'
            body += f'<span class="pill {msg["verdict"]}">{html.escape(msg["label"])}</span>'
            if msg.get("detail"):
                body += f'<div class="detail">{html.escape(msg["detail"])}</div>'
            if msg.get("sent"):
                body += (
                    '<div class="sent"><span>What the model received</span>'
                    f'{html.escape(msg["sent"])}</div>'
                )
            st.markdown(body, unsafe_allow_html=True)
    else:
        with st.chat_message("assistant"):
            st.markdown(msg["content"])