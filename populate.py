import random
from time import sleep
import logging
from urllib2 import URLError
from __init__ import LOG_FILENAME
from twitter import TwitterHTTPError
from twitter_user import TwitterUser
from stats import PopulationStats, UserStats
from errors import BadUser
import utils

#TODO decide on weighting for @replies

class Population(object):
    '''Gathers a population of interconnected twitter users.'''

    def __init__(self, root_user_id="", max_population=24, \
      max_friends_per_user=5, community_file="", new=True, safe=False):
        '''Either load a prexisting community to add to or start a new one.
        If not starting a new community then root_user_id doesn't do anything.
        Community is loaded/saved to community_file.'''
        logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG, 
          format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
          datefmt='%m-%d %H:%M')
        self._new = new
        self._write_path = community_file
        self._max_population = max_population
        self._max_friends_per_user = max_friends_per_user
        self._safe = safe
        #new community
        if new and root_user_id:
            self._root_user_id = root_user_id
            self._node_pool = {}
            self._community_members = []
            self._community = {
                'root_user_id':root_user_id, 
                'node_pool':{},
                'members':[], 
            }
        #add to existing community
        elif not new:
            self._community = utils.read_output(community_file)
            self._root_user_id = self._community['root_user_id']
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
        root_user = TwitterUser(self._root_user_id)
        root_node = root_user.get_all_data()
        self._community_members.append(root_node)
        root_score = self._filled_user_score(root_node)
        #user scores determine how interconnected a user is
        self._node_pool[self._root_user_id] = {'user':root_node, 'score':root_score}
        logging.debug('Adding root to node_pool')
        self.save()
        self._resume_populate()
            
    def _resume_populate(self):
        '''Gather a group of TwitterUsers. Tries to choose a highly
        interconnected group. Picks up where a previous _populate()
        call stopped''' 
        while self._node_pool and len(self._community_members) < self._max_population:
            #choose person on list with highest interconnection
            #first 0 at end of line is to take first user, second 0 get's user's id from tuple result
            self._rescore_node_pool()
            highest_scoring_id = sorted(self._node_pool.items(), key=lambda item: item[1]['score'], reverse=True)[0][0]
            curr_node = self._node_pool[highest_scoring_id]['user']
            print 'A'
            print 'highest_scoring_id', highest_scoring_id
            print 'highest_scoring_id in nodes:', highest_scoring_id in self._node_pool
            #choose friends by rank to add to community, seems to work
            #better then followers
            friend_ids = self._sort_by_empty_score(curr_node['friend_ids'])
            added_count = 0
            community_ids = []
            for member in self._community_members:
                community_ids.append(member['uid'])
            #flag to delete the id we are using from the node pool when finished with it
            delete_highest_scoring_id = True
            for friend_id in friend_ids:
                if added_count <= self._max_friends_per_user:
                    try:
                        if friend_id not in community_ids:
                            tu = TwitterUser(friend_id)
                            sleep(1)
                            new_user = tu.get_all_data()
                            #TODO add some sort of conditions for addition to the community
                            self._community_members.append(new_user)
                            logging.debug('TwitterUser accepted to community')
                            new_user_score = self._filled_user_score(new_user)
                            self._node_pool[friend_id] = {'user':new_user, 'score':new_user_score}
                            if self._safe:
                                self.save()
                            print len(self._community_members), "members"
                            added_count += 1
                            logging.debug('TwitterUser accepted to node_pool')
                            delete_highest_scoring_id = True
                    except TwitterHTTPError as error:
                        logging.debug('Twitter error: %s' % error)
                        self.save()
                        print error
                        print "Number of members: ", len(self._community_members)
                        #rate limiting error
                        if '400' in str(error) or '420' in str(error):
                           delete_highest_scoring_id = False
                           logging.debug('Hit rate limit, quitting')
                           return
                        #unauthorized for user error
                        elif '401' in str(error) or '404' in str(error):
                            delete_highest_scoring_id = True
                            if self._safe:
                                self.save()
                        #otherwise it's probably just a twitter server issue
                        else:
                            delete_highest_scoring_id = False
                            logging.debug('Server error, sleeping for 5 secs')
                            sleep(5)
                    except BadUser as error:
                        delete_highest_scoring_id = True
                        logging.debug('TwitterUser rejected: %s' % error)
                    except URLError:
                        delete_highest_scoring_id = False
                        logging.debug('URLError, sleeping for 5 secs')
                        sleep(5)
                    
            #once a user is chosen for evaluation pop him off the node list
            del self._node_pool[highest_scoring_id]
            if self._safe:
                self.save()
            logging.debug('Deleting node from node pool')
        self.save()
        print "Maximum community size reached."
        print "Number of members: ", len(self._community_members)

    def get_community(self):
        return self._community
        
    def _rescore_node_pool(self):
        for node_id in self._node_pool:
            curr_node = self._node_pool[node_id]
            curr_node['score'] = self._filled_user_score(curr_node['user'])

    def _filled_user_score(self, user):
        '''The score for a user for where user is the result of a TwitterUser object.'''
        if self._community:
            pop_stats = PopulationStats(self._community_members)
            community_member_ids = pop_stats.all_user_ids()
            #num of user's followers/friends in the community
            friend_overlap = len(self._intersection(user['friend_ids'], \
              community_member_ids))
            try:
                friend_percent_overlap = friend_overlap/user['friend_count']
            except ZeroDivisionError:
                friend_percent_overlap = 0
            follower_overlap = len(self._intersection(user['follower_ids'], \
              community_member_ids))
            try:
                follower_percent_overlap = follower_overlap/user['follower_count']
            except ZeroDivisionError:
                follower_percent_overlap = 0
            
            reply_score = 0
            user_stats = UserStats(user, self._community_members)
            replies = user_stats.replies()
            member_ids = [user['uid'] for user in self._community_members]
            for replying_to in replies:
                if replying_to in member_ids:
                    reply_score += 1
            score = follower_percent_overlap + friend_percent_overlap
            #+ reply_score
        else:
            score = 0
        return score

    def _empty_user_score(self, user_id):
        '''The score for a user_id.'''
        if self._community:
            stats = PopulationStats(self._community_members)
            community_friend_ids = stats.all_relation('friend_ids')
            friended = community_friend_ids.count(user_id)
            community_follow_ids = stats.all_relation('follower_ids')
            followed = community_follow_ids.count(user_id)
            score = friended + followed
        else:
            score = 0
        return 0

    def _sort_by_empty_score(self, user_ids):
        users = {}
        shuffle_ids = user_ids[:]
        #random shuffle in case all scores are 0
        random.shuffle(shuffle_ids)
        for uid in shuffle_ids:
            score = self._empty_user_score(uid)
            users[uid] = score
        sorted_users = sorted(users, key=users.get)
        return sorted_users

    def _intersection(self, first_list, second_list):
        intersection = set(first_list).intersection(set(second_list))
        return intersection
        
    def save(self):
        self._community['node_pool'] = self._node_pool
        self._community['members'] = self._community_members
        utils.write_output(self._community, self._write_path)
