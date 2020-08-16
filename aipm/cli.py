#!/usr/bin/python3


import argparse
import os
import pprint
import sys
import logging

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
            downloadsDir = f"/home/{config.username}/bin"

        if os.path.isdir(downloadsDir) == False:
            logging.critical(f"Downloads directory {downloadsDir} does not exist")
            return 1
        elif os.path.isdir("/".join([downloadsDir, ".apps"])) == False:
            os.makedirs("/".join([downloadsDir, ".apps"]))

        ai.downloadAppImage(downloadsDir)

        ail.addItem(ai)

        return 0

    def update(self, inputfile=None):
        gh_creds = (self.configuration["gh_login"], self.configuration["gh_token"])
        ail = appimagelibrary.AppImageLibrary(self.configuration["libraryLocation"])
        ail.update(gh_creds, filename=inputfile)
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
        answer = None

        answer = input(
            'This feature is deprecated, and is not maintained. You\'re going to have a better experience with the "update" command. Continue? [y/N]\n'
        )

        if answer.lower() == "y":
            ail = appimagelibrary.AppImageLibrary(self.configuration["libraryLocation"])

            gh_creds = (self.configuration["gh_login"], self.configuration["gh_token"])
            ail.scrapeLibrary(gh_creds)
            return 0
        else:
            return 0

    def importJson(self, inputFile):
        ail = appimagelibrary.AppImageLibrary(self.configuration["libraryLocation"])
        ail.importJSON(inputFile)
        return 0

    def clean(self, ainame):
        ail = appimagelibrary.AppImageLibrary(self.configuration["libraryLocation"])
        ail.clean(self.configuration["AppImageLocation"], ainame)
        return 0


    def uninstall(self, ainame):
        ail = appimagelibrary.AppImageLibrary(self.configuration["libraryLocation"])
        ai = ail.select(ainame)
        ai.uninstall(self.configuration["AppImageLocation"])
        ail.addItem(ai)
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

    parse_import = subparsers.add_parser("clean", help="Remove old AppImages")
    parse_import.add_argument("appimage", help="Package name", default="all")

    parse_import = subparsers.add_parser("uninstall", help="Remove an AppImages")
    parse_import.add_argument("appimage", help="Package name")

    parse_update = subparsers.add_parser(
        "update", help="Update package database from repository"
    )
    parse_update.add_argument(
        "-f", "--file", help="feed.json containing release info", default=None, required=False
    )

    parse_export = subparsers.add_parser("export", help="Export to a JSON file")

    parse_scrape = subparsers.add_parser(
        "scrape", help="Scrape library from internet (deprecated)"
    )

    parse_upgrade = subparsers.add_parser(
        "upgrade", help="Download newest versions of installed packages"
    )

    args = parser.parse_args(sys.argv[1:])

    prog = Program()

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
    elif args.option == "update":
        prog.update(inputfile=args.file)
    elif args.option == "clean":
        prog.clean(args.appimage)
    elif args.option == "uninstall":
        prog.uninstall(args.appimage)
    elif args.option == "upgrade":
        logging.critical("Not implemented yet :e")
    # except AttributeError:
    #     args = parser.parse_args(["--help"])


if __name__ == "__main__":
    main()
