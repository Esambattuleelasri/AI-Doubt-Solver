# ─────────────────────────────────────────────
#  auth/auth_service.py — Auth Logic for Streamlit
# ─────────────────────────────────────────────
import streamlit as st
import bcrypt
from database.db import SessionLocal
from database import crud
from auth.jwt_handler import create_access_token, decode_user_id


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def register_user(name: str, email: str, password: str) -> dict:
    """Returns {"success": bool, "message": str, "user": User|None}"""
    with SessionLocal() as db:
        existing = crud.get_user_by_email(db, email)
        if existing:
            return {"success": False, "message": "Email already registered.", "user": None}
        hashed = hash_password(password)
        user = crud.create_user(db, name=name, email=email, hashed_password=hashed)
        return {"success": True, "message": "Registration successful!", "user": user}


def login_user(email: str, password: str) -> dict:
    """Returns {"success": bool, "message": str, "token": str|None, "user": User|None}"""
    with SessionLocal() as db:
        user = crud.get_user_by_email(db, email)
        if not user:
            return {"success": False, "message": "User not found.", "token": None, "user": None}
        if not user.hashed_password or not verify_password(password, user.hashed_password):
            return {"success": False, "message": "Incorrect password.", "token": None, "user": None}
        token = create_access_token({"sub": str(user.id), "email": user.email})
        return {"success": True, "message": "Login successful!", "token": token, "user": user}


def get_current_user_from_session():
    """Get authenticated user from st.session_state."""
    token = st.session_state.get("auth_token")
    if not token:
        return None
    user_id = decode_user_id(token)
    if not user_id:
        return None
    with SessionLocal() as db:
        return crud.get_user_by_id(db, user_id)


def logout():
    """Clear session state auth data."""
    for key in ["auth_token", "current_user", "chat_session_id"]:
        st.session_state.pop(key, None)


def is_authenticated() -> bool:
    return get_current_user_from_session() is not None


def require_auth():
    """Call at top of each page; redirects to login if not authenticated."""
    user = get_current_user_from_session()
    if not user:
        st.session_state["redirect_to_login"] = True
        st.switch_page("app.py")
    return user
