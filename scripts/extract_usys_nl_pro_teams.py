import bs4
import json
import requests
import uuid

url = "https://www.usysnationalleague.com/national-league-pro-2021-22-teams/"


def get_age_group_from_title(title: str) -> str:
    return title.split(" ")[0]


def get_gender_from_title(title: str) -> str:
    tokens = title.split(" ")
    if tokens[-1] == "BOYS":
        return "Male"

    return "Female"


def get_team(el):
    cells = el.findChildren("td")
    
    team = {
        "id": str(uuid.uuid4()),
        "group": cells[0].text.strip(),
        "team": cells[1].text.strip(),
        "pair": cells[2].text.strip(),
        "event1": cells[3].text.strip(),
        "event2": cells[4].text.strip()
    }

    return team

def process_age_group(el, gender, age_group):
    print(f"Processing {gender} {age_group} ...")

    teams = []

    rows = el.find_all("tr")
    for row in rows:
        team = get_team(row)

        # Skips the header
        if team["group"] == "GROUP":
            continue

        team["gender"] = gender
        team["age_group"] = age_group
        teams.append(team)

    return teams

def process_accordion(el):
    title = None
    gender = None
    age_group = None

    teams = []
    for child in el.children:
        if child.name == "h3":
            title = child.text.strip()
            gender = get_gender_from_title(title)
            age_group = get_age_group_from_title(title)
        elif child.name == "div":
            teams.extend(process_age_group(child, gender, age_group))
        else:
            # Todo: Deal with an unexpected element
            pass

    return teams

if __name__ == "__main__":
    response = requests.get(url)
    response.raise_for_status()

    soup = bs4.BeautifulSoup(response.content, "html.parser")

    teams = []

    accordions = soup.find_all("div", class_=["accordion"])
    for accordion in accordions:
        teams.extend(process_accordion(accordion))

    print(f"Retrieved {len(teams)} teams")

    data = {
        "data": teams
    }

    with open("nlpro_teams.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4, sort_keys=True)    
