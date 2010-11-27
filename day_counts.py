#!/usr/bin/python

from word_counts import WordCounter
from utils import read_output, parse_twitter_timestamp

class DayCounts(object):
    def __init__(self, community):
        self._community_members = community['members']
        self._tweets_by_day = self._split_tweets()
        
    def _split_tweets(self):
        tweet_days = {}
        for member in self._community_members:
            tweets = member['tweets']
            for tweet in tweets:
                raw_timestamp = tweet['created_at']
                formatted_timestamp = parse_twitter_timestamp(raw_timestamp)
                if formatted_timestamp in tweet_days:
                    tweet_days[formatted_timestamp].append(tweet)
                else:
                    tweet_days[formatted_timestamp] = [tweet]
        return tweet_days
        
    def words_by_day(self):
        word_counts = {}
        for day, tweets in self._tweets_by_day.items():
            tweet_text = ''
            for tweet in tweets:
                tweet_text += tweet['text']
            day_counts = WordCounter(tweet_text).get_word_data()
            word_counts[day] = day_counts
        return word_counts
        
if __name__ == "__main__":
    community = read_output('pickled_populations/lizardbill_11_20_2010')
    dc = DayCounts(community)
    wc = dc.words_by_day()
    import pprint
    pprint.pprint(wc)