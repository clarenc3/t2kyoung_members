#!/usr/bin/env python

# Clarence Wret, July 24 2024

import pandas as pd
import datetime

df = pd.read_csv('t2kyoung.csv')
# Convert the time to datetime
df['Member since']=pd.to_datetime(df['Member since'], format='%Y-%m-%d')
#df.info()

#df_postdoc = df[df['Position'] == 'Postdoc']
#print(df_postdoc)

#df_phd = df[df['Position'] == 'Student PhD']
#print(df_phd)

#df_msc = df[df['Position'] == 'Student MSc']
#print(df_msc)

mask=(df['Member since'] > '2010-1-1') & (df['Member since'] <= '2018-1-1') & (df['Position'] == 'Postdoc')
df = df.loc[mask]
print(df)

