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
FILE_END = "===FILE_END==="

SYSTEM_PROMPT = f"""You are an autonomous software engineering agent.
You are given:
1. A natural language instruction describing a bug or change request.
2. Several retrieved code snippets from the repository that are likely relevant.
3. The full current content of the single file that looks most relevant to the fix.

Your job:
- Diagnose the likely root cause of the issue described in the instruction.
- Produce a corrected version of the FULL file content (not just a diff).
- Keep the fix minimal and focused; do not rewrite unrelated code.
- If the file genuinely does not need changes, say so in the explanation and
  return the file content unchanged.

You MUST respond in EXACTLY this plain text format, with nothing else
before or after it, and no markdown code fences:

{EXPLANATION_START}
<3-6 sentence explanation of the root cause and the fix>
{EXPLANATION_END}
{FILE_START}
<the full corrected file content, exactly as it should appear on disk>
{FILE_END}

Do not wrap the file content in triple quotes, markdown fences, or any
extra quoting - output the raw file content exactly as-is between the
markers.
"""


def build_context_block(chunks: list) -> str:
    parts = []
    for c in chunks:
        parts.append(f"--- {c['file_path']} ---\n{c['content']}")
    return "\n\n".join(parts)


def _extract_between(text: str, start_marker: str, end_marker: str) -> str:
    pattern = re.escape(start_marker) + r"(.*?)" + re.escape(end_marker)
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        raise ValueError(
            f"Could not find {start_marker}...{end_marker} in model output. "
            f"Raw output:\n{text[:1000]}"
        )
    return match.group(1).strip("\n")


def generate_fix(instruction: str, target_file_path: str,
                  target_file_content: str, context_chunks: list) -> dict:
    context_block = build_context_block(context_chunks)

    user_prompt = f"""Instruction: {instruction}

Target file to fix: {target_file_path}

Full current content of target file:
-----
{target_file_content}
-----

Other potentially relevant retrieved snippets from the repo:
{context_block}
"""

    response = _client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )

    raw = response.choices[0].message.content

    explanation = _extract_between(raw, EXPLANATION_START, EXPLANATION_END)
    updated_file_content = _extract_between(raw, FILE_START, FILE_END)

    return {
        "explanation": explanation,
        "updated_file_content": updated_file_content,
    }


def pick_target_file(retrieved_chunks: list) -> str:
    """Simplest possible heuristic: the top retrieved chunk's file is
    the one we attempt to fix. Good enough for a focused demo repo."""
    if not retrieved_chunks:
        raise ValueError("No relevant code found for this instruction.")
    return retrieved_chunks[0]["file_path"]
