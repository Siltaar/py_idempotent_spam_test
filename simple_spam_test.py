#!/usr/bin/env python2
# coding: utf-8
# author : Simon Descarpentries
# date: 2017 - 2018
# licence: GPLv3

from __future__ import print_function
from sys import stdin, stderr, version_info
from email.parser import Parser
from email.header import decode_header
from email.header import make_header
from email.utils import getaddresses, parseaddr, parsedate_tz, mktime_tz
from curses.ascii import isalpha
from datetime import datetime, timedelta


def spam_test(stdin_eml, debug=0):
	eml = Parser().parsestr(stdin_eml)
	score = 0
	debug and print("%s " % eml.get('Subject', ''), end='', file=stderr)

	ctype = ''
	text_parts = []
	html_parts = []

	for part in eml.walk():
		ctype = part.get_content_type()
		# debug and print('ctype %s ' % part.get_content_type(), end='', file=stderr)

		if 'plain' in ctype or 'application/octet-stream' in ctype:
			text_parts.append(part)

		if 'html' in ctype:
			html_parts.append(part)

	for part in html_parts:
		html_src = part.get_payload(decode=True)

		if b'<' not in html_src[:128]:  # looks like malformed HTML
			debug and print("\033[1;33mbad HTML\033[0m ", end='', file=stderr)
			score += 1

		if len(html_src) > 30000:
			debug and print("\033[1;33mbig HTML\033[0m ", end='', file=stderr)
			score += score == 0

	body = ''

	for part in text_parts:
		text = part.get_payload(decode=True)

		if len(body) < len(text):
			body = text

	body_len, body_alpha_len = email_alpha_len(body, lambda b: b[:256])

	if body_alpha_len < 25 and len(html_parts) == 0:  # too small, not so interesting
		score += 1

	if body_alpha_len == 0 or body_len // body_alpha_len > 1:
		score += 1
		debug and print("body %i/%i " % (body_alpha_len, body_len), end='', file=stderr)

	from_len, from_alpha_len = email_alpha_len(parseaddr(eml.get('From', ''))[0], header_txt)

	if from_len > 0 and (from_alpha_len == 0 or from_len // from_alpha_len > 1):
		score += score == 0
		debug and print("from %i/%i " % (from_alpha_len, from_len), end='', file=stderr)

	subj_len, subj_alpha_len = email_alpha_len(eml.get('Subject', ''), header_txt)

	if subj_alpha_len == 0 or subj_len // subj_alpha_len > 1:
		score += 1  # If no more than 1 ascii char over 2 in subject, I can't read it
		debug and print("subj %i/%i " % (subj_alpha_len, subj_len), end='', file=stderr)

	recipient_count = len(getaddresses(eml.get_all('To', []) + eml.get_all('Cc', [])))

	if recipient_count == 0 or recipient_count > 9:
		score += 1  # If there is no or more than 9 recipients, it may be a spam
		debug and print("recs %i " % (recipient_count), end='', file=stderr)

	recv_dt = datetime.utcfromtimestamp(mktime_tz(parsedate_tz(
		eml.get('Received', 'Sat, 01 Jan 9999 01:01:01 +0000')[-30:])))
	eml_dt = datetime.utcfromtimestamp(mktime_tz(parsedate_tz(
		eml.get('Date', 'Sat, 01 Jan 0001 01:01:01 +0000'))))

	if eml_dt < recv_dt - timedelta(hours=6) or eml_dt > recv_dt + timedelta(hours=2):
		debug and print("date %s recv %s " % (eml_dt, recv_dt), end='', file=stderr)
		score += 1

		if eml_dt < recv_dt - timedelta(days=15) or \
			eml_dt > recv_dt + timedelta(days=2):
			debug and print("\033[1;31mfar\033[0m ", end='', file=stderr)
			score += 1
		else:
			debug and print("\033[1;33mnear\033[0m ", end='', file=stderr)

	if (eml.get('X-Spam-Status', '').lower() == 'yes' or
		eml.get('X-Spam-Flag', '').lower() == 'yes' or
		len(eml.get('X-Spam-Level', '')) > 3):
		debug and print("\033[1;33mX-Spam\033[0m ", end='', file=stderr)
		score += 1

	debug and print('\033[1;35m%s\033[0m\n' % score, end='', file=stderr)
	print(str(score))


def email_alpha_len(t, f):
	try:
		refined_t = f(t)
	except Exception as e:
		print(str(e) + '\n', file=stderr)
		refined_t = ''
	return alpha_len(refined_t)


def alpha_len(s):
	s_len = len(s)

	if type(s) is not unicode:
		s = unicode(s, errors='ignore')

	ascii_s = s.encode('ascii', errors='ignore')
	s_alpha_len = len([c for c in ascii_s if isalpha(c)])
	return s_len, s_alpha_len


def header_txt(h):
	return unicode(make_header(decode_header(h)))


if version_info.major > 2:  # In Python 3: str is the new unicode
	unicode = str

if __name__ == "__main__":
	if version_info.major > 2:
		from io import TextIOWrapper
		spam_test(TextIOWrapper(stdin.buffer, errors='ignore').read())
	else:
		spam_test(stdin.read())
