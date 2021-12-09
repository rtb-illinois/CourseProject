'''
This module contains an example of searching through available Hearthstone
cards according to information retrieval search engine methods.
'''
import argparse
import json

import metapy
import pytoml


def main(config_file: str, query_term: str, num_docs: int):
    '''
    This function builds a search engine for hearthstone cards with an inverted
    index based on the config file provided, then uses the provided query term
    to perform a search for a few top results.

    Params
    -------
    - config_file: str
        The name of a config file for building the search engine
    - query_term: str
        A query term to search with
    - num_docs: int
        The number of results to fetch

    Returns
    -------
    - None
    '''
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
    print(json.dumps(results, indent=4))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config-file', default='config.toml')
    parser.add_argument('--query-term', required=True)
    parser.add_argument('--num-docs', type=int, default=3)
    args = parser.parse_args()
    main(args.config_file, args.query_term, args.num_docs)
