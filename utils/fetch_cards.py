'''
Utility module for downloading all of the current Hearthstone cards.
'''
import argparse
import json
import requests
from requests.auth import HTTPBasicAuth


def main(oauth_client_id: str, oauth_client_secret: str):
    '''
    This function will fetch all current hearthstone cards using pagination that
    is built in to the Blizzard Hearthstone API.

    Params
    -------
    - oauth_client_id: str
        The OAuth Client ID for authentication with the Blizzard API
    - oauth_client_secret: str
        The OAuth Client secret for authentication with the Blizzard API

    Returns
    -------
    - hearthstone_cards: list
        A list of all Hearthstone cards and their metadata
    '''
    oauth_response = requests.post('https://us.battle.net/oauth/token',
                                   data={'grant_type': 'client_credentials'},
                                   auth=HTTPBasicAuth(oauth_client_id,
                                                      oauth_client_secret))
    oauth_json = json.loads(oauth_response.text)
    oauth_token = oauth_json['access_token']

    card_uri = 'https://us.api.blizzard.com/hearthstone/cards'
    headers = {'Authorization': f'Bearer {oauth_token}'}
    params = {'locale': 'en_US', 'pageSize': 100}
    card_response = requests.get(card_uri, headers=headers, params=params)
    card_json = json.loads(card_response.text)
    page_count = card_json['pageCount']

    hearthstone_cards = []
    for page_num in range(1, page_count + 1):
        params.update({'page': page_num})
        page_response = requests.get(card_uri, headers=headers, params=params)
        page_json = json.loads(page_response.text)
        hearthstone_cards += page_json['cards']

    metadata_uri = 'https://us.api.blizzard.com/hearthstone/metadata'
    metadata_params = {'locale': 'en_US'}
    metadata_response = requests.get(metadata_uri, headers=headers,
                                     params=metadata_params)
    metadata_json = json.loads(metadata_response.text)
    classes = {classs['id']: classs['name'] for classs in metadata_json['classes']}
    spell_schools = {school['id']: school['name'] for school in metadata_json['spellSchools']}
    minion_types = {mtype['id']: mtype['name'] for mtype in metadata_json['minionTypes']}

    for card in hearthstone_cards:
        card['class'] = classes.get(card.get('classId', ''), '')
        card['spellschool'] = spell_schools.get(card.get('spellSchoolId', ''), '')
        card['miniontype'] = minion_types.get(card.get('minionTypeId', ''), '')

    return hearthstone_cards

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--oauth-client-id', required=True)
    parser.add_argument('--oauth-client-secret', required=True)
    args = parser.parse_args()
    main(args.oauth_client_id, args.oauth_client_secret)
