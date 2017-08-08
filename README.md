Test the spam probability of an email based on idempotent rules (no learning). \
`spam_test.py` expect email input via stdin and outputs the spam score on the standard output. \
Created to be used with [FDM](https://github.com/nicm/fdm) in a `pipe` action.

## Rules and scores
There are currently 4 sets of rules, each one is able to increment the spam score by 1.

### Subject and From alphabetic letters
If the subject is missing, empty or contains less than half ASCII alphabetic letters, the spam score is incremented by 1 and the From header name part is tested also, incrementing the score again by 1 in the same conditions.

### Recipient count
If there is no recipients or more than 9, the spam score is incremented by 1.

### Date and time
If the date and time of the Date header of the email is in the future compared to the last Received header, more than 2h (or more than 2 days) the spam score is incremented by 1 (or 2).

If it's more than 6h in the past (or more than 6 days) the spam score is incremented by 1 (or 2).

### X-Spam-Status
If the message has already been flagged as spam, and the spam score is already more than 1, we increment it by 1.

## Performance note
In a quest for performance, I compared Python 3 and Python 2 versions of the code. Python 2.7 appeared to be 20% to 30% quicker than Python 3.4 in Debian stable 8.7 for a sample of 200 randomly contact@ emails of a small french software company. So I kept using Python 2 and made a cross-compatible version.

Cython compilation was 2 times slower in this edge case.

`-O` and `-OO` python's options are slowing down the computation by 3.

## Example
### `fdm.conf` snippet :
```conf
match pipe "python -SE spam_test.py" returns (,'^([0-9]+)$') action tag "spam_score" value "%[command0]" continue
match string "%[spam_score]" to "1" action maildir "%h/.Maildir/.spam"
match string "%[spam_score]" to "[2-9]" action maildir "%h/.Maildir/.furspam"
```

## Testsuite
To run the embeded testsuite : \
`python2 -m doctest spam_test.py` \
`python3 -m doctest spam_test.py`
