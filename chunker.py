"""Split resumes into chunks and job descriptions into requirements."""
import re

# Bullet characters at the start of a line (-, *, dots, dashes, arrows)
BULLET_PREFIX = re.compile(r"^[\-\*\u2022\u25cf\u25aa\u2023\u00b7\u2013\u2014>]+\s*")


def strip_bullet(line):
    return BULLET_PREFIX.sub("", line).strip()


def chunk_resume(text, target_chars=300):
    """Group resume lines into chunks of roughly 300 characters."""
    lines = [strip_bullet(line) for line in text.split("\n")]
    lines = [line for line in lines if line]

    chunks = []
    current = ""
    for line in lines:
        current = (current + " " + line).strip()
        if len(current) >= target_chars:
            chunks.append(current)
            current = ""

    # Whatever is left at the end
    if current:
        if chunks and len(current) < 60:
            chunks[-1] = chunks[-1] + " " + current
        else:
            chunks.append(current)

    return chunks


def jd_requirements(text, max_items=40):
    """Turn a job description into a list of requirement sentences."""
    requirements = []
    for line in text.split("\n"):
        line = strip_bullet(line)
        if not line:
            continue
        # A long line may hold several sentences
        for part in re.split(r"(?<=[.!?])\s+", line):
            part = part.strip()
            # Skip headings and fragments (fewer than 4 words)
            if len(part) >= 15 and len(part.split()) >= 4:
                requirements.append(part)

    # Fallback: very short JD, use the whole text as one requirement
    if not requirements and text.strip():
        requirements = [text.strip()[:500]]

    return requirements[:max_items]
