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
        offers = soup.find_all("article", attrs={"data-media-size":"small"})

        for offer in offers:

            try:
                title = offer.find("h1").text[:29]
                link = offer.find("a")["href"]
                id = link[-13:-5]

                year = offer.find("dd", attrs={"data-parameter":"year"}).text
                distance = offer.find("dd", attrs={"data-parameter":"mileage"}).text[:-2].replace(" ", "")
                capacity = offer.find("dd", attrs={"data-parameter":"mileage"}).text[:-3].replace(" ", "")
                fuel = offer.find("dd", attrs={"data-parameter":"fuel_type"}).text

                location = offer.find("p", class_ = "ooa-gmxnzj").text.split(' ')[0]
                price = offer.find("h3").text
            except:
                title = link = id = year = distance = capacity = fuel = location = price = "N/D"

            try:
                foto = offer.find("img")
                foto = foto["src"]
            except TypeError:
                foto = 'https://static.vecteezy.com/system/resources/previews/005/576/332/original/car-icon-car-icon-car-icon-simple-sign-free-vector.jpg'


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