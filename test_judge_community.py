#! /usr/bin/python
from time import sleep
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=4)
from datetime import datetime
from populate import Population
from stats import PopulationStats
from utils import write_output, read_output

#TODO make a much better way to judge community

def main():
    community = read_output('pickled_populations/testing_community_ids')
    s = PopulationStats(community['members'])
    community_member_names = s.all_user_names()
    print 'Community Members:'
    pp.pprint(community_member_names)
    for user in community['members']:
        print '\n'
        print 'User:', user['screen_name']
        print 'Tweet Count:', len(user['tweets'])
        print 'Friend IDs:', len(user['friend_ids'])
        print 'Follower IDs:', len(user['follower_ids'])
             
if __name__=="__main__":
   main()