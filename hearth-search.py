import argparse
import os

from flask import Flask, g
from flask_restx import Api, Resource
import metapy
import pytoml

app = Flask(__name__)
api = Api(app)


def get_config():
    if 'config' not in g:
        with open(os.environ['METAPY_CONFIG']) as f:
            g.config = pytoml.load(f)
    return g.config


def get_cards():
    if 'cards' not in g:
        config = get_config()
        card_dataset = config['dataset']
        card_file = f'{card_dataset}/{card_dataset}.dat'
        with open(card_file) as f:
            g.cards = f.readlines()
    return g.cards


def get_search_engine():
    if 'search_engine' not in g:
        idx = metapy.index.make_inverted_index('config.toml')
        ranker = metapy.index.OkapiBM25()
        g.search_engine = {'idx': idx, 'ranker': ranker}
    return g.search_engine


@api.route('/search/<string:query_term>')
class Search(Resource):
    def get(self, query_term):
        query = metapy.index.Document()
        query.content(query_term)
        search_engine = get_search_engine()
        ranker = search_engine['ranker']
        idx = search_engine['idx']
        top_docs = ranker.score(idx, query, num_results=3)

        print(f'Query: "{query_term}"')
        cards = get_cards()
        top_cards = {doc[0]: cards[doc[0]] for doc in top_docs}
        print(f'Result: {top_cards}')
        return top_cards


if __name__ == '__main__':
    app.run()
