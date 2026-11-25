import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3.5-flash-lite"

TONES = {
    "beginner": "beginner-friendly, simple language, no jargon, short sentences, relatable analogies",
    "technical": "technical and precise, assumes domain knowledge, uses correct terminology and specifics",
    "casual": "conversational and friendly, light humor allowed, easy to skim",
    "professional": "polished and authoritative, clear and business-appropriate",
}

LENGTHS = {
    "short": 600,
    "medium": 1000,
    "long": 1500,
}

MIN_WORD_RATIO = 0.8
MAX_RETRIES = 3
