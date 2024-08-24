import os
from dotenv import load_dotenv

load_dotenv()

this_dir = os.path.abspath(os.path.dirname(__file__))
LOCAL_FILE = os.path.join(this_dir, os.getenv("DAYLIST_FILE"))
