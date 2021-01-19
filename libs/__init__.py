import os

LIB_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(LIB_DIR)
USER_DATA_DIR = os.path.join(ROOT_DIR, "userData")
DOWNLOAD_DIR = os.path.join(USER_DATA_DIR, "downloads")
URL_FILE = os.path.join(USER_DATA_DIR, "urlfile")
