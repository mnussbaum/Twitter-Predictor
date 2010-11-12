import pickle
from datetime import datetime
from populate import Population

def write_output(data, out_file):
    f = open(out_file, 'w')
    pickle.dump(data, f)
    f.close()
    print 'written'

def read_output(out_file):
    try:
        f = open(out_file, 'r')
        existing_records = pickle.load(f)
        f.close()
    except IOError:
        existing_records = {} 
    return existing_records

def get_community(root_name, max_people=10, max_followers_per_person=2,\
   write=False, out_file="", write_dir=""):
    if write:
        if out_file:
            file_name = out_file
        elif not out_file:
            file_name = "pickled_" + str(datetime.now()).split()[0]
        
        if write_dir:
            write_path = "%s%s" % (write_dir, file_name))
        else:
            write_path = file_name
    else:
        write_path = None
    pop = Population(root_name, max_people, max_followers_per_person)
    pop.populate(write_path)
    community = pop.get_community(write_path)
    return community