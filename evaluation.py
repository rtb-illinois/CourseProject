'''
This module executes an evaluation for a given user. Each user is able to input
any number of queries, which will return results and are judged by the user
'''
import argparse
import json

import metapy


def yes_no_input():
    '''
    Simple function to get a yes or no boolean response from a user

    Params
    -------
    -  None

    Returns
    -------
    - response: bool
    '''
    response = str(input('Is this document relevant? (y/N) ')).lower().strip()
    print('\n')
    if response == 'y':
        return True
    else:
        return False


def main(config_file: str, num_queries: int, num_docs: int, output_file: str):
    '''
    This function prompts users for queries, returns search results, and then
    prompts users for relevance judgements, storing them to a file.

    Params
    -------
    - config_file: str
        The name of a config file for building the search engine
    - num_queries: int
        The number of queries a user should enter
    - num_docs: int
        The number of results to fetch for each query
    - output_file: str
        The file to store relevance judgements to

    Returns
    -------
    - None
    '''
    relevance_results = []
    for _ in range(num_queries):
        query_term = str(input('Enter query term: ')).lower().strip()
        print('\n')
        relevance_result = {'query': query_term, 'results': []}
        idx = metapy.index.make_inverted_index('config.toml')
        ranker = metapy.index.OkapiBM25()
        query = metapy.index.Document()
        query.content(query_term)
        top_docs = ranker.score(idx, query, num_results=num_docs)

        results = {}
        for index, card in enumerate(top_docs):
            doc_id = card[0]
            doc_metadata = idx.metadata(doc_id)
            card_data = {'name': doc_metadata.get('name'),
                         'body': doc_metadata.get('body'),
                         'id': doc_metadata.get('id'),
                         'slug': doc_metadata.get('slug'),
                         'image': doc_metadata.get('image')}
            results[index] = card_data

        for result in results.values():
            print(json.dumps(result, indent=2), '\n')
            is_relevant = yes_no_input()
            result['relevant'] = is_relevant
            relevance_result['results'].append(result)
        relevance_results.append(relevance_result)

    with open(output_file, 'w+') as f:
        json.dump(relevance_results, f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config-file', default='config.toml')
    parser.add_argument('--num-queries', type=int, default=3)
    parser.add_argument('--num-docs', type=int, default=3)
    parser.add_argument('--output-file', type=str, default='relevance.json')
    args = parser.parse_args()
    main(args.config_file, args.num_queries, args.num_docs, args.output_file)
