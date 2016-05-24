# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# 															 #
# Python Crawler and Site Map Generator v1.2.0				 #
#															 #
# Copyright 2016, PedroHenriques 							 #
# http://www.pedrojhenriques.com 							 #
# https://github.com/PedroHenriques 						 #
# 															 #
# Free to use under the MIT license.			 			 #
# http://www.opensource.org/licenses/mit-license.php 		 #
# 															 #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import threading, time, urllib.robotparser

class MapGenerator(threading.Thread) :
	"""This class will build a site map for a given web domain, that has been crawled.
	Any rules set for that domain in it's robots.txt file will be followed."""

	# class variable used to force all instances to terminate
	terminate_thread_ = False

	# class variables referencing a queue and its lock
	queue_ = None
	queue_lock_ = None

	# class variable with the root URL for the website we're crawling
	root_url_ = ""

	# class variable with the robots.txt parser
	robots_parser_ = None

	# class variable with the local system's time to be used as the lastmod value
	local_time_ = ""

	# class variable used to store the final items
	site_map_items_ = None

	def __init__(self, use_robots) :
		# call the threading.Thread __init__ method, and make sure all threads are daemon=True
		# this insures all threads will terminate if the application is shutdown...even thought data can be corrupted.
		super().__init__(daemon=True)

		# set the instance variable to control the use or not of the robots.txt file
		self.use_robots = bool(use_robots)

		# if we haven't set the robots.txt parse, do so
		if (self.use_robots and self.robots_parser_ == None) :
			self.parseRobots()

	# main method of a thread, defining what the thread should do
	# will continue running until self.terminate_thread_ is True
	def run(self) :
		# if the class variables aren't set, terminate thread
		if (self.queue_ == None or self.queue_lock_ == None or self.root_url_ == "" or (self.use_robots and self.robots_parser_ == None) or self.local_time_ == "" or self.site_map_items_ == None) :
			print("MapGenerator: At least 1 class variable not set!")
			return

		# loop until the terminate flag is set to True
		while not self.terminate_thread_ :
			# get the lock for the queue
			self.queue_lock_.acquire()

			if (len(self.queue_) > 0) :
				# get the next URL from the queue
				cur_url = self.queue_.pop()
				# release the lock for the queue
				self.queue_lock_.release()

				# check if this URL passes the robots.txt rules
				if (self.canAccessURL(cur_url)) :
					# build the site map item
					item = self.buildSiteMapItem(cur_url)

					# get the lock for the queue
					self.queue_lock_.acquire()

					# add the item to the storing variable
					self.site_map_items_.append(item)

					# release the lock for the queue
					self.queue_lock_.release()
			else :
				# release the lock for the queue
				self.queue_lock_.release()
				# wait 1 second
				time.sleep(1)

		print("thread terminating: " + str(threading.get_ident()))

	# find and read the robots.txt file on the server
	def parseRobots(self) :
		self.robots_parser_ = urllib.robotparser.RobotFileParser(self.root_url_ + "/robots.txt")
		self.robots_parser_.read()

	# checks if the passed URL should be indexed by SEO, based on the server's robots.txt file
	# returns True if the URL is to be indexed, False otherwise
	def canAccessURL(self, url) :
		# if the robots.txt is empty, doesn't exist
		# or we don't want to use the robots.txt file (==None), allow all URLs
		if (self.robots_parser_ == None) :
			return(True)

		return(self.robots_parser_.can_fetch("*", url))

	# adds a url to the site map with all necessary data for it
	def buildSiteMapItem(self, url) :
		# calculate how many levels deep this URL is
		levels_deep = url[len(self.root_url_):].count("/")

		# calculate a default priority for this URL, based on the level of depth compared to the home page
		# he home page gets 0.8 priority
		if (levels_deep == 0) :
			# it's the home page
			priority = 0.9
		elif (levels_deep == 1) :
			# 1 level deep. Done here because the formula below would return 1
			priority = 0.7
		else :
			priority = 1 / levels_deep

		# build the site map's item
		item = {"url" : url, "lastmod" : self.local_time_, "changefreq" : "monthly", "priority" : str(round(priority, 1))}

		return(item)
