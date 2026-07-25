"""
The reasoning core: takes a natural-language instruction plus retrieved code
context, and produces an explanation + a full corrected file. This stands
in for the "Planner + Bug Agent + Code Generation Agent" chain from the
full architecture, collapsed into a single LLM call for the demo version.

Note: we deliberately do NOT ask the model for JSON output. Source code
(docstrings, quotes, escapes) is unreliable to embed inside a JSON string
even with json_object mode - models frequently break their own JSON doing
so. Plain-text markers are far more robust for code-shaped payloads.
"""
import re
from openai import OpenAI

from app.config import GROQ_API_KEY, GROQ_BASE_URL, LLM_MODEL

# Uses Groq's free, OpenAI-compatible API instead of paid OpenAI.
_client = OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)

EXPLANATION_START = "===EXPLANATION_START==="
EXPLANATION_END = "===EXPLANATION_END==="
FILE_START = "===FILE_START==="
FILE_END = "