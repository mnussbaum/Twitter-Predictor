#!/usr/bin/env python

# Extracting word information from populations!
# Print to a file readable by libSVM!

from populate import Population
import datetime
import re
import math

def test():
    import populate
    pop = Population(community_file="lizardbill_11_20_2010", new=False)
    udc = WordData(pop)
    return udc

def count_words(text):
    '''Takes a string. Returns a dictionary whose keys are words that appear
    in the string and whose entries are word counts.'''
    counts = {}
    clean = re.compile("""[!();:'",<.>/?-]""")
    words = text.split()
    for word in words:
        word = clean.sub("", word.lower())
        if word == '':
            continue
        if word in counts:
            counts[word] += 1
        else:
            counts[word] = 1
    return counts

def scale(x):
    e = 2.71828182845904523536
    if x == 0:
        return -1
    else:
        y = e ** (-1.0 / x)
        return (2 * y) - 1

months = {'Jan':1, 'Feb':2, 'Mar':3,\
          'Apr':4, 'May':5, 'Jun':6,\
          'Jul':7, 'Aug':8, 'Sep':9,\
          'Oct':10, 'Nov':11, 'Dec':12}

class WordData(object):
    '''Creates dictionaries of words & tweets by date by user.'''
    
    def __init__(self, source_population):
        self._pop = source_population
        # udc.tweets_by_user[uid] -> all of a user's tweets
        self.tweets_by_user = {}
        # udc.tweets_by_user_date[uid][date] -> all of a user's tweets on a day
        self.tweets_by_user_date = {}
        # udc.words_by_user_date[uid][date][word] -> word count for that user
        # on that day for the given word
        self.words_by_user_date = {}
        # udc.words_by_date[date][word] -> wordcount for whole population on
        # given date
        self.words_by_date = {}
        # udc.words_upto_date[date][word] -> wordcount for whole population up
        # to and including given date
        self.words_upto_date = {}
        # lexical data read in from the hoosier corpus
        # keys are orthographic words; entries are dicts with the fields:
        # transcription, length, frequency, logfrequency, familiarity
        self.lexicon = {}
        # a dictionary of word data to write to a csv file for ML!
        # Keys are words mentioned 2 days before data collection
        self.dataset = {}
        
        print "getting tweets by user..."
        self.get_tweets_by_user()
        print "gettings tweets by user and date..."
        self.get_tweets_by_user_date()
        print "gettting word counts by user and date..."
        self.get_words_by_user_date()
        print "getting word counts by date..."
        self.get_words_by_date()
        print "getting word counts up to (& including) 2 days before collection..."
        self.get_words_upto_date()
        print "building lexicon..."
        self.build_lexicon()
        print "building dataset..."
        self.build_dataset()
        print "printing dataset to csv..."
        self.print_dataset()
        
    def get_tweets_by_user(self):
        for user in self._pop._community_members:
            dated_tweets = [(x['created_at'], x['text']) for x in user['tweets']]
            self.tweets_by_user[user['uid']] = dated_tweets
    
    def get_tweets_by_user_date(self):
        for uid in [x['uid'] for x in self._pop._community_members]:
            self.tweets_by_user_date[uid] = {}
            for tweet in self.tweets_by_user[uid]:
                rawdate = tweet[0].split()
                text = tweet[1]
                year = eval(rawdate[5].lstrip('0'))
                month = months[rawdate[1]]
                day = eval(rawdate[2].lstrip('0'))
                date = datetime.date(year, month, day)
                try:
                    self.tweets_by_user_date[uid][date] += [text]
                except:
                    self.tweets_by_user_date[uid][date] = [text]
                    
    def get_words_by_user_date(self):
        for uid in [x['uid'] for x in self._pop._community_members]:
            self.words_by_user_date[uid] = {}
            for date in self.tweets_by_user_date[uid].keys():
                tweets = "\n".join(self.tweets_by_user_date[uid][date])
                self.words_by_user_date[uid][date] = count_words(tweets)
                
    def get_words_by_date(self):
        for user in self.words_by_user_date.keys():
            for date in self.words_by_user_date[user].keys():
                if date not in self.words_by_date:
                    self.words_by_date[date] = {}
                for word in self.words_by_user_date[user][date].keys():
                    count = self.words_by_user_date[user][date][word]
                    if word in self.words_by_date[date]:
                        self.words_by_date[date][word] += count
                    else:
                        self.words_by_date[date][word] = count
                        
    def get_words_upto_date(self, day=None):
        # day defaults to 2 days before collection
        if day == None:
            day = sorted(self.words_by_date.keys())[-3]
        # find all days no later than given date
        dates = filter(lambda x: day >= x, self.words_by_date.keys())
        for date in dates:
            for word in self.words_by_date[date].keys():
                count = self.words_by_date[date][word]
                if word in self.words_upto_date:
                    self.words_upto_date[word] += count
                else:
                    self.words_upto_date[word] = count
                    
    def build_lexicon(self, inpath="hoosier.txt"):
        # Creates a dictionary from hoosier corpus.
        # orthography = 0, transcription=1, length = 2
        # frequency = 3, logfrequency = 4, familiarity=5
        f = open(inpath, 'r')
        lines = f.readlines()[1:]
        for line in lines:
            line = line.split()
            self.lexicon[line[0]] = {'transcription':line[1], \
                                     'length':eval(line[2]), \
                                     'frequency':eval(line[3]), \
                                     'logfrequency':eval(line[4]), \
                                     'familiarity':eval(line[5])}
            
    def build_dataset(self, day_i=None):
        if day_i == None:
            day_i = sorted(self.words_by_date.keys())[-3]
        else:
            self.get_words_upto_date(self, day)
        oneday = datetime.timedelta(1)
        today_words = self.words_by_date[day_i]
        tomorrow_words = self.words_by_date[day_i + oneday]
        yesterday_words = self.words_by_date[day_i - oneday]
        for word in today_words.keys():
            self.dataset[word] = {'tomorrow_frequency':0, \
                                  'today_frequency':0, \
                                  'yesterday_frequency':0, \
                                  'total_population_frequency':0, \
                                  'lexicon_frequency':0, \
                                  'familiarity':0, \
                                  'in_lexicon':0, \
                                  'not_in_lexicon':0, \
                                  'is_hashtag':0, \
                                  'not_hashtag':0, \
                                  'is_atreply':0, \
                                  'not_atreply':0}
            
            # frequency of word on day i + 1
            try:
                freq = tomorrow_words[word]
                self.dataset[word]['tomorrow_frequency'] = freq
            except KeyError: pass
            
            # frequency of word on day i
            freq = today_words[word]
            self.dataset[word]['today_frequency'] = freq
            
            # frequency of word on day i - 1
            try:
                freq = yesterday_words[word]
                self.dataset[word]['yesterday_frequency'] = freq
            except KeyError: pass
            
            # frequency of word in population up to day i
            freq = self.words_upto_date[word]
            self.dataset[word]['total_population_frequency'] = freq
            
            # frequency of word in lexicon
            try:
                freq = self.lexicon[word]['frequency']
                self.dataset[word]['lexicon_frequency'] = freq
            except KeyError: pass
            
            # familiarity of word in lexicon
            try:
                fam = self.lexicon[word]['familiarity']
                self.dataset[word]['familiarity'] = fam
            except KeyError: pass
                
            # is the word in the lexicon?
            if word in self.lexicon:
                self.dataset[word]['in_lexicon'] = 1
            else:
                self.dataset[word]['not_in_lexicon'] = 1
                
            # is the word a hashtag? 0 if no, 1 if yes
            if word[0] == '#':
                self.dataset[word]['is_hashtag'] = 1
            else:
                self.dataset[word]['not_hashtag'] = 1
                
            # is the word an atreply? 0 if no, 1 if yes
            if word[0] == '@':
                self.dataset[word]['is_atreply'] = 1
            else:
                self.dataset[word]['not_atreply'] = 1
                
    def print_dataset(self, name="twitterdata"):
        f = open(name, 'w')
        for word in self.dataset.keys():
            attrs = self.dataset[word]
            data = (str(scale(attrs['tomorrow_frequency'])), \
                    '1:' + str(scale(attrs['today_frequency'])), \
                    '2:' + str(scale(attrs['yesterday_frequency'])), \
                    '3:' + str(scale(attrs['total_population_frequency'])), \
                    '4:' + str(scale(attrs['lexicon_frequency'])), \
                    '5:' + str(attrs['familiarity'] / 7.0), \
                    '6:' + str(attrs['in_lexicon']), \
                    '7:' + str(attrs['not_in_lexicon']), \
                    '8:' + str(attrs['is_hashtag']), \
                    '9:' + str(attrs['not_hashtag']), \
                    '10:' + str(attrs['is_atreply']), \
                    '11:' + str(attrs['not_hashtag']))
            f.write("%s %s %s %s %s %s %s %s %s %s %s %s\n" % data)











