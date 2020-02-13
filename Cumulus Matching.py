#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 04 10:28:35 2020

@author: pierre.casco
"""

import pandas as pd
import datetime

# Import excel files
kn_ns_mapping = pd.read_excel('Knack to NS Team Mapping.xlsx',
                              sheet_name = 'Knack Data')

cumulus = pd.read_excel('Cumulus 2018 Data.xlsx')

backfill = pd.read_csv('backfill.csv')

#backfill = backfill.drop(columns = 'Internal ID', axis = 0)

ama = pd.read_csv('ama.csv')

# Merge cumulus data with the NS to Knack mapping
cumulus_merged = cumulus.merge(kn_ns_mapping, right_on='Agent Entity', 
                               left_on='Primary Agent Team', how = 'left')

# Identify matches and non matches
mismatches = cumulus_merged[cumulus_merged['Agent Entity'].isnull()]

matches = cumulus_merged[pd.notnull(cumulus_merged['Agent Entity'])]

matches = matches.reset_index()

# Change date format for match
matches['Close Date'] = matches['Close Date'].astype(str)

matches['Closed Date'] = ''

for i in range(0,(len(matches)-1)):
    matches['Closed Date'][i] = datetime.datetime.strptime(matches['Close Date'][i], '%Y-%m-%d').strftime('%m/%d/%Y').lstrip('0').replace(' 0','').replace('/0','/')


# Merge matches with NS data
matches_bf = matches.merge(backfill, 
                           right_on = ['Compass Listing Id'],
                           left_on = ['Closing: ID'], 
                           how = 'left')    
    
matches_bf2 = matches.merge(backfill, 
                           right_on = ['Compass Listing Id','Close Date'],
                           left_on = ['Closing: ID','Closed Date'], 
                           how = 'left')

# mm = mismatches
mm = matches_bf[matches_bf['Compass Team ID'].isnull()]


# Trim the compass listing ID to 15 chars on the backfill df
backfill['trimmed'] = ''

for i in range(0, (len(matches) - 1)):
    backfill['trimmed'][i] = backfill['Compass Listing Id'][i][0:15]


matches_bf_trim = mm.merge(backfill, 
                           right_on = ['trimmed'],
                           left_on = ['Closing: ID'], 
                           how = 'left')   

mm_trim = matches_bf_trim[matches_bf_trim['trimmed'].isnull()]

# m = matches, m_t = matches trimmed
m = matches_bf[pd.notnull(matches_bf['Compass Team ID'])]
m = m.reset_index()

m_t = matches_bf_trim[pd.notnull(matches_bf_trim['Compass Team ID_y'])]
m_t = m_t.reset_index()

# Compare the team ID's
compare = pd.DataFrame(columns = m.columns)
research = pd.DataFrame(columns = m.columns)

for i in range(0,(len(m)-1)):
    if m['Salesforce Team ID'][i] == m['Compass Team ID'][i]:
        compare.loc[i] = m.loc[i]
    else:
        research.loc[i] = m.loc[i]


compare_t = pd.DataFrame(columns = m_t.columns)
research_t = pd.DataFrame(columns = m_t.columns)

for i in range(0,(len(m_t)-1)):
    if m_t['Salesforce Team ID'][i] == m_t['Compass Team ID_y'][i]:
        compare_t.loc[i] = m_t.loc[i]
    else:
        research_t.loc[i] = m_t.loc[i]
        
# Combine the 2 research dataframes 
# Drop unnecessary columns
research_t = research_t.drop(columns = ['level_0', 'index','Compass Team ID_x', 'Close Date_y', 'Compass Listing Id_x', 'External ID_x','External ID_y', 'Internal ID_x'], axis = 0)

research = research.drop(columns = ['level_0', 'index'], axis = 0)

# Format for renaming columns
for i in range(0,(len(research_t.columns)-1)):
    print("'"+research_t.columns[i]+"'"+': '+"'"+research.columns[i]+"'"+',')

research_t = research_t.rename(columns = {'Closing: Closing Name': 'Closing: Closing Name',
'Transactions??': 'Transactions??',
'Closing: ID': 'Closing: ID',
'Close Date Copy': 'Close Date Copy',
'Final Contract Price': 'Final Contract Price',
'SideRepresented': 'SideRepresented',
'Type of Sale': 'Type of Sale',
'Gross Commissions to Compass': 'Gross Commissions to Compass',
'Compass $ From Split': 'Compass $ From Split',
'Compass Net Commission $': 'Compass Net Commission $',
'Primary Agent Team': 'Primary Agent Team',
'Primary Agent': 'Primary Agent',
'Primary Agent Final Commission': 'Primary Agent Final Commission',
'Secondary Agent': 'Secondary Agent',
'Secondary Agent Final Commission': 'Secondary Agent Final Commission',
'Close Date_x': 'Close Date_x',
'Status': 'Status',
'Salesforce Team ID': 'Salesforce Team ID',
'Agent Entity': 'Agent Entity',
'Closed Date': 'Closed Date',
'Internal ID_y': 'Internal ID',
'Compass Team ID_y': 'Compass Team ID',
'Close Date': 'Close Date_y',
'Compass Listing Id_y': 'Compass Listing Id'})

# Finally, combine dataframes
final = research.append(research_t, ignore_index = True, sort=False)

a = final.merge(ama, left_on = 'Salesforce Team ID',
            right_on = 'SalesForce Account ID',
            how = 'left')

a_mismatch = a[a['Name'].isnull()]

a_match = a[pd.notnull(a['Name'])]

# Export to csv
a_mismatch.to_csv('/Users/pierre.casco/helpscout/team_id_mismatches.csv')
a_match.to_csv('/Users/pierre.casco/helpscout/team_id_matches.csv')



# Find principals
word = 'Principal'

a_match['agent_type'] = ''

for i in range(0,(len(a_match)-1)):
    if word in a_match['Name'].loc[i]:
        a_match['agent_type'].loc[i] = 'Principal'
    else:
        a_match['agent_type'].loc[i] = 'Agent'


# Add a new column using the side a or side b in external id. Then, dont remove duplicates that have a side a and side b listed

a_match['side'] = ''

side_one = 'SideOne'
side_two = 'SideTwo'


try:
    for i in range(0, (len(a_match) - 1)):
        if side_one in a_match['External ID'].loc[i]:
            a_match['side'].loc[i] = 'Side One'
        elif side_two in a_match['External ID'].loc[i]:
            a_match['side'].loc[i] = 'Side Two'
except TypeError:
    pass


principals = a_match[a_match['agent_type'] == 'Principal']
principals = principals.drop_duplicates(subset = ['Internal ID'], 
                                        keep = 'first')
# Find missing internal ID's
list(set(a_match['Internal ID'].unique()).difference(list(principals['Internal ID'])))

principals = principals.append(a_match[a_match['Internal ID'] == 24200])
principals = principals.append(a_match[a_match['Internal ID'] == 139682])

principals.to_csv('/Users/pierre.casco/helpscout/team_id_matches_principals.csv')




