import os
import json
from coloring import Color, colorize

def get_home_dir():
    return os.path.expanduser("~")

TEST = False

APP_NAME = "paper"

# boiler constants

HOME_DIR: str
CWD: str
LOC_FILE: str
LIB_DIR: str
CONF_DIR: str

# project constants

DB_DIR: str

def update():
    global HOME_DIR, CWD, LOC_FILE, LIB_DIR, CONF_DIR

    HOME_DIR = get_home_dir()
    CWD = os.getcwd()
    LOC_FILE = os.path.join(HOME_DIR, ".loc.json")
    LIB_DIR = os.path.join(CWD, "library")
    CONF_DIR = os.path.join(CWD, "config")
    if os.path.exists(LOC_FILE) and TEST is False:
        with open(LOC_FILE, "r") as f:
            loc = json.load(f)
            LIB_DIR = os.path.join(loc["library"], APP_NAME)
            CONF_DIR = os.path.join(loc["config"], APP_NAME)
    else:
        print(colorize("using test values ...", Color.YELLOW))

    global DB_DIR

    DB_DIR = os.path.join(LIB_DIR, "db")
