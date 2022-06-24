import requests
from bs4 import BeautifulSoup
import sqlite3
import smtplib
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
        pages.append(base_url + '?page=' + str(page))

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
    :param articles: Dict[str, str]
    :return: List
    """
    new_articles = []
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
        new_articles.append(row)

    c.executemany(
        """INSERT INTO offers 
        (id, title, location, year, distance, capacity, fuel, price, link)
        VALUES
        (?,?,?,?,?,?,?,?,?)
        """, new_articles
    )

    print('Baza uzupelniona o nowe oferty', len(new_articles))

    c.execute(
        """DELETE from search_results"""
    )

    conn.commit()
    conn.close()

    return new_articles


def send_mail(new_offers):
    """
    Send mail with new offers
    :param new_offers:
    :return:
    """
    smtp = smtplib.SMTP(config.SMTP_SERVER, config.PORT)
    smtp.starttls()
    smtp.login(config.LOGIN, config.PASSWORD)

    header = """
    Dzień dobry, nowe oferty:
    """

    item = ""

    for offer in new_offers:
        title = str(offer[1])
        localization = str(offer[2])
        year = str(offer[3])
        distance = str(offer[4])
        capacity = str(offer[5])
        fuel = str(offer[6])
        price = str(offer[7])
        link = str(offer[8])

        item = item + """
{:20s}{:40s}
{:20s}{:40s}
{:20s}{:40s}
{:20s}{:40s}
{:20s}{:40s}
{:20s}{:40s}
{:20s}{:40s}
{:20s}{:40s}

""".format('Nazwa:', title, 'Miejsce:', localization, 'Rok:', year, 'Przebieg:', distance, 'Pojemność:', capacity,
           'Paliwo:', fuel, 'Cena:', price, 'Link:', link)

    message_text = header + item
    subject = 'elo'
    message = 'Subject: {}\n\n{}'.format(subject, message_text)

    smtp.sendmail('mailer.bartek3@interia.pl', 'bartsol21@gmail.com', message.encode('utf-8'))
    smtp.quit()
    print('Mail z nowymi ofertami wysłany')


if __name__ == "__main__":
    base_url = 'https://www.otomoto.pl/osobowe/bentley'
    urls = get_pages(base_url)
    articles = get_articles(urls)
    new_offers = get_only_new_articles(articles)
    send_mail(new_offers)