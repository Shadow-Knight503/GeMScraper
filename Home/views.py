import firebase_admin
import requests
from django.shortcuts import render
from bs4 import BeautifulSoup
from firebase_admin import firestore, credentials

Cred = credentials.Certificate("./pinup.json")
App = firebase_admin.initialize_app(Cred)
Db = firestore.client()

# Create your views here.
def Scraper(url):
    USER_AGENT = 'Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Mobile/7B405'
    LANGUAGE = "en-US,en;q=0.5"
    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT
    session.headers['Accept-Language'] = LANGUAGE
    session.headers['Content-Language'] = LANGUAGE
    cnt = session.get(f"https://mkp.gem.gov.in/computers-0912tc/search").text
    return cnt


def home(request):
    print("Initialising...")
    prod = []
    for i in range(1, 20):
        res = Scraper(f"#/?page={i}&_xhr=1")
        soup = BeautifulSoup(res, 'html.parser')
        for sup in soup.find_all('div', {'class': 'variant-wrapper'}):
            ist = {
                'ID': f"{sup.findChild('div', {'class': 'variant-image'}).findChild('a')['href'][-19:]}",
                'Img': f"{sup.findChild('img')['src']}",
                'Name': f"{sup.findChild('span', {'class': 'variant-title'}).text}",
                'Price': sup.findChild('span', {'class': 'variant-final-price'}).text.replace('\n', ''),
            }
            ref = Db.collection("GeM").document(ist['ID'])
            del ist['ID']
            ref.set(ist)
            prod.append(ist)
        print(prod)

    return render(request, "Home.html", {'Prods': prod})
