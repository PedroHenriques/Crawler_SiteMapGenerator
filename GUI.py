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

import tkinter as tk, tkinter.ttk as ttk, tkinter.messagebox as msgbox, tkinter.font as tkFont, re, math
import ToolTips

class GUI :
	"""This class is responsible for creating, editing and updating all the GUI elements."""

	# class variable: a list with the values that changefreq accepts as valid
	# used in the site map task
	changefreq_values_ = ["", "hourly", "daily", "weekly", "monthly", "yearly", "always", "never"]

	def __init__(self, caller_object, app_window) :
		self.caller_object = caller_object
		self.app_window = app_window

		# update the application window title
		self.updateWindowTitle("")

		# instance variables to store the information of task buttons
		self.task_button_pointers = {}
		self.task_button_imgs = {}

		# create the instance variables to store input data
		self.resetAllVariables(False)

		# store the current app_window width and height
		self.app_window_width = int(self.app_window.winfo_width())
		self.app_window_height = int(self.app_window.winfo_height())

		# set the GUI theme and styles
		self.setTheme()

		# create the main frame
		self.frame_main = ttk.Frame(self.app_window)
		self.frame_main.grid(row=0, column=0, sticky="N,E,S,W")
		# make the only column of this frame occupy the entire width
		self.frame_main.columnconfigure(0, weight=1)
		# make the rows of this frame stretch
		self.frame_main.rowconfigure(2, weight=1)

		# add the main appliation buttons
		self.frame_navribbon = ttk.Frame(self.frame_main)
		self.task_button_imgs["new_proj"] = tk.PhotoImage(file="images/new_proj.gif", width="50", height="50")
		self.task_button_pointers["new_proj"] = ttk.Button(self.frame_navribbon, text="New Project", image=self.task_button_imgs["new_proj"], compound="top", command=self.activateTaskNewProj)
		self.task_button_pointers["new_proj"].grid(row=0, column=0, pady=self.pad_half_rem, padx=self.pad_half_rem)

		self.task_button_imgs["open_proj"] = tk.PhotoImage(file="images/open_proj.gif", width="50", height="50")
		self.task_button_pointers["open_proj"] = ttk.Button(self.frame_navribbon, text="Open Project", image=self.task_button_imgs["open_proj"], compound="top", command=self.activateTaskOpenProj)
		self.task_button_pointers["open_proj"].grid(row=0, column=1, pady=self.pad_half_rem, padx=self.pad_half_rem)

		self.task_button_imgs["delete_proj"] = tk.PhotoImage(file="images/delete_proj.gif", width="50", height="50")
		self.task_button_pointers["delete_proj"] = ttk.Button(self.frame_navribbon, text="Delete Project", image=self.task_button_imgs["delete_proj"], compound="top", command=self.activateTaskDeleteProj)
		self.task_button_pointers["delete_proj"].grid(row=0, column=2, pady=self.pad_half_rem, padx=self.pad_half_rem)

		self.task_button_imgs["crawl"] = tk.PhotoImage(file="images/crawler.gif", width="50", height="50")
		self.task_button_pointers["crawl"] = ttk.Button(self.frame_navribbon, text="Crawl Website", image=self.task_button_imgs["crawl"], compound="top", command=self.activateTaskCrawl)
		self.task_button_pointers["crawl"].grid(row=0, column=3, pady=self.pad_half_rem, padx=self.pad_half_rem)

		self.task_button_imgs["site_map"] = tk.PhotoImage(file="images/site_map.gif", width="50", height="50")
		self.task_button_pointers["site_map"] = ttk.Button(self.frame_navribbon, text="Site Map", image=self.task_button_imgs["site_map"], compound="top", command=self.activateTaskSiteMap)
		self.task_button_pointers["site_map"].grid(row=0, column=4, pady=self.pad_half_rem, padx=self.pad_half_rem)

		self.frame_navribbon.grid(row=0, column=0, sticky="N,E,S,W")

		# create the UI to deal with gathering the website's root URL
		# also contains the button to start the map generation process
		self.frame_inputs = ttk.Frame(self.frame_main)
		self.frame_inputs.grid(row=1, column=0, sticky="N,E,S,W")

		# create the frame where all the task specific elements will go into
		# this frame will have a canvas and a frame inside it
		# the task specific elements will go into the inner frame
		# this structure is needed in order to have a vertical scrollbar
		self.frame_task = ttk.Frame(self.frame_main)
		self.frame_task.grid(row=2, column=0, sticky="N,E,S,W")
		self.frame_task.rowconfigure(0, weight=1)
		self.frame_task.columnconfigure(0, weight=1)

		# add the canvas to frame_task
		self.frame_task_canvas = tk.Canvas(self.frame_task)
		self.frame_task_canvas.grid(row=0, column=0, sticky="N,E,S,W")
		# add the inner frame to frame_task_canvas
		self.frame_task_data = ttk.Frame(self.frame_task_canvas)
		self.frame_task_canvas.create_window(0, 0, window=self.frame_task_data, anchor="nw")

		# set the initial state of the task buttons
		self.setTaskButtons("initial")

		# add an event listener to the root window for a size change
		self.app_window.bind("<Configure>", self.onWindowUpdate)

	# this method creates/resets all variables needed for the GUI operation
	def resetAllVariables(self, reset_frames) :
		# reset the instance variables to store input data
		self.createInputVariables()
		self.createSiteMapVariables()

		# if needed, reset the input and task frames + set the task buttons to the initial setup
		if (reset_frames) :
			# clear the frame of any slaves
			self.clearFrame([self.frame_inputs, self.frame_task_data], -1)
			# remove any scrollbars from the canvas
			self.removeScrollBars()

			# set the initial state of the task buttons
			self.setTaskButtons("initial")

	# triggered everytime the window is resized
	# deals with all the GUI code that needs to run on window resize
	def onWindowUpdate(self, event) :
		# if the event widget is not the app_window bail out
		if (event.widget != self.app_window) :
			return

		# if the app_window hasn't been resized, bail out
		if (int(event.width) == self.app_window_width and int(event.height) == self.app_window_height) :
			return

		# update the current app_window size
		self.app_window_width = int(event.width)
		self.app_window_height = int(event.height)

		# remove the window resize event listener to be able to change the GUI without entering a constant loop
		self.app_window.unbind("<Configure>")

		# store the current base font size
		before_base_font_size = self.gui_font_base["size"]

		# update the font size
		self.setFontSize()

		# calculate the ratio between the base font size before and after adjustment
		font_size_ratio = self.gui_font_base["size"] / before_base_font_size

		# if the base font size changed loop through all widgets on the screen, check if they have grid padding set
		# and if they do, change it's value depending on the new font size
		if (font_size_ratio != 1) :
			# calculate the new padding values
			self.setPaddingValues()

			# start with the main window and go through it's children and their children, and so on
			self.updateChildrenGridPadding(self.app_window, font_size_ratio)

		# re-add an event listener to the root window for a size change
		# will wait for 1s to avoid a constant loop where the font change triggers the resize event
		# and it never stabilizes in a new font size
		# will also do other actions that need to wait for the grid to recalculate all widget sizes and positions
		self.app_window.after(500, self.afterWindowUpdate)

	# this method will be called after xx seconds of onWindowUpdate() returning and will
	# execute any code that needs to wait for the grid manager to readjust all widget's
	# positions and dimensions
	def afterWindowUpdate(self) :
		# if the canvas has a scrollregion config set, and thus has scrollbars visible, adjust them
		if (self.frame_task_canvas.cget("scrollregion") != "") :
			# calculate the new canvas size and adjust scrollregion for the scrollbar
			self.frame_task_canvas.configure(scrollregion=self.frame_task_canvas.bbox("all"))

		# re-add an event listener to the root window for a size change
		self.app_window.bind("<Configure>", self.onWindowUpdate)

	# recursive method responsible for updating the widget's grid padding
	# this method will be called when the font size changes and helps make the
	# GUI's design responsive
	def updateChildrenGridPadding(self, start_widget, font_size_ratio) :
		try :
			# grab start_widget's grid info
			grid_info = start_widget.grid_info()

			# round the font_size_ratio to 2 decimal points
			font_size_ratio = round(font_size_ratio, 2)

			# check if start_widget has any grid padding set
			# and update any of them by the font_size_ratio
			# using round() to limit deviations when resizing the window multiple times
			if ("padx" in grid_info) :
				start_widget.grid_configure(padx=round(float(grid_info["padx"]) * font_size_ratio))

			if ("pady" in grid_info) :
				start_widget.grid_configure(pady=round(float(grid_info["pady"]) * font_size_ratio))

			if ("ipadx" in grid_info) :
				start_widget.grid_configure(ipadx=round(float(grid_info["ipadx"]) * font_size_ratio))

			if ("ipady" in grid_info) :
				start_widget.grid_configure(ipady=round(float(grid_info["ipady"]) * font_size_ratio))
		except Exception as e :
			# this widget isn't managed by the grid manager and thus doesn't have grid_info()
			# in that case tehre are no grid paddings to update, so move along to next code block
			pass

		# loop through the start_widget's children
		for child in start_widget.winfo_children() :
			# update this child's paddings
			self.updateChildrenGridPadding(child, font_size_ratio)

	# this method calculates and, if needed, updates the GUI fonts with a font size
	# based on the current window dimensions
	def setFontSize(self) :
		# based on the window width, determine the font size to use
		if (self.app_window_width < 1045) :
			base_font_size = 10
		elif (self.app_window_width < 1125) :
			base_font_size = 11
		else :
			base_font_size = 12

		# update all fonts with the correct font size
		self.gui_font_base["size"] = base_font_size
		self.gui_font_bold["size"] = base_font_size

	# this method calculates the padding values, based on the current base font size
	# using round() to limit deviations when resizing the window multiple times
	def setPaddingValues(self) :
		self.pad_one_rem = self.gui_font_base["size"]
		self.pad_half_rem = round(self.gui_font_base["size"] * 0.5)

	# this method contains all the code to set the GUI's theme and styles
	def setTheme(self) :
		# create the fonts
		font_family = "Helvetica"
		self.gui_font_base = tkFont.Font(family=font_family)
		self.gui_font_bold = tkFont.Font(family=font_family, weight=tkFont.BOLD)
		self.setFontSize()

		# set the paddings to be used
		self.setPaddingValues()

		# create a new style instance
		gui_style = ttk.Style()

		# set the relevant styles
		gui_style.configure("TLabel", font=self.gui_font_base)
		gui_style.configure("Bold.TLabel", font=self.gui_font_bold)
		gui_style.configure("TEntry", font=self.gui_font_base)
		gui_style.configure("TCombobox", font=self.gui_font_base)
		gui_style.configure("TCheckbutton", font=self.gui_font_base)
		gui_style.configure("Bold.TCheckbutton", font=self.gui_font_bold)
		gui_style.configure("TButton", font=self.gui_font_base)
		gui_style.configure("Primary.TButton", foreground="#00A105", font=self.gui_font_bold)
		gui_style.configure("Stop.TButton", foreground="#FF0000", font=self.gui_font_bold)

	# this method will add scrollbars to the canvas element in frame_task
	def addScrollBars(self) :
		try :
			# add the scrollbars and link them to the canvas elements
			self.task_canvas_vscrollbar = ttk.Scrollbar(self.frame_task, orient="vertical", command=self.frame_task_canvas.yview)
			self.task_canvas_hscrollbar = ttk.Scrollbar(self.frame_task, orient="horizontal", command=self.frame_task_canvas.xview)
			self.frame_task_canvas.configure(yscrollcommand=self.task_canvas_vscrollbar.set, xscrollcommand=self.task_canvas_hscrollbar.set)
			self.task_canvas_vscrollbar.grid(row=0, column=1, sticky="N,S")
			self.task_canvas_hscrollbar.grid(row=1, column=0, sticky="W,E")

			# force a GUI redraw
			self.app_window.update()
			# calculate the new canvas size and adjust scrollregion for the scrollbar
			self.frame_task_canvas.configure(scrollregion=self.frame_task_canvas.bbox("all"))
		except Exception as e :
			# this element doesn't support scrollbars, so do nothing
			self.task_canvas_vscrollbar = None
			self.task_canvas_hscrollbar = None

	# this method will remove scrollbars from the canvas element in frame_task
	def removeScrollBars(self) :
		try:
			self.task_canvas_vscrollbar.grid_remove()
			self.task_canvas_vscrollbar = None
		except AttributeError:
			# there is no vertical scrollbar, so do nothing
			pass

		try:
			self.task_canvas_hscrollbar.grid_remove()
			self.task_canvas_hscrollbar = None
		except AttributeError:
			# there is no horizontal scrollbar, so do nothing
			pass

	# creates/resets the instance variables used to store/control any input data
	def createInputVariables(self) :
		# instance variables used to store information
		self.entry_elems = {}
		self.label_elems = {}
		self.combobox_elems = {}
		self.checkbox_elems = {}
		self.input_button_elems = {}
		self.tk_vars = {}

		# instance variable used to store any gui widgets related to opening folders
		# format: {frame_id : {row # (0 indexed) : {col # (0 indexed) : {widget pointer}}}}
		self.tk_open_folder = {}

		# instance variable used to store any active scrollbars
		self.active_scrollbars = {}

	# creates/resets the instance variables used to store/control site map task data
	def createSiteMapVariables(self) :
		# instance variables used to store site map task's information
		self.sitemap_label_header = [] # format: [col # (0 indexed)][ui element reference]
		self.sitemap_checkbox_elems = [] # format: [row # (0 indexed)][ui element reference]
		self.sitemap_entry_lastmod = [] # format: [row # (0 indexed)][ui element reference]
		self.sitemap_combobox_changefreq = [] # format: [row # (0 indexed)][ui element reference]
		self.sitemap_entry_priority = [] # format: [row # (0 indexed)][ui element reference]

		# instance variables used to store the ToolTips class objects
		self.tooltips_inputs = None
		self.tooltips_header = None

		# instance variables used to control site map task's manipulation of data
		self.sitemap_cur_index = -1 # we haven't grabbed any items yet
		self.sitemap_selected_rows = set()

	# this method clears a frame from all slaves
	def clearFrame(self, frames, reset_vars) :
		# clear any references to relevant input variables
		if (reset_vars == 1) :
			self.createSiteMapVariables()
		elif (reset_vars == 0) :
			self.createInputVariables()

		# loop through each frame
		for frame in frames :
			# clear any pointers to open folder widgets on this frame
			if (frame.winfo_id() in self.tk_open_folder) :
				del self.tk_open_folder[frame.winfo_id()]

			# loop through each slave and destroy them
			for slave in frame.grid_slaves() :
				# clear any pointers to open folder widgets on this slave
				# checked again in case this slave is a frame
				if (slave.winfo_id() in self.tk_open_folder) :
					del self.tk_open_folder[slave.winfo_id()]

				slave.destroy()

	# this method is responsible for setting the state of the task buttons
	def setTaskButtons(self, command) :
		# grab the GUI slaves to the navribbon frame
		slaves = self.frame_navribbon.grid_slaves()

		# if we want the initial state for the buttons
		if (command == "initial") :
			# local set with the keys of the buttons to be active
			active_button = set()
			active_button.add("new_proj")
			active_button.add("open_proj")
			active_button.add("delete_proj")

			# loop every button and set the correct states
			for slave in slaves :
				for item in active_button :
					if (slave == self.task_button_pointers[item]) :
						# this button should be active
						slave.configure(state="normal")

						# break the for loop to prevent the else clause from running
						break
				else :
					# this button should be inactive
					slave.configure(state="disabled")
		elif (command == "disable_all") :
			# in this case, disable all buttons
			# loop every button and set the correct states
			for slave in slaves :
				# this button should be disabled
				slave.configure(state="disabled")
		elif (command == "activate_all" or command == "open_crawled" or command == "crawl_competed") :
			# in this case, activate all buttons
			# loop every button and set the correct states
			for slave in slaves :
				# this button should be active
				slave.configure(state="normal")
		elif (command == "open_not_crawled") :
			# local set with the keys of the buttons to be active
			active_button = set()
			active_button.add("new_proj")
			active_button.add("open_proj")
			active_button.add("delete_proj")
			active_button.add("crawl")

			# loop every button and set the correct states
			for slave in slaves :
				for item in active_button :
					if (slave == self.task_button_pointers[item]) :
						# this button should be active
						slave.configure(state="normal")

						# break the for loop to prevent the else clause from running
						break
				else :
					# this button should be inactive
					slave.configure(state="disabled")

	# this method will activate/disable all GUI elements inside the supplied frame
	def setInputElementsState(self, disable, frame) :
		if (not disable) :
			# activate all
			state = "normal"
		else :
			# disable all
			state = "disabled"

		for slave in frame.grid_slaves() :
			slave.configure(state=state)

	# creates the UI elements for the new project task and sets initial values
	def activateTaskNewProj(self) :
		# clear the frame of any slaves
		self.clearFrame([self.frame_inputs, self.frame_task_data], 0)
		# remove any scrollbars from the canvas
		self.removeScrollBars()

		# create and grid the input widgets
		ttk.Label(self.frame_inputs, text="Project Root URL: ").grid(row=0, column=0, sticky="W", pady=self.pad_half_rem, padx=self.pad_half_rem)
		self.entry_elems["root_url"] = ttk.Entry(self.frame_inputs)
		self.entry_elems["root_url"].grid(row=0, column=1, sticky="W,E", pady=self.pad_half_rem, padx=self.pad_half_rem)
		self.input_button_elems["create_proj"] = ttk.Button(self.frame_inputs, text="Create Project", command=self.caller_object.createProject)
		self.input_button_elems["create_proj"].grid(row=0, column=2, sticky="W,E", pady=self.pad_half_rem, padx=self.pad_half_rem)

		# create and grid the subdomain info widgets
		ttk.Label(self.frame_task_data, style="Bold.TLabel", text="NOTE:").grid(row=0, column=0, sticky="W", pady=self.pad_half_rem, padx=self.pad_half_rem)
		ttk.Label(self.frame_task_data, text="Regarding subdomains, this program can deal with them to some extent.\nIn order to maximize the support for subdomain please insert the root URL in one of the following formats:\n\t- subdomains.domain.ending\n\t- domain.ending/subdomains").grid(row=1, column=0, sticky="W", pady=self.pad_half_rem, padx=self.pad_half_rem)
		ttk.Label(self.frame_task_data, text="As an example, considering the root URL \"pedrojhenriques.com\" with two subdomains, try using one of the following formats:\n\t- subdomain1.subdomain2.pedrojhenriques.com\n\t- pedrojhenriques.com/subdomain1/subdomain2").grid(row=2, column=0, sticky="W", pady=self.pad_half_rem, padx=self.pad_half_rem)
		ttk.Label(self.frame_task_data, text="Restrain from using, for example, the format:\n\t- subdomain1.pedrojhenriques.com/subdomain2").grid(row=3, column=0, sticky="W", pady=self.pad_half_rem, padx=self.pad_half_rem)

	# creates the UI elements for the open project task and sets initial values
	def activateTaskOpenProj(self) :
		# clear the frame of any slaves
		self.clearFrame([self.frame_inputs, self.frame_task_data], 0)
		# remove any scrollbars from the canvas
		self.removeScrollBars()

		# get the list of projects currently created
		projects = self.caller_object.projectList()

		# create the GUI elements
		ttk.Label(self.frame_inputs, text="Please select the project to open: ").grid(row=0, column=0, sticky="W", pady=self.pad_half_rem, padx=self.pad_half_rem)
		self.combobox_elems["open_proj"] = ttk.Combobox(self.frame_inputs, state="readonly", values=projects, height="10")
		self.combobox_elems["open_proj"].grid(row=0, column=1, pady=self.pad_half_rem, padx=self.pad_half_rem)
		self.input_button_elems["open_proj"] = ttk.Button(self.frame_inputs, text="Open", command=lambda: self.caller_object.openProject(self.combobox_elems["open_proj"].get()))
		self.input_button_elems["open_proj"].grid(row=0, column=2, sticky="W,E", pady=self.pad_half_rem, padx=self.pad_half_rem)

	# creates the UI elements for the delete project task and sets initial values
	def activateTaskDeleteProj(self) :
		# clear the frame of any slaves
		self.clearFrame([self.frame_inputs, self.frame_task_data], 0)
		# remove any scrollbars from the canvas
		self.removeScrollBars()

		# get the list of projects currently created
		projects = self.caller_object.projectList()

		# create the GUI elements
		ttk.Label(self.frame_inputs, text="Please select the project to delete: ").grid(row=0, column=0, sticky="W", pady=self.pad_half_rem, padx=self.pad_half_rem)
		self.combobox_elems["delete_proj"] = ttk.Combobox(self.frame_inputs, state="readonly", values=projects, height="10")
		self.combobox_elems["delete_proj"].grid(row=0, column=1, pady=self.pad_half_rem, padx=self.pad_half_rem)
		self.input_button_elems["delete_proj"] = ttk.Button(self.frame_inputs, text="Delete", command=lambda: self.caller_object.deleteProject(self.combobox_elems["delete_proj"].get()))
		self.input_button_elems["delete_proj"].grid(row=0, column=2, sticky="W,E", pady=self.pad_half_rem, padx=self.pad_half_rem)

	# update the project list for the active task
	def updateProjectList(self, active_task) :
		# check if there is a widget for the active_task
		if (active_task in self.combobox_elems) :
			# get the list of projects currently created
			projects = self.caller_object.projectList()

			# update the combobox options
			self.combobox_elems[active_task].configure(values=projects)

	# create a label and an entry widgets for the number of threads to be used
	# returns a pointer to the created widgets
	def createNumThreadElems(self, frame, label_text="") :
		# local var to store the points to the widgets
		res = {}

		# create the label
		res["label"] = ttk.Label(frame, text=label_text)

		# create the entry and store it in the relevant instance variable
		self.entry_elems["num_threads"] = ttk.Entry(frame, width="5")

		return(res)

	# creates the UI elements for the crawl task and sets initial values
	def activateTaskCrawl(self) :
		# clear the frame of any slaves
		self.clearFrame([self.frame_inputs, self.frame_task_data], 0)
		# remove any scrollbars from the canvas
		self.removeScrollBars()

		# create the number of threads elements
		num_thread_widgets = self.createNumThreadElems(self.frame_inputs, "Number of crawlers to be used: ")

		# create this task's GUI elements
		num_thread_widgets["label"].grid(row=0, column=0, sticky="W", pady=self.pad_half_rem, padx=self.pad_half_rem)
		self.entry_elems["num_threads"].grid(row=0, column=1, sticky="W", pady=self.pad_half_rem, padx=self.pad_half_rem)
		self.input_button_elems["run_crawl"] = ttk.Button(self.frame_inputs, text="Run Crawl", command=self.caller_object.crawlSite)
		self.input_button_elems["run_crawl"].grid(row=0, column=2, sticky="W,E", pady=self.pad_half_rem, padx=self.pad_half_rem)

		# set initial value for crawlers
		self.updateNumThreads(self.caller_object.num_threads)

		# grab from the Application class, the count of URLs for the current project
		url_counts = self.caller_object.getURLCounts()

		# create the crawl task GUI elements
		self.createCrawlTaskElems()
		# update the GUI numbers with the current state of the crawl of this project
		self.updateCrawlTaskElems(url_counts["crawled"], url_counts["known"], url_counts["external"], url_counts["failed"])

	# this method deals with changes to GUI elements, of the crawls task, based
	# on the state of the crawl at the moment
	def manageTaskCrawlElems(self, command) :
		if (command == "continued") :
			# we resumed the crawl
			# add the pause button
			self.crawl_pause_button = ttk.Button(self.frame_task_data, style="Stop.TButton", text="Pause Crawl", command=self.pauseTaskCrawl)
			self.crawl_pause_button.grid(row=3, column=0, columnspan=2, sticky="W,E", pady=self.pad_half_rem, padx=self.pad_half_rem)

			# disable all elements in frame_inputs
			self.setInputElementsState(True, self.frame_inputs)
		else :
			# we paused or finished the crawl
			# remove the pause button
			self.crawl_pause_button.grid_remove()
			self.crawl_pause_button = None

			# activate all elements in frame_inputs
			self.setInputElementsState(False, self.frame_inputs)
			# change it's text to better reflect what it will do
			if (command == "paused") :
				# we paused the crawl
				self.input_button_elems["run_crawl"].configure(text="Continue Crawl", style="Primary.TButton")
			elif (command == "completed") :
				# we finished, so go back to the initial text
				self.input_button_elems["run_crawl"].configure(text="Run Crawl", style="TButton")

	# this method handles the process of pausing the crawl task
	def pauseTaskCrawl(self) :
		self.caller_object.paused = True

	# creates the UI elements for the site map task and sets initial values
	def activateTaskSiteMap(self) :
		# clear the frame of any slaves
		self.clearFrame([self.frame_inputs, self.frame_task_data], 0)
		# remove any scrollbars from the canvas
		self.removeScrollBars()

		# instance dictionary with the links between column numbers and what they represent
		self.sitemap_cols_nums = {1 : {"data" : "url", "ui" : "URL"}, 2 : {"data" : "lastmod", "ui" : "Last Modified"}, 3 : {"data" : "changefreq", "ui" : "Change Frequency"}, 4 : {"data" : "priority", "ui" : "Priority"}}
		# instance dictionary with the links between column alias and column numbers
		self.sitemap_cols_alias = {"url" : 1, "lastmod" : 2, "changefreq" : 3, "priority" : 4}

		# instance variable used to store the active tooltip Label
		self.tt_widget = None

		# create this task's input GUI elements
		self.manageTaskSiteMapInputElems("initial")

		# create this task's canvas GUI elements
		self.addSiteMapItemsHeader()

		# add the scrollbars to frame_task_canvas
		self.addScrollBars()

	# this method deals with changes to the GUI elements of the site map task
	# depending on the state of execution at the moment
	def manageTaskSiteMapInputElems(self, command) :
		# check if the temp save file with site map data exists and has data
		tmp_file_exists = self.caller_object.tempSaveSiteMapExists()

		if (command == "initial") :
			# create a frame for the "sitemap_initial_data" inputs and button (grid below)
			frame_sitemap_initial_data = ttk.Labelframe(self.frame_inputs, text="Initial Setup")

			# create a frame for the selected rows data manipulation inputs and buttons (grid below)
			frame_sitemap_selected_rows = ttk.Labelframe(self.frame_inputs, text="Update Selected Rows")

			# create a frame for the other buttons (grid below)
			frame_sitemap_buttons = ttk.Labelframe(self.frame_inputs, text="Actions")
			# line all the buttons in the same vertical space
			frame_sitemap_buttons.rowconfigure(0, weight=1)

			# create a frame to house the last save time and open project directory widgets (grid below)
			frame_sitemap_extras = ttk.Frame(self.frame_inputs)

			# create the tk variable to be linked to the robots checkbox
			self.tk_vars["sitemap_robots"] = tk.IntVar()
			self.tk_vars["sitemap_robots"].set(1)

			# create the number of threads elements
			num_thread_widgets = self.createNumThreadElems(frame_sitemap_initial_data, "Number of threads to used: ")

			# set the GUI elems for the initial_data
			num_thread_widgets["label"].grid(row=0, column=0, sticky="W", pady=self.pad_half_rem, padx=self.pad_half_rem)
			self.entry_elems["num_threads"].grid(row=0, column=1, sticky="W", pady=self.pad_half_rem, padx=self.pad_half_rem)
			self.checkbox_elems["sitemap_use_robots_file"] = ttk.Checkbutton(frame_sitemap_initial_data, text="Use robots.txt", variable=self.tk_vars["sitemap_robots"], onvalue=1, offvalue=0)
			self.checkbox_elems["sitemap_use_robots_file"].grid(row=1, column=0, sticky="W,E", pady=self.pad_half_rem, padx=self.pad_half_rem)
			self.input_button_elems["sitemap_initial_data"] = ttk.Button(frame_sitemap_initial_data, text="Build Initial Data", command=self.caller_object.buildSiteMapData)
			self.input_button_elems["sitemap_initial_data"].grid(row=2, column=0, sticky="W,E", pady=self.pad_half_rem, padx=self.pad_half_rem)

			# set the GUI elems related to selected rows data manipulation
			ttk.Label(frame_sitemap_selected_rows, text=self.sitemap_cols_nums[self.sitemap_cols_alias["lastmod"]]["ui"]).grid(row=0, column=0, sticky="W", pady=self.pad_half_rem, padx=self.pad_half_rem)
			self.entry_elems["sitemap_selected_rows_lastmod"] = ttk.Entry(frame_sitemap_selected_rows, width=15)
			self.entry_elems["sitemap_selected_rows_lastmod"].grid(row=0, column=1, sticky="W", pady=self.pad_half_rem, padx=self.pad_half_rem)
			self.input_button_elems["sitemap_update_selected_lastmod"] = ttk.Button(frame_sitemap_selected_rows, state="disabled", text="Update", command=lambda: self.updateSelectedRows("lastmod"))
			self.input_button_elems["sitemap_update_selected_lastmod"].grid(row=0, column=2, sticky="W,E", pady=self.pad_half_rem, padx=self.pad_half_rem)
			ttk.Label(frame_sitemap_selected_rows, text=self.sitemap_cols_nums[self.sitemap_cols_alias["changefreq"]]["ui"]).grid(row=1, column=0, sticky="W", pady=self.pad_half_rem, padx=self.pad_half_rem)
			self.combobox_elems["sitemap_selected_rows_changefreq"] = ttk.Combobox(frame_sitemap_selected_rows, state="readonly", values=self.changefreq_values_)
			self.combobox_elems["sitemap_selected_rows_changefreq"].grid(row=1, column=1, sticky="W", pady=self.pad_half_rem, padx=self.pad_half_rem)
			self.input_button_elems["sitemap_update_selected_changefreq"] = ttk.Button(frame_sitemap_selected_rows, state="disabled", text="Update", command=lambda: self.updateSelectedRows("changefreq"))
			self.input_button_elems["sitemap_update_selected_changefreq"].grid(row=1, column=2, sticky="W,E", pady=self.pad_half_rem, padx=self.pad_half_rem)
			ttk.Label(frame_sitemap_selected_rows, text=self.sitemap_cols_nums[self.sitemap_cols_alias["priority"]]["ui"]).grid(row=2, column=0, sticky="W", pady=self.pad_half_rem, padx=self.pad_half_rem)
			self.entry_elems["sitemap_selected_rows_priority"] = ttk.Entry(frame_sitemap_selected_rows, width=5)
			self.entry_elems["sitemap_selected_rows_priority"].grid(row=2, column=1, sticky="W", pady=self.pad_half_rem, padx=self.pad_half_rem)
			self.input_button_elems["sitemap_update_selected_priority"] = ttk.Button(frame_sitemap_selected_rows, state="disabled", text="Update", command=lambda: self.updateSelectedRows("priority"))
			self.input_button_elems["sitemap_update_selected_priority"].grid(row=2, column=2, sticky="W,E", pady=self.pad_half_rem, padx=self.pad_half_rem)

			# set the GUI button elems related to file management
			self.input_button_elems["sitemap_save"] = ttk.Button(frame_sitemap_buttons, state="disabled", text="Save Data Values", command=lambda: self.caller_object.processSiteMapFileOperations("save"))
			self.input_button_elems["sitemap_save"].grid(row=0, column=0, sticky="W,E", pady=self.pad_half_rem, padx=self.pad_half_rem)
			self.input_button_elems["sitemap_load"] = ttk.Button(frame_sitemap_buttons, text="Load Data Values", command=lambda: self.caller_object.processSiteMapFileOperations("load"))
			self.input_button_elems["sitemap_load"].grid(row=1, column=0, sticky="W,E", pady=self.pad_half_rem, padx=self.pad_half_rem)
			self.input_button_elems["sitemap_createXML"] = ttk.Button(frame_sitemap_buttons, style="Primary.TButton", state="disabled", text="Create Site Map File", command=lambda: self.caller_object.processSiteMapFileOperations("xml"))
			self.input_button_elems["sitemap_createXML"].grid(row=2, column=0, sticky="W,E", pady=self.pad_half_rem, padx=self.pad_half_rem)

			# grid the local frames
			frame_sitemap_initial_data.grid(row=0, column=0, sticky="N,E,S,W", pady=self.pad_half_rem, padx=self.pad_half_rem)
			frame_sitemap_selected_rows.grid(row=0, column=1, sticky="N,E,S,W", pady=self.pad_half_rem, padx=self.pad_half_rem)
			frame_sitemap_buttons.grid(row=0, column=2, sticky="N,E,S,W", pady=self.pad_half_rem, padx=self.pad_half_rem)
			frame_sitemap_extras.grid(row=1, column=0, columnspan=3, sticky="N,E,S,W", pady=self.pad_half_rem, padx=self.pad_half_rem)

			# set initial value for number of threads
			self.updateNumThreads(self.caller_object.num_threads)

			# if needed, disable the load button
			if (not tmp_file_exists) :
				self.input_button_elems["sitemap_load"].configure(state="disabled")

			# add the labels with the last saved date/time
			self.label_elems["sitemap_save_time"] = ttk.Label(frame_sitemap_extras, text="")
			self.label_elems["sitemap_save_time"].grid(row=0, column=0, sticky="N,W", pady=self.pad_half_rem, padx=self.pad_half_rem)
			# update the label's text with the last save date/time
			self.updateSiteMapSaveTime()

			# add the label with the separator between the "sitemap_save_time" and the open folder widgets
			ttk.Label(frame_sitemap_extras, text=" | ").grid(row=0, column=1, pady=self.pad_half_rem, padx=self.pad_half_rem)

			# add the open project's folder label and button
			self.createOpenFolderElems(self.caller_object.paths["project_folder"], frame_sitemap_extras, 0, 2, "Open project directory: ")

			# create local variables with the list of widgets with tooltips and their text
			tooltip_widgets = []
			tooltip_strings = []
			tooltip_widgets.append(self.entry_elems["num_threads"])
			tooltip_strings.append("In general, the more threads used the faster the data will be processed, although there is a drop off point.\nIf you are uncertain about the number to use, stay between 1 and 8.")
			tooltip_widgets.append(self.checkbox_elems["sitemap_use_robots_file"])
			tooltip_strings.append("Use this project's domain robots.txt (if one exists) to ignore any URLs not intended for indexing by search engines.\nNote that search engines treat robots.txt and sitemap.xml files as separate information. As such it's not mandatory for both files to be consistent on the URLs presented.")
			tooltip_widgets.append(self.input_button_elems["sitemap_initial_data"])
			tooltip_strings.append("Build the list of relevant URLs and assign default values to the several fields.")
			tooltip_widgets.append(self.input_button_elems["sitemap_save"])
			tooltip_strings.append("Save the current data to a temporary file.")
			tooltip_widgets.append(self.input_button_elems["sitemap_load"])
			tooltip_strings.append("Load data from the last saved temporary file.")
			tooltip_widgets.append(self.input_button_elems["sitemap_createXML"])
			tooltip_strings.append("Create the final XML file to be linked to this domain.")
			tooltip_widgets.append(self.entry_elems["sitemap_selected_rows_lastmod"])
			tooltip_strings.append("Change the selected rows \"Last Modified\" field to this value.\nThe date (YYYY-MM-DD) at which the webpage file was last modified.")
			tooltip_widgets.append(self.combobox_elems["sitemap_selected_rows_changefreq"])
			tooltip_strings.append("Change the selected rows \"Change Frequency\" field to this value.\nHow frequently the webpage's content is likely to change.")
			tooltip_widgets.append(self.entry_elems["sitemap_selected_rows_priority"])
			tooltip_strings.append("Change the selected rows \"Priority\" field to this value.\nThe priority of this URL relative to other URLs on your site. Valid values range from 0.0 to 1.0.\nThis value does not affect how your pages are compared to pages on other sites, it only lets the search engines know which pages you deem most important for the crawlers.")

			# instantiate the ToolTips class for these widgets
			self.tooltips_inputs = ToolTips.ToolTips(tooltip_widgets, tooltip_strings, self.gui_font_base)
		elif (command == "working") :
			# set the GUI elems when the site map task is building the initial data, saving the data, loading from a save
			# or creating the XML file
			self.input_button_elems["sitemap_save"].configure(state="disabled")
			self.input_button_elems["sitemap_load"].configure(state="disabled")
			self.input_button_elems["sitemap_createXML"].configure(state="disabled")

			self.input_button_elems["sitemap_update_selected_lastmod"].configure(state="disabled")
			self.input_button_elems["sitemap_update_selected_changefreq"].configure(state="disabled")
			self.input_button_elems["sitemap_update_selected_priority"].configure(state="disabled")
		elif (command == "continued") :
			# set the GUI elems when the site map task has completed the "working" state
			self.input_button_elems["sitemap_save"].configure(state="normal")
			# if needed, disable the load button
			if (tmp_file_exists) :
				self.input_button_elems["sitemap_load"].configure(state="normal")
			self.input_button_elems["sitemap_createXML"].configure(state="normal")

			self.input_button_elems["sitemap_update_selected_lastmod"].configure(state="normal")
			self.input_button_elems["sitemap_update_selected_changefreq"].configure(state="normal")
			self.input_button_elems["sitemap_update_selected_priority"].configure(state="normal")

			# update the label's text with the last save date/time
			self.updateSiteMapSaveTime()

	# responsible for processing event listener triggers from the site map task's header cols
	def sitemapHeaderEventHandling(self, event) :
		# remove any tooltips currently being shown on this widget
		self.tooltips_header.hideToolTips(event)

		# grab a reference to the event widget
		widget_ref = event.widget
		# get the widget's grid information
		widget_grid_info = widget_ref.grid_info()
		# store the widget's row and column in the grid
		widget_col = widget_grid_info["column"]

		# local variable used to store the new sorting info
		new_sort = []

		# check if the selected column is already the primary sorting column
		if (self.sitemap_cols_nums[widget_col]["data"] == self.caller_object.site_map_items_sorting[0][0]) :
			# the selected column is already the primary sorting column, so flip its order
			# start by grabing a copy of the current sort info
			new_sort = self.caller_object.site_map_items_sorting.copy()
			# flip the primary sorting column order
			new_sort[0][1] = not new_sort[0][1]
		else :
			# the selected column is a new primary sorting column, add it
			# use ASC as the default order
			new_sort.append([self.sitemap_cols_nums[widget_col]["data"], False])

			# check if the selected column is the URL column
			if (self.sitemap_cols_alias["url"] != widget_col) :
				# the sorting column is NOT the URL column
				# so add the URL asc as the secondary sorting column
				new_sort.append(["url", False])

		# call for the sorting to be executed
		if (self.caller_object.sortSiteMapItems(new_sort)) :
			# execute GUI changes for a loading site map task
			self.manageTaskSiteMapInputElems("working")

			# the sort was successful, so redraw the items to the screen
			self.redrawSiteMapItems(self.caller_object.site_map_items)

			# update the arrows in the table header of the GUI
			self.updateSortArrows()

			# update the button's state
			self.manageTaskSiteMapInputElems("continued")
		else :
			# the sort failed, give feedback to user
			self.showErrorMsgBox(title="Sorting Failed", message="An error occured while sorting the data.\nPlease try again.")

	# update the site map task's selected rows with the specified "last modified" value
	def updateSelectedRows(self, col_alias) :
		# make sure we have, at least, 1 row selected
		if (len(self.sitemap_selected_rows) == 0) :
			# no rows selected, give feedback and bail out
			self.showErrorMsgBox(title="Operation Failed", message="There are no rows selected to be updated.\nPlease select, at least, 1 row from the list below before atempting to update a value.")
			return

		# get the new input value
		if (col_alias == "lastmod") :
			new_value = self.entry_elems["sitemap_selected_rows_lastmod"].get()
		elif (col_alias == "changefreq") :
			new_value = self.combobox_elems["sitemap_selected_rows_changefreq"].get()
		elif (col_alias == "priority") :
			new_value = self.entry_elems["sitemap_selected_rows_priority"].get()

		# strip any extra whitespaces
		new_value = new_value.strip()

		# determine the column number
		col_num = self.sitemap_cols_alias[col_alias]

		# validate and process the new value
		if (self.validateSiteMapValue(self.sitemap_cols_nums[col_num]["data"], new_value)) :
			# the date inserted is valid -> update the selected rows

			# make a copy of the currently selected rows
			selected_rows = self.sitemap_selected_rows.copy()

			# loop through each of the selected rows
			for row in selected_rows :
				# update the row's data
				self.caller_object.site_map_items[row - 1][self.sitemap_cols_nums[col_num]["data"]] = new_value

			# check if a save to file is needed
			self.caller_object.saveSiteMapData(True)

			# redraw the data to the screen
			self.redrawSiteMapItems(self.caller_object.site_map_items)

			# reselect the rows that were selected before the redraw
			for row in selected_rows :
				self.sitemap_checkbox_elems[row - 1].invoke()

			# all done -> give feedback to user
			self.showInfoMsgBox(title="Update Completed", message=str(len(selected_rows)) + " rows were updated.")
		else :
			# set the correct message
			if (col_alias == "lastmod") :
				message = "The date inserted as " + self.sitemap_cols_nums[col_num]["ui"] + " for the selected rows is not valid.\n\nPlease either leave the field empty or insert a date in the format YYYY-MM-DD."
			elif (col_alias == "changefreq") :
				message = "The value inserted as " + self.sitemap_cols_nums[col_num]["ui"] + " for the selected rows is not valid.\n\nPlease either leave the field empty or insert a value from the provided list."
			elif (col_alias == "priority") :
				message = "The value inserted as " + self.sitemap_cols_nums[col_num]["ui"] + " for the selected rows is not valid.\n\nPlease either leave the field empty or insert a decimal number between 0.0 and 1.0."

			self.showErrorMsgBox(title="Invalid Value", message=message)

	# changes the text from the label with the date/time of the last time the site map data was saved
	# to th temp file
	def updateSiteMapSaveTime(self) :
		text = "Time of last save: "

		# ask the Application class for the time stamp with the last modified of the temp file
		time = self.caller_object.lastSiteMapSaveTime()

		# process the result
		if (time == "") :
			# the file doesn't exist
			text += "Never"
		else :
			# add the time
			text += time

		self.label_elems["sitemap_save_time"].configure(text=text)

	# returns a boolean with the current value of the "use robots.txt file" checkbutton
	def getRobotsUse(self) :
		return(bool(self.tk_vars["sitemap_robots"].get()))

	# sets the value for the number of threads entry GUI element
	def updateNumThreads(self, value) :
		self.entry_elems["num_threads"].insert(0, value)

	# returns the current value in the num crawlers entry GUI element
	# raises ValueError exception if the value can't be cast to Int
	def getNumThreads(self) :
		try :
			return(int(self.entry_elems["num_threads"].get()))
		except ValueError :
			raise

	# returns the current value in the root URL entry GUI element
	def getRootURL(self) :
		return(self.entry_elems["root_url"].get())

	# creates all the UI elements to show the results of the crawl task
	def createCrawlTaskElems(self) :
		# create the UI to display the # of pages found and crawled
		ttk.Label(self.frame_task_data, text="Successfully crawled ").grid(row=0, column=0, sticky="W", pady=self.pad_half_rem, padx=self.pad_half_rem)
		self.label_elems["crawled"] = ttk.Label(self.frame_task_data, text="0")
		self.label_elems["crawled"].grid(row=0, column=1, sticky="W", pady=self.pad_half_rem, padx=self.pad_half_rem)
		ttk.Label(self.frame_task_data, text=" webpages of ").grid(row=0, column=2, sticky="W")
		self.label_elems["known"] = ttk.Label(self.frame_task_data, text="1")
		self.label_elems["known"].grid(row=0, column=3, sticky="W", pady=self.pad_half_rem, padx=self.pad_half_rem)
		ttk.Label(self.frame_task_data, text=" found.").grid(row=0, column=4, sticky="W", pady=self.pad_half_rem, padx=self.pad_half_rem)

		# show how many failed links we've come across
		ttk.Label(self.frame_task_data, text="Number of failed links: ").grid(row=1, column=0, columnspan="4", sticky="W", pady=self.pad_half_rem, padx=self.pad_half_rem)
		self.label_elems["failed"] = ttk.Label(self.frame_task_data, text="0")
		self.label_elems["failed"].grid(row=1, column=4, sticky="W", pady=self.pad_half_rem, padx=self.pad_half_rem)

		# show how many external links we've found
		ttk.Label(self.frame_task_data, text="Number of external links found: ").grid(row=2, column=0, columnspan="4", sticky="W", pady=self.pad_half_rem, padx=self.pad_half_rem)
		self.label_elems["external"] = ttk.Label(self.frame_task_data, text="0")
		self.label_elems["external"].grid(row=2, column=4, sticky="W", pady=self.pad_half_rem, padx=self.pad_half_rem)

	# updates all the elements relating to the crawl task
	def updateCrawlTaskElems(self, crawled, known, external, failed) :
		if ("crawled" in self.label_elems) :
			self.label_elems["crawled"].configure(text=str(crawled))

		if ("known" in self.label_elems) :
			self.label_elems["known"].configure(text=str(known))

		if ("external" in self.label_elems) :
			self.label_elems["external"].configure(text=str(external))

		if ("failed" in self.label_elems) :
			self.label_elems["failed"].configure(text=str(failed))

		self.app_window.update()

	# this method will redraw the entire site map data displayed on the GUI
	# usualy will be called when processing a load button press
	def redrawSiteMapItems(self, items) :
		# clear the frame with the site map data
		self.clearFrame([self.frame_task_data], 1)

		# add the data headers again
		self.addSiteMapItemsHeader()

		# add the new site map data
		if (items != None and len(items) > 0) :
			self.updateSiteMapItems(items)

	# creates the first row of the site map task's data table
	def addSiteMapItemsHeader(self) :
		# local variable with the tooltips text
		tooltip_text = [
			"The date (YYYY-MM-DD) at which the webpage file was last modified.",
			"How frequently the webpage's content is likely to change.",
			"The priority of this URL relative to other URLs on your site. Valid values range from 0.0 to 1.0.\nThis value does not affect how your pages are compared to pages on other sites, it only lets the search engines know which pages you deem most important for the crawlers."
		]

		# create the "select all" checkbutton
		self.tk_vars["sitemap_select_all"] = tk.IntVar()
		self.tk_vars["sitemap_select_all"].set(0)
		ttk.Checkbutton(self.frame_task_data, style="Bold.TCheckbutton", text="All", variable=self.tk_vars["sitemap_select_all"], command=self.selectAllSiteMapItems).grid(row=0, column=0, sticky="W", pady=self.pad_half_rem, padx=self.pad_half_rem)

		# create the header labels and add any tooltip event listeners as needed
		# add en empty index for column 1's checkbox
		self.sitemap_label_header.append(None)

		self.sitemap_label_header.append(ttk.Label(self.frame_task_data, style="Bold.TLabel", text=self.sitemap_cols_nums[1]["ui"]))
		self.sitemap_label_header[-1].grid(row=0, column=1, pady=self.pad_half_rem, padx=self.pad_half_rem)

		self.sitemap_label_header.append(ttk.Label(self.frame_task_data, style="Bold.TLabel", text=self.sitemap_cols_nums[2]["ui"]))
		self.sitemap_label_header[-1].grid(row=0, column=2, pady=self.pad_half_rem, padx=self.pad_half_rem)

		self.sitemap_label_header.append(ttk.Label(self.frame_task_data, style="Bold.TLabel", text=self.sitemap_cols_nums[3]["ui"]))
		self.sitemap_label_header[-1].grid(row=0, column=3, pady=self.pad_half_rem, padx=self.pad_half_rem)

		self.sitemap_label_header.append(ttk.Label(self.frame_task_data, style="Bold.TLabel", text=self.sitemap_cols_nums[4]["ui"]))
		self.sitemap_label_header[-1].grid(row=0, column=4, pady=self.pad_half_rem, padx=self.pad_half_rem)

		# instantiate the ToolTips class for these widgets
		self.tooltips_header = ToolTips.ToolTips(self.sitemap_label_header[2:], tooltip_text, self.gui_font_base)

	# selects/deselects all the rows in site map task's data table
	def selectAllSiteMapItems(self) :
		# check if we want to select or deselect
		if (self.tk_vars["sitemap_select_all"].get() == 0) :
			# deselect any selected rows
			# check if there are any selected rows
			if (len(self.sitemap_selected_rows) == 0) :
				# there are no selected rows, so nothing needs to be done
				return
			else :
				# loop through all currently selected rows and deselect them
				for row in self.sitemap_selected_rows.copy() :
					self.sitemap_checkbox_elems[int(row) - 1].invoke()
		else :
			# select any deselected rows
			# check if there is any deselcted rows
			if (len(self.sitemap_selected_rows) == len(self.sitemap_checkbox_elems)) :
				# there are no deselected rows, so nothing needs to be done
				return
			else :
				# loop through all checkboxes and select any deselcted ones
				for index in range(0, len(self.sitemap_checkbox_elems)) :
					# check if this row is deselected
					if (index + 1 not in self.sitemap_selected_rows) :
						# select it
						self.sitemap_checkbox_elems[index].invoke()

	# updates the site map items displayed on the screen
	def updateSiteMapItems(self, items) :
		# check if there are any new items to draw to screen
		num_items = len(items)
		if (num_items <= self.sitemap_cur_index + 1) :
			# there are no new items
			return

		# draw the new items to the screen
		while self.sitemap_cur_index + 1 < num_items :
			# move to the item after the one we left off
			self.sitemap_cur_index += 1

			# calculate the row number
			# +1 for the 1st row as header
			row_num = self.sitemap_cur_index + 1

			# create the input GUI elements for this item
			# also add the validation binds
			self.sitemap_entry_lastmod.append(ttk.Entry(self.frame_task_data, validate="all"))
			self.sitemap_combobox_changefreq.append(ttk.Combobox(self.frame_task_data, state="readonly", values=self.changefreq_values_, validate="focusout"))
			self.sitemap_entry_priority.append(ttk.Entry(self.frame_task_data, validate="all"))
			# add an extra validation bind to the combobox, to make sure the data is updated when an item is selected
			# this removes the case where the user changes a value and before focusout clicks on a column label to
			# change the sorting, which would not have updated the site_map_items variable with the last change
			# and when the new sort was made it would revert the last changed value
			self.sitemap_combobox_changefreq[-1].bind("<<ComboboxSelected>>", self.validateSiteMapComboboxInput)

			# add the validation callbacks to the entry widgets
			self.sitemap_entry_lastmod[-1].configure(validatecommand=(self.sitemap_entry_lastmod[-1].register(self.validateSiteMapInput), "%W", "%V", "%P"), invalidcommand=(self.sitemap_entry_lastmod[-1].register(self.invalidSiteMapUserInput), "%W"))
			self.sitemap_combobox_changefreq[-1].configure(validatecommand=(self.sitemap_combobox_changefreq[-1].register(self.validateSiteMapInput), "%W", "%V", "%P"), invalidcommand=(self.sitemap_combobox_changefreq[-1].register(self.invalidSiteMapUserInput), "%W"))
			self.sitemap_entry_priority[-1].configure(validatecommand=(self.sitemap_entry_priority[-1].register(self.validateSiteMapInput), "%W", "%V", "%P"), invalidcommand=(self.sitemap_entry_priority[-1].register(self.invalidSiteMapUserInput), "%W"))

			# create this item's checkbutton
			self.sitemap_checkbox_elems.append(ttk.Checkbutton(self.frame_task_data, text=str(row_num)))
			# make sure the checkbutton starts as not checked (before the callback is registered)
			self.sitemap_checkbox_elems[-1].invoke()
			self.sitemap_checkbox_elems[-1].invoke()
			# add the callback to the checkbutton, passing the row as a parameter
			self.sitemap_checkbox_elems[-1].configure(command=(self.sitemap_checkbox_elems[-1].register(self.processSiteMapItemSelection), row_num))

			# prepare the URL text to be displayed. If it exceed the max #characters, truncate it and add ... to the end
			# the max #characters is a % of the window's width
			url_max_len = int(int(self.app_window.winfo_width()) * 0.3)
			url_string = items[self.sitemap_cur_index]["url"][0:url_max_len]
			if (len(items[self.sitemap_cur_index]["url"]) > url_max_len) :
				url_string += "..."

			# draw this item to the screen
			# NOTE: make sure to grid before inserting the value, otherwise the validation will fail due to not finding grid information
			self.sitemap_checkbox_elems[-1].grid(row=row_num, column=0, sticky="W", pady=self.pad_half_rem, padx=self.pad_half_rem)
			ttk.Label(self.frame_task_data, text=url_string).grid(row=row_num, column=1, sticky="W", pady=self.pad_half_rem, padx=self.pad_half_rem)
			self.sitemap_entry_lastmod[-1].grid(row=row_num, column=2, sticky="W", pady=self.pad_half_rem, padx=self.pad_half_rem)
			self.sitemap_entry_lastmod[-1].insert(0, items[self.sitemap_cur_index]["lastmod"])
			self.sitemap_combobox_changefreq[-1].grid(row=row_num, column=3, sticky="W", pady=self.pad_half_rem, padx=self.pad_half_rem)
			self.sitemap_combobox_changefreq[-1].set(items[self.sitemap_cur_index]["changefreq"])
			self.sitemap_entry_priority[-1].grid(row=row_num, column=4, sticky="W", pady=self.pad_half_rem, padx=self.pad_half_rem)
			self.sitemap_entry_priority[-1].insert(0, items[self.sitemap_cur_index]["priority"])

			# force a GUI redraw
			self.app_window.update()

		# calculate the new canvas size and adjust scrollregion for the scrollbar
		self.frame_task_canvas.configure(scrollregion=self.frame_task_canvas.bbox("all"))

		# add sorting event listeners to table header and change their cursor to a hand
		for i in range(0, len(self.sitemap_label_header)) :
			# if there is no widget in this index, move to next index
			if (self.sitemap_label_header[i] == None) :
				continue

			# add sorting event listener
			self.sitemap_label_header[i].bind("<Button-1>", self.sitemapHeaderEventHandling)

			# change cursor
			self.sitemap_label_header[i].configure(cursor="hand2")

	# this method is called when a checkbutton of a site map's item is clicked
	# the instance variable with the currently selected rows will be updated by
	# either adding or removing the clicked item from it
	def processSiteMapItemSelection(self, row) :
		row = int(row)

		# if this row is in the set, then remove it
		if (row in self.sitemap_selected_rows) :
			self.sitemap_selected_rows.remove(row)

			# not all rows are selected, so if the "select all" checkbox is ticked, untick it
			if (self.tk_vars["sitemap_select_all"].get() == 1) :
				self.tk_vars["sitemap_select_all"].set(0)
		else:
			# not in the list, so add it
			self.sitemap_selected_rows.add(row)

			# if all rows are selected, tick the "select all" checkbox
			if (len(self.sitemap_selected_rows) == len(self.sitemap_checkbox_elems)) :
				self.tk_vars["sitemap_select_all"].set(1)

		# force a GUI redraw
		self.app_window.update()

	# this method will validate/invalidate a value from one of the site map task's data inputs
	# returns True if valid, False otherwise
	def validateSiteMapValue(self, col_alias, new_value) :
		# check which type of data we're validating
		if (col_alias == "lastmod") :
			if (new_value != "") :
				re_res = re.fullmatch("(\d{4})-(\d{2})-(\d{2})", new_value)
				if (re_res == None) :
					return(False)
				else :
					# check if the year, month and day are inside reasonable boundaries
					# NOTE: not really checking if the day-month pair is valid
					try :
						if (int(re_res.group(1)) <= 1900 or int(re_res.group(2)) not in range(1,13) or int(re_res.group(3)) not in range(1,32)) :
							# at least 1 of the date parts doesn't have a reasonable value
							return(False)
					except Exception as e :
						return(False)
		elif (col_alias == "changefreq") :
			# check if the new value is one of the allowed ones
			if (new_value not in self.changefreq_values_) :
				return(False)
		elif (col_alias == "priority") :
			if (new_value != "") :
				try :
					# cast to float and round to 1 decimal point
					aux = float(new_value)

					# check if the number is not valid
					if (aux < 0.0 or aux > 1.0) :
						return(False)
				except Exception as e :
					return(False)
		else :
			# not a known input, so invalidate
			return(False)

		# if we reach this point, then it's valid
		return(True)

	# method called by tkinter when a site map task's data input widget changes value
	# i.e., when a character is entered into an entry widget or an item is selected in a combobox
	# this method will NOT give an error message if the value is invalid/incomplete, but
	# will update the the value in site_map_items if the value is completed and valid
	def validateSiteMapComboboxInput(self, event) :
		# get a reference to the widget that changed value
		widget_ref = event.widget
		if (widget_ref == None) :
			# something went wrong, so bail out
			return(False)

		# get the widget's grid information
		widget_grid_info = widget_ref.grid_info()
		if (widget_grid_info == None or "row" not in widget_grid_info or "column" not in widget_grid_info) :
			# something went wrong, so bail out
			return(False)

		# store the widget's row and column in the grid
		widget_row = widget_grid_info["row"]
		widget_col = widget_grid_info["column"]

		# check if the new value is NOT a valid format
		new_value = widget_ref.get().strip()
		if (not self.validateSiteMapValue(self.sitemap_cols_nums[widget_col]["data"], new_value)) :
			# the value is not valid
			return(False)

		# update the site map data
		self.caller_object.site_map_items[widget_row - 1][self.sitemap_cols_nums[widget_col]["data"]] = new_value

		# check if a save to file is needed
		self.caller_object.saveSiteMapData(True)

		# signal that the new value can be accepted
		return(True)

	# method called by tkinter when a site map task's data input widget looses focus (focusout)
	# or a new value is being entered (key)
	# this method will check if the new value is valid or not
	def validateSiteMapInput(self, widget_name, validation_condition, new_value) :
		# only interested in "key" and "focusout" validation conditions
		if (validation_condition not in ("key", "focusout")) :
			# it's a validation condition that doesn't need processing, so validate
			return(True)

		# get a reference to the widget that changed value
		widget_ref = self.app_window.nametowidget(widget_name)
		if (widget_ref == None) :
			# something went wrong, so invalidate
			return(False)

		# get the widget's grid information
		widget_grid_info = widget_ref.grid_info()
		if (widget_grid_info == None or "row" not in widget_grid_info or "column" not in widget_grid_info) :
			# something went wrong, so invalidate
			return(False)

		# store the widget's row and column in the grid
		widget_row = widget_grid_info["row"]
		widget_col = widget_grid_info["column"]

		# check if the new value is NOT a valid format
		new_value = new_value.strip()
		if (not self.validateSiteMapValue(self.sitemap_cols_nums[widget_col]["data"], new_value)) :
			# the value is not valid
			# if the validation condition is "key", then don't call the invalidate method, because
			# the user maight be inserting the value. When the value becomes valid it will be saved
			# and when the user focusout a full validation will be made
			if (validation_condition == "key") :
				return(True)
			else :
				return(False)

		# update the site map data
		self.caller_object.site_map_items[widget_row - 1][self.sitemap_cols_nums[widget_col]["data"]] = new_value

		# check if a save to file is needed
		self.caller_object.saveSiteMapData(True)

		# signal that the new value can be accepted
		return(True)

	# method called by tkinter when a site map task's data input widgets fails it's data validation
	def invalidSiteMapUserInput(self, widget_name) :
		# get a reference to the widget that changed value
		widget_ref = self.app_window.nametowidget(widget_name)
		if (widget_ref == None) :
			# something went wrong, so bail out
			# return the expected value
			return(0)

		# get the widget's grid information
		widget_grid_info = widget_ref.grid_info()
		if (widget_grid_info == None or "row" not in widget_grid_info or "column" not in widget_grid_info) :
			# something went wrong, so bail out
			# return the expected value
			return(0)

		widget_row = widget_grid_info["row"]
		widget_col = widget_grid_info["column"]

		# build the message, depending on which column was changed
		message = "The value inserted for \"" + self.sitemap_cols_nums[widget_col]["ui"] + "\" for row " + str(widget_row) + " is not valid.\n\n"
		if (self.sitemap_cols_nums[widget_col]["data"] == "lastmod") :
			message += "Either leave the field empty or insert a date in the format: YYYY-MM-DD"
		elif (self.sitemap_cols_nums[widget_col]["data"] == "changefreq") :
			message += "Either leave the field empty or insert a value from the provided list"
		elif (self.sitemap_cols_nums[widget_col]["data"] == "priority") :
			message += "Either leave the field empty or insert a decimal number between 0.0 and 1.0\n\nMake sure to use a period (.) as the decimal point indicator"

		# create a msgbox to inform the user that the value inserted is not valid
		# and give info on valid values
		self.showErrorMsgBox(title="Invalid Value", message=message)

		# change the widget's value to the last accepted value
		widget_ref.delete(0, "end")
		widget_ref.insert(0, self.caller_object.site_map_items[widget_row - 1][self.sitemap_cols_nums[widget_col]["data"]])

		# return the expected value
		return(0)

	# this method will update the site map task's table headers with the correct arrows
	# for the current sorting info
	def updateSortArrows(self) :
		# local variables with the up and down arrows
		up_arrow = "↑"
		down_arrow = "↓"

		# loop through all the header columns and add/remove arrows as needed
		for header_col_index in range(0, len(self.sitemap_label_header)) :
			# if this header column is None, then it doesn't support sorting, so skip
			if (self.sitemap_label_header[header_col_index] == None) :
				continue

			# grab a copy of the current widget's text for this header
			label_text = self.sitemap_label_header[header_col_index].cget("text")

			# remove any arrows from this header
			label_text = label_text.replace(up_arrow, "")
			label_text = label_text.replace(down_arrow, "")
			label_text = label_text.strip()

			# loop through the sorting cols, from primary to secondary, and if this header is in use
			# for sorting, add the corresponding arrow
			sorting_cols_len = len(self.caller_object.site_map_items_sorting)
			for sort_col_index in range(0, sorting_cols_len) :
				# grab this index's info
				sort_col_info = self.caller_object.site_map_items_sorting[sort_col_index]

				# check if this sorting column is the current header column
				if (self.sitemap_cols_alias[sort_col_info[0]] != header_col_index) :
					# the columns don't match, so skip to next one
					continue

				# at this point, the columns match
				# if there is only 1 sorting column, simply add the arrow (up or down)
				# start by adding the correct arrow
				if (sort_col_info[1]) :
					# DESC order
					label_text = label_text + "  " + down_arrow
				else :
					# ASC order
					label_text = label_text + "  " + up_arrow

				# if there are more than 1 columns add numbers as well
				if (sorting_cols_len > 1) :
					label_text += str(sort_col_index + 1)

				# update the widget's text
				self.sitemap_label_header[header_col_index].configure(text=label_text)

	# update the GUI after a project is opened (either when creating a new project or opening an existing one)
	def projectOpened(self, root_domain, crawled) :
		# update the task button status
		if (crawled) :
			# this project has already been crawled, so unlock all task buttons
			self.setTaskButtons("open_crawled")
		else :
			# this project has not been crawled, so only unlock the crawl task button
			self.setTaskButtons("open_not_crawled")

		# update the application window title
		self.updateWindowTitle(root_domain)

		# clear the frame with the site map data
		self.clearFrame([self.frame_task_data], -1)

		# add the open project's folder label and button
		self.createOpenFolderElems(self.caller_object.paths["project_folder"], self.frame_task_data, 0, 0, "Open project directory: ")

	# Update the main window's title
	def updateWindowTitle(self, text) :
		if (text != "") :
			text = " - " + text

		# update the application window title
		self.app_window.title("Website Analyzer" + text)

	# this method will create a label and a btton that when pressed will open the user's OS
	# default browsing program on the path location
	# the label will be grid inside frame at row and col
	# the button will be grid inside frame at row and col + 1
	def createOpenFolderElems(self, path, frame, row, col, text) :
		# check if there are already open directory gui elements on the given frame, row and col
		frame_id = frame.winfo_id()
		if (frame_id in self.tk_open_folder and row in self.tk_open_folder[frame_id] and col in self.tk_open_folder[frame_id][row]) :
			# there is already an open directory widget at these coordinates
			# so update the label's text and the button's command
			self.tk_open_folder[frame_id][row][col]["label"].configure(text=text)
			self.tk_open_folder[frame_id][row][col]["button"].configure(command=lambda: self.caller_object.openFolder(path))
		else :
			# if needed create the necessary dummy data in self.tk_open_folder to facilitate the storing
			# of the pointers to th relevant widgets below
			if (frame_id not in self.tk_open_folder) :
				self.tk_open_folder[frame_id] = {row : {col : {}}}
			elif (row not in self.tk_open_folder[frame_id]) :
				self.tk_open_folder[frame_id][row] = {col : {}}
			elif (col not in self.tk_open_folder[frame_id][row]) :
				self.tk_open_folder[frame_id][row][col] = {}

			# create the label and button
			self.tk_open_folder[frame_id][row][col]["label"] = ttk.Label(frame, text=text)
			self.tk_open_folder[frame_id][row][col]["img"] = tk.PhotoImage(file="images/open_dir.gif", width="20", height="20")
			self.tk_open_folder[frame_id][row][col]["button"] = ttk.Button(frame, image=self.tk_open_folder[frame_id][row][col]["img"], command=lambda: self.caller_object.openFolder(path))

			# grid the label and button
			self.tk_open_folder[frame_id][row][col]["label"].grid(row=row, column=col, sticky="W", pady=self.pad_half_rem, padx=self.pad_half_rem)
			self.tk_open_folder[frame_id][row][col]["button"].grid(row=row, column=col + 1, sticky="W,E", pady=self.pad_half_rem, padx=self.pad_half_rem)

	# show info messagebox to user
	def showInfoMsgBox(self, message, title) :
		msgbox.showinfo(icon="info", message=message, title=title)

	# show error messagebox to user
	def showErrorMsgBox(self, message, title) :
		msgbox.showerror(icon="error", message=message, title=title)
