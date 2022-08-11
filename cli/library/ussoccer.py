import bs4
import requests

def _get_data(el):
    unordered_list = el.find("ul", class_=["PlayerThumbnail-module__stats--TCgax", "PlayerThumbnail-module__stats3--3kNTk"])

    if unordered_list is None:
        return {}

    items = unordered_list.find_all("li")

    data = {}

    for item in items:
        children = item.findChildren('div')
        value = int(children[0].text.strip())
        name = children[1].text.strip()
        data[name] = value

    return data


def _get_player_name(el):
    item = el.find("div", class_=["PlayerThumbnail-module__playerName--2bbtZ"])
    text = item.text
    text = text.strip()
    text = text.replace("  ", " ")

    tokens = text.split(" ")
    text = " ".join(tokens[1:])

    return text

def _get_player_number(el):
    item = el.find("div", class_=["PlayerThumbnail-module__playerName--2bbtZ"])
    text = item.text
    text = text.strip()
    text = text.replace("  ", " ")

    tokens = text.split(" ")
    text = tokens[0]

    return text

def _get_player_position(el):
    item = el.find("div", class_=["PlayerThumbnail-module__playerPosition--KP4od"])

    if item is None:
        return "Coach"
    
    if item.text is not None:
        return item.text.strip()
    else:
        return None
    


def _read_player_card(el):
    player = {}

    player["name"] = _get_player_name(el)
    player["number"] = _get_player_number(el)
    player["position"] = _get_player_position(el)

    data = _get_data(el)

    for key in data:
        player[key.lower().replace(" ", "_")] = data[key]

    return player

def get_players(gender: str):
    if gender == "Male":
        url = "https://www.ussoccer.com/teams/usmnt"
    else:
        url = "https://www.ussoccer.com/teams/uswnt"

    response = requests.get(url)
    response.raise_for_status()

    soup = bs4.BeautifulSoup(response.content, "html.parser")

    players = []

    cards = soup.find_all("div", class_=["col--md-3"])
    for card in cards:
        player = _read_player_card(card)

        if player["position"] is not "Coach":
            players.append(player)

    return players

if __name__ == "__main__":
    print ("Men")
    players = get_players("Male")

    for player in players:
        print(player)

    print("")
    print("Women")
    players = get_players("Female")

    for player in players:
        print(player)
