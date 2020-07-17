#!/usr/bin/python3

import os
import pprint

import yaml

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

username = os.getlogin()
configLocations = (
    f"/home/{username}/.config/aipm.yaml",
    ".aipm/config.yaml",
    "/etc/aipm.yaml",
    "/".join([os.getcwd(), "aipm.yaml"]),
)


def getconfig():
    config = None
    try:
        for location in configLocations:
            if os.path.isfile(location):
                with open(location, "r") as configFile:
                    config = yaml.load(configFile, Loader=Loader)
                break
        print(f"Configuration loaded from {location} ")
    except:
        print("No valid config files found!")
    return config
