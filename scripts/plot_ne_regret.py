import os
import numpy as np
from BasicFunctions import flatten

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from argparse import ArgumentParser
import json
import math

def parse_input():
    """
    Sets stdout and parses json files from input argument.

    If input is a directory, this function applies a filter to find files in 
    that directory containing a specified substring, then parses all of them.

    This function always returns a list of json-objects (dicts or lists), 
    followed by the args Namespaces, which contains bucket width, output file,
    and mode information.
    """
    parser = ArgumentParser()
    parser.add_argument("in_file", type=str, help="Input file or files.")
    args = parser.parse_args()

    data = None
    if os.path.isfile(args.in_file):
        with open(args.in_file) as f:
            data = json.load(f)
    else:
        raise IOError("Input must be a file.")
    return data, args

def plot_distributions(distribution, args):
    pp = PdfPages(args.in_file.split(".json")[0]+"_ne_scatter.pdf")
    plt.figure(args.in_file)
    plt.xlabel("NE-Regret")
    plt.ylabel("Number of samples")
    colors = {"0.0": "b", "0.1": "k", "1.0": "r", "10.0": "b", "100.0": "y"}
    plt.xlim(-0.5, 100)
    plt.ylim(0, 1000)
    keys = [float(k) for k in distribution.keys()]
    keys.sort()
    keys.reverse()
    for key in keys:
        label = str(key)
        data = distribution[label]
        x_points = []
        y_points = []
        for x in data:
            if x["sample_count"] > 5 and x["sample_count"] < 1000:
                ne_regrets = [e for e in flatten(x["ne-regrets"]) if e > 0.1]
                if len(ne_regrets) > 0:
                    x_points.append(min(ne_regrets))
                else:
                    x_points.append(max(flatten(x["ne-regrets"])))
                y_points.append(-np.log(x["sample_count"]))
        f = np.poly1d(np.polyfit(x_points, y_points, 1))
        x_grid = np.arange(0, 100, 0.1)
        plt.plot(x_grid, [math.exp(-f(x)) for x in x_grid], c=colors[label], label=label)

    plt.legend(loc="upper right", prop={'size':6})
    pp.savefig()
    pp.close()

if __name__ == "__main__":
    data, args = parse_input()
    plot_distributions(data, args)

