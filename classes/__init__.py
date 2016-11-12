# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#															  #
# Python Crawler and Site Map Generator v1.2.1				  #
#															  #
# Copyright 2016, PedroHenriques 							  #
# http://www.pedrojhenriques.com 							  #
# https://github.com/PedroHenriques 						  #
# 															  #
# Free to use under the MIT license.			 			  #
# http://www.opensource.org/licenses/mit-license.php 		  #
# 															  #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import os

# list with the files to be imported when "from package import *" is called
__all__ = []

# grab the list of contents in this directory
dir_path = os.path.dirname(os.path.realpath(__file__))
dir_contents = os.listdir(dir_path)

# find all the python files
for item in dir_contents :
	# ignore this file
	if (item == "__init__.py") :
		continue

	# check if this item is a file
	if (not os.path.isfile(dir_path + "\\" + item)) :
		# it's not a file, so ignore
		continue

	# check if it's a python file
	if (not item.endswith(".py")) :
		# it isn't, so ignore
		continue

	# at this point this item is a python file, so add it to __all__
	# not including the ".py"
	__all__.append(item[:-3])
