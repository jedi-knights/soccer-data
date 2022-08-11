import requests
import json
import bs4

def get_conferences():
    f = open("org/usys/national_league/conferences.json")
    container = json.load(f)

    conferences = container["data"]

    f.close()

    return conferences

if __name__ == "__main__":
    conferences = get_conferences()

    for conference in conferences:
        response = requests.get(conference["url"])
        response.raise_for_status()

        soup = bs4.BeautifulSoup(response.content, "html.parser")
        links = soup.find_all("a", class_=["btn"])

        for link in links:
            if link.text.strip() == "Schedule":
                schedule_url = link["href"]

                print(conference["name"])
                print(f"\t{schedule_url}")

                response2 = requests.get(schedule_url)
                response2.raise_for_status()

                soup2 = bs4.BeautifulSoup(response2.content, "html.parser")
                gender_age_schedule_links = soup2.find_all("a", class_=["pull-right"])

                for gender_age_schedule_link in gender_age_schedule_links:
                    response3 = requests.get(gender_age_schedule_link["href"])
                    response3.raise_for_status()

                    soup3 = bs4.BeautifulSoup(response3.content, "html.parser")
                    
