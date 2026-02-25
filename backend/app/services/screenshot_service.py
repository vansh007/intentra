import asyncio
import base64
import google.generativeai as genai
from app.core.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)


async def extract_text_from_screenshot(image_bytes: bytes) -> str:
    """Uses Gemini Vision to read and understand a screenshot."""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")

        image_part = {
            "mime_type": "image/png",
            "data": base64.b64encode(image_bytes).decode("utf-8")
        }

        prompt = """You are analyzing a screenshot the user saved.
Extract and describe:
1. What this page/content is about
2. Key information visible
3. Why someone might have saved this

Be concise, 3-4 sentences max."""

        response = await asyncio.to_thread(
            model.generate_content,
            [prompt, image_part]
        )
        return response.text.strip()
    except Exception as e:
        print(f"[screenshot_service] Error: {e}")
        return None