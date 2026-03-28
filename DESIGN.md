## Subcommands

### `git-link check`

Checks whether currently staged files make edits to linked segments. Intended to be called from a git pre-commit hook. Exits non-zero to block the commit if linked segments have diverged without acknowledgement.

### `git-link accept <comment>`

Accepts an issue highlighted by `check`, with an associated reason recorded as `<comment>`. Allows the commit to proceed despite the divergence.

---

## Comments

There are several types of comments that are used as markers for git-link:

## Many-to-many

The default `git-link`: bind every link to every other link of the same name.

Useful for linking together constant values in a polyglot environment.

```python
# git-link <num_lines> <link_name>
```

```c
// git-link <num_lines> <link_name>

/* git-link <num_lines> <link_name> */
```

Where:
 * `link_name` is simply a name that all the comments can refer to
 * `num_lines` is the number of lines following the comment that should be
    considered part of the linked material


## Many-to-one

What would a use-case be?

## One-to-many

Changing the many doesn't invoke, but changing the one does?
What would the use-case be?