#!/usr/bin/env python2
# coding: utf-8
# author : Simon Descarpentries, 2017-10
# licence: GPLv3

from doctest import run_docstring_examples
from datetime import datetime
from simple_spam_test import test_spam_test, spam_test

"""
20171012 3 : 17 tests ; 0.62s ; 0.364ms/t
20171012 2 : 19 tests ; 0.71s ; 0.373ms/t (added 2 real cases)
20171012 3 : 19 tests ; 0.81s ; 0.426ms/t
20171012 2 : 19 tests ; 0.80s ; 0.421ms/t (parse all mail)
20171012 3 : 19 tests ; 0.90s ; 0.473ms/t
20171012 2 : 19 tests ; 0.86s ; 0.452ms/t (check body readability)
20171012 3 : 19 tests ; 0.99s ; 0.521ms/t
"""

startTime = datetime.now()
DEBUG = 0

for i in range(0, 100):
	run_docstring_examples(test_spam_test, globals())

print(datetime.now() - startTime)
