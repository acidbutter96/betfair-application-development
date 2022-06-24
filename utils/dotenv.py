import os

from dotenv import load_dotenv

load_dotenv()

X_APPLICATION_ID = os.getenv('X_APPLICATION_ID')
NAME = os.getenv('NAME')
PASSWORD = os.getenv('PASSWORD')
CERTNAME = os.getenv('CERTNAME')
