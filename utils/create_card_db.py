'''
Utility module for creating a sqlite DB of the current Hearthstone cards.
'''
import argparse
import json
import sqlite3

import utils.fetch_cards as fc


def main(db_file: str, oauth_client_id: str, oauth_client_secret: str,
         existing_db: bool = False):
    '''
    This function creates a new DB or connects to an existing DB and populates
    it with hearthstone cards.

    Params
    -------
    - db_file: str
        The name of a SQLite DB file to create or connect to
    - oauth_client_id: str
        The OAuth Client ID for authentication with the Blizzard API
    - oauth_client_secret: str
        The OAuth Client secret for authentication with the Blizzard API
    - existing_db: bool
        A flag indicating whether to use an existing DB. If true, this function
        will raise an exception if the DB does not already exist.

    Returns
    -------
    - None
    '''
    cards = fc.main(oauth_client_id, oauth_client_secret)

    db_mode = 'rwc' if not existing_db else 'rw'
    db_uri = f'file:{db_file}?mode={db_mode}'
    db = sqlite3.connect(db_uri, uri=True)
    cursor = db.cursor()

    create_table_statement = ('CREATE TABLE IF NOT EXISTS cards (id INT '
                              'PRIMARY KEY, slug TEXT, name TEXT, body TEXT, '
                              'hidden TEXT, image TEXT, class TEXT, '
                              'spellschool TEXT, miniontype TEXT)')
    cursor.execute(create_table_statement)

    insert_statement = ('INSERT INTO cards VALUES (?,?,?,?,?,?,?,?,?) ON CONFLICT(id) '
                        'DO UPDATE SET slug=excluded.slug, name=excluded.name, '
                        'body=excluded.body, hidden=excluded.hidden, '
                        'image=excluded.image, class=excluded.class, '
                        'spellschool=excluded.spellschool, '
                        'miniontype=excluded.miniontype')
    for card in cards:
        card_row_info = (card['id'], card['slug'], card['name'], card['text'],
                         card['flavorText'], card['image'], card['class'],
                         card['spellschool'], card['miniontype'])
        cursor.execute(insert_statement, card_row_info)

    db.commit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db-file', required=True)
    parser.add_argument('--oauth-client-id', required=True)
    parser.add_argument('--oauth-client-secret', required=True)
    parser.add_argument('--existing-db', action='store_true', default=False)
    args = parser.parse_args()
    main(args.db_file, args.oauth_client_id, args.oauth_client_secret,
         args.existing_db)
