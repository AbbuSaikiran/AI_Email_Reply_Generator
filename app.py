"""
AI Email Reply Generator  -  Streamlit web app
Run with:  streamlit run app.py
"""
import os
import streamlit as st

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from email_engine import (TONES, LENGTHS, PROVIDERS, MAX_INPUT_CHARS,
                          GenAIError, generate_email, validate_input)

st.set_page_config(page_title="AI Email Reply Generator", page_icon="📧", layout="centered")

# ---------- Sidebar: settings ----------
with st.sidebar:
    st.header("⚙️ Settings")
    default_idx = 1 if os.getenv("GEMINI_API_KEY") else 2 if os.getenv("ANTHROPIC_API_KEY") else 0
    provider = st.selectbox("AI Model", PROVIDERS, index=default_idx)
    api_key = ""
    if not provider.startswith("Offline"):
        api_key = st.text_input("API key (optional if set in .env)", type="password")
    else:
        st.info("Offline Demo uses simple templates, not a real AI model. "
                "Choose Gemini or Claude for true Generative AI output.")
    sender_name = st.text_input("Your name (optional)", placeholder="e.g. Ravi Kumar")
    recipient = st.text_input("Recipient (optional)", placeholder="e.g. Prof. Sharma / HR Team")
    st.caption("Always review the email before sending it.")

# ---------- Main page ----------
st.title("📧 AI Email Reply Generator")
st.caption("Describe a situation or paste an email. Get a ready-to-send reply in seconds.")

situation = st.text_area(
    "✉️ Enter the email or situation",
    height=150, max_chars=MAX_INPUT_CHARS,
    placeholder="Example: I cannot attend tomorrow's meeting because I have an examination.",
)

col1, col2 = st.columns(2)
tone = col1.selectbox("🎨 Tone", TONES)
length = col2.selectbox("📏 Length", LENGTHS, index=1)

if "email" not in st.session_state:
    st.session_state.email = ""
    st.session_state.variation = 0


def run(variation: int):
    ok, err = validate_input(situation)
    if not ok:
        st.warning(err)
        return
    try:
        with st.spinner("🤖 Generating your email..."):
            st.session_state.email = generate_email(
                situation, tone, length, provider, api_key,
                sender_name, recipient, variation)
            st.session_state.variation = variation
            st.session_state.used_provider = provider
    except GenAIError as e:
        st.error(str(e))
    except Exception:
        st.error("Something went wrong while contacting the AI service. "
                 "Check your internet connection and try again.")


b1, b2 = st.columns([1, 1])
if b1.button("✨ Generate Reply", type="primary", use_container_width=True):
    run(0)
if b2.button("🔄 Regenerate", use_container_width=True,
             disabled=not st.session_state.email):
    run(st.session_state.variation + 1)

# ---------- Output ----------
if st.session_state.email:
    st.divider()
    st.subheader("Generated Email")
    # st.code shows a built-in "copy" icon in the top-right corner (📋 Copy)
    st.code(st.session_state.email, language=None, wrap_lines=True)
    st.caption("📋 Use the copy icon at the top-right of the box to copy the email.")
    st.download_button("⬇️ Download as .txt", st.session_state.email,
                       file_name="email_reply.txt", mime="text/plain")
