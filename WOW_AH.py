import requests
from datetime import datetime
import pandas as pd

print( 'Generating Access Token ...' )

# Create a new Access Token
def create_access_token(client_id, client_secret, region = 'eu'):
    data = { 'grant_type': 'client_credentials' }
    response = requests.post('https://%s.battle.net/oauth/token' % region, data=data, auth=(client_id, client_secret))
    return response.json()

def get_kazzak(token):
    search = "https://eu.api.blizzard.com/data/wow/connected-realm/1305/auctions?namespace=dynamic-eu&locale=en_GB&access_token=" + token
    response = requests.get(search)
    return response.json()["auctions"]

def get_hellfire(token):
    search = "https://eu.api.blizzard.com/data/wow/connected-realm/1587/auctions?namespace=dynamic-eu&locale=en_GB&access_token=" + token
    response = requests.get(search)
    return response.json()["auctions"]

response = create_access_token('59cc7fe2d633479a8eabf7bfd61ec8aa', 'fq48ndwEJ6P7dLMxG7gTThGlYwIPVjmD')
token = response['access_token']

kazzak_auctions = get_kazzak(token)
hellfire_auctions = get_hellfire(token)
auction_df = pd.DataFrame( kazzak_auctions )
auction_df2 = pd.DataFrame( hellfire_auctions )

# Expand the item column
auction_df = auction_df.rename(columns={"id": "auction_id",})
auction_df2 = auction_df2.rename(columns={"id": "auction_id",})

auction_df = pd.concat([auction_df.drop(['item'], axis=1), auction_df['item'].apply(pd.Series)], axis=1)
auction_df2 = pd.concat([auction_df2.drop(['item'], axis=1), auction_df2['item'].apply(pd.Series)], axis=1)

# Drop 'bonus_list' and 'modifiers' 
#   These are subgroups of an equipable item with the bonus stats (intellect agility, strength, etc)
auction_df['collection_year'] = datetime.now().strftime('%Y')
auction_df['collection_month'] = datetime.now().strftime('%m')
auction_df['collection_day'] = datetime.now().strftime('%d')
auction_df['collection_hour'] = datetime.now().strftime('%H')

auction_df2['collection_year'] = datetime.now().strftime('%Y')
auction_df2['collection_month'] = datetime.now().strftime('%m')
auction_df2['collection_day'] = datetime.now().strftime('%d')
auction_df2['collection_hour'] = datetime.now().strftime('%H')

filename = datetime.now().strftime('Kazzak_EU-%Y-%m-%d-%H-%M.csv')
filename2 = datetime.now().strftime('Hellfire_EU-%Y-%m-%d-%H-%M.csv')
print( 'Exporting Data ...' )
auction_df.to_csv(filename, index=False)
auction_df2.to_csv(filename2, index=False)




