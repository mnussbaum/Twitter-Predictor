import random
from time import sleep
from twitter import TwitterHTTPError
from twitter_user import TwitterUser
from stats import PopulationStats, UserStats
import utils

#TODO decide on population size and how many followers do to take from each person
#TODO decide weighting for filled user score

class Population(object):
    '''Gathers a population of interconnected twitter users.'''

    def __init__(self, root_user_name, max_population=24, max_friends_per_user=5):
        self._root_user_name = root_user_name
        self._max_population = max_population
        self._max_friends_per_user = max_friends_per_user
        self._community = []

    def populate(self, write_path=None):
        '''Gather a group of TwitterUsers. Tries to choose a highly
        interconnected group.''' 
        root_user = TwitterUser(self._root_user_name)
        root_node = root_user.get_all_data()
        self._community.append(root_node)
        #save with every new user
        utils.write_output(self._community, write_path)
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
            #choose friends by rank to add to community, seems to work
            #better then followers
            friends = self._sort_by_empty_score(curr_node['friends'])
            for friend in friends[:self._max_friends_per_user]:
                try:
                    tu = TwitterUser(friend)
                    sleep(1)
                    new_user = tu.get_all_data()
                    self._community.append(new_user)
                    #save with every new user
                    if write_path:
                        utils.write_output(self._community, write_path)
                    new_user_score = self._filled_user_score(new_user)
                    nodes[new_user_score] = new_user
                except TwitterHTTPError:
                    pass

    def get_community(self, write_path=None):
        if not self._community:
            self.populate(write_path)
        return self._community

    def _filled_user_score(self, user):
        '''The score for a user for where user is the result of a TwitterUser object.'''
        if self._community:
            pop_stats = PopulationStats(self._community)
            community_members = pop_stats.all_users()
            #num of user's followers/friends in the community
            friend_overlap = len(self._intersection(user['friends'], \
              community_members))
            follower_overlap = len(self._intersection(user['followers'], \
              community_members))
            #num of times user occurs in follower/friends of 
            #people in community
            community_friends = pop_stats.all_relation('friends')
            friended = community_friends.count(user)
            community_follows = pop_stats.all_relation('followers')
            followed = community_follows.count(user)
            #at replies to members of the community
            reply_score = 0
            user_stats = UserStats(user, self._community)
            replies = user_stats.replies()
            for reply in replies:
                word = reply['word']
                target = word[1:]
                if target in community_members:
                    reply_score += 1
            #just total or should we weight? Probably should normalize
            #for current population size some how
            score = follower_overlap + friend_overlap + \
              friended + followed + reply_score
        else:
            score = 0
        return score

    def _empty_user_score(self, user_name):
        '''The score for a user_name.'''
        if self._community:
            stats = PopulationStats(self._community)
            community_friends = stats.all_relation('friends')
            friended = community_friends.count(user_name)
            community_follows = stats.all_relation('followers')
            followed = community_follows.count(user_name)
            #just total or should we weight? Probably should normalize
            #for current population size somehow
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

    def _intersection(self, first_list, second_list):
        intersection = set(first_list).intersection(set(second_list))
        return intersection