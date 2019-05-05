import glob2

filenames = glob2.glob('**/*.py')  # list of all .txt files in the directory

with open('all.txt', 'w') as f:
    for file in filenames:
        with open(file) as infile:
            f.write(infile.read() + '\n')
