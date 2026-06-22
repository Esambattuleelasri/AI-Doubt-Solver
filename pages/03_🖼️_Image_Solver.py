# ─────────────────────────────────────────────
#  pages/03_🖼️_Image_Solver.py — Image OCR + AI
# ─────────────────────────────────────────────
import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from auth.auth_service import require_auth, logout
from ai.image_solver import solve_from_image, save_uploaded_image
from utils.ui_components import load_css, top_navigation, page_header, sidebar_user_info, info_banner, glass_card
from utils.helpers import file_size_str

st.set_page_config(page_title="Image Solver — AI Doubt Solver Pro", page_icon="🖼️", layout="wide")
load_css()

# ── Top Navigation ──
top_navigation("Image Solver")


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
    st.markdown("""
### 🖼️ Supported Formats
- **Images:** JPG, PNG, WEBP
- **Content:** Printed text, handwriting, equations, diagrams
- **Subjects:** Math, Physics, Chemistry, Biology

### 💡 Tips
- Use clear, well-lit images
- Crop to the problem area
- Higher resolution = better OCR
""")
    if st.button("🚪 Logout", use_container_width=True):
        logout()
        st.switch_page("app.py")

page_header("Image Solver", "Upload any problem image — AI solves it step by step", "🖼️")

col_upload, col_result = st.columns([1, 1])

with col_upload:
    st.markdown("#### 📤 Upload Image")
    uploaded = st.file_uploader(
        "Drop your image here",
        type=["jpg", "jpeg", "png", "webp", "bmp"],
        help="Upload a photo of your math problem, textbook page, or handwritten notes",
    )
    hint = st.text_input("💬 Additional hint (optional)", placeholder="e.g., 'This is a Physics problem about force'")

    if uploaded:
        st.image(uploaded, caption="Uploaded Image", use_container_width=True)
        size_str = file_size_str(uploaded.size)
        st.markdown(f"""
<div style="color:#64748B; font-size:0.8rem; margin-top:0.5rem;">
  📄 {uploaded.name} · {size_str}
</div>""", unsafe_allow_html=True)

        if st.button("🔍 Solve This Problem", use_container_width=True):
            with st.spinner("📸 Processing image and generating solution..."):
                path = save_uploaded_image(uploaded)
                result = solve_from_image(path, hint)
                st.session_state["image_result"] = result
                # Clean up processed file
                processed = path.replace(".", "_processed.")
                if os.path.exists(processed):
                    try:
                        os.remove(processed)
                    except Exception:
                        pass

with col_result:
    st.markdown("#### 💡 Solution")

    if "image_result" not in st.session_state:
        st.markdown("""
<div style="text-align:center; padding:3rem 1rem; color:#64748B; background:rgba(30,41,59,0.4);
  border:1px dashed rgba(99,102,241,0.2); border-radius:16px;">
  <div style="font-size:3rem; margin-bottom:1rem;">🔍</div>
  <div style="color:#94A3B8; font-size:1rem; font-weight:500;">Upload an image to get started</div>
  <div style="font-size:0.8rem; margin-top:0.5rem;">AI will extract text using OCR and solve the problem</div>
</div>""", unsafe_allow_html=True)
    else:
        res = st.session_state["image_result"]
        method_labels = {
            "vision": ("🎯 GPT-4 Vision", "#10B981"),
            "ocr+llm": ("🔤 OCR + AI", "#6366F1"),
            "ocr_only": ("🔤 OCR Only", "#F59E0B"),
            "failed": ("❌ Failed", "#EF4444"),
        }
        label, color = method_labels.get(res.get("method", ""), ("🔤 OCR + AI", "#6366F1"))
        st.markdown(f'<span style="background:rgba(99,102,241,0.15); color:{color}; border:1px solid {color}40; padding:3px 10px; border-radius:100px; font-size:0.75rem; font-weight:600;">{label}</span>', unsafe_allow_html=True)

        if res.get("extracted_text"):
            with st.expander("📝 Extracted Text (OCR)", expanded=False):
                st.code(res["extracted_text"], language=None)

        st.markdown("##### 🧮 AI Solution")
        st.markdown(res.get("solution", "No solution generated."))

        # Export solution
        solution_text = f"Problem (OCR):\n{res.get('extracted_text','')}\n\nSolution:\n{res.get('solution','')}"
        st.download_button("📥 Download Solution", solution_text, "solution.txt", use_container_width=True)

# ── How it works ──────────────────────────────
st.markdown("---")
st.markdown("### ⚙️ How It Works")
c1, c2, c3, c4 = st.columns(4)
steps = [
    ("📤", "Upload", "Upload a clear image of your problem"),
    ("🔍", "OCR", "EasyOCR extracts text from the image"),
    ("🤖", "AI Analysis", "GPT-4o analyzes and solves step-by-step"),
    ("✅", "Solution", "Get detailed explanation with steps"),
]
for col, (icon, title, desc) in zip([c1, c2, c3, c4], steps):
    with col:
        st.markdown(f"""
<div style="text-align:center; padding:1rem; background:rgba(30,41,59,0.7); border:1px solid rgba(99,102,241,0.15); border-radius:12px;">
  <div style="font-size:2rem; margin-bottom:0.5rem;">{icon}</div>
  <div style="color:#F1F5F9; font-weight:600; font-size:0.9rem;">{title}</div>
  <div style="color:#64748B; font-size:0.78rem; margin-top:4px;">{desc}</div>
</div>""", unsafe_allow_html=True)
