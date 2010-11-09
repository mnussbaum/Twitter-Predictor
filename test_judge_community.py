#! /usr/bin/python
from time import sleep
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=4)
from datetime import datetime
from populate import Population
from stats import PopulationStats
from utils import write_output, get_community, read_output

def main():
    community = read_output('pickled_populations/pickled_2010-11-06')
    s = PopulationStats(community)
    community_members = s.all_users()
    print 'Community Members:'
    pp.pprint(community_members)
    print '\nFollower list overlap (keys are user names, ' +\
      'values are a list their followers who occur on more' +\
      ' then one follower list in the community):'
    pp.pprint(s.relation_list_overlap('followers'))
    print '\nFriend list overlap (keys are user names, ' +\
      'values are a list their friends who occur on more' +\
      ' then one friend list in the community):'
    pp.pprint(s.relation_list_overlap('friends'))

if __name__=="__main__":
   main()