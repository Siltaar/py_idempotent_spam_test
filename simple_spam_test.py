#!/usr/bin/python2
# coding: utf-8
# author : Simon Descarpentries, 2017-03
# licence: GPLv3

from __future__ import print_function
from sys import stdin, stderr, version_info
from email.parser import Parser
from email.header import decode_header
from email.header import make_header
from email.utils import getaddresses, parseaddr, parsedate_tz, mktime_tz, formatdate  # noqa
from curses.ascii import isalnum
from datetime import datetime, timedelta
from calendar import timegm  # noqa


def spam_test(stdin_eml, debug=0):
	eml = Parser().parsestr(stdin_eml)
	score = 0
	debug and print("-> %s " % eml.get('Subject', ''), end='', file=stderr)
	subj_len, subj_alpha_len = header_alpha_len(eml.get('Subject', ''))

	if subj_alpha_len == 0 or subj_len // subj_alpha_len > 1:
		score += 1  # If no more than 1 ascii char over 2 in subject, I can't read it
		debug and print("subj %i/%i " % (subj_alpha_len, subj_len), end='', file=stderr)

	body=''

	for a in eml.walk() :
		if 'text' in a.get_content_type():
			# debug and print('ctype %s ' % a.get_content_type(), end='', file=stderr)
			body = a.get_payload(decode=True)[:256]
			break;

	body_len, body_alpha_len = alpha_len(body)

	if body_alpha_len == 0 or body_len // body_alpha_len > 1:
		score += 1
		debug and print("body %i/%i " % (body_alpha_len, body_len), end='', file=stderr)

	if score > 0:
		from_len, from_alpha_len = header_alpha_len(parseaddr(eml.get('From', ''))[0])

		if from_len > 0 and (from_alpha_len == 0 or from_len // from_alpha_len > 1):
			score += 1
			debug and print("from %i/%i " % (from_alpha_len, from_len), end='', file=stderr)

	recipient_count = len(getaddresses(eml.get_all('To', []) + eml.get_all('Cc', [])))

	if recipient_count == 0 or recipient_count > 9:
		score += 1  # If there is no or more than 9 recipients, it may be a spam
		debug and print("dests %i " % (recipient_count), end='', file=stderr)

	recv_dt = datetime.utcfromtimestamp(mktime_tz(parsedate_tz(
		eml.get('Received', 'Sat, 01 Jan 9999 01:01:01 +0000')[-30:])))
	eml_dt = datetime.utcfromtimestamp(mktime_tz(parsedate_tz(
		eml.get('Date', 'Sat, 01 Jan 0001 01:01:01 +0000'))))

	if eml_dt < recv_dt - timedelta(hours=6) or eml_dt > recv_dt + timedelta(hours=2):
		debug and print("near date %s recv %s " % (eml_dt, recv_dt), end='', file=stderr)
		score += 1

		if eml_dt < recv_dt - timedelta(days=15) or \
			eml_dt > recv_dt + timedelta(days=2):
			debug and print("far date ", end='', file=stderr)
			score += 1

	if (eml.get('X-Spam-Status', '').lower() == 'yes' or
		eml.get('X-Spam-Flag', '').lower() == 'yes' or
		len(eml.get('X-Spam-Level', '')) > 3):
		score += 1

	debug and print('score %s\n' % score, end='', file=stderr)
	print(str(score))


DEBUG=1
def test_spam_test(stdin_eml):
	"""
	>>> spam_test('From:Bb<b@b.tk>\\nTo:a@a.tk\\nSubject:eml ok\\nContent-Type: text/plain;\\n'
	... 'Date:Wed, 26 Apr 2017 16:20:14 +0200\\nReceived:Wed, 26 Apr 2017 16:21:14 +0200\\n'
	... 'Coucou\\n', DEBUG)
	0
	>>> spam_test('To:\\nSubject: Missing recipient should be scored 1\\n'
	... 'Date:Wed, 26 Apr 2017 16:20:14 +0200\\nReceived:Wed, 26 Apr 2017 16:21:14 +0200',DEBUG)
	2
	>>> spam_test('Subject: No recp, 1 non-alpha =?utf-8?b?w6k=?= scored 1\\n'
	... 'Date:Wed, 26 Apr 2017 16:20:14 +0200\\nReceived:Wed, 26 Apr 2017 16:21:14 +0200',DEBUG)
	2
	>>> spam_test('Subject: Enough ASCII letters should be score 1 =?gb231'
	... '2?B?vNLT0NChxau499bW1sa3/sC009W78w==?=\\n'
	... 'Date:Wed, 26 Apr 2017 16:20:14 +0200\\nReceived:Wed, 26 Apr 2017 16:21:14 +0200',DEBUG)
	2
	>>> spam_test('To:a@a.tk,b@b.tk,c@c.tk,d@d.tk,e@e.tk,f@f.tk,g@g.tk,'
	...	'h@h.tk,i@i.tk,j@j.tk\\nSubject: More than 9 recipients, scored 1\\n'
	... 'Date:Wed, 26 Apr 2017 16:20:14 +0200\\nReceived:Wed, 26 Apr 2017 16:21:14 +0200',DEBUG)
	2
	>>> spam_test('To:a@a.tk\\nSubject:Not 1/2 ASCII =?utf-8?b?w6nDqcOpw6nDqcOpw6nD=?=\\n'
	... 'Date:Wed, 26 Apr 2017 16:20:14 +0200\\nReceived:Wed, 26 Apr 2017 16:21:14 +0200',DEBUG)
	2
	>>> spam_test('To:No subject scored 1 <a@a.tk>\\n'
	... 'Date:Wed, 26 Apr 2017 16:20:14 +0200\\nReceived:Wed, 26 Apr 2017 16:21:14 +0200',DEBUG)
	2
	>>> spam_test('Subject: no To no ASCII scored 2=?utf-8?b?w6nDqcOpw6nD'
	...	'qcOpw6nDqcOpw6nDqcOpw6nDqcOpw6nDqcOpw6nDqcOpw6k=?=\\n'
	... 'Date:Wed, 26 Apr 2017 16:20:14 +0200\\nReceived:Wed, 26 Apr 2017 16:21:14 +0200',DEBUG)
	3
	>>> spam_test('Subject: =?gb2312?B?vNLT0NChxau499bW1sa3/sC009W78w==?=\\n'
	... 'Date:Wed, 26 Apr 2017 16:20:14 +0200\\nReceived:Wed, 26 Apr 2017 16:21:14 +0200',DEBUG)
	3
	>>> spam_test('Subject: =?gb2312?B?Encoding error score 2 代 =?=\\n'
	... 'Date:Wed, 26 Apr 2017 16:20:14 +0200\\nReceived:Wed, 26 Apr 2017 16:21:14 +0200',DEBUG)
	3
	>>> spam_test('Subject: Near past +6 h \\nDate: Wed, 26 Apr 2017 16:20:14 +0200\\n'
	... 'Received:Wed, 26 Apr 2017 22:21:14 +0200', DEBUG)
	3
	>>> spam_test('Subject: Near futur -2 h\\nDate: Wed, 26 Apr 2017 16:20:14 +0200\\n'
	... 'Received:Wed, 26 Apr 2017 14:19:14 +0200', DEBUG)
	3
	>>> spam_test('Subject: Far past +15 d \\nDate: Tue, 11 Apr 2017 16:20:14 +0200\\n'
	... 'Received:Wed, 26 Apr 2016 14:21:14 +0200', DEBUG)
	4
	>>> spam_test('Subject: Far futur -2 d \\nDate: Wed, 26 Apr 2017 16:20:14 +0200\\n'
	... 'Received:Mon, 24 Apr 2016 16:19:14 +0200', DEBUG)
	4
	>>> spam_test('From: =?utf-8?b?5Luj?= <a@a.tk>\\nDate: Wed, 26 Apr '
	... '2017 16:20:14 +0200\\nReceived:Wed, 26 Apr 2017 16:25:14 +0200', DEBUG)
	4
	>>> spam_test('X-Spam-Status: Yes', DEBUG)
	6
	>>> spam_test('X-Spam-Level: ****', DEBUG)
	6
	>>> spam_test(open('test_email/20171010.eml').read(), DEBUG)  # chinese content
	2
	>>> spam_test(open('test_email/20171012.eml').read(), DEBUG)  # no text nor HTML part
	2
	>>> spam_test(open('test_email/20171107.eml').read(), DEBUG)  # longer chinese content
	2
	"""
	return spam_test(stdin_eml)


def header_alpha_len(h):
	try:
		refined_h = unicode(make_header(decode_header(h)))
	except Exception as e:
		print(str(e) + '\n', file=stderr)
		refined_h = ''
	return alpha_len(refined_h)


def alpha_len(s):
	if type(s) is not unicode:
		s = unicode(s, errors='ignore')
	s_len = len(s)
	ascii_s = s.encode('ascii', errors='ignore')
	s_alpha_len = len([c for c in ascii_s if isalnum(c)])
	return s_len, s_alpha_len


if version_info.major > 2:  # In Python 3: str is the new unicode
	unicode = str

if __name__ == "__main__":
	if version_info.major > 2:
		from io import TextIOWrapper
		spam_test(TextIOWrapper(stdin.buffer, errors='ignore').read())
	else:
		spam_test(stdin.read())
