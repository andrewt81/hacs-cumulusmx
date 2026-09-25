"""Open one review issue per upstream stable release; never modify integration code."""
import json
import os
import re
import urllib.request

API = "https://api.github.com"
UPSTREAM = "cumulusmx/CumulusMX"
LABEL = "upstream-review"
KEYWORDS = re.compile(r"api|web.?tag|json|sensor|breaking|deprecat|weather station", re.I)


def request(url, token=None, method="GET", data=None):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "cumulusmx-ha-release-check"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if data is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(data).encode()
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers, method=method, data=data), timeout=20) as response:
        return json.load(response)


def main():
    token = os.environ["GH_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]
    latest = request(f"{API}/repos/{UPSTREAM}/releases/latest")
    release_id = latest["id"]
    title = f"Review Cumulus MX upstream release #{release_id}: {latest['name']}"
    issues = request(f"{API}/repos/{repo}/issues?state=all&per_page=100&labels={LABEL}", token)
    if any(issue["title"] == title for issue in issues):
        print("Already tracked:", title)
        return
    notes = latest.get("body") or "No release notes provided. Inspect the upstream changelog."
    matches = [line for line in notes.splitlines() if KEYWORDS.search(line)]
    body = (f"Upstream release: {latest['html_url']}\n\nRelevant release note lines:\n"
            + ("\n".join(matches[:40]) if matches else "No API or sensor keywords found in release notes.")
            + "\n\nChecklist: compare web tags and units; test on a real instance; update compatibility notes; publish a new integration release only if necessary.")
    request(f"{API}/repos/{repo}/issues", token, "POST", {"title": title, "body": body, "labels": [LABEL]})
    print("Created:", title)


if __name__ == "__main__":
    main()
