import requests
import os
import re
import sys
from conans.tools import Version
from requests.auth import HTTPBasicAuth


class Github(object):

    GITHUB_API_URL = "https://api.github.com"
    GITHUB_PER_PAGE = 100

    def __init__(self, username=None, token=None, organization=None):
        user = username or os.getenv("GITHUB_USERNAME")
        token = token or os.getenv("GITHUB_API_KEY")
        self.ignore_errors = os.getenv("GITHUB_IGNORE_ERRORS", "1").lower() in ["1", "true", "yes"]
        self.organization = organization or os.getenv("GITHUB_ORGANIZATION", "bincrafters")
        self._auth = None
        if user and token:
            self._auth = HTTPBasicAuth(user, token)

    def get_total_pages(self, org):
        params = {"per_page": Github.GITHUB_PER_PAGE}
        url = "{}/orgs/{}/repos".format(Github.GITHUB_API_URL, org)
        response = requests.get(url, auth=self._auth, params=params)
        link = response.headers["Link"].split(',')[1]
        filter = re.search(r"page=(\d+)>", link)
        if filter:
            return int(filter.group(1))
        return 1

    def get_repo_list(self):
        page = 1
        last_page = self.get_total_pages(self.organization)
        json_data = []
        while page <= last_page:
            params = {"per_page": Github.GITHUB_PER_PAGE, "page": page}
            url = "{}/orgs/{}/repos".format(Github.GITHUB_API_URL, self.organization)
            response = requests.get(url, auth=self._auth, params=params)
            json_data.extend([(it.get("name"), it.get("default_branch")) for it in response.json()])
            page += 1
        return json_data

    def get_repo_branches(self, repository):
        url = "{}/repos/{}/{}/branches".format(Github.GITHUB_API_URL, self.organization, repository)
        response = requests.get(url, auth=self._auth)
        return [it.get("name") for it in response.json()]

    def extract_branch_version(self, branch):
        if not branch:
            return "0.0.0"
        return branch[branch.find('/') + 1:] if '/' in branch else branch

    def get_stable_branch(self, branches):
        def clean_branch_version(branch):
            if "_" in branch:
                branch = branch[:branch.find("_")]
            return branch

        stable_branch = None
        stable_branches = [clean_branch_version(branch) for branch in branches if
                           (branch.startswith("stable/") or branch.startswith("release/")) and
                           "master" not in branch]
        if not stable_branches:
            stable_branches = [clean_branch_version(branch) for branch in branches if
                               branch.startswith("testing/")]
        for branch in stable_branches:
            version = self.extract_branch_version(branch)
            stable_version = self.extract_branch_version(stable_branch)
            if Version(version) > Version(stable_version):
                stable_branch = branch
        if not stable_branches:
            stable_branch = branches[0]

        return stable_branch

    def set_default_branch(self, repository, default_branch):
        url = "{}/repos/{}/{}".format(Github.GITHUB_API_URL, self.organization, repository)
        body = {"default_branch": default_branch}
        response = requests.patch(url, auth=self._auth, json=body)
        response.raise_for_status()
        return response.ok

    def update_default_branch(self, repository):
        name, default_branch = repository

        print("Repository {} has been using '{}' as default branch".format(name, default_branch))
        branches = self.get_repo_branches(name) or [default_branch]
        new_default_branch = self.get_stable_branch(branches)
        if default_branch != new_default_branch:
            print("Repository {} will be updated to {}".format(name, new_default_branch))
            self.set_default_branch(name, new_default_branch)
            print("Repository {} has been updated with success".format(name))
        else:
            print("Repository {} is up-to-date".format(name))


if __name__ == "__main__":
    github = Github()
    print("=== BINCRAFTERS - UPDATE DEFAULT BRANCH ===")
    print("Collecting repositories for the organization {}".format(github.organization))
    repositories = github.get_repo_list()
    print("Found {} repositories".format(len(repositories)))
    for repo in repositories:
        try:
            print("\nChecking default branch for {}/{}".format(github.organization, repo[0]))
            github.update_default_branch(repo)
        except Exception as error:
            print("ERROR: {}".format(error))
            if not github.ignore_errors:
                sys.exit(1)
