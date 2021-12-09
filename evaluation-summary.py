'''
This module parses results from  user evaluations of search relevance and
outputs a summary
'''
import argparse
import json


def average_precision(judgements: list):
    '''
    Helper function to calculate average precision based on a list of judgements

    Params
    -------
    - judgements: list[bool]
        A list of boolean relevance judgements

    Returns
    -------
    - averge_precision: float
    '''
    running_total = 0
    relevant_docs = 0
    for idx, judgement in enumerate(judgements):
        if judgement:
            relevant_docs += 1
            running_total += relevant_docs / (idx + 1)
    return running_total / 10


def main(relevance_file: str):
    '''
    This function reads in a JSON file of relevance judgements, computes
    average precisions, and returns results

    Params
    -------
    - relevance_file: str
        A file to load, containing relevance judgements

    Returns
    -------
    - precision_results: list[float]
        A list of average precision per query
    '''
    with open(relevance_file) as f:
        results = json.load(f)
    precision_results = []
    for result in results:
        judgements = [doc['relevant'] for doc in result['results']]
        precision_results.append(round(average_precision(judgements), 3))
    print(precision_results)
    return precision_results

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--relevance-file', type=str, default='relevance.json')
    args = parser.parse_args()
    main(args.relevance_file)
