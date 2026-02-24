import json
import asyncio
import google.generativeai as genai
from app.core.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-2.5-flash")

VALID_INTENTS = [
    "learning",
    "career",
    "startup",
    "shopping",
    "entertainment",
    "self-improvement",
    "other"
]


async def classify_intent(title: str, url: str, content: str) -> dict:
    combined_text = f"""
Title: {title}
URL: {url}
Content: {content[:2500]}
"""

    if len(combined_text.strip()) < 20:
        return fallback()

    prompt = f"""
You are an AI that infers USER INTENT behind saved content.

Your job:
Determine WHY the user saved this.
Infer motivation, not just topic.

Valid intents:
- learning (courses, research, tutorials, knowledge)
- career (jobs, internships, resumes, networking)
- startup (business ideas, funding, entrepreneurship)
- shopping (products, Amazon links, wishlists)
- entertainment (memes, videos, social browsing)
- self-improvement (fitness, mindset, productivity)
- other (ONLY if absolutely unclear)

IMPORTANT:
- Do NOT default to "other" unless truly ambiguous.
- If it's a product page → shopping
- If it's research or GitHub → learning
- If it's job/career related → career
- If it's YouTube educational → learning
- If it's purely fun scrolling → entertainment

Return ONLY raw JSON:
{{"intent": "<valid>", "confidence": <0-1>, "suggested_action": "<short next step>"}}

Content:
{combined_text}
"""

    try:
        response = await asyncio.to_thread(
            model.generate_content,
            prompt
        )

        raw = response.text.strip()

        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        result = json.loads(raw)

        if result.get("intent") not in VALID_INTENTS:
            result["intent"] = "other"

        return result

    except Exception as e:
        print("[intent_service] ERROR:", e)
        return fallback()


def fallback():
    return {
        "intent": "other",
        "confidence": 0.4,
        "suggested_action": "Review this save manually."
    }

# import json
# import asyncio
# import google.generativeai as genai
# from app.core.config import settings

# genai.configure(api_key=settings.GEMINI_API_KEY)

# # ✅ Correct model for v1beta SDK
# model = genai.GenerativeModel("models/gemini-1.0-pro")

# VALID_INTENTS = [
#     "learning",
#     "career",
#     "startup",
#     "shopping",
#     "entertainment",
#     "self-improvement",
#     "other"
# ]


# async def classify_intent(text: str) -> dict:
#     if not text or len(text.strip()) < 10:
#         return {
#             "intent": "other",
#             "confidence": 0.5,
#             "suggested_action": "Review this save manually."
#         }

#     prompt = f"""
# You are an intent classification AI.
# Analyze the content below and return ONLY a valid JSON object.
# Do NOT include markdown. Do NOT include explanations.

# Valid intents: {", ".join(VALID_INTENTS)}

# Return exactly:
# {{
#   "intent": "<one of the valid intents>",
#   "confidence": <float between 0 and 1>,
#   "suggested_action": "<one short actionable sentence>"
# }}

# Content:
# {text[:2000]}
# """

#     try:
#         # Run blocking Gemini call safely in async FastAPI
#         response = await asyncio.to_thread(
#             model.generate_content,
#             prompt
#         )

#         raw = response.text.strip()

#         # Remove code fences if present
#         if raw.startswith("```"):
#             raw = raw.split("```")[1]
#             if raw.startswith("json"):
#                 raw = raw[4:]
#         raw = raw.strip()

#         result = json.loads(raw)

#         if result.get("intent") not in VALID_INTENTS:
#             result["intent"] = "other"

#         return result

#     except Exception as e:
#         print("Intent classification error:", e)
#         return {
#             "intent": "other",
#             "confidence": 0.5,
#             "suggested_action": "Review this save manually."
#         }
