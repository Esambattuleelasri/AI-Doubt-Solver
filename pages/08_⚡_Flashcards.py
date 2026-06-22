# ─────────────────────────────────────────────
#  pages/08_⚡_Flashcards.py — Interactive Flashcards
# ─────────────────────────────────────────────
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from auth.auth_service import require_auth, logout
from database.db import SessionLocal
from database import crud
from ai.flashcard_generator import generate_flashcards_from_topic
from utils.ui_components import load_css, top_navigation, page_header, sidebar_user_info, render_flashcard, info_banner
from utils.helpers import truncate_text

st.set_page_config(page_title="Flashcards — AI Doubt Solver Pro", page_icon="⚡", layout="wide")
load_css()

# ── Top Navigation ──
top_navigation("Flashcards")


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

    # Topic filter
    st.markdown("#### 🔍 Filter by Topic")
    with SessionLocal() as db:
        all_cards = crud.get_flashcards(db, user.id)
    topics = list(set(c.topic for c in all_cards)) if all_cards else []
    selected_topic = st.selectbox("Topic", ["All"] + sorted(topics))
    if st.button("🚪 Logout", use_container_width=True):
        logout()
        st.switch_page("app.py")

page_header("Flashcards", "Study smarter with AI-generated interactive flashcards", "⚡")

tab_study, tab_generate, tab_manage = st.tabs(["📖 Study Cards", "✨ Generate New", "🗂️ Manage"])

# ── Study Tab ──────────────────────────────────
with tab_study:
    with SessionLocal() as db:
        if selected_topic == "All":
            cards = crud.get_flashcards(db, user.id)
        else:
            cards = crud.get_flashcards(db, user.id, topic=selected_topic)

    if not cards:
        info_banner("No flashcards found. Generate some using the '✨ Generate New' tab!", "info")
    else:
        # Flashcard navigator
        if "fc_index" not in st.session_state:
            st.session_state.fc_index = 0
        if "fc_score" not in st.session_state:
            st.session_state.fc_score = {"correct": 0, "total": 0}

        idx = min(st.session_state.fc_index, len(cards) - 1)
        card = cards[idx]

        # Progress
        st.markdown(f"""
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
  <div style="color:#94A3B8; font-size:0.85rem;">Card <strong style="color:#818CF8;">{idx+1}</strong> of <strong style="color:#818CF8;">{len(cards)}</strong></div>
  <div style="color:#94A3B8; font-size:0.85rem;">
    ✅ {st.session_state.fc_score['correct']} correct &nbsp;|&nbsp;
    📚 {st.session_state.fc_score['total']} reviewed
  </div>
</div>""", unsafe_allow_html=True)

        st.progress((idx + 1) / len(cards))

        # Render card
        col_main = st.columns([1, 4, 1])
        with col_main[1]:
            render_flashcard(card.front, card.back, str(card.id))

            st.markdown("<br>", unsafe_allow_html=True)
            # Know it / Don't know buttons
            know_col, unsure_col, nav_col = st.columns([1, 1, 2])
            with know_col:
                if st.button("✅ Got it!", use_container_width=True, key="got_it"):
                    st.session_state.fc_score["correct"] += 1
                    st.session_state.fc_score["total"] += 1
                    st.session_state.fc_index = (idx + 1) % len(cards)
                    # Reset flip state
                    st.session_state.pop(f"card_flipped_{card.id}", None)
                    st.rerun()
            with unsure_col:
                if st.button("🔄 Review again", use_container_width=True, key="review_again"):
                    st.session_state.fc_score["total"] += 1
                    st.session_state.fc_index = (idx + 1) % len(cards)
                    st.session_state.pop(f"card_flipped_{card.id}", None)
                    st.rerun()
            with nav_col:
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("⬅️ Prev", use_container_width=True):
                        st.session_state.fc_index = (idx - 1) % len(cards)
                        st.rerun()
                with c2:
                    if st.button("➡️ Next", use_container_width=True):
                        st.session_state.fc_index = (idx + 1) % len(cards)
                        st.rerun()

        # Session score summary
        if st.session_state.fc_score["total"] > 0:
            pct = round(st.session_state.fc_score["correct"] / st.session_state.fc_score["total"] * 100)
            st.markdown(f"""
<div style="text-align:center; margin-top:1rem; padding:0.75rem; background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.2); border-radius:12px;">
  <span style="color:#10B981; font-weight:600;">Session Score: {pct}% ({st.session_state.fc_score['correct']}/{st.session_state.fc_score['total']})</span>
</div>""", unsafe_allow_html=True)

# ── Generate Tab ───────────────────────────────
with tab_generate:
    st.markdown("### ✨ Generate Flashcards by Topic")
    with st.form("gen_flash_form"):
        topic_inp = st.text_input("Topic", placeholder="e.g. Python OOP, Photosynthesis, Newton's Laws")
        col_a, col_b = st.columns(2)
        with col_a:
            count_inp = st.slider("Number of cards", 5, 25, 10)
        with col_b:
            diff_inp = st.selectbox("Difficulty", ["easy", "medium", "hard"])
        gen_submit = st.form_submit_button("⚡ Generate Flashcards", use_container_width=True)

    if gen_submit:
        if not topic_inp.strip():
            st.error("Please enter a topic!")
        else:
            with st.spinner(f"Generating {count_inp} flashcards on {topic_inp}..."):
                new_cards = generate_flashcards_from_topic(topic_inp, count_inp, diff_inp)
                if new_cards:
                    with SessionLocal() as db:
                        crud.create_flashcards(db, user.id, new_cards, topic_inp)
                    st.success(f"✅ Created {len(new_cards)} flashcards on '{topic_inp}'!")
                    st.rerun()
                else:
                    st.error("Failed to generate flashcards. Please try again.")

# ── Manage Tab ─────────────────────────────────
with tab_manage:
    st.markdown("### 🗂️ All Flashcards")
    with SessionLocal() as db:
        manage_cards = crud.get_flashcards(db, user.id)

    if not manage_cards:
        info_banner("No flashcards yet.", "info")
    else:
        st.markdown(f"**Total: {len(manage_cards)} cards**")
        # Group by topic
        by_topic = {}
        for c in manage_cards:
            by_topic.setdefault(c.topic, []).append(c)

        for topic_name, t_cards in by_topic.items():
            with st.expander(f"📚 {topic_name} ({len(t_cards)} cards)"):
                for card in t_cards:
                    col_q, col_del = st.columns([5, 1])
                    with col_q:
                        st.markdown(f"**Q:** {card.front}")
                        st.markdown(f"**A:** {truncate_text(card.back, 80)}")
                        st.markdown("---")
                    with col_del:
                        if st.button("🗑️", key=f"del_{card.id}", help="Delete this card"):
                            with SessionLocal() as db:
                                crud.delete_flashcard(db, card.id, user.id)
                            st.rerun()
