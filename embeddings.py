"""Turn text into vectors with a sentence-transformers model."""
from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

from .config import EMBED_MODEL


@lru_cache(maxsize=1)
def get_model():
    """Load the model once and reuse it."""
    return SentenceTransformer(EMBED_MODEL)


def embed(texts):
    """Return a normalised float32 matrix, one row per text."""
    texts = list(texts)
    if not texts:
        return np.zeros((0, 1), dtype=np.float32)
    vectors = get_model().encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    return np.asarray(vectors, dtype=np.float32)
