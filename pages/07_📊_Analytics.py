# ─────────────────────────────────────────────
#  pages/07_📊_Analytics.py — Learning Analytics
# ─────────────────────────────────────────────
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from auth.auth_service import require_auth, logout
from database.db import SessionLocal
from database import crud
from utils.ui_components import load_css, top_navigation, page_header, sidebar_user_info, metric_card
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from collections import Counter
from datetime import datetime, timedelta

st.set_page_config(page_title="Analytics — AI Doubt Solver Pro", page_icon="📊", layout="wide")
load_css()

# ── Top Navigation ──
top_navigation("Analytics")


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

page_header("Analytics", "Visualize your learning journey and track progress", "📊")

PLOTLY_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#94A3B8"),
    title_font=dict(color="#F1F5F9", size=16),
    legend=dict(bgcolor="rgba(30,41,59,0.7)", bordercolor="rgba(99,102,241,0.3)", borderwidth=1),
)
GRID_STYLE = dict(gridcolor="rgba(99,102,241,0.1)", zerolinecolor="rgba(99,102,241,0.2)")

# ── Load Data ─────────────────────────────────
with SessionLocal() as db:
    all_chats   = crud.get_chat_history(db, user.id, limit=500)
    all_quizzes = crud.get_user_quizzes(db, user.id, limit=200)
    flashcards  = crud.get_flashcards(db, user.id)
    study_plans = crud.get_study_plans(db, user.id)

total_doubts = len(all_chats)
total_quizzes = len(all_quizzes)
quiz_avg = round(sum(q.score / q.total_questions * 100 for q in all_quizzes) / len(all_quizzes)) if all_quizzes else 0
total_fc = len(flashcards)

# ── Top Metrics ───────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1: metric_card("Total Doubts", str(total_doubts), "💬", color="#6366F1")
with c2: metric_card("Quizzes Taken", str(total_quizzes), "🧠", color="#8B5CF6")
with c3: metric_card("Avg Quiz Score", f"{quiz_avg}%", "🎯", color="#06B6D4")
with c4: metric_card("Flashcards", str(total_fc), "⚡", color="#F59E0B")

st.markdown("<br>", unsafe_allow_html=True)

# ── Charts Row 1 ──────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 📚 Doubts by Subject")
    if all_chats:
        subject_counts = Counter(c.subject for c in all_chats)
        df_subj = pd.DataFrame(subject_counts.items(), columns=["Subject", "Count"])
        fig = px.pie(df_subj, values="Count", names="Subject",
                     color_discrete_sequence=["#6366F1","#8B5CF6","#06B6D4","#F59E0B","#10B981","#EF4444","#EC4899"],
                     hole=0.4)
        fig.update_layout(**PLOTLY_THEME, height=300, margin=dict(t=20,b=10,l=10,r=10))
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown('<div style="color:#64748B; text-align:center; padding:3rem;">No chat data yet.</div>', unsafe_allow_html=True)

with col2:
    st.markdown("#### 📈 Quiz Performance Over Time")
    if all_quizzes:
        df_quiz = pd.DataFrame([{
            "Date": q.timestamp.strftime("%b %d") if q.timestamp else "",
            "Score %": round(q.score / q.total_questions * 100),
            "Topic": q.topic[:20],
            "Difficulty": q.difficulty,
        } for q in reversed(all_quizzes)])
        fig2 = px.line(df_quiz, x="Date", y="Score %", markers=True,
                       color_discrete_sequence=["#6366F1"],
                       hover_data={"Topic": True, "Difficulty": True})
        fig2.add_hline(y=70, line_dash="dash", line_color="#10B981",
                       annotation_text="Pass (70%)", annotation_position="right")
        fig2.update_layout(**PLOTLY_THEME, height=300, margin=dict(t=20,b=10,l=10,r=10),
                           xaxis=GRID_STYLE, yaxis={**GRID_STYLE, "range":[0,105]})
        fig2.update_traces(line=dict(width=2.5), marker=dict(size=8, color="#818CF8"))
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.markdown('<div style="color:#64748B; text-align:center; padding:3rem;">No quiz data yet.</div>', unsafe_allow_html=True)

# ── Charts Row 2 ──────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.markdown("#### 🕐 Learning Activity (Last 14 Days)")
    if all_chats:
        today = datetime.utcnow()
        days_list = [(today - timedelta(days=i)).strftime("%b %d") for i in range(13, -1, -1)]
        day_counts = Counter()
        for chat in all_chats:
            if chat.timestamp and (today - chat.timestamp).days <= 13:
                day_counts[chat.timestamp.strftime("%b %d")] += 1
        counts = [day_counts.get(d, 0) for d in days_list]
        fig3 = go.Figure(go.Bar(
            x=days_list, y=counts,
            marker=dict(color=counts, colorscale=[[0,"rgba(99,102,241,0.3)"],[1,"#6366F1"]]),
        ))
        fig3.update_layout(**PLOTLY_THEME, height=280, margin=dict(t=20,b=10,l=10,r=10),
                           xaxis={**GRID_STYLE, "tickangle": -45}, yaxis=GRID_STYLE)
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.markdown('<div style="color:#64748B; text-align:center; padding:3rem;">No activity yet.</div>', unsafe_allow_html=True)

with col4:
    st.markdown("#### 🎯 Quiz Score Distribution")
    if all_quizzes:
        scores = [round(q.score / q.total_questions * 100) for q in all_quizzes]
        fig4 = go.Figure(go.Histogram(
            x=scores, nbinsx=10, name="Score %",
            marker=dict(
                color=scores,
                colorscale=[[0,"#EF4444"],[0.5,"#F59E0B"],[1,"#10B981"]],
                line=dict(color="rgba(99,102,241,0.3)", width=1),
            )
        ))
        fig4.update_layout(**PLOTLY_THEME, height=280, margin=dict(t=20,b=10,l=10,r=10),
                           xaxis={**GRID_STYLE, "title":"Score %"}, yaxis={**GRID_STYLE, "title":"Count"})
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.markdown('<div style="color:#64748B; text-align:center; padding:3rem;">No quiz data yet.</div>', unsafe_allow_html=True)

# ── Difficulty Breakdown ──────────────────────
if all_quizzes:
    st.markdown("#### 🏋️ Performance by Difficulty")
    diff_data = {}
    for q in all_quizzes:
        d = q.difficulty
        if d not in diff_data:
            diff_data[d] = []
        diff_data[d].append(round(q.score / q.total_questions * 100))

    diff_avgs = {d: round(sum(v)/len(v)) for d, v in diff_data.items()}
    df_diff = pd.DataFrame(diff_avgs.items(), columns=["Difficulty", "Avg Score"])
    fig5 = px.bar(df_diff, x="Difficulty", y="Avg Score",
                  color="Difficulty",
                  color_discrete_map={"easy": "#10B981", "medium": "#F59E0B", "hard": "#EF4444"},
                  text="Avg Score")
    fig5.update_traces(texttemplate="%{text}%", textposition="outside")
    fig5.update_layout(**PLOTLY_THEME, height=280, margin=dict(t=20,b=10,l=10,r=10),
                       xaxis=GRID_STYLE, yaxis={**GRID_STYLE, "range":[0,110]},
                       showlegend=False)
    st.plotly_chart(fig5, use_container_width=True)

# ── Subject Performance Table ─────────────────
if all_quizzes:
    st.markdown("#### 📋 Subject-wise Quiz Performance")
    subject_quiz_data = {}
    for q in all_quizzes:
        subj = q.topic
        if subj not in subject_quiz_data:
            subject_quiz_data[subj] = {"scores": [], "count": 0}
        subject_quiz_data[subj]["scores"].append(round(q.score / q.total_questions * 100))
        subject_quiz_data[subj]["count"] += 1

    rows = []
    for topic, data in sorted(subject_quiz_data.items(), key=lambda x: -sum(x[1]["scores"])/len(x[1]["scores"])):
        avg = round(sum(data["scores"]) / len(data["scores"]))
        grade = "🟢" if avg >= 70 else "🟡" if avg >= 50 else "🔴"
        rows.append({"Topic": topic, "Quizzes": data["count"], "Avg Score": f"{avg}%", "Status": grade})

    df_table = pd.DataFrame(rows)
    st.dataframe(df_table, use_container_width=True, hide_index=True,
                 column_config={"Status": st.column_config.TextColumn("Status")})
