#!/usr/bin/env python2
# coding: utf-8
# author : Simon Descarpentries
# date: 2017 - 2018
# licence: GPLv3

from __future__ import print_function
from sys import version_info
from email.parser import Parser
from email.header import decode_header, make_header
# from email.utils import getaddresses
from email.utils import parseaddr, parsedate_tz, mktime_tz
from datetime import datetime, timedelta
from curses.ascii import isalpha
from re import compile as compile_re


def spam_test(stdin_eml, debug=0):
	score, eml, log = spam_test_eml_log(stdin_eml, debug)
	return score


def spam_test_eml_log(stdin_eml, debug=0):
	eml = Parser().parsestr(stdin_eml)
	score = 0
	log = ''
	debug and put("%s " % eml.get('Subject', '')[:20].ljust(20))

	ctype = ''
	text_parts = []
	html_parts = []
	same_links = True

	for part in eml.walk():
		ctype = part.get_content_type()
		# debug and put('ctype %s ' % part.get_content_type())

		if 'plain' in ctype or 'application/octet-stream' in ctype:
			text_parts.append(part)

		if 'html' in ctype:
			html_parts.append(part)

	for part in html_parts:
		html_src = part.get_payload(decode=True)

		if b'<' not in html_src[:10]:  # looks like malformed HTML
			debug and put(yel("bad HTML "))
			log += 'bad HTML '
			score += 1

		if len(html_src) > 32000:
			debug and put(yel("big HTML "))
			log += 'big HTML '
			score += score == 0
		elif same_links:
			a = max_same_links(html_src, htm_links_re)

			if a > 4:
				score += 1

				if a > 14:
					score += 1
					debug and put('same HTML ' + red("links") + " %i " % a)
				else:
					debug and put('same HTML ' + yel("links") + " %i " % a)

				log += 'same HTML links %i ' % a
				same_links = False

	body = ''

	for part in text_parts:
		text = part.get_payload(decode=True)

		if len(body) < len(text):
			body = text

	body_len, body_alpha_len = email_alpha_len(body, lambda b: b[:256])
	# debug and put("body %i/%i " % (body_alpha_len, body_len))

	if body_alpha_len < 20 and len(html_parts) == 0:  # too small, not so interesting
		score += 1
		log += 'small body and no HTML '
	elif same_links:
		a = max_same_links(body, txt_links_re)

		if a > 4:
			score += 1

			if a > 14:
				score += 1
				debug and put('same TXT ' + red("links") + " %i " % a)
			else:
				debug and put('same TXT ' + yel("links") + " %i " % a)

			log += 'same TXT links %i ' % a
			same_links = False

	if body_alpha_len == 0 or body_len // body_alpha_len > 1:
		score += 1
		debug and put(yel("body") + " %i/%i " % (body_alpha_len, body_len))
		log += 'bad body '

	subj_len, subj_alpha_len = email_alpha_len(eml.get('Subject', ''), header_str)
	# debug and put("subj %i/%i " % (subj_alpha_len, subj_len))

	if subj_alpha_len == 0 or subj_len // subj_alpha_len > 1:
		score += 1  # If no more than 1 ascii char over 2 in subject, I can't read it
		debug and put(yel("subj") + " %i/%i " % (subj_alpha_len, subj_len))
		log += 'bad subj '

	from_len, from_alpha_len = email_alpha_len(parseaddr(eml.get('From', ''))[0], header_str)

	if from_len > 0 and (from_alpha_len == 0 or from_len // from_alpha_len > 1):
		score += score > 0
		debug and put(yel("from") + " %i/%i " % (from_alpha_len, from_len))
		log += 'bad from '

	# recipient_count = len(getaddresses(eml.get_all('To', []) + eml.get_all('Cc', [])))

	# if recipient_count == 0 or recipient_count > 9:
	# 	score += 1  # If there is no or more than 9 recipients, it may be a spam
	# 	debug and put(yel("recs") + " %i " % (recipient_count))
	# 	log += 'recs %i ' % recipient_count

	recv_dt = datetime.utcfromtimestamp(mktime_tz(parsedate_tz(
		eml.get('Received', 'Sat, 01 Jan 9999 01:01:01 +0000')[-30:])))
	eml_dt = datetime.utcfromtimestamp(mktime_tz(parsedate_tz(
		eml.get('Date', 'Sat, 01 Jan 0001 01:01:01 +0000'))))

	if eml_dt < recv_dt - timedelta(days=1) or eml_dt > recv_dt + timedelta(hours=1):
		# debug and put("date %s recv %s " % (eml_dt, recv_dt))
		score += 1

		if eml_dt < recv_dt - timedelta(days=15) or \
			eml_dt > recv_dt + timedelta(days=2):
			debug and put(red("time") + " %s " % str(recv_dt - eml_dt))
			score += 1
			log += 'far time '
		else:
			debug and put(yel("time") + " %s " % str(recv_dt - eml_dt))
			log += 'near time '

	if (eml.get('X-Spam-Status', '').lower() == 'yes' or
		eml.get('X-Spam-Flag', '').lower() == 'yes' or
		len(eml.get('X-Spam-Level', '')) > 3):
		debug and put(yel(" X-Spam "))
		score += 1
		log += 'X-Spam '

	debug and put('\033[1;35m%s\033[0m\n' % score)  # purple
	return score, eml, log


bad_chars_re = compile_re('[ >\n\xc2\xa0.,@#-=:*\]\[+_()/|\'\t\r\f\v]')


def email_alpha_len(t, f):
	try:
		s = f(t)
	except Exception as e:
		put(str(e) + '\n')
		s = ''

	s_len = len(s)

	if type(s) is not unicode:
		s = unicode(s, errors='ignore')

	s_with_bad_chars_len = len(s)
	s = bad_chars_re.sub('', s)
	bad_chars_len = s_with_bad_chars_len - len(s)
	ascii_s = s.encode('ascii', errors='ignore')
	s_alpha_len = len([c for c in ascii_s if isalpha(c)])
	# s_unicode_len = len([c for c in s if s.isalnum()])  # considers chinese char as alpha
	return s_len - bad_chars_len, s_alpha_len


txt_links_re = compile_re('http.?://([^./]*?\.)*([^./]*?\.[^./]*?)[/ \n]')
htm_links_re = compile_re('href=.http.?://([^./]*?\.)*([^./]*?\.[^./]*?)[/ "\n]')


def max_same_links(t, links_re):
	domains = [a[1] for a in links_re.findall(str(t))]
	occurences = [domains.count(a) for a in domains]
	occurences.sort()
	return occurences[-1] if len(occurences) else 0


def header_str(h):
	return unicode(make_header(decode_header(h)))


def yel(s):
	return '\033[1;33m' + s + '\033[0m'


def red(s):
	return '\033[1;31m' + s + '\033[0m'


def put(s):
	from sys import stderr
	print(s, end='', file=stderr)


if version_info.major > 2:  # In Python 3: str is the new unicode
	unicode = str

if __name__ == "__main__":
	from sys import stdin

	eml = None
	log = ''

	if version_info.major > 2:
		from io import TextIOWrapper
		score, eml, log = spam_test_eml_log(TextIOWrapper(stdin.buffer, errors='ignore').read())
	else:
		score, eml, log = spam_test_eml_log(stdin.read())

	eml['x-simple-spam-score'] = str(score)
	eml['x-simple-spam-log'] = log
	print(eml)
