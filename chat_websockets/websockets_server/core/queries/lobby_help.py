import os
import glob

dir_path = os.path.dirname(os.path.realpath(__file__))
messages = []
pattern = os.path.join(dir_path, '*.txt')
files = sorted(glob.glob(pattern))
for file in files:

    with open(file, 'r') as fcont:
        message = fcont.read()
        messages.append(message)

if __name__ == '__main__':
    print(message)
