import requests
import time
from bs4 import BeautifulSoup
import config
import json
import googler
import re
import urllib

def search(name):
    #people = []
    site = 'twitter.com'
    page = 0
    offset = 0
    link_hash = {}
    
    while page < config.MAX_RESULTS_PAGES:# and not done:
        links = googler.search(site, name, offset)

        texts = list(map(lambda l: l.text, links))
        links = parse_link_els(links)
        print('Parsing results page {:d} of {:d}'.format(page + 1, config.MAX_RESULTS_PAGES))
        
        #ensure we don't get any duplicates
        filtered_links = []
        for i in range(len(links)):
            l = links[i]
            text = texts[i]
            if re.match(r'^.+\ \(\@.+\)\ \|\ Twitter.*$', text):
                if re.match(r'^https\://twitter\.com/[^/]+/?$', l):
                    if l not in link_hash:
                        link_hash[l] = True
                        filtered_links.append(l)

        #print(filtered_links)
        found = parse_people(filtered_links)
        if not found:
            time.sleep(config.CRAWL_TIMEOUT)
                    
        offset += len(links)
        page += 1

    #return people

def parse_link_els(els):
    results = []
    for link in els:
        m = re.match(r'^.*\?q=(https\://[^\&\?]+).*$', link.attrs['href'])
        if m:
            href = m.groups()[0]
            unquoted = urllib.parse.unquote(href)
            results.append(unquoted)

    return results

def parse_people(links):
    #people = []
    found = False
    for link in links:
        m = re.match(r'^.*(https\://[^\&\?]+).*$', link)
        url = m.groups()[0] if m and m.groups() else None
        if url:
            print('Following Twitter link: {:s}'.format(url))
            person = parse_details(url)
            if person['name']:
                #print_person(person)
                insert_person(person)
                found = True
                time.sleep(config.CRAWL_TIMEOUT)
                
    return found

def get_pic_url(soup):
    url = None
    imgs = soup.select('img.ProfileAvatar-image')
    if imgs:
        url = imgs[0].attrs['src']

    return url

def get_name(soup):
    name = None
    links = soup.select('a.ProfileHeaderCard-nameLink.u-textInheritColor.js-nav')
    if links and links[0].string:
        name = links[0].string.strip()

    return name

def get_handle(soup):
    handle = None
    links = soup.select('a.ProfileHeaderCard-screennameLink.u-linkComplex.js-nav')
    if links:
        handle = links[0].text.strip()

    return handle

def get_bio(soup):
    bio = None
    ps = soup.select('p.ProfileHeaderCard-bio.u-dir')
    if ps:
        bio = ps[0].text.strip()

    return bio

def get_location(soup):
    location = None
    div = soup.select('div.ProfileHeaderCard-location')
    if div:
        location = div[0].text.strip()

    return location

def get_website(soup):
    website = None
    div = soup.select('div.ProfileHeaderCard-url')
    if div:
        link = div[0].find('a')
        if link:
            website = link.href #note: may not include 'http://' or 'https://'

    return website

def get_join_date(soup):
    joined = None
    div = soup.select('div.ProfileHeaderCard-joinDate')
    if div:
        joined = div[0].text.strip()

    return joined

def get_birthdate(soup):
    bdate = None
    div = soup.select('div.ProfileHeaderCard-birthdate')
    if div and div[0].string: # note: this one may be unavailable even though the div exists (if the user's elected not to show it)
        bdate = div[0].text.strip()

    return bdate

def get_tweets(soup):
    tweets = []
    ol = soup.find('ol', id='stream-items-id')
    if ol:
        items = ol.select('div.tweet')
        tweets = list(map(str, items[:config.NUM_TOP_TWEETS]))

    return tweets

def parse_details(profile_url):
    req = requests.get(profile_url)
    html = req.text
    
    details = {'url': profile_url}
    soup = BeautifulSoup(html, 'html.parser')

    pic_url = get_pic_url(soup)
    details['pic_url'] = pic_url
    
    name = get_name(soup)
    details['name'] = name

    handle = get_handle(soup)
    details['handle'] = handle

    bio = get_bio(soup)
    details['bio'] = bio

    location = get_location(soup)
    details['location'] = location

    website = get_website(soup)
    details['website'] = website
    
    joined = get_join_date(soup)
    details['joined'] = joined
    
    birthdate = get_birthdate(soup)
    details['birthdate'] = birthdate

    tweets = get_tweets(soup)
    details['tweets'] = tweets

    return details

def print_person(person):
    print('---')
    for key in person:
        if key != 'tweets':
            print('%s: %s' % (key, person[key]))
    #print(person)
    print('---\n')

def insert_person(person):
    profile_id = config.DB.insert(
        'profiles',
        platform = 'Twitter',
        profile_url = person['url'],
        profile_handle = person['handle'],
        pic_url = person['pic_url'],
        name = person['name'],
        bio = person['bio']
    )

    config.DB.insert(
        'locations',
        name = person['location'],
        profile_id = profile_id
    )

    for i in range(len(person['tweets'])):
        tweet = person['tweets'][i]
        config.DB.insert(
            'tweets',
            num = i, #so we can order in the UI later
            html = tweet,
            profile_id = profile_id
        )

if __name__ == '__main__':
    people = search(config.search_name)
