"""Resume analysis using Groq (free, fast LLM API).

Get a free API key (no credit card) at: https://console.groq.com/keys
"""
import os
import json
import re
from typing import Optional
from groq import Groq


SYSTEM_PROMPT = """You are an expert technical recruiter and ATS specialist.
Analyze the candidate's resume against the job description and respond with STRICT JSON only.

Return this exact shape:
{
  "score": <integer 0-100>,
  "verdict": "<one short sentence overall verdict>",
  "summary": "<2-3 sentence assessment of how well the resume fits>",
  "strengths": ["...", "..."],
  "weaknesses": ["...", "..."],
  "missing_keywords": ["...", "..."],
  "suggestions": ["...", "..."],
  "section_scores": [
    {"section": "Skills", "score": <0-5>, "note": "<one sentence>"},
    {"section": "Experience", "score": <0-5>, "note": "<one sentence>"},
    {"section": "Education", "score": <0-5>, "note": "<one sentence>"},
    {"section": "Projects/Impact", "score": <0-5>, "note": "<one sentence>"},
    {"section": "Formatting/Clarity", "score": <0-5>, "note": "<one sentence>"}
  ]
}

Rules:
- Output ONLY valid JSON. No markdown fences, no commentary.
- 3-7 items per list.
- Be specific and actionable; avoid generic platitudes.
"""


def _client() -> tuple[Groq, str]:
    api_key = (os.getenv("GROQ_API_KEY") or "").strip()
    if not api_key or api_key == "your-groq-api-key-here":
        raise ValueError(
            "GROQ_API_KEY is not set. Get a FREE key at https://console.groq.com/keys "
            "and add it to your .env file, then restart the server."
        )
    model = (os.getenv("GROQ_MODEL") or "llama-3.3-70b-versatile").strip()
    return Groq(api_key=api_key), model


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```\s*$", "", text)
    return text.strip()


# Models that support Groq's JSON response format
_JSON_MODE_MODELS = {
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
}


def analyze_resume(resume_text: str, job_description: Optional[str] = None) -> dict:
    client, model = _client()

    user_msg = f"RESUME:\n{resume_text}"
    if job_description:
        user_msg += f"\n\nJOB DESCRIPTION:\n{job_description}"
    else:
        user_msg += "\n\nJOB DESCRIPTION: (none provided — assess against general industry expectations)"

    kwargs = dict(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.3,
    )
    if model in _JSON_MODE_MODELS:
        kwargs["response_format"] = {"type": "json_object"}

    completion = client.chat.completions.create(**kwargs)
    raw = (completion.choices[0].message.content or "").strip()
    if not raw:
        raise ValueError("AI returned an empty response. Try again.")

    raw = _strip_fences(raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise ValueError(f"Could not parse AI response as JSON. Raw: {raw[:300]}")
