import os
from git import Commit
import numpy as np
from sentence_transformers import SentenceTransformer


def embed_query(model, text: str):
    embeddings = model.encode([text])[0]
    return embeddings


def embed_commit(model, commit: Commit, save: bool, save_dir: str | None):
    embedding_path = os.path.join(save_dir, str(commit["hexsha"]))
    try:
        with open(embedding_path, "rb") as f:
            return np.load(f)
    except IOError:
        # missing embedding
        pass

    embeddings = model.encode([commit["message"]])[0]

    if save:
        with open(embedding_path, "wb") as f:
            np.save(f, embeddings)

    return embeddings


def load_model(model_name: str):
    return SentenceTransformer(
        model_name, tokenizer_kwargs={"clean_up_tokenization_spaces": False}
    )
