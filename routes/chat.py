# ─────────────────────────────────────────────
#  routes/chat.py — FastAPI Chat Endpoints
# ─────────────────────────────────────────────
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from database.db import get_db
from database import crud
from auth.jwt_handler import decode_user_id

router = APIRouter(prefix="/chat", tags=["Chat"])


def get_user_id_from_token(authorization: str = "") -> int:
    token = authorization.replace("Bearer ", "").strip()
    uid = decode_user_id(token)
    if not uid:
        raise HTTPException(status_code=401, detail="Invalid token.")
    return uid


class ChatRequest(BaseModel):
    question: str
    subject: str = "General"
    session_id: str = "default"
    teacher_mode: bool = False
    history: List[dict] = []


class ChatResponse(BaseModel):
    answer: str
    tokens_used: int
    session_id: str


@router.post("/ask", response_model=ChatResponse)
def ask_question(req: ChatRequest, db: Session = Depends(get_db)):
    from ai.chatbot import ChatSession
    session = ChatSession(subject=req.subject, teacher_mode=req.teacher_mode)
    result = session.ask(req.question, req.history)
    return ChatResponse(
        answer=result["answer"],
        tokens_used=result.get("tokens", 0),
        session_id=req.session_id,
    )


@router.get("/history/{user_id}")
def get_history(user_id: int, session_id: Optional[str] = None,
                limit: int = 50, db: Session = Depends(get_db)):
    chats = crud.get_chat_history(db, user_id, session_id, limit)
    return [{"id": c.id, "question": c.question, "answer": c.answer,
             "subject": c.subject, "timestamp": str(c.timestamp)} for c in chats]


@router.get("/sessions/{user_id}")
def get_sessions(user_id: int, db: Session = Depends(get_db)):
    return {"sessions": crud.get_all_sessions(db, user_id)}
