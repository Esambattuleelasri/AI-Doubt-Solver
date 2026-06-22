# 🧠 AI Doubt Solver Pro

> **An intelligent, AI-powered learning platform built in Python** — solve doubts, analyze images & PDFs, generate quizzes, plan your studies, and track your progress.

---

## ✨ Features

| Module | Capabilities |
|--------|-------------|
| 💬 **AI Chat** | Real-time Q&A, subject-specific answers, conversation history, Teacher Mode |
| 🖼️ **Image Solver** | Upload problem images → OCR → GPT-4 Vision step-by-step solution |
| 📄 **PDF Assistant** | Upload PDFs → Q&A, summaries, key points, notes, flashcard generation |
| 🧠 **Quiz Generator** | MCQ / True-False / Fill-in-the-blank, difficulty levels, scored results |
| 📅 **Study Planner** | AI daily/weekly/monthly schedules, progress tracking, daily challenges |
| 📊 **Analytics** | Plotly charts — subject distribution, quiz trends, activity heatmap |
| ⚡ **Flashcards** | Interactive flip cards, topic generator, session scoring |
| ⚙️ **Settings** | AI provider config, language/translation, data export |

---

## 🚀 Quick Start

### 1. Clone & Setup

```bash
cd ai_doubt_solver
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
copy .env.example .env
# Edit .env — add your OpenAI API key
```

**Minimum `.env` to get started:**
```env
OPENAI_API_KEY=sk-your-key-here
LLM_PROVIDER=openai
```

### 3. Run the App

```bash
# Streamlit UI (main app)
streamlit run app.py

# FastAPI REST backend (optional, separate terminal)
python backend_main.py
```

The app opens at **http://localhost:8501**

---

## 📁 Project Structure

```
ai_doubt_solver/
├── app.py                  # Streamlit entry + login/register
├── backend_main.py         # FastAPI REST API
├── config.py               # Pydantic settings (reads .env)
├── requirements.txt
├── .env.example
│
├── database/
│   ├── db.py               # SQLAlchemy engine + sessions
│   ├── models.py           # ORM: User, Chat, Quiz, Flashcard, StudyPlan, PDF
│   └── crud.py             # All DB operations
│
├── auth/
│   ├── jwt_handler.py      # JWT create/verify
│   └── auth_service.py     # Register/login/session for Streamlit
│
├── ai/
│   ├── chatbot.py          # LangChain chat (OpenAI + Ollama)
│   ├── quiz_generator.py   # MCQ/TF/FillIn quiz generation + grading
│   ├── pdf_assistant.py    # RAG pipeline: FAISS + HuggingFace embeddings
│   ├── image_solver.py     # EasyOCR + GPT-4 Vision
│   ├── study_planner.py    # AI schedule generator + daily challenges
│   ├── flashcard_generator.py  # Flashcards from topic or text
│   └── teacher_mode.py     # Socratic teacher: explain → example → test
│
├── routes/
│   ├── auth.py             # /auth/register, /auth/login, /auth/me
│   ├── chat.py             # /chat/ask, /chat/history, /chat/sessions
│   └── quiz.py             # /quiz/generate, /quiz/submit, /quiz/history
│
├── pages/                  # Streamlit multi-page app
│   ├── 01_🏠_Home.py
│   ├── 02_💬_AI_Chat.py
│   ├── 03_🖼️_Image_Solver.py
│   ├── 04_📄_PDF_Assistant.py
│   ├── 05_🧠_Quiz_Generator.py
│   ├── 06_📅_Study_Planner.py
│   ├── 07_📊_Analytics.py
│   ├── 08_⚡_Flashcards.py
│   └── 09_⚙️_Settings.py
│
├── utils/
│   ├── ui_components.py    # Glass cards, badges, flashcard flip, banners
│   └── helpers.py          # File utils, timestamps, export
│
├── static/style.css        # Dark glassmorphism CSS theme
├── uploads/                # Uploaded images + PDFs
├── vector_db/              # FAISS vector indices
└── tests/
    ├── test_chatbot.py
    └── test_quiz.py
```

---

## 🤖 LLM Providers

### OpenAI (Default)
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o        # or gpt-4o-mini, gpt-3.5-turbo
```

### Ollama (Free, Local)
```bash
# Install Ollama: https://ollama.com
ollama pull llama3
```
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

---

## 🗄️ Database

**Default:** SQLite (zero setup, file: `ai_doubt_solver.db`)

**PostgreSQL:**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/ai_doubt_solver
```
Then run Alembic migrations:
```bash
alembic upgrade head
```

---

## 🧪 Running Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

---

## 📊 Database Schema

| Table | Key Columns |
|-------|------------|
| `users` | id, name, email, hashed_password, total_points, streak |
| `chats` | id, user_id, session_id, question, answer, subject |
| `quizzes` | id, user_id, topic, difficulty, score, total_questions |
| `quiz_questions` | id, quiz_id, question, options (JSON), correct_answer |
| `flashcards` | id, user_id, front, back, topic |
| `study_plans` | id, user_id, goal, schedule (JSON), progress_pct |
| `pdf_documents` | id, user_id, filename, text_content, vector_index_path |

---

## 🎨 UI Theme

- **Dark Mode** background: `#0F172A`
- **Primary:** `#6366F1` (Indigo)
- **Secondary:** `#8B5CF6` (Violet)
- **Accent:** `#06B6D4` (Cyan)
- Glassmorphism cards with `backdrop-filter: blur`
- Smooth CSS animations (`fadeIn`, `slideIn`, `glow`)
- JetBrains Mono for code, Inter for UI text

---

## 🔌 FastAPI Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login → JWT token |
| GET | `/auth/me` | Current user info |
| POST | `/chat/ask` | Ask AI question |
| GET | `/chat/history/{user_id}` | Chat history |
| GET | `/chat/sessions/{user_id}` | All sessions |
| POST | `/quiz/generate` | Generate quiz |
| POST | `/quiz/submit` | Submit answers |
| GET | `/quiz/history/{user_id}` | Quiz history |

API Docs: **http://localhost:8000/docs**

---

## 🏆 Viva Description

> *"AI Doubt Solver Pro is a Python-based intelligent learning platform that uses artificial intelligence, natural language processing, OCR, and document analysis to provide instant doubt resolution. It supports text, image, PDF, and voice-based queries, generates quizzes and study plans, and tracks learning progress through an interactive dashboard. The system helps students learn more efficiently through personalized AI assistance."*

---

## 📦 Key Dependencies

| Package | Purpose |
|---------|---------|
| `streamlit` | Interactive web UI |
| `fastapi` + `uvicorn` | REST API backend |
| `langchain` + `langchain-openai` | LLM orchestration |
| `openai` | GPT-4o API |
| `sentence-transformers` + `faiss-cpu` | PDF RAG pipeline |
| `easyocr` + `opencv-python-headless` | Image OCR |
| `pdfplumber` + `PyPDF2` | PDF text extraction |
| `plotly` + `pandas` | Analytics charts |
| `sqlalchemy` + `alembic` | Database ORM |
| `python-jose` + `passlib` | JWT auth |
| `deep-translator` | Multi-language support |

---

*Built with ❤️ using Python, LangChain, and Streamlit*
