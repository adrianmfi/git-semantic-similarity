import argparse
import os
import re
import sys
from typing import List, TypedDict

import numpy as np
from git import Repo
from git.exc import InvalidGitRepositoryError
from InstructorEmbedding import INSTRUCTOR


def parse_git_args(remainder):
    git_args = {}
    it = iter(remainder)  # Create an iterator for the remainder list
    for arg in it:
        if arg.startswith('-'):
            # Remove leading dashes and split if it contains '='
            key, eq, val = arg.lstrip('-').partition('=')
            if eq:  # If the argument is in the format -key=value or --key=value
                git_args[key] = val
            else:  # If the argument is in the format -key value or --key value
                # Peek next item to see if it's a value or another key
                next_arg = next(it, None)
                if next_arg and not next_arg.startswith('-'):
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
    return re.sub(r'[<>:"/\\|?*]', '_', filename)


class Commit(TypedDict):
    hexsha: str
    message: str


def embed_query(instructor_model, text: str):
    instruction = "Represent the search term for retrieval of git commit messages"
    embeddings = instructor_model.encode([[instruction, text]])[0]
    return embeddings


def embed_commit(instructor_model, commit: Commit, save: bool, save_dir: str):
    embedding_path = os.path.join(save_dir, str(commit['hexsha']))
    try:
        with open(embedding_path, 'rb') as f:
            return np.load(f)
    except IOError:
        # missing embedding
        pass

    instruction = "Represent the commit message for retrieval"
    embeddings = instructor_model.encode([[instruction, commit['message']]])[0]

    if save:
        with open(embedding_path, 'wb') as f:
            np.save(f, embeddings)

    return embeddings


def main():
    try:
        parser = argparse.ArgumentParser(
            prog='git-semsim',
            description='Give a similarity score for each commit, based on the semantic similarity from an NLP embedding model')

        parser.add_argument(
            '-m', '--model',
            choices=['hkunlp/instructor-xl', "hkunlp/instructor-large"],
            default='hkunlp/instructor-xl',
            help="Model to use")

        parser.add_argument(
            '-s', '--save',
            default=True,
            type=bool,
            help="Save commit embeddings")

        parser.add_argument(
            '--save-path',
            help="Path to save embeddings to (default git_root/.git_semsim/model_name)")

        parser.add_argument('query',
                            help="The string to compare with")
        parser.add_argument('git_args', nargs=argparse.REMAINDER,
                            help="Arguments to forward to git rev-list (for example --author bob --max-count 10)")

        args = parser.parse_args()
        git_args = parse_git_args(args.git_args)
        try:
            repo = Repo('.', search_parent_directories=True)
        except InvalidGitRepositoryError:
            print("Not a valid git repository")
            sys.exit(1)

        commits: List[Commit] = [{'hexsha': commit.hexsha, 'message': commit.message}
                                 for commit in repo.iter_commits(**git_args)]

        instructor_model = INSTRUCTOR(args.model)
        query_embedding = embed_query(instructor_model, args.query)

        save_path = args.save_path
        if not save_path:
            save_path = os.path.join(
                repo.working_tree_dir,  '.git_semsim', sanitize_filename(args.model))
        if args.save:
            os.makedirs(save_path, exist_ok=True)

        for commit in commits:
            commit_embedding = embed_commit(
                instructor_model, commit,  args.save, save_path)
            similarity = np.dot(commit_embedding, query_embedding)
            print(str(similarity) + "\t"+commit['hexsha'] +
                  " "+commit['message'].splitlines()[0])
    except KeyboardInterrupt:
        sys.exit(0)
