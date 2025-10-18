#
# copyright "c" 2025 coneastdev
# licenced under gpl-3.0, a copy of this licence should be provided with software 
#

import requests
from bs4 import BeautifulSoup
import json


# Update the licences.json file from the opensource.org API
def updateLicences():
    url = "https://opensource.org/api/license/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        licences = response.json()
        with open("licences.json", "w") as f:
            f.write(str(json.dump(licences, f, indent=4)).replace("None", ""))
            f.close()
    except requests.RequestException as e:
        print(f"Error fetching licenses: {e}")
    
# Get the full text of a licence by its ID by scraping the opensource.org website with BeautifulSoup
def getLicence(licenceID):
    with open("licences.json", "r") as f:
        licences = json.load(f)
        for licence in licences:
            if licenceID.lower() == licence["id"].lower():
                print(f"Found licence: {licenceID}")
                url = f"https://opensource.org/license/{licenceID}"
                try:
                    response = requests.get(url)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, "html.parser")
                    
                    licenceContainer = soup.find("div", class_="license-content")
                    
                    licenceText = ""
                    
                    for p in licenceContainer.find_all("p"):
                        data = p.get_text(separator="\n").strip()
                        
                        # replace every 10th space (counting across the string) with a newline for better readability
                        count = 0
                        parts = []
                        for ch in data:
                            if ch == " ":
                                count += 1
                                if count % 10 == 0:
                                    parts.append("\n")
                                    continue
                            parts.append(ch)
                        data = "".join(parts)
                        
                        licenceText += ("\n\n" +  data)
                    
                    return licenceText
                except requests.RequestException as e:
                    print(f"Error fetching license details: {e}")
    return None