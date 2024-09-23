# git-semantic-similarity

## Summary:
git-semantic-similarity is a command-line tool for finding git commits by semantic search

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

To get the 10 most relevant commits:
```bash
git-semsim "refactoring the user service" -n 10
```

The tool supports forwarding arguments to `git rev-list` (e.g. filter by author, num results)
For example, to only search in the 10 most recent commits:

Example
```bash
git-semsim "refactoring the user service" --sort false -- -n 10
```

Or to filter by a specific author:
```
git-semsim "refactoring the user service" -- --author bob
```

Or you can format the output in a single line for further shell processing:
```bash
git-semsim "refactoring the user service" --sort False --oneline | sort -n -r | head -n 10
``` 

## License

MIT
