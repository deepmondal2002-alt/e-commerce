import os
import base64
import requests
from langchain_core.tools import tool

BASE_URL = os.getenv("GITHUB_API_URL", "https://api.github.com/repos/OWNER/REPO")
PR_NUMBER = os.getenv("PR_NUMBER", "1")
HEADERS = {
    "Authorization": f"token {os.getenv('GITHUB_TOKEN')}",
    "Accept": "application/vnd.github.v3+json",
}


@tool
def get_pr_details() -> dict:
    """Fetch PR title, description, author, and current status."""
    url = f"{BASE_URL}/pulls/{PR_NUMBER}"
    r = requests.get(url, headers=HEADERS)
    pr = r.json()
    return {
        "title": pr.get("title"),
        "description": pr.get("body", "no description provided"),
        "author": pr["user"]["login"],
        "state": pr.get("state"),
        "branch": pr["head"]["ref"],
    }


@tool
def get_pr_files() -> list:
    """List all files changed in the PR with their status and patch."""
    url = f"{BASE_URL}/pulls/{PR_NUMBER}/files"
    r = requests.get(url, headers=HEADERS)
    files = []
    for f in r.json():
        files.append({
            "filename": f.get("filename"),
            "status": f.get("status"),
            "changes": f.get("changes"),
            "path": f.get("path", "")[:2000],
        })
    return files


@tool
def get_files(file_path: str) -> str:
    """Fetch the full content of a file from the repo default branch."""
    url = f"{BASE_URL}/contents/{file_path}"
    r = requests.get(url, headers=HEADERS)
    data = r.json()
    if "content" not in data:
        return f"could not fetch : {file_path}"
    return base64.b64decode(data["content"]).decode("utf-8")


@tool
def post_pr_comment(comment: str) -> dict:
    """Post a review comment on the PR."""
    url = f"{BASE_URL}/issues/{PR_NUMBER}/comments"
    payload = {"body": comment}
    r = requests.post(url, headers=HEADERS, json=payload)
    return {"status": r.status_code, "comment_url": r.json().get("html_url")}
