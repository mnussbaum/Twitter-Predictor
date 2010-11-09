#! /usr/bin/python
from time import sleep
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=4)
from datetime import datetime
from populate import Population
from stats import Stats
from utils import write_output, get_community, read_output

def main():
    community = read_output(\
      '/Users/michaelnussbaum08/Documents/College/Junior_Year/Quarter_1/Machine_Learning/group_project/code/pickled_2010-11-08')
    s = Stats(community)
    community_members = s.all_users()
    pp.pprint(community_members)
    pp.pprint(s.relation_list_overlap('followers'))
    pp.pprint(s.relation_list_overlap('friends'))

if __name__=="__main__":
   main()