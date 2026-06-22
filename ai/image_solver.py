# ─────────────────────────────────────────────
#  ai/image_solver.py — OCR + AI Image Analysis
# ─────────────────────────────────────────────
import os
import base64
from pathlib import Path
from typing import Optional
from PIL import Image
import io


def preprocess_image(image_path: str) -> str:
    """Preprocess image for better OCR — returns path to processed image."""
    try:
        import cv2
        import numpy as np
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Denoise + threshold
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        processed_path = image_path.replace(".", "_processed.")
        cv2.imwrite(processed_path, thresh)
        return processed_path
    except Exception:
        return image_path


def extract_text_easyocr(image_path: str) -> str:
    """Extract text using EasyOCR (handles handwritten + printed)."""
    try:
        import easyocr
        reader = easyocr.Reader(["en"], gpu=False, verbose=False)
        results = reader.readtext(image_path)
        return " ".join([text for (_, text, conf) in results if conf > 0.3])
    except Exception as e:
        return ""


def extract_text_tesseract(image_path: str) -> str:
    """Fallback OCR using pytesseract."""
    try:
        import pytesseract
        img = Image.open(image_path)
        return pytesseract.image_to_string(img)
    except Exception:
        return ""


def extract_text_from_image(image_path: str) -> str:
    """Try EasyOCR first, fallback to Tesseract, then PIL."""
    # Try preprocessing
    processed = preprocess_image(image_path)

    # EasyOCR
    text = extract_text_easyocr(processed)
    if text and len(text.strip()) > 10:
        return text.strip()

    # Tesseract fallback
    text = extract_text_tesseract(processed)
    if text and len(text.strip()) > 10:
        return text.strip()

    return ""


def image_to_base64(image_path: str) -> str:
    """Convert image to base64 for vision models."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def solve_from_image(image_path: str, user_hint: str = "") -> dict:
    """
    Main function: Extract text from image and get AI solution.
    Returns {"extracted_text": str, "solution": str, "method": str}
    """
    from config import settings
    from ai.chatbot import get_llm

    extracted_text = extract_text_from_image(image_path)
    method = "ocr"

    # If OpenAI or Gemini with vision, use multimodal
    if (settings.llm_provider == "openai" and settings.openai_api_key) or \
       (settings.llm_provider == "gemini" and settings.gemini_api_key):
        try:
            from openai import OpenAI
            if settings.llm_provider == "gemini":
                client = OpenAI(api_key=settings.gemini_api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
                model_name = settings.gemini_model or "gemini-3.5-flash"
            else:
                client = OpenAI(api_key=settings.openai_api_key)
                model_name = settings.openai_model

            img_b64 = image_to_base64(image_path)
            ext = Path(image_path).suffix.lower().replace(".", "")
            mime = f"image/{ext if ext in ['jpeg','jpg','png','gif','webp'] else 'jpeg'}"
            if mime == "image/jpg":
                mime = "image/jpeg"

            prompt_text = f"Solve this problem step-by-step. {user_hint}" if user_hint else \
                "Analyze this image. If it contains a math problem, science question, or any educational content, solve it step-by-step with clear explanations."

            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{img_b64}"}},
                        {"type": "text", "text": prompt_text},
                    ],
                }
            ]
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=1500,
            )
            solution = response.choices[0].message.content
            method = "vision"
            return {"extracted_text": extracted_text, "solution": solution, "method": method}
        except Exception as e:
            pass  # Fall through to text-based approach

    # Text-based approach using OCR output
    if not extracted_text:
        return {
            "extracted_text": "",
            "solution": "⚠️ Could not extract text from the image. Please ensure the image is clear and well-lit. Try a higher resolution image.",
            "method": "failed",
        }

    llm = get_llm(temperature=0.3)
    hint_part = f"\nAdditional context from user: {user_hint}" if user_hint else ""
    prompt = f"""I extracted the following text from an image of a problem/question:

"{extracted_text}"
{hint_part}

Please:
1. Identify what type of problem this is (Math, Physics, Chemistry, etc.)
2. Solve it completely, step-by-step
3. Explain each step clearly
4. Provide the final answer clearly highlighted

Use Markdown formatting."""

    try:
        response = llm.invoke(prompt)
        solution = response.content if hasattr(response, "content") else str(response)
        return {"extracted_text": extracted_text, "solution": solution, "method": "ocr+llm"}
    except Exception as e:
        return {
            "extracted_text": extracted_text,
            "solution": f"OCR extracted: {extracted_text}\n\nError getting AI solution: {e}",
            "method": "ocr_only",
        }


def save_uploaded_image(uploaded_file, upload_dir: str = "uploads") -> str:
    """Save Streamlit uploaded file to disk. Returns file path."""
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path
