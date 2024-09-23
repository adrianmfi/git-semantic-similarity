# git-semantic-similarity

## Summary:
git-semantic-similarity is a command-line tool for finding git commits by semantic search

## Examples

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

To get the 50 most relevant commits:
```bash
git-semsim "refactoring the user service" | sort -n -r | head -n 50
```

The tool supports forwarding arguments to git rev-list (e.g. filter by author, num results)
For example, to only search the most recent commits for a specific author:

Example
```bash
git-semsim "refactoring the user service" -- -n 50 --author Bob
```

## License

MIT
