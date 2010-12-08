#!/usr/bin/env python

# Takes two files, f1 and f2. For each line index i, prints f1[i] \t f2[i]
# Stops when the shorter file runs out of lines.
# Use -h flag to ignore first line headers.
# Use -s flag to unscale SVM output back to real frequencies.

import sys
import getopt
import math

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:g:o:hs")
    except getopt.GetoptError:
        print "Invalid options. Valid options are -f FILE1" + \
          "-g FILE2 -o OUTPATH -h -s"
        sys.exit(1)
    in1 = None
    in2 = None
    outpath = None
    head = False
    scale = False
    for o, a in opts:
        if o == '-f':
            in1 = a
        if o == '-g':
            in2 = a
        if o == '-o':
            outpath = a
        if o == '-h':
            head = True
        if o == '-s':
            scale = True
    f1 = open(in1, 'r')
    f2 = open(in2, 'r')
    lines1 = f1.readlines()
    lines2 = f2.readlines()
    if head == True:
        lines1 = lines1[1:]
        lines2 = lines2[1:]
    f1.close()
    f2.close()
    outfile = open(outpath, 'w')
    L = min(len(lines1), len(lines2))
    for i in range(L):
        one = lines1[i].rstrip('\n')
        two = lines2[i]
        if scale == True:
            two = str(unscale(eval(two))) + '\n'
        output = one + '\t' + two
        outfile.write(output)

def unscale(y):
    if y <= -1:
        return 0
    if y >= 1:
        return 1000
    else:
        x = (y + 1) * 0.5
        return -1.0 / math.log(x)

if __name__ == "__main__":
    main()
