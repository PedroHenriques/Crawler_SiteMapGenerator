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

import traceback, threading, queue, os, time, tkinter as tk, subprocess, platform, urllib.parse
import general, GUI, MapGenerator, Crawler

class Application :
	"""This is the application's main class.
	Contains the GUI and handles passing the information to and from the sitemap generator code."""

	# class constant with the default # of threads to use
	DEFAULT_NUM_THREADS_ = 8
	# class constant with #secods between a save of data to files (in automated tasks)
	SAVE_STATE_SECONDS_ = 5
	# class constant with #secods between a save of data to files (in tasks when the user changes an input value)
	SAVE_TMP_FILE_SECONDS_ = 30
	# class constant with #secods between a GUI update (when needed)
	GUI_UPDATE_SECONDS_ = 1

	def __init__(self, app_window) :
		# instance variable containing the # of threads to be used when crawling
		self.num_threads = self.DEFAULT_NUM_THREADS_

		# create the instance variables for data storage
		self.resetDataVariables()

		# instance variable with the path to the projects folder
		self.path_projects = os.getcwd() + "/projects/"

		# instance variables with the partial path to the temp sitemap file
		self.path_tmp_folder = "/tmp/"
		self.file_tmp_save_sitemap = "tmp_save_sitemap.txt"

		# instance variable pointing to an instance of the GUI class
		self.gui = GUI.GUI(self, app_window)

	# this method creates/resets the instance variables used to store the
	# data and their situation for the current project
	def resetDataVariables(self) :
		# instance variable with the currently opened project's data
		self.root_url = ""
		self.root_domain = ""

		# instance variables used by the crawlers to store all URLs
		# that have been found (they are either in the queue or processed)
		# and the URLs that have been crawled already
		self.known_urls = set()
		self.crawled_urls = set()

		# instance variable used by the crawlers to store URLs that were not
		# possible to either access or get the html
		self.failed_urls = set()

		# instance variable used by the crawlers to store URLs pointing
		# to external websites. NOTE: these links will not be crawled!
		self.external_urls = set()

		# instance variable used by the crawlers with the URLs still not crawled
		self.url_queue = set()

		# instance variable used to store the site map items and sorting info
		self.site_map_items = []
		self.site_map_items_sorting = []

	# determined the domain from a URL
	def getDomain(self, url) :
		# parse the URL
		parsed_url = urllib.parse.urlparse(self.root_url)

		# build the domain
		# if the url has a subdomain in the folder format, convert it to the subdomain format
		if (parsed_url.path != "") :
			domain = general.convertFoldersToSubdomain(parsed_url)
		else :
			# remove the port information, if it's present
			port_index = parsed_url.netloc.find(":")
			if (port_index != -1) :
				domain = parsed_url.netloc[:port_index]
			else :
				domain = parsed_url.netloc

			domain += parsed_url.path

		# if the url passed ended with a / remove it
		if (domain.endswith("/")) :
			domain = domain[:-1]

		return(domain)

	# validate root URL
	# return True if valid, False if not valid
	def validateRootURL(self) :
		# strip whitespaces from start and end of the root URL
		self.root_url = self.root_url.strip()

		# add the http:// to the start of the root URL, if not there already
		if (not self.root_url.startswith("http://") and not self.root_url.startswith("https://")) :
			self.root_url = "http://" + self.root_url

		# parse the URL
		parsed_url = urllib.parse.urlparse(self.root_url)

		# check if there a main body to the URL and that there are no queries in the URL
		if (parsed_url.netloc == "" or parsed_url.query != "") :
			# there isn't a main body or there is a query, so fail validation
			return(False)

		# store the tentative final URL
		self.root_url = parsed_url.geturl()

		# local variables used to know if any changes to path were made below and upsate the final URL
		update_url = False
		cur_path = parsed_url.path

		# if the URL ends with "index.[file type]" remove it
		if (parsed_url.path.count(".") > 0) :
			# remove everything after the last /, making sure it doesn't end with a /
			new_path = parsed_url.path[:parsed_url.path.rindex("/")]

			update_url = True
		elif (parsed_url.path.endswith("/")) :
			# remove the ending / from path
			new_path = parsed_url.path[:-1]

			update_url = True

		# if needed, update the path with the changes made above
		if (update_url) :
			self.root_url = self.root_url.replace(cur_path, new_path)

		return(True)

	# this method scans the projects folder and returns a list of all the
	# projects currently created
	def projectList(self) :
		# local variable where the project names will be added
		projects = []

		# loop each item and if it's a directory add it to the list
		for item in os.listdir(self.path_projects) :
			# check if this item is a folder
			if (os.path.isdir(self.path_projects + item)) :
				projects.append(item)

		# return the project list, sorted by alphabetical order
		projects.sort(key=str.lower)
		return(projects)

	# create the folder for a new project
	def createProject(self) :
		# grab the URL inserted by the user on the UI
		self.root_url = self.gui.getRootURL()

		# validate the root URL
		if (not self.validateRootURL()) :
			# the root URL is not valid, so give error
			self.gui.showErrorMsgBox(title="An error occured", message="The root URL inserted is not valid.")
			return

		# get the domain name for the root url
		self.root_domain = self.getDomain(self.root_url)

		# build the folder and file paths for this project
		self.buildFilePaths()

		# check if the project path already exists
		if (os.path.isdir(self.paths["project_folder"])) :
			# the project already exists, so give error
			self.gui.showErrorMsgBox(title="An error occured", message="A project already exists for the inserted root url!")
			return

		# project path doesn't exist, so create the necessary directory and files
		os.mkdir(self.paths["project_folder"])
		general.writeToFile(self.paths["webpages"], "w", "")
		general.writeToFile(self.paths["queue"], "w", self.root_url + "\n")
		general.writeToFile(self.paths["external_links"], "w", "")
		general.writeToFile(self.paths["failed_links"], "w", "")

		# open the newly created project
		self.openProject(self.root_domain)

	# open a project
	def openProject(self, root_domain) :
		# check if the project folder exists
		if (not os.path.isdir(self.path_projects + root_domain)) :
			self.gui.showErrorMsgBox(title="Operation Failed", message="The project folder does not exist.")
			return

		# reset the instance variables used to store the data of the project
		self.resetDataVariables()

		# set the new root domain
		self.root_domain = root_domain

		# build the folder and file paths for this project
		self.buildFilePaths()

		# set the root URL for this project
		self.root_url = self.root_domain
		self.validateRootURL()

		# determine if this project has already been crawled
		crawled = False
		if (os.path.isfile(self.paths["queue"]) and os.path.getsize(self.paths["queue"]) == 0) :
			# the only way the queue.txt file exists and is empty is if all pages have been crawled
			crawled = True

		# do the necessary GUI updates
		self.gui.projectOpened(self.root_domain, crawled)

		# operation completed, show complete message
		self.gui.showInfoMsgBox(title="Operation Completed", message="The project has been successfully opened.")

	# delete a project
	def deleteProject(self, root_domain) :
		path = self.path_projects + root_domain

		# check if the project folder exists
		if (not os.path.isdir(path)) :
			self.gui.showErrorMsgBox(title="Operation Failed", message="The project folder does not exist.")
			return

		# delete the project
		if (general.deleteDir(path)) :
			# if the project selected to be deleted is the currenly opened project, start by closing it
			if (self.root_domain == root_domain) :
				# reset the instance variables used to store the data of the project
				self.resetDataVariables()

				# reset the GUI variables and frames
				self.gui.resetAllVariables(True)

				# update the application window title
				self.gui.updateWindowTitle("")

			# do the necessary GUI updates
			self.gui.updateProjectList("delete_proj")

			# operation completed, show complete message
			self.gui.showInfoMsgBox(title="Operation Completed", message="The project has been successfully deleted.")
		else :
			# couldn't delete the selected project
			self.gui.showErrorMsgBox(title="Operation Failed", message="The project could not be deleted.\nPlease try again.")

	# this method builds the initial version of the site map, using the URLs stored in the .txt file
	# those URLs will be cross-referenced with the robots.txt of the target domain
	def buildSiteMapData(self) :
		# if the current project's URL state variables are not set, do so
		if (len(self.known_urls) == 0) :
			self.setCrawlVariables(True)

		# if the queue isn't empty, then this project hasn't been fully crawled
		# so bail out
		if (len(self.url_queue) != 0) :
			self.gui.showErrorMsgBox(title="Operation Failed", message="The currently opened project hasn't been completely crawled.\n\nPlease do so before generating a site map.")
			return

		# local variable used by the crawlers to control access to the queue
		queue_lock = threading.Lock()
		# local list variable used as the queue, built from the known_urls set
		queue = []
		for item in self.known_urls :
			queue.append(item)
		# sort the queue by URL asc
		queue.sort(key=str.lower, reverse=True)

		# reset the instance variable with the site map data
		self.site_map_items = []
		# reset the instance variable with the site map data's sorting
		# in the form [[col_alias, True/False], [col_alias, True/False]]
		# the default is to sort by url asc
		self.site_map_items_sorting = [["url", False]]

		# local variable used to store all the crawler objects created
		threads = []

		# local variable with the current system date as YYYY-MM-DD
		local_time_aux = time.localtime()
		local_time_str = "{0}-{1}-{2}".format(str(local_time_aux.tm_year), str(local_time_aux.tm_mon).zfill(2), str(local_time_aux.tm_mday).zfill(2))

		# disable all task buttons in the GUI
		self.gui.setTaskButtons("disable_all")
		# execute GUI changes for a building site map task
		self.gui.manageTaskSiteMapInputElems("working")
		# clear any site map data already drawn to the screen
		self.gui.redrawSiteMapItems(None)

		# set the MapGenerator's class variables, to keep all instances in sync
		MapGenerator.MapGenerator.terminate_thread_ = False
		MapGenerator.MapGenerator.queue_ = queue
		MapGenerator.MapGenerator.queue_lock_ = queue_lock
		MapGenerator.MapGenerator.root_url_ = self.root_url
		MapGenerator.MapGenerator.local_time_ = local_time_str
		MapGenerator.MapGenerator.site_map_items_ = self.site_map_items

		# local variables used to control the periodic update of the GUI with
		# the site map items
		last_time_call = time.monotonic()
		gui_update_cooldown = self.GUI_UPDATE_SECONDS_

		# grab the # of threads the user wants to have created
		self.getNumThreads()
		# get from the GUI class the use/nouse of robots.txt file value
		use_robots_file = self.gui.getRobotsUse()

		# instantiate each MapGenerator thread, start it and store the object reference
		for _ in range(self.num_threads) :
			thread = MapGenerator.MapGenerator(use_robots_file)
			thread.start()
			threads.append(thread)

		# loop until all items have been processed
		# (checked after updating UI to make sure it updates with last items processed)
		while True :
			# update the gui update timers
			gui_update_cooldown -= time.monotonic() - last_time_call
			last_time_call = time.monotonic()
			# check if it's time to update the GUI
			if (gui_update_cooldown <= 0) :
				# send the call for the GUI to update the site map items on the screen
				self.gui.updateSiteMapItems(self.site_map_items)

				# reset the gui update cooldown
				gui_update_cooldown = self.GUI_UPDATE_SECONDS_

			# check if all processing is done
			if (len(self.known_urls) == len(self.site_map_items)) :
				# all done
				# send the call for the GUI to update the site map items on the screen
				self.gui.updateSiteMapItems(self.site_map_items)

				# exit loop
				break

			# wait 1 second before checking again
			time.sleep(1)

		# signal all instances of MapGenerator to terminate
		MapGenerator.MapGenerator.terminate_thread_ = True

		# wait for all the MapGenerator instances to terminate
		for t in threads:
			t.join()

		# update the arrows in the table header of the GUI
		self.gui.updateSortArrows()

		# activate all task buttons in the GUI
		self.gui.setTaskButtons("activate_all")
		# execute GUI changes for a completed site map task
		self.gui.manageTaskSiteMapInputElems("continued")

		# show message to user to indicate that the process is complete
		self.gui.showInfoMsgBox(message="The list of webpages for this project has been compiled.\n\nThe values for \"last modified\", \"change frequency\" and \"priority\" have been given default values, based on the best guess of the application.\n\nYou should confirm and, if necessary, change them before requesting the creation of the Site Map file.", title="Operation Completed")

	# sorts the site map items based on the passed column sorting (in a list of lists)
	# the columns should be passed with index=0 being the primary sorting col,
	# index=1 being the secondary sorting col, and so on
	# and for each col there should be an asc/desc bool value (asc=False, desc=True)
	# sort_cols should be in the form [[col_alias, True/False], [col_alias, True/False]]
	# the method returns True if successful, False otherwise
	def sortSiteMapItems(self, new_sort) :
		# try to do the requested sorting
		try:
			# create a copy of the site map items as they are right now
			sorted_data = self.site_map_items.copy()

			# create a reversed copy of new_sort, because we need to execute the sorting
			# from the lowest to primary
			new_sort_rev = new_sort.copy()
			new_sort_rev.reverse()

			# run each sort, starting from the lowest to the primary sorting
			for sort_info in new_sort_rev :
				# sort the data, using for each row the column and asc/desc indicated
				sorted_data.sort(key=lambda data_row: data_row[sort_info[0]], reverse=sort_info[1])
		except Exception as e:
			return(False)

		# if everything went ok, then store the new site map data and sorting
		self.site_map_items = sorted_data.copy()
		self.site_map_items_sorting = new_sort.copy()

		return(True)

	# this method will be called by the GUI whenever the user changes any of the site map's data
	# it will check if the data should be saved to a temp file, based on a timer
	def saveSiteMapData(self, timed) :
		# build the path to the temp file
		file_path = self.paths["project_folder"] + self.path_tmp_folder + self.file_tmp_save_sitemap

		# if the temp file doesn't exist or we want to save now or the last save was longer than the save cooldown
		if (not os.path.isfile(file_path) or not timed or time.time() - os.path.getmtime(file_path) >= self.SAVE_TMP_FILE_SECONDS_) :
			# execute GUI changes for a loading site map task
			self.gui.manageTaskSiteMapInputElems("working")

			# save the current site map data to the temp file
			general.saveTmpSiteMap(self.paths["project_folder"], self.file_tmp_save_sitemap, "w", self.site_map_items, self.site_map_items_sorting)

			# update the button's state
			self.gui.manageTaskSiteMapInputElems("continued")

	# this method returns the last modified time stamp of the temp file with the site map data
	def lastSiteMapSaveTime(self) :
		file_path = self.paths["project_folder"] + self.path_tmp_folder + self.file_tmp_save_sitemap

		# check if the the temp file exists
		if (not os.path.isfile(file_path)) :
			# if it doesn't exist, return empty string
			return("")

		# at this point, the file exists, so grab the modified time stamp
		# local variable with the last modified time stamp
		ts = os.path.getmtime(file_path)
		ts_aux = time.localtime(ts)
		return("{0}-{1}-{2} {3}:{4}:{5}".format(str(ts_aux.tm_year), str(ts_aux.tm_mon).zfill(2), str(ts_aux.tm_mday).zfill(2), str(ts_aux.tm_hour).zfill(2), str(ts_aux.tm_min).zfill(2), str(ts_aux.tm_sec).zfill(2)))

	# this method checks if the temporary save file with site map data exists and has data
	# returns True if the file eists and has data, False otherwise
	def tempSaveSiteMapExists(self, file_path="") :
		# if needed, build the path to the temp file
		if (file_path == "") :
			file_path = self.paths["project_folder"] + self.path_tmp_folder + self.file_tmp_save_sitemap

		# if the temp file doesn't exist or it's empty, return False
		if (not os.path.isfile(file_path) or os.path.getsize(file_path) == 0) :
			return(False)

		# return True if all checks pass
		return(True)

	# this method will populate the site_map_items variable with the data in the site map temp file
	def loadSiteMapData(self) :
		# build the path to the temp file
		file_path = self.paths["project_folder"] + self.path_tmp_folder + self.file_tmp_save_sitemap

		# if the temp file doesn't exist or it's empty, skip
		if (not self.tempSaveSiteMapExists(file_path)) :
			return

		# execute GUI changes for a loading site map task
		self.gui.manageTaskSiteMapInputElems("working")

		# empty the current site map data and sorting info
		self.site_map_items.clear()
		self.site_map_items_sorting.clear()

		# local bool variable to know if we've loaded the sorting info
		first_line = True

		with open(file_path, "r") as f :
			# loop each line
			for line in f :
				# remove any new line characters returned
				line = line.replace("\n", "")
				if (line == "") :
					continue

				# split the line into the several information
				line_parts = line.split("||")

				# if we're on the 1st line, then we have the sorting info
				if (first_line) :
					# loop through each sorting item
					for sorting_item in line_parts :
						if (sorting_item == "") :
							continue

						# split this item into the 2 parts
						sorting_item_parts = sorting_item.split(";")

						# add it to the instance variable
						self.site_map_items_sorting.append([sorting_item_parts[0], bool(int(sorting_item_parts[1]))])

					first_line = False
				else :
					# we're not on the 1st line, so we have sitemap data
					# build this item's data and add it to the site map data variable
					self.site_map_items.append({"url" : line_parts[0], "lastmod" : line_parts[1], "changefreq" : line_parts[2], "priority" : line_parts[3]})

		# update the button's state
		self.gui.manageTaskSiteMapInputElems("continued")

	# this method will be called when the save, load or create XML buttons are pressed
	# it will call the necessary code for the requested operation
	def processSiteMapFileOperations(self, command) :
		if (command == "save") :
			# save the current input values to the temp file
			self.saveSiteMapData(False)

			# give feedback to the user
			self.gui.showInfoMsgBox(title="Data Saved", message="The current state of the data has been saved to a temporary file.")
		elif (command == "load") :
			# execute GUI changes for a loading site map task
			self.gui.manageTaskSiteMapInputElems("working")

			# load from the temp file the input values
			self.loadSiteMapData()

			# update the GUI with the loaded data
			self.gui.redrawSiteMapItems(self.site_map_items)

			# update the arrows in the table header of the GUI
			self.gui.updateSortArrows()

			# update the button's state
			self.gui.manageTaskSiteMapInputElems("continued")

			# give feedback to the user
			self.gui.showInfoMsgBox(title="Data Loaded", message="The data has been updated with the information of the last save.")
		elif (command == "xml") :
			# execute GUI changes for a working site map task
			self.gui.manageTaskSiteMapInputElems("working")

			# save the current input values to the temp file
			# this way the load command will laod the same data that was placed in the XML file
			self.saveSiteMapData(False)

			# we want to create the final site map XML file
			general.createSiteMapXML(self.paths["project_folder"], self.site_map_items)

			# update the button's state
			self.gui.manageTaskSiteMapInputElems("continued")

			# give feedback to the user
			self.gui.showInfoMsgBox(title="Site Map File Created", message="The sitemap.xml file for this project has been created.\n\nThe file has been stored in the project's folder \"" + self.paths["project_folder"] + "\"")

	# returns a dictionary with the number of URL known, crawled, external and failed for the current project
	def getURLCounts(self) :
		counts = {}

		# count
		c_known = len(self.known_urls)
		c_crawled = len(self.crawled_urls)
		c_external = len(self.external_urls)
		c_failed = len(self.failed_urls)

		# if the crawl instance variables aren't set yet, do so
		if (c_known == 0 and c_crawled == 0 and c_external == 0 and c_failed == 0) :
			# set the variables
			self.setCrawlVariables(True)
			# count again
			c_known = len(self.known_urls)
			c_crawled = len(self.crawled_urls)
			c_external = len(self.external_urls)
			c_failed = len(self.failed_urls)

		counts["known"] = c_known
		counts["crawled"] = c_crawled
		counts["external"] = c_external
		counts["failed"] = c_failed

		return(counts)

	# sets instance variables used in the crawl task
	# if read_only is True, the variables will be set based on the files.
	# if False, the treatment will depend on whether the project has been fully crawled already or not
	# if it has, then it will reset to the initial values, else it will set from where we left off
	def setCrawlVariables(self, read_only) :
		# if the folder or any of the files don't exist, show error and return
		if (not os.path.isdir(self.paths["project_folder"]) or not os.path.isfile(self.paths["webpages"]) or not os.path.isfile(self.paths["queue"]) or not os.path.isfile(self.paths["external_links"]) or not os.path.isfile(self.paths["failed_links"])) :
			self.gui.showErrorMsgBox(title="An error occured", message="Some of the required files for this project could not be found.")
			return(False)

		# clear all the sets of past data
		self.known_urls.clear()
		self.crawled_urls.clear()
		self.url_queue.clear()
		self.external_urls.clear()
		self.failed_urls.clear()

		# if not in read_only mode and the queue.txt is empty, then build the variables
		# with the initial values (as if the project was created) to crawl the website again
		if (not read_only and os.path.getsize(self.paths["queue"]) == 0) :
			self.known_urls.add(self.root_url)
			self.url_queue.add(self.root_url)
		else :
			# build the variables based on the file's content
			with open(self.paths["webpages"], "r") as f :
				# loop each line
				for line in f :
					# remove any new line characters returned
					line = line.replace("\n", "")
					if (line == "") :
						continue

					# add this URL to the sets
					self.crawled_urls.add(line)
					self.known_urls.add(line)

			with open(self.paths["queue"], "r") as f :
				# loop each line
				for line in f :
					# remove any new line characters returned
					line = line.replace("\n", "")
					if (line == "") :
						continue

					# add this URL to the sets
					self.url_queue.add(line)
					self.known_urls.add(line)

			with open(self.paths["external_links"], "r") as f :
				# loop each line
				for line in f :
					# remove any new line characters returned
					line = line.replace("\n", "")
					if (line == "") :
						continue

					# add this URL to the set
					self.external_urls.add(line)

			with open(self.paths["failed_links"], "r") as f :
				# loop each line
				for line in f :
					# remove any new line characters returned
					line = line.replace("\n", "")
					if (line == "") :
						continue

					# add this URL to the set
					self.failed_urls.add(line)

		return(True)

	# grabs the number of threads input from the GUI and sets
	# the relevant instance variable
	def getNumThreads(self) :
		# grab the # of threads the user wants to have created
		try :
			self.num_threads = self.gui.getNumThreads()

			#validate the value
			if (self.num_threads < 1) :
				# use default value
				raise(ValueError)
		except ValueError :
			# if int() throws an exception, use default value
			self.num_threads = self.DEFAULT_NUM_THREADS_

	# crawls the inserted website and gathers all the links (just internal or all)
	# the links will be stored in a file inside a folder with the project's name
	def crawlSite(self) :
		# make sure a root URL is set
		if (self.root_url == "") :
			self.gui.showErrorMsgBox(title="An error occured", message="The root URL for this project could not be found.\n\nPlease make sure a project is opened.")
			return

		# grab the # of threads the user wants to have created
		self.getNumThreads()

		# local variables used by the crawlers to control access to the queue
		queue_lock = threading.Lock()

		# local variable used to store all the crawler objects created
		threads = []

		# if the queue is empty, then reset the data to start crawling again
		# NOTE: if we reach ths code, we want to crawl the site
		# either continue an incomplete crawl, or start from scratch
		if (len(self.url_queue) == 0) :
			# this project has been fully crawled before, so reset
			if (not self.setCrawlVariables(False)) :
				# the variables couldn't be set, so bail out
				return

		# update the GUI with the initial values
		self.gui.updateCrawlTaskElems(len(self.crawled_urls), len(self.known_urls), len(self.external_urls), len(self.failed_urls))
		# disable all task buttons in the GUI
		self.gui.setTaskButtons("disable_all")
		# execute GUI changes for a running crawl task
		self.gui.manageTaskCrawlElems("continued")

		# set the crawler's class variables, to keep all crawlers in sync
		Crawler.Crawler.terminate_thread_ = False
		Crawler.Crawler.known_urls_ = self.known_urls
		Crawler.Crawler.crawled_urls_ = self.crawled_urls
		Crawler.Crawler.external_urls_ = self.external_urls
		Crawler.Crawler.failed_urls_ = self.failed_urls
		Crawler.Crawler.queue_ = self.url_queue
		Crawler.Crawler.queue_lock_ = queue_lock
		Crawler.Crawler.root_url_ = self.root_url

		# local variables used to control the periodic save of the queue to a file
		last_time_call = time.monotonic()
		state_save_cooldown = self.SAVE_STATE_SECONDS_

		# instance boolean variable used to exit the loop below if the PAUSE button is pressed
		self.paused = False

		# instantiate each crawler, start it and store the object reference
		for _ in range(self.num_threads) :
			thread = Crawler.Crawler()
			thread.start()
			threads.append(thread)

		# loop until all items have been processed
		# (checked after updating UI to make sure it updates with last items processed)
		while True :
			# update the UI with the URLs crawled and found
			self.gui.updateCrawlTaskElems(len(self.crawled_urls), len(self.known_urls), len(self.external_urls), len(self.failed_urls))

			# update the queue save timers
			state_save_cooldown -= time.monotonic() - last_time_call
			last_time_call = time.monotonic()
			# check if it's time to store the queue in a file
			if (state_save_cooldown <= 0) :
				# save the queue to the file
				general.saveSetToFile(self.paths["queue"], "w", self.url_queue)
				# save the processed URLs to the file
				general.saveSetToFile(self.paths["webpages"], "w", self.crawled_urls)
				# save the external URLs to the file
				general.saveSetToFile(self.paths["external_links"], "w", self.external_urls)
				# save the failed URLs to the file
				general.saveSetToFile(self.paths["failed_links"], "w", self.failed_urls)

				# reset the queue save cooldown
				state_save_cooldown = self.SAVE_STATE_SECONDS_

			# if all processing is done OR the pause button was pressed
			# do final operations and exit loop
			if ((len(self.known_urls) == len(self.crawled_urls) + len(self.failed_urls)) or self.paused) :
				# all done
				# save the queue to the file (to empty it)
				general.saveSetToFile(self.paths["queue"], "w", self.url_queue)
				# save the processed URLs to the file
				general.saveSetToFile(self.paths["webpages"], "w", self.crawled_urls)
				# save the external URLs to the file
				general.saveSetToFile(self.paths["external_links"], "w", self.external_urls)
				# save the failed URLs to the file
				general.saveSetToFile(self.paths["failed_links"], "w", self.failed_urls)

				# exit loop
				break

			# wait 1 second before checking again
			time.sleep(1)

		# signal all instances of the crawler to terminate
		Crawler.Crawler.terminate_thread_ = True

		# wait for all the crawlers to terminate
		for t in threads:
			t.join()

		# do final operations for this method
		if (len(self.known_urls) == len(self.crawled_urls) + len(self.failed_urls)) :
			# the loop ended because the website was completely crawled
			# operation completed, show complete message
			self.gui.showInfoMsgBox(title="Operation Completed", message="The website has been successfully crawled.\n\n" + str(len(self.known_urls)) + " interal webpages found!\n\n" + str(len(self.failed_urls)) + " URLs could not be successfully crawled!\n\n" + str(len(self.external_urls)) + " external webpages found!")

			# update the task buttons' state now that the current project has been crawled
			self.gui.setTaskButtons("crawl_competed")
			# execute GUI changes for a compleated(i.e., paused) crawl task
			self.gui.manageTaskCrawlElems("completed")
		else :
			# the loop ended because the pause button was pressed
			# update the task buttons' state for a not fully crawled project
			self.gui.setTaskButtons("open_not_crawled")
			# execute GUI changes for a paused crawl task
			self.gui.manageTaskCrawlElems("paused")

			# operation paused, show message
			self.gui.showInfoMsgBox(title="Operation Paused", message="The crawl task has been paused.\nYou can continue crawling by clicking the \"Continue Crawl\" button.")

	# builds the paths for a project's files
	def buildFilePaths(self) :
		self.paths = {}

		self.paths["project_folder"] = self.path_projects + self.root_domain
		self.paths["webpages"] = self.paths["project_folder"] + "/webpages.txt"
		self.paths["queue"] = self.paths["project_folder"] + "/queue.txt"
		self.paths["external_links"] = self.paths["project_folder"] + "/external_links.txt"
		self.paths["failed_links"] = self.paths["project_folder"] + "/failed_links.txt"

	# define the method to open a folder using the user's OS default browser
	if (platform.system() == "Windows") :
		def openFolder(self, path) :
			os.startfile(path)
	elif (platform.system() == "Darwin") :
		def openFolder(self, path) :
			subprocess.Popen(["open", path])
	else :
		def openFolder(self, path) :
			subprocess.Popen(["xdg-open", path])

# code that starts the entire application
try:
	# create the application window
	app_window = tk.Tk()
	app_window.minsize(960, 600)
	app_window.state("zoomed")

	app_window.rowconfigure(0, weight=1)
	app_window.columnconfigure(0, weight=1)

	# instantiate the application's main class
	app = Application(app_window)

	# start the GUI event listener loop
	app_window.mainloop()
except Exception as e:
	traceback.print_exc()
	print("\n")
