# ─────────────────────────────────────────────
#  routes/quiz.py — FastAPI Quiz Endpoints
# ─────────────────────────────────────────────
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from database.db import get_db
from database import crud

router = APIRouter(prefix="/quiz", tags=["Quiz"])


class QuizGenerateRequest(BaseModel):
    topic: str
    quiz_type: str = "mcq"
    difficulty: str = "medium"
    count: int = 5
    user_id: Optional[int] = None


class QuizSubmitRequest(BaseModel):
    quiz_id: int
    answers: dict  # {question_index: answer_string}


@router.post("/generate")
def generate_quiz_endpoint(req: QuizGenerateRequest, db: Session = Depends(get_db)):
    from ai.quiz_generator import generate_quiz
    questions = generate_quiz(req.topic, req.quiz_type, req.difficulty, req.count)
    if req.user_id:
        quiz_db = crud.create_quiz(db, req.user_id, req.topic, req.quiz_type, req.difficulty, len(questions))
        crud.add_quiz_questions(db, quiz_db.id, questions)
        return {"quiz_id": quiz_db.id, "questions": questions}
    return {"questions": questions}


@router.post("/submit")
def submit_quiz_endpoint(req: QuizSubmitRequest, db: Session = Depends(get_db)):
    from database.models import Quiz
    score = crud.submit_quiz(db, req.quiz_id, req.answers)
    quiz = db.query(Quiz).filter(Quiz.id == req.quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found.")
    pct = round((score / quiz.total_questions) * 100)
    return {"score": score, "total": quiz.total_questions, "percentage": pct}


@router.get("/history/{user_id}")
def quiz_history(user_id: int, db: Session = Depends(get_db)):
    quizzes = crud.get_user_quizzes(db, user_id)
    return [{"id": q.id, "topic": q.topic, "score": q.score,
             "total": q.total_questions, "difficulty": q.difficulty,
             "timestamp": str(q.timestamp)} for q in quizzes]
