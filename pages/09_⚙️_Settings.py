# ─────────────────────────────────────────────
#  pages/09_⚙️_Settings.py — User Settings
# ─────────────────────────────────────────────
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from auth.auth_service import require_auth, logout
from database.db import SessionLocal
from database import crud
from utils.ui_components import load_css, top_navigation, page_header, sidebar_user_info, info_banner
from config import settings

st.set_page_config(page_title="Settings — AI Doubt Solver Pro", page_icon="⚙️", layout="wide")
load_css()

# ── Top Navigation ──
top_navigation("Settings")


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

page_header("Settings", "Manage your profile and AI configuration", "⚙️")

tab_profile, tab_ai, tab_lang, tab_data = st.tabs(["👤 Profile", "🤖 AI Config", "🌐 Language", "📊 Data"])

# ── Profile Tab ───────────────────────────────
with tab_profile:
    st.markdown("### 👤 Your Profile")
    col_avatar, col_form = st.columns([1, 3])

    with col_avatar:
        initials = "".join([n[0].upper() for n in user.name.split()[:2]])
        st.markdown(f"""
<div style="width:100px; height:100px; background:linear-gradient(135deg,#6366F1,#8B5CF6); border-radius:50%;
  display:flex; align-items:center; justify-content:center; font-size:2rem; font-weight:700; color:white; margin:0 auto;">
  {initials}
</div>
<div style="text-align:center; margin-top:0.75rem;">
  <div style="color:#F1F5F9; font-weight:600;">{user.name}</div>
  <div style="color:#64748B; font-size:0.8rem;">{user.provider.title()} account</div>
</div>""", unsafe_allow_html=True)

    with col_form:
        with st.form("profile_form"):
            new_name = st.text_input("Full Name", value=user.name)
            st.text_input("Email", value=user.email, disabled=True, help="Email cannot be changed")
            save_profile = st.form_submit_button("💾 Save Profile")
            if save_profile:
                # In a real app, update name in DB
                info_banner("Profile updated! (Name change requires DB update implementation)", "success")

    st.markdown("---")
    st.markdown("### 📈 Account Statistics")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total Points", user.total_points, delta=None)
    with c2:
        st.metric("Learning Streak", f"🔥 {user.streak} days")
    with c3:
        st.metric("Member Since", user.created_at.strftime("%b %Y") if user.created_at else "N/A")

# ── AI Config Tab ─────────────────────────────
with tab_ai:
    st.markdown("### 🤖 AI Provider Configuration")
    info_banner("Changes here are applied for this session only. To persist, edit your .env file.", "warning")

    with st.form("ai_config_form"):
        provider = st.selectbox("LLM Provider", ["openai", "ollama", "gemini"],
                                index=0 if settings.llm_provider == "openai" else 1 if settings.llm_provider == "ollama" else 2,
                                format_func=lambda x: "🌐 OpenAI (GPT-4o)" if x == "openai" else "🏠 Ollama (Local)" if x == "ollama" else "♊ Google Gemini")

        if provider == "openai":
            api_key = st.text_input("OpenAI API Key", value=settings.openai_api_key, type="password",
                                    placeholder="sk-...")
            model_name = st.selectbox("Model", ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
                                      index=0)
            ollama_url, ollama_model, gemini_key, gemini_mod = "", "", "", ""
        elif provider == "ollama":
            api_key, model_name = "", ""
            ollama_url = st.text_input("Ollama Base URL", value=settings.ollama_base_url)
            ollama_model = st.text_input("Ollama Model", value=settings.ollama_model)
            gemini_key, gemini_mod = "", ""
        else:
            api_key, model_name = "", ""
            ollama_url, ollama_model = "", ""
            gemini_key = st.text_input("Gemini API Key", value=settings.gemini_api_key, type="password",
                                       placeholder="AIzaSy...")
            gemini_mod = st.selectbox("Gemini Model", ["gemini-3.5-flash", "gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-3.1-flash-lite"], index=0)

        temperature = st.slider("Temperature (Creativity)", 0.0, 1.0, 0.7, 0.05,
                                help="Higher = more creative. Lower = more deterministic.")

        save_ai = st.form_submit_button("💾 Apply AI Settings")
        if save_ai:
            os.environ["LLM_PROVIDER"] = provider
            if provider == "openai":
                if api_key:
                    os.environ["OPENAI_API_KEY"] = api_key
                if model_name:
                    os.environ["OPENAI_MODEL"] = model_name
            elif provider == "ollama":
                if ollama_url:
                    os.environ["OLLAMA_BASE_URL"] = ollama_url
                if ollama_model:
                    os.environ["OLLAMA_MODEL"] = ollama_model
            elif provider == "gemini":
                if gemini_key:
                    os.environ["GEMINI_API_KEY"] = gemini_key
                if gemini_mod:
                    os.environ["GEMINI_MODEL"] = gemini_mod
            info_banner("AI settings applied for this session!", "success")

    st.markdown("---")
    st.markdown("### 🧪 Test Connection")
    if st.button("🔌 Test AI Connection"):
        with st.spinner("Testing..."):
            try:
                from ai.chatbot import simple_ask
                resp = simple_ask("Say 'Connection successful!' in exactly 3 words.")
                st.success(f"✅ Connected! Response: {resp[:100]}")
            except Exception as e:
                st.error(f"❌ Connection failed: {e}")

# ── Language Tab ──────────────────────────────
with tab_lang:
    st.markdown("### 🌐 Language & Translation")
    info_banner("Multi-language responses use deep-translator. Ensure the package is installed.", "info")

    lang_options = {
        "en": "🇺🇸 English",
        "hi": "🇮🇳 Hindi",
        "te": "🇮🇳 Telugu",
        "ta": "🇮🇳 Tamil",
        "es": "🇪🇸 Spanish",
        "fr": "🇫🇷 French",
        "de": "🇩🇪 German",
        "zh-cn": "🇨🇳 Chinese (Simplified)",
        "ja": "🇯🇵 Japanese",
    }
    current_lang = st.session_state.get("ui_language", "en")
    selected_lang = st.selectbox("Response Language", list(lang_options.keys()),
                                  index=list(lang_options.keys()).index(current_lang),
                                  format_func=lambda x: lang_options[x])

    if st.button("💾 Save Language Preference"):
        st.session_state["ui_language"] = selected_lang
        info_banner(f"Language set to {lang_options[selected_lang]}!", "success")

    st.markdown("---")
    st.markdown("### 🔤 Live Translation Test")
    test_text = st.text_area("Text to translate", placeholder="Enter any text here...")
    target_lang = st.selectbox("Translate to", list(lang_options.keys()),
                                format_func=lambda x: lang_options[x], key="trans_lang")
    if st.button("🌍 Translate") and test_text:
        with st.spinner("Translating..."):
            try:
                from deep_translator import GoogleTranslator
                translated = GoogleTranslator(source="auto", target=target_lang).translate(test_text)
                st.markdown(f"""
<div style="background:rgba(6,182,212,0.08); border:1px solid rgba(6,182,212,0.2); border-radius:12px; padding:1rem; margin-top:0.5rem;">
  <div style="color:#64748B; font-size:0.75rem; margin-bottom:0.5rem;">Translation ({lang_options[target_lang]})</div>
  <div style="color:#F1F5F9;">{translated}</div>
</div>""", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Translation error: {e}")

# ── Data Tab ──────────────────────────────────
with tab_data:
    st.markdown("### 📊 Your Data")
    with SessionLocal() as db:
        chat_count = crud.count_chats(db, user.id)
        quiz_count = len(crud.get_user_quizzes(db, user.id, limit=1000))
        fc_count = len(crud.get_flashcards(db, user.id))
        pdf_count = len(crud.get_user_pdfs(db, user.id))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Chats", chat_count)
    c2.metric("Quizzes", quiz_count)
    c3.metric("Flashcards", fc_count)
    c4.metric("PDFs", pdf_count)

    st.markdown("---")
    st.markdown("### 💾 Export Your Data")
    if st.button("📥 Export All Chats"):
        with SessionLocal() as db:
            chats = crud.get_chat_history(db, user.id, limit=10000)
        from utils.helpers import export_chat_to_text
        history = [{"role":"user","content":c.question} for c in chats] + [{"role":"assistant","content":c.answer} for c in chats]
        st.download_button("Download Chat History", export_chat_to_text(history), "all_chats.txt")

    st.markdown("---")
    st.markdown("### ⚠️ Danger Zone")
    with st.expander("🗑️ Delete Account Data"):
        st.warning("This will permanently delete all your chats, quizzes, flashcards, and study plans.")
        confirm = st.text_input("Type DELETE to confirm", placeholder="DELETE")
        if st.button("🗑️ Delete My Data", type="primary") and confirm == "DELETE":
            info_banner("Data deletion would be implemented here. (Protected in demo mode)", "warning")
