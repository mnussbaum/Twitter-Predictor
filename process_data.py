#!/usr/bin/env python

# Extracting word information from populations!
# Anatomy of a twittery user!
# pt.tweets_by_user_date[15573995][datetime.date(2010, 5, 1)]

from populate import Population
import datetime
import re
import math

def udctest():
    import populate
    pop = Population(community_file="lizardbill_11_20_2010", new=False)
    udc = UserDatedCounts(pop)
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

months = {'Jan':1, 'Feb':2, 'Mar':3,\
          'Apr':4, 'May':5, 'Jun':6,\
          'Jul':7, 'Aug':8, 'Sep':9,\
          'Oct':10, 'Nov':11, 'Dec':12}

class UserDatedCounts(object):
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
        # Keys are words mentioned 2 days before data collection; fields are:
        # 
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
            self.dataset[word] = {'tomorrow_logfrequency':'?', \
                                  'today_logfrequency':'?', \
                                  'yesterday_logfrequency':'?', \
                                  'total_population_logfrequency':'?', \
                                  'lexicon_logfrequency':'?', \
                                  'familiarity':'?', \
                                  'in_lexicon':'?', \
                                  'is_hashtag':'?', \
                                  'is_atreply':'?'}
            
            # log frequency of word on day i + 1
            try:
                LF = math.log(tomorrow_words[word], 10)
                self.dataset[word]['tomorrow_logfrequency'] = LF
            except KeyError:
                self.dataset[word]['tomorrow_logfrequency'] = -1
            
            # log frequency of word on day i
            LF = math.log(today_words[word], 10)
            self.dataset[word]['today_logfrequency'] = LF
            
            # log frequency of word on day i - 1
            try:
                LF = math.log(yesterday_words[word], 10)
                self.dataset[word]['yesterday_logfrequency'] = LF
            except KeyError: pass
            
            # log frequency of word in population up to day i
            LF = math.log(self.words_upto_date[word], 10)
            self.dataset[word]['total_population_logfrequency'] = LF
            
            # log frequency of word in lexicon
            try:
                LF = self.lexicon[word]['logfrequency']
                self.dataset[word]['lexicon_logfrequency'] = LF
            except KeyError: pass
            
            # familiarity of word in lexicon
            try:
                fam = self.lexicon[word]['familiarity']
                self.dataset[word]['familiarity'] = fam
            except KeyError: pass
            
            # is the word in the lexicon? 0 if no, 1 if yes
            if word in self.lexicon:
                self.dataset[word]['in_lexicon'] = 1
            else:
                self.dataset[word]['in_lexicon'] = 0
                
            # is the word a hashtag? 0 if no, 1 if yes
            if word[0] == '#':
                self.dataset[word]['is_hashtag'] = 1
            else:
                self.dataset[word]['is_hashtag'] = 0
                
            # is the word an atreply? 0 if no, 1 if yes
            if word[0] == '@':
                self.dataset[word]['is_atreply'] = 1
            else:
                self.dataset[word]['is_atreply'] = 0
                
    def print_dataset(self, name="twitterdata"):
        f = open(name + '.csv', 'w')
        f.write("tomorrow_logfrequency,today_logfrequency,yesterday_logfrequency,total_population_logfrequency,lexicon_logfrequency,familiarity,in_lexicon,is_hashtag,is_atreply\n")
        for word in self.dataset.keys():
            attrs = self.dataset[word]
            data = (repr(attrs['tomorrow_logfrequency']), \
                    repr(attrs['today_logfrequency']), \
                    repr(attrs['yesterday_logfrequency']), \
                    repr(attrs['total_population_logfrequency']), \
                    repr(attrs['lexicon_logfrequency']), \
                    repr(attrs['familiarity']), \
                    repr(attrs['in_lexicon']), \
                    repr(attrs['is_hashtag']), \
                    repr(attrs['is_atreply']))
            f.write("%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % data)











