#!/usr/bin/env python2
# coding: utf-8
# author : Simon Descarpentries
# date: 2017 - 2018
# licence: GPLv3

from doctest import run_docstring_examples
from simple_spam_test import spam_test


DEBUG = 1


def test_spam_test_theoritical_cases(stdin_eml):
	"""
	>>> spam_test('From:Bb<b@b.tk>\\nTo:a@a.tk\\nSubject:eml ok\\nContent-Type: text/plain;\\n'
	... 'Date:Wed, 26 Apr 2017 16:20:14 +0200\\nReceived:Wed, 26 Apr 2017 16:21:14 +0200\\n'
	... 'Coucou, il nous faut un grand texte ici désormais et on devrait y arriver !', DEBUG)
	0
	>>> spam_test('To:\\nSubject: Missing recipient should be scored 2\\n'
	... 'Date:Wed, 26 Apr 2017 16:20:14 +0200\\nReceived:Wed, 26 Apr 2017 16:21:14 +0200',DEBUG)
	2
	>>> spam_test('Subject: No recp, 1 non-alpha =?utf-8?b?w6k=?= scored 2\\n'
	... 'Date:Wed, 26 Apr 2017 16:20:14 +0200\\nReceived:Wed, 26 Apr 2017 16:21:14 +0200',DEBUG)
	2
	>>> spam_test('Subject: Enough ASCII should be 2 =?gb2312?B?vNLT0NChxau499bW1sa3/sC0==?=\\n'
	... 'Date:Wed, 26 Apr 2017 16:20:14 +0200\\nReceived:Wed, 26 Apr 2017 16:21:14 +0200',DEBUG)
	2
	>>> spam_test('To:a@a.tk\\nSubject:Not / ASCII =?utf-8?b?w6nDqcOpw6nDqcOpw6nDqcOpw6n=?=\\n'
	... 'Date:Wed, 26 Apr 2017 16:20:14 +0200\\nReceived:Wed, 26 Apr 2017 16:21:14 +0200',DEBUG)
	3
	>>> spam_test('To:No subject scored 2 <a@a.tk>\\n'
	... 'Date:Wed, 26 Apr 2017 16:20:14 +0200\\nReceived:Wed, 26 Apr 2017 16:21:14 +0200',DEBUG)
	3
	>>> spam_test('Subject:no To no ASCII =?utf-8?b?w6nDqcOpw6nDqcOpw6nDqcOpw6nDqcOpw6n=?=\\n'
	... 'Date:Wed, 26 Apr 2017 16:20:14 +0200\\nReceived:Wed, 26 Apr 2017 16:21:14 +0200',DEBUG)
	3
	>>> spam_test('Subject: =?gb2312?B?vNLT0NChxau499bW1sa3/sC009W78w==?=\\n'
	... 'Date:Wed, 26 Apr 2017 16:20:14 +0200\\nReceived:Wed, 26 Apr 2017 16:21:14 +0200',DEBUG)
	3
	>>> spam_test('Subject: =?gb2312?B?Encoding error score 2 代 =?=\\n'
	... 'Date:Wed, 26 Apr 2017 16:20:14 +0200\\nReceived:Wed, 26 Apr 2017 16:21:14 +0200',DEBUG)
	3
	>>> spam_test('Subject: Near past +1 d \\nDate: Wed, 26 Apr 2017 16:20:14 +0200\\n'
	... 'Received:Wed, 27 Apr 2017 22:21:14 +0200', DEBUG)
	3
	>>> spam_test('Subject: Near futur -2 h\\nDate: Wed, 26 Apr 2017 16:20:14 +0200\\n'
	... 'Received:Wed, 26 Apr 2017 14:19:14 +0200', DEBUG)
	3
	>>> spam_test('Subject: Far past +15 d \\nDate: Tue, 10 Apr 2017 16:20:14 +0200\\n'
	... 'Received:Wed, 26 Apr 2017 14:21:14 +0200', DEBUG)
	4
	>>> spam_test('Subject: Far futur -2 d \\nDate: Wed, 26 Apr 2017 16:20:14 +0200\\n'
	... 'Received:Mon, 24 Apr 2017 16:19:14 +0200', DEBUG)
	4
	>>> spam_test('From: =?utf-8?b?5Luj?= <a@a.tk>\\nDate: Wed, 26 Apr '
	... '2017 16:20:14 +0200\\nReceived:Wed, 26 Apr 2017 16:25:14 +0200', DEBUG)
	4
	>>> spam_test('X-Spam-Status: Yes', DEBUG)
	6
	>>> spam_test('X-Spam-Level: ****', DEBUG)
	6
	"""
	# >>> spam_test('To:a@a.tk,b@b.tk,c@c.tk,d@d.tk,e@e.tk,f@f.tk,g@g.tk,'
	# ... 'h@h.tk,i@i.tk,j@j.tk\\nSubject: More than 9 recipients, scored 2\\n'
	#...'Date:Wed, 26 Apr 2017 16:20:14 +0200\\nReceived:Wed, 26 Apr 2017 16:21:14 +0200',DEBUG)
	# 3
	return spam_test(stdin_eml)


def test_spam_test_real_cases(stdin_eml):
	"""
	>>> spam_test(open('email_test/20171010.eml').read(), DEBUG)  # chinese content
	3
	>>> spam_test(open('email_test/20171012.eml').read(), DEBUG)  # no text nor HTML part
	3
	>>> spam_test(open('email_test/20171107.eml').read(), DEBUG)  # longer chinese content
	3
	>>> spam_test(open('email_test/20171130.eml').read(), DEBUG)  # PGP ciphered email
	0
	>>> spam_test(open('email_test/20171219.eml').read(), DEBUG)  # chinese base64 body
	2
	>>> spam_test(open('email_test/20180130.eml').read(), DEBUG)  # no text, bad HTML
	2
	>>> spam_test(open('email_test/20180321.eml').read(), DEBUG)  # small body chinese Subj, To:
	2
	>>> spam_test(open('email_test/20180322.eml').read(), DEBUG)  # valid big HTML body only
	2
	>>> spam_test(open('email_test/20180326.eml').read(), DEBUG)  # small text 0 alpha length
	2
	>>> spam_test(open('email_test/20180328.eml').read(), DEBUG)  # Mozilla AsciiArt deco
	0
	>>> spam_test(open('email_test/20180429.eml').read(), DEBUG)  # Trop de liens, même URL
	1
	>>> spam_test(open('email_test/20180523.eml').read(), DEBUG)  # Limite sur nombre de liens
	0
	"""
	return spam_test(stdin_eml)


if __name__ == "__main__":
	run_docstring_examples(test_spam_test_theoritical_cases, globals())
	run_docstring_examples(test_spam_test_real_cases, globals())
