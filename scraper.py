# pip install requests
# pip install beautifulsoup4
# pip install lxml

import requests
from bs4 import BeautifulSoup
import sqlite3
import smtplib

def GetPages(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')

    # pobierz liste wszystkich stron danego wyszukania, znajdz ostatni element
    # pages = ['1'] na wypadek gdyby nie bylo juz innych stron - nie pojawi sie paginacja
    pages = ['1']
    pagination = soup.find_all("a", class_="ooa-g4wbjr")
    for page in pagination:
        pages.append(page.text)
    last_page = int(pages[-1])

    # zwroc liste z numerami wszystkich stron
    p = []
    for i in range(1,last_page+1):
        p.append(i)

    print('Pobralem liste stron!')
    return p


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
        title = title[:29]      #skracam do 30 znakow
        year = year.text
        distance = distance.text
        capacity = capacity.text
        fuel = fuel.text
        price = price.text
        link = link["href"]

        # oczyszczam dane
        distance = distance[:-2].replace(" ", "")
        capacity = capacity[:-3].replace(" ", "")
        price = price[:-3].replace(" ", "")

        # wrzucam dane do listy
        list_one.extend([id, title, location, year, distance, capacity, fuel, price, link])
        list_all.append(list_one)

    print('Pobralem artykuly z strony: ', url)

    return list_all

# porownaj oferty wrappera z archiwalnymi, zwroc tylko nowe, wszystkie oferty zapisz w db
def GetNewArticles(list):
    new_offers = []
    conn = sqlite3.connect('./cars.sqlite')
    c = conn.cursor()

    # tworze tabele z do przechowywania wszystkich ofert
    c.execute("""
    CREATE TABLE if not exists offers
    ( id TEXT, title TEXT, location TEXT, year INTEGER, distance INTEGER, capacity INTEGER, fuel TEXT, price INTEGER, link TEXT)
    """)

    # tworze tabele robocza do przechowywania wynikow scrapera
    c.execute("""
    CREATE TABLE if not exists search_results
    ( id TEXT, title TEXT, location TEXT, year INTEGER, distance INTEGER, capacity INTEGER, fuel TEXT, price INTEGER, link TEXT)
    """)

    # wrzucam dane z scrapera do roboczej tabeli
    c.executemany("""INSERT INTO search_results 
    (id, title, location, year, distance, capacity, fuel, price, link)
    VALUES
    (?,?,?,?,?,?,?,?,?)
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
        (id, title, location, year, distance, capacity, fuel, price, link)
        VALUES
        (?,?,?,?,?,?,?,?,?)
        """, new_offers
    )

    print('Baza uzupelniona o nowe oferty', len(new_offers))

    # czyszcze tabele robocza
    c.execute(
        """DELETE from search_results"""
    )

    # zapisuje zmiany i koncze polaczenie z db
    conn.commit()
    conn.close()

    return new_offers

def SendMail(new_offers):

    # config do SMTP
    smtp = smtplib.SMTP('SERWER_SMTP',587)
    smtp.starttls()
    smtp.login('LOGIN', 'PASS')

    # naglowek maila
    header = """
    Dzień dobry, nowe oferty:
    """

    item = ""

    # wypakuj z listy paametry poszczegolnych ofert
    for offer in new_offers:
        title = str(offer[1])
        localization = str(offer[2])
        year = str(offer[3])
        distance = str(offer[4])
        capacity = str(offer[5])
        fuel = str(offer[6])
        price = str(offer[7])
        link = str(offer[8])

        # ladnie poscalaj i sformatuj do stringa
        item = item + """
{:20s}{:40s}
{:20s}{:40s}
{:20s}{:40s}
{:20s}{:40s}
{:20s}{:40s}
{:20s}{:40s}
{:20s}{:40s}
{:20s}{:40s}

""".format('Nazwa:',title,'Miejsce:',localization,'Rok:',year,'Przebieg:',distance,'Pojemność:',capacity,
           'Paliwo:',fuel,'Cena:',price,'Link:',link)

    # wiadomosc wysylana mailem
    message_text = header + item
    subject = 'Nowe oferty'
    message = 'Subject: {}\n\n{}'.format(subject, message_text)

    # wysyłka maila
    smtp.sendmail('mailer.bartek@interia.pl', 'bartsol21@gmail.com', message.encode('utf-8'))
    smtp.quit()
    print('Mail z nowymi ofertami wysłany')


################# main ####################

# test z 2 stronami
#url = 'https://www.otomoto.pl/osobowe/mazda?search%5Bfilter_enum_damaged%5D=0&search%5Bfilter_enum_no_accident%5D=1&search%5Bfilter_float_mileage%3Ato%5D=125000&search%5Bfilter_float_price%3Afrom%5D=30000&search%5Bfilter_float_price%3Ato%5D=50000&search%5Border%5D=created_at_first%3Adesc&search%5Badvanced_search_expanded%5D=true'

# test z n stronami
url = 'https://www.otomoto.pl/osobowe/mazda?search%5Bfilter_enum_damaged%5D=0&search%5Bfilter_enum_no_accident%5D=1&search%5Bfilter_float_mileage%3Ato%5D=125000&search%5Bfilter_float_price%3Afrom%5D=30000&search%5Bfilter_float_price%3Ato%5D=65000&search%5Border%5D=created_at_first%3Adesc'

# test z 0 stronami
#url = 'https://www.otomoto.pl/osobowe/mazda?search%5Bfilter_enum_damaged%5D=0&search%5Bfilter_enum_no_accident%5D=1&search%5Bfilter_float_mileage%3Ato%5D=125000&search%5Bfilter_float_price%3Afrom%5D=30000&search%5Bfilter_float_price%3Ato%5D=40000&search%5Border%5D=created_at_first%3Adesc'


# pobierz ile jest stron z wynikami wyszukiwania
pages = GetPages(url)

# lista ofert
list = []

# dodaj do listy wszystkie oferty ze wszystkich stron
for page in pages:
    dest_url = url + '&page=' + str(page)
    list.extend(GetArticles(dest_url))
print('Pobralem:',len(list), 'ofert.')

# porownaj wrappera z aktualna baza i przypisz tylko nowe oferty
new_offers = GetNewArticles(list)

# wyslij maila z nowymi ofertami
SendMail(new_offers)

