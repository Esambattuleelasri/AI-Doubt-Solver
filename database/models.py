# ─────────────────────────────────────────────
#  database/models.py — ORM Models
# ─────────────────────────────────────────────
from datetime import datetime
import json
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean,
    DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from database.db import Base


class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String(120), nullable=False)
    email         = Column(String(200), unique=True, index=True, nullable=False)
    hashed_password = Column(String(256), nullable=True)  # nullable for OAuth users
    avatar_url    = Column(String(500), nullable=True)
    provider      = Column(String(20), default="local")   # "local" | "google"
    total_points  = Column(Integer, default=0)
    streak        = Column(Integer, default=0)
    last_active   = Column(DateTime, default=datetime.utcnow)
    preferred_language = Column(String(10), default="en")
    created_at    = Column(DateTime, default=datetime.utcnow)

    chats         = relationship("Chat", back_populates="user", cascade="all, delete")
    quizzes       = relationship("Quiz", back_populates="user", cascade="all, delete")
    flashcards    = relationship("Flashcard", back_populates="user", cascade="all, delete")
    study_plans   = relationship("StudyPlan", back_populates="user", cascade="all, delete")
    pdf_documents = relationship("PDFDocument", back_populates="user", cascade="all, delete")

    def __repr__(self):
        return f"<User id={self.id} email={self.email}>"


class Chat(Base):
    __tablename__ = "chats"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(String(64), index=True, nullable=False)
    question   = Column(Text, nullable=False)
    answer     = Column(Text, nullable=False)
    subject    = Column(String(60), default="General")
    mode       = Column(String(30), default="chat")    # "chat" | "teacher"
    tokens_used = Column(Integer, default=0)
    timestamp  = Column(DateTime, default=datetime.utcnow)

    user       = relationship("User", back_populates="chats")

    def __repr__(self):
        return f"<Chat id={self.id} session={self.session_id}>"


class Quiz(Base):
    __tablename__ = "quizzes"

    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic           = Column(String(200), nullable=False)
    quiz_type       = Column(String(30), default="mcq")       # mcq | truefalse | fillin
    difficulty      = Column(String(20), default="medium")
    score           = Column(Integer, default=0)
    total_questions = Column(Integer, default=5)
    completed       = Column(Boolean, default=False)
    timestamp       = Column(DateTime, default=datetime.utcnow)

    user      = relationship("User", back_populates="quizzes")
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete")


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id             = Column(Integer, primary_key=True, index=True)
    quiz_id        = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    question       = Column(Text, nullable=False)
    options        = Column(JSON, nullable=True)      # list of strings for MCQ
    correct_answer = Column(String(500), nullable=False)
    user_answer    = Column(String(500), nullable=True)
    explanation    = Column(Text, nullable=True)
    is_correct     = Column(Boolean, nullable=True)

    quiz = relationship("Quiz", back_populates="questions")


class Flashcard(Base):
    __tablename__ = "flashcards"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    front      = Column(Text, nullable=False)
    back       = Column(Text, nullable=False)
    topic      = Column(String(100), default="General")
    difficulty = Column(String(20), default="medium")
    reviewed   = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="flashcards")


class StudyPlan(Base):
    __tablename__ = "study_plans"

    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id"), nullable=False)
    goal         = Column(String(300), nullable=False)
    subject      = Column(String(100), nullable=True)
    deadline     = Column(String(50), nullable=True)
    plan_type    = Column(String(20), default="daily")  # daily | weekly | monthly
    schedule     = Column(JSON, nullable=True)           # structured schedule dict
    progress_pct = Column(Float, default=0.0)
    streak       = Column(Integer, default=0)
    created_at   = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="study_plans")


class PDFDocument(Base):
    __tablename__ = "pdf_documents"

    id               = Column(Integer, primary_key=True, index=True)
    user_id          = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename         = Column(String(300), nullable=False)
    original_name    = Column(String(300), nullable=False)
    text_content     = Column(Text, nullable=True)
    page_count       = Column(Integer, default=0)
    vector_index_path = Column(String(500), nullable=True)
    uploaded_at      = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="pdf_documents")
