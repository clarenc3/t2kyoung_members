#!/usr/bin/env python

# Clarence Wret, July 24 2024

import requests
from bs4 import BeautifulSoup
import sys
import warnings
import pandas as pd
from datetime import datetime
# Read the xml
import xml.etree.ElementTree as ET

t2k_user="user"
t2k_password="pass"

# Now read the xml data
tree = ET.parse('membertable.xml')
root = tree.getroot()

# Save the schema that's in the member table
schema="{urn:schemas-microsoft-com:office:spreadsheet}"

# The format that we're after is
# User name, first name, second name, email

# Loop over each row
t2k_members=[]
for child in root.findall(schema+'Worksheet/'+schema+'Table/'+schema+'Row'):

    # A single entry in the xml
    counter=0
    entries=[]
    # Get each row's data
    for entry in child.findall(schema+'Cell/'+schema+'Data'):
        # Skip any field beyond university
        if counter > 5:  
            break
        # The email address is always third
        text=entry.text
        entries.append(text)
        counter+=1

    # If you want to find the format of the xml, print(entries)
    t2k_members.append(entries)

# Skip the first entry, which contains the headers
t2k_members=t2k_members[1:-1]

# Sort by last name
t2k_members.sort(key=lambda x:x[2])

t2k_students=[]
npersons = 0
ntotal = len(t2k_members)
for name in t2k_members:
    if npersons%20 == 0:
        print("Processing user "+name[0]+", "+str(npersons)+"/"+str(ntotal)+" ("+str(round(npersons/ntotal*100.,2))+"%)")
    npersons=npersons+1
    url="https://t2k.org/author/"+name[0]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        # Eeek, plaintext password and user
        page = requests.get(url, auth=(t2k_user, t2k_password))

    # GET THE SOUP
    soup = BeautifulSoup(page.text, features="html.parser")

    # Look for "Position"
    pos = str(soup.find_all("p")[1].text.strip())
    # Country
    country = pos.split('(')[-1].split(')')[0]

    pos_pretty=""
    # Include only students and postdocs
    if "Grad student (MSc)" in pos:
        pos_pretty = "Student MSc"
    elif "Grad student (PhD)" in pos:
        pos_pretty = "Student PhD"
    elif "Postdoc" in pos:
        pos_pretty = "Postdoc"
    else:
        pos_pretty = "Permanent"

    member_since = str(soup.find_all("p")[2].text.strip())
    member_since = member_since.replace('T2K member since: ', '')
    member_since_datetime = datetime.strptime(member_since, '%Y/%m')

    # First name, last name, username, email, institute, country, position, member since
    person=[name[1], name[2], name[0], name[3], name[4], country, pos_pretty, member_since_datetime]
    t2k_students.append(person)

df = pd.DataFrame(t2k_students, columns=["First name", "Last name", "Username", "Email", "Institute", "Country", "Position", "Member since"])
print(df)

df.to_csv('t2kyoung_wcountry_everyone.csv', index=False)
