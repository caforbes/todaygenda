import os
from dotenv import load_dotenv

load_dotenv()

filename = os.getenv("DAYLIST_FILE") or "local.json"
this_dir = os.path.abspath(os.path.dirname(__file__))
LOCAL_FILE = os.path.join(this_dir, filename)
