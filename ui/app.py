import os
import sys
import uuid
import logfire
import streamlit as st
from dotenv import load_dotenv

# Ensure root folder is in sys.path for evals and local imports
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

load_dotenv(os.path.join(ROOT_DIR, ".env"))

# Import modular views
from ui.chat_view import render_chat_view
from ui.evals_view import render_evals_view
from ui.docs_view import render_docs_view

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Enterprise Agentic OS",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- LOGFIRE SETUP ---
if "logfire_status" not in st.session_state:
    try:
        token = os.getenv("LOGFIRE_TOKEN")
        if not token:
            st.session_state.logfire_status = "⚠️ No Token Found"
        else:
            logfire.configure(token=token, service_name="agent-os-ui")
            st.session_state.logfire_status = "🟢 Connected & Tracing"
    except Exception as e:
        st.session_state.logfire_status = f"🔴 Error: {str(e)[:20]}"

# --- GLOBAL SESSION INIT ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    logfire.info(f"✨ New User Session Created: {st.session_state.session_id}")

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- GLOBAL SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🧠 Agent OS")
    st.caption("Kubernetes AI & Observability Platform")
    st.markdown("---")
    
    # Navigation Selector
    view_selection = st.radio(
        "Navigation",
        ["🤖 Assistant Chat", "📚 Documentation", "🧪 Eval Suite"],
        index=0,
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.subheader("System Status")
    st.caption(f"**Logfire:** {st.session_state.logfire_status}")
    st.caption(f"**Memory ID:** `{st.session_state.session_id[:8]}...`")
    
    if st.button("🗑️ Reset Session & Memory", use_container_width=True, type="secondary"):
        logfire.warn(f"🗑️ Memory Wipe Triggered: {st.session_state.session_id}")
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

# --- VIEW ROUTER ---
if view_selection == "🤖 Assistant Chat":
    render_chat_view()
elif view_selection == "📚 Documentation":
    render_docs_view(os.path.join(ROOT_DIR, "docs"))
elif view_selection == "🧪 Eval Suite":
    render_evals_view()
