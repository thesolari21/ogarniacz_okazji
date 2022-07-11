from bs4 import BeautifulSoup
import sqlite3
import requests
import json
import config

def get_pages(base_url):
    """
    Get number of search pages.
    Next create target links [1,...,n] and return in list
    :param base_url: str
    :return: List[str]
    """

    r = requests.get(base_url)
    soup = BeautifulSoup(r.text, 'lxml')
    pagination = soup.find_all("a", class_="ooa-g4wbjr")

    last_page = pagination[-1].text if pagination else 1
    print(f'Liczba stron z wynikami wyszukiwania: {last_page}')

    pages = []
    for page in list(range(1, int(last_page)+1)):
        pages.append(base_url + '&page=' + str(page))

    return pages


def get_articles(urls):
    """
    Get list with URLs
    For every URL extract parameters of each offer and add to dict
    :param urls: str
    :return: Dict[str, str]
    """

    list_of_articles = []

    for url in urls:
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'lxml')
        offers = soup.find_all("article", class_="e1b25f6f18")

        for offer in offers:
            title = offer.find("h2", class_="e1b25f6f13")
            link = title.find("a")
            descr_offer = offer.find("ul", class_="e1b25f6f7")
            desc_list = descr_offer.find_all("li")
            year = desc_list[0] if desc_list else 'N/D'
            distance = desc_list[1] if desc_list else 'N/D'
            capacity = desc_list[2] if desc_list else 'N/D'
            fuel = desc_list[3] if desc_list else 'N/D'
            location = offer.find("svg")
            location = location.next_sibling
            price = offer.find("span", class_="ooa-epvm6")

            title = title.text
            title = title[:29]
            id = link["href"][-13:-5]
            link = link["href"]
            year = year.text
            distance = distance.text
            capacity = capacity.text
            fuel = fuel.text
            price = price.text

            distance = distance[:-2].replace(" ", "")
            capacity = capacity[:-3].replace(" ", "")
            price = price[:-3].replace(" ", "")

            single_split_offer = {
                "title": title,
                "link": link,
                "id": id,
                "year": year,
                "distance": distance,
                "capacity": capacity,
                "fuel": fuel,
                "price": price,
                "location": location
            }

            list_of_articles.append(single_split_offer)
    print(f'Pobranych ofert: {len(list_of_articles)}')

    return list_of_articles


def get_only_new_articles(articles):
    """
    Create tables with all offers and search results if not exists
    Add data to table with search results
    Compare data with all offers and search results
    Add new data to list
    :param articles: List[Dict]
    :return: List
    """
    list_new_articles = []
    conn = sqlite3.connect('./cars.sqlite')
    c = conn.cursor()

    c.execute("""
    CREATE TABLE if not exists offers
    ( id TEXT, title TEXT, location TEXT, year INTEGER, distance INTEGER, capacity INTEGER, fuel TEXT, price INTEGER, link TEXT)
    """)

    c.execute("""
    CREATE TABLE if not exists search_results
    ( id TEXT, title TEXT, location TEXT, year INTEGER, distance INTEGER, capacity INTEGER, fuel TEXT, price INTEGER, link TEXT)
    """)

    c.executemany("""
    INSERT INTO search_results 
    (id, title, location, year, distance, capacity, fuel, price, link)
    VALUES
    (:id,:title,:location,:year,:distance,:capacity,:fuel,:price,:link)
    """, articles)

    for row in c.execute("""
    select sr.* from search_results sr
    left join offers o
    on sr.id = o.id
    where o.id is NULL
    """):
        dict_new_article = dict(zip(["id", "title", "location", "year","distance","capacity","fuel","price","link"],row))
        list_new_articles.append(dict_new_article)

    c.executemany(
        """INSERT INTO offers 
        (id, title, location, year, distance, capacity, fuel, price, link)
        VALUES
        (:id,:title,:location,:year,:distance,:capacity,:fuel,:price,:link)
        """, list_new_articles
    )

    print('Baza uzupelniona o nowe oferty', len(list_new_articles))

    c.execute(
        """DELETE from search_results"""
    )

    conn.commit()
    conn.close()

    return list_new_articles


def send_mail(new_offers):
    """
    Send mail with new offers via API
    :param new_offers: Dict[str, str]
    :return: None
    """

    header = "Dzień dobry, nowe oferty:\n"

    item = ""

    for offer in new_offers:
        title = str(offer["title"])
        localization = str(offer["location"])
        year = str(offer["year"])
        distance = str(offer["distance"])
        capacity = str(offer["capacity"])
        fuel = str(offer["fuel"])
        price = str(offer["price"])
        link = str(offer["link"])

        item = item + '{:20s}{:40s}\n{:20s}{:40s}\n{:20s}{:40s}\n' \
                      '{:20s}{:40s}\n{:20s}{:40s}\n{:20s}{:40s}\n' \
                      '{:20s}{:40s}\n{:20s}{:40s}\n\n'\
            .format('Nazwa:', title, 'Miejsce:', localization, 'Rok:', year, 'Przebieg:', distance, 'Pojemność:', capacity,
           'Paliwo:', fuel, 'Cena:', price, 'Link:', link)

    message_text = header + item
    subject = 'Nowe oferty'

    payload = {
        "api_key": config.API_KEY,
        "to": [
            config.RECIPIENT
        ],
        "sender": config.SENDER,
        "subject": subject,
        "text_body": message_text
    }
    headers = {"Content-Type": "application/json"}
    res = requests.post(config.API_ADDRESS, headers=headers, data=json.dumps(payload))
    if res.status_code == requests.codes.ok:
        print('Mail z nowymi ofertami wysłany. Code:' , res.status_code)
    else:
        print('Cos poszło nie tak z wysyłką... Code:' , res.status_code)

if __name__ == "__main__":
    base_url = config.URL
    urls = get_pages(base_url)
    articles = get_articles(urls)
    new_offers = get_only_new_articles(articles)
    send_mail(new_offers)