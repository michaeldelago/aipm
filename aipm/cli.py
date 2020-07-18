#!/usr/bin/python3


import argparse
import os
import pprint
import sys

from aipm import config
from aipm import appimagelibrary


class Program:
    def __init__(self):
        self.configuration = config.getconfig()

    def install(self, appimageName):
        ail = appimagelibrary.AppImageLibrary(self.configuration["libraryLocation"])
        ai = ail.select(appimageName)
        if ai == None:
            return 1
        if self.configuration["AppImageLocation"]:
            downloadsDir = self.configuration["AppImageLocation"]
        else:
            downloadsDir = f"/home/{config.username}/bin/apps"

        if not os.path.isdir(downloadsDir):
            print(f"Downloads directory {downloadsDir} does not exist", file=sys.stderr)
            return 1

        ai.downloadAppImage(downloadsDir)

        return 0

    def export(self):
        ail = appimagelibrary.AppImageLibrary(self.configuration["libraryLocation"])
        if ail.exportJSON() == 0:
            print(f"Library exported as {os.getcwd()}/library.json")
        return 0

    def search(self, searchTerm):
        ail = appimagelibrary.AppImageLibrary(self.configuration["libraryLocation"])
        ail.search(searchTerm)
        return 0

    def scrape(self):
        ail = appimagelibrary.AppImageLibrary(self.configuration["libraryLocation"])

        gh_creds = (self.configuration["gh_login"], self.configuration["gh_token"])
        ail.scrapeLibrary(gh_creds)
        return 0

    def importJson(self, inputFile):
        ail = appimagelibrary.AppImageLibrary(self.configuration["libraryLocation"])
        ail.importJSON(inputFile)
        return 0


def main():
    parser = argparse.ArgumentParser(
        prog="aipm", description="Package Manager for AppImages"
    )
    subparsers = parser.add_subparsers(dest="option")

    parse_install = subparsers.add_parser("install", help="Install a package")
    parse_install.add_argument("appimage", help="Package Name")

    parse_search = subparsers.add_parser("search", help="Search for a package")
    parse_search.add_argument("search_term", help="term to search for")

    parse_import = subparsers.add_parser("import", help="Import a JSON library")
    parse_import.add_argument("-f", "--file", help="JSON file", required=True)

    parse_export = subparsers.add_parser("export", help="Export to a JSON file")

    parse_scrape = subparsers.add_parser("scrape", help="Scrape library from internet")

    args = parser.parse_args(sys.argv[1:])

    prog = Program()

    try:
        if args.option == "search":
            prog.search(args.search_term)
        elif args.option == "install":
            prog.install(args.appimage)
        elif args.option == "scrape":
            prog.scrape()
        elif args.option == "import":
            prog.importJson(args.file)
        elif args.option == "export":
            prog.export()
        elif args.action == "upgrade":
            print("Not implemented yet :e")
    except AttributeError:
        args = parser.parse_args(["--help"])


if __name__ == "__main__":
    main()
