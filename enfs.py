import pandas as pd
import requests
import bs4
from datetime import datetime


def enfs():
    base_url = "https://www.sas.ipl.pt/"
    base_response = requests.get(base_url + "ementas")
    base_soup = bs4.BeautifulSoup(base_response.content, "html.parser")

    for link in base_soup.find_all("a"):
        if "Tecnologia" in link.get("href"):
            ementa_url = link.get("href")

    tables = pd.read_html(base_url + ementa_url)[1:]
    weekday = datetime.now().weekday()
    ementa = ["Hoje:"]

    if datetime.now().hour > 14:
        weekday += 1
        ementa = ["Amanhã:"]

    if weekday > 4:
        return "É fim de semana, não há enfs..."

    foodtypes = ["Sopa", "Terra", "Mar", "Veggie", "Finger Food"]
    food = [a[1][0] for a in tables[weekday].iterrows()]

    for ft in foodtypes:
        for f in food:
            if ft in f:
                ementa.append(f"{ft}: {f.split(ft)[0].strip()}")
    return "\n".join(ementa)




if __name__ == "__main__":
    enfs()
