# spam_test
Test the spam probability of an email based on idempotent rules (no learning).

`spam_test` expect email input via stdin and outputs the spam score on the standard output.

Created to be used with [FDM](https://github.com/nicm/fdm) in a `pipe` action.

## Rules and scores

There are currently 3 sets of rules, each one is able to increment the spam score by 1.

### Subject and From

If the subject is missing, empty or contains less than half ASCII characters, the spam score is incremented by 1.

If the From name part is not empty but contains less than half ASCII characters, the spam score is incremented by 1.

### Recipient count

If there is no recipients or more than 9, the spam score is incremented by 1.

### X-Spam-Status

If the messages has already been flagged as spam, the spam score is incremented by 1.

## Performance note
In a quest for performance, I compared Python 3 and Python 2 versions of the code. Python 2.7 appeared to be 20% to 30% quicker than Python 3.4 in Debian stable 8.7 for a sample of 200 randomly contact@ emails of a small french software company. So I kept using Python 2 and made a cross-compatible version.

Cython compilation was 2 times slower in this edge case.

`-O` and `-OO` python's options are slowing down the computation by 3.

## Example

### `spam_test` `fdm.conf` example :

```
match pipe "python -SE spam_test.py" returns (,'^([0-9]+)$') action tag "spam_score" value "%[command0]" continue
match string "%[spam_score]" to "1" action maildir "%h/.Maildir/.spam"
match string "%[spam_score]" to "[2-9]" action maildir "%h/.Maildir/.furspam"
```


## Tests

To run the embeded testsuite :
```shell
python2 -m doctest spam_test.py
python3 -m doctest spam_test.py
```
