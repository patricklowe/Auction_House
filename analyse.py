import pandas as pd
import requests
import plotly.graph_objects as go
import plotly.io as pio
#pio.renderers.default = 'svg'
pio.renderers.default = 'browser'

def create_access_token(client_id, client_secret, region = 'eu'):
    data = { 'grant_type': 'client_credentials' }
    response = requests.post('https://%s.battle.net/oauth/token' % region, data=data, auth=(client_id, client_secret))
    return response.json()

# Load sold data
df = pd.read_csv('sold_auctions.csv')


df['cost_gold'] = pd.to_numeric( df['cost_gold'].fillna(0) )
df['cost_gold'] = df['cost_gold'].astype(str).replace('','0')
df['cost_gold'] = pd.to_numeric( df['cost_gold'] )
# Create a token to access API
response = create_access_token('YOUR_ID', 'YOUR_SECRET')
token = response['access_token']

# Item Data
print( 'Processing Top Sold Items... ' )
most_sold_items  = df[ df['id'] != 82800]
most_sold_items = most_sold_items.groupby(by=['id']).agg({'auction_id':'count', 'cost_gold': 'min', 'hrs_to_sell':'mean'}).reset_index().sort_values(by='auction_id',ascending=False)
most_sold_items.columns = ['item_id','count','cost_gold','selltime']
most_sold_items = most_sold_items[ most_sold_items['cost_gold'] > 0].head(50)
get_ids = most_sold_items['item_id'].astype(int)
item_names = []

print( 'Collecting Item Data ...' )
for item_id in get_ids:
    search = "https://us.api.blizzard.com/data/wow/item/" + str(item_id) + "?namespace=static-us&locale=en_US&access_token=" + token
    response = str( requests.get(search).json()["name"])
    item_names.append( response )
most_sold_items['name'] = item_names

fig = go.Figure([go.Bar(
    x=most_sold_items['name'], 
    y=most_sold_items['cost_gold'],
    text=most_sold_items['count'],
    marker={'color': most_sold_items['selltime'],'colorscale': 'Portland', 'showscale':True, 'reversescale':True},
    textposition='auto',
)])
fig.update_layout(
    title="Most Sold Items",
    xaxis_title="Item Name",
    yaxis_title="Common Sell Price",
)
fig.update_xaxes(showline=True, linewidth=2, linecolor='black', gridcolor='grey')
fig.update_yaxes(showline=True, linewidth=2, linecolor='black', gridcolor='gray')
fig.show()

# Pet Data
print( 'Processing Top Sold Pets... ' )
pets = df[df['id'] == 82800]
most_sold_pets = pets.groupby(by=['pet_species_id']).agg({'auction_id':'count', 'cost_gold': 'min', 'hrs_to_sell':'mean'}).reset_index().sort_values(by='auction_id',ascending=False).head(50)
most_sold_pets.columns = ['pet_id','count','cost_gold','selltime']
pet_ids = most_sold_pets['pet_id'].astype(int)
pet_names = []

print( 'Collecting Pet Data ...' )
for item_id in pet_ids:
    search = "https://us.api.blizzard.com/data/wow/pet/" + str(item_id) + "?namespace=static-us&locale=en_US&access_token=" + token
    response = str( requests.get(search).json()["name"])
    pet_names.append( response )
most_sold_pets['name'] = pet_names

fig = go.Figure([go.Bar(
    x=most_sold_pets['name'], 
    y=most_sold_pets['cost_gold'],
    text=most_sold_pets['count'],
    marker={'color': most_sold_pets['selltime'],'colorscale': 'Portland', 'showscale':True, 'reversescale':True},
    textposition='auto',
    )])
fig.update_layout(
#    template="plotly_dark",
    title="Most Sold Pets",
    xaxis_title="Pet Name",
    yaxis_title="Avg Sell Price",
)
fig.update_xaxes(showline=True, linewidth=2, linecolor='black', gridcolor='grey')
fig.update_yaxes(showline=True, linewidth=2, linecolor='black', gridcolor='gray')
fig.show()

# Graph profitable items
profitable_items = df.groupby(by=['id']).agg({'auction_id':'count', 'hrs_to_sell': 'mean', 'cost_gold': lambda x: pd.Series.mode(x)[0]}).reset_index().sort_values(by='auction_id',ascending=False)
profitable_items.columns = ['item_id','count','selltime','cost_gold']
profitable_items = profitable_items[ profitable_items['count'] > 1]
profitable_items = profitable_items[profitable_items['item_id'] != 82800]
profitable_items['income'] = profitable_items['count'] * profitable_items['cost_gold']
profitable_items = profitable_items.sort_values(by='selltime',ascending=True).head(50)

sold_ids = profitable_items['item_id'].astype(int)
item_names = []
print( 'Collecting Item Data ...' )
for item_id in sold_ids :
    search = "https://us.api.blizzard.com/data/wow/item/" + str(item_id) + "?namespace=static-us&locale=en_US&access_token=" + token
    response = str( requests.get(search).json()["name"])
    item_names.append( response )
profitable_items['name'] = item_names

fig = go.Figure(data=[go.Bar(
    x=profitable_items['name'], 
    y=profitable_items['cost_gold'],
    text=profitable_items['count'],
    marker={'color': profitable_items['selltime'],'colorscale': 'Portland', 'showscale':True, 'reversescale':True},
    textposition='auto',
        )])
fig.update_layout(
    yaxis=dict(range=[0, 7500]),
#    template="plotly_dark",
    margin=dict(l=20, r=20, t=100, b=400),
    title="Most profitable Items",
    xaxis_title="Item",
    yaxis_title="Common Sell Price",
)
fig.update_xaxes(showline=True, linewidth=2, linecolor='black', gridcolor='grey')
fig.update_yaxes(showline=True, linewidth=2, linecolor='black', gridcolor='gray')
fig.show()

# Graph profitable pets
profitable_pets = df[df['id'] == 82800]
profitable_pets = profitable_pets.groupby(by=['pet_species_id']).agg({'auction_id':'count','hrs_to_sell':'mean', 'cost_gold': 'mean'}).reset_index().sort_values(by='auction_id',ascending=False)
profitable_pets.columns = ['pet_id','count','selltime','cost_gold']
profitable_pets['income'] = profitable_pets['count'] * profitable_pets['cost_gold']
profitable_pets = profitable_pets.sort_values(by=['selltime'], ascending=[True]).head(50)

pet_ids = profitable_pets['pet_id'].astype(int)
pet_names = []
print( 'Collecting Pet Data ...' )
for item_id in pet_ids:
    search = "https://us.api.blizzard.com/data/wow/pet/" + str(item_id) + "?namespace=static-us&locale=en_US&access_token=" + token
    response = str( requests.get(search).json()["name"])
    pet_names.append( response )
profitable_pets['name'] = pet_names

fig = go.Figure(data=[go.Bar(
    x=profitable_pets['name'], 
    y=profitable_pets['cost_gold'],
    text=profitable_pets['count'],
    marker={'color': profitable_pets['selltime'],'colorscale': 'Portland', 'showscale':True, 'reversescale':True},
    textposition='auto',
        )])
fig.update_layout(
    yaxis=dict(range=[0, 160000]),
    #template="plotly_dark",
    margin=dict(l=20, r=20, t=100, b=400),
    title="Most profitable Pets",
    xaxis_title="Item",
    yaxis_title="Common Sell Price",
)
fig.update_xaxes(showline=True, linewidth=2, linecolor='black', gridcolor='grey')
fig.update_yaxes(showline=True, linewidth=2, linecolor='black', gridcolor='gray')
fig.show()

# Consumables
consumables = [174352,174350,174349,174348,174351,160053,163223,163222,163224,
               163225,168489,168498,168499,168500,152639,152638,152640,152641,
               168651,168652,168653,168654]
consumable_items = df[df['id'].isin(consumables)]
consumable_items = consumable_items.groupby(by=['id']).agg({'auction_id':'count','hrs_to_sell':'mean', 'cost_gold': lambda x: pd.Series.mode(x)[0]}).reset_index().sort_values(by='auction_id',ascending=False)
consumable_items.columns = ['item_id','count','selltime','cost_gold']

consumable_ids = consumable_items['item_id'].astype(int)
item_name = []
print( 'Collecting Item Data ...' )
for item_id in consumable_ids :
    search = "https://us.api.blizzard.com/data/wow/item/" + str(item_id) + "?namespace=static-us&locale=en_US&access_token=" + token
    response = str( requests.get(search).json()["name"])
    item_name.append( response )
consumable_items['name'] = item_name

fig = go.Figure(data=[go.Bar(
    x=consumable_items['name'], 
    y=consumable_items['cost_gold'],
    text=consumable_items['count'],
    marker={'color': consumable_items['selltime'],'colorscale': 'Portland', 'showscale':True, 'reversescale':True},
    textposition='auto',
        )])
fig.update_layout(
    yaxis=dict(range=[0, 170]),
    #template="plotly_dark",
    margin=dict(l=20, r=20, t=100, b=400),
    title="Consumable Items",
    xaxis_title="Item",
    yaxis_title="Common Sell Price",
)
fig.update_xaxes(showline=True, linewidth=2, linecolor='black', gridcolor='grey')
fig.update_yaxes(showline=True, linewidth=2, linecolor='black', gridcolor='gray')
fig.show()



