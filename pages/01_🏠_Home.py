# ─────────────────────────────────────────────
#  pages/01_🏠_Home.py — Dashboard
# ─────────────────────────────────────────────
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from auth.auth_service import require_auth, logout
from database.db import SessionLocal
from database import crud
from utils.ui_components import load_css, top_navigation, page_header, metric_card, glass_card, info_banner, sidebar_user_info
from utils.helpers import format_timestamp, get_subject_icon, truncate_text, generate_session_id

st.set_page_config(page_title="Home — AI Doubt Solver Pro", page_icon="🏠", layout="wide")
load_css()

# ── Top Navigation ──
top_navigation("Home")


user = require_auth()
if not user:
    st.stop()

# Sidebar
with st.sidebar:
    st.markdown("""<div style="text-align:center; padding:1rem 0 0.5rem;">
  <div style="font-size:2rem;">🧠</div>
  <div style="font-size:1rem; font-weight:800; background:linear-gradient(135deg,#818CF8,#06B6D4);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">AI Doubt Solver Pro</div>
</div><hr style="border-color:rgba(99,102,241,0.2);">""", unsafe_allow_html=True)
    sidebar_user_info(user)
    if st.button("🚪 Logout", use_container_width=True):
        logout()
        st.switch_page("app.py")

# ── Header ────────────────────────────────────
page_header("Dashboard", f"Welcome back, {user.name.split()[0]}! 👋", "🏠")

# ── Metrics ───────────────────────────────────
with SessionLocal() as db:
    total_chats   = crud.count_chats(db, user.id)
    quizzes       = crud.get_user_quizzes(db, user.id, limit=100)
    flashcards    = crud.get_flashcards(db, user.id)
    study_plans   = crud.get_study_plans(db, user.id)
    recent_chats  = crud.get_chat_history(db, user.id, limit=5)
    pdfs          = crud.get_user_pdfs(db, user.id)

quiz_avg = round(sum(q.score / q.total_questions * 100 for q in quizzes) / len(quizzes)) if quizzes else 0

c1, c2, c3, c4, c5 = st.columns(5)
with c1: metric_card("Questions Asked",  str(total_chats),    "💬", color="#6366F1")
with c2: metric_card("Quizzes Taken",    str(len(quizzes)),   "🧠", color="#8B5CF6")
with c3: metric_card("Quiz Avg Score",   f"{quiz_avg}%",      "🎯", color="#06B6D4")
with c4: metric_card("Flashcards",       str(len(flashcards)),"⚡", color="#F59E0B")
with c5: metric_card("Learning Streak",  f"🔥 {user.streak}", "📅", color="#10B981")

st.markdown("<br>", unsafe_allow_html=True)

# ── Main Content ──────────────────────────────
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown("### 📖 Recent Activity")
    if recent_chats:
        for chat in recent_chats:
            icon = get_subject_icon(chat.subject)
            ts = format_timestamp(chat.timestamp)
            st.markdown(f"""
<div class="glass-card" style="padding:1rem; margin-bottom:0.6rem; display:flex; gap:1rem; align-items:flex-start; cursor:default;">
  <div style="font-size:1.5rem;">{icon}</div>
  <div style="flex:1; min-width:0;">
    <div style="color:#F1F5F9; font-weight:600; font-size:0.9rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{truncate_text(chat.question, 80)}</div>
    <div style="color:#64748B; font-size:0.75rem; margin-top:3px;">{chat.subject} · {ts}</div>
  </div>
</div>""", unsafe_allow_html=True)
    else:
        info_banner("No questions yet — go to AI Chat to ask your first question!", "info")

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    qa1, qa2, qa3, qa4 = st.columns(4)
    with qa1:
        if st.button("💬 Ask AI", use_container_width=True):
            st.switch_page("pages/02_💬_AI_Chat.py")
    with qa2:
        if st.button("🧠 Take Quiz", use_container_width=True):
            st.switch_page("pages/05_🧠_Quiz_Generator.py")
    with qa3:
        if st.button("📄 Upload PDF", use_container_width=True):
            st.switch_page("pages/04_📄_PDF_Assistant.py")
    with qa4:
        if st.button("📅 Study Plan", use_container_width=True):
            st.switch_page("pages/06_📅_Study_Planner.py")

with col_right:
    st.markdown("### 🏆 Your Progress")

    # Quiz performance
    if quizzes:
        recent_q = quizzes[:5]
        for q in recent_q:
            pct = round(q.score / q.total_questions * 100)
            color = "#10B981" if pct >= 70 else "#F59E0B" if pct >= 50 else "#EF4444"
            st.markdown(f"""
<div style="background:rgba(30,41,59,0.7); border:1px solid rgba(99,102,241,0.15); border-radius:12px;
  padding:0.75rem 1rem; margin-bottom:0.5rem; display:flex; justify-content:space-between; align-items:center;">
  <div>
    <div style="color:#F1F5F9; font-size:0.85rem; font-weight:600;">{truncate_text(q.topic, 25)}</div>
    <div style="color:#64748B; font-size:0.72rem;">{format_timestamp(q.timestamp)}</div>
  </div>
  <div style="color:{color}; font-weight:700; font-size:1rem;">{pct}%</div>
</div>""", unsafe_allow_html=True)
    else:
        info_banner("Take your first quiz to see scores here!", "info")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📚 Study Plans")
    if study_plans:
        for plan in study_plans[:3]:
            st.markdown(f"""
<div style="background:rgba(30,41,59,0.7); border:1px solid rgba(99,102,241,0.15); border-radius:12px; padding:0.75rem 1rem; margin-bottom:0.5rem;">
  <div style="color:#F1F5F9; font-size:0.85rem; font-weight:600;">{truncate_text(plan.goal, 35)}</div>
  <div style="color:#64748B; font-size:0.72rem; margin:3px 0;">{plan.plan_type.title()} plan · {plan.deadline}</div>
  <div style="background:rgba(30,41,59,0.9); border-radius:100px; height:6px; margin-top:6px; overflow:hidden;">
    <div style="width:{plan.progress_pct}%; height:100%; background:linear-gradient(90deg,#6366F1,#06B6D4); border-radius:100px;"></div>
  </div>
</div>""", unsafe_allow_html=True)
    else:
        info_banner("Create a study plan to track progress!", "info")

# ── Daily Challenge ───────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 🎯 Daily Learning Challenge")
if st.button("✨ Generate Today's Challenge"):
    with st.spinner("Generating your personalized challenge..."):
        from ai.study_planner import generate_daily_challenge
        challenge = generate_daily_challenge("General Knowledge")
        st.session_state["daily_challenge"] = challenge

if "daily_challenge" in st.session_state:
    st.markdown(f"""
<div class="glass-card" style="border-color:rgba(245,158,11,0.3); background:rgba(245,158,11,0.05);">
  {st.session_state['daily_challenge'].replace(chr(10), '<br>')}
</div>""", unsafe_allow_html=True)
