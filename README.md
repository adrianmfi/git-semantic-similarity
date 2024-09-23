# git-semantic-similarity

## Summary:
Search git commit messages by semantic similarity with sentence-transformers.

Embeddings are stored on disk for faster retrieval, and can easily be checked into git.

## Installation
Clone and run locally
```bash
git clone https://github.com/adrianmfi/git-semantic-similarity.git
cd git-semantic-similarity
pip install .
```

## Usage
In a git repository, run:
`git-semsim "query string"`

To only show the 10 most relevant commits:
```bash
git-semsim "changes to project documentation" -n 10
```

To use another pretrained model, for example the current best but slower all-mpnet-base-v2 
```bash
git-semsim "user service refactoring" --model all-mpnet-base-v2
```
A list of supported models [can be found here](https://www.sbert.net/docs/sentence_transformer/pretrained_models.html)

The tool supports forwarding arguments to `git rev-list`
For example, to only search in the 10 most recent commits:

```bash
git-semsim "query string" -- -n 10
```

Or to filter by a specific author:
```
git-semsim "query string" -- --author bob
```

Or you can format the output in a single line for further shell processing:
```bash
git-semsim "query string" --sort False --oneline -- n 100 | sort -n -r | head -n 10
``` 

## License

MIT
