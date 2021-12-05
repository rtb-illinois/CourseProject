import argparse

import bs4
import sqlite3


def main(db_file: str, output_filename: str):
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
