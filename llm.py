"""Turn the match result into a readable explanation (Groq API, with a safe fallback)."""
import requests

from .config import GROQ_API_KEY, GROQ_MODEL

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def llm_enabled():
    return bool(GROQ_API_KEY)


def _build_prompt(result):
    lines = [
        f"Overall match score: {result['score']}/100 ({result['verdict']})",
        f"Matched skills: {', '.join(result['matched_skills']) or 'none'}",
        f"Missing skills: {', '.join(result['missing_skills']) or 'none'}",
        "",
        "Evidence (job requirement -> best resume text -> status):",
    ]
    for item in result["evidence"][:12]:
        lines.append(
            f"- {item['requirement'][:160]} -> {item['best_resume_chunk'][:160]} -> {item['status']}"
        )

    return (
        "\n".join(lines)
        + "\n\nWrite a short report with these parts:\n"
        "1. Summary (2-3 sentences)\n"
        "2. Top 3 strengths\n"
        "3. Top 3 gaps and one concrete way to close each\n"
        "4. Two tips to reword the resume for this job\n"
        "Use only the evidence above. Do not invent experience. Maximum 300 words, plain text."
    )


def _template_explanation(result):
    """Used when there is no API key or the API call fails."""
    counts = result["counts"]
    parts = [
        f"Your resume scores {result['score']}/100 for this role ({result['verdict']}).",
        f"{counts['strong']} of {counts['requirements']} requirements are clearly covered, "
        f"{counts['partial']} partly, and {counts['gap']} show no clear evidence.",
    ]
    if result["matched_skills"]:
        parts.append("Skills you already show: " + ", ".join(result["matched_skills"]) + ".")
    if result["missing_skills"]:
        parts.append(
            "Skills to add or build projects around: " + ", ".join(result["missing_skills"]) + "."
        )
    gaps = [e["requirement"] for e in result["evidence"] if e["status"] == "gap"][:3]
    if gaps:
        parts.append("Requirements with the weakest evidence:\n- " + "\n- ".join(gaps))
    return "\n\n".join(parts)


def explain(result):
    """Return {"text": ..., "source": "llm" or "template"}."""
    if not llm_enabled():
        return {"text": _template_explanation(result), "source": "template"}

    try:
        response = requests.post(
            GROQ_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": GROQ_MODEL,
                "temperature": 0.2,
                "max_tokens": 600,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a careful career coach. Use only the evidence provided.",
                    },
                    {"role": "user", "content": _build_prompt(result)},
                ],
            },
            timeout=40,
        )
        response.raise_for_status()
        text = response.json()["choices"][0]["message"]["content"].strip()
        if not text:
            raise ValueError("Empty response")
        return {"text": text, "source": "llm"}
    except Exception:
        # Never let an API problem break the whole analysis
        return {"text": _template_explanation(result), "source": "template"}
