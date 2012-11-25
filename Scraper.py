import re
import sys
import threading
import httplib2
import string
import textwrap
import time
import shutil
from bs4 import BeautifulSoup

class Scraper:
	mainList = []
	emailList = []
	doneList = []
	lfiList = []
	switch = []
	bot = None
	timeout = None
	domain = None
	lag = None
	lfiscan = False
	emailscan = False
	depth = None
	shouldDie = False
	depthCounter = 0
	cycles = 0
	h = httplib2.Http()
	
	def __init__(self, domain=None, switch=None, bot=None, timeout=3, depth=3, lag=0.1, lfiscan=False, emailscan=False):
		self.domain = domain
		self.mainList = [domain]
		self.switch = switch
		self.bot = bot
		self.timeout = timeout
		self.depth = depth
		self.lag = lag
		self.lfiscan = lfiscan
		self.emailscan = emailscan
		self.h = httplib2.Http(".cache", self.timeout)
		self.h.follow_all_redirects = True
		self.h.follow_redirects = True	

	def WriteToDisk(self):
		# Only write to a file if emailList list is not empty
		if self.emailList:
			print "Writing emails..."
			file = open("emails.txt", "w")
			
			for email in self.emailList:
				file.write(email + "\n")
			file.close()
			
		if self.lfiList:
			print "Writing possible LFI vulns..."
			file = open("vulns.txt", "w")
			
			for url in self.lfiList:
				file.write(url + "\n")
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
	
	def Scrape_LFI(self, urlList, lfiList):
		# Find all links on the page that may be vulnerable to LFI
		tmpList = []
		
		# Finds all possible LFI
		for url in urlList:
			m = re.search("[a-zA-z0-9]*\.[a-zA-Z0-9]{3}\?[a-zA-Z0-9]*=[a-zA-Z0-9]*\.[a-zA-Z0-9]{3}", url)
			if m is not None:
				tmpList.append(m.group(0))
		
		# Add to list with unique links
		tmpList = list(set(tmpList))
		lfiList = [self.domain + url for url in tmpList]
		return lfiList
	
	def Scrape_Links(self, soup, domain):

		if domain.endswith("/"):
			domain = domain[0:-1]
		
		# For each link in the html code that has <a href= that is not blank (None) add it to urlList
		urlList = [link.get("href") for link in soup.findAll("a") if link.get("href") is not None]
		
		# First type of non-absolute links
		nonAbsolute1 = [link[1:] for link in urlList if link.startswith("/")]
		nonAbsolute1 = [domain + "/" + link for link in nonAbsolute1]
		
		# Second type of non-absolute links
		nonAbsolute2 = [domain + "/" + link for link in urlList if not link.startswith("http") and not link.startswith("/") and not link.startswith(".")]
		
		urlList.extend(nonAbsolute1)
		urlList.extend(nonAbsolute2)
		
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

		# Keep scraping links as long as there are links in self.mainList
		while self.mainList:
			try:
				
				# Set lag between connection attempts
				time.sleep(self.lag)

				# Grab the first link from mainList
				url = self.mainList.pop(0)
				
				# Check if url in doneList; if it is skip this cycle.
				if url in self.doneList:
					self.mainList = [ourl for ourl in self.mainList if ourl != url]
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
				
				# lfiscan
				if self.lfiscan == True:
					self.lfiList.extend(self.Scrape_LFI(urlList, self.lfiList))
					self.lfiList = list(set(self.lfiList))
					
				
				# Scrape emails
				if self.emailscan == True:
					# Scrape emails	and add them to self.emailList
					self.emailList = self.Scrape_Emails(content, self.emailList)
				
				# Write to disk
				if self.cycles % 100 == 0:
					if self.emailList:
						self.WriteToDisk()
		
				# Add url to donelist so we do not re-scrape
				self.doneList.append(url)
	
				self.cycles += 1

			except (KeyboardInterrupt, SystemExit):
				print "\n\nKeyboardInterrupt caught, exiting..."
				self.WriteToDisk()
				shutil.rmtree(".cache")
				self.shouldDie = True
				sys.exit(0)
	
		try:
			self.WriteToDisk()
		except:
			print "Unable to initially scrape the target; double-check domain name."
