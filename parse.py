
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
import json
import urllib2
import urllib
import sys
import os

#sys.setdefaultencoding('iso-8859-1') doesnt werk

HOME_DIR ="/home/carolinux/Projects/flatSearcher/data"

asciify = lambda x:unicodedata.normalize('NFD', x).encode('ascii', 'ignore')

def generate_google_url(origin, destination, time):

    url_args = urllib.urlencode({"origin":origin, "destination":destination, "departure_time":time, "mode":"transit"})
    return "http://maps.googleapis.com/maps/api/directions/json?"+url_args

def utc(dt):
	return int(time.mktime(dt.timetuple()))

url ="http://www.homegate.ch/mieten/104741983?oa=false"

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

driver = webdriver.Firefox()
driver.get(url)
html = driver.page_source

main = driver.current_window_handle




if "bot like" in html:
	print "we were detected :("
	sys.exit(1)

if "cookies" in html:
	print "cookie problems"
	sys.exit(1)

import unicodedata

location = re.findall('paramsArray\["ObjectLocation"\]\s+=\s+["\'](.+)["\'];',html)[0]
address = re.findall('paramsArray\["ObjectStreet"\]\s+=\s+["\'](.+)["\'];',html)[0]
zipc = int(re.findall('paramsArray\["ObjectZIP"\]\s+=\s+["\'](.+)["\'];',html)[0])
price = int(re.findall('paramsArray\["ObjectPrice"\]\s+=\s+["\'](.+)["\'];',html)[0])
location = asciify(location)
address = asciify(address)

phone = re.findall("<span class=\"phoneNumber\">Tel:\s*([0-9\s\+]+)\s*</span>",html)


slug = ''.join(address.split())+"-"+''.join(location.split())
out_dir = os.path.join(HOME_DIR,slug)

if not os.path.exists(out_dir):
    os.mkdir(out_dir)


driver.save_screenshot(os.path.join(out_dir,"screenshot.png")) # screenshot of the whole page :)
# try except?
res = driver.find_element_by_css_selector(".gallery a")
res.click()
handles = driver.window_handles
driver.switch_to_window(handles[-1]) #use handle different from main
i=1
while True:

    try:
        driver.save_screenshot(os.path.join(out_dir,"pic"+str(i)+".png"))
        next = driver.find_element_by_css_selector("#pictureForward")
        next.click()
        i+=1
    except:
        break

driver.switch_to_window(main)



# get phone number
#<span class="phoneNumber">Tel: 044 487 17 47</span>

#TODO autosubmit form that says "o hai ppl from address xx, i wants to visit kkthxbai from selenium at will"
#TODO Save infos in csv
#TODO Handle case where phone/photos is missing


important_locations = ["Zurich HB","Oerlikon Zurich","Wetzikon HB"]

# for each location
gmaps = generate_google_url(" ".join([address,location]),important_locations[0],utc(datetime.now()))
directions = json.load(urllib2.urlopen(gmaps))
total_dist = directions["routes"][0]["legs"][0]["distance"]
duration = directions["routes"][0]["legs"][0]["duration"]
steps = directions["routes"][0]["legs"][0]["steps"]
summary = []
for step in steps:

    if "transit_details" in step:
        line = step["transit_details"]["line"]["short_name"]
        summary.append(step["html_instructions"]+","+line)
    else:
        meters = step["distance"]["value"]
        summary.append(step["html_instructions"]+", "+str(meters)+"m")

