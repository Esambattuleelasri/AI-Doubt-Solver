# ─────────────────────────────────────────────
#  utils/ui_components.py — Reusable Streamlit Components
# ─────────────────────────────────────────────
import streamlit as st
from pathlib import Path


def load_css():
    """Inject global CSS theme into Streamlit."""
    css_path = Path(__file__).parent.parent / "static" / "style.css"
    if css_path.exists():
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "", icon: str = ""):
    """Render a styled page header."""
    st.markdown(f"""
<div style="padding: 1.5rem 0 1rem 0; border-bottom: 1px solid rgba(99,102,241,0.2); margin-bottom: 1.5rem;">
  <h1 style="
    font-size: 2rem; font-weight: 800; margin: 0;
    background: linear-gradient(135deg, #818CF8, #06B6D4);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
  ">{icon} {title}</h1>
  {f'<p style="color:#94A3B8; margin: 0.4rem 0 0 0; font-size: 0.95rem;">{subtitle}</p>' if subtitle else ''}
</div>
""", unsafe_allow_html=True)


def metric_card(label: str, value: str, icon: str = "📊", delta: str = "", color: str = "#6366F1"):
    """Render a glassmorphism metric card."""
    delta_html = f'<div style="color:#10B981; font-size:0.75rem; margin-top:4px;">{delta}</div>' if delta else ''
    st.markdown(f"""
<div class="metric-card">
  <div style="font-size:2rem; margin-bottom:0.25rem;">{icon}</div>
  <div style="font-size:2rem; font-weight:800; color:{color}; line-height:1;">{value}</div>
  <div style="color:#94A3B8; font-size:0.8rem; margin-top:0.4rem; font-weight:500;">{label}</div>
  {delta_html}
</div>
""", unsafe_allow_html=True)


def glass_card(content_html: str, padding: str = "1.5rem"):
    """Render a glassmorphism card with arbitrary HTML content."""
    st.markdown(f"""
<div class="glass-card" style="padding:{padding}">
  {content_html}
</div>
""", unsafe_allow_html=True)


def subject_badge(subject: str) -> str:
    """Return HTML badge for a subject."""
    colors = {
        "Mathematics":    ("rgba(99,102,241,0.2)",  "#818CF8", "rgba(99,102,241,0.4)"),
        "Physics":        ("rgba(6,182,212,0.2)",   "#22D3EE", "rgba(6,182,212,0.4)"),
        "Chemistry":      ("rgba(16,185,129,0.2)",  "#34D399", "rgba(16,185,129,0.4)"),
        "Biology":        ("rgba(245,158,11,0.2)",  "#FCD34D", "rgba(245,158,11,0.4)"),
        "Computer Science":("rgba(139,92,246,0.2)", "#A78BFA", "rgba(139,92,246,0.4)"),
        "Programming":    ("rgba(239,68,68,0.2)",   "#FCA5A5", "rgba(239,68,68,0.4)"),
        "General":        ("rgba(148,163,184,0.2)", "#CBD5E1", "rgba(148,163,184,0.4)"),
    }
    bg, color, border = colors.get(subject, colors["General"])
    return f'<span style="background:{bg}; color:{color}; border:1px solid {border}; padding:3px 10px; border-radius:100px; font-size:0.75rem; font-weight:600;">{subject}</span>'


def chat_bubble(role: str, content: str, timestamp: str = ""):
    """Render a styled chat bubble."""
    is_user = role == "user"
    align = "flex-end" if is_user else "flex-start"
    bg = "linear-gradient(135deg, rgba(99,102,241,0.25), rgba(139,92,246,0.25))" if is_user else "rgba(30,41,59,0.8)"
    border = "rgba(99,102,241,0.4)" if is_user else "rgba(99,102,241,0.15)"
    avatar = "👤" if is_user else "🤖"
    ts_html = f'<div style="color:#64748B; font-size:0.7rem; margin-top:4px; text-align:{"right" if is_user else "left"};">{timestamp}</div>' if timestamp else ""

    st.markdown(f"""
<div style="display:flex; justify-content:{align}; margin-bottom:0.75rem; animation:slideIn 0.3s ease;">
  <div style="max-width:80%; background:{bg}; border:1px solid {border}; border-radius:16px; padding:1rem 1.25rem; backdrop-filter:blur(10px);">
    <div style="font-size:1.2rem; margin-bottom:0.4rem;">{avatar}</div>
    <div style="color:#F1F5F9; line-height:1.6;">{content}</div>
    {ts_html}
  </div>
</div>
""", unsafe_allow_html=True)


def progress_bar_custom(label: str, value: float, max_value: float = 100, color: str = "#6366F1"):
    """Render a styled progress bar."""
    pct = min((value / max_value) * 100, 100)
    st.markdown(f"""
<div style="margin-bottom: 0.75rem;">
  <div style="display:flex; justify-content:space-between; margin-bottom:0.35rem;">
    <span style="color:#94A3B8; font-size:0.85rem; font-weight:500;">{label}</span>
    <span style="color:#F1F5F9; font-size:0.85rem; font-weight:700;">{pct:.0f}%</span>
  </div>
  <div style="background:rgba(30,41,59,0.8); border-radius:100px; height:8px; overflow:hidden; border:1px solid rgba(99,102,241,0.15);">
    <div style="width:{pct}%; height:100%; background:linear-gradient(90deg, {color}, #06B6D4); border-radius:100px; transition:width 0.5s ease;"></div>
  </div>
</div>
""", unsafe_allow_html=True)


def score_display(score: int, total: int, grade: str):
    """Render a large score display for quiz results."""
    pct = round((score / total) * 100) if total else 0
    color = "#10B981" if pct >= 70 else "#F59E0B" if pct >= 50 else "#EF4444"
    st.markdown(f"""
<div style="text-align:center; padding:2rem; background:rgba(30,41,59,0.7); border:1px solid rgba(99,102,241,0.2); border-radius:20px; backdrop-filter:blur(15px);">
  <div style="font-size:4rem; font-weight:900; color:{color}; line-height:1;">{score}/{total}</div>
  <div style="font-size:1.5rem; color:{color}; font-weight:700; margin:0.5rem 0;">Grade: {grade}</div>
  <div style="color:#94A3B8; font-size:1rem;">Score: {pct}%</div>
  <div style="margin-top:1rem; font-size:2rem;">{'🏆' if pct >= 90 else '🎉' if pct >= 70 else '💪' if pct >= 50 else '📚'}</div>
</div>
""", unsafe_allow_html=True)


def info_banner(message: str, type: str = "info"):
    """Render a styled info/success/warning/error banner."""
    configs = {
        "info":    ("rgba(6,182,212,0.1)",   "#22D3EE", "rgba(6,182,212,0.3)",   "ℹ️"),
        "success": ("rgba(16,185,129,0.1)",  "#34D399", "rgba(16,185,129,0.3)",  "✅"),
        "warning": ("rgba(245,158,11,0.1)",  "#FCD34D", "rgba(245,158,11,0.3)",  "⚠️"),
        "error":   ("rgba(239,68,68,0.1)",   "#FCA5A5", "rgba(239,68,68,0.3)",   "❌"),
    }
    bg, color, border, icon = configs.get(type, configs["info"])
    st.markdown(f"""
<div style="background:{bg}; border:1px solid {border}; border-radius:12px; padding:1rem 1.25rem; margin:0.75rem 0; display:flex; gap:0.75rem; align-items:center;">
  <span style="font-size:1.2rem;">{icon}</span>
  <span style="color:{color}; font-size:0.9rem; font-weight:500;">{message}</span>
</div>
""", unsafe_allow_html=True)


def sidebar_user_info(user):
    """Render user info in sidebar."""
    if not user:
        return
    initials = "".join([n[0].upper() for n in user.name.split()[:2]])
    st.sidebar.markdown(f"""
<div style="background:rgba(99,102,241,0.1); border:1px solid rgba(99,102,241,0.2); border-radius:16px; padding:1rem; margin-bottom:1rem; text-align:center;">
  <div style="width:56px; height:56px; background:linear-gradient(135deg,#6366F1,#8B5CF6); border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:1.2rem; font-weight:700; color:white; margin:0 auto 0.75rem auto;">{initials}</div>
  <div style="color:#F1F5F9; font-weight:700; font-size:0.95rem;">{user.name}</div>
  <div style="color:#94A3B8; font-size:0.75rem; margin-top:2px;">{user.email}</div>
  <div style="display:flex; justify-content:center; gap:1rem; margin-top:0.75rem;">
    <div style="text-align:center;">
      <div style="color:#818CF8; font-weight:700; font-size:1rem;">{user.total_points}</div>
      <div style="color:#64748B; font-size:0.7rem;">Points</div>
    </div>
    <div style="text-align:center;">
      <div style="color:#F59E0B; font-weight:700; font-size:1rem;">🔥 {user.streak}</div>
      <div style="color:#64748B; font-size:0.7rem;">Streak</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


def render_flashcard(front: str, back: str, card_id: str):
    """Render an interactive flipable flashcard using session state."""
    flip_key = f"card_flipped_{card_id}"
    if flip_key not in st.session_state:
        st.session_state[flip_key] = False

    flipped = st.session_state[flip_key]
    side = "ANSWER" if flipped else "QUESTION"
    content = back if flipped else front
    bg = "linear-gradient(135deg, rgba(6,182,212,0.2), rgba(16,185,129,0.2))" if flipped else "linear-gradient(135deg, rgba(99,102,241,0.2), rgba(139,92,246,0.2))"
    border = "rgba(6,182,212,0.3)" if flipped else "rgba(99,102,241,0.3)"
    icon = "💡" if flipped else "❓"

    st.markdown(f"""
<div style="background:{bg}; border:1px solid {border}; border-radius:20px; padding:2.5rem 2rem; text-align:center; min-height:180px; display:flex; flex-direction:column; align-items:center; justify-content:center; transition:all 0.4s ease; cursor:pointer; box-shadow:0 4px 20px rgba(99,102,241,0.15);">
  <div style="color:#64748B; font-size:0.7rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:1rem;">{icon} {side}</div>
  <div style="color:#F1F5F9; font-size:1.1rem; font-weight:500; line-height:1.6;">{content}</div>
</div>
""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Flip Card", key=f"flip_{card_id}", use_container_width=True):
            st.session_state[flip_key] = not flipped
            st.rerun()
    return flipped

def top_navigation(current_page: str):
    from streamlit_option_menu import option_menu
    
    pages = ["Home", "AI Chat", "Image Solver", "PDF", "Quiz", "Study Plan", "Analytics", "Flashcards", "Settings"]
    icons = ["house", "chat", "image", "file-pdf", "puzzle", "calendar", "bar-chart", "lightning", "gear"]
    paths = [
        "pages/01_🏠_Home.py",
        "pages/02_💬_AI_Chat.py",
        "pages/03_🖼️_Image_Solver.py",
        "pages/04_📄_PDF_Assistant.py",
        "pages/05_🧠_Quiz_Generator.py",
        "pages/06_📅_Study_Planner.py",
        "pages/07_📊_Analytics.py",
        "pages/08_⚡_Flashcards.py",
        "pages/09_⚙️_Settings.py"
    ]
    
    try:
        default_index = pages.index(current_page)
    except ValueError:
        default_index = 0
        
    selected = option_menu(
        menu_title=None,
        options=pages,
        icons=icons,
        default_index=default_index,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "transparent", "margin-bottom": "1rem"},
            "icon": {"color": "#6366F1", "font-size": "14px"},
            "nav-link": {"font-size": "12px", "text-align": "center", "margin": "0px", "--hover-color": "rgba(99,102,241,0.1)"},
            "nav-link-selected": {"background-color": "rgba(99,102,241,0.2)", "color": "#F1F5F9", "border": "1px solid rgba(99,102,241,0.4)", "font-weight": "bold"},
        }
    )
    
    if selected != current_page:
        st.switch_page(paths[pages.index(selected)])
