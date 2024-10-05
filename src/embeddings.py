import json
import os
from git import Commit
import numpy as np
from sentence_transformers import SentenceTransformer

msg_prefix = "commit message:\n"


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
        self.embeddings[commit_hash] = embedding
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
        return model.encode([msg_prefix + commit.message])[0]

    commit_hash = str(commit.hexsha)
    embedding = cache.get_embedding(commit_hash)
    if embedding is not None:
        return embedding
    embedding = model.encode([msg_prefix + commit.message])[0]
    cache.add_embedding(commit_hash, embedding)
    return embedding


def embed_commit_batch(model, commits, cache: EmbeddingsCache | None):
    if cache is None:
        return model.encode([msg_prefix + commit.message for commit in commits])

    commits_to_embed = [c for c in commits if not cache.has_embedding(c.hexsha)]
    if len(commits_to_embed) > 0:
        embeddings = model.encode(
            [msg_prefix + commit.message for commit in commits_to_embed]
        )
        for commit, embedding in zip(commits_to_embed, embeddings):
            cache.add_embedding(commit.hexsha, embedding)

    return np.array([cache.get_embedding(c.hexsha) for c in commits])


def embed_query(model, text: str):
    embeddings = model.encode([text])[0]
    return embeddings


def load_model(model_name: str):
    return SentenceTransformer(
        model_name, tokenizer_kwargs={"clean_up_tokenization_spaces": False}
    )
