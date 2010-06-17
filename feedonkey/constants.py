import os.path
import os

CONFIG_DIR = os.path.expanduser("~/.feedonkey/")

if not os.path.exists(CONFIG_DIR):
    os.mkdir(CONFIG_DIR)
