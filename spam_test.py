#!/usr/bin/python
# coding: utf-8
# author : Simon Descarpentries, 2017-03
# licence: GPLv3

from __future__ import print_function
from io import TextIOWrapper
from sys import stdin, version_info
# from sys import stderr
from email.parser import Parser
from email.header import decode_header as decode_h
from email.header import make_header as make_h
from email.utils import getaddresses
from curses.ascii import isalpha


def spam_test(stdin_eml):
	"""
		>>> spam_test('To:a@a.tk\\nSubject: "Normal" email should pass')
		0

		>>> spam_test('To:\\nSubject: Missing recipient should be scored 1')
		1

		>>> spam_test('To:a@a.tk, b@b.tk, c@c.tk, d@d.tk, e@e.tk, f@f.tk, g@g.tk, \
			h@h.tk, i@i.tk, j@j.tk\\nSubject: More than 9 recipients, scored 1')
		1

		>>> spam_test('To:a@a.tk\\nSubject: Not a half letters ..............................')
		1

		>>> spam_test('To:a@a.tk\\n')
		1

		>>> spam_test('To:\\nSubject: 2 conditions scored 2 ..............................')
		2
	"""
	eml = Parser().parsestr(stdin_eml, headersonly=True)  # Parse header of stdin piped email
	score = 0

	try:
		refined_subject = make_h(decode_h(eml.get('Subject', ''))).encode('utf8')
	except:  # Encoding exception ? Might be spam, and we can't continue
		refined_subject = ''

	alpha_length = len([c for c in refined_subject if isalpha(c)])

	if alpha_length == 0 or len(refined_subject) / alpha_length > 2:
		score += 1  # If not 1 ascii letter over 2 in the subject, I don't want to read it

	recipient_count = len(getaddresses(eml.get_all('to', []) + eml.get_all('cc', [])))

	if recipient_count > 9 or recipient_count < 1:
		score += 1  # If there is no or more than 20 recipients, it may be a spam

	# print('%s score %i recipients %i' % (refined_subject, score, recipient_count), file=stderr)
	# print(eml, file=stderr)
	print(str(score), end='')


if __name__ == "__main__":
	if version_info.major > 2:
		spam_test(TextIOWrapper(stdin.buffer, errors='ignore', encoding='utf8').read())
	else:
		spam_test(stdin.read())
