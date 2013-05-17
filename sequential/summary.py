from argparse import ArgumentParser
import json
import numpy as np
import collections

def _summarize(data):
    odict = _organize(data)
    for key, value in odict.items():
        print key
        regret = [x["statistic"] for x in value]
        sample_count = [x["sample_count"] for x in value]
        print "Mean Regret:", np.mean(regret)
        print "Median Regret:", np.median(regret)
        print "95% Regret:", sorted(regret)[int(len(regret)*0.95)-1]
        print "Average Sample Count:", np.mean(sample_count)
        print "Median Sample Count:", np.median(sample_count)
    
def _organize(data):
    rdict = collections.defaultdict(list)
    for entry in data:
        for key, value in entry.items():
            rdict[key].extend(value["0"])
    return rdict
    
def main():
    parser = ArgumentParser(description='Sequential Bootstrap Experiments')
    parser.add_argument('input_file', metavar='input_file', help='a json file to analyze')
    args = parser.parse_args()
    data = json.load(open(args.input_file))
    _summarize(data)

if __name__ == "__main__":
    main()