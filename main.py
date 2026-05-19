import requests

from scraper.cnn_scraper import URL, HEADERS

r = requests.get(URL, headers=HEADERS)

print("STATUS:", r.status_code)
print("SIZE:", len(r.text))
print(r.text[:1000])
