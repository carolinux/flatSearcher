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


import re
from datetime import datetime
import time
import json
import urllib2
import urllib
import sys
import os
import time
import unicodedata  #sys.setdefaultencoding('iso-8859-1') doesnt werk
from selenium import webdriver
import random
import traceback

HOME_DIR = "/home/carolinux/Projects/flatSearcher/data"

asciify = lambda x: unicodedata.normalize('NFD', x).encode('ascii', 'ignore')


def generate_google_url(origin, destination, time):
    url_args = urllib.urlencode(
        {"origin": origin, "destination": destination, "departure_time": time,
         "mode": "transit"})
    return "http://maps.googleapis.com/maps/api/directions/json?" + url_args

def get_id(url):
    return re.findall("([0-9]+)",url)[0]

def utc(dt):
    return int(time.mktime(dt.timetuple()))

def print_summary(summary,newline='\n'):
    res=""
    for line in summary:
        res+=asciify(line)+newline
    return res+newline


def parse(driver, url, force_update=False):
    os.mkdir(os.path.join(HOME_DIR,get_id(url)))


    #driver.get(url)
    html = driver.page_source
    #return

    main = driver.current_window_handle

    if "bot like" in html:
        print "we were detected :("
        sys.exit(1)

    if "cookies" in html:
        print "cookie problems"
        sys.exit(1)

    location = \
    re.findall('paramsArray\["ObjectLocation"\]\s+=\s+["\'](.+)["\'];', html)[
        0]
    address = \
    re.findall('paramsArray\["ObjectStreet"\]\s+=\s+["\'](.+)["\'];', html)[0]
    zipc = int(
        re.findall('paramsArray\["ObjectZIP"\]\s+=\s+["\'](.+)["\'];', html)[
            0])
    price = int(
        re.findall('paramsArray\["ObjectPrice"\]\s+=\s+["\'](.+)["\'];', html)[
            0])
    location = asciify(location)
    address = asciify(address)

    phone = re.findall(
        "<span class=\"phoneNumber\">Tel:\s*([0-9\s\+]+)\s*</span>", html)[0]
    avail =  re.findall("gbar:(.{5,20})</p>",html)[0]

    slug = ''.join(address.split()) + "-" + ''.join(location.split())
    out_dir = os.path.join(HOME_DIR, slug)

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    else:
        print "Have already seen this"
        if not force_update:
            return

    driver.save_screenshot(os.path.join(out_dir,
                                        "screenshot.png"))  # screenshot of the whole page :)
    # try except?
    res = driver.find_element_by_css_selector(".gallery a")
    res.click()
    handles = driver.window_handles
    driver.switch_to_window(handles[-1])  #use handle different from main
    i = 1
    while True:

        try:
            driver.save_screenshot(
                os.path.join(out_dir, slug + "-pic" + str(i) + ".png"))
            next = driver.find_element_by_css_selector("#pictureForward")
            next.click()
            i += 1
            time.sleep(3)
        except:
            break

    driver.close()
    driver.switch_to_window(main)
    #driver.quit()



    # get phone number
    #<span class="phoneNumber">Tel: 044 487 17 47</span>

    #TODO autosubmit form that says "o hai ppl from address xx, i wants to visit kkthxbai from selenium at will"
    #How? python submit ../foldur/ (then it knows where to go)
    #TODO Handle case where phone/photos is missing and you should only use the form
    #TODO Handle besichtigung termins
    #TODO parse search results


    important_locations = ["Zurich HB", "Oerlikon Zurich", "Wetzikon HB"]
    summaries = {}

    # for each location
    for i in range(len(important_locations)):
        print "Getting directions to "+important_locations[i]
        try:
            gmaps = generate_google_url(" ".join([address, location]),
                                        important_locations[i], utc(datetime.now()))
            directions = json.load(urllib2.urlopen(gmaps))
            total_dist = directions["routes"][0]["legs"][0]["distance"]
            duration = directions["routes"][0]["legs"][0]["duration"]
            steps = directions["routes"][0]["legs"][0]["steps"]
            summary = []
            summary.append("Total duration:"+duration["text"])
            for step in steps:

                if "transit_details" in step:
                    line = step["transit_details"]["line"]["short_name"]
                    summary.append(step["html_instructions"] + "," + line)
                else:
                    meters = step["distance"]["value"]
                    summary.append(
                        step["html_instructions"] + ", " + str(meters) + "m")
            summaries[important_locations[i]] = summary
            time.sleep(2)
        except Exception,e:
            print e
            continue

            #import ipdb;ipdb.set_trace();


    print "Parsed "+address+" "+location

    f = open(os.path.join(out_dir, "info.csv"),"w")
    f2 = open(os.path.join(out_dir,"info.html"),"w")
    write_info_page(f2,summaries,url,address,location,phone,price,avail)
    f2.close()

    f.write("url|address|phone|price|available_from|termin\n")
    f.write("|".join([url, address + " " + location, str(phone), str(price),str(avail)]))
    f.write("\n\n")
    for loc in summaries.keys():
        f.write(loc+":"+print_summary(summaries[loc]))
    f.close()
def exc():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    print "*** print_tb:"
    traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
    print "*** print_exception:"
    traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=2, file=sys.stdout)
    print "*** print_exc:"
    traceback.print_exc()
    print "*** format_exc, first and last line:"
    formatted_lines = traceback.format_exc().splitlines()
    print formatted_lines[0]
    print formatted_lines[-1]
    print "*** format_exception:"
    print repr(traceback.format_exception(exc_type, exc_value,
                                          exc_traceback))
    print "*** extract_tb:"
    print repr(traceback.extract_tb(exc_traceback))
    print "*** format_tb:"
    print repr(traceback.format_tb(exc_traceback))
    print "*** tb_lineno:", exc_traceback.tb_lineno

def parse_serps(url):
    driver = webdriver.Firefox()
    driver.get(url)
    html = driver.page_source
    REGEX = "http://www.homegate.ch/mieten/[0-9]{9,10}"
    urls = re.findall(REGEX,html)
    urls = set(urls)
    print "Houses to look at:",len(urls)

    #return
    #print urls
    #import ipdb;ipdb.set_trace()
    #driver.close()
    looked = 0
    skip = 0
    looked_at = {}
    prevLooked=-1
    while looked<len(urls):
        print looked, prevLooked

        if looked == prevLooked:
            driver.back()

        prevLooked = looked

        print "Looked at "+str(looked)+" pages"
        elems =  driver.find_elements_by_css_selector("a")
        print "found "+str(len(elems))+" links"
        print "on page ",driver.title
        for i,elem in enumerate(elems):

            url = elem.get_attribute("href")
            if url is None:
                continue
            try:
                if not re.match(REGEX,url) or url in looked_at.keys():
                    #print url," does not match"
                    continue
            except Exception,e:
                print url
                continue
            print get_id(url)
            looked_at[url]=True
            prevLooked = looked
            looked+=1

            #import ipdb;ipdb.set_trace()
            if os.path.exists(os.path.join(HOME_DIR,get_id(url))):
                print "already seen this one"
                continue
            if(i>=skip):
                time.sleep(random.randint(8,20))
                print url
                try:
                    elem.click()
                    parse(driver,url)
                    driver.back();
                    time.sleep(4);


                except Exception,e:
                    #exc()
                    print e
                    print url+" not parseable, continuing"
                    break
            break
    #TODO next pages
    # http://www.homegate.ch/mieten/wohnung-und-haus/bezirk-andelfingen/trefferliste?ao=&oa=false&am=&a=default&ep=4&tab=list&incsubs=default&l=default&fromItem=ctn_zh&be=&cid=4422482&tid=1
    # <span class="picturePreviewInactive">4</span>
    #look for link with ep=3

    #TODO what's it mean when it gets stuck, how to wait for page load
    #TODO auto e-mail.. maybe

    print "Parsed all :)"
    driver.quit()
    sys.exit(0)

def write_info_page(f,summaries,url,address,location,phone,price,avail):
    f.write("url|address|phone|price|available_from|termin<br>")
    f.write("|".join([url, address + " " + location, str(phone), str(price),str(avail)]))
    f.write("<br><br>")
    for loc in summaries.keys():
        f.write("<b>"+loc+"</b>:"+print_summary(summaries[loc],newline="<br>"))
    f.write("<a href=\""+url+"\">Visit on homegate</a>")


def main():
    #test
    parse_serps("http://www.homegate.ch/mieten/wohnung-und-haus/bezirk-andelfingen/trefferliste?mn=ctn_zh&ao=&oa=false&am=&tab=list&incsubs=default&fromItem=ctn_zh&be=&tid=1")
    #Zurich
    #parse_serps("http://www.homegate.ch/mieten/wohnung-und-haus/bezirk-zuerich/trefferliste?a=default&tab=list&l=default&av=01.10.2014&oa=false&ao=&am=&ep=1&ac=2.5&ad=3.0&incsubs=default&ag=1300&fromItem=ctn_zh&ah=1900&be=&cid=4293106&tid=1")
    #parse("http://www.homegate.ch/mieten/104580007?oa=false")
    #Uster
    #parse_serps("http://www.homegate.ch/mieten/wohnung-und-haus/bezirk-uster/trefferliste?a=default&tab=list&l=default&av=01.10.2014&oa=false&ao=&am=&ep=1&ac=2.5&ad=3.5&incsubs=default&ag=1400&fromItem=ctn_zh&ah=2000&be=&cid=4302607&tid=1")


if __name__=="__main__":
    main()

