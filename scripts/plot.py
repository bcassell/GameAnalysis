import os
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from argparse import ArgumentParser
import json

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
    pp = PdfPages(args.in_file.split(".json")[0]+"_scatter.pdf")
    plt.figure(args.in_file)
    plt.xlabel("Regret")
    plt.ylabel("Number of samples")
    colors = {"0.0": "b", "0.1": "k", "1.0": "r", "10.0": "b", "100.0": "w"}
    plt.xlim(-0.5, 30)
    plt.ylim(0, 1050)
    for label, data in distribution.items():
        x_points = []
        y_points = []
        for x in data:
            x_points.append(x["regret"])
            y_points.append(x["sample_count"])
        plt.scatter(x_points, y_points, c=colors[label], label=label)

    plt.legend(loc="upper right", prop={'size':6})
    pp.savefig()
    pp.close()

if __name__ == "__main__":
    data, args = parse_input()
    plot_distributions(data, args)

