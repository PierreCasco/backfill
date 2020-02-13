#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 11:11:04 2020

@author: pierre.casco
"""

import pandas as pd
import os
import datetime


knack_extract = pd.read_csv(r'/Users/pierre.casco/backfill/Files/KnackExtract2018.csv', usecols = ['Address','Compass listing ID','Listing Type','Close date','Entity name','Represented?'])


# Import file

path = r'/Users/pierre.casco/backfill/Files/Imports'
os.chdir('/Users/pierre.casco/backfill/Files/Imports')
all_files = os.path.join(path, "*.csv")

a_f = []

for f in os.listdir():
    a_f.append(f)


li = []
i = 1

for f in a_f:
    df = pd.read_csv(f, usecols = ['External ID','Compass Listing ID','Close Date','Side Represented (Source)','Listing Type (Source)','Compass Team ID'])
    li.append(df)
    print(i,'-', f)
    i+=1
    
frame = pd.concat(li, axis = 0, ignore_index = True, sort = False)

frame['dummy_id'] = frame['Compass Listing ID'] + frame['Side Represented (Source)'] + frame['Close Date']


# Import other Knack file

os.chdir('/Users/pierre.casco/backfill/Files/Knack 2018')
more_files = []

for f in os.listdir():
    more_files.append(f)
    
mi = []
i = 1

for f in more_files:
    df = pd.read_excel(f, usecols = ['Address','Compass listing ID','Close date','Represented?','Listing Type','Entity name'])
    mi.append(df)
    print(i,'-', f)
    i+=1
    
df = pd.concat(mi, axis = 0, ignore_index = True, sort = False)


df['Close date'] = df['Close date'].astype('str')

for i in range(0,(len(df)-1)):
    df['Close date'][i] = datetime.datetime.strptime(df['Close date'][i], '%Y-%m-%d').strftime('%m/%d/%Y').lstrip('0').replace(' 0','').replace('/0','/')
    

# Merge knack data with the NS to Knack mapping
import open_files

open_knack_file = open_files.open_knack_file()
open_ama = open_files.open_ama_table()

knack_merged = knack_extract.merge(open_knack_file, 
                                   right_on='Agent Entity', 
                                   left_on='Entity name', 
                                   how = 'left')

# Identify matches and non matches
knack_mismatches = knack_merged[knack_merged['Entity name'].isnull()]

knack_matches = knack_merged[pd.notnull(knack_merged['Entity name'])]

knack_matches = knack_matches.reset_index()

# Remove represent from column

for i in range(0, (len(knack_matches)-1)):
    if pd.notnull(knack_matches['Represented?'][i]):
        knack_matches['Represented?'][i] = knack_matches['Represented?'][i].lstrip().replace('Represent ','')
    else:
        pass

knack_matches['Closed date'] = ''

for i in range(0, (len(knack_matches)-1)):
    knack_matches['Closed date'][i] = knack_matches['Close date'][i].lstrip('0').replace(' 0','').replace('/0','/')


knack_matches = knack_matches.fillna('')

knack_matches['dummy_id'] = ''

for i in range(0,(len(knack_matches)-1)):
    if len(knack_matches['Compass listing ID'][i]) >= 1:
        knack_matches['dummy_id'][i] = knack_matches['Compass listing ID'][i] +  knack_matches['Represented?'][i] + knack_matches['Closed date'][i]
    else:
        knack_matches['dummy_id'][i] = knack_matches['Address'][i]  + knack_matches['Represented?'][i] + knack_matches['Closed date'][i]



# kam = knack after match

kam = knack_matches.merge(frame, on = 'dummy_id', how = 'right')


kam_m = kam[pd.notnull(kam['Compass Listing ID'])]

kam_m = kam_m.reset_index(drop=True)

good = pd.DataFrame(columns = kam_m.columns)
research_k = pd.DataFrame(columns = kam_m.columns)

for i in range(0,(len(kam_m)-1)):
    if kam_m['Salesforce Team ID'][i] == kam_m['Compass Team ID'][i]:
        good.loc[i] = kam_m.loc[i]
    else:
        research_k.loc[i] = kam_m.loc[i]












