import argparse, os, sys, traceback
import hashlib
import inflect
import redis
import requests

from pyquery import PyQuery as PQ
from twython import Twython

TWITTER_CONSUMER_KEY = os.environ['TWITTER_CONSUMER_KEY']
TWITTER_CONSUMER_SECRET = os.environ['TWITTER_CONSUMER_SECRET']
TWITTER_ACCESS_TOKEN = os.environ['TWITTER_ACCESS_TOKEN']
TWITTER_ACCESS_SECRET = os.environ['TWITTER_ACCESS_SECRET']
INFLECTION = inflect.engine()

DRY_RUN = True
LOCAL_TEST = True

# this could be used to scrape other locations,
# if one were so inclined
LOCATIONS = [
    {
        'name': 'South Hill Growler Guys',
        'url': 'http://www.thegrowlerguys.com/whats-on-tap/washington-spokane-south-hill/',
    },
]

def create_redis_connection():
    redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
    r = redis.from_url(redis_url)
    
    return r

def flush_redis():
    '''
    Empty the current redis db
    '''
    r = create_redis_connection()
    r.flushdb()
    
    print 'Redis keys set to: ' + str(r.keys())

def fetch_taps(seed_db=False):
    for location in LOCATIONS:
        location_name = location['name']
        if LOCAL_TEST:
            page = PQ(filename='test.html')
        else:
            page = PQ(location['url'])
        r = create_redis_connection()
        
        beer_list = page('.beerTapList li')
        for item in beer_list:
            beer_obj = PQ(item)
            tap_number = beer_obj('.tap_number').text().strip()
            
            beer = build_beer_record(
                location = location_name,
                name = beer_obj('.beerName .title').text().strip(),
                style = beer_obj('.beerName .style').text().strip().strip('- ').lower(),
                brewery = beer_obj('.brewery').text().strip(),
                city = beer_obj('.breweryInfo .txt').text().strip().strip('- ').replace(' ,',','),
            )
            
            # make a hash value for the key key
            h = hashlib.md5(b'{0} {1}'.format(beer['location'], tap_number))
            redis_key = h.hexdigest()
            
            current_tap = r.hgetall(redis_key)
            if cmp(beer, current_tap) != 0:
                if not seed_db: tweet_tap_update(beer, current_tap)
                r.hmset(redis_key, beer)
            else:
                pass

def build_beer_record(location, name, style=None, brewery=None, city=None):
    beer = {
        'location': location,
        'name': name,
        'style': style,
        'brewery': brewery,
        'city': city
    }
    
    return prettify(beer)
    
def compare_taps(beer, redis_key, seed_db):
    current_tap = r.hgetall(redis_key)
    if cmp(beer, current_tap) != 0:
        if not seed_db: tweet_tap_update(beer, current_tap)
        r.hmset(redis_key, beer)
    else:
        pass
    
def prettify(beer):
    if 'style' in beer:
        capitals = ['Imperial', 'IPA', 'Russian', 'Scottish', 'Scotch', 'Cascadian', 'Belgian', 'German', 'American', 'British', 'Munich', 'Flanders', 'Christmas', 'Double', 'Triple']
        for item in capitals:
            if item.lower() in beer['style']:
                beer['style'] = beer['style'].replace(item.lower(), item)
            
        hyphenated = ['barrel-aged']
        for item in hyphenated:
            unhyphenated = item.replace('-', ' ')
            if unhyphenated in beer['style']:
                beer['style'] = beer['style'].replace(unhyphenated, item)
            
    return beer

def tweet_tap_update(beer, previous_beer=None):
    twitter = Twython(
        TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET,
        TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
    )
    
    # tweet about the beer that used to be on tap
    if previous_beer:
        tweet = 'Blown keg at {0}: {1}, {2} from {3} in {4} is gone'.format(
            previous_beer['location'], previous_beer['name'],
            INFLECTION.a(previous_beer['style']),
            previous_beer['brewery'], previous_beer['city']
        )
        tweet = check_tweet(tweet)

        if DRY_RUN:
            print 'Would Tweet: ' + tweet
        else:
            twitter.update_status(status=tweet)

    # tweet about the new beer on tap
    tweet = 'Now on tap at {0}: {1}, {2} from {3} in {4}'.format(
        beer['location'], beer['name'],
        INFLECTION.a(beer['style']),
        beer['brewery'], beer['city']
    )
    tweet = check_tweet(tweet)
    
    if DRY_RUN:
        print 'Would Tweet: ' + tweet
    else:
        twitter.update_status(status=tweet)

def check_tweet(tweet):
    if len(tweet) > 140:
        tweet = tweet[:137] + '...'

    return tweet

def process_args(arglist=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', action='store_const', const=True)
    parser.add_argument('--flush', action='store_const', const=True)
    args = parser.parse_args()
    
    return args

def main(args=None):
    if args is None:
        args = sys.argv[1:]
    args = process_args(args)
    
    if args.flush:
        flush_redis()
    else:
        fetch_taps(seed_db=args.seed)

if __name__ == '__main__':
    try:
        main()
    except Exception, e:
        sys.stderr.write('\n')
        traceback.print_exc(file=sys.stderr)
        sys.stderr.write('\n')
        sys.exit(1)

