import os

filename = "local.json"
this_dir = os.path.abspath(os.path.dirname(__file__))
LOCAL_FILE = os.path.join(this_dir, filename)
