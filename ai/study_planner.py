# ─────────────────────────────────────────────
#  ai/study_planner.py — AI Study Schedule Generator
# ─────────────────────────────────────────────
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List
from ai.chatbot import get_llm


def _build_planner_prompt(goal: str, subject: str, deadline: str,
                           plan_type: str, hours_per_day: int) -> str:
    return f"""Create a detailed {plan_type} study plan for a student with these details:
- Goal: {goal}
- Subject/Topic: {subject}
- Deadline: {deadline}
- Available hours per day: {hours_per_day}
- Plan type: {plan_type}

Return ONLY valid JSON (no markdown fences) in this format:
{{
  "overview": "Brief overview of the study plan strategy",
  "total_topics": 5,
  "schedule": [
    {{
      "day": "Day 1 / Monday",
      "date": "2024-01-15",
      "topics": ["Topic 1", "Topic 2"],
      "tasks": ["Read Chapter 1", "Solve 10 practice problems"],
      "duration_hours": 3,
      "priority": "high"
    }}
  ],
  "milestones": [
    {{"week": 1, "milestone": "Complete foundational concepts"}},
    {{"week": 2, "milestone": "Practice problems and revision"}}
  ],
  "tips": ["Study tip 1", "Study tip 2", "Study tip 3"],
  "resources": ["Resource/book 1", "Resource 2"]
}}

Generate {7 if plan_type == 'weekly' else 30 if plan_type == 'monthly' else 1} day entries in schedule."""


def generate_study_plan(goal: str, subject: str = "General",
                        deadline: str = "1 week", plan_type: str = "weekly",
                        hours_per_day: int = 4) -> Dict:
    """Generate a structured study plan. Returns plan dict."""
    llm = get_llm(temperature=0.6)
    prompt = _build_planner_prompt(goal, subject, deadline, plan_type, hours_per_day)

    try:
        response = llm.invoke(prompt)
        raw = response.content if hasattr(response, "content") else str(response)
        raw = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("```").strip()
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
        return _fallback_plan(goal, subject, plan_type)
    except Exception as e:
        return _fallback_plan(goal, subject, plan_type)


def _fallback_plan(goal: str, subject: str, plan_type: str) -> Dict:
    days = 7 if plan_type == "weekly" else 30 if plan_type == "monthly" else 1
    schedule = []
    for i in range(days):
        date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
        schedule.append({
            "day": f"Day {i+1}",
            "date": date,
            "topics": [f"{subject} - Topic {i+1}"],
            "tasks": ["Review notes", "Practice problems"],
            "duration_hours": 3,
            "priority": "medium",
        })
    return {
        "overview": f"Study plan for: {goal}",
        "total_topics": days,
        "schedule": schedule,
        "milestones": [{"week": 1, "milestone": "Complete initial review"}],
        "tips": ["Study in focused 25-min blocks", "Take regular breaks", "Review daily"],
        "resources": [f"{subject} textbook", "Online resources"],
    }


def calculate_progress(plan: Dict, completed_days: List[int]) -> float:
    """Calculate % completion of a study plan."""
    total = len(plan.get("schedule", []))
    if total == 0:
        return 0.0
    return round((len(completed_days) / total) * 100, 1)


def get_todays_tasks(plan: Dict, day_index: int = 0) -> Dict:
    """Get today's study tasks from a plan."""
    schedule = plan.get("schedule", [])
    if not schedule or day_index >= len(schedule):
        return {}
    return schedule[day_index]


def generate_daily_challenge(subject: str) -> str:
    """Generate a single daily learning challenge."""
    llm = get_llm(temperature=0.8)
    prompt = f"""Generate an engaging daily learning challenge for the subject: {subject}.
Format:
**🎯 Today's Challenge:** [Challenge title]
**📋 Task:** [1-2 sentence task description]
**⏱️ Time:** [Estimated time]
**💡 Hint:** [One helpful hint]
**🏆 Reward:** [Points/badge description]

Make it fun, specific, and achievable in one study session."""
    try:
        response = llm.invoke(prompt)
        return response.content if hasattr(response, "content") else str(response)
    except Exception:
        return f"**🎯 Today's Challenge:** Master one concept in {subject}\n**📋 Task:** Pick one topic and create 5 summary bullet points.\n**⏱️ Time:** 30 minutes"
