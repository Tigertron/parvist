# Parvist v0.481
#
# Features:
#	TODO - Implement SSN scraping
#	TODO - Implement phone/fax scraping
#
# Changelog
#
##	0.31
#		* Added argv input for domain
##	0.315
#		* Domain checking
##	0.32
#		* Rewrote Scrape_Links
#		* Optimizations
##	0.33
#		* Started using httplib2 for connections (drastically improved connection performance)
#		* Rewrite of various components
#		* Fixed how it would hang on certain websites
##	0.34
#		* Rewrote Scrape_Emails
##	0.35
#		* Added timeout for scraping (2 seconds)
##	0.36
#		* Emails converted to lowercase
## 	0.37
#		* Added -s switch for "single" domain scraping only.
#		* Fixed email scrape regex
##	0.38
#		* Fixed major bug in Scrape_Links
##	0.39
#		* User-Agent now defaults to GoogleBot
##	0.40
#		* Restructured main email harvesting loop to a function definition in Parvist
## 	0.41
#		* Updated how switches are handled
#		* Added help
#		* Added timeout control using -t switch
##	0.42
#		* Added -b switch to specify which bot to use
## 	0.43
#		* Fixed bug where main request loop wasn't reflecting chosen bot
#		* Code changes and optimizations
##	0.44
#		* Code base changes
##	0.45
#		* Code base changes
#		* Added depth feature to scraping
##	0.451
#		* Bug fixes
##	0.46
#		* Bug fixes
#		* Dynamic depth determination (performance improvement)
#		* No need to specify full URL now; automatically handled by script
##	0.47
#		* Redesigned main loop with performance in mind
#		* Done links are skipped
#		* main loop forces script to run until mainList is empty
##	0.48
#		* KeyboardInterrupt is finally handled.
#		* -l switch added.
#		* .cache removed upon exit
##	0.481
#		* Minor tweaks and adjustments

import re
import sys
import threading
import httplib2
import string
import textwrap
import time
import shutil
from bs4 import BeautifulSoup

class Parvist:
	mainList = []
	scrapedList = []
	emailList = []
	doneList = []
	switch = []
	bot = ""
	timeout = 3
	domain = ""
	counter = 0
	depth = 3
	depthCounter = 0
	cycles = 0
	lag = 0.1
	h = httplib2.Http()
	
	def __init__(self, domain=None, switch=None, bot=None, timeout=3, depth=3, lag=0.1):
		self.domain = domain
		self.mainList = [domain]
		self.switch = switch
		self.bot = bot
		self.timeout = timeout
		self.depth = depth
		self.lag = lag
		self.h = httplib2.Http(".cache", self.timeout)
		self.h.follow_all_redirects = True
		self.h.follow_redirects = True
	
	def Help(self):
		print "\n"
		print "SYNOPSIS:"
		print textwrap.fill("parvist.py <domain> [switches]", initial_indent="\t", subsequent_indent="\t")
		print "\n"
		print "SWITCHES:"
		print textwrap.fill("-s", initial_indent="\t", subsequent_indent="\t"),
		print textwrap.fill("Scrape only the domain in <domain>, do not go to third party domains.", initial_indent="\t\t", subsequent_indent="\t")
		print textwrap.fill("-t <int>", initial_indent="\t", subsequent_indent="\t"),
		print textwrap.fill("Specify the timeout in seconds.", initial_indent="\t", subsequent_indent="\t")
		print textwrap.fill("-b <int>", initial_indent="\t", subsequent_indent="\t"),
		print textwrap.fill("Specify the User-Agent bot to impersonate. Default is 1 (Googlebot).", initial_indent="\t", subsequent_indent="\t")
		print textwrap.fill("-d <int>", initial_indent="\t", subsequent_indent="\t"),
		print textwrap.fill("Specify the depth the scraper should go; default is 3.", initial_indent="\t", subsequent_indent="\t")
		print textwrap.fill("-l <int/float>", initial_indent="\t", subsequent_indent="\t"),
		print textwrap.fill("Specify the \"lag\" between connection attempts; default is 100ms", initial_indent="\t", subsequent_indent="\t")
		print textwrap.fill("-e", initial_indent="\t", subsequent_indent="\t"),
		print textwrap.fill("If specified, the scraper will harvest emails.", initial_indent="\t\t", subsequent_indent="\t")
		print textwrap.fill("-h", initial_indent="\t", subsequent_indent="\t"),
		print textwrap.fill("Print help information.", initial_indent="\t\t", subsequent_indent="\t")
		print "\n"
		print "NOTES:"
		print textwrap.fill("Timeout: If the timeout is set too low the connection will be aborted AND THE HTML WILL NOT BE SCRAPED! The default timeout is 3 seconds. It is highly recommended that you do NOT set this any lower than 3 seconds. Any time there is a socket.timeout error the message \"<domain> timed out.\" will be printed.", initial_indent="\t", subsequent_indent="\t")
		print "\n"
		print textwrap.fill("User-Agent bots:", initial_indent="\t", subsequent_indent="\t")
		print textwrap.fill("1. Google bot", initial_indent="\t", subsequent_indent="\t")
		print textwrap.fill("2. Yahoo bot", initial_indent="\t", subsequent_indent="\t")
		print textwrap.fill("3. Bing bot", initial_indent="\t", subsequent_indent="\t")
		print "\n"
		print textwrap.fill("Depth: is defined as how many sub-directories there are; so if a URI was \"about/contact\" then the depth is 2.", initial_indent="\t", subsequent_indent="\t")
		print "\n"
		print textwrap.fill("Lag: is the time delay between scraping links. If this is set to 0 then KeyboardInterrupts will NOT work!", initial_indent="\t", subsequent_indent="\t")
		print "\n"		

	def WriteToDisk(self):
		# Only write to a file if emailList list is not empty
		if self.emailList:
			print "Writing emails..."
			file = open("emails.txt", "w")
			
			for email in self.emailList:
				file.write(email + "\n")
			file.close()
	
	def Scrape_Emails(self, webpage, emailList):
		# Find all emails in a webpage using a regex
		m = re.findall("[\w\-\.]+@[\w\-]+\.[\w\.]*[a-zA-Z]+", webpage)
		
		# Convert all of the found emails to lowercase
		m = [email.lower() for email in m]
		
		# Add emails to previous emailList and only store unique emails
		emailList.extend(m)
		emailList = list(set(emailList))

		return emailList
	
	def Scrape_Links(self, soup, domain):

		if domain.endswith("/"):
			domain = domain[0:-1]
		
		# For each link in the html code that has <a href= that is not blank (None) add it to urlList
		urlList = [link.get("href") for link in soup.findAll("a") if link.get("href") is not None]
		
		# Remove the leading "/" to properly build links
		urlListNotAbsolute = [url for url in urlList if url.startswith("/")]
		
		# Remove non absolute links
		urlList = [url for url in urlList if not url.startswith("/")]
		
		# Make all links absolute
		urlListNotAbsolute = [domain + url for url in urlListNotAbsolute if url.startswith("/")]
		
		# Combine urlLists
		urlList.extend(urlListNotAbsolute)
		
		# No links over 60 characters
		#urlList = [url for url in urlList if len(url) <= 60]
		
		# Only scrape first party domain
		if "-s" in self.switch:
			urlList = [url for url in urlList if url.startswith(domain)]

		# Remove all links that do not start with "http"
		urlList = [url for url in urlList if url.startswith("http")]
		
		# For non threading
		return urlList
	
	def sub_request(self, element):
		method = "GET"
		headers = {"User-Agent":self.bot}
		body = None
		
		return self.h.request(element, method, body, headers, redirections=15)
	
	def Scrape(self):
		print "Switches: " + str(parvist.switch)
		print "User-agent: " + self.bot
		print "Depth: " + str(self.depth)
		print "Lag: " + str(self.lag)
		print "Timeout: " + str(self.timeout)

		# Keep scraping links as long as there are links in self.mainList
		while self.mainList:
			try:
				print "Cycles: " + str(self.cycles)
				print "Remaining links: " + str(len(self.mainList))
				print "Scanned links: " + str(len(self.doneList))
				
				# Set lag between connection attempts
				time.sleep(self.lag)

				# Grab the first link from mainList
				url = self.mainList.pop(0)
				print url
				
				# Check if url in doneList; if it is skip this cycle.
				if url in self.doneList:
					self.mainList = [ourl for ourl in self.mainList if ourl != url]
					print
					continue			
	
				# Dynamically determine depth
				stripurl = string.replace(url, self.domain, '')
				self.depthCounter = string.count(stripurl[:-1], '/') + 1
						
				# Open the remote connection
				content = ""
				try:
					resp, content = self.sub_request(url)
				except:
					print url + " timed out."
		
				# Get BeautifulSoup object from content
				try:
					soup = BeautifulSoup(content)
				except:
					pass
							
				# Grab all of the links from url and add them to mainList while abiding by depth
				try:
					# Grab all links while conforming to the depth requirement
					if self.depthCounter < self.depth:
						urlList = self.Scrape_Links(soup, url)
						self.mainList.extend(urlList)
				except:
					print "Error has occured in mainList.extend"
				
				# Scrape emails
				if '-e' in self.switch:
					# Scrape emails	and add them to self.emailList
					self.emailList = self.Scrape_Emails(content, self.emailList)
					print "Emails found: " + str(len(self.emailList))
			
				# Write to disk
				if self.cycles % 100 == 0:
					if self.emailList:
						self.WriteToDisk()
		
				# Add url to donelist so we do not re-scrape
				self.doneList.append(url)
	
				self.cycles += 1

				print
			except (KeyboardInterrupt, SystemExit):
				print "\n\nKeyboardInterrupt caught, exiting..."
				self.WriteToDisk()
				shutil.rmtree(".cache")
				sys.exit(0)
	
		try:
			self.WriteToDisk()
		except:
			print "Unable to initially scrape the target; double-check domain name."

switch = sys.argv
domain = None
timeout = 3
depth = 3
lag = 0.1
bots = ["Googlebot/2.1 (+http://www.google.com/bot.html)", "Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)", "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)"]
bot = bots[0]
parvist = Parvist()

# Remove previous .cache if it exists
shutil.rmtree(".cache")

# Print Help()
if len(sys.argv) == 1:
	parvist.Help()
	sys.exit(0)

if "-h" in sys.argv:
	parvist.Help()
	sys.exit(0)

# Nicelly allow for domain to be input
if sys.argv[1].startswith("http"):
	domain = sys.argv[1]
else:
	domain = "http://" + sys.argv[1]

# Add "/" to end of domain
if not sys.argv[1].endswith("/"):
	domain = domain + "/"

# Set timeout
for item in range(0, len(switch)):
	try:
		if switch[item] == "-t":
			timeout = int(switch[item + 1])
	except:
		print "Did not specify timeout argument correctly."
		sys.exit(1)

# Set bot
for item in range(0, len(switch)):
	try:
		if switch[item] == "-b":
			if int(switch[item + 1]) >= 1 and int(switch[item + 1]) <= 3:
				bot = bots[int(switch[item + 1]) - 1]
	except:
		print "Did not specify bot argument correctly."
		sys.exit(1)

# Set depth
for item in range(0, len(switch)):
	try:
		if switch[item] == "-d":
			depth = int(switch[item + 1])
	except:
		print "Did not specify depth argument correctly."
		sys.exit(1)

# Set lag
for item in range(0, len(switch)):
	try:
		if switch[item] == "-l":
			lag = float(switch[item + 1])
	except:
		print "Did not specify lag argument correctly."
		sys.exit(1)

parvist = Parvist(domain, switch, bot, timeout, depth, lag)

parvist.Scrape()

# Remove .cache if it exists
shutil.rmtree(".cache")