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
