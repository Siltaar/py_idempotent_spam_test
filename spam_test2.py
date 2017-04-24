#!/usr/bin/python2
# coding: utf-8
# author : Simon Descarpentries, 2017-03
# licence: GPLv3

from __future__ import print_function
from io import TextIOWrapper
from sys import stdin #, stderr
from email.parser import Parser
from email.header import decode_header as decode_h
from email.header import make_header as make_h
from email.utils import getaddresses


def spam_test(stdin_eml):
	"""
		>>> spam_test('To:a@a.tk\\nSubject: "Normal" email should pass')
		0
		>>> spam_test('To:\\nSubject: Missing recipient should be scored 1')
		1
		>>> spam_test('To:a@a.tk, b@b.tk, c@c.tk, d@d.tk, e@e.tk, f@f.tk, g@g.tk,\
			h@h.tk, i@i.tk, j@j.tk\\nSubject: More than 9 recipients, scored 1')
		1
		>>> spam_test('To:a@a.tk\\nSubject: Not half ASCII =?utf-8?b?w6nDqcOpw\
6nDqcOpw6nDqcOpw6nDqcOpw6nDqcOpw6nDqcOpw6nDqcOpw6k=?=\\n =?utf-8?b?w6nDqcOpw6n\
DqcOpw6nDqQ==?=')
		1
		>>> spam_test('To:No subject scored 1 <a@a.tk>')
		1
		>>> spam_test('Subject: no To no ASCII scored 2=?utf-8?b?w6nDqcOpw6nD\
qcOpw6nDqcOpw6nDqcOpw6nDqcOpw6nDqcOpw6nDqcOpw6k=?=\\n =?utf-8?b?w6nDqcOpw6nDqc\
Opw6nDqcOpw6nDqcOpw6nDqcOpw6nDqcOpw6nDqcOpw6k=?=\\n =?utf-8?b?w6nDqcOpw6k=?=')
		2
		>>> spam_test('Subject: =?gb2312?B?vNLT0NChxau499bW1sa3/sC009W78w==?=')
		2
		>>> spam_test('Subject: Encoding érror')
		2
	"""
	eml = Parser().parsestr(stdin_eml, headersonly=True)  # Parse header of stdin piped email
	score = 0

	try:
		refined_subject = unicode(make_h(decode_h(eml.get('Subject', ''))))
	except:
		refined_subject = ''

	ascii_length = len(refined_subject.encode('ascii', 'ignore'))

	if ascii_length == 0 or len(refined_subject) / ascii_length > 2:
		score += 1  # If not 1 ascii letter over 2 in the subject, I don't want to read it

	recipient_count = len(getaddresses(eml.get_all('to', []) + eml.get_all('cc', [])))

	if recipient_count == 0 or recipient_count > 9:
		score += 1  # If there is no or more than 20 recipients, it may be a spam

	# print(eml, file=stderr)
	# print('%s score %i ascii %i To: %i' % (
	#	refined_subject, score, ascii_length, recipient_count), file=stderr)
	print(str(score), end='')


if __name__ == "__main__":
	spam_test(stdin.read())
