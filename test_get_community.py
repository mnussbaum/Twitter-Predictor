#! /usr/bin/python
import logging
from time import sleep
from datetime import datetime
from pprint import PrettyPrinter
pp = PrettyPrinter(indent=4)
from utils import write_output
from populate import Population
from __init__ import LOG_FILENAME

logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG, 
  format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
  datefmt='%m-%d %H:%M')

def main():
    community = get_community(60919433, write=True,
      max_people=200, max_followers_per_person=5, out_file="lizardbill_11_20_2010",
      write_dir="pickled_populations/", new_community=False, safe_mode=False)
   

def get_community(root_id, max_people=10, max_followers_per_person=2,
   write=False, out_file="", write_dir="", new_community=True, safe_mode=False):
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
    pop = Population(root_id, max_people, max_followers_per_person,
      write_path, new=new_community, safe=safe_mode)
    try:
        pop.populate()
        community = pop.get_community()
	return community
    except Exception as error:
        logging.debug('Uncaught exception, quitting %s' % error)
        pop.save()
    
if __name__=="__main__":
   main()
