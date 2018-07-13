import urllib.request
from bs4 import BeautifulSoup

def soup(url):
    return BeautifulSoup(urllib.request.urlopen(url).read())

def make_digikey_url(part_number):
    pass
def get_digikey_info(part_number):
    pass

