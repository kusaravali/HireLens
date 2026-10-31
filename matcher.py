"""Core logic: compare a resume with a job description."""
from .chunker import chunk_resume, jd_requirements
from .config import PARTIAL_MATCH, STRONG_MATCH
from .embeddings import embed
from .retriever import ResumeIndex
from .skills import extract_skills


def _status(similarity):
    if similarity >= STRONG_MATCH:
        return "strong"
    if similarity >= PARTIAL_MATCH:
        return "partial"
    return "gap"


def _verdict(score):
    if score >= 75:
        return "Strong match"
    if score >= 55:
        return "Good match"
    if score >= 40:
        return "Partial match"
    return "Weak match"


def analyze(resume_text, jd_text):
    """Return scores, skill gaps and per-requirement evidence."""
    resume_chunks = chunk_resume(resume_text)
    requirements = jd_requirements(jd_text)

    if not resume_chunks:
        raise ValueError("The resume looks empty.")
    if not requirements:
        raise ValueError("The job description looks empty.")

    # Step 1: build the index and retrieve the best resume chunk for every requirement
    index = ResumeIndex(resume_chunks)
    requirement_vectors = embed(requirements)
    hits = index.search_batch(requirement_vectors, k=1)

    # Step 2: score each requirement
    points_for_status = {"strong": 1.0, "partial": 0.5, "gap": 0.0}
    evidence = []
    total_points = 0.0
    for requirement, hit in zip(requirements, hits):
        chunk_id, similarity = hit[0]
        status = _status(similarity)
        total_points += points_for_status[status]
        evidence.append(
            {
                "requirement": requirement,
                "best_resume_chunk": resume_chunks[chunk_id],
                "similarity": round(similarity, 3),
                "status": status,
            }
        )
    semantic_score = total_points / len(requirements)

    # Step 3: compare explicit skills
    jd_skills = extract_skills(jd_text)
    resume_skills = extract_skills(resume_text)
    matched = [s for s in jd_skills if s in resume_skills]
    missing = [s for s in jd_skills if s not in resume_skills]
    extra = [s for s in resume_skills if s not in jd_skills]

    if jd_skills:
        skill_score = len(matched) / len(jd_skills)
        overall = 0.6 * skill_score + 0.4 * semantic_score
        skill_percent = round(skill_score * 100)
    else:
        overall = semantic_score
        skill_percent = None

    score = round(overall * 100)

    return {
        "score": score,
        "verdict": _verdict(score),
        "skill_score": skill_percent,
        "semantic_score": round(semantic_score * 100),
        "matched_skills": matched,
        "missing_skills": missing,
        "extra_skills": extra,
        "evidence": evidence,
        "counts": {
            "strong": sum(1 for e in evidence if e["status"] == "strong"),
            "partial": sum(1 for e in evidence if e["status"] == "partial"),
            "gap": sum(1 for e in evidence if e["status"] == "gap"),
            "requirements": len(evidence),
        },
    }
