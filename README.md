Parvist
=======
Parvist is a web-crawler bot that can be used to harvest emails and many other bits of information on the web.

A new feature in version 0.5 is link saving for possible LFI/RFI vulnerabilities.

License
=======
GPLv3

Author
======
Josten Moore

Features
========

1. Single domain scrape mode.
2. Link builder mode.
3. Time delays and "lag" to mitigate red-flags on the server.
4. Email harvesting mode.
5. Able to spoof your user-agent (3 supported, default is Googlebot).
6. Output is now threaded in a timer to make it easier to read
7. Link scanning for possible LFI/RFI vulnerabilites.

Getting Started
===============

Clone this repo by doing:

<code>git clone git@github.com:josten/parvist.git</code>

Make sure that you have <code>python 2.7.x</code> installed.

Switches
========

* <code>-s</code> Scrape only the specified domain (no third party domains).
* <code>-t</code> Specify the connection timeout (default is 3 seconds).
* <code>-b</code> Specify the user-agent bot (default is google).
* <code>-d</code> Specify the depth to scrape (default is 3).
* <code>-l</code> Specify the lag between connection attempts (default is 100ms).
* <code>-e</code> If specified the scraper will harvest emails.
* <code>-r</code> If specified the scraper will look for possible LFI/RFI vulnerabilities.
* <code>-h</code> Prints help.

Usage
=====

Using parvist is very simple; here are some examples:

* <code>python parvist.py -h</code> will print the help information.
* <code>python parvist.py www.google.com -s -e</code> will start scraping www.google.com for emails and ignore all third party domains.
* <code>python parvist.py www.google.com -s -e -l 1 -t 5</code> will start scraping www.google.com for emails while ignoring third party domains and setting a 'lag' delay of 1 second and a connection timeout of 5 seconds.
* <code>python parvist.py www.google.com -s -e -r</code> will start scraping for possible LFI/RFI vulnerabilies while harvesting emails using default settings.
<<<<<<< HEAD

RFI/LFI Sample
==============

The new <code>-r</code> switch has proven to be quite useful; here is a same of some finds (real domains ommitted):

http://www.example.com/template.php?page=ref.php
http://www.example.com/template.php?page=products.php
http://www.example.com/template.php?page=history.php
http://www.example.com/template.php?page=impressum.php
http://www.example.com/template.php?page=finance.php
http://www.example.com/template.php?page=customer.php
http://www.example.com/template.php?page=sales.php
http://www.example.com/template.php?page=contact.php
http://www.example.com/template.php?page=index2.php
http://www.example.com/template.php?page=intro.php
