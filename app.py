#
# copyright © 2025 coneastdev
# licenced under gpl-3.0, a copy of this licence should be provided with the software 
#

import requests
from bs4 import BeautifulSoup
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QScrollArea, QFrame, QFileDialog
import os
from datetime import datetime
import subprocess
import time

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

def insertNoticeInFile(workspacePath, fileName, gitignored, licenceID):
    fullpath = os.path.join(workspacePath, fileName)

    # Read file contents (tolerant read so single bad file won't crash)
    try:
        with open(fullpath, "r", encoding="utf-8", errors="replace") as file:
            fileData = file.read()
    except Exception as e:
        # If we can't read the file, skip it
        print(f"Skipping unreadable file {fullpath}: {e}")
        return

    # Skip ignored or special files BEFORE opening for write
    if fileName in gitignored:
        return
    if fileName == "LICENCE" or fileName == ".gitignore":
        return

    # Determine extension safely
    extension = fileName.rsplit(".", 1)[1] if "." in fileName else ""

    # Only compute git user info when we actually need to write
    res = subprocess.run(["git", "config", "user.name"], stdout=subprocess.PIPE)
    git_username = res.stdout.strip().decode()
    res = subprocess.run(["git", "config", "user.email"], stdout=subprocess.PIPE)
    git_email = res.stdout.strip().decode()
    copyright = f"copyright © {datetime.now().year} {git_username} <{git_email}>"

    # Prepare the comment block based on file extension
    new_data = None

    # languages that use /* */ for comments
    if extension in ["css", "js", "acedb", "actionscript", "asy", "bind-named", "c", "cg", "ch", "clean", "clipper", "cpp", "cs", "cuda", "d", "dot", "dylan", "fx", "glsl", "go", "groovy", "h", "haxe", "hercules", "hyphy", "idl", "ishd", "java", "javacc", "javascript", "javascript.jquery", "json5", "jsonc", "jsonnet", "kscript", "lpc", "mel", "named", "objc", "objcpp", "objj", "ooc", "pccts", "php", "pike", "pilrc", "plm", "pov", "processing", "proto", "rc", "rust", "scala", "scss", "slice", "stan", "stp", "supercollider", "swift", "systemverilog", "tads", "teak", "tsalt", "typescript", "uc", "vala", "vera", "verilog", "verilog_systemverilog", "sass"]:
        new_data = f"/*\n{copyright}\nThis project is licenced under the {licenceID} licence.\n*/\n\n" + fileData

    # languages that use # for comments
    elif extension in ["py", "aap", "ampl", "ansible", "apache", "apachestyle", "awk", "bc", "cairo", "cfg", "cl", "cmake", "conkyrc", "crontab", "cucumber", "cython", "dakota", "debcontrol", "debsources", "desktop", "dhcpd", "diff", "dockerfile", "ebuild", "ecd", "eclass", "elixir", "elmfilt", "ember-script", "esmtprc", "exim", "expect", "exports", "fancy", "fgl", "fstab", "fvwm", "gdb", "gdscript3", "gentoo-conf-d", "gentoo-env-d", "gentoo-init-d", "gentoo-make-conf", "gentoo-package-keywords", "gentoo-package-mask", "gentoo-package-use", "gitcommit", "gitignore", "gitrebase", "gnuplot", "gtkrc", "hb", "hog", "hostsaccess", "hxml", "ia64", "icon", "inittab", "jproperties", "kivy", "ldif", "lilo", "lout", "lss", "lynx", "maple", "meson", "mips", "mirah", "mush", "nginx", "nimrod", "nix", "nsis", "ntp", "ora", "paludis-use-conf", "pcap", "perl", "pine", "po", "praat", "privoxy", "ps1", "psf", "ptcap", "puppet", "pyrex", "python", "radiance", "ratpoison", "rego", "remind", "resolv", "rib", "robot", "robots", "rspec", "ruby", "scons", "sdc", "sed", "sh", "shader_test", "sls", "sm", "snakemake", "snippets", "snnsnet", "snnspat", "snnsres", "spec", "squid", "sshconfig", "sshdconfig", "tcl", "tf", "tidy", "tli", "tmux", "tsscl", "ttl", "tup", "upstart", "vgrindefs", "vrml", "wget", "wml", "xmath", "yaml", "r", "renpy"]:
        new_data = f"#\n# {copyright}\n# This project is licenced under the {licenceID} licence.\n#\n\n" + fileData

    # languages that use <!-- --> for comments
    elif extension in ["html", "markdown", "pandoc", "rmarkdown", "sgmllnx", "wikipedia", "docbk", "xml", "cf", "eruby", "genshi", "gsp", "jinja", "mason", "myghty", "xhtml"]:
        new_data = f"<!--\n{copyright}\nThis project is licenced under the {licenceID} licence.\n-->\n\n" + fileData

    # languages that use -- for comments
    elif extension in ["ada", "adb", "ads", "al", "asc", "asm", "basemake", "bds", "blitzbasic", "boo", "cobol", "cm", "crystal", "dcl", "eiffel", "fortran", "fsharp", "haskell", "idl", "inno", "lisp", "lua", "m4", "matlab", "modula-2", "modula-3", "ncl", "nim", "openedge", "pascal", "plsql", "pogo", "powerbuilder", "progress", "puppet-legacy", "qmake", "racket", "rebol", "red", "sas", "sql", "tclsh", "tex", "vhdl"]:
        new_data = f"--\n-- {copyright}\n-- This project is licenced under the {licenceID} licence.\n--\n\n" + fileData

    else:
        print(f"Skipping file with unsupported extension: {fullpath}")

    # If none of the branches matched, don't modify the file (avoid truncation)
    if new_data is None:
        return

    # Finally write the modified content back (UTF-8)
    try:
        with open(fullpath, "w", encoding="utf-8") as file:
            file.write(new_data)
    except Exception as e:
        print(f"Failed to write to {fullpath}: {e}")

# Add the licence text to the specified workspace path and notices in files
def addLicenceToWorkspace(licenceID, workspacePath, licences):
    licenceText = getLicence(licenceID, licences)
    if not licenceText:
        print(f"Could not fetch licence text for ID: {licenceID}")
        return False
    try:
        with open(f"{workspacePath}/LICENCE", "w", encoding="utf-8") as f:
            f.write(licenceText)

        # Build a set of ignored paths relative to the repo root.
        gitignored = set()
        try:
            # Use git to get the canonical list of ignored files (relative paths)
            res = subprocess.run(
                ["git", "-C", workspacePath, "ls-files", "--others", "-i", "--exclude-standard"],
                stdout=subprocess.PIPE, text=True, check=True
            )
            gitignored = set(line.strip() for line in res.stdout.splitlines() if line.strip())
        except Exception:
            # Fallback: parse .gitignore (simple, pattern entries only)
            gi_path = os.path.join(workspacePath, ".gitignore")
            if os.path.exists(gi_path):
                with open(gi_path, "r", encoding="utf-8", errors="replace") as gitignore:
                    for line in gitignore:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        gitignored.add(line.rstrip("/"))

        # Walk top-level entries and build a queue of directories to traverse.
        directories = []
        for entry in os.listdir(workspacePath):
            # skip the git metadata directory entirely
            if entry == ".git":
                continue
            full = os.path.join(workspacePath, entry)
            rel = os.path.relpath(full, workspacePath)  # relative path to compare with gitignored
            if rel in gitignored:
                continue
            if os.path.isdir(full):
                # append absolute path for traversal
                directories.append(full)
            else:
                # pass the same workspacePath and filename (top-level name) to insertion
                insertNoticeInFile(workspacePath, entry, gitignored, licenceID)
            time.sleep(0.1)  # slight delay to avoid overwhelming the filesystem

        # Traverse directories queue correctly (BFS)
        while directories:
            dirpath = directories.pop(0)
            for entry in os.listdir(dirpath):
                full = os.path.join(dirpath, entry)
                rel = os.path.relpath(full, workspacePath)
                if rel in gitignored:
                    continue
                if os.path.isdir(full):
                    # skip .git dir
                    if entry == ".git":
                         continue
                    directories.append(full)
                else:
                    # call insertNoticeInFile with the directory containing the file and the filename
                    insertNoticeInFile(dirpath, entry, gitignored, licenceID)
                time.sleep(0.1)
        return True
    except IOError as e:
        print(f"Error writing licence to workspace: {e}")
        return False

# Launces pyside6 Qt app
def app(licences):
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
                    
                    resultName = QLabel(f"Name: {result["name"]}")
                    resultCompLayout.addWidget(resultName)
                    resultID = QLabel(f"ID: {result["id"]}")
                    resultCompLayout.addWidget(resultID)
                    addButton = QPushButton("Add")
                    addButton.clicked.connect(lambda checked, id=result["id"]: addLicenceToWorkspace(id, pathInput.text().strip(), licences))
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