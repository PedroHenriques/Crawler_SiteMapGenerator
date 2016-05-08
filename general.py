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

import os, xml.etree.ElementTree as ET

# general method for creating/opening and editing files
def writeToFile(file_path, mode, content) :
	# TODO: add try/catch block
	file_object = open(file_path, mode, encoding="utf-8")
	file_object.write(content)
	file_object.close()
	print(file_path + " in mode \"" + mode + "\"")

# method used to save url set() to a file
def saveSetToFile(path, mode, urls) :
	content = ""

	for url in urls :
		content += url + "\n"

	writeToFile(path, mode, content)

# method used specificaly to save the site map state to a file
# NOTE: does not create the actual site map
def saveTmpSiteMap(path_cur_project, file_name, mode, items, sorting) :
	# check if the tmp folder exists and if not create it
	if (not os.path.isdir(path_cur_project + "/tmp")) :
		os.mkdir(path_cur_project + "/tmp")

	content = ""

	# add the sorting info to the 1st line
	for item in sorting :
		content += item[0] + ";" + str(int(item[1])) + "||"

	# remove the last ||
	content = content[0:-2]
	# advance to the 2nd line to start adding the data
	content += "\n"

	# add the items
	for item in items :
		content += item["url"] + "||" + item["lastmod"] + "||" + item["changefreq"] + "||" + item["priority"] + "\n"

	writeToFile(path_cur_project + "/tmp/" + file_name, mode, content)

# this method will build the final site map XML file, based on site_map_items
def createSiteMapXML(path_cur_project, site_map_items) :
	# create the site map root node
	xml_root = ET.Element("urlset", {"xmlns" : "http://www.sitemaps.org/schemas/sitemap/0.9"})

	# loop each item in the site map data and build the XML entry
	for item in site_map_items :
		# create the "url" node
		node = ET.SubElement(xml_root, "url")

		# add the "loc" node
		# FIXME: we need to encode some characters (& ' " < >) + encode the entire URL with the server's encoding protocol
		ET.SubElement(node, "loc").text = item["url"]

		# if the lastmod data exists for this item and it's not empty, add it to the XML
		if ("lastmod" in item and item["lastmod"] != "") :
			ET.SubElement(node, "lastmod").text = item["lastmod"]

		# if the changefreq data exists for this item and it's not empty, add it to the XML
		if ("changefreq" in item and item["changefreq"] != "") :
			ET.SubElement(node, "changefreq").text = item["changefreq"]

		# if the priority data exists for this item and it's not empty, add it to the XML
		if ("priority" in item and item["priority"] != "") :
			ET.SubElement(node, "priority").text = item["priority"]

	# create the XML tree
	xml_obj = ET.ElementTree(xml_root)

	# write the XML tree to the XML file
	xml_obj.write(path_cur_project + "/sitemap.xml", encoding="utf-8", xml_declaration=True)


# recursive method that will delete a directory and all its contents
# returns True if successful, False if not
def deleteDir(path) :
	# if the path is NOT a folder or file, return False
	if (not os.path.isdir(path) and not os.path.isfile(path)) :
		return(False)

	# loop through each item in this directory
	for item in os.listdir(path) :
		# build the items full path
		item_path = path + "/" + item

		# if this item is a file, delete it
		if (os.path.isfile(item_path)) :
			os.remove(item_path)
		else :
			# it's a directory, so call this method with the directory's path
			if (not deleteDir(item_path)) :
				# the directory could not be deleted
				return(False)

	# now that we have cleared this directory of items, delete it
	try :
		os.rmdir(path)
	except OSError as e :
		# the directory could not be deleted
		return(False)

	return(True)

# converts a URL from "(www.)?domain.ending/subdomain" format
# to "subdomain.domain.ending" format
def convertFoldersToSubdomain(parsed_url) :
	# remove the port information, if it's present
	port_index = parsed_url.netloc.find(":")
	if (port_index != -1) :
		parsed_url_noport = parsed_url.netloc[:port_index]
	else :
		parsed_url_noport = parsed_url.netloc

	# remove the starting / from parsed_url.path
	aux_url_path = parsed_url.path[1:]

	# remove the "www." from the start of the root url, if it exists
	# leaving the "." in place
	if (parsed_url_noport.startswith("www.")) :
		aux_root_url = parsed_url_noport[3:]
	else :
		aux_root_url = parsed_url_noport

	# return: convert to the form "subdomain.domain.ending"
	return(aux_url_path.replace("/", ".") + aux_root_url)
