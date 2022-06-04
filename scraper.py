# pip install requests
# pip install beautifulsoup4
# pip install lxml

import requests
from bs4 import BeautifulSoup
import sqlite3

# uruchom wrappera i pobierz wszystkie oferty
def GetArticles(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')

    # pobierz caly div z opisem, cena itp
    cars = soup.find_all("article", class_="e1b25f6f18")

    list_all = []
    # kazda oferte rozbij na skladowe
    for car in cars:
        list_one = []

        title = car.find("h2", class_="e1b25f6f13")
        link = title.find("a")

        # zakladam, ze ID to ostatnie znaki z linka do oferty
        id = link["href"][-13:-5]

        desc_all = car.find("ul", class_="e1b25f6f7")
        desc_list = desc_all.find_all("li")
        year = desc_list[0]
        distance = desc_list[1]
        capacity = desc_list[2]
        fuel = desc_list[3]

        # poryta akcja, nie mogłem zlapac miejscowosci, trzeba bylo skorzystac z .nextsibling aby znalazlo text za tagiem
        location = car.find("svg")
        location = location.next_sibling

        price = car.find("span", class_="ooa-epvm6")

        # wyciagam dane z znacznikow HTML
        title = title.text
        year = year.text
        distance = distance.text
        capacity = capacity.text
        fuel = fuel.text
        price = price.text

        # oczyszczam dane
        distance = distance[:-2].replace(" ", "")
        capacity = capacity[:-3].replace(" ", "")
        price = price[:-3].replace(" ", "")

        # wrzucam dane do listy
        list_one.extend([id, title, location, year, distance, capacity, fuel, price])
        list_all.append(list_one)

    print(list_all)
    print(len(list_all))

    return list_all

# porownaj oferty wrappera z archiwalnymi, zwroc tylko nowe, wszystkie oferty zapisz w db
def GetNewArticles(list):
    new_offers = []
    conn = sqlite3.connect('./cars.sqlite')
    c = conn.cursor()

    # tworze tabele z do przechowywania wszystkich ofert
    c.execute("""
    CREATE TABLE if not exists offers
    ( id TEXT, title TEXT, location TEXT, year INTEGER, distance INTEGER, capacity INTEGER, fuel TEXT, price INTEGER)
    """)

    # tworze tabele robocza do przechowywania wynikow scrapera
    c.execute("""
    CREATE TABLE if not exists search_results
    ( id TEXT, title TEXT, location TEXT, year INTEGER, distance INTEGER, capacity INTEGER, fuel TEXT, price INTEGER)
    """)

    # wrzucam dane z scrapera do roboczej tabeli
    c.executemany("""INSERT INTO search_results 
    (id, title, location, year, distance, capacity, fuel, price)
    VALUES
    (?,?,?,?,?,?,?,?)
    """, list)

    # porownuje dane pomiedzy wynikami scrapera, a wszystkimi ofertami.
    # nowe oferty wrzucam do listy
    for row in c.execute("""
    select sr.* from search_results sr
    left join offers o
    on sr.id = o.id
    where o.id is NULL
    """):
        new_offers.append(row)

    # uzupelniam tabele z wszystkimi ofertami - nowymi ofertami
    c.executemany(
        """INSERT INTO offers 
        (id, title, location, year, distance, capacity, fuel, price)
        VALUES
        (?,?,?,?,?,?,?,?)
        """, new_offers
    )

    # czyszcze tabele robocza
    c.execute(
        """DELETE from search_results"""
    )

    # zapisuje zmiany i koncze polaczenie z db
    conn.commit()
    conn.close()

    return new_offers

url = 'https://www.otomoto.pl/osobowe/mazda?search%5Bfilter_enum_damaged%5D=0&search%5Bfilter_enum_no_accident%5D=1&search%5Bfilter_float_mileage%3Ato%5D=125000&search%5Bfilter_float_price%3Afrom%5D=30000&search%5Bfilter_float_price%3Ato%5D=50000&search%5Border%5D=created_at_first%3Adesc&search%5Badvanced_search_expanded%5D=true'
list = GetArticles(url)
new_offers = GetNewArticles(list)

