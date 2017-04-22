# spam_test and spam_test_rewrite
Test the spam probability of an email based on idempotent rules (no learning).

Both expect email input via stdin.
`spam_test.py` outputs the score on the standard output.
`spam_test_rewrite.py` rewrites the email to stdout adding an `X-Spam-Score` header.

Created to be used with [FDM](https://github.com/nicm/fdm) in a `pipe` or `rewrite` action.

## Rules and scores

There are currently 2 sets of rules, each one is able to increment the spam score by 1.

### Subject

If the subject is missing, empty or contains less than half alphabetical letters, the spam score is incremented by 1.

### Recipient count

If there is no recipient or more than 9, the spam score is incremented by 1.

## Performance note
In a quest for performance, I compared Python 3 and Python 2 versions of the code. Python 2.7 appeared to be 20% to 30% quicker than Python 3.4 in Debian stable 8.7 for a sample of 80 randomly contact@ emails of a small french software company. So I kept the Python 2 version.

The Python 3 version is also provided.

Cython compilation was 50% slower in this edge case.

`spam_test.py` is 50% quicker than `spam_test_rewrite` and works with both Python 2.7 and 3.x.

## Example

### `spam_test` `fdm.conf` example :

`match pipe "python spam_test.py" returns (,'^([0-9]+)$') action tag "%[command0]" continue`

`match tagged "1" action maildir "%h/.Maildir/.spam"`

`match tagged "2" action maildir "%h/.Maildir/.furspam"`


### `spam_test_rewrite` `fdm.conf` example :

`match all action rewrite "python2 -SE spam_test_rewrite2.py" continue`

`match "^X-Spam-Score: 1$" in headers action maildir "%h/.Maildir/.spam"`

`match "^X-Spam-Score: [2-9]$" in headers action maildir "%h/.Maildir/.furspam"`

## Tests

To run the embeded testsuite :
`python2 -m doctest spam_test_rewrite2.py`

`python3 -m doctest spam_test_rewrite3.py`

`python -m doctest spam_test.py` (works with both Python 2.7 and 3.x)
