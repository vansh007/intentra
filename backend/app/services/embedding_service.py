import google.generativeai as genai
from app.core.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)


async def generate_embedding(text: str) -> list[float] | None:
    if not text or len(text.strip()) < 5:
        return None

    try:
        response = genai.embed_content(
            model="models/gemini-embedding-001",
            content=text[:2000],
            task_type="retrieval_document"
        )

        return response["embedding"]

    except Exception as e:
        print(f"Embedding error: {e}")
        return None