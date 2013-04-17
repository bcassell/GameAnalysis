from argparse import ArgumentParser
import json
import numpy as np

def _summarize(name, results):
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
    data = {x: [] for x in ["ff", "ft", "fu", "tf", "tt", "tu"]}
    for result in results:
        if result["game_eq"] is False:
            if result["stopping_decision"] == "No":
                counter_false_false += 1
            elif result["stopping_decision"] == "Yes":
                counter_false_true += 1
            elif result["stopping_decision"] == "Undetermined-Yes":
                counter_false_undecided_true += 1
            elif result["stopping_decision"] == "Undetermined-No":
                counter_false_undecided_false += 1
            else:
                counter_false_undecided += 1
        elif result["stopping_decision"] == "No":
            counter_true_false += 1
        elif result["stopping_decision"] == "Yes":
            counter_true_true += 1
        elif result["stopping_decision"] == "Undetermined-Yes":
            counter_true_undecided_true += 1
        elif result["stopping_decision"] == "Undetermined-No":
            counter_true_undecided_false += 1
        else:
            counter_true_undecided += 1
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
    print '  Incorrectly labeled:', counter_true_false, float(counter_true_false)/total_true
    if counter_true_undecided > 0:
        print '  Undecided:', counter_true_undecided, float(counter_true_undecided)/total_true
    else:
        print '  Undecided:', counter_true_undecided_true+counter_true_undecided_false, float(counter_true_undecided_true+counter_true_undecided_false)/total_true
        print '  U-Correctly labeled:', counter_true_undecided_true, float(counter_true_undecided_true)/(counter_true_undecided_true+counter_true_undecided_false)
        print '  U-Incorrectly labeled:', counter_true_undecided_false, float(counter_true_undecided_false)/(counter_true_undecided_true+counter_true_undecided_false)
        print '  Total correctly labeled:', counter_true_true+counter_true_undecided_true, float(counter_true_true+counter_true_undecided_true)/total_true
        print '  Total incorrectly labeled:', counter_true_false+counter_true_undecided_false, float(counter_true_false+counter_true_undecided_false)/total_true
    print '# non-eq examples: ', total_false, float(total_false)/(total_true+total_false)
    print '  Average sample count:', np.mean([result["sample_count"] for result in results if result["game_eq"] == False])
    print '  Median sample count:', np.median([result["sample_count"] for result in results if result["game_eq"] == False])
    print '  Average regret:', np.mean([result["regret"] for result in results if result["game_eq"] == False])
    print '  Median regret:', np.median([result["regret"] for result in results if result["game_eq"] == False])
    print '  Correctly labeled:', counter_false_false, float(counter_false_false)/total_false
    print '  Incorrectly labeled:', counter_false_true, float(counter_false_true)/total_false
    if counter_false_undecided > 0:
        print '  Undecided:', counter_false_undecided, float(counter_false_undecided)/total_false
    else:
        print '  Undecided:', counter_false_undecided_true+counter_false_undecided_false, float(counter_false_undecided_true+counter_false_undecided_false)/total_false
        print '  U-Correctly labeled:', counter_false_undecided_true, float(counter_false_undecided_true)/(counter_false_undecided_true+counter_false_undecided_false)
        print '  U-Incorrectly labeled:', counter_false_undecided_false, float(counter_false_undecided_false)/(counter_false_undecided_true+counter_false_undecided_false)
        print '  Total correctly labeled:', counter_false_false+counter_false_undecided_false, float(counter_false_false+counter_false_undecided_false)/total_false
        print '  Total incorrectly labeled:', counter_false_true+counter_false_undecided_true, float(counter_false_true+counter_false_undecided_true)/total_false

def main():
    parser = ArgumentParser(description='Sequential CI Experiments')
    parser.add_argument('input_file', metavar='input_file', help='a json file to analyze')
    args = parser.parse_args()
    input = json.load(open(args.input_file))
    for key, results in input.items():
        _summarize(key, results)

if __name__ == "__main__":
    main()