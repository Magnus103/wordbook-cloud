import requests
from bs4 import BeautifulSoup

url = "https://quotes.toscrape.com/"

res = requests.get(url)
soup = BeautifulSoup(res.text, "html.parser")

quotes = soup.find_all("div", class_="quote")

for q in quotes:
    text = q.find("span", class_="text").text
    author = q.find("small", class_="author").text
    print(text, "-", author)
