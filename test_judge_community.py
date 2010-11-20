#! /usr/bin/python
from time import sleep
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=4)
from datetime import datetime
from populate import Population
from stats import PopulationStats
from utils import write_output, read_output

def main():
    community = read_output('pickled_populations/lizardbill_11_20_2010')
    s = PopulationStats(community['members'])
    community_member_names = s.all_user_names()
    print 'Community Members:', len(community['members'])
    for user in community['members']:
        print ''
        print 'User:', user['screen_name']
        print 'ID:', user['uid']
        print 'Tweet Count:', len(user['tweets'])
        print 'Friend IDs:', len(user['friend_ids'])
        print 'Follower IDs:', len(user['follower_ids'])
             
if __name__=="__main__":
   main()