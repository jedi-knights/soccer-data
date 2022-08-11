# from cli.common.config import GITHUB_DATA

from cli.common import config

def get_clubs():
    return config.load_github_data("https://raw.githubusercontent.com/ocrosby/soccer-data/main/org/ga/clubs.json")


def get_conferences():
    return config.load_github_data("https://raw.githubusercontent.com/ocrosby/soccer-data/main/org/ga/conferences.json")


def get_conference_name_from_cell(cell):
    if cell is None:
        return None

    elements = cell.find_all("strong")

    for element in elements:
        text = element.text
        text = text.strip()

        if len(text) > 0:
            text = text.upper()
            text = text.replace("CONFERENCE", "")
            text = text.strip()

            return text

    return None
