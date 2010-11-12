#! /usr/bin/python
from time import sleep
from datetime import datetime
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=4)
from utils import write_output

def main():
    community = get_community('nuss08', write=True, \
      out_file="test3", write_dir="pickled_populations/")
    #pp.pprint(community)
    
def get_community(root_name, max_people=10, max_followers_per_person=2,\
   write=False, out_file="", write_dir=""):
    if write:
        if out_file:
            file_name = out_file
        elif not out_file:
            file_name = "pickled_" + str(datetime.now()).split()[0]
        
        if write_dir:
            write_path = "%s%s" % (write_dir, file_name)
        else:
            write_path = file_name
    else:
        write_path = None
    pop = Population(root_name, max_people, max_followers_per_person)
    pop.populate(write_path)
    community = pop.get_community(write_path)
    return community

if __name__=="__main__":
   main()