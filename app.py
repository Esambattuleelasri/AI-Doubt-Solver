# ─────────────────────────────────────────────
#  app.py — Streamlit Entry Point & Login/Register
# ─────────────────────────────────────────────
import streamlit as st
import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(__file__))

from database.db import init_db
from auth.auth_service import is_authenticated, login_user, register_user, get_current_user_from_session
from utils.ui_components import load_css
from utils.helpers import generate_session_id

# ── Page Config ───────────────────────────────
st.set_page_config(
    page_title="AI Doubt Solver Pro",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "AI Doubt Solver Pro — Your intelligent learning companion.",
    },
)

# ── Init DB on first run ──────────────────────
@st.cache_resource
def initialize():
    init_db()
    return True

initialize()
load_css()

# ── Session defaults ──────────────────────────
if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "chat_session_id" not in st.session_state:
    st.session_state.chat_session_id = generate_session_id()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ── If logged in, redirect to Home ────────────
if is_authenticated():
    user = get_current_user_from_session()

    # Sidebar
    with st.sidebar:
        st.markdown("""
<div style="text-align:center; padding: 1rem 0 0.5rem 0;">
  <div style="font-size:2.5rem;">🧠</div>
  <div style="font-size:1.1rem; font-weight:800; background:linear-gradient(135deg,#818CF8,#06B6D4);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;">
    AI Doubt Solver Pro
  </div>
  <div style="color:#64748B; font-size:0.75rem; margin-top:2px;">Your AI Learning Companion</div>
</div>
<hr style="border-color:rgba(99,102,241,0.2); margin:0.75rem 0;">
""", unsafe_allow_html=True)

        from utils.ui_components import sidebar_user_info
        sidebar_user_info(user)

        st.markdown("""
<div style="color:#64748B; font-size:0.72rem; text-align:center; padding:0.5rem; margin-top:auto;">
  Powered by GPT-4o & LangChain
</div>
""", unsafe_allow_html=True)

    st.switch_page("pages/01_🏠_Home.py")

else:
    # ── Auth UI ───────────────────────────────
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
<div style="text-align:center; padding:3rem 0 2rem 0; animation:fadeIn 0.6s ease;">
  <div style="font-size:4rem; margin-bottom:0.75rem; animation:glow 3s ease infinite;">🧠</div>
  <h1 style="font-size:2.5rem; font-weight:900; margin:0;
    background:linear-gradient(135deg,#818CF8,#06B6D4);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;">
    AI Doubt Solver Pro
  </h1>
  <p style="color:#94A3B8; font-size:1rem; margin:0.75rem 0 0 0;">
    Your intelligent AI-powered learning companion
  </p>
</div>

<div style="display:flex; justify-content:center; gap:1.5rem; margin:1.5rem 0 2rem 0; flex-wrap:wrap;">
  <div style="text-align:center; color:#94A3B8; font-size:0.85rem;">💬 <br>AI Chat</div>
  <div style="text-align:center; color:#94A3B8; font-size:0.85rem;">🖼️ <br>Image Solver</div>
  <div style="text-align:center; color:#94A3B8; font-size:0.85rem;">📄 <br>PDF Assistant</div>
  <div style="text-align:center; color:#94A3B8; font-size:0.85rem;">🧠 <br>Quiz Generator</div>
  <div style="text-align:center; color:#94A3B8; font-size:0.85rem;">📅 <br>Study Planner</div>
  <div style="text-align:center; color:#94A3B8; font-size:0.85rem;">📊 <br>Analytics</div>
</div>
""", unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["🔑 Login", "📝 Register"])

        with tab_login:
            st.markdown('<div style="margin-top:1rem;"></div>', unsafe_allow_html=True)
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="you@example.com", key="login_email")
                password = st.text_input("Password", type="password", placeholder="••••••••", key="login_pass")
                submitted = st.form_submit_button("🚀 Sign In", use_container_width=True)

                if submitted:
                    if not email or not password:
                        st.error("Please fill in all fields.")
                    else:
                        result = login_user(email, password)
                        if result["success"]:
                            st.session_state.auth_token = result["token"]
                            st.success("Welcome back! Redirecting...")
                            st.rerun()
                        else:
                            st.error(result["message"])

            st.markdown("""
<div style="text-align:center; margin-top:1rem;">
  <span style="color:#64748B; font-size:0.8rem;">
    Demo account: demo@ai.com / demo1234
  </span>
</div>""", unsafe_allow_html=True)

        with tab_register:
            st.markdown('<div style="margin-top:1rem;"></div>', unsafe_allow_html=True)
            with st.form("register_form"):
                name = st.text_input("Full Name", placeholder="Arjun Kumar", key="reg_name")
                email_r = st.text_input("Email", placeholder="you@example.com", key="reg_email")
                pass_r = st.text_input("Password", type="password", placeholder="Min. 8 characters", key="reg_pass")
                pass_r2 = st.text_input("Confirm Password", type="password", placeholder="Repeat password", key="reg_pass2")
                submitted_r = st.form_submit_button("✨ Create Account", use_container_width=True)

                if submitted_r:
                    if not all([name, email_r, pass_r, pass_r2]):
                        st.error("Please fill in all fields.")
                    elif pass_r != pass_r2:
                        st.error("Passwords do not match.")
                    elif len(pass_r) < 8:
                        st.error("Password must be at least 8 characters.")
                    else:
                        result = register_user(name, email_r, pass_r)
                        if result["success"]:
                            st.success("Account created! Please log in.")
                        else:
                            st.error(result["message"])

        st.markdown("""
<div style="text-align:center; margin-top:2rem; padding:1rem; background:rgba(99,102,241,0.05); border:1px solid rgba(99,102,241,0.15); border-radius:12px;">
  <div style="color:#64748B; font-size:0.78rem; line-height:1.8;">
    🔒 Secure JWT Authentication &nbsp;|&nbsp; 🚀 Powered by GPT-4o &nbsp;|&nbsp; 📱 All devices
  </div>
</div>
""", unsafe_allow_html=True)
