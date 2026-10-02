from dotenv import load_dotenv
import os
load_dotenv()

MCP_SERVER = "http://localhost:8000"


ORGANIZER_EMAIL = "deepmondal823@gmail.com"
ALLOW_DUPLICATE_EVENT = True
DATA_DIR = os.path.join("data")
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CALENDAR_CREDENTIALS_PATH = os.path.join(
    PROJECT_ROOT, "calender-server", "gcp-ouath.key.json"
)

MCP_SERVER =  {
    "ats": {
        "command" :"python",
        "args": [str(os.path.join(PROJECT_ROOT, "server", "server.py"))],
         "transport": "stdio",

    },
    "calendar": {
        "command": "npx.cmd",
         "args": ["@cocal/google-calendar-mcp"],
          "transport": "stdio",
          "env": {"GOOGLE_OAUTH_CREDENTIALS": CALENDAR_CREDENTIALS_PATH, **os.environ}

    },

     "email": {
        "command": "npx.cmd",
        "args": ["@gongrzhe/server-gmail-autoauth-mcp"],
        "transport": "stdio",
    }
}