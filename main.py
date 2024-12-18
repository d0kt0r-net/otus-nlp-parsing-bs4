import json
import random
import time
from tqdm import tqdm
from operator import itemgetter

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

SITE_TO_PARSE = "https://books.toscrape.com"
USER_AGENT = UserAgent().random
MAX_PAGE = 60
DELAY = 0.1, 0.5


def main():
    book_page_links = set()

    for page in tqdm(range(1, MAX_PAGE)):
        response = requests.get(
            f"{SITE_TO_PARSE}/catalogue/page-{page}.html",
            headers={"User-Agent": USER_AGENT},
        )

        time.sleep(random.uniform(*DELAY))

        if not response.ok:
            break

        soup = BeautifulSoup(response.content, "html.parser")
        book_page_links |= set(
            itemgetter("href")(el) for el in soup.select("div.image_container > a")
        )

    result = []
    rating_list = ("Zero", "One", "Two", "Three", "Four", "Five")

    for book_page_link in tqdm(book_page_links):
        response = requests.get(
            f"{SITE_TO_PARSE}/catalogue/{book_page_link}",
            headers={"User-Agent": USER_AGENT},
        )

        time.sleep(random.uniform(*DELAY))

        soup = BeautifulSoup(response.content, "html.parser")

        result.append(
            {
                "url": book_page_link,
                "title": soup.find("h1").text,
                "description": soup.find("h2").text,
                "rating": rating_list.index(
                    list(
                        set(
                            soup.find("p", class_="star-rating").attrs["class"]
                        ).difference(["star-rating"])
                    )[0]
                ),
            }
            | {
                el.find("th").text.split()[0].lower(): el.find("td").text
                for el in soup.select("table.table > tr")
            }
        )

    with open('result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
