import bs4
import json
import requests
import uuid

url = "https://www.usysnationalleague.com/elite-64-club-directory/"


def process_conference(el, title):
    clubs = []

    if title == "Boys Clubs":
        gender = "Male"
    else:
        gender = "Female"

    conference_name = None
    for child in el.children:
        if child.name == "a":
            club = {
                "id": str(uuid.uuid4()),
                "name": child.text.strip(),
                "url": child["href"].strip(),
                "gender": gender
            }
            clubs.append(club)
        elif child.name == "u":
            conference_name = child.text.strip()

    for club in clubs:
        if conference_name is not None:
            club["conference"] = conference_name

    return clubs

def process_accordion(el):
    clubs = []

    title = None
    for child in el.children:
        if child.name == "h3":
            title = child.text.strip()
        elif child.name == "div":
            cells = el.findChildren("td")
            for cell in cells:
                clubs.extend(process_conference(cell, title))

    return clubs

def contains_club(name: str, clubs: list):
    for club in clubs:
        if club["name"] == name:
            return True

    return False

def get_club_by_name(name: str, clubs: list):
    for club in clubs:
        if club["name"] == name:
            return club

    return None

def get_normal_clubs(clubs):
    normal_clubs = []

    for club in clubs:
        normal_club = get_club_by_name(club["name"], normal_clubs)
        if normal_club is None:
            normal_club = {
                "id": str(uuid.uuid4()),
                "name": club["name"],
                "conference": club["conference"],
                "url": club["url"]
            }

            normal_clubs.append(normal_club)

    return normal_clubs

if __name__ == "__main__":
    response = requests.get(url)
    response.raise_for_status()

    soup = bs4.BeautifulSoup(response.content, "html.parser")

    clubs = []

    accordions = soup.find_all("div", class_=["accordion"])
    for accordion in accordions:
        clubs.extend(process_accordion(accordion))

    clubs = get_normal_clubs(clubs)

    print(f"Retrieved {len(clubs)} clubs")

    data = {
        "data": clubs
    }

    with open("elite64_clubs.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4, sort_keys=True)    
