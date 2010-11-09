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

def get_community(root_name, max_people=10, max_followers_per_person=2, write=False, write_dir=""):
    pop = Population(root_name, max_people, max_followers_per_person)
    pop.populate()
    community = pop.get_community()
    if write:
        file_stamp = "pickled_" + str(datetime.now()).split()[0]
        if write_dir:
            write_output(community, "%s%s" % (write_dir, file_stamp))
        else:
            write_output(community, file_stamp)
    return community