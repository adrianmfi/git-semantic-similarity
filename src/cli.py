import argparse
import os
import re
import sys
from typing import List, TypedDict

import numpy as np
from git import Repo
from git.exc import InvalidGitRepositoryError

from src.embeddings import embed_commit, embed_query, load_model

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


def main():
    try:
        parser = argparse.ArgumentParser(
            prog='git-semsim',
            description='Give a similarity score for each commit, based on the semantic similarity from an NLP embedding model')

        parser.add_argument(
            '-m', '--model',
            choices=['sentence-transformers/all-MiniLM-L6-v2'],
            default='sentence-transformers/all-MiniLM-L6-v2',
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

        model = load_model('sentence-transformers/all-MiniLM-L6-v2')
        query_embedding = embed_query(model, args.query)

        save_path = args.save_path
        if not save_path:
            save_path = os.path.join(
                repo.working_tree_dir,  '.git_semsim', sanitize_filename(args.model))
        if args.save:
            os.makedirs(save_path, exist_ok=True)

        for commit in commits:
            commit_embedding = embed_commit(
                model, commit,  args.save, save_path)
            similarity = np.dot(commit_embedding, query_embedding)
            print(str(similarity) + "\t"+commit['hexsha'] +
                  " "+commit['message'].splitlines()[0])
    except KeyboardInterrupt:
        sys.exit(0)
