from datetime import datetime
from time import sleep
import twitter
from twitter.oauth import OAuth

class TwitterUser(object):
    '''Pulls information about a twitter screen name.'''
    
    def __init__(self, user_screen_name):
        #Twitter OAuth tokens and secrets, necessary for logging in to get higher rate-limit
        con_secret = '3fxVf35NsyWhepbAYnDijr5uVK1jnTEIQwuSOaFbqA'
        con_secret_key = 'trIWfh6cLrWtX75DLgTGA'
        token = '49893981-FjrShAQdJCTYsITL81QZJRlzq4KVMd2dBg6Z8h1ax'
        token_key = 'xkCRbB5nBRl9niuC4gYgpOd0ka3tIf391SNmBEdRBs0'
        self._uname = user_screen_name      
        self._timestamp = datetime.now()
        self._twit = twitter.Twitter(auth=OAuth(token, token_key, con_secret, con_secret_key))

    def _get_followers(self):
        raw_followers = self._twit.statuses.followers(screen_name=self._uname)
        followers = []
        for rf in raw_followers:
            followers.append(rf['screen_name'])
        return followers

    def _get_friends(self):
        '''Friends are people a user follows.'''
        raw_friends = self._twit.statuses.friends(screen_name=self._uname)
        friends = []
        for rf in raw_friends:
            friends.append(rf['screen_name'])
        return friends

    def _get_tweets(self):
        '''Tweets come with lots of metadata, only keeping some of it.'''
        raw_tweets = self._twit.statuses.user_timeline(screen_name=self._uname)
        trimmed_tweets = []
        desired_fields = ['created_at', 'favorited', 'geo', 'coordinates', 'id', \
          'in_reply_to_screen_name', 'in_reply_to_status_id', 'place', \
          'retweet_count', 'retweeted', 'text','truncated']
        for tweet in raw_tweets:
            new_tweet = {}
            for field in tweet:
                if field in desired_fields:
                    new_tweet[field] = tweet[field]
            trimmed_tweets.append(new_tweet)
        return trimmed_tweets
        
        
    def get_all_data(self):
        '''Runs all data gathering methods, returns results.'''
        followers = self._get_followers()
        sleep(1)
        friends = self._get_friends()
        sleep(1)
        tweets = self._get_tweets()
        sleep(1)
        result = {'tweets':tweets, 'friends':friends, 'followers':followers, \
          'screen_name':self._uname, 'timestamp':self._timestamp}
        return result