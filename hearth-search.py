'''
This module contains a simple flask app for search the hearthstone cards using
a metapy based information retrieval method
'''
import argparse
import os

from flask import Flask, g, request
from flask_restx import Api, Resource, reqparse
import metapy
import pytoml

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument("query_term", type=str, required=True)
parser.add_argument("num_docs", type=int, default=3)


def get_search_engine():
    '''
    This function fetches a "search engine" that is represented as a dictionary
    with a metapy index and a metapy ranker. The function uses the flask app
    context so that the ranker and index do not need to be rebuilt for
    subsequent requests

    Params
    -------
    - None

    Returns
    -------
    - search_engine: dict
        The metapy ranker and metapy index to be used for searching
    '''
    if 'search_engine' not in g:
        idx = metapy.index.make_inverted_index(os.environ['METAPY_CONFIG'])
        ranker = metapy.index.OkapiBM25()
        g.search_engine = {'idx': idx, 'ranker': ranker}
    return g.search_engine


def format_card_results(top_cards, idx):
    '''
    This functions formats the search results by utilizing the metapy index
    metadata associated with each document in the metapy index, returning a
    human readable result.

    Params
    -------
    - top_cards: list[tuple]
        A list of tuples of the top document results
    - idx: metapy.Index
        A metapy inverted index

    Returns
    -------
    - results: dict
        The formatted top card results
    '''
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


@api.route('/search')
class Search(Resource):
    '''
    The main search api route for the flask app
    '''

    @api.expect(parser)
    def get(self):
        '''
        This function is the main get method for the search api route.

        Params
        -------
        - None

        Returns
        -------
        - formatted_results: dict
            The formatted top card results, organized by their ranking returned
            by the search
        '''
        args = parser.parse_args()
        query = metapy.index.Document()
        query.content(args['query_term'])
        search_engine = get_search_engine()
        ranker = search_engine['ranker']
        idx = search_engine['idx']
        top_docs = ranker.score(idx, query, num_results=args['num_docs'])
        formatted_results = format_card_results(top_docs, idx)
        return formatted_results


if __name__ == '__main__':
    app.run()
