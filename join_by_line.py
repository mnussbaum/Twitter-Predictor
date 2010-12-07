#!/usr/bin/env python

# Takes two files, f1 and f2. For each line index i, prints f1[i] \t f2[i]
# Stops when the shorter file runs out of lines.

import sys
import getopt

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:g:o:h")
    except getopt.GetoptError:
        print "Invalid options. Valid options are -f FILE1 -f FILE2 -o OUTPATh -h"
        sys.exit(1)
    in1 = None
    in2 = None
    outpath = None
    head = False
    for o, a in opts:
        if o == '-f':
            in1 = a
        if o == '-g':
            in2 = a
        if o == '-o':
            outpath = a
        if o == '-h':
            head = True
    f1 = open(in1, 'r')
    f2 = open(in2, 'r')
    lines1 = f1.readlines()
    lines2 = f2.readlines()
    if head == True:
        lines1 = lines1[1:]
        lines2 = lines2[2:]
    f1.close()
    f2.close()
    outfile = open(outpath, 'w')
    L = min(len(lines1), len(lines2))
    for i in range(L):
        one = lines1[i].rstrip('\n')
        two = lines2[i]
        output = one + '\t' + two
        outfile.write(output)
        
if __name__ == "__main__":
    main()