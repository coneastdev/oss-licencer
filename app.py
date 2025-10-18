#
# copyright "c" 2025 coneastdev
# licenced under gpl-3.0, a copy of this licence should be provided with the software 
#

import requests
from bs4 import BeautifulSoup
import json
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QScrollArea, QFrame, QFileDialog

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
    
# Return licences that match a search term
def searchLicences(searchTerm):
    matchingLicences = []
    with open("licences.json", "r") as f:
        licences = json.load(f)
        for licence in licences:
            if searchTerm.lower() in licence["id"].lower() or searchTerm.lower() in licence["name"].lower():
                matchingLicences.append(licence)
        # Sort the licences by their first keyword, if they have any
        matchingLicences.sort(key=lambda x: x["keywords"][0] if x["keywords"] else "")
    return matchingLicences    

# Get the full text of a licence by its ID by scraping the opensource.org website with BeautifulSoup
def getLicence(licenceID):
    with open("licences.json", "r") as f:
        licences = json.load(f)
        for licence in licences:
            if licenceID.lower() == licence["id"].lower():
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

def app():
    app = QApplication([])
    window = QWidget()
    window.setWindowTitle("oss licencer")
    window.resize(400, 500)
    
    layout = QVBoxLayout()
    
    # Workspace path section
    pathLabel = QLabel("Workspace Path")
    layout.addWidget(pathLabel)
    
    pathInput = QLineEdit()
    layout.addWidget(pathInput)
    
    pathButton = QPushButton("Select Path")
    layout.addWidget(pathButton)
    
    def onPathClicked():
        directory = QFileDialog.getExistingDirectory(window, "Select Workspace Directory")
        if directory:
            pathInput.setText(directory)
    pathButton.clicked.connect(onPathClicked)
    
    # Search licence section
    searchLabel = QLabel("Licence To Search For")
    layout.addWidget(searchLabel)
    
    searchInput = QLineEdit()
    layout.addWidget(searchInput)
    
    fetchButton = QPushButton("Find Licence")
    layout.addWidget(fetchButton)
    
    # Licence display section
    licenceDisplay = QScrollArea()
    licenceDisplay.setWidgetResizable(True)
    licenceContainer = QWidget()
    licenceDisplayLayout = QVBoxLayout(licenceContainer)
    licenceContainer.setLayout(licenceDisplayLayout)
    licenceDisplay.setWidget(licenceContainer)
    layout.addWidget(licenceDisplay)
    
    # Fetch and display licences on button click
    def onFetchClicked():
        searchTerm = searchInput.text().strip()
        if searchTerm:
            results = searchLicences(searchTerm)
            def clear_layout(layout):
                while layout.count():
                    item = layout.takeAt(0)
                    widget = item.widget()
                    if widget:
                        widget.setParent(None)
                        widget.deleteLater()
                    elif item.layout():
                        clear_layout(item.layout())

            clear_layout(licenceDisplayLayout)
            if results:
                for result in results:
                    resultComp = QFrame()
                    resultComp.setFrameShape(QFrame.StyledPanel)
                    resultCompLayout = QVBoxLayout(resultComp)
                    resultComp.setLayout(resultCompLayout)
                    
                    resultName = QLabel(f"Name: {result['name']}")
                    resultCompLayout.addWidget(resultName)
                    resultID = QLabel(f"ID: {result['id']}")
                    resultCompLayout.addWidget(resultID)
                    addButton = QPushButton("Add")
                    resultCompLayout.addWidget(addButton)
                    
                    licenceDisplayLayout.addWidget(resultComp)
            else:
                noLabel = QLabel("No Licences Found.")
                licenceDisplayLayout.addWidget(noLabel)
    
    fetchButton.clicked.connect(onFetchClicked)
    
    window.setLayout(layout)
    window.show()
    app.exec()
    
if __name__ == "__main__":
    app()