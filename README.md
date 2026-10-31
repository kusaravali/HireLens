# HireLens
HireLens is a RAG-powered resume-to-job-description matcher built with FastAPI and sentence-transformers. Upload your resume, paste a job posting, and get a match score, matched and missing skills, and requirement-by-requirement evidence from your resume. An optional LLM writes a short report to help you close the gaps and tailor your resume.
# HireLens

Resume vs job description matching with explainable skill gaps, built as a RAG-style pipeline.

**How it works**

1. The resume is split into chunks and the job description into requirement sentences.
2. Every text is embedded with `all-MiniLM-L6-v2` (runs locally, no API needed).
3. For each requirement, the most similar resume chunk is retrieved (cosine similarity).
4. Each requirement is marked strong, partial or gap, and explicit skills are compared separately.
5. An LLM (Groq, optional) writes a short report using only the retrieved evidence. Without a key, a built-in summary is used.

Final score = 60% skill match + 40% requirement coverage.

## Setup (Windows, VS Code terminal)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

macOS or Linux: `source .venv/bin/activate` instead of the activate line above.

## Optional: AI-written reports

1. Get a free key at https://console.groq.com
2. Copy `.env.example` to `.env` and paste the key after `GROQ_API_KEY=`

## Run

```bash
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000

The first start downloads the embedding model (about 90 MB), so it needs internet once.
Try it with `sample_data/sample_resume.txt` and `sample_data/sample_jd.txt`.

## Folder structure

```
hirelens/
├── app/
│   ├── __init__.py
│   ├── config.py       settings and thresholds
│   ├── parser.py       PDF / DOCX / TXT reading
│   ├── chunker.py      resume chunks, JD requirements
│   ├── skills.py       skill dictionary and extraction
│   ├── embeddings.py   embedding model
│   ├── retriever.py    in-memory vector search
│   ├── matcher.py      scoring logic
│   ├── llm.py          Groq explanation with fallback
│   └── main.py         FastAPI routes
├── static/index.html   web UI
├── sample_data/        test resume and JD
├── requirements.txt
├── .env.example
└── README.md
```

## Notes

- Scanned (image-only) PDFs have no text to extract. Paste the text instead.
- Run `uvicorn` from the `hirelens` folder, not from inside `app/`.
- Python 3.9 or newer.
