# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# 															 #
# Python Crawler and Site Map Generator v1.1.0				 #
#															 #
# Copyright 2016, PedroHenriques 							 #
# http://www.pedrojhenriques.com 							 #
# https://github.com/PedroHenriques 						 #
# 															 #
# Free to use under the MIT license.			 			 #
# http://www.opensource.org/licenses/mit-license.php 		 #
# 															 #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from html.parser import HTMLParser

class ParserHTML(HTMLParser) :
	"""This class inherits HTMLParser (default python class).
	It receives a tuple of HTML tags to watch and will store all the attributes in those tags.
	It can be passed an HTML string using he feed() method.

	The stored attributes will be in the public list collected_attrs."""

	# sets the instance varible with the tags to look for
	def __init__(self, root_url, tags) :
		super().__init__()

		# instance variables
		self.root_url = root_url
		self.relevant_data = tags
		self.collected_attrs = set()

	# this method will trigger for every opening tag in the HTML string fed to this class
	# it will cross-reference the tags and their attributes with the data provided to the class at
	# instantiation and store the relevant data in collected_attrs variable
	def handle_starttag(self, tag, attrs) :
		if (tag in self.relevant_data) :
			for attr in attrs :
				if (attr[0] in self.relevant_data[tag]) :
					# if the attribute is a URL, do any preparations needed first
					if (self.relevant_data[tag][attr[0]]) :
						value = self.prepareURL(attr[1].lower())
					else :
						value = attr[1].lower()

					# add the item to the final data set
					self.collected_attrs.add(value)

	# do any adjustments to the URL in order for the code to use it
	# returns the adjusted URL
	def prepareURL(self, url) :
		# if the URL starts with a /, i.e., it's a relative link, then add the root_url to the start of it
		if (url.startswith("/")) :
			url = self.root_url + url

		# add the http:// to the start of the URL, if not there already
		if ("http://" not in url and "https://" not in url) :
			url = "http://" + url

		return(url)
