# git-semantic-similarity

Search git commit messages by semantic similarity with embeddings from [sentence-transformers](https://github.com/UKPLab/sentence-transformers).

Embeddings are stored on disk for faster retrieval, and can easily be checked into git.


```
$ gitsem "project scaffolding"

Commit 403836d2ee4900579b0d1e8169dd4bfebddab0ba
Author: Foo Bar <foo@barcom>
Date:   2024-09-23 19:08:05
Similarity: 0.2299

    Change model, add src folder

Commit d2909a8ec352a881ab05cab8b8a67038b063f37a
Author: Foo Bar <foo@barcom>
Date:   2024-09-23 19:08:05
Similarity: 0.2086

    Initial commit

...

Commit a09923166072aca4910e92272ef161e3398b1d89
Author: Foo Bar <foo@barcom>
Date:   2024-09-23 19:08:05
Similarity: -0.0716

    Remove buggy rounding
```

## Installation
First, install [pipx](https://github.com/pypa/pipx).
Then, install with pipx:
```bash
pipx install git-semantic-similarity
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
  Batch size for embedding commits. Default is `100`.

- `query [STRING]`:  
  The query string to compare against commit messages.

- `git_args [STRING...]`:  
  Arguments after `--` will be forwarded to `git rev-list`.


## License

MIT
