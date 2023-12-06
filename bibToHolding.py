print("""\n\n
####################################################################################
####################################################################################
#######
#######    Title:	BibToHolding.py
#######    Author:	Henry Steele, Library Technology Services, Tufts University
#######
#######    Purpose:
#######    	This program adds a fixed 541 field from the bib record to
#######    	attached holding records
#######
#######    Input:
#######    	a text file containing a list of MMS ID record numbers, one per line
#######
#######    Output:
#######    	The updated records are written to Alma and recorded in the
#######    	updated_holdings XML file.  Any errors are recorded in
#######    	records_with_errors.txt
#######
####################################################################################
####################################################################################
""")
print("\n\n")

import sys

import requests
import json
import os
import time
import csv
import re
sys.path.append('secrets_local/')
import secrets_local
# Python 3
# import importlib



import sys
import subprocess
# Python 2
reload(sys)
sys.setdefaultencoding('utf8')

#Python 3
# importlib.reload(sys)
# sys.setdefaultencoding('utf8')

import io

# Python 2
from Tkinter import Tk
from tkFileDialog import askopenfilename
from Tkinter import *
# from Tkinter import messagebox

#Python 3

# from tkinter import filedialog
# from tkinter import *


import pymarc as pym
import xml.etree.cElementTree as et


# subprocess.run('PYTHONIOENCODING="UTF-8"')
def update_holding(holding, holding_id, full_holding_string, five_forty_one, mms_id):
    holding.add_field(five_forty_one)
    print("Holding with new field: \n" + str(holding) + "\n\n\n" )
    updated_holding = pym.record_to_xml(holding).decode('utf-8')


    full_holding_string = full_holding_string.decode('utf-8')

    full_updated_holding = re.sub(r'<record>(.+)</record>', updated_holding, full_holding_string)

    print("Updated XML Holding Record: \n" + full_updated_holding + "\n")

    full_updated_holding = full_updated_holding.replace('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', '')

    #success = True



    # faulty_xml = "<holding></holding>"
    #
    # # full_holdings_xml = root.find('holding/holding_id=')
    #
    #
    response = requests.put("https://api-na.hosted.exlibrisgroup.com/almaws/v1/bibs/" + str(mms_id) + "/holdings/" + str(holding_id) + "?apikey=" + secrets_local.bib_api_key, data=full_updated_holding, headers=headers)
    #
    time.sleep(2)
    print(response.content)
    # #
    # #
    # # # response = requests.put("https://api-na.hosted.exlibrisgroup.com/almaws/v1/bibs/" + str(mms_id) + "/holdings/" + str(holding_id) + "?apikey=", data=full_updated_holding, headers=headers)
    # # #
    # # # print(response.content)
    if re.search('<errorsExist>true</errorsExist>', response.content):
        print("Couldn't write back to Alma for MMS ID: " + mms_id + "\n")
        error_file.write("Couldn't write back to Alma for MMS ID: " + mms_id + "\n")
        success = False
    else:
        output_file.write("<MMS_ID_" + mms_id + ">" + full_updated_holding + "</MMS_ID_" + mms_id + ">")

        success = True

    # print(response.content)
    #
    # print(success)
    #
    # sys.exit()
    return success

def getLocations():
    url = "https://api-na.hosted.exlibrisgroup.com/almaws/v1/analytics/reports?apikey=" + secrets_local.analytics_api_key
    limit = "&limit=1000"
    format = "&format=xml"
    path = "&path=%2Fshared%2FTufts+University%2FReports%2FCataloging%2FAdding+541+to+Holdings+Records%2FLocation+Name-Location+Code"

    report = requests.get(url + format + path + limit)

    #print("\nReport Content: \n" + report.content)

    report_outfile = open('Output/list of codes and locations.xml', "w+")

    # report_str = report.content.decode('utf-8')
    report_outfile.write(str(report.content))

    # print("\n\nReport: \n" + report.content)

    report_outfile.close()

    tree = et.ElementTree(et.fromstring(report.content))

    # print("\nTree: " + tree.text + "\n")

    root = tree.getroot()

    print("\nRoot: \n" + str(root.text) + "\n")



    reportDict = {}
    #for element in root.iter('{urn:schemas-microsoft-com:xml-analysis:rowset}Row'):
    # print("\n\nAll Elements: \n" + str(list(root.iter())))

    for element in root.iter():
        library = ""
        code = ""
        description = ""
        if re.match(r'.*Row', element.tag):
            for sub_element in element.iter():
                if re.match(r'.*Column2', sub_element.tag):
                    code = sub_element.text
                if re.match(r'.*Column3', sub_element.tag):
                    description = sub_element.text
                elif re.match(r'.*Column1', sub_element.tag):
                    library = sub_element.text


        if library in reportDict:
            reportDict[library][description] = code
        else:
            reportDict[library] = {}
            reportDict[library][description] = code



    # for c in reportDict:
    # 	c = c.decode('ascii')
    # 	for d in reportDict[c]:
    # 		reportDict[c][d] = reportDict[c][d].decode('ascii')
    for i in reportDict:
        for j in reportDict[i]:
            print("Library: " + str(i) + "; Description: " + str(j)  + "; Code: " + str(reportDict[i][j]) +  "\n")
    return reportDict



oDir = "./Output"
if not os.path.isdir(oDir) or not os.path.exists(oDir):
    os.makedirs(oDir)

mappings = getLocations()

Tk().withdraw()

#Python 2

filename = askopenfilename(title = "Select list of MMS IDs")

#Python 3
# filename = filedialog.askopenfilename(title = "Select list of MMS IDs")

#print(filenameResource)

bibList = []


bibListCounter = 0
with open(filename, 'rb') as file1:
    for line in file1:
        line = line.decode('utf-8')
        line = line.replace("\r\n", "")
        line = line.replace("\n", "")
        bibList.append(line)
        bibListCounter += 1

print("Number of bib records in input file: " + str(bibListCounter) + "\n")

headers = {'Content-Type': 'application/xml'}




errorCount = 0
# mismatchCount = 0
successCount = 0
count_file = open('Success and Error Counts.txt', 'w+')
output_file = open("Output/updated_holdings.xml", "w+")
output_file.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><holdings>')
error_file = open("Output/records_with_errors.txt", "w+")
fiveFortyOneCount = 0

# foutError = open('Output/Parsing Errors.txt', "w+")
for mms_id in bibList:

    print("MMS ID: " + str(mms_id))

    bib_url = r'https://api-na.hosted.exlibrisgroup.com/almaws/v1/bibs/' + str(mms_id) + '?apikey=' + secrets_local.bib_api_key

    holdings_url = r'https://api-na.hosted.exlibrisgroup.com/almaws/v1/bibs/' + str(mms_id) + '/holdings?apikey=' + secrets_local.bib_api_key

    print(bib_url + "\n")
    print("\n" + holdings_url + "\n")
    bib_record = requests.get(bib_url)
    bib_record_str = bib_record.content
    print("\nBib record: " + bib_record_str + "\n")
    attached_holdings = requests.get(holdings_url)

    attached_holdings_str = attached_holdings.content
    print("\nHoldings: " + attached_holdings_str + "\n")

    # Python 2

    unicode_bib_record = unicode(bib_record_str)

    # Python 3

    # unicode_bib_record = str(bib_record_str)
    if re.search('<errorsExist>true</errorsExist>', unicode_bib_record):

        error_file.write("MMS ID " + mms_id + " not in system\n")
        errorCount += 1
        print("MMS ID " + mms_id + " not in system\n")
        continue



    holdings_count_match = re.search(r'holdings\stotal_record_count\="(\d+)"', attached_holdings_str)
    holdingsCount = int(holdings_count_match.group(1))

    if holdingsCount == 0:
        error_file.write("No holdings for MMS ID" + mms_id + "\n")
        print("No holdings for MMS ID" + mms_id + "\n")
        errorCount += 1
        continue


    # Python 2
    unicode_attached_holdings = unicode(attached_holdings_str)

    # Python 3

    # unicode_attached_holdings = str(attached_holdings_str)



    bib_record = pym.parse_xml_to_array(io.StringIO(unicode_bib_record))





    tree_orig = et.ElementTree(et.fromstring(attached_holdings_str))

    root_orig = tree_orig.getroot()
    holdings_xml_string = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><holdings>'
    for attached_holding in root_orig.findall('holding'):

        print("\n\nHolding: " + str(et.tostring(attached_holding))  + "\n")



        holding_id = attached_holding.find('holding_id').text

        print("\nHolding ID: " + str(holding_id) + "\n")

        try:
            holding_record = requests.get("https://api-na.hosted.exlibrisgroup.com/almaws/v1/bibs/" + str(mms_id) + "/holdings/" + str(holding_id) + "?apikey=" + secrets_local.bib_api_key)
        except:
            print("Can't retrieve holding with MMS ID: " + mms_id + " and holding ID: " + str(holding_id) + "\n")
            error_file.write("Can't retrieve holding with MMS ID: " + mms_id + " and holding ID: " + str(holding_id) + "\n")
            errorCount += 1
            continue
        holding_string = holding_record.content.decode('utf-8')

        holding_string = holding_string.replace('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', '')

        holdings_xml_string += holding_string


    holdings_xml_string += "</holdings>"

    # Python 2
    unicode_holdings_xml_string = unicode(holdings_xml_string)

    #Python 3
    # unicode_holdings_xml_string = holdings_xml_string




    b = 1

    tree = et.ElementTree(et.fromstring(unicode_holdings_xml_string))
    root = tree.getroot()

    countList = []
    for five_forty_one in bib_record[0].get_fields('541'):

        found541 = False
        fiveFortyOneCount += 1
        subfield_3 = five_forty_one['3']
        # if not subfield_3 in all541:
        # 	all541.append(subfield_3)
        print("\n\nRepeated 541 subfield 3: \n" + str(subfield_3) + "\n\n")
        print("\n\n541: \n" + str(five_forty_one) + "\n\n")

        try:
            location_541_match = re.search(r'^(.+Library|TISCH|HHSL|MUSIC|GINN|VET|Tisch|Ginn|Music|Vet|Hirsh)[ ]?(.+)?([ ]print)?[ ]+copy', subfield_3, re.IGNORECASE)
            library_541 = location_541_match.group(1)
            # library_541 = library_541.encode('utf-8', 'replace').decode()
        except:
            print("Library or location in 541 for MMS ID: " + str(mms_id) + " and holding ID: " + str(holding_id) + " is not retrievable or is not an expected value\n")
            error_file.write("Library or location in 541 for MMS ID: " + str(mms_id) + " is not retrievable or is not an expected value\n")
            errorCount += 1
            continue

        print("\nLibrary: <boundary>" + library_541 + "</boundary>" + "Data type: " + str(type(library_541)) + "\n")

        location_541 = ""
        library = ""
        location = ""
        location_code = ""
        location_description = ""
        location_suffix = ""
        try:
            location_541 = location_541_match.group(2)
            # location_541 = location_541.encode('utf-8', 'replace')
        except:
            location_541 = ""

        if not location_541:
            location_541 = ""
        if not re.match(r'[A-Za-z]+', location_541):
            location_541 = ""
        # try:
        # 	location_541 = location_541.decode('utf-8')
        # except:
        # 	pass

        # foutError.write(str(mms_id) + " - Location 541: " + str(location_541 + "\n"))

        if library_541 == "Tisch Library" or str(library_541) == "TISCH" or str(library_541) == "Tisch":
            library = "TISCH"
        elif str(library_541) == "Ginn Library" or str(library_541) == "GINN" or str(library_541) == "Ginn":
            library = "GINN"
        elif library_541 == "Lilly Music Library" or str(library_541) == "MUSIC" or str(library_541) == "Music":
            library = "MUSIC"
        elif library_541 == "W. Van Alan Clark, Jr. Library" or str(library_541) == "SMFA":
            library = "SMFA"
        elif library_541 == "Webster Family Library" or str(library_541) == "VET" or str(library_541) == "Vet" or str(library_541) == "Veterinary Library":
            library = "VET"
        elif library_541 == "Hirsch Health Sciences Library" or str(library_541) == "Hirsh Health Sciences Library" or str(library_541) == "HHSL" or str(library_541) == "Hirsh":
            library = "HIRSH"
        else:
            print("Library in 541 for MMS ID: " + str(mms_id) + " is not retrievable or is not an expected value\n")
            error_file.write("Library in 541 for MMS ID: " + str(mms_id)  + " is not retrievable or is not an expected value\n")
            errorCount += 1
            continue

        print("\nLibrary for 852 from 541: " + library + "\n")
        print("Location_541:               " + str(location_541) + "\n")

        for full_holding in root.findall('holding'):
            print ("\nHolding record " + str(b) + ": \n" + str(full_holding) + "\n")
            b += 1
            holding_id = full_holding.find('holding_id').text
            c = 0
            print("541: \n" + str(bib_record))

            # full_holding = unicode(full_holding)
            holding = pym.parse_xml_to_array(io.StringIO(unicode(et.tostring(full_holding))))[0]

            full_holding_string = et.tostring(full_holding)

            foundLocation = False

            library_locations = mappings[library]


            for dict_location in library_locations:


                if location_541 != "":
                    if dict_location.lower().endswith(location_541.lower()):
                        location_description = dict_location
                        foundLocation = True
                        break
                    elif location_541.lower() == "reference":
                        alternate_location_541 = "Reference Collection"
                        if dict_location.lower().endswith(alternate_location_541.lower()):
                            location_description = dict_location
                            foundLocation = True
                            break

            # foutError.write("Finished location mapping loop? " + str(foundLocation) + "\n")

            if str(location_541) != "" and foundLocation == True:
                location_code = mappings[library][location_description]
                # foutError.write("Location in 541 and mapped correctly: " + location_541 + "\n")
            elif foundLocation == False and str(location_541) == "" and holding['852']['b'] == library:
                library_list = {'TISCH': 0, "HIRSH": 0, "GINN": 0, "MUSIC": 0, "SMFA": 0, "VET": 0}
                for holding_pym_string in root.findall('holding'):
                    #
                    # holding = unicode(holding)


                    holding_pym = pym.parse_xml_to_array(io.StringIO(unicode(et.tostring(holding_pym_string))))[0]
                    library_list[holding_pym['852']['b']] += 1

                if library_list[library] == 1:

                    location_code = holding['852']['c']
                    countList.append(library)
                    foundLocation = True
                    # foutError.write("No location in 541 but mapped correctly to only holding at that library: " + location_541 + "\n")
            # elif holdingsCount > 1:
            # 	print("No location specified in 541, but more than one holding in record for " + str(mms_id) + "\n")
            # 	error_file.write("No location specified in 541, but more than one holding in record for " + str(mms_id) + "\n")
            # 	errorCount += 1
            # 	continue



            #library_and_location = library + location_suffix

            #print("Library and location: " + library_and_location + "\n\n")






            if foundLocation == True:

                # foutError.write("Got into Found Location == True for location code " + location_code + "\n")

                print("Location code: " + location_code + "\n")
                # foutError.write("Location code from matching with Alma and in 541: " + str(location_code) + "; location in holding: " + str(holding['852']['c']) + "\n")
                if holding['852']['c'] == location_code:
                    # foutError.write("MATCHED: Location code from matching with Alma and in 541: " + str(location_code) + "; location in holding: " + str(holding['852']['c']) + "\n")
                    found541 = True
                    success = update_holding(holding, holding_id, full_holding_string, five_forty_one, mms_id)
                    # matched541.append(subfield_3)
                    if success == True:
                        successCount += 1
                    else:
                        print("Couldn't write holding " + str(holding_id) + " for " + str(mms_id) + "to Alma via the API.\n")
                        error_file.write("Couldn't write holding " + str(holding_id) + " for " + str(mms_id) + "to Alma via the API.\n")
                        errorCount += 1
                        # continue


            #
            # else:
            # 	# print("Could not match location field from 541 to a location in Alma for " + str(mms_id) + ". This might be because there is no location in the 541, there's no matching library, or there's a typo in the 541 location.\n")
            # 	# error_file.write("Could not match location field from 541 to a location in Alma for " + str(mms_id) + ". This might be because there is no location in the 541, there's no matching library, or there's a typo in the 541 location.\n")
            # 	# mismatchCount += 1
            #

        # foutError.write(str(mms_id) + " - End of 541 for " + library + " and " + library_541 + "\n")
        if found541 == False:
            print("The 541 for bib record " + str(mms_id)  + " could not match to a holding location.\n")
            error_file.write("The 541 for bib record " + str(mms_id)  + " could not match to a holding location.\n")
            errorCount += 1

        # Python 2

        # holding = pym.parse_xml_to_array(io.StringIO(unicode(et.tostring(full_holding))))[0]

        #Python 3




print("Number of 541s:                                                       " + str(fiveFortyOneCount) + "\n")
count_file.write("Number of 541s:                                            " + str(fiveFortyOneCount) + "\n")
print("Records successfully updated:                                         " + str(successCount) + "\n")
count_file.write("Records successfully updated:                              " + str(successCount) + "\n")
print("Records that couldn't be updated.  Check error file:                  " + str(errorCount) + "\n")
count_file.write("Records that couldn't be updated.  Check error file:       " + str(errorCount) + "\n")
# print("Matching errors between 541 and holdings. Check error file:           " + str(mismatchCount) + "\n")
# count_file.write("atching errors between 541 and holdings. Check error file: " + str(mismatchCount) + "\n")

output_file.write("</holdings>")
error_file.close()
output_file.close()
# foutError.close()
