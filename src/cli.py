import os
import re
import sys
from typing import List, TypedDict

import click
import numpy as np
from git import Commit, Repo
from git.exc import InvalidGitRepositoryError
import tqdm

os.environ["TOKENIZERS_PARALLELISM"] = "false"


class CommitData(TypedDict):
    commit: Commit
    similarity: float


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


def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx : min(ndx + n, l)]


def parse_model_args(args_str: str) -> dict:
    if not args_str:
        return {}

    result = {}
    try:
        # Parse "key1=value1,key2=value2" format
        pairs = args_str.split(",")
        for pair in pairs:
            key, value = pair.split("=")
            # Try to convert to appropriate type
            try:
                value = eval(value)  # safely convert numbers and bools
            except:
                pass  # keep as string if eval fails
            result[key] = value
    except Exception as e:
        click.echo(f"Error parsing model arguments: {str(e)}", err=True)
        sys.exit(1)
    return result


@click.command()
@click.option(
    "-m",
    "--model",
    type=str,
    default="sentence-transformers/all-mpnet-base-v2",
    show_default=True,
    help="A sentence-transformers model to use for embeddings (for example, a smaller and faster model sentence-transformers/all-MiniLM-L6-v2).",
)
@click.option(
    "--model-args",
    type=str,
    default="",
    help="Additional arguments for model initialization in format: key1=value1,key2=value2",
)
@click.option(
    "-c",
    "--cache",
    type=bool,
    default=True,
    show_default=True,
    help="Cache commit embeddings on disk for faster retrieval.",
)
@click.option(
    "--cache-dir",
    type=click.Path(),
    help="Directory to store cached embeddings (default: git_root/.git_semsim/model_name).",
)
@click.option(
    "--oneline",
    is_flag=True,
    help="Use a concise output format.",
)
@click.option(
    "--sort",
    type=bool,
    default=True,
    show_default=True,
    help="Sort results by similarity score.",
)
@click.option(
    "-n",
    "--max-count",
    type=int,
    default=None,
    help="Limit the number of results displayed.",
)
@click.option(
    "-b",
    "--batch-size",
    type=int,
    default=100,
    help="Batch size for embedding commits.",
)
@click.argument("query")
@click.argument("git_args", nargs=-1, type=click.UNPROCESSED)
def main(
    query,
    model,
    model_args,
    cache,
    cache_dir,
    oneline,
    sort,
    max_count,
    batch_size,
    git_args,
):
    """
    Give a similarity score for each commit based on semantic similarity from a sentence-transformers model.

    QUERY is the search string to compare with.
    """
    try:

        git_args = process_git_args(git_args)

        try:
            repo = Repo(".", search_parent_directories=True)
        except InvalidGitRepositoryError:
            click.echo("Error: Not a valid git repository.", err=True)
            sys.exit(1)

        commits = list(repo.iter_commits(**git_args))

        from src.embeddings import (
            EmbeddingsCache,
            embed_commit_batch,
            embed_query,
            load_model,
        )

        model_kwargs = parse_model_args(model_args)
        model_instance = load_model(model, **model_kwargs)
        query_embedding = embed_query(model_instance, query)

        # Determine the save path
        cache_obj = None
        if cache:
            if not cache_dir:
                cache_dir = os.path.join(
                    repo.working_tree_dir, ".gitsem", sanitize_filename(model)
                )
            os.makedirs(cache_dir, exist_ok=True)
            cache_obj = EmbeddingsCache(cache_dir)

        enable_tqdm = not cache or any(
            not cache_obj.has_embedding(commit.hexsha) for commit in commits
        )

        results: List[CommitData] = []
        with tqdm.tqdm(
            total=len(commits),
            desc="Processing commits",
            unit="commit",
            disable=not enable_tqdm,
        ) as pbar:
            for commit_batch in batch(commits, batch_size):
                commit_batch_embeddings = embed_commit_batch(
                    model_instance, commit_batch, cache_obj
                )

                for commit, commit_embedding in zip(
                    commit_batch, commit_batch_embeddings
                ):
                    # Convert cached embedding to float32
                    commit_embedding = commit_embedding.astype(np.float32)
                    similarity = model_instance.similarity(
                        commit_embedding, query_embedding[0]
                    )
                    similarity = float(similarity)
                    results.append({"commit": commit, "similarity": similarity})

                pbar.update(len(commit_batch))

        # Sort results
        if sort:
            results.sort(key=lambda x: x["similarity"], reverse=True)

        if max_count:
            results = results[:max_count]

        # Prepare output
        output_lines = []
        for data in results:
            commit = data["commit"]
            similarity = data["similarity"]
            if oneline:
                line = f"{similarity:.4f}\t{commit.hexsha} {commit.summary}"
            else:
                line = (
                    f"Commit {click.style(commit.hexsha, fg='yellow')}\n"
                    f"Author: {commit.author.name} <{commit.author.email}>\n"
                    f"Date:   {commit.authored_datetime}\n"
                    f"Similarity: {similarity:.4f}\n\n"
                    f"    {commit.message.strip()}\n"
                )
            output_lines.append(line)

        output = "\n".join(output_lines)

        click.echo_via_pager(output)

    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)
