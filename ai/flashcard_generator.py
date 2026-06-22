# ─────────────────────────────────────────────
#  ai/flashcard_generator.py — AI Flashcard Engine
# ─────────────────────────────────────────────
import json
import re
from typing import List, Dict
from ai.chatbot import get_llm


def generate_flashcards(text: str, topic: str = "General", count: int = 10) -> List[Dict]:
    """Generate flashcards from text content."""
    llm = get_llm(temperature=0.5)
    truncated = text[:5000]
    prompt = f"""Create {count} educational flashcards from the following content about "{topic}".

Return ONLY valid JSON (no markdown fences):
{{
  "flashcards": [
    {{
      "front": "Question or term",
      "back": "Answer or definition (concise, 1-3 sentences)"
    }}
  ]
}}

Content:
{truncated}

Rules:
- Focus on key concepts, definitions, formulas, and important facts
- Make questions clear and unambiguous
- Keep answers concise but complete
- Vary between definition, explanation, and application questions"""

    try:
        response = llm.invoke(prompt)
        raw = response.content if hasattr(response, "content") else str(response)
        raw = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("```").strip()
        data = json.loads(raw)
        return data.get("flashcards", [])
    except Exception:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
                return data.get("flashcards", [])
            except Exception:
                pass
        return _fallback_flashcards(topic, count)


def generate_flashcards_from_topic(topic: str, count: int = 10, difficulty: str = "medium") -> List[Dict]:
    """Generate flashcards directly from a topic name."""
    llm = get_llm(temperature=0.6)
    prompt = f"""Create {count} comprehensive flashcards for studying "{topic}" at {difficulty} level.

Return ONLY valid JSON:
{{
  "flashcards": [
    {{
      "front": "What is...? / Define... / Explain...",
      "back": "Clear, complete answer in 1-3 sentences"
    }}
  ]
}}

Cover: definitions, key concepts, important formulas/rules, examples, and applications.
Difficulty: {difficulty} — {'basic definitions and concepts' if difficulty == 'easy' else 'applications and analysis' if difficulty == 'hard' else 'mix of concepts and applications'}"""

    try:
        response = llm.invoke(prompt)
        raw = response.content if hasattr(response, "content") else str(response)
        raw = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("```").strip()
        data = json.loads(raw)
        return data.get("flashcards", [])
    except Exception:
        return _fallback_flashcards(topic, count)


def _fallback_flashcards(topic: str, count: int) -> List[Dict]:
    return [
        {
            "front": f"What is a key concept in {topic}? (Card {i+1})",
            "back": f"Please regenerate — AI could not create flashcards for {topic}.",
        }
        for i in range(min(count, 5))
    ]
