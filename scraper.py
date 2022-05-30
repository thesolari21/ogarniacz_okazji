# pip install requests
# pip install beautifulsoup4
# pip install lxml

import requests
from bs4 import BeautifulSoup

url = 'https://www.otomoto.pl/osobowe/mazda?search%5Bfilter_enum_damaged%5D=0&search%5Bfilter_enum_no_accident%5D=1&search%5Bfilter_float_mileage%3Ato%5D=125000&search%5Bfilter_float_price%3Afrom%5D=30000&search%5Bfilter_float_price%3Ato%5D=50000&search%5Border%5D=created_at_first%3Adesc&search%5Badvanced_search_expanded%5D=true'
r = requests.get(url)
soup = BeautifulSoup(r.text, 'lxml')

print(soup.title)
cars = soup.find_all("article", class_="e1b25f6f18")

print(r)
print(len(cars))

for car in cars:
    title = car.find("h2", class_="e1b25f6f13")
    link = title.find("a")
    id = link["href"][-13:-5]

    desc_all = car.find("ul", class_="e1b25f6f7")
    desc_list = desc_all.find_all("li")
    rok = desc_list[0]
    przebieg = desc_list[1]
    silnik = desc_list[2]
    paliwo = desc_list[3]

    price = car.find("span", class_="ooa-epvm6")

    print(id)
    print(title.text)
    print(link["href"])
    print(rok.text)
    print(przebieg.text)
    print(silnik.text)
    print(paliwo.text)
    print(price.text, "\n")
