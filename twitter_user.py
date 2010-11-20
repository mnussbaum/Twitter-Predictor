from datetime import datetime, timedelta
from time import sleep
import twitter
from twitter.oauth import OAuth

from errors import BadUser

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=4)

class TwitterUser(object):
    '''Pulls information about a twitter screen name.'''

    def __init__(self, uid):
        '''Twitter OAuth tokens and secrets, necessary for
        logging in to get higher rate-limit.'''
        con_secret = 'D0yCV2JwUzRstWNvTqDBynT8UbqFSSy7k38MlRHzUK4'
        con_secret_key = 'fQefIH0xSzeV0q2LqHUsZQ'
        token = '216605248-QRmiLAmNIKGEQWsNUSJ6MQGDMq6nhiyZqYJo4zTH'
        token_key = 'dDyY7M4uGrnJ8K7EzTGyuFhazjtW2zEqQlSAOVHmqE'
        self._uid = uid      
        self._twit = twitter.Twitter()
        #self._twit = twitter.Twitter(auth=OAuth(token, token_key, \
        #  con_secret, con_secret_key))

    def _get_follower_ids(self):
        follower_ids = self._twit.followers.ids(user_id=\
          self._uid)        
        return follower_ids

    def _get_friend_ids(self):
        '''Friends are people a user follows.'''
        friend_ids = self._twit.friends.ids(user_id=\
          self._uid)
        return friend_ids

    def _get_tweets(self):
        '''Tweets come with lots of metadata, only keeping some of it.'''
        raw_tweets = self._twit.statuses.user_timeline(user_id=\
          self._uid, count=200)
        trimmed_tweets = []
        desired_fields = ['created_at', 'favorited', 'geo', 'coordinates', \
          'id', 'in_reply_to_screen_name', 'in_reply_to_status_id', \
          'place', 'retweet_count', 'retweeted', 'text','truncated', 'user']
        for tweet in raw_tweets:
            new_tweet = {}
            for field in tweet:
                if field in desired_fields:
                    new_tweet[field] = tweet[field]
            trimmed_tweets.append(new_tweet)
        return trimmed_tweets
        
    def _user_data_from_tweets(self, tweets):
        if tweets:
            most_recent_tweet = tweets[0]
            friend_count = most_recent_tweet['user']['friends_count']
            follower_count = most_recent_tweet['user']['followers_count']
            screen_name = most_recent_tweet['user']['screen_name']
        else:
            friend_count = 0
            follower_count = 0
            screen_name = ""
        return friend_count, follower_count, screen_name
        
    def _active_tweeter(self, tweets):
        tweeted_today = False
        tweeted_yesterday = False
        for tweet in tweets:
            raw_timestamp = tweet['created_at']
            split_timestamp = raw_timestamp.split()
            month_dict = {"Jan":1, "Feb":2, "Mar":3, "Apr":4, "May":5, \
              "Jun":6, "Jul":7, "Aug":8, "Sep":9, "Oct":10, "Nov":11, \
              "Dec":12}
            year = int(split_timestamp[5])
            month = int(month_dict[split_timestamp[1]])
            day = int(split_timestamp[2])
            formatted_timestamp = datetime(year, month, day)
            now = datetime.now()
            time_diff = now - formatted_timestamp
            if time_diff <= timedelta(days=1):
                tweeted_today = True
            if time_diff <= timedelta(days=2) and time_diff > timedelta(days=1):
                tweeted_yesterday = True
        return tweeted_today and tweeted_yesterday

    def get_all_data(self):
        '''Runs all data gathering methods, returns results.'''
        self._timestamp = datetime.now()
        tweets = self._get_tweets()
        friend_count, follower_count, screen_name = self._user_data_from_tweets(tweets)
        if friend_count > 5000 or follower_count > 5000:
           raise BadUser('too many friends/followers')
        if not self._active_tweeter(tweets):
            raise BadUser('not an active tweeter')
        sleep(1)
        follower_ids = self._get_follower_ids()
        sleep(1)
        friend_ids = self._get_friend_ids()        
        sleep(1)
        result = {'tweets':tweets, 'friend_ids':friend_ids, 'follower_ids':follower_ids, \
          'uid':self._uid, 'timestamp':self._timestamp, 'friend_count':friend_count, \
          'follower_count':follower_count, 'screen_name':screen_name}
        return result