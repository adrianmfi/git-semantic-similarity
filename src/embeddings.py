import json
import os
from git import Commit
import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingsCache:
    def __init__(self, cache_dir: str):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.embeddings_file = os.path.join(cache_dir, "embeddings.jsonl")
        self.embeddings = {}
        self._load_embeddings()

    def _load_embeddings(self):
        """Load embeddings from the cache file into a dictionary."""
        if not os.path.exists(self.embeddings_file):
            return

        with open(self.embeddings_file, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                commit_hash = data["commit_hash"]
                if commit_hash not in self.embeddings:
                    self.embeddings[commit_hash] = np.array(data["embedding"])

    def get_embedding(self, commit_hash: str):
        """Retrieve an embedding from the cache."""
        return self.embeddings.get(commit_hash)

    def add_embedding(self, commit_hash: str, embedding: np.ndarray):
        """Add a new embedding to the cache and append it to the cache file."""
        rounded_embedding = np.round(embedding, decimals=3)
        self.embeddings[commit_hash] = rounded_embedding
        data = {
            "commit_hash": commit_hash,
            "embedding": embedding.tolist(),
        }
        with open(self.embeddings_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")

    def has_embedding(self, commit_hash: str) -> bool:
        return commit_hash in self.embeddings


def embed_commit(model, commit: Commit, cache: EmbeddingsCache | None):
    if cache is None:
        return model.encode([commit.message])[0]

    commit_hash = str(commit.hexsha)
    embedding = cache.get_embedding(commit_hash)
    if embedding is not None:
        return embedding
    embedding = model.encode([commit.message])[0]
    cache.add_embedding(commit_hash, embedding)
    return embedding


def embed_query(model, text: str):
    embeddings = model.encode([text])[0]
    return embeddings


def load_model(model_name: str):
    return SentenceTransformer(
        model_name, tokenizer_kwargs={"clean_up_tokenization_spaces": False}
    )
