import os

from dotenv import load_dotenv

load_dotenv()

X_APPLICATION_ID = os.getenv('X_APPLICATION_ID')
NAME = os.getenv('NAME')
PASSWORD = os.getenv('PASSWORD')
CERTNAME = os.getenv('CERTNAME')
REDIS_URL = os.getenv('REDIS_URL')
REDIS_BROKER_URL = os.getenv('REDIS_BROKER_URL')
