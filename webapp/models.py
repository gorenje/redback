import os, secrets, base64, json, peewee, uuid, traceback, numpy, re, requests
import urllib3, logging

from datetime               import datetime, timedelta
from peewee                 import *
from playhouse.postgres_ext import *
from playhouse.signals      import Model, post_save, pre_save
from dotenv                 import dotenv_values
from urllib.parse           import urlparse

# load_dotenv()
config = {
    **dotenv_values("../.env"),  # load shared development variables
    **dotenv_values(".env"),  # load shared development variables
    **os.environ,  # override loaded values with environment variables
}

if os.environ.get("ENV_FILE") != None:
    config = { **config, **dotenv_values(os.environ.get("ENV_FILE")) }
