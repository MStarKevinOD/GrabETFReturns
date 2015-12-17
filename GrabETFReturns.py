
import datetime as dt
import re
import requests
import StringIO
import sys
import time

try:
	action = sys.argv[1]		# can be either P for print or L for log or K for log until killed
except IndexError:
	action = "P"

if len(sys.argv) > 2:

	if action == 'K':
		wait_time = sys.argv[2]
	else:
		wait_time = 60

NOW = dt.datetime.now

HEADERS = {'User-Agent' : "Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.696.16 Safari/534.24"}

google = 'https://www.google.com/finance?q='
yahoo =  'https://au.finance.yahoo.com/q?s='

tickers = ['VGS', 'IAF','SLF', 'STW', 'DJRE', 'WXOZ']

OUTPUT_FILE = 'C:\\temp\\ETF_Prices.txt'


def try_yahoo(url, ticker):

	url_ticker = ticker + '.ax'

	r = requests.get(url + url_ticker, headers=HEADERS)

	text = r.content#.encode('utf-8', 'ignore')

	s = StringIO.StringIO(text)
	s.seek(0)

	for line in s.readlines():

		m = re.search(r'<span id="yfs_p43_%s">\(([-+]?\d*.\d*).*\)<\/span>' % url_ticker.lower(), line, re.IGNORECASE)

		if m:
			
			if "neg_arrow" in line:

				return "-" + m.group(1)

			else:

				return m.group(1)


def try_google(url, ticker):

	url_ticker = 'ASX%3a' + ticker

	r = requests.get(url+url_ticker, headers=HEADERS)

	text = r.content#.encode('utf-8', 'ignore')

	s = StringIO.StringIO(text)
	s.seek(0)

	for line in s.readlines():

		m = re.search(r'name:"%s",cp:"([-+]?\d*.\d*)"' % ticker.lower(), line, re.IGNORECASE)

		if m:

			break

	else:
		
		return try_google2(s, ticker)
			
	return m.group(1)


def try_google2(s, ticker):

	scan_level = 1

	s.seek(0)

	for line in s.readlines():

		if scan_level == 1:

			m = re.search(r'<a id=rct-1 href="\/finance\?q=ASX:%s.*" >%s<\/a>' % (ticker, ticker), line, re.IGNORECASE)

			if m:

				scan_level = 2

			continue

		else:

			m = re.search(r'<span class=chr id=ref_.*_cp>\(([-+]?\d*.\d*)%\)<\/span><\/nobr>', line, re.IGNORECASE)

			if m:

				return m.group(1)



def collect_returns():
	
	results = []

	for ticker in tickers:

		result = try_google(google, ticker)

		try:
			res = float(result)
		except (ValueError, TypeError):
			res = 'NaN'

		results.append((ticker + '-Google', res))

		result = try_yahoo(yahoo, ticker)

		try:
			res = float(result)
		except (ValueError, TypeError):
			res = 'NaN'

		results.append((ticker + '-Yahoo', res))

	return results


def log_returns():

	res = collect_returns()

	log_string = "%s,%s\n" % (NOW().strftime("%H:%M:%S"), ','.join([str(r) for r in res]).replace('(','').replace(')','').replace(' ','').replace("'",''))

	with open(OUTPUT_FILE, 'a') as f:
		f.write(log_string)


def log_until_killed(wait=60):

	while True:
		log_returns()
		time.sleep(wait)


if __name__ == "__main__":

	if action == 'K':
		log_until_killed(wait_time)

	elif action == "L":

		log_returns()

	else:

		ETF_returns = collect_returns()

		print "%s,%s\n" % (NOW().strftime("%H:%M:%S"), ','.join([str(x) for x in ETF_returns]).replace('(','').replace(')','').replace(' ','').replace("'",''))





