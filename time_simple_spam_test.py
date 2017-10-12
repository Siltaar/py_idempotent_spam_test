import doctest
from simple_spam_test import spam_test

"""
20171012 3 : 17 tests ; 0.62s ; 0.364ms/t
20171012 2 : 19 tests ; 0.71s ; 0.373ms/t (added 2 real cases)
20171012 3 : 19 tests ; 0.81s ; 0.426ms/t
20171012 2 : 19 tests ; 0.80s ; 0.421ms/t (parse all mail)
20171012 3 : 19 tests ; 0.90s ; 0.473ms/t
20171012 2 : 19 tests ; 0.86s ; 0.452ms/t (check body readability)
20171012 3 : 19 tests ; 0.99s ; 0.521ms/t
"""

from datetime import datetime
startTime = datetime.now()

for i in range(0,100):
	doctest.run_docstring_examples(spam_test, globals())

print(datetime.now() - startTime)
