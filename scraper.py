# pip install requests
# pip install beautifulsoup4
# pip install lxml

import requests
from bs4 import BeautifulSoup

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

        #poryta akcja, nie mogłem zlapac miejscowosci, trzeba bylo skorzystac z .nextsibling aby znalazlo text za tagiem
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


url = 'https://www.otomoto.pl/osobowe/mazda?search%5Bfilter_enum_damaged%5D=0&search%5Bfilter_enum_no_accident%5D=1&search%5Bfilter_float_mileage%3Ato%5D=125000&search%5Bfilter_float_price%3Afrom%5D=30000&search%5Bfilter_float_price%3Ato%5D=50000&search%5Border%5D=created_at_first%3Adesc&search%5Badvanced_search_expanded%5D=true'
GetArticles(url)