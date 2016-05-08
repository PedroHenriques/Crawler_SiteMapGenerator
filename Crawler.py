# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# 															 #
# Python Crawler and Site Map Generator v1.0.0				 #
#															 #
# Copyright 2016, PedroHenriques 							 #
# http://www.pedrojhenriques.com 							 #
# https://github.com/PedroHenriques 						 #
# 															 #
# Free to use under the MIT license.			 			 #
# http://www.opensource.org/licenses/mit-license.php 		 #
# 															 #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import threading, time, urllib.robotparser, urllib.request, urllib.parse
import ParserHTML, general

class Crawler(threading.Thread) :
	"""This class defined a website crawler.
	It will visit a URL and grab all the links in it.
	The links collected will then be stored in a queue for later use."""

	# class variable used to force all instances to terminate
	terminate_thread_ = False

	# class variable used to keep track of the URLs that are either in the queue or have been processed
	# and the URLs that have been fully processed
	known_urls_ = None
	crawled_urls_ = None

	# class variable used to keep track of URLs found that point to an
	# external website
	external_urls_ = None

	# class variable used to keep track of URLs found that could not be successfully crawled
	failed_urls_ = None

	# class variables referencing a queue and its lock
	queue_ = None
	queue_lock_ = None

	# class variable with the root URL for the website we're crawling
	root_url_ = ""

	def __init__(self) :
		# call the threading.Thread __init__ method, and make sure all threads are daemon=True
		# this insures all threads will terminate if the application is shutdown...even thought data can be corrupted.
		super().__init__(daemon=True)

	# main method of a thread, defining what the thread should do
	# will continue running until self.terminate_thread_ is True
	def run(self) :
		# if the class variables aren't set, terminate thread
		if (self.known_urls_ == None or self.crawled_urls_ == None or self.external_urls_ == None or self.failed_urls_ == None or self.queue_ == None or self.queue_lock_ == None or self.root_url_ == "") :
			print("At least 1 class variable not set!")
			return

		# parse the root_url_
		self.parsed_root_url = urllib.parse.urlparse(self.root_url_)
		# remove the port information, if it's present
		port_index = self.parsed_root_url.netloc.find(":")
		if (port_index != -1) :
			self.parsed_root_url_noport = self.parsed_root_url.netloc[:port_index]
		else :
			self.parsed_root_url_noport = self.parsed_root_url.netloc

		# build the full URL with no port
		self.parsed_root_url_full = self.parsed_root_url_noport + self.parsed_root_url.path

		# loop until the terminate flag is set to True
		while not self.terminate_thread_ :
			# get the lock for the queue
			self.queue_lock_.acquire()

			if (len(self.queue_) > 0) :
				# get the next URL from the queue
				cur_url = self.queue_.pop()
				# release the lock for the queue
				self.queue_lock_.release()

				# process this URL
				try:
					urls = self.processURL(cur_url)

					# get the lock for the queue
					self.queue_lock_.acquire()

					# if the list is not empty, add them to the queue_
					if (len(urls) > 0) :
						for url in urls :
							# check if this URL is already in the queue or has been processed
							if (url not in self.known_urls_) :
								# add this URL to the queue
								self.queue_.add(url)
								# add this URL to the set with known URLs
								self.known_urls_.add(url)

					# add this URL to the set with crawled URLs
					self.crawled_urls_.add(cur_url)

					# release the lock for the queue
					self.queue_lock_.release()
				except Exception as e:
					# add this URL to the failed_urls_
					self.failed_urls_.add(cur_url)
					# add this URL to the set with known URLs
					self.known_urls_.add(cur_url)
			else :
				# release the lock for the queue
				self.queue_lock_.release()
				# wait 1 second
				time.sleep(1)

		print("thread terminating: " + str(threading.get_ident()))

	# this mehod will visit the url, collect all it's HTML, feed it to the HTML parser
	# and gather all the links in that URL
	def processURL(self, cur_url) :
		# local variable to store the desired URLs
		urls = []

		# instantiate the class to parse the HTML
		html_parser = ParserHTML.ParserHTML(self.root_url_, {"a" : {"href" : True}})

		# grab the URL's HTML text and feed it to the html parser
		# FIXME: get the encoding being used on the url and use it to decode, instead of the hardcoded utf-8
		html_parser.feed(urllib.request.urlopen(cur_url).read().decode("utf-8"))

		# loop through the gathered links, prepare them and add them to the queue
		for url_candidate in html_parser.collected_attrs :
			# check if this URL points to an external domain
			if (self.isExternal(url_candidate)) :
				# store it in the seperate set
				self.external_urls_.add(url_candidate)
				continue

			# add this URL to the final list
			urls.append(url_candidate)

		return(urls)

	# checks if the passed URL is external to the project's domain
	# return True if it's external, False otherwise
	def isExternal(self, url) :
		# add the http:// to the start of url, if not there already
		if (not url.startswith("http://") and not url.startswith("https://")) :
			url = "http://" + url

		# parse the URL
		parsed_url = urllib.parse.urlparse(url)

		# remove the port information, if it's present
		port_index = parsed_url.netloc.find(":")
		if (port_index != -1) :
			parsed_url_noport = parsed_url.netloc[0:port_index]
		else :
			parsed_url_noport = parsed_url.netloc

		# build the full URL with no port
		parsed_url_full = parsed_url_noport + parsed_url.path

		# if the root url for the current project is in url, then it's an internal link
		# doesn't necessarily work for subdomains
		if (self.parsed_root_url_full in parsed_url_full) :
			return(False)

		# check if the reason root url isn't in url is because 1 of them having the www. omitted
		# if that's the case, then it's still an internal link
		if (self.parsed_root_url_full.startswith("www.")) :
			aux_root_url_full = self.parsed_root_url_full[4:]
		else :
			aux_root_url_full = self.parsed_root_url_full

		if (parsed_url_full.startswith("www.")) :
			aux_url_full = parsed_url_full[4:]
		else :
			aux_url_full = parsed_url_full

		if (aux_root_url_full in aux_url_full) :
			return(False)

		# check if we're dealing with a case of a subdomain written in 2 different forms
		# at this point we only haven't checked the case where both forms are being used,
		# 1 by each url
		# i.e., 1 is using "subdomain.domain.ending" and the other is using "(www.)?domain.ending/subdomain"
		# we'll work with the root url and, if possible, swap from 1 form to the other and match it against
		# the passed url to check if they're part of the same subdomain
		# NOTE: this code assumes all levels of a subdomain are represented either as subdomains or folders, no mixed structures (ex: subdomain1.domain.ending/subdomain2)
		# check if the root url could be of the form "subdomain.domain.ending"
		if (self.parsed_root_url.path == "" and not self.parsed_root_url_noport.startswith("www.") and self.parsed_root_url_noport.count(".") > 1) :
			# the root url might be of the form "subdomain.domain.ending" --> it can also be something like "domain.co.uk" which isn't a subdomain
			# convert to the form "domain.ending/subdomain"
			converted_root_url_parts = self.parsed_root_url_noport.split(".")

			# start by testing assuming the ending is 1 part (so not "co.uk")
			converted_root_url = ".".join(converted_root_url_parts[-2:]) + "/" + "/".join(converted_root_url_parts[:-2])
			# match converted_root_url against passed url with no "www."
			if (converted_root_url in aux_url_full) :
				return(False)

			# test assuming the ending is 2 part (so for example "co.uk")
			converted_root_url = ".".join(converted_root_url_parts[-3:]) + "/" + "/".join(converted_root_url_parts[:-3])
			# match converted_root_url against passed url with no "www."
			if (converted_root_url in aux_url_full) :
				return(False)
		# check if the root url could be of the form "(www.)?domain.ending/subdomain"
		# only possible if path isn't empty
		elif (self.parsed_root_url.path != "") :
			# the root url might be of the form "(www.)?domain.ending/subdomain"
			# convert to the form "subdomain.domain.ending"
			converted_root_url = general.convertFoldersToSubdomain(self.parsed_root_url)

			# match converted_root_url against passed url with no "www."
			if (converted_root_url in aux_url_full) :
				return(False)

		# at this point it must be an external link, or a multi-level deep subdomain with a mixed structure
		return(True)
