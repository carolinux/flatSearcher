from selenium import webdriver
import sys
import re
import time
import unicodedata
# usage: python form.py url_of_invididual_listing_on homegate

def asciify(x):
	return unicodedata.normalize('NFD', x).encode('ascii', 'ignore')

def submit(url):
	driver = webdriver.Firefox()
	driver.get(url)
	time.sleep(5)
	html = driver.page_source

	location = re.findall('paramsArray\["ObjectLocation"\]\s+=\s+["\'](.+)["\'];', html)[0]
	address = re.findall('paramsArray\["ObjectStreet"\]\s+=\s+["\'](.+)["\'];', html)[0]

	msg = """Ich bin interessiert an der Wohnung an der {}. Ich freue mich auf Ihre Rueckmeldung bezueglich einem Besichtigungstermin.\n\n
	Vielen Dank""".format(asciify(address)+" "+asciify(location))




	#select gender as female
	try:
		driver.find_element_by_id("interestFormBox:interestForm:genderField:gender:0").click()
	except:
		pass
	# first name
	try:
		driver.find_element_by_id("interestFormBox:interestForm:prenameField:form_prename").send_keys("")
		driver.find_element_by_id("interestFormBox:interestForm:form_lastnameField:form_lastname").send_keys("")
		driver.find_element_by_id("interestFormBox:interestForm:form_addressField:form_address").send_keys("")
		driver.find_element_by_id("interestFormBox:interestForm:interest_zipField:form_zip").send_keys("")
		driver.find_element_by_id("interestFormBox:interestForm:interest_cityField:form_city").send_keys("Zurich")
	except:
		pass
	driver.find_element_by_id("interestFormBox:interestForm:form_phoneField:form_phone").send_keys("")
	driver.find_element_by_id("interestFormBox:interestForm:form_mailField:form_mail").send_keys("")

	driver.find_element_by_id("interestFormBox:interestForm:form_messageField:form_message").send_keys(msg)


	driver.find_element_by_id("interestFormBox:interestForm:interestedMailConf").click()

if __name__=="__main__":
	submit(sys.argv[1])


