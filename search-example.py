'''
This module contains an example of searching through available Hearthstone
cards according to information retrieval search engine methods.
'''
import argparse

import metapy
import pytoml


def main(config_file: str, query_term: str):
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

    Returns
    -------
    - None
    '''
    idx = metapy.index.make_inverted_index('config.toml')
    ranker = metapy.index.OkapiBM25()
    query = metapy.index.Document()
    query.content(query_term)
    top_docs = ranker.score(idx, query, num_results=3)

    with open(config_file) as f:
        config = pytoml.load(f)

    card_dataset = config['dataset']
    card_file = f'{card_dataset}/{card_dataset}.dat'
    with open(card_file) as f:
        cards = f.readlines()

    print(f'Query: "{query_term}"')
    top_cards = [cards[doc[0]] for doc in top_docs]
    for index, card in enumerate(top_cards):
        print(f'Result {index}: {card.strip()}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config-file', default='config.toml')
    parser.add_argument('--query-term', required=True)
    args = parser.parse_args()
    main(args.config_file, args.query_term)
