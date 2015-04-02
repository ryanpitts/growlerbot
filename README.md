GrowlerBot
==========

A little Python script that scrapes a tap list from the web, compares it to data from the last scrape, and posts any new beers to a Twitter account. Designed to be run as a cron job.

As configured, this bot is aimed at the [South Hill Growler Guys](http://www.thegrowlerguys.com/whats-on-tap/washington-spokane-south-hill/') in Spokane, WA. It tweets at [@SoHillGrowlers](https://twitter.com/SoHillGrowlers).

To post to Twitter, you'll need to create an app and generate an auth token, then store some environment variables. To add these to Heroku, for example:

```bash
heroku config:set TWITTER_CONSUMER_KEY=<your_key> \
                  TWITTER_CONSUMER_SECRET=<your_secret> \
                  TWITTER_ACCESS_TOKEN=<your_token> \
                  TWITTER_ACCESS_SECRET=<your_token_secret>
```