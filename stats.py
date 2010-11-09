from word_counts import WordCounter

#TODO get retweets -- it looks like you need to be friends with a user to get their retweets

class Stats(object):
    
    def __init__(self, population):
        self._population = population

    def relation_list_overlap(self, list_name):
        '''
        Number of users occurring in multiple follower/friends
        (or other) lists, how many re-occurrences.
        '''
        if list_name not in self._population[0]:
            raise Exception("User doesn't have list: %s" % list_name)
        all_list_members = []
        for user in self._population:
            all_list_members.extend(user[list_name])
        duplicates = []
        for list_member in all_list_members:
            copied_list_members = all_list_members[:]
            copied_list_members.remove(list_member)
            if list_member in copied_list_members and list_member not in duplicates:
                duplicates.append(list_member)
        assigned_duplicates = {}
        for duplicate in duplicates:
            for user in self._population:
                if duplicate in user[list_name]:
                    if user['screen_name'] in assigned_duplicates:
                        if duplicate not in assigned_duplicates[user['screen_name']]:
                            assigned_duplicates[user['screen_name']].append(duplicate)
                    else:
                        assigned_duplicates[user['screen_name']] = [duplicate]
        return len(duplicates), assigned_duplicates
    
    def word_data(self):
        '''Word counts and neighbors for all tweets combined into one.'''
        all_text = ""
        for user in self._population:
            tweets = user['tweets']
            for tweet in tweets:
                all_text += tweet['text']
        counter = WordCounter(all_text)
        word_data = counter.get_word_data()
        return word_data
    
    def all_users(self):
        '''All user screen names.'''
        user_names = []
        for user in self._population:
            user_names.append(user['screen_name'])
        return user_names
    
    def all_relation(self, list_name):
        '''Get all followers/friends names.'''
        if list_name not in self._population[0]:
            raise Exception("User doesn't have list: %s" % list_name)
        relation_names = []
        for user in self._population:
            relations = user[list_name]
            relation_names.extend(relations)
        return relation_names
    
    def user_word_data(self, user_name, by_tweet=True):
        '''Word counts and neighbors for each of a user's tweets or all of a user's tweets.'''
        for user in self._population:
            if user['screen_name'] == user_name:
                found = True
                break
            else:
                found = False
        if not found:
            raise Exception('User not in population: %s' % user_name)
        #either gets users word data by tweet or in entirety
        if by_tweet:
            tweet_data = []
            for tweet in user['tweets']:
                text = tweet['text']
                counter = WordCounter(text)
                word_data = counter.get_word_data()
                tweet_data.append({'id':tweet['id'], 'text':text, 'word_data':word_data})
            return tweet_data
        elif not by_tweet:
            all_text = ""
            for tweet in user['tweets']:
                all_text += ' ' + tweet['text']
            counter = WordCounter(all_text)
            word_data = counter.get_word_data()
            return word_data
    
    def user_hash_tags(self, user_name):
        word_data = self.user_word_data(user_name, by_tweet=False)
        found_hashes = []
        for word in word_data:
            if word[0] == "#":
                found_hashes.append(word_data[word])
        return found_hashes
        
    def user_replies(self, user_name):
        word_data = self.user_word_data(user_name, by_tweet=False)
        found_replies = []
        for word in word_data:
            if word[0] == "@":
                found_replies.append(word_data[word])
        return found_replies