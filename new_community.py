#! /usr/bin/python
from time import sleep
from datetime import datetime
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=4)
from utils import get_community, write_output

def main():
    community = get_community('nuss08', write=True)
    pp.pprint(community)
            
if __name__=="__main__":
   main()