# ─────────────────────────────────────────────
#  ai/quiz_generator.py — AI Quiz Generation
# ─────────────────────────────────────────────
import json
import re
from typing import List, Dict
from ai.chatbot import get_llm

QUIZ_TYPES = ["mcq", "truefalse", "fillin"]
DIFFICULTIES = ["easy", "medium", "hard"]


def _build_quiz_prompt(topic: str, quiz_type: str, difficulty: str, count: int) -> str:
    if quiz_type == "mcq":
        return f"""Generate {count} multiple-choice questions on the topic: "{topic}".
Difficulty: {difficulty}.

Return ONLY valid JSON in this exact format:
{{
  "questions": [
    {{
      "question": "Question text here?",
      "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
      "correct_answer": "A) Option 1",
      "explanation": "Brief explanation of why this is correct."
    }}
  ]
}}

Rules:
- No markdown fences, only raw JSON
- Correct answer must exactly match one of the options
- Explanations should be 1-2 sentences
- Vary question types (conceptual, applied, numerical)"""

    elif quiz_type == "truefalse":
        return f"""Generate {count} True/False questions on the topic: "{topic}".
Difficulty: {difficulty}.

Return ONLY valid JSON:
{{
  "questions": [
    {{
      "question": "Statement to evaluate.",
      "options": ["True", "False"],
      "correct_answer": "True",
      "explanation": "Brief explanation."
    }}
  ]
}}"""

    else:  # fillin
        return f"""Generate {count} fill-in-the-blank questions on the topic: "{topic}".
Difficulty: {difficulty}.

Return ONLY valid JSON:
{{
  "questions": [
    {{
      "question": "The _____ is the powerhouse of the cell.",
      "options": null,
      "correct_answer": "mitochondria",
      "explanation": "Brief explanation."
    }}
  ]
}}"""


def generate_quiz(topic: str, quiz_type: str = "mcq",
                  difficulty: str = "medium", count: int = 5) -> List[Dict]:
    """Generate quiz questions. Returns list of question dicts."""
    llm = get_llm(temperature=0.5)
    prompt = _build_quiz_prompt(topic, quiz_type, difficulty, count)

    try:
        response = llm.invoke(prompt)
        raw = response.content if hasattr(response, "content") else str(response)

        # Strip markdown fences if present
        raw = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("```").strip()

        data = json.loads(raw)
        return data.get("questions", [])

    except json.JSONDecodeError:
        # Fallback: try to extract JSON block
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
                return data.get("questions", [])
            except Exception:
                pass
        return _fallback_questions(topic, quiz_type, count)

    except Exception as e:
        return _fallback_questions(topic, quiz_type, count)


def _fallback_questions(topic: str, quiz_type: str, count: int) -> List[Dict]:
    """Return placeholder questions if generation fails."""
    questions = []
    for i in range(count):
        questions.append({
            "question": f"[Sample] What is an important concept in {topic}? (Question {i+1})",
            "options": ["A) Concept A", "B) Concept B", "C) Concept C", "D) Concept D"] if quiz_type == "mcq" else ["True", "False"],
            "correct_answer": "A) Concept A" if quiz_type == "mcq" else "True",
            "explanation": f"Please regenerate — AI could not parse the quiz for {topic}.",
        })
    return questions


def grade_quiz(questions: List[Dict], user_answers: Dict[int, str]) -> Dict:
    """Grade submitted quiz. Returns score details."""
    total = len(questions)
    correct = 0
    results = []

    for i, q in enumerate(questions):
        ua = user_answers.get(i, "").strip().lower()
        ca = q["correct_answer"].strip().lower()
        is_correct = ua == ca
        if is_correct:
            correct += 1
        results.append({
            "question": q["question"],
            "user_answer": user_answers.get(i, "Not answered"),
            "correct_answer": q["correct_answer"],
            "is_correct": is_correct,
            "explanation": q.get("explanation", ""),
        })

    pct = round((correct / total) * 100) if total else 0
    return {
        "score": correct,
        "total": total,
        "percentage": pct,
        "grade": _letter_grade(pct),
        "results": results,
    }


def _letter_grade(pct: int) -> str:
    if pct >= 90: return "A+"
    if pct >= 80: return "A"
    if pct >= 70: return "B"
    if pct >= 60: return "C"
    if pct >= 50: return "D"
    return "F"
