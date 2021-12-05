'''
Utility module for cleaning the the text data and metadata of Hearthstone cards.
'''
import argparse

import bs4
import sqlite3


def main(db_file: str, output_filename: str):
    '''
    This function reads a list of hearthstone cards from a Sqlite3 DB and then
    cleans the text data and metadata of those cards, saving a new file that is
    a line corpus of all the cards to be used by metapy

    Params
    -------
    - db_file: str
        The name of a SQLite DB file to connect to for fetching cards
    - output_filename: str
        The name of the output file that the cleaned card text should be
        written to as a line corpus

    Returns
    -------
    - None
    '''
    db_uri = f'file:{db_file}?mode=rw'
    db = sqlite3.connect(db_uri, uri=True)
    cursor = db.cursor()

    fetch_cards_statement = 'SELECT * FROM cards'
    db_cards = cursor.execute(fetch_cards_statement).fetchall()

    cards = {card[0]: ' '.join(card[1:]) for card in db_cards}
    cleaned_cards = [bs4.BeautifulSoup(card, "lxml").text for card in cards.values()]

    with open(output_filename, 'w') as f:
        for card in cleaned_cards:
            f.write(card + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db-file', required=True)
    parser.add_argument('--output-filename', required=True)
    args = parser.parse_args()
    main(args.db_file, args.output_filename)
