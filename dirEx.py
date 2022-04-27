import os.path

from exDir import dirTest
from pathlib import Path

def main():
    with open('example',mode='r') as read:
        print(read.readlines())


if __name__ == "__main":
    main()