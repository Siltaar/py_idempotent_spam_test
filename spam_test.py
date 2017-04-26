#!/usr/bin/python2
# coding: utf-8
# author : Simon Descarpentries, 2017-03
# licence: GPLv3

from __future__ import print_function
from sys import stdin, version_info
# from sys import stderr
from email.parser import Parser
from email.header import decode_header
from email.header import make_header
from email.utils import getaddresses, parseaddr
from curses.ascii import isalpha


def spam_test(stdin_eml):
	"""
		>>> spam_test('From:Bb<b@b.tk>\\nTo:a@a.tk\\nSubject:"Normal" eml ok')
		0
		>>> spam_test('To:\\nSubject: Missing recipient should be scored 1')
		1
		>>> spam_test('Subject: No recp, 1 non-alpha =?utf-8?b?w6k=?= scored 1')
		1
		>>> spam_test('Subject: Enough ASCII letters should be score 1 =?gb231'
		... '2?B?vNLT0NChxau499bW1sa3/sC009W78w==?=')
		1
		>>> spam_test('To:a@a.tk,b@b.tk,c@c.tk,d@d.tk,e@e.tk,f@f.tk,g@g.tk,'
		...	'h@h.tk,i@i.tk,j@j.tk\\nSubject: More than 9 recipients, scored 1')
		1
		>>> spam_test('To:a@a.tk\\nSubject: Not half ASCII =?utf-8?b?w6nDqcOpw'
		...	'6nDqcOpw6nDqcOpw6k=?=')
		1
		>>> spam_test('To:No subject scored 1 <a@a.tk>')
		1
		>>> spam_test('Subject: no To no ASCII scored 2=?utf-8?b?w6nDqcOpw6nD'
		...	'qcOpw6nDqcOpw6nDqcOpw6nDqcOpw6nDqcOpw6nDqcOpw6k=?=')
		2
		>>> spam_test('Subject: =?gb2312?B?vNLT0NChxau499bW1sa3/sC009W78w==?=')
		2
		>>> spam_test('Subject: =?gb2312?B?Encoding error 代 ?=')
		2
		>>> spam_test('X-Spam-Status: Yes')
		3
		>>> spam_test('From: =?utf-8?b?5Luj?= <a@a.tk>')
		3
	"""
	eml = Parser().parsestr(stdin_eml, headersonly=True)  # Parse header of stdin piped email
	score = 0

	if eml.get('X-Spam-Status', '').lower() == 'yes' or \
		eml.get('X-Spam-Flag', '').lower() == 'yes':
		score += 1  # if already flagged as spam, we should get cautious

	subj_len, subj_alpha_len = header_alpha_length(eml.get('Subject', ''))

	if subj_alpha_len == 0 or subj_len // subj_alpha_len > 1:
		score += 1  # If no more than 1 ascii char over 2 in subject, I can't read it

	recipient_count = len(getaddresses(eml.get_all('To', []) + eml.get_all('Cc', [])))

	if recipient_count == 0 or recipient_count > 9:
		score += 1  # If there is no or more than 9 recipients, it may be a spam

	from_len, from_alpha_len = header_alpha_length(parseaddr(eml.get('From', ''))[0])

	if from_len > 0 and (from_alpha_len == 0 or from_len // from_alpha_len > 1):
		score += 1  # If no more than 1 ascii char over 2 in from name, I can't read it

	# print('score %i alpha %i To: %i alpha_To %i' % (
	# 	score, subj_alpha_len, recipient_count, from_alpha_len), file=stderr)
	print(str(score), end='')


def header_alpha_length(h):
	try:
		refined_h = unicode(make_header(decode_header(h)))
	except:
		# print(e, file=stderr)
		refined_h = ''

	# print(refined_h, end=' ', file=stderr)
	h_len = len(refined_h)
	ascii_h = refined_h.encode('ascii', 'ignore')
	h_alpha_len = len([c for c in ascii_h if isalpha(c)])
	return h_len, h_alpha_len


try:
	a = type(unicode)  # If unicode is missing we're in Python 3, should fix this
except:
	globals()['unicode'] = lambda s: str(s)

if __name__ == "__main__":
	if version_info.major > 2:
		from io import TextIOWrapper
		spam_test(TextIOWrapper(stdin.buffer, errors='ignore').read())
	else:
		spam_test(stdin.read())
