import requests
import time
from bs4 import BeautifulSoup
import config
import googler
import re
import urllib
import json

def search(name, json_file):
    #people = []
    site = 'facebook.com'
    done = False
    page = 0
    offset = 0
    link_hash = {}
    
    while page < config.MAX_RESULTS_PAGES:# and not done:
        links = googler.search(site, name, offset)

        links = parse_link_els(links)
        print('Parsing results page {:d} of {:d}'.format(page + 1, config.MAX_RESULTS_PAGES))
        
        #ensure we don't get any duplicates
        filtered_links = []
        for l in links:
            if re.match(r'^https\://www\.facebook\.com/[^/]+/?$', l):
                if l not in link_hash:
                    link_hash[l] = True
                    filtered_links.append(l)

        #new_people = parse_people(filtered_links)
        parse_people(filtered_links, json_file)

        #if new_people:
            #people.extend(new_people)

        #if not done:
        offset += len(links)
        page += 1

#    return people

def parse_people(links, json_file):
    #people = []
    for link in links:
        #href = link.attrs['href'] if 'href' in link.attrs else ''
        #href = urllib.parse.unquote(href)
        m = re.match(r'^.*(https\://[^\&\?]+).*$', link)
        url = m.groups()[0] if m and m.groups() else None
        if url:
            print('Following Facebook link: {:s}'.format(url))
            person = parse_details(url)
            if person['name']:
                #people.append(person)
                insert_person(person, json_file)
                
            time.sleep(config.CRAWL_TIMEOUT)

    #return people

def get_name(soup):
    name = None
    name_span = soup.find('span', id='fb-timeline-cover-name')
    if name_span:
        name = name_span.string if name_span.string else name_span.text

    return name

def get_work(soup):
    workplaces = []
    work_div = soup.find('div', {'data-pnref': 'work'})
    if work_div:
        items = work_div.findAll('li')
        for item in items:
            workplace = {
                'name': None,
                'title': None,
            }
            links = item.findAll('a')
            if links:
                link = links[1]
                workplace['name'] = link.string
            title_divs = item.select('div.fsm.fwn.fcg')
            if title_divs:
                workplace['title'] = title_divs[0].string

            if workplace:
                workplaces.append(workplace)
            
    return workplaces

def get_schools(soup):
    schools = []
    school_div = soup.find('div', {'data-pnref': 'edu'})
    if school_div:
        items = school_div.findAll('li')
        for item in items:
            school = {
                'name': None,
                'desc': None,
                'location': None,
            }
            links = item.findAll('a')
            if links:
                link = links[1]
                school['name'] = link.string
            desc_divs = item.select('div.fsm.fwn.fcg')
            if desc_divs:
                desc = desc_divs[0].text

                if desc is not None:
                    parts = desc.split('Â·')
                    location = None
                    if len(parts) > 1:
                        school['desc'], school['location'] = map(str.strip, parts[:2])
                    else:
                        school['location'] = desc.strip()

            if school:
                schools.append(school)
            
    return schools

def get_bio(soup):
    bio = None

    div = soup.find('div', id='pagelet_bio')
    if div:
        ul = div.find('ul')
        if ul:
            bio = ul.text
    
    return bio

def get_cities(soup):
    cities = []
    city_div = soup.find('div', id='pagelet_hometown')
    if city_div:
        items = city_div.findAll('li')
        for item in items:
            city = {
                'name': None,
                'desc': None,
            }
            link = item.find('a')
            if link:
                city['name'] = link.string
            desc_divs = item.select('div.fsm.fwn.fcg')
            if desc_divs:
                city['desc'] = desc_divs[0].text

            if city:
                cities.append(city)
            
    return cities

def get_pic_url(soup):
    url = None
    imgs = soup.select('img.profilePic.img')
    if imgs:
        url = imgs[0].attrs['src']

    return url

def extract_links(div):
    links = []
    els = div.find_all('a')
    for el in els:
        #text = el.text
        match = re.match(r'^.*\?u=(http[^\&]+).*$', el.attrs['href'])
        if match and match.groups():
            href = match.groups()[0]
            links.append(urllib.parse.unquote(href))

    #result = list(filter(lambda l: 'facebook.com' not in l, links))
    return links

def parse_link_els(els):
    results = []
    for link in els:
        m = re.match(r'^.*\?q=(https\://[^\&\?]+).*$', link.attrs['href'])
        if m:
            href = m.groups()[0]
            unquoted = urllib.parse.unquote(href)
            results.append(unquoted)

    return results

def parse_links(s):
    return re.findall(r'(http[^\s]+)', s)

def parse_details(profile_url):
    req = requests.get(profile_url)
    html = req.text
    
    details = {
        'url': profile_url,
        'pic_url': None,
        'name': None,
        'other': {
            'workplaces': [],
            'schools': [],
            'cities': [],
            'bio': None,
        },
    }
    soup = BeautifulSoup(html, 'html.parser')

    #public profile
    about_link = soup.find('a', attrs={'href': re.compile(r'.+/about/.*')})
    about_href = about_link.attrs['href'] if about_link and ('href' in about_link.attrs) else None
    if about_href:
        #profile pic
        meta = soup.find('meta', attrs={'property': 'og:image'})
        if meta:
            pic_url = meta.attrs['content'] if 'content' in meta.attrs else None
            details['pic_url'] = pic_url

        #name
        meta = soup.find('meta', attrs={'property': 'og:title'})
        name = meta.attrs['content'] if meta and ('content' in meta.attrs) else None
        details['name'] = name
        if name:
            req = requests.get('https://facebook.com' + about_href)
            html = req.text
            soup = BeautifulSoup(html, 'html.parser')
            about_div = soup.find('div', attrs={'class': '_4-u2 _3-98 _4-u8'})
            if about_div:
                section_divs = soup.find_all('div', attrs={'class': '_4-u2 _3xaf _3-95 _4-u8'})
                for div in section_divs:
                    title_div = div.find('div', attrs={'class': '_50f7'})
                    title = None
                    if title_div:
                        title = title_div.text.lower()
                        details['other'][title] = {}
                        items = div.findAll('div', attrs={'class': '_5aj7 _3-8j'})
                        for item in items:
                            attr_title = item.find('div', attrs={'class': '_50f4'})
                            attr_details = item.find('div', attrs={'class': '_3-8w'})
                            links = extract_links(item) or parse_links(item.text)

                            if attr_title and links:
                                details['other'][title]['links'] = links
                            elif attr_title and attr_details:
                                details['other'][title][attr_title.text] = attr_details.text
    
    # semi-public profile
    else:
        pic_url = get_pic_url(soup)
        details['pic_url'] = pic_url

        name = get_name(soup)
        details['name'] = name
        if name:
            workplaces = get_work(soup)
            details['other']['workplaces'] = workplaces

            schools = get_schools(soup)
            details['other']['schools'] = schools

            cities = get_cities(soup)
            details['other']['cities'] = cities

            bio = get_bio(soup)
            details['other']['bio'] = bio

    return details

def print_person(person):
    print('---')
    print(person)
    print('---')
    print('')

def insert_person(person, json_file):
    json_file.write(json.dumps(person, sort_keys=True, indent=3))
    
    profile_id = config.DB.insert(
        'profiles',
        platform = 'Facebook',
        profile_url = person['url'],
        profile_handle = person['name'],
        pic_url = person['pic_url'],
        name = person['name'],
        bio = person['other']['bio']
    )

    for city in person['other']['cities']:
        config.DB.insert(
            'locations',
            name = city['name'],
            desc = city['desc'],
            profile_id = profile_id
            )

    for work in person['other']['workplaces']:
        config.DB.insert(
            'workplaces',
            name = work['name'],
            title = work['title'],
            profile_id = profile_id
            )

    for school in person['other']['schools']:
        config.DB.insert(
            'schools',
            name = school['name'],
            desc = school['desc'],
            location = school['location'],
            profile_id = profile_id
        )

if __name__ == '__main__':
    json_file = open('json.txt', mode='w', buffering=1)
    people = search(config.search_name, json_file)
    json_file.close()
