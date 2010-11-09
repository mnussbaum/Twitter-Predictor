import random
from time import sleep
from twitter import TwitterHTTPError
from twitter_user import TwitterUser
from stats import Stats

#TODO decide on population size and how many followers do to take from each person
#TODO more granular caching

class Population(object):
   
    def __init__(self, root_user_name, max_population=100, max_followers_per_user=10):
        self._root_user_name = root_user_name
        self._max_population = max_population
        self._max_followers_per_user = max_followers_per_user
        self._community = []
        
    def populate(self):
        '''Gather a group of TwitterUsers. Tries to choose a highly
        interconnected group.''' 
        root_user = TwitterUser(self._root_user_name)
        root_node = root_user.get_all_data()
        root_score = self._filled_user_score(root_node)
        #user scores determine how interconnected a user is
        nodes = {root_score:root_node}
        #what's a good number of users?
        while nodes and len(self._community) < self._max_population:
            #choose person on list with highest interconnection
            highest_score = sorted(nodes, key=nodes.__getitem__, reverse=False)[0]
            curr_node = nodes[highest_score]
            #once a user is chosen for evaluation pop him off the node list
            del nodes[highest_score]
            #choose followers by rank to add to community
            followers = self._sort_by_empty_score(curr_node['followers'])
            for follower in followers[:self._max_followers_per_user]:
                try:
                    tu = TwitterUser(follower)
                    sleep(1)
                    new_user = tu.get_all_data()
                    self._community.append(new_user)
                    new_user_score = self._filled_user_score(new_user)
                    nodes[new_user_score] = new_user
                except TwitterHTTPError:
                    pass
    
    def get_community(self):
        return self._community
        
    def _filled_user_score(self, user):
        if self._community:
            stats = Stats(self._community)
            community_members = stats.all_users()
            #num of user's followers/friends in the community
            friend_overlap = len(self._intersection(user['friends'], community_members))
            follower_overlap = len(self._intersection(user['followers'], community_members))
            #num of times user occurs in follower/friends of 
            #people in community
            community_friends = stats.all_relation('friends')
            friended = community_friends.count(user)
            community_follows = stats.all_relation('followers')
            followed = community_follows.count(user)
            #at replies to members of the community
            reply_score = 0
            replies = stats.user_replies(user['screen_name'])
            for reply in replies:
                word = reply['word']
                target = word[1:]
                if target in community_members:
                    reply_score += 1
            #just total or should we weight? Probably should normalize for current population size somehow
            score = follower_overlap + friend_overlap + friended + followed + reply_score
        else:
            score = 0
        return score
    
    def _empty_user_score(self, user):
        '''Number of times user occurs in follower/friends of 
        people in community'''
        if self._community:
            stats = Stats(self._community)
            community_friends = stats.all_relation('friends')
            friended = community_friends.count(user)
            community_follows = stats.all_relation('followers')
            followed = community_follows.count(user)
            #just total or should we weight? Probably should normalize for current population size somehow
            score = friended + followed
        else:
            score = 0
        return 0
    
    def _sort_by_empty_score(self, user_names):
        users = {}
        shuffle_names = user_names[:]
        #random shuffle in case all scores are 0
        random.shuffle(shuffle_names)
        for user_name in shuffle_names:
            score = self._empty_user_score(user_name)
            users[user_name] = score
        sorted_users = sorted(users, key=users.get)
        return sorted_users
        

    def _intersection(self, first_item, second_item):
        intersection = set(first_item).intersection(set(second_item))
        return intersection