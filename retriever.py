"""A tiny in-memory vector index over resume chunks."""
import numpy as np

from .embeddings import embed


class ResumeIndex:
    def __init__(self, chunks):
        self.chunks = list(chunks)
        self.vectors = embed(self.chunks)

    def search_batch(self, query_vectors, k=1):
        """For each query vector return the top-k (chunk_index, similarity) pairs."""
        k = max(1, min(k, len(self.chunks)))
        # Vectors are normalised, so a dot product equals cosine similarity
        similarities = query_vectors @ self.vectors.T

        results = []
        for row in similarities:
            best = np.argsort(-row)[:k]
            results.append([(int(i), float(row[i])) for i in best])
        return results
