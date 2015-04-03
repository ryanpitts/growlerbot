import os
import inflect
import redis
import requests

from pyquery import PyQuery as PQ
from twython import Twython

# this could be used to scrape other Growler Guys locations,
# if one were so inclined
LOCATION_URLS = {
    'Spokane South Hill': 'http://www.thegrowlerguys.com/whats-on-tap/washington-spokane-south-hill/'
}

TWITTER_CONSUMER_KEY = os.environ['TWITTER_CONSUMER_KEY']
TWITTER_CONSUMER_SECRET = os.environ['TWITTER_CONSUMER_SECRET']
TWITTER_ACCESS_TOKEN = os.environ['TWITTER_ACCESS_TOKEN']
TWITTER_ACCESS_SECRET = os.environ['TWITTER_ACCESS_SECRET']
INFLECTION = inflect.engine()

def fetch_taps(location='Spokane South Hill'):
    page = PQ(LOCATION_URLS[location])
    beer_list = page('.beerTapList li')
    redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
    r = redis.from_url(redis_url)
    
    for item in beer_list:
        beer_obj = PQ(item)
        tap_number = beer_obj('.tap_number').text().strip()
        
        beer = {
            'tap_number': tap_number,
            'name': beer_obj('.beerName .title').text().strip(),
            'style': beer_obj('.beerName .style').text().strip().strip('- ').lower(),
            'brewery': beer_obj('.brewery').text().strip(),
            'city': beer_obj('.breweryInfo .txt').text().strip().strip('- ').replace(' ,',','),
        }
        beer = prettify(beer)
        
        redis_key = '{0} {1}'.format(location, tap_number)
        current_tap = r.hgetall(redis_key)
        if cmp(beer, current_tap) != 0:
            #print 'New beer on Tap {0}: {1}'.format(tap_number, beer['name'])
            tweet(beer)
            r.hmset(redis_key, beer)
        else:
            #print 'Same beer on Tap {0}'.format(tap_number)
            pass

def prettify(beer):
    capitals = ['Imperial', 'IPA', 'Russian', 'Scottish', 'Cascadian', 'Belgian']
    for item in capitals:
        if item.lower() in beer['style']:
            beer['style'] = beer['style'].replace(item.lower(), item)
            
    hyphenated = ['barrel-aged']
    for item in hyphenated:
        if beer['style'] == item.replace('-', ' '):
            beer['style'] = item
            
    return beer

def tweet(beer):
    twitter = Twython(
        TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET,
        TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
    )
    
    tweet = 'Now on Tap {0} at South Hill Growler Guys: {1}, {2} from {3} in {4}'.format(
        beer['tap_number'], beer['name'], INFLECTION.a(beer['style']),
        beer['brewery'], beer['city']
    )
    if len(tweet) > 140:
        tweet = tweet[:137] + '...'
    
    #print tweet
    twitter.update_status(status=tweet)

if __name__ == "__main__":
    fetch_taps()
