from bs4 import BeautifulSoup
import sqlite3
import requests
import html_template as ht
import sys


def get_pages(base_url):
    """
    Get number of search pages.
    Create target links [1,...,n] and return in list
    :param base_url: str
    :return: List[str]
    """

    headers = {"Content-Type": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36 OPR/94.0.0.0"}

    r = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    pagination = soup.find("ul", attrs={'data-testid': 'pagination-list'})

    char = ''

    # if is only one page with offers - web doesn't show pagination (None)
    if pagination:
        pagination = pagination.find_all('a', href=True)
        last_page = pagination[-1].text

        # depending on the search criteria, the page= parameter is combined with '&' or '?'
        if '&' in pagination[-1]['href']:
            char = '&'
        else:
            char = '?'
    else:
        last_page = str(1)

    print(f'Liczba stron z wynikami wyszukiwania: {last_page}')

    pages = []
    for page in list(range(1, int(last_page)+1)):
        pages.append(base_url + char + 'page=' + str(page))

    print(pages)

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
        offers = soup.find_all("article", attrs={"data-variant":"regular"})

        for offer in offers:
            title = offer.find("h2")
            link = title.find("a")
            descr_offer = offer.find("ul")
            desc_list = descr_offer.find_all("li")

            # in case one of the parameters is missing
            try:
                year = desc_list[0].text
                distance = desc_list[1].text
                capacity = desc_list[2].text
                fuel = desc_list[3].text
            except:
                year = distance = capacity = fuel = "N/D"

            try:
                location = offer.find("span", class_ = "ooa-fzu03x").text
                price = offer.find("span", class_ = "ooa-1bmnxg7 evg565y13").text
            except:
                location = price = "N/D"

            title = title.text
            title = title[:29]
            id = link["href"][-13:-5]
            link = link["href"]

            try:
                foto = offer.find("img")
                foto = foto["src"]
            except TypeError:
                foto = 'https://static.vecteezy.com/system/resources/previews/005/576/332/original/car-icon-car-icon-car-icon-simple-sign-free-vector.jpg'

            distance = distance[:-2].replace(" ", "")
            capacity = capacity[:-3].replace(" ", "")
            location = location.split(' ')[0]
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
                "location": location,
                "foto": foto
            }

            list_of_articles.append(single_split_offer)

    print(f'Pobranych ofert: {len(list_of_articles)}')

    return list_of_articles


def get_only_new_articles(articles):
    """
    Create tables with all offers and search results -> if not exists
    Add data to table with search results
    Compare data with all offers and search results
    Add new data to Dict
    :param articles: List[Dict]
    :return: Dict
    """

    list_new_articles = []
    conn = sqlite3.connect('./cars.sqlite')
    c = conn.cursor()

    c.execute("""
    CREATE TABLE if not exists offers
    ( id TEXT, title TEXT, location TEXT, year INTEGER, distance INTEGER, capacity INTEGER, fuel TEXT, price INTEGER, link TEXT, foto TEXT)
    """)

    c.execute("""
    CREATE TABLE if not exists search_results
    ( id TEXT, title TEXT, location TEXT, year INTEGER, distance INTEGER, capacity INTEGER, fuel TEXT, price INTEGER, link TEXT, foto TEXT)
    """)

    c.executemany("""
    INSERT INTO search_results 
    (id, title, location, year, distance, capacity, fuel, price, link, foto)
    VALUES
    (:id,:title,:location,:year,:distance,:capacity,:fuel,:price,:link,:foto)
    """, articles)

    for row in c.execute("""
    select sr.* from search_results sr
    left join offers o
    on sr.id = o.id
    where o.id is NULL
    """):
        dict_new_article = dict(zip(["id", "title", "location", "year","distance","capacity","fuel","price","link","foto"],row))
        list_new_articles.append(dict_new_article)

    c.executemany(
        """INSERT INTO offers 
        (id, title, location, year, distance, capacity, fuel, price, link, foto)
        VALUES
        (:id,:title,:location,:year,:distance,:capacity,:fuel,:price,:link,:foto)
        """, list_new_articles
    )

    print('Baza uzupelniona o nowe oferty', len(list_new_articles))

    c.execute(
        """DELETE from search_results"""
    )

    conn.commit()
    conn.close()

    return list_new_articles


if __name__ == "__main__":
    pages = get_pages(sys.argv[1])
    articles = get_articles(pages)
    new_offers = get_only_new_articles(articles)
    ht.prepare_mail(new_offers)
    print('Gotowe')