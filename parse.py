
# sample infos 

# var paramsArray = {}
#                        paramsArray["ObjectID"] = "104729337";
#                        paramsArray["ObjectLocation"] = "Bruttisellen";
#                        paramsArray["ObjectZIP"] = "8306";
#                        paramsArray["ObjectStreet"] = "Ringstrasse 24";
#                        paramsArray["ObjectPrice"] = "1620";
#                        paramsArray["ObjectTitle"] = "Chicke Wohnung sucht neuen Mieter";
#                        paramsArray["ObjectPicture"] = "objPicture";
#                        paramsArray["ObjectList"] = 'http://www.homegate.ch/mieten/104729337?oa=false'; 


import requests
import re
import sys
from datetime import datetime
import time
import simplejson
import urllib2

def generate_google_url(origin, destination, time):
	return "http://maps.googleapis.com/maps/api/directions/json?origin="+origin+"&destination="+destination+"&departure_time="+time+"&mode=transit"

def utc(dt):
	return int(time.mktime(dt.timetuple()))

url ="http://www.homegate.ch/mieten/104741983?oa=false"

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

driver = webdriver.Firefox()
driver.get(url)
html = driver.page_source


if "bot like" in html:
	print "we were detected :("
	sys.exit(1)

if "browser" in html:
	print "cookie problems"
	sys.exit(1)


location = re.findall('paramsArray\["ObjectLocation"\]\s+=\s+["\'](.+)["\'];',html)[0]
address = re.findall('paramsArray\["ObjectStreet"\]\s+=\s+["\'](.+)["\'];',html)[0]
zipc = int(re.findall('paramsArray\["ObjectZIP"\]\s+=\s+["\'](.+)["\'];',html)[0])
price = int(re.findall('paramsArray\["ObjectPrice"\]\s+=\s+["\'](.+)["\'];',html)[0])

#TODO urlencode, handle googlemaps
#TODO handle unicode
gmaps = generate_google_url(" ".join([address,location]),"Zurich HB",str(utc(datetime.now()))
json = urllib2.urlopen(gmaps).read()
json = simplejson.load(json)

