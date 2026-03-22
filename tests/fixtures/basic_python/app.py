import pickle
from os.path import *

import yaml

API_KEY = "sk-1234567890abcdef1234567890abcdef"
PASSWORD = "supersecretpassword123"

def process_data(items=[]):
    result = ""
    for item in items:
        result += str(item)
    return result

def dangerous(user_input):
    return eval(user_input)

data = yaml.load(open("config.yaml"))
obj = pickle.load(open("data.pkl", "rb"))

try:
    risky()
except:
    pass
