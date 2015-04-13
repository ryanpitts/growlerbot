import hashlib
from pyquery import PyQuery as PQ

from utils.format_beers import build_beer_record

LOCAL_TEST = False

def scrape_growler_guys(location):
    taps = {}

    if LOCAL_TEST:
        page = PQ(filename='test.html')
    else:
        page = PQ(location['url'])

    beer_list = page('.beerTapList li')
    for item in beer_list:
        beer_obj = PQ(item)
        tap_number = beer_obj('.tap_number').text().strip()

        beer = build_beer_record(
            location = location['name'],
            name = beer_obj('.beerName .title').text().strip().encode('utf-8'),
            style = beer_obj('.beerName .style').text().strip().strip('- ').lower().encode('utf-8'),
            brewery = beer_obj('.brewery').text().strip().encode('utf-8'),
            city = beer_obj('.breweryInfo .txt').text().strip().strip('- ').replace(' ,',',').encode('utf-8'),
        )

        # make a hash value for the key
        h = hashlib.md5(b'{0} {1}'.format(beer['location'], tap_number))
        beer_key = h.hexdigest()
        taps[beer_key] = beer

    return taps