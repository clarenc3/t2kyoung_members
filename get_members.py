#!/usr/bin/env python

# Clarence Wret, July 24 2024

import requests
from bs4 import BeautifulSoup
import warnings
import pandas as pd
from datetime import datetime
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed

t2k_user="x"
t2k_password="x"

# Now read the xml data
tree = ET.parse('membertable.xml')
root = tree.getroot()

# Save the schema that's in the member table
schema="{urn:schemas-microsoft-com:office:spreadsheet}"

# The format that we're after is
# User name, first name, second name, email

# Loop over each row
t2k_members = []
for child in root.findall(schema+'Worksheet/'+schema+'Table/'+schema+'Row'):

    # A single entry in the xml
    counter = 0
    entries = []
    # Get each row's data
    for entry in child.findall(schema+'Cell/'+schema+'Data'):
        # Skip any field beyond university
        if counter > 5:
            break
        # The email address is always third
        text = entry.text
        entries.append(text)
        counter += 1

    # If you want to find the format of the xml, print(entries)
    t2k_members.append(entries)

# Skip the first entry, which contains the headers
t2k_members = t2k_members[1:-1]

# Sort by last name
t2k_members.sort(key=lambda x: x[2])

def process_member(name):
    url = "https://t2k.org/author/" + name[0]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        # Eeek, plaintext password and user
        page = requests.get(url, auth=(t2k_user, t2k_password))

    # GET THE SOUP
    soup = BeautifulSoup(page.text, features="html.parser")

    # If there is a contribution it is listed as class "vertical listing"
    if soup.find("table", {"class": "vertical listing"}) is not None:
        contrib = soup.find("table", {"class": "vertical listing"}).find_all("th")[0].text
    else:
        contrib = 'Jan 1, 0001'

    contrib_datetime = datetime.strptime(contrib, "%b %d, %Y")
    # Look for "Position"
    pos = str(soup.find_all("p")[1].text.strip())
    # Country
    country = pos.split('(')[-1].split(')')[0]

    pos_pretty = ""
    # Include only students and postdocs
    if "Grad student (MSc)" in pos:
        pos_pretty = "Student MSc"
    elif "Grad student (PhD)" in pos:
        pos_pretty = "Student PhD"
    elif "Postdoc" in pos:
        pos_pretty = "Postdoc"
    else:
        pos_pretty = "Faculty"

    member_since = str(soup.find_all("p")[2].text.strip())
    member_since = member_since.replace('T2K member since: ', '')
    member_since_datetime = datetime.strptime(member_since, '%Y/%m')

    # First name, last name, username, email, institute, country, position, member since, last contribution
    person = [name[1], name[2], name[0], name[3], name[4], country, pos_pretty, member_since_datetime.strftime("%Y-%m-%d"), contrib_datetime.strftime("%Y-%m-%d")]
    return person

t2k_students = []
ntotal = len(t2k_members)

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(process_member, name): name for name in t2k_members}
    for i, future in enumerate(as_completed(futures)):
        name = futures[future]
        if i % 20 == 0:
            print(f"Processing user {name[0]}, {i}/{ntotal} ({round(i/ntotal*100., 2)}%)")
        try:
            result = future.result()
            t2k_students.append(result)
        except Exception as exc:
            print(f"User {name[0]} generated an exception: {exc}")

df = pd.DataFrame(t2k_students, columns=["First name", "Last name", "Username", "Email", "Institute", "Country", "Position", "Member since", "Last contribution"])
print(df)

df.to_csv('t2kyoung_wcountry_wcontrib_everyone.csv', index=False)