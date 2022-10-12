import requests
import xmltodict


def esperanto():
    url = "https://wotd.transparent.com/rss/esp-widget.xml?t=1664937434282"
    result = requests.get(url)

    data = xmltodict.parse(result.text)
    data = data["xml"]["words"]

    return data


if __name__ == "__main__":
    esperanto()
