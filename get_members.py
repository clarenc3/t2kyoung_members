#!/usr/bin/env python
import requests
from bs4 import BeautifulSoup
import warnings
import pandas as pd
from datetime import datetime
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed

t2k_user = ""
t2k_password = ""

def parse_xml_members(xml_file):
    """Parse XML file and return member data with validation"""
    tree = ET.parse(xml_file)
    root = tree.getroot()
    schema = "{urn:schemas-microsoft-com:office:spreadsheet}"
    t2k_members = []
    
    for child in root.findall(schema+'Worksheet/'+schema+'Table/'+schema+'Row'):
        entries = []
        for entry in child.findall(schema+'Cell/'+schema+'Data'):
            entries.append(entry.text if entry.text else '')
            
        # Ensure each entry has at least 6 fields, pad with empty strings if needed
        while len(entries) < 6:
            entries.append('')
            
        # Only append entries that have at least a username (first field)
        if entries[0]:
            t2k_members.append(entries[:6])  # Only take first 6 fields
            
    # Skip the header row and any trailing empty rows
    return [m for m in t2k_members[1:] if any(m)]

def process_member(name):
    """Process individual member data with error handling"""
    try:
        # Validate input data
        if not isinstance(name, (list, tuple)) or len(name) < 5:
            raise ValueError(f"Invalid member data format: {name}")
            
        username = name[0]
        if not username:
            raise ValueError("Empty username")
            
        url = f"https://t2k.org/author/{username}"
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            page = requests.get(url, auth=(t2k_user, t2k_password))
            
        page.raise_for_status()  # Raise exception for bad HTTP status
        
        soup = BeautifulSoup(page.text, features="html.parser")
        
        # Get contribution date with fallback
        contrib = 'Jan 1, 0001'
        contrib_table = soup.find("table", {"class": "vertical listing"})
        if contrib_table and contrib_table.find_all("th"):
            contrib = contrib_table.find_all("th")[0].text
        contrib_datetime = datetime.strptime(contrib, "%b %d, %Y")
        
        # Get position and country with error handling
        paragraphs = soup.find_all("p")
        if len(paragraphs) < 2:
            raise ValueError("Required paragraph elements not found")
            
        pos = str(paragraphs[1].text.strip())
        
        # Extract country more safely
        try:
            country = pos.split('(')[-1].split(')')[0]
        except IndexError:
            country = "Unknown"
        
        # Determine position
        pos_pretty = "Faculty"  # default
        if "Grad student (MSc)" in pos:
            pos_pretty = "Student MSc"
        elif "Grad student (PhD)" in pos:
            pos_pretty = "Student PhD"
        elif "Postdoc" in pos:
            pos_pretty = "Postdoc"
        
        # Get member since date
        member_since = "1970/01"  # default
        if len(paragraphs) >= 3:
            member_since = str(paragraphs[2].text.strip())
            member_since = member_since.replace('T2K member since: ', '')
        member_since_datetime = datetime.strptime(member_since, '%Y/%m')
        
        return [
            name[1] or "Unknown",  # First name
            name[2] or "Unknown",  # Last name
            username,
            name[3] or "Unknown",  # Email
            name[4] or "Unknown",  # Institute
            country,
            pos_pretty,
            member_since_datetime.strftime("%Y-%m-%d"),
            contrib_datetime.strftime("%Y-%m-%d")
        ]
        
    except Exception as e:
        print(f"Error processing user {name[0] if name and len(name) > 0 else 'unknown'}: {str(e)}")
        # Return None to indicate failure
        return None

def main():
    # Parse XML
    t2k_members = parse_xml_members('membertable.xml')
    
    # Sort by last name (index 2), handling None values
    t2k_members.sort(key=lambda x: x[2] if x and len(x) > 2 and x[2] else '')
    
    # Process members
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
                if result:  # Only append successful results
                    t2k_students.append(result)
            except Exception as exc:
                print(f"User {name[0]} generated an exception: {exc}")
    
    # Create DataFrame and save to CSV
    if t2k_students:
        df = pd.DataFrame(
            t2k_students,
            columns=["First name", "Last name", "Username", "Email", "Institute", 
                    "Country", "Position", "Member since", "Last contribution"]
        )
        print(df)
        df.to_csv('t2kyoung_wcountry_wcontrib_everyone.csv', index=False)
    else:
        print("No valid data was processed")

if __name__ == "__main__":
    main()

# df.to_csv('t2kyoung_wcountry_wcontrib_everyone.csv', index=False)