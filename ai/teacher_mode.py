# ─────────────────────────────────────────────
#  ai/teacher_mode.py — Socratic Teacher AI
# ─────────────────────────────────────────────
from ai.chatbot import get_llm, SUBJECT_PROMPTS


TEACHER_STAGES = {
    "explain": "Explain the concept clearly with simple language and analogies.",
    "example": "Provide real-world examples and illustrations.",
    "practice": "Give a practice question for the student to attempt.",
    "test": "Conduct a brief 3-question mini test on the topic.",
    "feedback": "Evaluate the student's answer and provide detailed feedback.",
}


def teach_concept(topic: str, subject: str = "General",
                  stage: str = "explain", student_answer: str = None,
                  history: list = None) -> str:
    """Run one stage of the teacher flow."""
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

    llm = get_llm(temperature=0.7)

    subject_context = SUBJECT_PROMPTS.get(subject, SUBJECT_PROMPTS["General"])
    system = f"""You are an expert, encouraging Socratic teacher specializing in {subject}.
{subject_context}

Your teaching approach:
- Be warm, encouraging, and patient
- Use simple language first, then build complexity
- Connect new concepts to things the student already knows
- Celebrate correct answers and gently guide wrong ones
- Always end with an encouraging message

Current stage: {TEACHER_STAGES.get(stage, TEACHER_STAGES['explain'])}"""

    messages = [SystemMessage(content=system)]

    if history:
        for msg in history[-10:]:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))

    if stage == "explain":
        user_msg = f"Please teach me about: {topic}"
    elif stage == "example":
        user_msg = f"Give me examples to understand: {topic}"
    elif stage == "practice":
        user_msg = f"Give me a practice question about: {topic}"
    elif stage == "test":
        user_msg = f"I'm ready for a mini test on: {topic}"
    elif stage == "feedback":
        user_msg = f"My answer to the question is: {student_answer}"
    else:
        user_msg = f"Help me understand: {topic}"

    messages.append(HumanMessage(content=user_msg))

    try:
        response = llm.invoke(messages)
        return response.content if hasattr(response, "content") else str(response)
    except Exception as e:
        return f"⚠️ Teacher mode error: {e}"


def generate_mini_test(topic: str, subject: str = "General") -> str:
    """Generate a 3-question mini test."""
    llm = get_llm(temperature=0.6)
    prompt = f"""As a {subject} teacher, create a 3-question mini test on "{topic}".

Format:
## 📝 Mini Test: {topic}

**Q1:** [Question]
*(Type: Multiple Choice / Short Answer / True-False)*

**Q2:** [Question]

**Q3:** [Question]

---
*Answer all questions and I will evaluate your responses.*"""
    try:
        response = llm.invoke(prompt)
        return response.content if hasattr(response, "content") else str(response)
    except Exception as e:
        return f"Error generating mini test: {e}"


def evaluate_test_answers(topic: str, questions: str, answers: str) -> str:
    """Evaluate student answers to a mini test."""
    llm = get_llm(temperature=0.4)
    prompt = f"""You are a supportive {topic} teacher evaluating a student's test answers.

QUESTIONS:
{questions}

STUDENT ANSWERS:
{answers}

Provide:
1. Score (X/3)
2. Answer-by-answer feedback (correct/incorrect + explanation)
3. Topics to review if needed
4. An encouraging closing message

Be constructive and specific."""
    try:
        response = llm.invoke(prompt)
        return response.content if hasattr(response, "content") else str(response)
    except Exception as e:
        return f"Error evaluating answers: {e}"
