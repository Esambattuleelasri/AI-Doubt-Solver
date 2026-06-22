# ─────────────────────────────────────────────
#  pages/06_📅_Study_Planner.py — AI Study Planner
# ─────────────────────────────────────────────
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from auth.auth_service import require_auth, logout
from database.db import SessionLocal
from database import crud
from ai.study_planner import generate_study_plan, get_todays_tasks
from utils.ui_components import load_css, top_navigation, page_header, sidebar_user_info, progress_bar_custom, info_banner
from utils.helpers import get_subject_icon

st.set_page_config(page_title="Study Planner — AI Doubt Solver Pro", page_icon="📅", layout="wide")
load_css()

# ── Top Navigation ──
top_navigation("Study Plan")


user = require_auth()
if not user:
    st.stop()

with st.sidebar:
    st.markdown("""<div style="text-align:center; padding:1rem 0 0.5rem;">
  <div style="font-size:1.8rem;">🧠</div>
  <div style="font-size:0.95rem; font-weight:800; background:linear-gradient(135deg,#818CF8,#06B6D4);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;">AI Doubt Solver Pro</div>
</div><hr style="border-color:rgba(99,102,241,0.2);">""", unsafe_allow_html=True)
    sidebar_user_info(user)
    if st.button("🚪 Logout", use_container_width=True):
        logout()
        st.switch_page("app.py")

page_header("Study Planner", "AI-generated study schedules to help you reach your goals", "📅")

tab_new, tab_plans = st.tabs(["✨ Create New Plan", "📋 My Plans"])

with tab_new:
    st.markdown("### 🎯 What do you want to achieve?")
    with st.form("planner_form"):
        col1, col2 = st.columns(2)
        with col1:
            goal = st.text_area("Learning Goal", placeholder="e.g. Prepare for Machine Learning exam\nLearn Python from scratch\nRevise Organic Chemistry", height=100)
            subject = st.text_input("Subject / Topic", placeholder="e.g. Machine Learning, Python, Chemistry")
        with col2:
            plan_type = st.selectbox("Plan Duration", ["daily", "weekly", "monthly"],
                                     format_func=lambda x: {"daily": "📅 Daily (1 day)", "weekly": "📆 Weekly (7 days)", "monthly": "🗓️ Monthly (30 days)"}[x])
            deadline = st.text_input("Deadline", placeholder="e.g. 2 weeks, December 15, 3 months")
            hours = st.slider("Study hours per day", 1, 12, 4)

        submitted = st.form_submit_button("🚀 Generate My Study Plan", use_container_width=True)

    if submitted:
        if not goal.strip():
            st.error("Please enter your learning goal!")
        else:
            with st.spinner("🤖 Creating your personalized study plan..."):
                plan = generate_study_plan(goal, subject, deadline, plan_type, hours)
                st.session_state["current_plan"] = plan
                st.session_state["plan_config"] = {
                    "goal": goal, "subject": subject, "deadline": deadline,
                    "plan_type": plan_type, "hours": hours
                }
                # Save to DB
                with SessionLocal() as db:
                    crud.create_study_plan(db, user.id, goal, subject, deadline, plan_type, plan)
                st.success("✅ Study plan created!")

    if "current_plan" in st.session_state:
        plan = st.session_state["current_plan"]
        cfg = st.session_state.get("plan_config", {})

        # Overview card
        st.markdown(f"""
<div class="glass-card" style="margin:1rem 0;">
  <div style="font-size:1.1rem; font-weight:700; color:#818CF8; margin-bottom:0.75rem;">📋 Plan Overview</div>
  <div style="color:#F1F5F9; line-height:1.7;">{plan.get('overview','Your personalized study plan is ready.')}</div>
  <div style="display:flex; gap:1.5rem; margin-top:1rem; flex-wrap:wrap;">
    <div style="color:#64748B; font-size:0.82rem;">📚 <span style="color:#94A3B8;">{plan.get('total_topics',0)} topics</span></div>
    <div style="color:#64748B; font-size:0.82rem;">⏰ <span style="color:#94A3B8;">{cfg.get('hours',4)}h/day</span></div>
    <div style="color:#64748B; font-size:0.82rem;">📅 <span style="color:#94A3B8;">{cfg.get('deadline','TBD')}</span></div>
  </div>
</div>""", unsafe_allow_html=True)

        # Schedule
        st.markdown("### 📅 Schedule")
        schedule = plan.get("schedule", [])
        if schedule:
            if cfg.get("plan_type") == "weekly":
                cols_per_row = 4
                for row_start in range(0, len(schedule), cols_per_row):
                    row = schedule[row_start:row_start + cols_per_row]
                    cols = st.columns(len(row))
                    for col, day in zip(cols, row):
                        priority_color = {"high": "#EF4444", "medium": "#F59E0B", "low": "#10B981"}.get(day.get("priority", "medium"), "#6366F1")
                        with col:
                            st.markdown(f"""
<div style="background:rgba(30,41,59,0.8); border:1px solid rgba(99,102,241,0.15); border-radius:12px; padding:0.875rem; height:100%;">
  <div style="color:#818CF8; font-size:0.75rem; font-weight:700; margin-bottom:0.4rem;">{day.get('day','')}</div>
  <div style="color:#64748B; font-size:0.7rem; margin-bottom:0.6rem;">{day.get('date','')}</div>
  {''.join(f'<div style="color:#F1F5F9; font-size:0.78rem; margin-bottom:2px;">• {t}</div>' for t in day.get('topics',[])[:2])}
  <div style="color:{priority_color}; font-size:0.7rem; margin-top:0.5rem; font-weight:600; text-transform:uppercase;">⬥ {day.get('priority','medium')}</div>
  <div style="color:#64748B; font-size:0.7rem;">⏰ {day.get('duration_hours',3)}h</div>
</div>""", unsafe_allow_html=True)
            else:
                for i, day in enumerate(schedule[:10]):
                    with st.expander(f"{day.get('day',f'Day {i+1}')} — {day.get('date','')}"):
                        topics = day.get("topics", [])
                        tasks = day.get("tasks", [])
                        col_t, col_k = st.columns(2)
                        with col_t:
                            st.markdown("**📚 Topics:**")
                            for t in topics:
                                st.markdown(f"- {t}")
                        with col_k:
                            st.markdown("**✅ Tasks:**")
                            for t in tasks:
                                st.markdown(f"- {t}")

        # Tips & Resources
        col_tips, col_res = st.columns(2)
        with col_tips:
            if plan.get("tips"):
                st.markdown("### 💡 Study Tips")
                for tip in plan["tips"]:
                    st.markdown(f"""<div style="padding:0.4rem 0; border-bottom:1px solid rgba(99,102,241,0.1); color:#94A3B8; font-size:0.85rem;">💡 {tip}</div>""", unsafe_allow_html=True)
        with col_res:
            if plan.get("resources"):
                st.markdown("### 📚 Resources")
                for res in plan["resources"]:
                    st.markdown(f"""<div style="padding:0.4rem 0; border-bottom:1px solid rgba(99,102,241,0.1); color:#94A3B8; font-size:0.85rem;">📖 {res}</div>""", unsafe_allow_html=True)

        # Export
        import json
        st.download_button("📥 Download Plan (JSON)", json.dumps(plan, indent=2), "study_plan.json", "application/json")

with tab_plans:
    st.markdown("### 📋 Your Study Plans")
    with SessionLocal() as db:
        plans = crud.get_study_plans(db, user.id)

    if not plans:
        info_banner("No study plans created yet. Create one in the tab above!", "info")
    else:
        for plan_db in plans:
            with st.expander(f"📅 {plan_db.goal[:60]}... — {plan_db.plan_type.title()}"):
                col_info, col_prog = st.columns([2, 1])
                with col_info:
                    st.markdown(f"**Subject:** {plan_db.subject or 'General'}")
                    st.markdown(f"**Deadline:** {plan_db.deadline}")
                    st.markdown(f"**Type:** {plan_db.plan_type.title()}")
                with col_prog:
                    progress_bar_custom("Progress", plan_db.progress_pct)
                    new_prog = st.slider("Update progress", 0, 100, int(plan_db.progress_pct), key=f"prog_{plan_db.id}")
                    if st.button("💾 Save", key=f"save_{plan_db.id}"):
                        with SessionLocal() as db:
                            crud.update_plan_progress(db, plan_db.id, new_prog)
                        st.success("Updated!")
                        st.rerun()
