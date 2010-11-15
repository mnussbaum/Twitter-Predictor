from datetime import datetime
from time import sleep
import twitter
from twitter.oauth import OAuth

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=4)

#TODO get longer friends/follower lists right now can only get 100
#TODO might be possible to get retweets with include_rts parameter, investigate

class TwitterUser(object):
    '''Pulls information about a twitter screen name.'''

    def __init__(self, uid):
        '''Twitter OAuth tokens and secrets, necessary for
        logging in to get higher rate-limit.'''
        con_secret = '3fxVf35NsyWhepbAYnDijr5uVK1jnTEIQwuSOaFbqA'
        con_secret_key = 'trIWfh6cLrWtX75DLgTGA'
        token = '49893981-FjrShAQdJCTYsITL81QZJRlzq4KVMd2dBg6Z8h1ax'
        token_key = 'xkCRbB5nBRl9niuC4gYgpOd0ka3tIf391SNmBEdRBs0'
        self._uid = uid      
        self._twit = twitter.Twitter(auth=OAuth(token, token_key, \
          con_secret, con_secret_key))

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
          'place', 'retweet_count', 'retweeted', 'text','truncated']
        for tweet in raw_tweets:
            new_tweet = {}
            for field in tweet:
                if field in desired_fields:
                    new_tweet[field] = tweet[field]
            trimmed_tweets.append(new_tweet)
        return trimmed_tweets

    def get_all_data(self):
        '''Runs all data gathering methods, returns results.'''
        self._timestamp = datetime.now()
        follower_ids = self._get_follower_ids()
        sleep(1)
        friend_ids = self._get_friend_ids()
        sleep(1)
        tweets = self._get_tweets()
        sleep(1)
        result = {'tweets':tweets, 'friend_ids':friend_ids, 'follower_ids':follower_ids, \
          'uid':self._uid, 'timestamp':self._timestamp}
        return result