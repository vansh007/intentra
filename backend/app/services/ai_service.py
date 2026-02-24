import asyncio
import google.generativeai as genai
from app.core.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

model = genai.GenerativeModel("models/gemini-2.5-flash")


async def generate_summary(text: str) -> str:
    if not text or len(text.strip()) < 30:
        return "No summary available."

    prompt = f"""
Summarize the following content in 2-3 clear sentences.
Be concise. No preamble.

Content:
{text[:3000]}

Summary:
"""

    try:
        response = await asyncio.to_thread(
            model.generate_content,
            prompt
        )
        return response.text.strip()
    except Exception as e:
        print("[ai_service] ERROR:", e)
        return "AI service temporarily unavailable."

# import asyncio
# import google.generativeai as genai
# from app.core.config import settings

# # Configure API key
# genai.configure(api_key=settings.GEMINI_API_KEY)

# # Use supported model for this SDK
# model = genai.GenerativeModel("gemini-pro")


# async def generate_summary(text: str) -> str:
#     """
#     Generate a 2–3 sentence summary of the provided text.
#     """

#     if not text or len(text.strip()) < 30:
#         return "No summary available."

#     prompt = f"""
# You are a summarization assistant.

# Summarize the following content in 2–3 clear, concise sentences.
# Focus only on the core idea.

# Content:
# {text[:3000]}

# Summary:
# """

#     try:
#         # Run blocking Gemini call in a thread (important for FastAPI async)
#         response = await asyncio.to_thread(
#             model.generate_content,
#             prompt
#         )

#         if not response or not response.text:
#             return "Summary generation failed."

#         return response.text.strip()

#     except Exception as e:
#         print("Gemini Error:", e)
#         return "AI service temporarily unavailable."