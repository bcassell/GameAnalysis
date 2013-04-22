from argparse import ArgumentParser
import json
import numpy as np
from collections import OrderedDict

def _summarize(name, results, alpha=None):
    print 'Stdev:', name
    counter_true_true = 0
    counter_true_false = 0
    counter_true_undecided = 0
    counter_false_true = 0
    counter_false_false = 0
    counter_false_undecided = 0
    counter_false_undecided_true = 0
    counter_false_undecided_false = 0
    counter_true_undecided_true = 0
    counter_true_undecided_false = 0
    data = {x: [] for x in ["ff", "ft", "fu", "tf", "tt", "tu", "tut", "tuf", "fuf", "fut"]}
    for result in results:
        if result["game_eq"] is False:
            if result["stopping_decision"] == "No":
                data["ff"].append(result)
                counter_false_false += 1
            elif result["stopping_decision"] == "Yes":
                data["ft"].append(result)
                counter_false_true += 1
            elif result["stopping_decision"] == "Undetermined-Yes":
                data["fut"].append(result)
                counter_false_undecided_true += 1
            elif result["stopping_decision"] == "Undetermined-No":
                data["fuf"].append(result)
                counter_false_undecided_false += 1
            else:
                data["fu"].append(result)
                counter_false_undecided += 1
        elif result["stopping_decision"] == "No":
            data["tf"].append(result)
            counter_true_false += 1
        elif result["stopping_decision"] == "Yes":
            data["tt"].append(result)
            counter_true_true += 1
        elif result["stopping_decision"] == "Undetermined-Yes":
            data["tut"].append(result)
            counter_true_undecided_true += 1
        elif result["stopping_decision"] == "Undetermined-No":
            data["tuf"].append(result)
            counter_true_undecided_false += 1
        else:
            data["tu"].append(result)
            counter_true_undecided += 1
    if alpha is not None:
        binned_data = {}
        for x, results in data.items():
            binned_data[x] = { str(alpha/2): 0, str(alpha): 0, str(alpha+alpha/2): 0, str(2*alpha): 0, ('> '+str(2*alpha)): 0 }
            for result in results:
                if result['regret'] < alpha/2:
                    binned_data[x][str(alpha/2)] += 1
                elif result['regret'] < alpha:
                    binned_data[x][str(alpha)] += 1
                elif result['regret'] < 1.5*alpha:
                    binned_data[x][str(alpha+alpha/2)] += 1
                elif result['regret'] < 2*alpha:
                    binned_data[x][str(2*alpha)] += 1
                else:
                    binned_data[x][('> '+str(2*alpha))] += 1

    total_true = counter_true_true+counter_true_false+counter_true_undecided+counter_true_undecided_true+counter_true_undecided_false
    total_false = counter_false_true+counter_false_false+counter_false_undecided+counter_false_undecided_true+counter_false_undecided_false
    print 'Average sample count:', np.mean([result["sample_count"] for result in results])
    print 'Median sample count:', np.median([result["sample_count"] for result in results])
    print 'Average regret:', np.mean([result["regret"] for result in results])
    print 'Median regret:', np.median([result["regret"] for result in results])
    print '# eq examples: ', total_true, float(total_true)/(total_true+total_false)
    print '  Average sample count:', np.mean([result["sample_count"] for result in results if result["game_eq"] == True])
    print '  Median sample count:', np.median([result["sample_count"] for result in results if result["game_eq"] == True])
    print '  Average regret:', np.mean([result["regret"] for result in results if result["game_eq"] == True])
    print '  Median regret:', np.median([result["regret"] for result in results if result["game_eq"] == True])
    print '  Correctly labeled:', counter_true_true, float(counter_true_true)/total_true
    if alpha is not None:
        _bucket_regret('tt', binned_data)
    print '  Incorrectly labeled:', counter_true_false, float(counter_true_false)/total_true
    if alpha is not None:
        _bucket_regret('tf', binned_data)
    if counter_true_undecided > 0:
        print '  Undecided:', counter_true_undecided, float(counter_true_undecided)/total_true
        if alpha is not None:
            _bucket_regret('tu', binned_data)
    elif counter_true_undecided_true+counter_true_undecided_false > 0:
        print '  Undecided:', counter_true_undecided_true+counter_true_undecided_false, float(counter_true_undecided_true+counter_true_undecided_false)/total_true
        print '  U-Correctly labeled:', counter_true_undecided_true, float(counter_true_undecided_true)/(counter_true_undecided_true+counter_true_undecided_false)
        if alpha is not None:
            _bucket_regret('tut', binned_data)
        print '  U-Incorrectly labeled:', counter_true_undecided_false, float(counter_true_undecided_false)/(counter_true_undecided_true+counter_true_undecided_false)
        if alpha is not None:
            _bucket_regret('tuf', binned_data)
        print '  Total correctly labeled:', counter_true_true+counter_true_undecided_true, float(counter_true_true+counter_true_undecided_true)/total_true
        print '  Total incorrectly labeled:', counter_true_false+counter_true_undecided_false, float(counter_true_false+counter_true_undecided_false)/total_true
    print '# non-eq examples: ', total_false, float(total_false)/(total_true+total_false)
    print '  Average sample count:', np.mean([result["sample_count"] for result in results if result["game_eq"] == False])
    print '  Median sample count:', np.median([result["sample_count"] for result in results if result["game_eq"] == False])
    print '  Average regret:', np.mean([result["regret"] for result in results if result["game_eq"] == False])
    print '  Median regret:', np.median([result["regret"] for result in results if result["game_eq"] == False])
    print '  Correctly labeled:', counter_false_false, float(counter_false_false)/total_false
    if alpha is not None:
        _bucket_regret('ff', binned_data)
    print '  Incorrectly labeled:', counter_false_true, float(counter_false_true)/total_false
    if alpha is not None:
        _bucket_regret('ft', binned_data)
    if counter_false_undecided > 0:
        print '  Undecided:', counter_false_undecided, float(counter_false_undecided)/total_false
        if alpha is not None:
            _bucket_regret('fu', binned_data)
    elif counter_false_undecided_true+counter_false_undecided_false > 0:
        print '  Undecided:', counter_false_undecided_true+counter_false_undecided_false, float(counter_false_undecided_true+counter_false_undecided_false)/total_false
        print '  U-Correctly labeled:', counter_false_undecided_true, float(counter_false_undecided_true)/(counter_false_undecided_true+counter_false_undecided_false)
        if alpha is not None:
            _bucket_regret('fuf', binned_data)
        print '  U-Incorrectly labeled:', counter_false_undecided_false, float(counter_false_undecided_false)/(counter_false_undecided_true+counter_false_undecided_false)
        if alpha is not None:
            _bucket_regret('fut', binned_data)
        print '  Total correctly labeled:', counter_false_false+counter_false_undecided_false, float(counter_false_false+counter_false_undecided_false)/total_false
        print '  Total incorrectly labeled:', counter_false_true+counter_false_undecided_true, float(counter_false_true+counter_false_undecided_true)/total_false

def _bucket_regret(key, dict):
    if key == 'tt' or key == 'ff':
        extra = 'correctly labeled:'
    elif key == 'tf' or key == 'ft':
        extra = 'incorrectly labeled:'
    elif key == 'tut' or key == 'fuf':
        extra = 'stalled but correctly labeled:'
    elif key == 'tuf' or key == 'fut':
        extra = 'stalled and incorrectly labeled:'
    else:
        extra = 'stalled:'
    print 'Bucket regret for', extra
    for x, count in dict[key].items():
        print x, ':', count

def main():
    parser = ArgumentParser(description='Sequential CI Experiments')
    parser.add_argument('input_file', metavar='input_file', help='a json file to analyze')
    parser.add_argument("-alpha", type=float, help="alpha setting so that buckets can be made.")
    args = parser.parse_args()
    input = json.load(open(args.input_file))
    for key, results in input.items():
        _summarize(key, results, args.alpha)

if __name__ == "__main__":
    main()