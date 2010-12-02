#!/usr/bin/python
def replace_unknowns(text_file):
    f = open(text_file, 'r')
    lines = f.readlines()
    f.close()
    index = 0
    for line in lines:
        unknown_value = '-1'
        line = line.replace('?', unknown_value)
        lines[index] = line
        index += 1
    f = open(text_file, 'w')
    for line in lines:
        print line
        f.write(line)
    f.close()
    
if __name__=="__main__":
    replace_unknowns('twitterdata')