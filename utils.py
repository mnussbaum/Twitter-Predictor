import pickle
from datetime import datetime

def write_output(data, out_file):
    f = open(out_file, 'w')
    pickle.dump(data, f)
    f.close()
    print 'written'
    

def read_output(out_file):
    print out_file
    try:
        f = open(out_file, 'r')
        existing_records = pickle.load(f)
        f.close()
    except IOError:
        print 'IO ERROR'
        return
    return existing_records