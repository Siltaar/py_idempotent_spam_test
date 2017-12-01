#!/usr/bin/env python2
# coding: utf-8
# author : Simon Descarpentries, 2017-10
# licence: GPLv3

from doctest import run_docstring_examples
from datetime import datetime
from simple_spam_test import test_spam_test, spam_test

"""
Debian 8.9
Python 2.7.9
Python 3.4.2

20171012 3 : 17 tests ; 0.62s ; 0.364ms/t
20171012 2 : 19 tests ; 0.71s ; 0.373ms/t (added 2 real cases)
20171012 3 : 19 tests ; 0.81s ; 0.426ms/t
20171012 2 : 19 tests ; 0.80s ; 0.421ms/t (parse all mail)
20171012 3 : 19 tests ; 0.90s ; 0.473ms/t
20171012 2 : 19 tests ; 0.86s ; 0.452ms/t (check body readability)
20171012 3 : 19 tests ; 0.99s ; 0.521ms/t
20171124 2 : 20 tests ; 1.06s ; 0.530ms/t (check alnum characters)
20171124 3 : 20 tests ; 1.20s ; 0.600ms/t
20171201 2 : 21 tests ; 1,15s ; 0.547ms/t (accept pgp-encrypted stream as valid)
20171201 3 : 21 tests ; 1,33s ; 0.630ms/t
"""

startTime = datetime.now()
DEBUG = 0

for i in range(0, 100):
	run_docstring_examples(test_spam_test, globals())

print(datetime.now() - startTime)
