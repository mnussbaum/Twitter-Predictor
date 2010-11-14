#! /usr/bin/python
from time import sleep
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=4)
from datetime import datetime
from populate import Population
from stats import PopulationStats
from utils import write_output, read_output

def main():
    community = read_output('pickled_populations/test3')
    s = PopulationStats(community['members'])
    community_member_names = s.all_users()
    print 'Community Members:'
    pp.pprint(community_member_names)
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