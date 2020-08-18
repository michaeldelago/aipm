#!/usr/bin/env python

import json
import os
import shelve
import sys
import logging
import re
from math import floor

# from functools import partial

import lxml
import requests
from bs4 import BeautifulSoup


class AppImage:
    mainurl = "https://appimage.github.io"

    def __init__(self, id=None, githubLink=None):
        if id != None:
            self.url = "".join([self.mainurl, id])
            self.name = id.strip("/").lower()
        else:
            self.url = self.mainurl
            self.name = None
        self.githubLink = githubLink
        self.downloadLink = None
        self.latestVersion = None
        self.installedVersion = list()

    def __repr__(self):
        return str(self.asdict())

    def fromDict(self, inputDict):
        for key in inputDict.keys():
            try:
                if hasattr(self, key):
                    setattr(self, key, inputDict[key])
            except KeyError:
                logging.warning(f"Key {key} missing from input dictionary")
        return self

    def asdict(self):
        retval = {
            "url": self.url,
            "githubLink": self.githubLink,
            "downloadLink": self.downloadLink,
            "latestVersion": self.latestVersion,
        }
        if hasattr(self, "installedVersion"):
            retval["installedVersion"] = self.installedVersion
        else:
            retval["installedVersion"] = None
        return retval

    def getReleaseLink(self):
        req = requests.get(self.url)
        soup = BeautifulSoup(req.text, "lxml")
        githubLink = soup.find("a", {"class": "button green"}, {"href": True})
        if githubLink != None:
            githubLink = githubLink.get("href")
        else:
            githubLinks = soup.findAll("a", {"class": "button white"}, {"href": True})
            if len(githubLinks) > 0:
                for link in githubLinks:
                    link = link.get("href")
                    if link.endswith("releases"):
                        githubLink = link
                        break
        if githubLink == None:
            logging.error(f"No github link found for {self.name}")
            return 1
        self.githubLink = githubLink
        return 0

    def getDownloadLink(self, gh_creds):
        downloadLink = None
        if self.githubLink == None:
            return 1

        if self.githubLink.endswith("mirrorlist"):
            return self.suseDownloadLink()

        ls = self.githubLink.split("/")
        ls[2] = "api.github.com"
        ls.insert(3, "repos")
        apiLink = "/".join(ls)

        reqcheckurl = "https://api.github.com/rate_limit"

        with requests.Session() as gh_session:
            gh_session.auth = gh_creds
            rate_limit = json.loads(gh_session.get(reqcheckurl).content)
            if rate_limit["rate"]["remaining"] < 1500:
                logging.error(f"Not enough requests left!")
                return 1

            logging.info(f"Requests Left: {rate_limit['rate']['remaining']}")

            try:
                req = gh_session.get(apiLink)
                data = json.loads(req.text)
            except KeyError:
                logging.info(
                    f"Unable to properly get the packages downloads for {self.name}"
                )
                return 1
            except IndexError:
                logging.error(f"Request failed for {self.name}")
                return 1
        try:
            for datum in data:
                assets = datum["assets"]
                for index in range(len(assets)):
                    if assets[index]["browser_download_url"].endswith("AppImage"):
                        downloadLink = assets[index]["browser_download_url"]
                        break
                if downloadLink:
                    break
        except TypeError:
            logging.error(
                f"Error retrieving download link for {self.name}. GitHub API returned:\n\t{data['message']}",
            )
            return 1

        # program does nothing if no download link is found
        self.downloadLink = downloadLink
        if self.downloadLink != None:
            self.latestVersion = downloadLink.split("/")[-2]

        return 0

    def suseDownloadLink(self):
        downloadLinkList = self.githubLink.split(".")
        mlist = downloadLinkList.pop().lower()
        if mlist != "mirrorlist":
            return 1
        else:
            # None of the links with OpenSuse's repositories haven an easily scrapable version
            self.latestVersion = "continuous"
            self.downloadLink = ".".join(downloadLinkList)
        return 0

    def populateLinks(self, gh_creds):
        return self.getReleaseLink() + self.getDownloadLink(gh_creds)

    def downloadAppImage(self, downloadsDir):
        if self.downloadLink == None:
            logging.error(f"No Download Link found for {self.name}")
            return 1

        filename = self.downloadLink.split("/")[-1]
        abspath = "/".join([downloadsDir, ".apps", filename])
        linkname = "/".join([downloadsDir, self.name])

        print(f"Starting download of package {self.name}")
        with open(abspath, "wb") as fp:
            req = requests.get(self.downloadLink, stream=True)
            filesize = req.headers.get("content-length")
            if filesize == None:
                logging.warning(f"Unable to generate progress bar")
                fp.write(req.content)
            else:
                downloaded = 0
                filesize = int(filesize)
                div1k = lambda x: x / 1000  # lambda to divide by 1000
                filesizeKB = div1k(filesize)  # represent downloads in KB
                print("\n")
                for data in req.iter_content(chunk_size=4096):
                    downloaded += div1k(len(data))
                    fp.write(data)
                    progstr = "/".join([str(floor(downloaded)), str(floor(filesizeKB))])
                    lenprog = len(progstr)
                    progress = int((75 - lenprog) * downloaded / filesizeKB)
                    print(
                        f"> {progstr} [{'=' * progress}>{' ' * ((75 - lenprog) - progress)}]",
                        end="\r",
                    )
                print("\n")

        # List of installed versions, append newest version as necessary
        if self.installedVersion == None:
            self.installedVersion = list()

        if (
            len(self.installedVersion) == 0
            or self.installedVersion[0] != self.latestVersion
        ):
            self.installedVersion.insert(0, self.latestVersion)

        # setup perms and shortcuts
        os.chmod(abspath, 0o755)
        if os.path.islink(linkname):
            os.unlink(linkname)
        os.symlink(abspath, linkname)

        print(f"{self.name} downloaded to {abspath}, linked as {linkname}")
        return 0

    def uninstall(self, binDir):
        binaryName = None
        binary = None
        linkPath = "/".join([binDir, self.name])
        try:
            binary = os.readlink(linkPath).split("/")[-1]
            binaryName = binary.split("-")[0]
        except:
            logging.error(f"getting link failed for {self.name}")
            return 1

        filenameRegEx = re.compile(rf"{binaryName}-.*.AppImage")
        filesDir = "/".join([binDir, ".apps"])

        files = filter(filenameRegEx.match, os.listdir(filesDir))

        for filename in files:
            os.remove("/".join([filesDir, filename]))
            logging.info(f"Removed: {filename}")
        os.unlink(linkPath)
        print(f"{self.name} has been uninstalled.")

        return 0

    def clean(self, binDir):
        binaryName = None
        binary = None
        linkPath = "/".join([binDir, self.name])
        try:
            binary = os.readlink(linkPath).split("/")[-1]
            binaryName = binary.split("-")[0]
        except:
            logging.error(f"getting link failed for {self.name}")
            return 1

        filenameRegEx = re.compile(rf"{binaryName}-.*.AppImage")
        filesDir = "/".join([binDir, ".apps"])

        files = filter(filenameRegEx.match, os.listdir(filesDir))
        oldfiles = filter(lambda x: x != binary, files)

        for filename in oldfiles:
            os.remove("/".join([filesDir, filename]))
            logging.info(f" Removed old file: {filename}")
            if len(self.installedVersion) > 1:
                self.installedVersion.pop()

        return 0


if __name__ == "__main__":
    pass
