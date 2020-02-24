import os

dir_path = os.path.dirname(os.path.realpath(__file__))

file = os.path.join(dir_path, 'lobby_help.txt')

with open(file, 'r') as fcont:
    message = fcont.read()

if __name__ == '__main__':
    print(message)

