# pip install requests
# pip install beautifulsoup4
# pip install lxml

import requests
from bs4 import BeautifulSoup

r = requests.get('https://pl.wikipedia.org/wiki/Wisła_Kraków_(piłka_nożna)')
soup = BeautifulSoup(r.text , 'lxml')

print(soup.title.text)
body = soup.body.find('div')
print(body)