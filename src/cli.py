import os
import re
import sys
from typing import List, TypedDict

import click
import numpy as np
from git import Repo
from git.exc import InvalidGitRepositoryError

from src.embeddings import embed_commit, embed_query, load_model


def process_git_args(remainder):
    git_args = {}
    it = iter(remainder)  # Create an iterator for the remainder list
    for arg in it:
        if arg.startswith("-"):
            # Remove leading dashes and split if it contains '='
            key, eq, val = arg.lstrip("-").partition("=")
            if eq:  # If the argument is in the format --key=value
                git_args[key] = val
            else:  # If the argument is in the format --key value
                # Peek next item to see if it's a value or another key
                next_arg = next(it, None)
                if next_arg and not next_arg.startswith("-"):
                    git_args[key] = next_arg
                else:
                    git_args[key] = True  # Handle flags without explicit value
                    if next_arg:
                        # Reinsert the peeked value
                        it = iter([next_arg] + list(it))
        else:
            # Handle non-prefixed args if necessary
            pass
    return git_args


def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', "_", filename)


class Commit(TypedDict):
    hexsha: str
    message: str


@click.command()
@click.option(
    "-m",
    "--model",
    type=click.Choice(["sentence-transformers/all-MiniLM-L6-v2"]),
    default="sentence-transformers/all-MiniLM-L6-v2",
    show_default=True,
    help="Model to use.",
)
@click.option(
    "-s",
    "--save",
    type=bool,
    default=True,
    show_default=True,
    help="Save commit embeddings.",
)
@click.option(
    "--save-path",
    type=click.Path(),
    help="Path to save embeddings (default: git_root/.git_semsim/model_name).",
)
@click.argument("query")
@click.argument("git_args", nargs=-1, type=click.UNPROCESSED)
def main(query, model, save, save_path, git_args):
    """
    Give a similarity score for each commit based on semantic similarity using an NLP embedding model.

    QUERY is the search string to compare with.
    """
    try:

        git_args = process_git_args(git_args)
        print(git_args)

        try:
            repo = Repo(".", search_parent_directories=True)
        except InvalidGitRepositoryError:
            click.echo("Not a valid git repository.", err=True)
            sys.exit(1)

        commits: List[Commit] = [
            {"hexsha": commit.hexsha, "message": commit.message}
            for commit in repo.iter_commits(**git_args)
        ]

        model_instance = load_model(model)
        query_embedding = embed_query(model_instance, query)

        # Determine the save path
        if not save_path:
            save_path = os.path.join(
                repo.working_tree_dir, ".git_semsim", sanitize_filename(model)
            )
        if save:
            os.makedirs(save_path, exist_ok=True)

        for commit in commits:
            commit_embedding = embed_commit(model_instance, commit, save, save_path)
            similarity = np.dot(commit_embedding, query_embedding)
            click.echo(
                f"{similarity}\t{commit['hexsha']} {commit['message'].splitlines()[0]}"
            )
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
