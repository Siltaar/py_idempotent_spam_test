# spam_test
Test the spam probability of an email based on idempotent rules (no learning).

`spam_test` expect email input via stdin and outputs the spam score on the standard output.

Created to be used with [FDM](https://github.com/nicm/fdm) in a `pipe` action.

## Rules and scores

There are currently 2 sets of rules, each one is able to increment the spam score by 1.

### Subject

If the subject is missing, empty or contains less than half ASCII characters, the spam score is incremented by 1.

### Recipient count

If there is no recipients or more than 9, the spam score is incremented by 1.

## Performance note
In a quest for performance, I compared Python 3 and Python 2 versions of the code. Python 2.7 appeared to be 20% to 30% quicker than Python 3.4 in Debian stable 8.7 for a sample of 200 randomly contact@ emails of a small french software company. So I kept the Python 2 version.

The Python 3 version is also provided.

Cython compilation was 50% slower in this edge case.

## Example

### `spam_test` `fdm.conf` example :

```match pipe "python2 -SE spam_test2.py" returns (,'^([0-9]+)$') action tag "spam_score_%[command0]" continue
match tagged "spam_score_1" action maildir "%h/.Maildir/.spam"
match tagged "spam_score_2" action maildir "%h/.Maildir/.furspam"```


## Tests

To run the embeded testsuite :
`python2 -m doctest spam_test2.py`
