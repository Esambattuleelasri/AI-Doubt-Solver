# ─────────────────────────────────────────────
#  ai/chatbot.py — LangChain Conversation Engine
# ─────────────────────────────────────────────
from typing import Optional
from config import settings

# ── LLM Factory ───────────────────────────────

def get_llm(temperature: float = 0.7):
    """Return LLM instance based on config."""
    if settings.llm_provider == "ollama":
        from langchain_community.llms import Ollama
        return Ollama(
            base_url=settings.ollama_base_url,
            model=settings.ollama_model,
            temperature=temperature,
        )
    elif settings.llm_provider == "gemini":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            api_key=settings.gemini_api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            model=settings.gemini_model or "gemini-3.5-flash",
            temperature=temperature,
        )
    else:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            temperature=temperature,
        )


# ── Subject System Prompts ─────────────────────

SUBJECT_PROMPTS = {
    "Mathematics": (
        "You are an expert Mathematics tutor. Solve problems step-by-step, "
        "show all working, explain formulas, and use LaTeX notation when helpful. "
        "Always verify the answer."
    ),
    "Physics": (
        "You are an expert Physics teacher. Explain concepts clearly, "
        "show derivations, include units, and provide real-world examples."
    ),
    "Chemistry": (
        "You are a Chemistry expert. Balance equations, explain reactions "
        "at the molecular level, and cover safety where relevant."
    ),
    "Biology": (
        "You are a Biology teacher. Explain biological processes with clarity, "
        "use diagrams described in text when helpful, and connect concepts to life."
    ),
    "Computer Science": (
        "You are a Computer Science professor. Explain algorithms, data structures, "
        "and CS theory with clear examples and complexity analysis."
    ),
    "Programming": (
        "You are a Senior Software Engineer and coding mentor. Write clean, commented "
        "code with explanations. Support Python, Java, C, C++, JavaScript."
    ),
    "General": (
        "You are a knowledgeable AI tutor. Answer questions clearly and thoroughly "
        "with examples where helpful."
    ),
}

TEACHER_MODE_PROMPT = """
You are an expert Socratic teacher. Your teaching style:
1. First EXPLAIN the concept clearly with simple language
2. Provide a REAL-WORLD EXAMPLE to illustrate
3. Give a PRACTICE QUESTION for the student to try
4. If they answer, evaluate and provide FEEDBACK
5. Conduct a SHORT MINI-TEST with 2-3 questions at the end

Always be encouraging, patient, and adjust complexity to the student's level.
"""


def build_system_prompt(subject: str = "General", teacher_mode: bool = False) -> str:
    base = SUBJECT_PROMPTS.get(subject, SUBJECT_PROMPTS["General"])
    if teacher_mode:
        base = TEACHER_MODE_PROMPT + "\n\nSubject expertise: " + base
    return base + "\n\nFormat your responses using Markdown with headers, bullet points, and code blocks where appropriate."


# ── Chat Session ──────────────────────────────

class ChatSession:
    """Stateless chat: accepts history list and returns response."""

    def __init__(self, subject: str = "General", teacher_mode: bool = False):
        self.subject = subject
        self.teacher_mode = teacher_mode
        self.llm = get_llm()

    def ask(self, question: str, history: list[dict] = None) -> dict:
        """
        history: [{"role": "user"|"assistant", "content": str}, ...]
        Returns: {"answer": str, "tokens": int}
        """
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

        messages = [SystemMessage(content=build_system_prompt(self.subject, self.teacher_mode))]

        # Inject prior history (last 10 exchanges to keep context window sane)
        if history:
            for msg in history[-20:]:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    messages.append(AIMessage(content=msg["content"]))

        messages.append(HumanMessage(content=question))

        try:
            response = self.llm.invoke(messages)
            answer = response.content if hasattr(response, "content") else str(response)
            tokens = getattr(response, "usage_metadata", {}) or {}
            total_tokens = tokens.get("total_tokens", 0) if isinstance(tokens, dict) else 0
            return {"answer": answer, "tokens": total_tokens, "success": True}
        except Exception as e:
            return {
                "answer": f"⚠️ Error communicating with AI: {str(e)}\n\nPlease check your API key in Settings.",
                "tokens": 0,
                "success": False,
            }


def simple_ask(question: str, subject: str = "General",
               history: list = None, teacher_mode: bool = False) -> str:
    """Convenience wrapper — returns answer string only."""
    session = ChatSession(subject=subject, teacher_mode=teacher_mode)
    result = session.ask(question, history or [])
    return result["answer"]
