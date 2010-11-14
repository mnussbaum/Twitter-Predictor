import random
from time import sleep
from twitter import TwitterHTTPError
from twitter_user import TwitterUser
from stats import PopulationStats, UserStats
import utils

#TODO decide on population size and how many followers do to take from each person
#TODO decide weighting for filled user score
#TODO decide weighting for scores derived from partially filled populations
#TODO right now our scores give us lots of celebs, this good? If not then fix.

class Population(object):
    '''Gathers a population of interconnected twitter users.'''

    def __init__(self, root_user_name="", max_population=24, \
      max_friends_per_user=5, community_file="", new=True):
        '''Either load a prexisting community to add to or start a new one.
        If not starting a new community then root_user_name doesn't do anything.
        Community is loaded/saved to community_file.'''
        self._new = new
        self._write_path = community_file
        self._max_population = max_population
        self._max_friends_per_user = max_friends_per_user
        #new community
        if new and root_user_name:
            self._root_user_name = root_user_name
            self._node_pool = {}
            self._community_members = []
            self._community = {
                'root_user_name':root_user_name, 
                'node_pool':{},
                'members':[], 
            }
        #add to existing community
        elif not new:
            self._community = utils.read_output(community_file)
            self._root_user_name = self._community['root_user_name']
            self._node_pool = self._community['node_pool']
            self._community_members = self._community['members']
            
    def populate(self):
        if self._new:
            self._initial_populate()
        elif not self._new:
            self._resume_populate()

    def _initial_populate(self):
        '''Gather a group of TwitterUsers. Tries to choose a highly
        interconnected group.''' 
        root_user = TwitterUser(self._root_user_name)
        root_node = root_user.get_all_data()
        self._community_members.append(root_node)
        root_score = self._filled_user_score(root_node)
        #user scores determine how interconnected a user is
        self._node_pool[root_score] = root_node
        self._save()
        #TODO what's a good number of users?
        while self._node_pool and len(self._community_members) < self._max_population:
            #choose person on list with highest interconnection
            highest_score = sorted(self._node_pool, key=self._node_pool.__getitem__, reverse=False)[0]
            curr_node = self._node_pool[highest_score]
            #once a user is chosen for evaluation pop him off the node list
            del self._node_pool[highest_score]
            self._save()
            #choose friends by rank to add to community, seems to work
            #better then followers
            friends = self._sort_by_empty_score(curr_node['friends'])
            for friend in friends[:self._max_friends_per_user]:
                try:
                    tu = TwitterUser(friend)
                    sleep(1)
                    new_user = tu.get_all_data()
                    self._community_members.append(new_user)
                    new_user_score = self._filled_user_score(new_user)
                    self._node_pool[new_user_score] = new_user
                    self._save()
                except TwitterHTTPError:
                    print 'TWITTER HTTP ERROR'
                    return
    
    def _resume_populate(self):
        '''Gather a group of TwitterUsers. Tries to choose a highly
        interconnected group. Picks up where a previous _populate()
        call stopped''' 
        #TODO what's a good number of users?
        while self._node_pool and len(self._community_members) < self._max_population:
            #choose person on list with highest interconnection
            highest_score = sorted(self._node_pool, key=self._node_pool.__getitem__, reverse=False)[0]
            curr_node = self._node_pool[highest_score]
            #once a user is chosen for evaluation pop him off the node list
            del self._node_pool[highest_score]
            self._save()
            #choose friends by rank to add to community, seems to work
            #better then followers
            friends = self._sort_by_empty_score(curr_node['friends'])
            for friend in friends[:self._max_friends_per_user]:
                try:
                    tu = TwitterUser(friend)
                    sleep(1)
                    new_user = tu.get_all_data()
                    self._community_members.append(new_user)
                    new_user_score = self._filled_user_score(new_user)
                    self._node_pool[new_user_score] = new_user
                    self._save()
                except TwitterHTTPError:
                    pass

    def get_community(self):
        return self._community

    def _filled_user_score(self, user):
        '''The score for a user for where user is the result of a TwitterUser object.'''
        if self._community:
            pop_stats = PopulationStats(self._community_members)
            community_member_names = pop_stats.all_users()
            #num of user's followers/friends in the community
            friend_overlap = len(self._intersection(user['friends'], \
              community_member_names))
            follower_overlap = len(self._intersection(user['followers'], \
              community_member_names))
            #num of times user occurs in follower/friends of 
            #people in community
            community_friend_names = pop_stats.all_relation('friends')
            friended = community_friend_names.count(user)
            community_follow_names = pop_stats.all_relation('followers')
            followed = community_follow_names.count(user)
            #at replies to members of the community
            reply_score = 0
            user_stats = UserStats(user, self._community_members)
            replies = user_stats.replies()
            for reply in replies:
                word = reply['word']
                target = word[1:]
                if target in community_member_names:
                    reply_score += 1
            #TODO just total or should we weight? Probably should normalize
            #for current population size some how
            score = follower_overlap + friend_overlap + \
              friended + followed + reply_score
        else:
            score = 0
        return score

    def _empty_user_score(self, user_name):
        '''The score for a user_name.'''
        if self._community:
            stats = PopulationStats(self._community_members)
            community_friend_names = stats.all_relation('friends')
            friended = community_friend_names.count(user_name)
            community_follow_names = stats.all_relation('followers')
            followed = community_follow_names.count(user_name)
            #TODO just total or should we weight? Probably should normalize
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
        
    def _save(self):
        self._community['node_pool'] = self._node_pool
        self._community['members'] = self._community_members
        utils.write_output(self._community, self._write_path)