import os

from argparse import ArgumentParser
import json

def parse_input():
    """
    Combines json files
    """
    parser = ArgumentParser()
    parser.add_argument("in_file", type=str, help="Input file or files.", nargs='+')
    parser.add_argument("-out_file", type=str, default='combined.json', help="Output file.")
    args = parser.parse_args()

    data = []
    for file in args.in_file:
        if os.path.isfile(file):
            with open(file) as f:
                data.extend(json.load(f))
        else:
            raise IOError("Input must be a file or directory.")
    return data, args

if __name__ == "__main__":
    data, args = parse_input()
    open(args.out_file, 'w').write(json.dump(data))
