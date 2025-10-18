#
# copyright "c" 2025 coneastdev
# licenced under gpl-3.0, a copy of this licence should be provided with the software 
#

import requests
from bs4 import BeautifulSoup
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QScrollArea, QFrame, QFileDialog

licences = []

# Update the licences.json file from the opensource.org API
def updateLicences():
    url = "https://opensource.org/api/license/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        # The API returns a JSON array of licence metadata.
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching licenses: {e}")
    
# Return licences that match a search term
def searchLicences(searchTerm, licences):
    matchingLicences = []
    for licence in licences:
        # Assumes licence dict contains 'id' and 'name' keys. If the API changes, guard these accesses.
        if searchTerm.lower() in licence["id"].lower() or searchTerm.lower() in licence["name"].lower():
            matchingLicences.append(licence)
    # Sort the licences by their first keyword, if they have any
    matchingLicences.sort(key=lambda x: (
        0 if any(k.strip().lower() == "popular-strong-community" for k in (x.get("keywords") or [])) else 1,
        (x.get("name") or "").lower()
    ))
    return matchingLicences    

# Get the full text of a licence by its ID by scraping the opensource.org website with BeautifulSoup
def getLicence(licenceID, licences):
    for licence in licences:
        if licenceID.lower() == licence["id"].lower():
            url = f"https://opensource.org/license/{licenceID}"
            try:
                response = requests.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Find the container that holds the licence text on the web page.
                licenceContainer = soup.find("div", class_="license-content")
                
                licenceText = ""
                
                if not licenceContainer:
                    # Could not find content container; return None so callers know fetching failed.
                    return None
                
                # Extract paragraphs and apply white space for readability.
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

# Launces pyside6 Qt app
def app(licences):
    # Avoid shadowing the function name `app` with the QApplication instance; local variable name is `qt_app`.
    qt_app = QApplication([])
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
            results = searchLicences(searchTerm, licences)
            def clear_layout(layout):
                # Recursively remove widgets from the layout to free them.
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
    qt_app.exec()
    
if __name__ == "__main__":
    # updateLicences() can return None if fetching failed — check before launching the UI.
    licences = updateLicences()
    if not licences:
        print("Warning: no licences loaded; UI will start with an empty list.")
        licences = []
    app(licences)