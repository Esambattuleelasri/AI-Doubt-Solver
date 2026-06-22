# ─────────────────────────────────────────────
#  database/crud.py — CRUD Helpers
# ─────────────────────────────────────────────
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from database.models import User, Chat, Quiz, QuizQuestion, Flashcard, StudyPlan, PDFDocument


# ── Users ─────────────────────────────────────

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, name: str, email: str, hashed_password: str = None,
                provider: str = "local", avatar_url: str = None) -> User:
    user = User(
        name=name, email=email, hashed_password=hashed_password,
        provider=provider, avatar_url=avatar_url
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user_streak(db: Session, user_id: int, streak: int) -> None:
    db.query(User).filter(User.id == user_id).update(
        {"streak": streak, "last_active": datetime.utcnow()}
    )
    db.commit()


def add_points(db: Session, user_id: int, points: int) -> None:
    user = get_user_by_id(db, user_id)
    if user:
        user.total_points += points
        db.commit()


# ── Chats ─────────────────────────────────────

def save_chat(db: Session, user_id: int, session_id: str, question: str,
              answer: str, subject: str = "General", mode: str = "chat",
              tokens_used: int = 0) -> Chat:
    chat = Chat(
        user_id=user_id, session_id=session_id, question=question,
        answer=answer, subject=subject, mode=mode, tokens_used=tokens_used
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat


def get_chat_history(db: Session, user_id: int, session_id: str = None,
                     limit: int = 50) -> List[Chat]:
    q = db.query(Chat).filter(Chat.user_id == user_id)
    if session_id:
        q = q.filter(Chat.session_id == session_id)
    return q.order_by(Chat.timestamp.desc()).limit(limit).all()


def get_all_sessions(db: Session, user_id: int) -> List[str]:
    rows = (
        db.query(Chat.session_id)
        .filter(Chat.user_id == user_id)
        .distinct()
        .all()
    )
    return [r[0] for r in rows]


def count_chats(db: Session, user_id: int) -> int:
    return db.query(Chat).filter(Chat.user_id == user_id).count()


# ── Quizzes ───────────────────────────────────

def create_quiz(db: Session, user_id: int, topic: str, quiz_type: str = "mcq",
                difficulty: str = "medium", total_questions: int = 5) -> Quiz:
    quiz = Quiz(
        user_id=user_id, topic=topic, quiz_type=quiz_type,
        difficulty=difficulty, total_questions=total_questions
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    return quiz


def add_quiz_questions(db: Session, quiz_id: int, questions: list) -> None:
    for q in questions:
        qq = QuizQuestion(
            quiz_id=quiz_id,
            question=q["question"],
            options=q.get("options"),
            correct_answer=q["correct_answer"],
            explanation=q.get("explanation", ""),
        )
        db.add(qq)
    db.commit()


def submit_quiz(db: Session, quiz_id: int, answers: dict) -> int:
    """answers: {question_id: user_answer}. Returns score."""
    questions = db.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz_id).all()
    score = 0
    for q in questions:
        ua = answers.get(str(q.id), "")
        correct = ua.strip().lower() == q.correct_answer.strip().lower()
        q.user_answer = ua
        q.is_correct = correct
        if correct:
            score += 1
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if quiz:
        quiz.score = score
        quiz.completed = True
    db.commit()
    return score


def get_user_quizzes(db: Session, user_id: int, limit: int = 20) -> List[Quiz]:
    return db.query(Quiz).filter(
        Quiz.user_id == user_id, Quiz.completed == True
    ).order_by(Quiz.timestamp.desc()).limit(limit).all()


# ── Flashcards ────────────────────────────────

def create_flashcards(db: Session, user_id: int, cards: list, topic: str = "General") -> List[Flashcard]:
    created = []
    for c in cards:
        fc = Flashcard(user_id=user_id, front=c["front"], back=c["back"], topic=topic)
        db.add(fc)
        created.append(fc)
    db.commit()
    return created


def get_flashcards(db: Session, user_id: int, topic: str = None) -> List[Flashcard]:
    q = db.query(Flashcard).filter(Flashcard.user_id == user_id)
    if topic:
        q = q.filter(Flashcard.topic == topic)
    return q.order_by(Flashcard.created_at.desc()).all()


def delete_flashcard(db: Session, card_id: int, user_id: int) -> bool:
    card = db.query(Flashcard).filter(
        Flashcard.id == card_id, Flashcard.user_id == user_id
    ).first()
    if card:
        db.delete(card)
        db.commit()
        return True
    return False


# ── Study Plans ───────────────────────────────

def create_study_plan(db: Session, user_id: int, goal: str, subject: str,
                      deadline: str, plan_type: str, schedule: dict) -> StudyPlan:
    plan = StudyPlan(
        user_id=user_id, goal=goal, subject=subject,
        deadline=deadline, plan_type=plan_type, schedule=schedule
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def get_study_plans(db: Session, user_id: int) -> List[StudyPlan]:
    return db.query(StudyPlan).filter(
        StudyPlan.user_id == user_id
    ).order_by(StudyPlan.created_at.desc()).all()


def update_plan_progress(db: Session, plan_id: int, progress: float) -> None:
    db.query(StudyPlan).filter(StudyPlan.id == plan_id).update(
        {"progress_pct": progress}
    )
    db.commit()


# ── PDFs ──────────────────────────────────────

def save_pdf_document(db: Session, user_id: int, filename: str,
                      original_name: str, text_content: str,
                      page_count: int, vector_index_path: str = None) -> PDFDocument:
    doc = PDFDocument(
        user_id=user_id, filename=filename, original_name=original_name,
        text_content=text_content, page_count=page_count,
        vector_index_path=vector_index_path
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def get_user_pdfs(db: Session, user_id: int) -> List[PDFDocument]:
    return db.query(PDFDocument).filter(
        PDFDocument.user_id == user_id
    ).order_by(PDFDocument.uploaded_at.desc()).all()


def get_pdf_by_id(db: Session, pdf_id: int, user_id: int) -> Optional[PDFDocument]:
    return db.query(PDFDocument).filter(
        PDFDocument.id == pdf_id, PDFDocument.user_id == user_id
    ).first()
