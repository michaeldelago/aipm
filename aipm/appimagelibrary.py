import json
import os
import shelve
import sys
from concurrent.futures import ThreadPoolExecutor

import lxml
import requests
from bs4 import BeautifulSoup

try:
    from aipm import appimage
except:
    import appimage


class AppImageLibrary:
    def __init__(self, location):
        self.location = "/".join([os.path.abspath(location), ".library"])

    def addItem(self, appimage):
        if not os.path.isfile(self.location):
            print(
                f"Appimage library doesn't exist at location {self.location}!",
                file=sys.stderr,
            )
            return 1
        with shelve.open(self.location) as library:
            library[appimage.name] = appimage
        print(f"Added Item to Library: {appimage.name}")
        return 0

    def delItem(self, appimageName):
        if not os.path.isfile(self.location):
            print(
                f"Appimage library doesn't exist at location {self.location}!",
                file=sys.stderr,
            )
            return 1
        with shelve.open(self.location) as library:
            library[appimageName] = None
        print(f"Deleted Item from Library: {appimageName}")
        return 0

    def select(self, searchTerm):
        appimage = None
        altlist = list()
        searchTerm = searchTerm.lower()  # Force lowercase to make life worth living
        with shelve.open(self.location) as library:
            try:
                appimage = library[searchTerm]
                appimage.name = searchTerm
            except KeyError:
                for packname in library.keys():
                    if packname.startswith(searchTerm[:3]):
                        altlist.append(packname)
                if len(altlist) > 0:
                    altlist = '" "'.join(altlist)
                    print(
                        f"Package {searchTerm} not found. Did you mean one of these?\n\t{altlist}"
                    )
                else:
                    print(f"Package {searchTerm} not found.")
                return appimage
        return appimage

    def search(self, searchTerm):
        searchResults = [("Software Name", "Latest Version"), ("", "")]
        longestname = len(searchResults[0][0])
        searchTerm = searchTerm.lower()
        with shelve.open(self.location) as library:
            for item in library.keys():
                if searchTerm in item:
                    ai = library[item]
                    latver = ai.latestVersion
                    searchResults.append((item, latver))
                    if len(item) > longestname:
                        longestname = len(item)
        if len(searchResults) > 2:
            for item in searchResults:
                print(f"\t{item[0].ljust(longestname + 2)} {item[1]}")
        else:
            print(f"No results found for term {searchTerm}")
        return 0

    def exportJSON(self):
        librarydict = dict()
        with shelve.open(self.location) as library:
            for appimage in library.keys():
                librarydict[appimage] = library[appimage].asdict()
        with open("./library.json", "w") as fp:
            json.dump(librarydict, fp)
        return 0

    def importJSON(self, inputfile):
        librarydict = dict()
        with open(inputfile, "r") as fp:
            librarydict = json.load(fp)
        with shelve.open(self.location) as library:
            for appimageName in librarydict.keys():
                ai = appimage.AppImage().fromDict(librarydict[appimageName])
                library[appimageName] = ai
        return 0

    def upgrade(self, downloadsDir, *args):
        if args:
            upgradelist = args
        else:
            upgradelist = None
        installed = list()

        with shelve.open(self.location) as library:
            if upgradelist != None:
                for item in upgradelist:
                    if library[item].installedVersion:
                        installed.append(library[item])
            else:
                for item in library.keys():
                    if library[item].installedVersion:
                        installed.append(library[item])
        for ai in installed:
            ai.getDownloadLink()
            ai.downloadAppImage(downloadsDir)
        # WORK IN PROGRESS

    # Pull the library of appImages
    def scrapeLibrary(self, gh_creds):
        ails = []
        url = "https://appimage.github.io/apps/"
        req = requests.get(url)
        soup = BeautifulSoup(req.text, "lxml")
        appimages = soup.find("tbody").findAll("tr", {"id": True})

        # Do this with threads because speed
        with ThreadPoolExecutor() as executor:
            for scrapedai in appimages:
                ai = appimage.AppImage(scrapedai.get("id"))
                executor.submit(ai.populateLinks, gh_creds)
                ails.append(ai)

        for ai in ails:
            if ai.downloadLink:
                self.addItem(ai)
            else:
                print(
                    f"No Download Link for {ai.name}. Not Adding to Library Database.",
                    file=sys.stderr,
                )
        print(f"Library has been built.")
        return 0
