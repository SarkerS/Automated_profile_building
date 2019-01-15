import requests
import time
from bs4 import BeautifulSoup
import config

def search(site, query, offset):
    url = 'https://www.google.ca/search'
    
    qparams = {
        'q': 'site:{:s} {:s}'.format(site, query),
        #'oq': 'site:{:s} {:s}'.format(site, query),
        'start': offset
    }
    links = []
    req = requests.get(url, params=qparams)
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')
    page_links = soup.select('div.g > h3.r > a')

    if page_links:
        links = page_links

    return links
