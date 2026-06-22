# ─────────────────────────────────────────────
#  pages/04_📄_PDF_Assistant.py — PDF Q&A
# ─────────────────────────────────────────────
import streamlit as st
import sys, os, uuid
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from auth.auth_service import require_auth, logout
from database.db import SessionLocal
from database import crud
from ai.pdf_assistant import (extract_text_from_pdf, build_vector_store,
                               ask_pdf, summarize_pdf, extract_key_points,
                               generate_notes_from_pdf)
from ai.flashcard_generator import generate_flashcards
from utils.ui_components import load_css, top_navigation, page_header, sidebar_user_info, info_banner
from utils.helpers import save_uploaded_file, file_size_str

st.set_page_config(page_title="PDF Assistant — AI Doubt Solver Pro", page_icon="📄", layout="wide")
load_css()

# ── Top Navigation ──
top_navigation("PDF")


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

    st.markdown("### 📚 Your PDFs")
    with SessionLocal() as db:
        user_pdfs = crud.get_user_pdfs(db, user.id)

    if user_pdfs:
        selected_pdf_id = st.selectbox(
            "Load saved PDF",
            options=[None] + [p.id for p in user_pdfs],
            format_func=lambda x: "— Select —" if x is None else next((p.original_name[:30] for p in user_pdfs if p.id == x), str(x)),
        )
        if selected_pdf_id and st.button("📂 Load Selected"):
            with SessionLocal() as db:
                pdf_doc = crud.get_pdf_by_id(db, selected_pdf_id, user.id)
            if pdf_doc:
                st.session_state["pdf_text"] = pdf_doc.text_content
                st.session_state["pdf_name"] = pdf_doc.original_name
                st.session_state["pdf_vector_path"] = pdf_doc.vector_index_path
                st.success(f"Loaded: {pdf_doc.original_name}")
                st.rerun()
    else:
        st.markdown('<div style="color:#64748B; font-size:0.8rem;">No PDFs uploaded yet.</div>', unsafe_allow_html=True)

    if st.button("🚪 Logout", use_container_width=True):
        logout()
        st.switch_page("app.py")

page_header("PDF Assistant", "Upload PDFs and ask questions, get summaries & notes", "📄")

# ── Upload Section ────────────────────────────
st.markdown("#### 📤 Upload PDF")
uploaded_pdf = st.file_uploader("Drop your PDF here", type=["pdf"])

if uploaded_pdf:
    size_str = file_size_str(uploaded_pdf.size)
    st.markdown(f"""
<div style="background:rgba(99,102,241,0.08); border:1px solid rgba(99,102,241,0.2); border-radius:12px; padding:0.75rem 1rem; margin:0.5rem 0; display:flex; gap:0.75rem; align-items:center;">
  <span style="font-size:1.5rem;">📄</span>
  <div>
    <div style="color:#F1F5F9; font-weight:600; font-size:0.9rem;">{uploaded_pdf.name}</div>
    <div style="color:#64748B; font-size:0.75rem;">{size_str}</div>
  </div>
</div>""", unsafe_allow_html=True)

    if st.button("🔄 Process PDF", use_container_width=False):
        with st.spinner("📖 Extracting text and building knowledge base..."):
            path = save_uploaded_file(uploaded_pdf)
            text, pages = extract_text_from_pdf(path)
            if text:
                doc_id = uuid.uuid4().hex[:8]
                vector_path = build_vector_store(text, doc_id)
                st.session_state["pdf_text"] = text
                st.session_state["pdf_name"] = uploaded_pdf.name
                st.session_state["pdf_vector_path"] = vector_path
                st.session_state["pdf_qa_history"] = []
                # Save to DB
                with SessionLocal() as db:
                    crud.save_pdf_document(
                        db, user.id, path, uploaded_pdf.name,
                        text[:50000], pages, vector_path
                    )
                st.success(f"✅ Processed {pages} pages! Knowledge base ready.")
            else:
                st.error("Could not extract text. Try a text-based PDF.")

# ── PDF Actions ───────────────────────────────
if "pdf_text" in st.session_state and st.session_state["pdf_text"]:
    pdf_text = st.session_state["pdf_text"]
    pdf_name = st.session_state.get("pdf_name", "Document")
    vector_path = st.session_state.get("pdf_vector_path")

    st.markdown(f"""
<div style="color:#10B981; font-size:0.85rem; margin:0.5rem 0;">
  ✅ Active document: <strong>{pdf_name}</strong> · {len(pdf_text.split()):,} words
</div>""", unsafe_allow_html=True)

    tab_qa, tab_summary, tab_keypoints, tab_notes, tab_flash = st.tabs([
        "💬 Q&A", "📋 Summary", "🔑 Key Points", "📝 Notes", "⚡ Flashcards"
    ])

    # ── Q&A Tab ───────────────────────────────
    with tab_qa:
        if "pdf_qa_history" not in st.session_state:
            st.session_state.pdf_qa_history = []

        for qa in st.session_state.pdf_qa_history:
            with st.chat_message("user", avatar="👤"):
                st.markdown(qa["q"])
            with st.chat_message("assistant", avatar="📄"):
                st.markdown(qa["a"])

        if question := st.chat_input("Ask anything about this PDF..."):
            with st.chat_message("user", avatar="👤"):
                st.markdown(question)
            with st.spinner("🔍 Searching document..."):
                answer = ask_pdf(question, pdf_text, vector_path)
            with st.chat_message("assistant", avatar="📄"):
                st.markdown(answer)
            st.session_state.pdf_qa_history.append({"q": question, "a": answer})
            st.rerun()

    # ── Summary Tab ───────────────────────────
    with tab_summary:
        col1, col2 = st.columns(2)
        with col1:
            detail = st.radio("Summary Detail", ["concise", "detailed"], horizontal=True)
        with col2:
            if st.button("📋 Generate Summary", use_container_width=True):
                with st.spinner("Summarizing document..."):
                    st.session_state["pdf_summary"] = summarize_pdf(pdf_text, detail)
        if "pdf_summary" in st.session_state:
            st.markdown(st.session_state["pdf_summary"])
            st.download_button("📥 Download Summary", st.session_state["pdf_summary"], "summary.md")

    # ── Key Points Tab ────────────────────────
    with tab_keypoints:
        if st.button("🔑 Extract Key Points", use_container_width=False):
            with st.spinner("Extracting key information..."):
                st.session_state["pdf_keypoints"] = extract_key_points(pdf_text)
        if "pdf_keypoints" in st.session_state:
            st.markdown(st.session_state["pdf_keypoints"])
            st.download_button("📥 Download Key Points", st.session_state["pdf_keypoints"], "key_points.md")

    # ── Notes Tab ─────────────────────────────
    with tab_notes:
        note_style = st.selectbox("Note Style", ["structured", "concise", "detailed"])
        if st.button("📝 Generate Notes", use_container_width=False):
            with st.spinner("Generating study notes..."):
                st.session_state["pdf_notes"] = generate_notes_from_pdf(pdf_text, note_style)
        if "pdf_notes" in st.session_state:
            st.markdown(st.session_state["pdf_notes"])
            st.download_button("📥 Download Notes", st.session_state["pdf_notes"], "study_notes.md")

    # ── Flashcards Tab ────────────────────────
    with tab_flash:
        n_cards = st.slider("Number of flashcards", 5, 20, 10)
        topic_label = st.text_input("Topic label", value=pdf_name[:30])
        if st.button("⚡ Generate Flashcards", use_container_width=False):
            with st.spinner("Creating flashcards..."):
                cards = generate_flashcards(pdf_text, topic_label, n_cards)
                if cards:
                    with SessionLocal() as db:
                        crud.create_flashcards(db, user.id, cards, topic_label)
                    st.session_state["pdf_flash"] = cards
                    st.success(f"✅ Created {len(cards)} flashcards — view them in ⚡ Flashcards page!")
        if "pdf_flash" in st.session_state:
            st.markdown(f"**{len(st.session_state['pdf_flash'])} flashcards generated:**")
            for i, card in enumerate(st.session_state["pdf_flash"][:5]):
                with st.expander(f"Card {i+1}: {card['front'][:50]}..."):
                    st.markdown(f"**Q:** {card['front']}")
                    st.markdown(f"**A:** {card['back']}")
else:
    info_banner("Upload a PDF above to get started.", "info")
