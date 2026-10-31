"""A small skill dictionary used to compare resume skills with JD skills."""
import re

# canonical skill name -> words that mean the same thing
SKILLS = {
    "Python": ["python"],
    "Java": ["java"],
    "JavaScript": ["javascript", "js", "ecmascript"],
    "TypeScript": ["typescript"],
    "C++": ["c++"],
    "C#": ["c#"],
    "SQL": ["sql"],
    "MySQL": ["mysql"],
    "PostgreSQL": ["postgresql", "postgres"],
    "SQLite": ["sqlite"],
    "MongoDB": ["mongodb", "mongo"],
    "Redis": ["redis"],
    "HTML": ["html", "html5"],
    "CSS": ["css", "css3"],
    "Tailwind CSS": ["tailwind", "tailwindcss"],
    "Bootstrap": ["bootstrap"],
    "React": ["react", "reactjs", "react.js"],
    "Angular": ["angular"],
    "Vue": ["vue", "vuejs", "vue.js"],
    "Node.js": ["node.js", "nodejs", "node"],
    "Express": ["express", "express.js"],
    "Django": ["django"],
    "Flask": ["flask"],
    "FastAPI": ["fastapi"],
    "Streamlit": ["streamlit"],
    "Spring Boot": ["spring boot", "springboot"],
    "Hibernate": ["hibernate"],
    "JDBC": ["jdbc"],
    "Java Swing": ["swing", "java swing"],
    "Maven": ["maven"],
    "REST APIs": ["rest api", "rest apis", "restful", "restful api", "restful apis"],
    "GraphQL": ["graphql"],
    "Microservices": ["microservices", "microservice"],
    "JWT": ["jwt"],
    "Git": ["git"],
    "GitHub": ["github"],
    "Docker": ["docker"],
    "Kubernetes": ["kubernetes", "k8s"],
    "CI/CD": ["ci/cd", "cicd"],
    "Linux": ["linux"],
    "AWS": ["aws", "amazon web services"],
    "Azure": ["azure"],
    "GCP": ["gcp", "google cloud"],
    "Render": ["render"],
    "Postman": ["postman"],
    "Jira": ["jira"],
    "Agile": ["agile", "scrum"],
    "Data Structures": ["data structures", "dsa"],
    "Algorithms": ["algorithms"],
    "OOP": ["oop", "oops", "object-oriented", "object oriented"],
    "Testing": ["unit testing", "pytest", "junit", "selenium"],
    "Machine Learning": ["machine learning", "ml"],
    "Deep Learning": ["deep learning"],
    "NLP": ["nlp", "natural language processing"],
    "LLMs": ["llm", "llms", "large language model", "large language models"],
    "RAG": ["rag", "retrieval augmented generation", "retrieval-augmented generation"],
    "Hugging Face": ["hugging face", "huggingface"],
    "TensorFlow": ["tensorflow"],
    "PyTorch": ["pytorch"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Kafka": ["kafka"],
    "Power BI": ["power bi", "powerbi"],
    "Tableau": ["tableau"],
    "Excel": ["excel", "ms excel"],
    "Arduino": ["arduino"],
    "Embedded Systems": ["embedded systems", "embedded"],
}


def _build_patterns():
    """Compile one regex per skill. The lookarounds stop 'java' from matching 'javascript'."""
    patterns = {}
    for name, aliases in SKILLS.items():
        parts = [re.escape(alias.lower()) for alias in aliases]
        regex = r"(?<![\w+#.])(?:" + "|".join(parts) + r")(?![\w+#])"
        patterns[name] = re.compile(regex)
    return patterns


_PATTERNS = _build_patterns()


def extract_skills(text):
    """Return the list of known skills found in the text (in dictionary order)."""
    lowered = text.lower()
    found = []
    for name, pattern in _PATTERNS.items():
        if pattern.search(lowered):
            found.append(name)
    return found
