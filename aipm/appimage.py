#!/usr/bin/env python

import json
import os
import shelve
import sys
from math import floor

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
        self.installedVersion = None

    def __repr__(self):
        return str(self.asdict())

    def fromDict(self, inputDict):
        for key in inputDict.keys():
            try:
                if hasattr(self, key):
                    setattr(self, key, inputDict[key])
            except KeyError:
                print(f"Key {key} missing from input dictionary", file=sys.stderr)
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
            print(f"No github link found for {self.name}", file=sys.stderr)
            return 1
        self.githubLink = githubLink
        return 0

    def getDownloadLink(self, gh_creds):
        downloadLink = None
        if self.githubLink == None:
            # print(f"No githubLink found for {self.name}", file=sys.stderr)
            return 1

        if self.githubLink.endswith("mirrorlist"):
            return self.suseDownloadLink()

        gh_login = gh_creds[0]
        gh_token = gh_creds[1]

        ls = self.githubLink.split("/")
        ls[2] = "api.github.com"
        ls.insert(3, "repos")
        apiLink = "/".join(ls)

        with requests.Session() as gh_session:
            gh_session.auth = (gh_login, gh_token)
            try:
                req = gh_session.get(apiLink)
                data = json.loads(req.text)
                # assets = data[0]["assets"]
            except KeyError:
                print(
                    f"Unable to properly download the packages downloads for {self.name}",
                    file=sys.stderr,
                )
                return 1
            except IndexError:
                print(f"Request failed for {self.name}", file=sys.stderr)
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
            print(
                f"Error retrieving Download link. GitHub API returned:\n\t{data['message']}",
                file=sys.stderr,
            )
            return 1
        if downloadLink == None:
            print(f"Unable to find a download link for {self.name}", file=sys.stderr)
            return 1

        self.downloadLink = downloadLink
        self.latestVersion = downloadLink.split("/")[-2]
        return 0

    def suseDownloadLink(self):
        downloadLinkList = self.githubLink.split(".")
        mlist = downloadLinkList.pop().lower()
        if mlist != "mirrorlist":
            return 1
        else:
            self.downloadLink = ".".join(downloadLinkList)
        return 0

    def populateLinks(self, gh_creds):
        return self.getReleaseLink() + self.getDownloadLink(gh_creds)

    def downloadAppImage(self, downloadsDir):
        if self.downloadLink == None:
            print(f"No downloadLink found for {self.name}", file=sys.stderr)
            return 1

        filename = self.downloadLink.split("/")[-1]
        abspath = "/".join([downloadsDir, ".apps", filename])
        linkname = "/".join([downloadsDir, self.name])

        print(f"Starting download of package {self.name}")
        with open(abspath, "wb") as fp:
            req = requests.get(self.downloadLink, stream=True)
            filesize = req.headers.get("content-length")
            if filesize == None:
                print(f"Unable to generate progress bar", file=sys.stderr)
                fp.write(req.content)
            else:
                downloaded = 0
                filesize = int(filesize)
                div1k = lambda x: x / 1000
                filesizeKB = div1k(filesize)
                print("\n")
                for data in req.iter_content(chunk_size=4096):
                    downloaded += len(data)
                    fp.write(data)
                    # Ugly way of converting to strings in KB
                    downloaded = div1k(downloaded)
                    progstr = "/".join(map(str, (map(floor, [downloaded, filesizeKB]))))
                    lenprog = len(progstr)
                    progress = int((75 - lenprog) * downloaded / filesize)
                    print(
                        f"> {progstr} [{'=' * progress}>{' ' * ((75 - lenprog) - progress)}]",
                        end="\r",
                    )
                print("\n")

        self.installedVersion = self.latestVersion

        # setup perms and shortcuts
        os.chmod(abspath, 0o755)
        if os.path.islink(linkname):
            os.unlink(linkname)
        os.symlink(abspath, linkname)

        print(f"{self.name} downloaded to {abspath}, linked as {linkname}")
        return 0


if __name__ == "__main__":
    pass
