import sys

def main(file_path):
    f = open(file_path, 'r')
    lines = f.readlines()
    f.close()
    lines_within_bounds = []
    for line in lines:
        split_line = line.split()
        if float(split_line[-1]) < 1000:
            lines_within_bounds.append(line)
    #take ever 100th line
    desired_output = []
    line_counter = 0
    for line in lines_within_bounds:
       if line_counter % 100 == 0:
           desired_output.append(line)
       line_counter += 1
    f = open(file_path, 'w')
    f.write(''.join(desired_output))
    f.close()

if __name__ == "__main__":
    main(sys.argv[1])
