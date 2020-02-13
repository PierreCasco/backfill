#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 09:11:07 2020

@author: pierre.casco
"""
import pandas as pd
import os


def open_knack_file():
    os.chdir('/Users/pierre.casco/backfill/Files')
    kn_ns_mapping = pd.read_excel('Knack to NS Team Mapping.xlsx',
                              sheet_name = 'Knack Data')
    return(kn_ns_mapping)
    
def open_ama_table():
    os.chdir('/Users/pierre.casco/backfill/Files')
    ama = pd.read_csv('ama.csv')
    
    return(ama)