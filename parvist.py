# Parvist v0.5
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
##	0.5
#		* LFI/RFI scanning added (use -r switch)
#		* Scrape() had a major bug that was skipping relative paths
#		* Scrape() should be faster now as a lot of fluff has been removed
#		* Did some cleanup for parsing command line arguments
#		* There is now a 'main' (parvist.py) and the class for parvist code has been renamed and moved to Scrape.py
#		* parvist.py now has init(), start(), and stop()
#		* Threaded output so everything is more organized, controlled, predictable, and easier to read
#		* Help has been removed from Scraper (parvist) class and made its own function in main (parvist.py)

from Scraper import *
import sys
import shutil
import os
import time
import threading

switch = sys.argv
domain = None
parvist = None
timeout = 3
depth = 3
lag = 0.1
bots = ["Googlebot/2.1 (+http://www.google.com/bot.html)", "Mozilla/5.0 (compatible; Yahoo! Slurp; http://help.yahoo.com/help/us/ysearch/slurp)", "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)"]
bot = bots[0]
lfiscan = False
emailscan = False
tprint = None

# Initializes everything
def init():
	global parvist
	global domain
	global switch
	global bot
	global timeout
	global depth
	global lag
	global lfiscan
	global emailscan
	global tprint
	
	# Remove previous files
	try:
		shutil.rmtree(".cache")
	except OSError:
		pass
	
	try:
		os.remove("vulns.txt")
	except OSError:
		pass
		
	try:
		os.remove("emails.txt")
	except OSError:
		pass
	
	# Process cmd line arguments
	cmdArgs()
	
	# Initialize scraper object
	parvist = Scraper(domain, switch, bot, timeout, depth, lag, lfiscan, emailscan)

	# Pretty print thread
	tprint = threading.Thread(target=ThreadPrettyPrint)
	
# Starts scraping
def start():
	global parvist
	global tprint
	
	tprint.start()
	parvist.Scrape()

# Called when the application is going to end
def stop():
	# Remove .cache if it exists
	shutil.rmtree(".cache")

# Command line args
def cmdArgs():
	global domain
	global switch
	global bot
	global timeout
	global depth
	global lag
	global lfiscan
	global emailscan
	
	if len(sys.argv) == 1:
		Help()
		sys.exit(0)

	if "-h" in sys.argv:
		Help()
		sys.exit(0)

	# Nicelly allow for domain to be input
	if sys.argv[1].startswith("http"):
		domain = sys.argv[1]
	else:
		domain = "http://" + sys.argv[1]

	# Add "/" to end of domain
	if not sys.argv[1].endswith("/"):
		domain = domain + "/"

	# Process switches
	for item in range(0, len(switch)):
		# Set timeout
		try:
			if switch[item] == "-t":
				timeout = int(switch[item + 1])
		except:
			print "Did not specify timeout argument correctly."
			sys.exit(1)
		
		# Set bot
		try:
			if switch[item] == "-b":
				if int(switch[item + 1]) >= 1 and int(switch[item + 1]) <= 3:
					bot = bots[int(switch[item + 1]) - 1]
		except:
			print "Did not specify bot argument correctly."
			sys.exit(1)

		# Set depth
		try:
			if switch[item] == "-d":
				depth = int(switch[item + 1])
		except:
			print "Did not specify depth argument correctly."
			sys.exit(1)
		
		# Set lag
		try:
			if switch[item] == "-l":
				lag = float(switch[item + 1])
		except:
			print "Did not specify lag argument correctly."
			sys.exit(1)
		
		# Set emailscan
		if switch[item] == "-e":
			emailscan = True

		# Set lfiscan
		if switch[item] == "-r":
			lfiscan = True

def ThreadPrettyPrint():
	global parvist
	
	print "Switches: " + str(parvist.switch)
	print "User-agent: " + parvist.bot
	print "Depth: " + str(parvist.depth)
	print "Lag: " + str(parvist.lag)
	print "Timeout: " + str(parvist.timeout)
	
	while parvist.shouldDie != True:
		print "Cycles: " + str(parvist.cycles)
		print "Remaining Links: " + str(len(parvist.mainList))
		print "Scanned links: " + str(len(parvist.doneList))
		
		if parvist.lfiscan == True:
			print "Possible LFI Vulnerabilities found: " + str(len(parvist.lfiList))
			
		if parvist.emailscan == True:
			print "Emails found: " + str(len(parvist.emailList))
		
		print
		time.sleep(1)

# Help
def Help():
	print "\n"
	print "SYNOPSIS:"
	print textwrap.fill("parvist.py <domain> [switches]", initial_indent="\t", subsequent_indent="\t")
	print "\n"
	print "SWITCHES:"
	print textwrap.fill("-s", initial_indent="\t", subsequent_indent="\t"),
	print textwrap.fill("Scrape only the domain in <domain>, no third party domains.", initial_indent="\t\t", subsequent_indent="\t")
	print textwrap.fill("-t <int>", initial_indent="\t", subsequent_indent="\t"),
	print textwrap.fill("Specify the timeout in seconds. Default is 3 seconds.", initial_indent="\t", subsequent_indent="\t")
	print textwrap.fill("-b <int>", initial_indent="\t", subsequent_indent="\t"),
	print textwrap.fill("Specify the User-Agent bot to impersonate. Default is 1 (Googlebot).", initial_indent="\t", subsequent_indent="\t")
	print textwrap.fill("-d <int>", initial_indent="\t", subsequent_indent="\t"),
	print textwrap.fill("Specify the depth the scraper should go. Default is 3.", initial_indent="\t", subsequent_indent="\t")
	print textwrap.fill("-l <int/float>", initial_indent="\t", subsequent_indent="\t"),
	print textwrap.fill("Specify the \"lag\" between connection attempts. Default is 100ms.", initial_indent="\t", subsequent_indent="\t")
	print textwrap.fill("-e", initial_indent="\t", subsequent_indent="\t"),
	print textwrap.fill("If specified, the scraper will harvest emails.", initial_indent="\t\t", subsequent_indent="\t")
	print textwrap.fill("-r", initial_indent="\t", subsequent_indent="\t"),
	print textwrap.fill("If specified, the scraper will look for LFI/RFI.", initial_indent="\t\t", subsequent_indent="\t")
	print textwrap.fill("-h", initial_indent="\t", subsequent_indent="\t"),
	print textwrap.fill("Print help information.", initial_indent="\t\t", subsequent_indent="\t")
	print "\n"
	print "NOTES:"
	print textwrap.fill("Timeout: If the timeout is set too low the connection will be aborted AND THE HTML WILL NOT BE SCRAPED! It is highly recommended that you do NOT set this any lower than 3 seconds. Any time there is a socket.timeout error the message \"<domain> timed out.\" will be printed.", initial_indent="\t", subsequent_indent="\t")
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

init()
start()
stop()
