from fnmatch import translate
from pprint import pprint
from urllib.error import HTTPError

import json
import requests

from bs4 import BeautifulSoup


from common import config
from . import topdrawer
from . import soccerwire

def compare_commits(commit_a: dict, commit_b: dict):
    name_a = commit_a["name"]
    name_b = commit_b["name"]

    if name_a < name_b:
        return -1
    elif name_a == name_b:
        return 0
    else:
        return 1


def find_commit(needle_commit: dict, commits: list):
    for haystack_commit in commits:
        if compare_commits(needle_commit, haystack_commit) == 0:
            return haystack_commit

    return None

def merge_commits(td_commit: dict, sw_commit: dict):
    """Merge two commits and come up with one that is a superset of the two."""
    commit = {}

    for key in td_commit:
        commit[key] = td_commit[key]

    for key in sw_commit:
        if key in commit:
            # The current attribute was found in the soccerwire commitment data.
            # Question: Which value do we take?  Who do we believe more?
            if commit[key] is None:
                commit[key] = sw_commit[key]
        else:
            # The current attribute was not found in the soccerwire commitment data.
            commit[key] = sw_commit[key]

    return commit

def get_commitments(gender: str, year: int):
    """Retrieve all of the commitments for a given gender and year."""

    merged_commits = []

    sw_commits = soccerwire.get_commitments(gender, year)
    td_commits = topdrawer.get_commitments(gender, year)

    # Now for the tricky bit!  
    # We have to merge the two lists without duplication.

    merged_commits.extend(sw_commits)

    for td_commit in td_commits:
        # Step 1: Check to see if this player appears in the set 
        #         attained from Soccerwire.  Do this by name.
        sw_commit = find_commit(td_commit, merged_commits)
        if sw_commit is not None:
            # We've found a matching name.
            # This means that td_commit and sw_commit appear to be the same person.
            # We need to merge the two to come up with the best of both worlds commit to return.
            commit = merge_commits(td_commit, sw_commit)
            merged_commits.append(commit)
        else:
            # There was no matching name, so add it.
            merged_commits.append(td_commit)

    return merged_commits