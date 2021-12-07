'''
Utility module for cleaning the the text data and metadata of Hearthstone cards.
'''
import argparse

import bs4
import pytoml
import sqlite3


def get_card_full_text(card: dict):
    card_text_elements = [card[key] for key in card.keys() if key != 'id']
    return ' '.join(card_text_elements)


def get_card_metadata(card: dict, metadata_config: list):
    card_metadata_elements = [str(card[metadata['name']]) for metadata in metadata_config]
    return '\t'.join(card_metadata_elements)


def main(db_file: str, config_file: str):
    '''
    This function reads a list of hearthstone cards from a Sqlite3 DB and then
    cleans the text data and metadata of those cards, saving a new file that is
    a line corpus of all the cards to be used by metapy, as well as a
    corresponding metadata file

    Params
    -------
    - db_file: str
        The name of a SQLite DB file to connect to for fetching cards
    - config_file: str
        The name of the config_file, which specifies the metadata format and
        the output directory

    Returns
    -------
    - None
    '''
    with open(config_file) as f:
        config = pytoml.load(f)

    db_uri = f'file:{db_file}?mode=rw'
    db = sqlite3.connect(db_uri, uri=True)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()

    fetch_cards_statement = 'SELECT * FROM cards'
    db_cards = cursor.execute(fetch_cards_statement).fetchall()

    card_texts = [get_card_full_text(card) for card in db_cards]
    cleaned_cards = [bs4.BeautifulSoup(card, "lxml").text for card in card_texts]

    output_name = config['dataset']
    corpus_name = config['corpus']
    corpus_file = f'{output_name}/{corpus_name}'
    with open(corpus_file) as f:
        corpus_config = pytoml.load(f)
    metadata_config = corpus_config['metadata']
    card_metadata = [get_card_metadata(card, metadata_config) for card in db_cards]

    data_filename = f'{output_name}/{output_name}.dat'
    metadata_filename = f'{output_name}/metadata.dat'
    with open(data_filename, 'w') as f:
        for card in cleaned_cards:
            f.write(card + '\n')
    with open(metadata_filename, 'w') as f:
        for card in card_metadata:
            f.write(card + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db-file', required=True)
    parser.add_argument('--config-file', required=True)
    args = parser.parse_args()
    main(args.db_file, args.config_file)
