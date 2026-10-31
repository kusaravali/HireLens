"""Central settings for HireLens."""
import os

from dotenv import load_dotenv

# Read values from a .env file if it exists
load_dotenv()

# --- LLM (optional) ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()

# --- Embedding model (downloads once, about 90 MB) ---
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2").strip()

# --- Matching thresholds (cosine similarity) ---
STRONG_MATCH = 0.50   # resume clearly covers the requirement
PARTIAL_MATCH = 0.35  # resume partly covers the requirement

# --- Upload limit ---
MAX_UPLOAD_MB = 5
