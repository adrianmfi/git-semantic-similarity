# git-semantic-similarity

## Summary:
git-semantic-similarity is a command-line tool leveraging NLP models to search for commits by commit message with semantic similarity. All computations are done locally.

## How It Works
On first use, the tool downloads the Instructor embedding model. Similarity is computed by embedding the search term and commit messages into vectors, and taking the cosine distance between them.
By default, the tool caches the embeddings of commit messages for faster subsequent search.

## Installation
Clone and run locally
```bash
git clone https://github.com/adrianmfi/git-semantic-similarity.git
cd git-semantic-similarity
pip install .
```

## Usage
In a git repository, run:
`git-semsim "text to calculate similarity to"`

The tool supports any argument to git rev-list for narrowing results (e.g. filter by author, num resulst)
For example, to only search the most recent 50 commits by author Bob, where the commit message must contain "service":

Example
```bash
git-semsim "refactoring the user service" -n 50 --author Bob --grep service
```

To get the 50 most relevant commits:
```bash
git-semsim "refactoring the user service" | sort -n -r | head -n 50
```

## License

MIT
