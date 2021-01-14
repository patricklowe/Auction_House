import pandas as pd
import numpy as np
import glob

# Read all auction files
path = r'C:\Users\patri\Desktop\Project_WOW\Data'

all_files = glob.glob(path + "/*.csv")

# Combine all files into one df
auction_df = pd.concat((pd.read_csv(f) for f in all_files))

auction_df = auction_df.sort_values(by=['auction_id','collection_day','collection_hour'])
auction_df['time_left'] = auction_df['time_left'].replace('SHORT','< 0.5 Hrs').replace('MEDIUM','0.5-2 Hrs').replace('LONG','2-12 Hrs').replace('VERY_LONG','12-48 Hrs')

# Unit_price are for stackable items, and buyout price is for non-stackable items. Let's combine into one cost source
auction_df['cost'] = (auction_df['unit_price'].fillna(0) + auction_df['buyout'].fillna(0)).astype(str)

# Converting cost into gold (100 silver), silver (100 copper) and copper pieces
auction_df['cost_gold'] = auction_df['cost'].astype(str).str[:-6]
auction_df['cost_silver'] = auction_df['cost'].astype(str).str[-6:-4]
auction_df['cost_copper'] = auction_df['cost'].astype(str).str[-4:-2]
auction_df['bid'] = auction_df['bid'].fillna(0)
auction_df['cost_gold'] = auction_df['cost_gold'].fillna(0)

# Convert Pet Breeds
auction_df['pet_breed_id'] = auction_df['pet_breed_id'].astype(str).replace('3.0','B/B').replace('13.0','B/B').replace('4.0','P/P').replace('14.0','P/P').replace('5.0','S/S').replace('15.0','S/S')
auction_df['pet_breed_id'] = auction_df['pet_breed_id'].astype(str).replace('6.0','H/H').replace('16.0','H/H')
auction_df['pet_breed_id'] = auction_df['pet_breed_id'].astype(str).replace('7.0','H/P').replace('17.0','H/P')
auction_df['pet_breed_id'] = auction_df['pet_breed_id'].astype(str).replace('8.0','P/S').replace('18.0','P/S')
auction_df['pet_breed_id'] = auction_df['pet_breed_id'].astype(str).replace('9.0','H/S').replace('19.0','H/S')
auction_df['pet_breed_id'] = auction_df['pet_breed_id'].astype(str).replace('10.0','P/B').replace('20.0','P/B')
auction_df['pet_breed_id'] = auction_df['pet_breed_id'].astype(str).replace('11.0','S/B').replace('21.0','S/B')
auction_df['pet_breed_id'] = auction_df['pet_breed_id'].astype(str).replace('12.0','H/B').replace('22.0','H/B')

# Hours & Days auction appeared in
days_appearing = auction_df.groupby(['auction_id'], as_index=False)['collection_day'].agg({'list':(lambda x: list(x))})
days_appearing = days_appearing.rename(columns={"list":'appearance_days'})
days_appearing['appearance_days'] = days_appearing['appearance_days'].map(np.unique)
#days_appearing['appearance_days'] = days_appearing['appearance_days'].apply(lambda x: list(set(x)))
auction_df = auction_df.merge(days_appearing, left_on='auction_id', right_on='auction_id')
hours_appearing = auction_df.groupby('auction_id', as_index=False)['collection_hour'].agg({'list':(lambda x: list(x))})
hours_appearing = hours_appearing.rename(columns={"list":'appearance_hours'})
auction_df = auction_df.merge(hours_appearing, left_on='auction_id', right_on='auction_id')
auction_df['posted_hour'] = auction_df['appearance_hours'].map(lambda x: x[0])
auction_df['posted_day'] = auction_df['appearance_days'].map(lambda x: x[0])
auction_df['finished_hour'] = auction_df['appearance_hours'].map(lambda x: x[-1])
auction_df['finished_day'] = auction_df['appearance_days'].map(lambda x: x[-1])
auction_df['posted'] = auction_df['posted_day'].astype(str) + "/" + auction_df['collection_month'].astype(str) + "/" + auction_df['collection_year'].astype(str) + " " + auction_df['posted_hour'].astype(str) + ":00"
auction_df['sold'] = auction_df['finished_day'].astype(str) + "/" + auction_df['collection_month'].astype(str) + "/" + auction_df['collection_year'].astype(str) + " " + auction_df['finished_hour'].astype(str) + ":00"
auction_df['posted'] = pd.to_datetime(auction_df['posted'], format='%d/%m/%Y %H:%M')
auction_df['sold'] = pd.to_datetime(auction_df['sold'], format='%d/%m/%Y %H:%M')
time_left_appearing = auction_df.groupby('auction_id', as_index=False)['time_left'].agg({'list':(lambda x: list(x))})
time_left_appearing = time_left_appearing.rename(columns={"list":'appearance_left'})
time_left_appearing['appearance_left'] = time_left_appearing['appearance_left'].map(np.unique)
auction_df = auction_df.merge(time_left_appearing, left_on='auction_id', right_on='auction_id')

result = auction_df[(auction_df['posted'] > '22/09/2020 23:00') & (auction_df['posted'] < '30/09/2020 01:00')]  
result = result.drop_duplicates(subset ="auction_id")
result['hrs_to_sell'] = (result['sold'] - result['posted']).astype('timedelta64[h]')
result['cost_gold'] = result['cost_gold'].fillna(0)
result = result[result['appearance_left'].apply(lambda x: '< 0.5 Hrs' not in x)]
#result.to_csv('sold_auctions.csv',index=False)

#DELETE
sold_bags = result[ result['id'] == 154695]
sold_ids = list(sold_bags['auction_id'])
unsold_bags = auction_df[ (auction_df['id'] == 154695) & ~(auction_df['auction_id'].isin(sold_ids))]
unsold_bags['item_sold'] = 'no'
sold_bags['item_sold'] = 'yes'

frames = [sold_bags, unsold_bags]
tester = pd.concat(frames)
tester.to_csv('deep_sea_bag.csv',index=False)