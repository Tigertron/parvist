Parvist
=======
Parvist is a web-crawler bot that can be used to harvest emails and many other bits of information on the web.

License
-------
GPLv3

Features
========

1. Single domain scrape mode.
2. Link builder mode.
3. Time delays and "lag" to mitigate red-flags.
4. Email harvesting mode.
5. Able to spoof your user-agent (3 supported, default is Googlebot).

Getting Started
===============

Clone this repo by doing:

<code>git clone git@github.com:josten/parvist.git</code>

Make sure that you have <code>python 2.7.x</code> installed.

Usage
=====

Using parvist is very simple; here are some examples:

* <code>python parvist.py -h</code> will print the help information.
* <code>python parvist.py www.google.com -s -e</code> will start scraping www.google.com for emails and ignore all third party domains.
* <code>python parvist.py www.google.com -s -e -l 1 -t 5</code> will start scraping www.google.com for emails while ignoring third party domains and setting a 'lag' delay of 1 second and a connection timeout of 5 seconds.