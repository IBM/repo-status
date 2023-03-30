import argparse
import base64
import os
import re
import time

import requests

parser = argparse.ArgumentParser(
    prog="status.py",
    description="""Create a CSV file with the status of repositories in the organization,
  assumes environment variable \"GH_TOKEN\" is already set with a valid token
  for making API calls.""",
)
parser.add_argument(
    "-o",
    "--org",
    help="Required: The name of the org in which to scan for repository status.",
    required=True,
)
parser.add_argument(
    "-u",
    "--url",
    default="https://api.github.com",
    help='Optional: The API url to call, defaults to "https://api.github.com".',
)
args = parser.parse_args()

date = time.strftime("%Y-%m-%d")

api_url = args.url
org_name = args.org
headers = {
    "Authorization": f"Bearer {os.environ.get('GH_TOKEN')}",
    "Accept": "application/vnd.github+json",
}
repos_path = f"/orgs/{org_name}/repos"

session = requests.Session()


def get_status(repo_readme: str):
    pattern = re.compile(
        "^.*https:\\/\\/img.shields.io\\/badge\\/status-(\\w+)%20.*$", flags=re.M | re.I
    )
    match = pattern.search(repo_readme)
    if match is None:
        return None
    return pattern.search(repo_readme).group(1)


def get_pages(url: str, headers):
    first_page = session.get(url, headers=headers)
    yield first_page

    next_page = first_page
    while next_page.links.get("next", None) is not None:
        next_page_url = next_page.links["next"]["url"]
        next_page = session.get(next_page_url, headers=headers)
        yield next_page


def controls_file_exists(repo_name: str):
    return (
        "content"
        in requests.get(
            f"{api_url}/repos/{org_name}/{repo_name}/contents/docs/controls.md",
            headers=headers,
        )
        .json()
        .keys()
    )


def get_server(url: str):
    server_pattern = re.compile("^.*github\\.?(\\w+)?\\.com$", flags=re.I)
    server = server_pattern.search(url)
    if server.group(1) is None:
        return "public"
    return server.group(1)


with open(f"status-{org_name}-{date}.csv", "w") as file:
    file.write("server,org-name,repo,status,controls.md-exists\n")
    server_name = get_server(api_url)
    for page in get_pages(api_url + repos_path, headers=headers):
        for repo in page.json():
            resp = requests.get(
                f"{api_url}/repos/{org_name}/{repo['name']}/readme", headers=headers
            )
            if resp.status_code != 200:
                file.write(
                    f"{server_name},{org_name},{repo['name']},None,{controls_file_exists(repo['name'])}\n"  # noqa: E501
                )
                continue
            readme = base64.b64decode(resp.json()["content"]).decode("utf-8")
            file.write(
                f"{server_name},{org_name},{repo['name']},{get_status(readme)},{controls_file_exists(repo['name'])}\n"  # noqa: E501
            )
