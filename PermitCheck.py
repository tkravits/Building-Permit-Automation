import pandas as pd
import pyodbc
import numpy as np
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from openpyxl import Workbook
import glob
import csv

# sets the display so that when the code prints, it is readable
pd.set_option('display.max_rows', 1500)
pd.set_option('display.max_columns', 50)
pd.set_option('display.width', 1500)

# imports the permit sheet to be cleaned up
print('Opening file window...\n')
Tk().withdraw()  # this prevents root tkinter window from appearing
filename = askopenfilename(filetypes=[('Excel', ('*.xls', '*.xlsx')), ('CSV', ('*.csv'))])  # this opens a window to choose out excel sheet
try:
    df = pd.read_excel(filename)  # assign df to the chosen
except:
    df = pd.read_csv(filename, sep=",", error_bad_lines=False, index_col=False, encoding='ISO-8859-1')
# print status
print('Data loading...\n')

# removes Information permits in both the Permit Type and Work Class fields, also removes any parcel number that starts
# with BLK, INT, or null. These are usually involved in right-of-ways and are not needed for valuation
# Also drops permits with no parcel number or address, usually right-of-way permits


# The City changed some columns, the below if/elif blocks rename these to work with our code.
# This can be continually updated with new elif statements as needed.
# Structuring the script this way means it's still able to run old permit files as well as new ones.

if 'Parcel Number' in df:
    pass  # if already named Parcel Number, do nothing
elif 'PIN' in df:
    df = df.rename(columns={'PIN': 'Parcel Number'})  # else if named pin, rename it

if 'Address' in df:
    pass
elif 'OriginalAddress' in df:
    df = df.rename(columns={'OriginalAddress': 'Address'})

if 'Status' in df:
    pass
elif 'StatusCurrent' in df:
    df = df.rename(columns={'StatusCurrent': 'Status'})

if 'Work Class' in df:
    pass
elif 'PermitWorkType' in df:
    df = df.rename(columns={'PermitWorkType': 'Work Class'})

if 'Permit Type' in df:
    pass
elif 'PermitType' in df:
    df = df.rename(columns={'PermitType': 'Permit Type'})

if 'Finaled Date' in df:
    pass
elif 'CompletedDate' in df:
    df = df.rename(columns={'CompletedDate': 'Finaled Date'})

if 'Issued Date' in df:
    pass
elif 'IssuedDate' in df:
    df = df.rename(columns={'IssuedDate': 'Issued Date'})

if 'Permit Number' in df:
    pass
elif 'PermitNum' in df:
    df = df.rename(columns={'PermitNum': 'Permit Number'})

if 'Parent Permit Number' in df:
    pass
elif 'MasterPermitNum' in df:
    df = df.rename(columns={'MasterPermitNum': 'Parent Permit Number'})

# remove if starts with
df = df.dropna(how='all')
df = df[~df['Parcel Number'].str.contains('BLK', na=False)]
df = df[~df['Parcel Number'].str.contains('INT', na=False)]
# remove missing values
df.dropna(subset=['Parcel Number', 'Address'])
df_review = df[df['Status'].str.contains('In Review', na=False)]
df = df[~df['Work Class'].str.contains('Information', na=False)]
df = df[~df['Work Class'].str.contains('Temporary Event', na=False)]

# removes Pending, Void, In Review, Withdrawn, Approved for permits in the Status. We only want permits that
# either have been issued or are already completed since permit value and other areas can change.
df = df[~df['Status'].str.contains('Pending', na=False)]
df = df[~df['Status'].str.contains('Void', na=False)]
df = df[~df['Status'].str.contains('In Review', na=False)]
df = df[~df['Status'].str.contains('Withdrawn', na=False)]
df = df[~df['Status'].str.contains('Approved for', na=False)]

# sets the parcel column type to a string
df['Parcel Number'] = df['Parcel Number'].astype('str')

# establishes a connection to the permit database
# TODO - update the connection string before implementation
#  --better to keep it separate? easier access?
print('Establishing connection...\n')

c_str = open('connection_string.txt', 'r').read()  # can be removed once connection string is added
cnxn = pyodbc.connect(c_str)

sql2 = '''SELECT distinct permit_num FROM r_prod.dbo.permit WHERE permit.agency_id = 'BLD' '''

print('Querying database...\n')

df_permit = pd.read_sql(sql2, cnxn)

df_permit.rename(columns={'permit_num': 'Permit Number'}, inplace=True)

df_uploaded = pd.merge(df, df_permit, on='Permit Number')

# compares permits that are in CAMA vs ones that aren't, merges df and drops ones that are already in CAMA
df_not_up = df.loc[~df['Permit Number'].isin(df_uploaded['Permit Number'])]
df_not_up.drop_duplicates()

print('\n\n----- df_not_up -----\n')
print(df_not_up.head)

#df_not_up.to_excel("Permits_Not_Uploaded.xlsx", index=False)
