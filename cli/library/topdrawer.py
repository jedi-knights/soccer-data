import re
from xmlrpc.client import boolean
import bs4
import requests

from cli.common import tools
from cli.common import config

from . import ga
from . import ecnl

PREFIX = "https://www.topdrawersoccer.com"


def get_identifier_from_url(url):
    if url is None:
        return None

    url = url.strip()
    if len(url) == 0:
        return None

    tokens = url.split('/')
    last_segment = tokens[-1]

    tokens = last_segment.split('-')
    buffer = tokens[-1]
    identifier = int(buffer)

    return identifier


def get_conferences_content(division: str):
    """Returns the HTML from the college conferences page."""
    url = "https://www.topdrawersoccer.com/college-soccer/college-conferences"

    suffix = ""

    division_mapping = config.load_github_data("https://raw.githubusercontent.com/ocrosby/soccer-data/main/org/tds/division_mapping.json")
    if division in division_mapping:
        suffix = division_mapping[division]

    url = url + suffix
    response = requests.get(url)

    response.raise_for_status()

    return response.content

def get_conference_commitments_content(gender: str, division: str, conference_name: str):
    """Returns the HTML from the given conferences commitments page."""
    conference = get_conference(gender, division, conference_name)

    if conference is None:
        return None

    url = conference["url"] + "/tab-commitments"

    response = requests.get(url)

    response.raise_for_status()

    return response.content


def get_conferences(gender: str, division: str):
    """Return a list of all conferences."""
    conferences = []

    content = get_conferences_content(division)
    soup = bs4.BeautifulSoup(content, "html.parser")
    columns = soup.find_all("div", class_=["col-lg-6"])

    for column in columns:
        heading = column.find("div", class_=["heading-rectangle"]).text.strip()

        if gender == "male" and "Men's" not in heading:
            continue

        if gender == "female" and "Women's" not in heading:
            continue

        table = column.find("table", class_=["table_stripped", "tds_table"])
        cells = table.find_all("td")

        for cell in cells:
            url = PREFIX + cell.find("a")["href"]
            conferences.append({
                "id": int(url.split('/')[-1].split('-')[-1]),
                "name": cell.text.strip(),
                "url": url
            })

    return conferences


def get_conference(gender: str, division: str, conference_name: str):
    """Return a conference by name."""
    conferences = get_conferences(gender, division)

    for conference in conferences:
        if conference["name"] == conference_name:
            return conference

    return None


def _get_league(club_name: str):
    if club_name is None:
        return "Other"

    if len(club_name) == 0:
        return "Other"

    translated_club_name = config.translate_club_name(club_name)

    ecnl_clubs = config.load_github_data("https://raw.githubusercontent.com/ocrosby/soccer-data/main/org/ecnl/clubs.json")
    ga_clubs = config.load_github_data("https://raw.githubusercontent.com/ocrosby/soccer-data/main/org/ga/clubs.json")
    elite64_clubs = config.load_github_data("https://raw.githubusercontent.com/ocrosby/soccer-data/main/org/usys/elite64/clubs.json")

    if tools.is_member_club(translated_club_name, ecnl_clubs):
        return "ECNL"
    elif tools.is_member_club(translated_club_name, ga_clubs):
        return "GA"
    elif tools.is_member_club(translated_club_name, elite64_clubs):
        return "Elite64"
    else:
        # if club_name != translated_club_name:
        #     print(f"Could not find translated club '{club_name}' -> '{translated_club_name}'")
        # else:
        #     print(f"Could not find the club '{club_name}'")

        return "Other"


def _extract_school_commits(element):
    tables = element.find_all("table", class_=["table-striped", "tds-table", "female"])

    body = None
    for table in tables:
        header = table.find("thead", class_="female")
        if header is not None:
            body = table.find("tbody")

    if body is None:
        return []

    players = []
    rows = body.find_all("tr")
    for row in rows:
        columns = row.find_all("td")

        player = {
            "id": -1,
            "name": tools.get_anchor_text(columns[0]),
            "url": tools.get_anchor_url(columns[0], PREFIX),
            "year": columns[1].text.strip(),
            "position": columns[2].text.strip(),
            "city": columns[3].text.strip(),
            "state": columns[4].text.strip(),
            "club": columns[5].text.strip().replace("  ", " ")
        }

        # print(f"Loading details for player '{player['name']}' ...")
        load_player_details(player)
        # print("Details loaded successfully")

        player["id"] = _get_id_from_url(player["url"])
        player["club"] = config.translate_club_name(player["club"])
        player["league"] = _get_league(player["club"])

        # print(f"Adding '{player['name']}' to '{school['name']}' ...")
        players.append(player)

    return players


def _get_id_from_url(url: str):
    if url is None:
        return -1

    url = url.strip()
    tokens = url.split("/")
    last_token = tokens[-1]
    parts = last_token.split("-")
    last_part = parts[-1]

    identifier = int(last_part)

    return identifier


def _extract_conference_commits(element, year: int = 0):
    tables = element.find_all("table", class_=["table-striped", "tds-table", "female"])

    body = None
    for table in tables:
        header = table.find("thead", class_="female")
        if header is not None:
            body = table.find("tbody")

    if body is None:
        return []

    school_mapping = {}
    anchors = element.find_all("a", class_=["player-name"])
    for anchor in anchors:
        href = anchor["href"]
        name = anchor.text.strip()

        school_mapping[name] = {
            "name": name,
            "url": PREFIX + href,
            "clgid": int(href.split("/")[-1].split("-")[-1])
        }

    schools = []
    rows = body.find_all("tr")
    for row in rows:
        columns = row.find_all("td")
        if len(columns) == 1:
            school = {
                "name": columns[0].text.strip(),
                "players": []
            }

            if school["name"] in school_mapping:
                item = school_mapping[school["name"]]
                school["url"] = item["url"]
                school["clgid"] = item["clgid"]
            # print(f"Adding school {school['name']} ...")
            schools.append(school)
        else:
            if year > 0:
                grad_year = columns[1].text.strip()

                if int(grad_year) == year:
                    player = {
                        "name": columns[0].text.strip(),
                        "url": PREFIX + columns[0].find("a")["href"],
                        "year": grad_year,
                        "position": columns[2].text.strip(),
                        "city": columns[3].text.strip(),
                        "state": columns[4].text.strip(),
                        "club": columns[5].text.strip().replace("  ", " "),
                        "commitment": school["name"],
                        "commitmentUrl": None
                    }

                    if "url" in school:
                        player["commitmentUrl"] = school["url"]

                    # print(f"Loading details for player '{player['name']}' ...")
                    load_player_details(player)
                    # print("Details loaded successfully")

                    player["club"] = config.translate_club_name(player["club"])
                    player["league"] = _get_league(player["club"])

                    # print(f"Adding '{player['name']}' to '{school['name']}' ...")
                    school["players"].append(player)
            else:
                # If the year is less than or equal to 0 completely skip loading players,
                # it just takes way too long.
                pass

    return schools


def lookup_conference(conference_name: str, division: str) -> boolean:
    division = division.strip().lower()
    division = division.replace("iii", "3")
    division = division.replace("ii", "2")
    division = division.replace("i", "1")

    conferences = config.load_github_data(f"https://github.com/ocrosby/soccer-data/raw/main/org/college/ncaa/divisions/{division}/conferences.json")

    for conference in conferences:
        if conference["name"] == conference_name:
            return conference

    return None


def lookup_division_by_conference(conference_name: str):
    """Given a conference name this function looks through all organizations to determine the division"""

    divisions = ["d1", "d2", "d3"]
    for division in divisions:
        conference = lookup_conference(conference_name, division)
        if conference is not None:
            return division

    return None


def get_conference_commitment_chart_data(gender: str, division: str, name: str, cfid: int, year: int):
    if name == "All":
        schools = []

        if gender == "male":
            gender = "Male"

        if gender == "female":
            gender = "Female"

        division = division.strip()
        division = division.lower()
        division = division.replace("i", "1")
        division = division.replace("ii", "2")
        division = division.replace("iii", "3")
        division = division.upper()
        conferences = config.GITHUB_DATA["TDS"]["College"]["NCAA"][division]["Conferences"][gender]
        for conference in conferences:
            details = get_conference_details(gender, conference["name"], conference["id"], year)
            schools.extend(details)
    else:
        schools = get_conference_details(gender, name, cfid, year)

    leagues = []
    players = []
    for school in schools:
        for player in school["players"]:
            players.append(player)
            if player["league"] not in leagues:
                leagues.append(player["league"])

    leagues.sort()

    records = []
    for league in leagues:
        record = {"name": '', "league": league, "value": 0}
        for player in players:
            if player["league"] == league:
                record["value"] += 1

        record["name"] = league + " " + str(round(100 * (record["value"] / len(players)))) + "%"
        records.append(record)

    return records


def get_conference_commits(gender: str, division: str, conference_name: str, year: int = 0):
    if conference_name != "All":
        content = get_conference_commitments_content(gender, division, conference_name)

        if content is None:
            return None

        soup = bs4.BeautifulSoup(content, "html.parser")

        return _extract_conference_commits(soup, year)
    else:
        commits = []
        conferences = get_conferences(gender, division)

        for conference in conferences:
            commits.extend(get_conference_commits(gender, division, conference["name"], year))
        
        return commits


def _get_player_rating(element):
    span = element.find("span", class_=["rating"])

    if span is None:
        return None

    rating = span["style"]
    rating = int(rating.split(':')[-1].split('%')[0]) // 20

    if rating > 0:
        rating = str(rating) + ' star'
    else:
        rating = "Not Rated"

    return rating


def _get_player_position(element):
    div = element.find("div", class_=["player-position"])

    if div is None:
        return None

    buffer = div.text.strip()
    tokens = buffer.split("-")
    position = tokens[0].strip()

    return position


def _get_player_year(element):
    div = element.find("div", class_=["player-position"])

    if div is None:
        return None

    buffer = div.text.strip()
    tokens = buffer.split("-")

    if len(tokens) > 1:
        year = tokens[1].strip()
        tokens = year.split(" ")
        year = tokens[-1]
    else:
        year = None

    return year


def _get_player_commitment(element):
    div = element.find("div", class_=["player-position"])
    if div is None:
        return None

    anchor = div.find('a')
    if anchor is None:
        return None

    commitment = anchor.text
    commitment = commitment.strip()

    return commitment


def _get_player_commitment_url(element):
    div = element.find("div", class_=["player-position"])
    if div is None:
        return None

    anchor = div.find('a')
    if anchor is None:
        return None

    url = anchor["href"]
    url = url.strip()
    url = PREFIX + url

    return url


def _load_profile_grid_settings(element, details):
    container = element.find("ul", class_=["profile_grid"])

    if container is None:
        return

    items = container.findChildren("li")

    for item in items:
        lvalue, rvalue = item.text.strip().split(":")

        lvalue = lvalue.strip()
        rvalue = rvalue.strip()

        if lvalue == "Club":
            details["club"] = rvalue
        elif lvalue == "Team Name":
            details["team"] = rvalue
        elif lvalue == "Jersey Number":
            details["jerseyNumber"] = rvalue
        elif lvalue == "High School":
            details["highSchool"] = rvalue
        elif lvalue == "Region":
            details["region"] = rvalue
        else:
            print("Unknown lvalue " + lvalue + " on player detail page.")


def get_committed_players_for_school(gender: str, school_name: str, clgid: int):
    gender = _normalize_gender(gender)
    school_name = _normalize_school_name(school_name)
    clgid = str(clgid)

    url = f"https://www.topdrawersoccer.com/college-soccer/college-soccer-details/{gender}/{school_name}/clgid-{clgid}/tab-commitments"

    response = requests.get(url)
    response.raise_for_status()

    soup = bs4.BeautifulSoup(response.content, "html.parser")

    players = _extract_school_commits(soup)

    return players


def load_player_details(player):
    if player is None:
        return

    if "url" not in player:
        return

    response = requests.get(player["url"])

    response.raise_for_status()

    soup = bs4.BeautifulSoup(response.content, "html.parser")

    _load_profile_grid_settings(soup, player)

    player["league"] = _get_league(player["club"])
    player["year"] = _get_player_year(soup)
    player["rating"] = _get_player_rating(soup)
    player["position"] = _get_player_position(soup)

    if "commitment" not in player:
        player["commitment"] = _get_player_commitment(soup)

    if "commitmentUrl" not in player:
        player["commitmentUrl"] = _get_player_commitment_url(soup)


def _get_transfer_position(cell):
    caption = cell.text.strip()
    if caption == "Player":
        return None

    if "\xa0" in caption:
        return caption.split("\xa0")[0].strip()

    return caption.split(" ")[0].strip()


def _get_transfer_name(cell):
    caption = cell.text.strip()
    if caption == "Player":
        return None

    if "\xa0" in caption:
        return caption.split("\xa0")[1].strip()

    return " ".join(caption.split(" ")[1:]).strip()


def _get_transfer(row):
    try:
        cells = row.find_all("td")

        name = _get_transfer_name(cells[0])
        print(f"Processing '{name}'")

        if name is None or len(name) == 0:
            return None

        transfer = {
            "name": name,
            "position": None,
            "url": None,
            "formerSchoolName": None,
            "formerSchoolUrl": None,
            "newSchoolName": None,
            "newSchoolUrl": None
        }

        transfer["position"] = _get_transfer_position(cells[0])
        transfer["url"] = tools.get_anchor_url(cells[0], PREFIX)

        if len(cells) > 1:
            transfer["formerSchoolName"] = tools.get_anchor_text(cells[1])
            transfer["formerSchoolUrl"] = tools.get_anchor_url(cells[1], PREFIX)

        if len(cells) > 2:
            transfer["newSchoolName"] = tools.get_anchor_text(cells[2])
            transfer["newSchoolUrl"] = tools.get_anchor_url(cells[2], PREFIX)

    except Exception as err:
        print(row.text)
        print(err)

    print(transfer)

    return transfer


def get_transfers():
    url = "https://www.topdrawersoccer.com/college-soccer-articles/2022-womens-di-transfer-tracker_aid50187"

    response = requests.get(url)
    response.raise_for_status()

    soup = bs4.BeautifulSoup(response.content, "html.parser")
    rows = soup.find_all("tr")

    transfers = []
    for row in rows:
        player = _get_transfer(row)
        if player is None:
            continue

        transfers.append(player)

    return transfers


def _generate_player_suffix(gender: str, position: str, grad_year: str, region: str, state: str, page: int):
    suffix = "&genderId=" + gender
    suffix += "&positionId=" + str(position)
    suffix += "&graduationYear=" + grad_year
    suffix += "&regionId=" + str(region)
    suffix += "&countyId=" + str(state)
    suffix += "&pageNo=" + str(page)
    suffix += "&area=clubplayer&sortColumns=0&sortDirections=1&search=1"

    return suffix


def _get_search_pages(element):
    pagination = element.find("ul", class_=["pagination"])

    if pagination is None:
        return []

    page_items = pagination.findChildren("li", class_=["page-item"])

    pages = []
    for page_item in page_items:
        text = page_item.text.strip()

        if text in ["Previous", "1", "Next"]:
            continue

        pages.append(int(text))

    return pages


def _extract_club(item):
    buffer = item.find("div", class_="ml-2").text.strip()
    target = buffer.split('\t\t\t\t')[1].strip()
    pieces = target.split('/')

    if len(pieces) >= 1:
        return pieces[0]

    return None


def _extract_high_school(item):
    buffer = item.find("div", class_="ml-2").text.strip()
    target = buffer.split('\t\t\t\t')[1].strip()
    pieces = target.split('/')

    if len(pieces) == 1:
        high_school = None
    elif len(pieces) == 2:
        high_school = pieces[1]
    else:
        high_school = None

    return high_school


def _extract_image_url(item):
    image = item.find("img", class_="imageProfile")

    if image is not None:
        return PREFIX + image["src"]

    return None


def _extract_rating(item):
    rating = item.find("span", class_="rating")["style"]
    rating = int(rating.split(':')[-1].split('%')[0]) // 20

    if rating > 0:
        rating = str(rating) + ' star'
    else:
        rating = "Not Rated"

    return rating


def _extract_commitment(item):
    commitment_span = item.find("span", class_="text-uppercase")

    if commitment_span is not None:
        anchor = commitment_span.find("a")
        return anchor.text.strip()

    return None


def _extract_commitment_url(item):
    commitment_span = item.find("span", class_="text-uppercase")

    if commitment_span is not None:
        anchor = commitment_span.find("a")
        return PREFIX + anchor["href"]

    return None


def _extract_player_id(item):
    name_anchor = item.find("a", class_="bd")

    return name_anchor["href"].split('/')[-1].split('-')[-1]


def _extract_player_name(item):
    name_anchor = item.find("a", class_="bd")

    return name_anchor.text.strip()


def _extract_player_url(item):
    name_anchor = item.find("a", class_="bd")

    return PREFIX + name_anchor["href"]


def _get_searched_player(element):
    return {
        "id": _extract_player_id(element),
        "name": _extract_player_name(element),
        "url": _extract_player_url(element),
        "imageUrl": _extract_image_url(element),
        "position": element.find("div", class_="col-position").text.strip(),
        "club": _extract_club(element),
        "highSchool": _extract_high_school(element),
        "rating": _extract_rating(element),
        "year": element.find("div", class_="col-grad").text.strip(),
        "state": element.find("div", class_="col-state").text.strip(),
        "commitment": _extract_commitment(element),
        "commitmentUrl": _extract_commitment_url(element)
    }


def _get_searched_players(element):
    players = []

    items = element.find_all("div", class_=["item"])
    for item in items:
        players.append(_get_searched_player(item))

    return players


def search_for_players(gender: str, position: str, grad_year: str, region: str, state: str):
    suffix = _generate_player_suffix(gender, position, grad_year, region, state, 0)

    url = "https://www.topdrawersoccer.com/search/?query="

    response = requests.get(url + suffix)
    response.raise_for_status()

    soup = bs4.BeautifulSoup(response.content, "html.parser")

    players = _get_searched_players(soup)

    pages = _get_search_pages(soup)
    for page in pages:
        suffix = _generate_player_suffix(gender, position, grad_year, region, state, page - 1)

        response = requests.get(url + suffix)
        response.raise_for_status()

        soup = bs4.BeautifulSoup(response.content, "html.parser")

        players.extend(_get_searched_players(soup))

    return players


def _normalize_school_name(name: str):
    if name is None:
        return None

    name = name.strip()
    name = name.lower()
    name = name.replace(" ", "-")
    name = name.replace(".", "")
    name = name.replace("'", "")

    return name


def _normalize_gender(gender: str):
    if gender is None:
        return None

    gender = gender.strip()

    if len(gender) == 0:
        return "male"

    gender = gender.lower()

    if gender == "male":
        return "men"

    if gender == "female":
        return "women"

    return "men"


def get_college_details(gender: str, name: str, clgid: int):
    gender = _normalize_gender(gender)
    name = _normalize_school_name(name)
    clgid = str(clgid)

    url = f"https://www.topdrawersoccer.com/college-soccer/college-soccer-details/{gender}/{name}/clgid-{clgid}"

    response = requests.get(url)
    response.raise_for_status()

    soup = bs4.BeautifulSoup(response.content, "html.parser")

    header = soup.find("th", text=re.compile(r"Program Information"))
    table = header.parent.parent.parent
    body = table.find("tbody")
    rows = body.findChildren("tr")

    details = {}
    for row in rows:
        cells = row.findChildren("td")
        attribute = cells[0].text.strip()

        if len(attribute) > 0 and attribute[-1] == ':':
            attribute = attribute[:-1]  # Omit the trailing colon.

        attribute = attribute.strip()  # Strip one more time just in case.

        cell = cells[1]
        if attribute == "Conference":
            details["conference"] = tools.get_anchor_text(cell)
            details["conferenceUrl"] = tools.get_anchor_url(cell, PREFIX)
        elif attribute == "Nickname":
            details["nickname"] = cell.text.strip()
        elif attribute == "State":
            details["state"] = cell.text.strip()
        elif attribute == "City":
            details["city"] = cell.text.strip()
        elif attribute == "Enrollment":
            details["enrollment"] = int(cell.text.strip())
        elif attribute == "Head Coach":
            details["coach"] = cell.text.strip()
        elif attribute == "Phone Number":
            details["phone"] = cell.text.strip()
        else:
            # Do nothing for now
            pass

    return details


def get_player_details(name: str, pid: int):
    player = {"id": pid, "name": name}
    pid = str(pid)

    name = name.strip().lower().replace(" ", "-")
    player["url"] = f"https://www.topdrawersoccer.com/club-player-profile/{name}/pid-{pid}"

    load_player_details(player)

    return player


def get_conference_details(gender: str, name: str, cfid: int, year: int = 0):
    gender = gender.strip().lower()

    if gender == "male":
        gender = "men"
    elif gender == "female":
        gender = "women"

    name = name.strip().lower().replace(" ", "-")
    cfid = str(cfid)

    url = "https://www.topdrawersoccer.com/college-soccer/college-conferences/conference-details/"
    url += f"{gender}/{name}/cfid-{cfid}/tab-commitments#commitments"

    response = requests.get(url)
    response.raise_for_status()

    soup = bs4.BeautifulSoup(response.content, "html.parser")

    return _extract_conference_commits(soup, year)


def get_commitments_by_club(gender: str, grad_year: int):
    if gender == "female":
        url = f"https://www.topdrawersoccer.com/commitments/club/women/{grad_year}"
    else:
        url = f"https://www.topdrawersoccer.com/commitments/club/men/{grad_year}"

    response = requests.get(url)
    response.raise_for_status()

    soup = bs4.BeautifulSoup(response.content, "html.parser")

    table = soup.find('table', class_=["table-striped"])

    if table is None:
        return []

    body = table.find('tbody')
    rows = body.find_all("tr")

    records = []
    for row in rows:
        cells = row.findChildren("td")
        record = {
            "club": cells[0].text.strip(),
            "di": int(cells[1].text.strip()),
            "dii": int(cells[2].text.strip()),
            "diii": int(cells[3].text.strip()),
            "naia": int(cells[4].text.strip()),
            "total": int(cells[5].text.strip())
        }
        records.append(record)

    return records


def _get_linked_content_from_cell(cell, prefix=None):
    name = tools.get_anchor_text(cell)

    if len(name) == 0:
        return (None, None)

    url = tools.get_anchor_url(cell, prefix)

    if url is None or len(url) == 0:
        return (name, None)

    return (name, url)


def _get_change_record(row_element, prefix=None):
    cells = row_element.findChildren("td")

    program = tools.get_anchor_text(cells[0])

    if program == "Program":
        return None

    if len(program) == 0:
        return None

    record = {}
    record["program"], record["program_url"] = _get_linked_content_from_cell(cells[0], prefix)
    record["old_coach"], record["old_coach_url"] = _get_linked_content_from_cell(cells[1])
    record["new_coach"], record["new_coach_url"] = _get_linked_content_from_cell(cells[2])
    record["clgid"] = get_identifier_from_url(record["program_url"])

    return record


def _get_change_data(table_element, prefix):
    records = []

    rows = table_element.findChildren("tr")
    for row in rows:
        record = _get_change_record(row, prefix)

        if record is None:
            continue

        records.append(record)

    return records


def _get_d1_coaching_changes(target_title: str, prefix: str):
    url = "https://www.topdrawersoccer.com/college-soccer-articles/tracking-division-i-coaching-changes_aid50078"

    response = requests.get(url)
    response.raise_for_status()

    soup = bs4.BeautifulSoup(response.content, "html.parser")
    grand_parent = soup.find("div", class_=["col-sm-11"])
    parent = grand_parent.find("div", class_=["col"])

    found_it = False
    for child in parent.children:
        if type(child) is not bs4.element.Tag:
            continue

        if child.name not in ["p", "table"]:
            continue

        if child.name == "p" and child.text.strip() == target_title:
            found_it = True
        elif child.name == "table" and found_it:
            return _get_change_data(child, prefix)

    return None


def get_d1_mens_coaching_changes():
    return _get_d1_coaching_changes("MEN'S", PREFIX)

def get_d1_womens_coaching_changes():
    return _get_d1_coaching_changes("WOMEN'S", PREFIX)

def get_commitments(gender: str, year: int):
    """Retrieve all of the commitments for a given gender and year."""
    players = []

    conferences = get_conferences(gender, "di")
    for conference in conferences:
        schools = get_conference_commits(gender, "di", conference["name"], year)

        for school in schools:            
            if "players" in school:
                players.extend(school["players"])    

    conferences = get_conferences(gender, "dii")
    for conference in conferences:
        schools = get_conference_commits(gender, "dii", conference["name"], year)

        for school in schools:            
            if "players" in school:
                players.extend(school["players"])

    conferences = get_conferences(gender, "diii")
    for conference in conferences:
        schools = get_conference_commits(gender, "diii", conference["name"], year)

        for school in schools:            
            if "players" in school:
                players.extend(school["players"])

    conferences = get_conferences(gender, "naia")
    for conference in conferences:
        schools = get_conference_commits(gender, "naia", conference["name"], year)

        for school in schools:
            if "players" in school:
                players.extend(school["players"])

    conferences = get_conferences(gender, "njcaa")
    for conference in conferences:
        schools = get_conference_commits(gender, "njcaa", conference["name"], year)

        for school in schools:
            if "players" in school:
                players.extend(school["players"])
       
    return players


class ClubPlayer:
    def __init__(self, name: str, pid: int):
        self.name = name
        self.pid = pid


class CollegePlayer:
    def __init__(self, name: str, cpid: int):
        self.name = name
        self.cpid = cpid

class ClubPlayerFactory:
    def __init__(self):
        pass


class School:
    def __init__(self, name: str, clgid: int):
        self.name = name
        self.clgid = clgid
        self.enrollment = 0
        self.state = None
        self.city = None
        self.coach = None
        self.phone = None
        self.nickname = None
        self.conference_id = -1
        self.conference_name = None

    def players(self):
        """Return a list of current players for the school."""
        pass

    def committed_players(self):
        """Return a list of committed players for the school."""
        pass


class SchoolFactory:
    def __init__(self):
        pass



class Conference:
    def __init__(self):
        self.id = None
        self.name = None
        self.gender = None
        self.division = None
        self.url = None

    def schools(self):
        """Return a list of schools in the conference."""
        pass

    def players(self):
        """Return a list of current players for the conference."""
        pass

    def commited_players(self):
        """Return a list of committed players for the conference."""
        pass

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url
        }

    def __repr__(self) -> str:
        return self.name


class ConferenceBuilder:
    def __init__(self):
        self.instance = None

    def build(self):
        self.instance = Conference()

    def build_id(self, value: int):
        self.instance.id = value

    def build_name(self, value: str):
        self.instance.name = value

    def build_gender(self, value: str):
        self.instance.gender = value

    def build_division(self, value: str):
        self.instance.division = value

    def build_url(self, value: str):
        self.instance.url = value

    def get_instance(self):
        return self.instance


class ConferenceFactory:
    def __init__(self, gender: str, division: str, builder: ConferenceBuilder = None):
        if builder is None:
            builder = ConferenceBuilder()

        self.gender = gender
        self.division = division
        self.builder = builder
        self.conferences = []

        data = get_conferences(self.gender, self.division)

        for item in data:
            self.conferences.append(self.create(item["id"], item["name"], item["url"]))

    def create(self, id: int, name: str, url: str):
        self.builder.build()
        self.builder.build_id(id)
        self.builder.build_name(name)
        self.builder.build_gender(self.gender)
        self.builder.build_division(self.division)
        self.builder.build_url(url)

        conference = self.builder.get_instance()

        return conference

    def find_by_name(self, name: str):
        for conference in self.conferences:
            if conference.name == name:
                return conference

        return None

    def find_by_id(self, id: int):
        for conference in self.conferences:
            if conference.id == id:
                return conference

        return None


class TopDrawerController:
    def __init__(self, gender: str, division: str):
        self.gender = gender
        self.division = division
        self.conference_builder = ConferenceBuilder()
        self.conference_factory = ConferenceFactory(gender, division, self.conference_builder)

    def conference(self, gender: str, division: str, name: str):
        data = get_conference(gender, division, name)

        conference = self.conference_factory.create(data["id"], data["name"], data["url"])

        return conference

    def conferences(self):
        items = []
        data = get_conferences(self.gender, self.division)

        for item in data:
            cfid = item["id"]
            name = item["name"]
            url = item["url"]
            item = self.conference_factory.create(cfid, name, url)
            items.append(item)

        return items

    def commitments_by_club(self, gender: str, grad_year: int):
        return get_commitments_by_club(gender, grad_year)

    def conference_details(self, gender: str, name: str, cfid: int, year: int = 0):
        return get_conference_details(gender, name, cfid, year)

    def player_details(self, name: str, pid: int):
        return get_player_details(name, pid)

    def college_details(self, gender: str, name: str, clgid: int):
        return get_college_details(gender, name, clgid)

    def player_search(self, gender, position: str, grad_year: str, region: str, state: str):
        return search_for_players(gender, position, grad_year, region, state)

    def committed_players_for_school(self, gender: str, school_name: str, clgid: int):
        return get_committed_players_for_school(gender, school_name, clgid)

    def conference_commits(self, gender: str, division: str, name: str, year: int = 0):
        return get_conference_commits(gender, division, name, year)


