import argparse
import os

from flask import Flask, g
from flask_restx import Api, Resource
import metapy
import pytoml

app = Flask(__name__)
api = Api(app)


def get_search_engine():
    if 'search_engine' not in g:
        idx = metapy.index.make_inverted_index(os.environ['METAPY_CONFIG'])
        ranker = metapy.index.OkapiBM25()
        g.search_engine = {'idx': idx, 'ranker': ranker}
    return g.search_engine


def format_card_results(top_cards, idx):
    results = {}
    for index, card in enumerate(top_cards):
        doc_id = card[0]
        doc_metadata = idx.metadata(doc_id)
        card_data = {'name': doc_metadata.get('name'),
                     'body': doc_metadata.get('body'),
                     'id': doc_metadata.get('id'),
                     'slug': doc_metadata.get('slug'),
                     'image': doc_metadata.get('image')}
        results[index] = card_data
    return results


@api.route('/search/<string:query_term>')
class Search(Resource):
    def get(self, query_term):
        query = metapy.index.Document()
        query.content(query_term)
        search_engine = get_search_engine()
        ranker = search_engine['ranker']
        idx = search_engine['idx']
        top_docs = ranker.score(idx, query, num_results=3)
        formatted_results = format_card_results(top_docs, idx)
        return formatted_results


if __name__ == '__main__':
    app.run()
