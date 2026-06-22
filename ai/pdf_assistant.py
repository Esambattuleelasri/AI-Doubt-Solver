# ─────────────────────────────────────────────
#  ai/pdf_assistant.py — PDF Q&A with RAG
# ─────────────────────────────────────────────
import os
import re
from pathlib import Path
from typing import Optional
from config import settings

VECTOR_DB_DIR = Path("vector_db")
VECTOR_DB_DIR.mkdir(exist_ok=True)


def extract_text_from_pdf(pdf_path: str) -> tuple[str, int]:
    """Extract all text from PDF. Returns (text, page_count)."""
    text_parts = []
    page_count = 0

    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            page_count = len(pdf.pages)
            for page in pdf.pages:
                pt = page.extract_text()
                if pt:
                    text_parts.append(pt)
    except Exception:
        pass

    if not text_parts:
        try:
            import PyPDF2
            with open(pdf_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                page_count = len(reader.pages)
                for page in reader.pages:
                    pt = page.extract_text()
                    if pt:
                        text_parts.append(pt)
        except Exception:
            pass

    return "\n\n".join(text_parts), page_count


def build_vector_store(text: str, doc_id: str) -> Optional[str]:
    """Chunk text and build FAISS vector store. Returns index path."""
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain_community.vectorstores import FAISS
        from langchain_community.embeddings import HuggingFaceEmbeddings

        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_text(text)
        if not chunks:
            return None

        embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model)
        vectorstore = FAISS.from_texts(chunks, embeddings)

        index_path = str(VECTOR_DB_DIR / doc_id)
        vectorstore.save_local(index_path)
        return index_path

    except Exception as e:
        print(f"[PDF Assistant] Vector store error: {e}")
        return None


def load_vector_store(index_path: str):
    """Load existing FAISS vector store."""
    try:
        from langchain_community.vectorstores import FAISS
        from langchain_community.embeddings import HuggingFaceEmbeddings
        embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model)
        return FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    except Exception:
        return None


def ask_pdf(question: str, text: str = None, index_path: str = None) -> str:
    """Answer a question about a PDF using RAG or raw text fallback."""

    # Try RAG first
    if index_path and os.path.exists(index_path):
        try:
            from langchain.chains import RetrievalQA
            from langchain_community.vectorstores import FAISS
            from langchain_community.embeddings import HuggingFaceEmbeddings
            from ai.chatbot import get_llm

            embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model)
            vs = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
            retriever = vs.as_retriever(search_kwargs={"k": 4})
            qa_chain = RetrievalQA.from_chain_type(
                llm=get_llm(temperature=0.3),
                retriever=retriever,
                return_source_documents=False,
            )
            result = qa_chain.invoke({"query": question})
            return result.get("result", "No answer found.")
        except Exception as e:
            pass

    # Fallback: send raw text snippet to LLM
    if text:
        from ai.chatbot import get_llm
        llm = get_llm(temperature=0.3)
        truncated = text[:6000]
        prompt = f"""Based on the following document content, answer this question:

QUESTION: {question}

DOCUMENT:
{truncated}

Provide a clear, detailed answer based only on the document content."""
        try:
            response = llm.invoke(prompt)
            return response.content if hasattr(response, "content") else str(response)
        except Exception as e:
            return f"Error: {e}"

    return "No document content available."


def summarize_pdf(text: str, detail: str = "concise") -> str:
    """Generate a summary of the PDF content."""
    from ai.chatbot import get_llm
    llm = get_llm(temperature=0.4)

    truncated = text[:8000]
    if detail == "detailed":
        prompt = f"""Provide a detailed summary of this document with:
1. **Main Topics** (bullet list)
2. **Key Concepts** explained
3. **Important Points** to remember
4. **Chapter/Section Breakdown** if applicable

DOCUMENT:
{truncated}"""
    else:
        prompt = f"""Provide a concise summary (5-8 bullet points) of the main ideas in this document:

{truncated}"""

    try:
        response = llm.invoke(prompt)
        return response.content if hasattr(response, "content") else str(response)
    except Exception as e:
        return f"Summary error: {e}"


def extract_key_points(text: str) -> str:
    """Extract key points, formulas, and important facts."""
    from ai.chatbot import get_llm
    llm = get_llm(temperature=0.3)
    truncated = text[:7000]
    prompt = f"""Extract and organize the most important information from this document:

1. **Key Definitions** — Important terms and their meanings
2. **Core Concepts** — Main ideas and theories
3. **Important Formulas/Rules** — Any formulas, equations, or rules mentioned
4. **Critical Facts** — Must-remember facts and data points
5. **Examples Given** — Notable examples from the text

DOCUMENT:
{truncated}

Format as structured Markdown."""
    try:
        response = llm.invoke(prompt)
        return response.content if hasattr(response, "content") else str(response)
    except Exception as e:
        return f"Extraction error: {e}"


def generate_notes_from_pdf(text: str, style: str = "structured") -> str:
    """Generate study notes from PDF text."""
    from ai.chatbot import get_llm
    llm = get_llm(temperature=0.5)
    truncated = text[:7000]
    prompt = f"""Convert this document into comprehensive {style} study notes.
Format with clear headers, bullet points, and highlight key terms in **bold**.
Include a quick-revision section at the end.

DOCUMENT:
{truncated}"""
    try:
        response = llm.invoke(prompt)
        return response.content if hasattr(response, "content") else str(response)
    except Exception as e:
        return f"Notes generation error: {e}"
