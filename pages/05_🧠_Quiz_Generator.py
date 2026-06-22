# ─────────────────────────────────────────────
#  pages/05_🧠_Quiz_Generator.py — AI Quiz
# ─────────────────────────────────────────────
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from auth.auth_service import require_auth, logout
from database.db import SessionLocal
from database import crud
from ai.quiz_generator import generate_quiz, grade_quiz
from utils.ui_components import load_css, top_navigation, page_header, sidebar_user_info, score_display, info_banner
from utils.helpers import get_difficulty_color

st.set_page_config(page_title="Quiz Generator — AI Doubt Solver Pro", page_icon="🧠", layout="wide")
load_css()

# ── Top Navigation ──
top_navigation("Quiz")


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

page_header("Quiz Generator", "Test your knowledge with AI-generated quizzes", "🧠")

# ── State ─────────────────────────────────────
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "quiz_result" not in st.session_state:
    st.session_state.quiz_result = None
if "quiz_config" not in st.session_state:
    st.session_state.quiz_config = {}

# ── Quiz Configuration ────────────────────────
if not st.session_state.quiz_questions:
    st.markdown("### ⚙️ Configure Your Quiz")
    with st.form("quiz_config_form"):
        col1, col2 = st.columns(2)
        with col1:
            topic = st.text_input("📚 Topic", placeholder="e.g. Python functions, Photosynthesis, Algebra")
            quiz_type = st.selectbox("📝 Quiz Type", ["mcq", "truefalse", "fillin"],
                                     format_func=lambda x: {"mcq": "Multiple Choice (MCQ)",
                                                             "truefalse": "True / False",
                                                             "fillin": "Fill in the Blank"}[x])
        with col2:
            difficulty = st.selectbox("🎯 Difficulty", ["easy", "medium", "hard"])
            num_q = st.slider("Number of Questions", 3, 15, 5)

        generate_btn = st.form_submit_button("🚀 Generate Quiz", use_container_width=True)

    if generate_btn:
        if not topic.strip():
            st.error("Please enter a topic!")
        else:
            with st.spinner(f"🤖 Generating {num_q} {difficulty} {quiz_type} questions on {topic}..."):
                questions = generate_quiz(topic, quiz_type, difficulty, num_q)
                if questions:
                    st.session_state.quiz_questions = questions
                    st.session_state.quiz_answers = {}
                    st.session_state.quiz_result = None
                    st.session_state.quiz_config = {
                        "topic": topic, "type": quiz_type,
                        "difficulty": difficulty, "count": len(questions)
                    }
                    st.rerun()
                else:
                    st.error("Failed to generate quiz. Please try again.")

    # Recent quiz history
    st.markdown("---")
    st.markdown("### 📊 Recent Quizzes")
    with SessionLocal() as db:
        past_quizzes = crud.get_user_quizzes(db, user.id, limit=5)
    if past_quizzes:
        for q in past_quizzes:
            pct = round(q.score / q.total_questions * 100)
            color = get_difficulty_color(q.difficulty)
            d_color = "#10B981" if pct >= 70 else "#F59E0B" if pct >= 50 else "#EF4444"
            st.markdown(f"""
<div style="background:rgba(30,41,59,0.7); border:1px solid rgba(99,102,241,0.15); border-radius:12px; padding:0.75rem 1rem; margin-bottom:0.5rem; display:flex; justify-content:space-between; align-items:center;">
  <div>
    <div style="color:#F1F5F9; font-weight:600; font-size:0.9rem;">{q.topic}</div>
    <div style="color:#64748B; font-size:0.75rem;">
      <span style="color:{color};">{q.difficulty.title()}</span> · {q.quiz_type.upper()} · {q.total_questions}Q
    </div>
  </div>
  <div style="color:{d_color}; font-weight:700; font-size:1.1rem;">{pct}%</div>
</div>""", unsafe_allow_html=True)
    else:
        info_banner("No quizzes taken yet — generate one above!", "info")

else:
    # ── Active Quiz ───────────────────────────
    cfg = st.session_state.quiz_config
    diff_color = get_difficulty_color(cfg.get("difficulty", "medium"))

    col_title, col_btn = st.columns([3, 1])
    with col_title:
        st.markdown(f"""
<div style="margin-bottom:1rem;">
  <span style="color:#F1F5F9; font-size:1.2rem; font-weight:700;">📚 {cfg.get('topic','Quiz')}</span>
  <span style="margin-left:0.75rem; background:rgba(99,102,241,0.15); color:#818CF8; border:1px solid rgba(99,102,241,0.3); padding:2px 8px; border-radius:100px; font-size:0.75rem;">{cfg.get('type','MCQ').upper()}</span>
  <span style="margin-left:0.5rem; color:{diff_color}; border:1px solid {diff_color}40; background:{diff_color}20; padding:2px 8px; border-radius:100px; font-size:0.75rem;">{cfg.get('difficulty','medium').title()}</span>
</div>""", unsafe_allow_html=True)
    with col_btn:
        if st.button("🗑️ New Quiz", use_container_width=True):
            st.session_state.quiz_questions = []
            st.session_state.quiz_answers = {}
            st.session_state.quiz_result = None
            st.rerun()

    if st.session_state.quiz_result:
        # ── Results ───────────────────────────
        res = st.session_state.quiz_result
        score_display(res["score"], res["total"], res["grade"])
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📋 Answer Review")
        for i, r in enumerate(res["results"]):
            icon = "✅" if r["is_correct"] else "❌"
            bg = "rgba(16,185,129,0.08)" if r["is_correct"] else "rgba(239,68,68,0.08)"
            border = "rgba(16,185,129,0.3)" if r["is_correct"] else "rgba(239,68,68,0.3)"
            st.markdown(f"""
<div style="background:{bg}; border:1px solid {border}; border-radius:12px; padding:1rem 1.25rem; margin-bottom:0.75rem;">
  <div style="color:#F1F5F9; font-weight:600; margin-bottom:0.5rem;">{icon} Q{i+1}. {r['question']}</div>
  <div style="color:#94A3B8; font-size:0.85rem;">Your answer: <span style="color:{'#10B981' if r['is_correct'] else '#EF4444'}; font-weight:600;">{r['user_answer'] or 'Not answered'}</span></div>
  {'<div style="color:#94A3B8; font-size:0.85rem;">Correct: <span style="color:#10B981; font-weight:600;">' + r['correct_answer'] + '</span></div>' if not r['is_correct'] else ''}
  {f'<div style="color:#64748B; font-size:0.8rem; margin-top:0.5rem; border-top:1px solid rgba(99,102,241,0.1); padding-top:0.5rem;">💡 {r["explanation"]}</div>' if r.get("explanation") else ''}
</div>""", unsafe_allow_html=True)

        if st.button("🔄 Take Another Quiz", use_container_width=True):
            st.session_state.quiz_questions = []
            st.session_state.quiz_answers = {}
            st.session_state.quiz_result = None
            st.rerun()
    else:
        # ── Quiz Questions ────────────────────
        questions = st.session_state.quiz_questions
        answered = len(st.session_state.quiz_answers)
        st.progress(answered / len(questions), text=f"Answered {answered}/{len(questions)}")

        with st.form("quiz_form"):
            for i, q in enumerate(questions):
                st.markdown(f"""
<div style="background:rgba(30,41,59,0.7); border:1px solid rgba(99,102,241,0.15); border-radius:16px; padding:1.25rem 1.5rem; margin-bottom:1rem;">
  <div style="color:#818CF8; font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:0.5rem;">Question {i+1}</div>
  <div style="color:#F1F5F9; font-size:1rem; font-weight:600; line-height:1.5;">{q['question']}</div>
</div>""", unsafe_allow_html=True)

                if q.get("options"):
                    ans = st.radio(
                        f"Select answer for Q{i+1}",
                        options=q["options"],
                        key=f"q_{i}",
                        label_visibility="collapsed",
                    )
                    st.session_state.quiz_answers[i] = ans
                else:
                    ans = st.text_input(f"Your answer for Q{i+1}", key=f"q_{i}", placeholder="Type your answer...")
                    if ans:
                        st.session_state.quiz_answers[i] = ans

            submitted = st.form_submit_button("📊 Submit Quiz", use_container_width=True)

        if submitted:
            result = grade_quiz(questions, st.session_state.quiz_answers)
            st.session_state.quiz_result = result
            # Save to DB (grade_quiz already scored locally; save summary)
            with SessionLocal() as db:
                quiz_db = crud.create_quiz(
                    db, user.id, cfg["topic"], cfg["type"], cfg["difficulty"], len(questions)
                )
                crud.add_quiz_questions(db, quiz_db.id, questions)
                # Map positional answers to DB question IDs
                from database.models import QuizQuestion as QQModel
                db_qs = db.query(QQModel).filter(QQModel.quiz_id == quiz_db.id).all()
                id_answers = {str(q.id): st.session_state.quiz_answers.get(i, "") for i, q in enumerate(db_qs)}
                crud.submit_quiz(db, quiz_db.id, id_answers)
                crud.add_points(db, user.id, result["score"] * 10)
            st.rerun()
