import urllib2
from bs4 import BeautifulSoup

def soup(url):
    return BeautifulSoup(urllib2.urlopen(url).read())

def make_digikey_url(part_number):

def get_digikey_info(part_number):

