# ─────────────────────────────────────────────
#  utils/helpers.py — Utility Functions
# ─────────────────────────────────────────────
import os
import re
import uuid
import hashlib
from datetime import datetime
from pathlib import Path


def generate_session_id() -> str:
    """Generate a unique chat session ID."""
    return str(uuid.uuid4())[:8]


def format_timestamp(dt: datetime) -> str:
    """Format datetime to readable string."""
    if not dt:
        return ""
    now = datetime.utcnow()
    diff = now - dt
    if diff.seconds < 60:
        return "Just now"
    elif diff.seconds < 3600:
        return f"{diff.seconds // 60}m ago"
    elif diff.days == 0:
        return f"{diff.seconds // 3600}h ago"
    elif diff.days == 1:
        return "Yesterday"
    else:
        return dt.strftime("%b %d, %Y")


def truncate_text(text: str, max_len: int = 100) -> str:
    """Truncate text with ellipsis."""
    return text[:max_len] + "..." if len(text) > max_len else text


def safe_filename(name: str) -> str:
    """Sanitize filename for storage."""
    name = re.sub(r'[^\w\s\-.]', '', name)
    name = re.sub(r'\s+', '_', name.strip())
    return name[:200]


def file_size_str(bytes_size: int) -> str:
    """Convert bytes to human-readable size."""
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 ** 2:
        return f"{bytes_size / 1024:.1f} KB"
    elif bytes_size < 1024 ** 3:
        return f"{bytes_size / 1024**2:.1f} MB"
    return f"{bytes_size / 1024**3:.1f} GB"


def save_uploaded_file(uploaded_file, upload_dir: str = "uploads") -> str:
    """Save a Streamlit UploadedFile to disk. Returns path."""
    os.makedirs(upload_dir, exist_ok=True)
    ext = Path(uploaded_file.name).suffix
    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(upload_dir, unique_name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path


def export_chat_to_text(history: list) -> str:
    """Convert chat history to plain text for export."""
    lines = []
    for msg in history:
        role = "You" if msg["role"] == "user" else "AI"
        lines.append(f"[{role}]\n{msg['content']}\n")
    return "\n".join(lines)


def markdown_to_plain(text: str) -> str:
    """Strip markdown formatting for plain text export."""
    text = re.sub(r'#{1,6}\s*', '', text)
    text = re.sub(r'\*{1,2}(.*?)\*{1,2}', r'\1', text)
    text = re.sub(r'`{1,3}.*?`{1,3}', '', text, flags=re.DOTALL)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    return text.strip()


def get_subject_icon(subject: str) -> str:
    """Get emoji icon for a subject."""
    icons = {
        "Mathematics": "📐",
        "Physics": "⚛️",
        "Chemistry": "🧪",
        "Biology": "🧬",
        "Computer Science": "💻",
        "Programming": "👨‍💻",
        "General": "🌐",
    }
    return icons.get(subject, "📚")


def get_difficulty_color(difficulty: str) -> str:
    """Get color for difficulty level."""
    return {
        "easy": "#10B981",
        "medium": "#F59E0B",
        "hard": "#EF4444",
    }.get(difficulty.lower(), "#94A3B8")


def calculate_streak(last_active: datetime) -> int:
    """Return 1 if last active today or yesterday, else 0 (simple streak logic)."""
    if not last_active:
        return 0
    diff = (datetime.utcnow() - last_active).days
    return 1 if diff <= 1 else 0


def count_words(text: str) -> int:
    return len(text.split())


def estimate_read_time(text: str) -> str:
    words = count_words(text)
    minutes = max(1, words // 200)
    return f"{minutes} min read"
