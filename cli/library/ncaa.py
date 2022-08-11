import requests

from bs4 import BeautifulSoup

def _get_rpi_ranking(row):
    cells = row.findChildren("td")
    ranking = {
        "rank": int(cells[0].text.strip()),
        "school": cells[1].text.strip(),
        "points": int(cells[2].text.strip()),
        "record": cells[3].text.strip(),
        "previous": cells[4].text.strip(),
    }

    return ranking

def _get_di_rpi_ranking(row):
    cells = row.findChildren("td")
    ranking = {
        "rank": int(cells[0].text.strip()),
        "school": cells[1].text.strip(),
        "conference": cells[2].text.strip(),
        "record": cells[3].text.strip(),
        "road": cells[4].text.strip(),
        "neutral": cells[4].text.strip(),
        "non-div-i": cells[5].text.strip(),
    }

    return ranking


def get_rpi_rankings():
    url = "https://www.ncaa.com/rankings/soccer-women/d1/ncaa-womens-soccer-rpi"

    response = requests.get(url)

    response.raise_for_status()

    rankings = []

    soup = BeautifulSoup(response.content, "html.parser")

    table = soup.find("table")
    body = table.find("tbody")
    rows = body.find_all("tr", recursive=False)

    for row in rows:
        rankings.append(_get_di_rpi_ranking(row))

    return rankings


def _get_usc_2d_ranking(row):
    cells = row.findChildren("td")
    ranking = {
        "rank": int(cells[0].text.strip()),
        "school": cells[1].text.strip(),
        "previous": cells[2].text.strip(),
        "record": cells[3].text.strip(),
    }

    return ranking


def get_usc_d1_rankings():
    url = "https://www.ncaa.com/rankings/soccer-women/d1/united-soccer-coaches"

    response = requests.get(url)

    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")

    table = soup.find("table")
    body = table.find("tbody")
    rows = body.find_all("tr", recursive=False)

    rankings = []
    for row in rows:
        rankings.append(_get_usc_2d_ranking(row))

    return rankings


def get_usc_d2_rankings():
    url = "https://unitedsoccercoaches.org/rankings/college-rankings/ncaa-dii-women/"

    response = requests.get(url)

    response.raise_for_status()

    rankings = []

    soup = BeautifulSoup(response.content, "html.parser")

    table = soup.find("table", class_="rankingsTable")
    body = table.find("tbody")
    rows = body.find_all("tr", recursive=False)

    for row in rows:
        rankings.append(_get_usc_2d_ranking(row))

    return rankings


def get_schools(division: str):
    if division == "di":
        url = "https://web3.ncaa.org/directory/api/directory/memberList?type=12&division=I&_=1658873231181"
    elif division == "dii":
        url = "https://web3.ncaa.org/directory/api/directory/memberList?type=12&division=II&_=1658873247608"
    elif division == "diii":
        url = "https://web3.ncaa.org/directory/api/directory/memberList?type=12&division=III&_=1658872974705"
    else:
        return []

    response = requests.get(url)

    response.raise_for_status()

    records = response.json()

    schools = []
    for record in records:
        school = {
            "name": record["nameOfficial"],
            "conference": record["conferenceName"],
            "private": record["privateFlag"],
            "hbcu": record["historicallyBlackFlag"],
            "state": record["memberOrgAddress"]["state"]
        }
        schools.append(school)

    return schools
