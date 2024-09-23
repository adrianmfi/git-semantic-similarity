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
`gitsem "query string"`

To only show the 10 most relevant commits:
```bash
gitsem "changes to project documentation" -n 10
```

To use another pretrained model, for example a smaller and faster model:
```bash
gitsem "user service refactoring" --model sentence-transformers/all-MiniLM-L6-v2
```
A list of supported models [can be found here](https://www.sbert.net/docs/sentence_transformer/pretrained_models.html)

The tool supports forwarding arguments to `git rev-list`
For example, to only search in the 10 most recent commits:

```bash
gitsem "query string" -- -n 10
```

Or to filter by a specific author:
```
gitsem "query string" -- --author bob
```

Or you can format the output in a single line for further shell processing:
```bash
gitsem "query string" --sort False --oneline -- n 100 | sort -n -r | head -n 10
``` 

## Arguments

- `-m, --model [STRING]`:  
  A sentence-transformers model to use for embeddings. Default is `all-mpnet-base-v2`.

- `-c, --cache [BOOLEAN]`:  
  Whether to cache commit embeddings on disk for faster retrieval. Default is `True`.

- `--cache-dir [PATH]`:  
  Directory to store cached embeddings. If not specified, defaults to `git_root/.git_semsim/model_name`.

- `--oneline`:  
  Use a concise output format.

- `--sort [BOOLEAN]`:  
  Sort results by similarity score. Default is `True`.

- `-n, --max-count [INTEGER]`:  
  Limit the number of results displayed. If not provided, no limit is applied.

- `-b, --batch-size [INTEGER]`:  
  Batch size for embedding commits. Default is `1000`.

- `query [STRING]`:  
  The query string to compare against commit messages.

- `git_args [STRING...]`:  
  Arguments after `--` will be forwarded to `git rev-list`.


## License

MIT
