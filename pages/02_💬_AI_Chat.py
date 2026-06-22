# ─────────────────────────────────────────────
#  pages/02_💬_AI_Chat.py — Real-time AI Chat
# ─────────────────────────────────────────────
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from auth.auth_service import require_auth, logout
from database.db import SessionLocal
from database import crud
from ai.chatbot import ChatSession, SUBJECT_PROMPTS
from utils.ui_components import load_css, top_navigation, page_header, sidebar_user_info, info_banner
from utils.helpers import generate_session_id, format_timestamp, export_chat_to_text

st.set_page_config(page_title="AI Chat — AI Doubt Solver Pro", page_icon="💬", layout="wide")
load_css()

# ── Top Navigation ──
top_navigation("AI Chat")


user = require_auth()
if not user:
    st.stop()

# ── Sidebar ───────────────────────────────────
with st.sidebar:
    st.markdown("""<div style="text-align:center; padding:1rem 0 0.5rem;">
  <div style="font-size:1.8rem;">🧠</div>
  <div style="font-size:0.95rem; font-weight:800; background:linear-gradient(135deg,#818CF8,#06B6D4);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">AI Doubt Solver Pro</div>
</div><hr style="border-color:rgba(99,102,241,0.2);">""", unsafe_allow_html=True)
    sidebar_user_info(user)

    st.markdown("#### ⚙️ Chat Settings")
    subject = st.selectbox("Subject", list(SUBJECT_PROMPTS.keys()), key="chat_subject")
    teacher_mode = st.toggle("🎓 Teacher Mode", value=False, key="teacher_mode_toggle")

    if teacher_mode:
        info_banner("Teacher Mode: AI will explain, give examples & test you!", "info")

    st.markdown("---")
    st.markdown("#### 📋 Sessions")

    # Load session list
    with SessionLocal() as db:
        sessions = crud.get_all_sessions(db, user.id)

    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.chat_session_id = generate_session_id()
        st.session_state.chat_history = []
        st.rerun()

    for sid in sessions[:8]:
        if st.button(f"💬 {sid}", key=f"sess_{sid}", use_container_width=True):
            st.session_state.chat_session_id = sid
            with SessionLocal() as db:
                hist = crud.get_chat_history(db, user.id, session_id=sid, limit=50)
            st.session_state.chat_history = []
            for h in reversed(hist):
                st.session_state.chat_history.append({"role": "user", "content": h.question})
                st.session_state.chat_history.append({"role": "assistant", "content": h.answer})
            st.rerun()

    if st.session_state.get("chat_history"):
        export_txt = export_chat_to_text(st.session_state.chat_history)
        st.download_button("📥 Export Chat", export_txt, "chat_export.txt", use_container_width=True)

    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        logout()
        st.switch_page("app.py")

# ── Main Chat UI ──────────────────────────────
page_header("AI Chat", "Ask any question — get step-by-step AI answers", "💬")

# Session indicator
session_id = st.session_state.get("chat_session_id", generate_session_id())
if "chat_session_id" not in st.session_state:
    st.session_state.chat_session_id = session_id

col_info, col_clear = st.columns([4, 1])
with col_info:
    st.markdown(f"""<div style="color:#64748B; font-size:0.8rem; margin-bottom:1rem;">
  Session: <code style="color:#818CF8;">{session_id}</code> &nbsp;·&nbsp;
  Subject: <code style="color:#06B6D4;">{subject}</code> &nbsp;·&nbsp;
  Mode: <code style="color:#{'F59E0B' if teacher_mode else '10B981'}">{'🎓 Teacher' if teacher_mode else '💬 Chat'}</code>
</div>""", unsafe_allow_html=True)
with col_clear:
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# ── Chat History Display ──────────────────────
chat_container = st.container()
with chat_container:
    if not st.session_state.chat_history:
        st.markdown("""
<div style="text-align:center; padding:3rem 1rem; color:#64748B;">
  <div style="font-size:3rem; margin-bottom:1rem;">🤖</div>
  <div style="font-size:1.1rem; font-weight:600; color:#94A3B8;">Ready to help you learn!</div>
  <div style="font-size:0.85rem; margin-top:0.5rem;">Ask any question about Mathematics, Physics, Chemistry, Programming, or anything else.</div>
</div>""", unsafe_allow_html=True)

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "🤖"):
            st.markdown(msg["content"])

# ── Quick Prompts ─────────────────────────────
if not st.session_state.chat_history:
    st.markdown("##### 💡 Try asking:")
    quick = [
        "Explain Newton's laws of motion step by step",
        "How do I solve a quadratic equation?",
        "Write a Python function to check if a number is prime",
        "What is the difference between DNA and RNA?",
    ]
    qcols = st.columns(2)
    for i, q in enumerate(quick):
        with qcols[i % 2]:
            if st.button(q, key=f"quick_{i}", use_container_width=True):
                st.session_state._quick_prompt = q
                st.rerun()

# Handle quick prompt
if "_quick_prompt" in st.session_state:
    prompt_to_send = st.session_state.pop("_quick_prompt")
    st.session_state.chat_history.append({"role": "user", "content": prompt_to_send})
    with st.spinner("🤔 Thinking..."):
        session = ChatSession(subject=subject, teacher_mode=teacher_mode)
        result = session.ask(prompt_to_send, st.session_state.chat_history[:-1])
        answer = result["answer"]
    st.session_state.chat_history.append({"role": "assistant", "content": answer})
    # Save to DB
    with SessionLocal() as db:
        crud.save_chat(db, user.id, session_id, prompt_to_send, answer, subject,
                       "teacher" if teacher_mode else "chat", result.get("tokens", 0))
        crud.add_points(db, user.id, 5)
    st.rerun()

# ── Chat Input ────────────────────────────────
if prompt := st.chat_input("Ask your question... (Ctrl+Enter to send)"):
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🤔 Thinking..."):
            session = ChatSession(subject=subject, teacher_mode=teacher_mode)
            result = session.ask(prompt, st.session_state.chat_history[:-1])
            answer = result["answer"]
        st.markdown(answer)

    st.session_state.chat_history.append({"role": "assistant", "content": answer})

    with SessionLocal() as db:
        crud.save_chat(db, user.id, session_id, prompt, answer, subject,
                       "teacher" if teacher_mode else "chat", result.get("tokens", 0))
        crud.add_points(db, user.id, 5)

    st.rerun()
