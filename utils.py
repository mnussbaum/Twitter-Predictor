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
    
def parse_twitter_timestamp(twitter_timestamp):
    split_timestamp = twitter_timestamp.split()
    month_dict = {"Jan":1, "Feb":2, "Mar":3, "Apr":4, "May":5, \
      "Jun":6, "Jul":7, "Aug":8, "Sep":9, "Oct":10, "Nov":11, \
      "Dec":12}
    year = int(split_timestamp[5])
    month = int(month_dict[split_timestamp[1]])
    day = int(split_timestamp[2])
    return datetime(year, month, day)