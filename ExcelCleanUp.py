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

# set the time for exported excel spreadsheets
CurrentDate = pd.Timestamp.today()
SetDate = (CurrentDate - pd.DateOffset(months=1)).strftime("%B%Y")

# imports the permit sheet to be cleaned up
print('Opening file window...\n')
Tk().withdraw()  # this prevents root tkinter window from appearing
filename = askopenfilename(filetypes=[('Excel', ('*.xls', '*.xlsx'))])  # this opens a window to choose out excel sheet
df = pd.read_excel(filename)  # assign df to the chosen file
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
df = df[~df['Parcel Number'].str.contains('BLK', na=False)]
df = df[~df['Parcel Number'].str.contains('INT', na=False)]
# remove missing values
df.dropna(subset=['Parcel Number', 'Address'])
df_review = df[df['Status'].str.contains('In Review')]
df = df[~df['Work Class'].str.contains('Information')]
df = df[~df['Work Class'].str.contains('Temporary Event')]

# these are the permits that are in review (aren't uploaded to cama)
df_review.to_excel("Permits_In_Review_" + SetDate + '.xlsx')

# removes Pending, Void, In Review, Withdrawn, Approved for permits in the Status. We only want permits that
# either have been issued or are already completed since permit value and other areas can change.
df = df[~df['Status'].str.contains('Pending')]
df = df[~df['Status'].str.contains('Void')]
df = df[~df['Status'].str.contains('In Review')]
df = df[~df['Status'].str.contains('Withdrawn')]
df = df[~df['Status'].str.contains('Approved for')]

# removes *, ", and carriage returns
df['Description'].replace(regex=True, inplace=True, to_replace=r'\*', value=r'')
df['Description'].replace(regex=True, inplace=True, to_replace=r'\n', value=r'')
df['Description'].replace(regex=True, inplace=True, to_replace=r'\r', value=r'')
df['Description'].replace(regex=True, inplace=True, to_replace=r'\*', value=r'')

# creates a column named Value Total, sets it to 0, and sums values that the City divides up into different categories
df['Value Total'] = '0'

# only sum the columns if needed (old version), else use the field from the new version
if 'EstProjectCost' in df:
    df['Value Total'] = df['EstProjectCost']
else:
    df['Value Total'] = df.iloc[:, 14:29].sum(axis=1)
    cols = [1, 9, 12, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]

    # removes the different valuation category columns the City provides
    df.drop(df.columns[cols], axis=1, inplace=True)
    calc_value = df['Calculated Valuation']
    updated_calc = df['Value Total'] == 0
    df.loc[updated_calc, 'Value Total'] = calc_value
    df.drop(df.columns[10], axis=1, inplace=True)


df['Value Total'] = df['Value Total'].fillna(0)
df['Description'] = df['Description'].fillna('No Description')
df['Value Total'] = df['Value Total'].astype('int')
df['SCOPE'] = 'N/A'

# The SCOPE column is what CAMA uses to classify each permit with a unique ID (ex. RRR is residential roofing), this is
# taking key words from either the Work Class column or the Description column and assigning a specific three letter
# code to be used in the upload process. This is also set up so that if a description can be found multiple times it is
# overwritten by more important codes (ie: OTH is lower, and remodels (REM) are more important and therefore listed
# towards the end of these)


df.loc[df['Work Class'].str.contains('Temporary', case=False), 'SCOPE'] = 'ELM'
df.loc[df['Work Class'].str.contains('Construction', case=False), 'SCOPE'] = 'OTH'
df.loc[df['Description'].str.contains('RTU', case=False), 'SCOPE'] = 'HTG'
df.loc[df['Description'].str.contains('RTUs', case=False), 'SCOPE'] = 'HTG'
df.loc[df['Work Class'].str.contains('Mechanical'), 'SCOPE'] = 'ELM'
df.loc[df['Work Class'].str.contains('Electrical', case=False), 'SCOPE'] = 'ELM'
df.loc[df['Work Class'].str.contains('Grading'), 'SCOPE'] = 'OTH'
df.loc[df['Work Class'].str.contains('Groundwater'), 'SCOPE'] = 'OTH'
df.loc[df['Work Class'].str.contains('Erosion'), 'SCOPE'] = 'OTH'
df.loc[df['Work Class'].str.contains('Roofing'), 'SCOPE'] = 'RRR'
df.loc[df['Description'].str.contains('heat', case=False), 'SCOPE'] = 'OTH'
df.loc[df['Work Class'].str.contains('Non-Public'), 'SCOPE'] = 'OTH'
df.loc[df['Work Class'].str.contains('Public'), 'SCOPE'] = 'OTH'
df.loc[df['Description'].str.contains('boiler', case=False), 'SCOPE'] = 'OTH'
df.loc[df['Description'].str.contains('ductless', case=False), 'SCOPE'] = 'HTG'
df.loc[df['Description'].str.contains('furnace', case=False), 'SCOPE'] = 'HTG'
df.loc[df['Description'].str.contains('heater', case=False), 'SCOPE'] = 'OTH'
df.loc[df['Description'].str.contains('PV', case=False), 'SCOPE'] = 'ENR'
df.loc[df['Description'].str.contains('solar', case=False), 'SCOPE'] = 'ENR'
df.loc[df['Description'].str.contains('photo', case=False), 'SCOPE'] = 'ENR'
df.loc[df['Description'].str.contains('P.V.', case=False), 'SCOPE'] = 'ENR'
df.loc[df['Description'].str.contains('photovoltaic', case=False), 'SCOPE'] = 'ENR'
df.loc[df['Description'].str.contains('geotherm', case=False), 'SCOPE'] = 'ENR'
df.loc[df['Description'].str.contains('flush-mounted', case=False), 'SCOPE'] = 'ENR'
df.loc[(df['Work Class'].str.contains('Mechanical')) & (
    df['Description'].str.contains('gas fireplace', case=False)), 'SCOPE'] = 'GFP'
df.loc[(df['Work Class'].str.contains('Mechanical')) & (
    df['Description'].str.contains('existing wood-burning', case=False)), 'SCOPE'] = 'GFP'
df.loc[(df['Work Class'].str.contains('Mechanical')) & (
    df['Description'].str.contains('wood burning', case=False)
    & (df['Description'].str.contains('replace', case=False))), 'SCOPE'] = 'GFP'
df.loc[df['Work Class'].str.contains('Repair'), 'SCOPE'] = 'GRP'
df.loc[(df['Work Class'].str.contains('Repair')) & (
    df['Description'].str.contains('foundation', case=False)), 'SCOPE'] = 'SRP'
df.loc[(df['Work Class'].str.contains('Repair')) & (
    df['Description'].str.contains('structural', case=False)), 'SCOPE'] = 'SRP'
df.loc[
    (df['Work Class'].str.contains('Repair')) & (df['Description'].str.contains('fire', case=False)), 'SCOPE'] = 'FRP'
df.loc[(df['Work Class'].str.contains('Mechanical HVAC')) & (
    df['Description'].str.contains('gas fireplace', case=False)), 'SCOPE'] = 'GFP'
df.loc[(df['Work Class'].str.contains('Mechanical HVAC')) & (
    df['Description'].str.contains('mini-split', case=False)), 'SCOPE'] = 'AIR'
df.loc[(df['Work Class'].str.contains('Mechanical HVAC')) & (
    df['Description'].str.contains('mini split', case=False)), 'SCOPE'] = 'AIR'
df.loc[(df['Work Class'].str.contains('Mechanical HVAC')) & (
    df['Description'].str.contains('condenser', case=False)), 'SCOPE'] = 'AIR'
df.loc[(df['Work Class'].str.contains('Mechanical HVAC')) & (
    df['Description'].str.contains('air condition', case=False)), 'SCOPE'] = 'AIR'
df.loc[(df['Work Class'].str.contains('Mechanical HVAC')) & (
    df['Description'].str.contains('a/c', case=False)), 'SCOPE'] = 'AIR'
df.loc[(df['Work Class'].str.contains('Mechanical HVAC')) & (
    df['Description'].str.contains(' ac ', case=False)), 'SCOPE'] = 'AIR'
df.loc[(df['Work Class'].str.contains('Mechanical HVAC')) & (
    df['Description'].str.contains(' ac', case=False)), 'SCOPE'] = 'AIR'
df.loc[(df['Work Class'].str.contains('Mechanical HVAC')) & (
    df['Description'].str.contains(' a/c ', case=False)), 'SCOPE'] = 'AIR'
df.loc[df['Work Class'].str.contains('Mechanical Sub-'), 'SCOPE'] = 'ELM'
df.loc[df['Work Class'].str.contains('Plumbing'), 'SCOPE'] = 'ELM'
df.loc[df['Work Class'].str.contains('Electrical Sub-'), 'SCOPE'] = 'ELM'
df.loc[df['Work Class'].str.contains('Utility'), 'SCOPE'] = 'OTH'
df.loc[df['Work Class'].str.contains('Siding'), 'SCOPE'] = 'SDG'
df.loc[df['Work Class'].str.contains('Right'), 'SCOPE'] = 'OTH'
df.loc[(df['Work Class'].str.contains('Right')) & (
    df['Description'].str.contains('sewer', case=False)), 'SCOPE'] = 'RWSRPR'
df.loc[df['Work Class'].str.contains('Fence'), 'SCOPE'] = 'FEN'
df.loc[df['Work Class'].str.contains('Tenant'), 'SCOPE'] = 'TFN'
df.loc[df['Work Class'].str.contains('Remodel'), 'SCOPE'] = 'REM'
df.loc[(df['Work Class'].str.contains('Remodel')) & (
    df['Description'].str.contains('finished basement', case=False)), 'SCOPE'] = 'BFN'
df.loc[(df['Work Class'].str.contains('Remodel')) & (
    df['Description'].str.contains('basement finish', case=False)), 'SCOPE'] = 'BFN'
df.loc[(df['Work Class'].str.contains('Remodel')) & (
    df['Description'].str.contains('basement remodel', case=False)), 'SCOPE'] = 'BFN'
df.loc[(df['Work Class'].str.contains('Remodel')) & (
    df['Description'].str.contains('bathroom remodel', case=False)), 'SCOPE'] = 'BTH'
df.loc[(df['Work Class'].str.contains('Remodel')) & (
    df['Description'].str.contains('bath remodel', case=False)), 'SCOPE'] = 'BTH'
df.loc[(df['Work Class'].str.contains('Remodel')) & (
    df['Description'].str.contains('tenant', case=False)), 'SCOPE'] = 'TFN'
df.loc[df['Work Class'].str.contains('New'), 'SCOPE'] = 'NEW'
df.loc[(df['Work Class'].str.contains('New')) & (
    df['Description'].str.contains('garage built', case=False)), 'SCOPE'] = 'GAR'
df.loc[df['Work Class'].str.contains('Addition'), 'SCOPE'] = 'ADD'
df.loc[(df['Work Class'].str.contains('Addition')) & (
    df['Description'].str.contains(' deck', case=False)), 'SCOPE'] = 'DEC'
df.loc[(df['Work Class'].str.contains('Addition')) & (
    df['Description'].str.contains('new porch', case=False)), 'SCOPE'] = 'POR'
df.loc[(df['Work Class'].str.contains('Addition')) & (
    df['Description'].str.contains('pergola', case=False)), 'SCOPE'] = 'POR'
df.loc[(df['Work Class'].str.contains('Addition')) & (
    df['Description'].str.contains(' shed', case=False)), 'SCOPE'] = 'OUT'
df.loc[df['Work Class'].str.contains('Addition and'), 'SCOPE'] = 'ADD'
df.loc[df['Work Class'].str.contains('Wireless'), 'SCOPE'] = 'OTH'
df.loc[df['Work Class'].str.contains('Demo'), 'SCOPE'] = 'DEM'
df.loc[df['Work Class'].str.contains('Sign'), 'SCOPE'] = 'SGN'
df.loc[df['Work Class'].str.contains('Fire'), 'SCOPE'] = 'SPK'
df.loc[(df['Permit Type'].str.contains('Mobile Home')) & (
    df['Description'].str.contains('replacement', case=False)), 'SCOPE'] = 'MHN'
df.loc[(df['Permit Type'].str.contains('Mobile Home')) & (
    df['Description'].str.contains('new', case=False)), 'SCOPE'] = 'MHN'
df.loc[
    (df['Work Class'].str.contains('Roofing')) & (df['Description'].str.contains('roof', case=False)), 'SCOPE'] = 'RRR'
df.loc[(df['Work Class'].str.contains('Roofing')) & (
    df['Description'].str.contains('single', case=False)), 'SCOPE'] = 'RRR'
df.loc[
    (df['Work Class'].str.contains('Roofing')) & (df['Description'].str.contains('SFD', case=False)), 'SCOPE'] = 'RRR'
df.loc[(df['Work Class'].str.contains('Roofing')) & (
    df['Description'].str.contains('residential', case=False)), 'SCOPE'] = 'RRR'
df.loc[
    (df['Work Class'].str.contains('Roofing')) & (df['Description'].str.contains('multi', case=False)), 'SCOPE'] = 'RRR'
df.loc[(df['Work Class'].str.contains('Roofing')) & (
    df['Description'].str.contains('duplex', case=False)), 'SCOPE'] = 'RRR'
df.loc[(df['Work Class'].str.contains('Roofing')) & (
    df['Description'].str.contains('re-roof', case=False)), 'SCOPE'] = 'RRR'
df.loc[(df['Work Class'].str.contains('Roofing')) & (
    df['Description'].str.contains('re roof', case=False)), 'SCOPE'] = 'RRR'
df.loc[(df['Work Class'].str.contains('Roofing')) & (
    df['Description'].str.contains('shingle', case=False)), 'SCOPE'] = 'RRR'
df.loc[(df['Work Class'].str.contains('Roofing')) & (
    df['Description'].str.contains('commercial', case=False)), 'SCOPE'] = 'CRR'

# creates an Excel file based on blank parcel fields, this is done as an edit check for the COB permit process just to
# make sure that there's nothing we're missing. Unfortunately, these will most likely need to be manually entered into
# CAMA, especially if they have some sort of larger value

df_blank = df[df['Parcel Number'].isna()]
# df_blank.to_excel("Permits_w_no_parcel_num_" + SetDate + '.xlsx')

# sets the parcel column type to a string
df['Parcel Number'] = df['Parcel Number'].astype('str')

# attempting to turn the date field to remove the time component (hours, minutes, sec)
df['Finaled Date'] = pd.to_datetime(df['Finaled Date'], format='%Y%m%d', errors='coerce')
pd.to_datetime(df['Issued Date'], format='%Y%m%d', errors='ignore')

# establishes a connection to the permit database
# TODO - update the connection string before implementation
#  --better to keep it separate? easier access?
print('Establishing connection...\n')
c_str = open('connection_string.txt', 'r').read()  # can be removed once connection string is added
cnxn = pyodbc.connect(c_str)  # add connection string here

# various SQLs that select from the database
sql = '''SELECT TOP 200000 parcel.strap, parcel.status_cd, parcel.dor_cd, parcel.nh_cd FROM r_prod.dbo.parcel
WHERE (parcel.dor_cd <> 'POSS') AND parcel.status_cd = 'A' '''

sql1 = '''SELECT TOP 200000 folio, strap FROM r_prod.dbo.strap_idx'''

sql2 = '''SELECT TOP 100000 permit_num FROM r_prod.dbo.permit WHERE permit.agency_id = 'BLD' '''

sql3 = '''SELECT TOP 200000 site.strap, site.str_num, site.str_pfx, site.str, site.str_sfx, site.str_sfx_dir,
site.str_unit FROM r_prod.dbo.site WHERE (site.city IN ('BOULDER', 'UNINCORPORATED'))'''

sql4 = '''SELECT parcel.map_id, parcel.nh_cd, parcel.dor_cd, parcel.strap FROM r_prod.dbo.parcel'''

print('Querying database...\n')
df_active_acct = pd.read_sql(sql, cnxn)
df_folio = pd.read_sql(sql1, cnxn)
df_permit = pd.read_sql(sql2, cnxn)
df_address = pd.read_sql(sql3, cnxn)
df_spread_for_app = pd.read_sql(sql4, cnxn)

# Takes the permit database, renames the column to Permit Number, and then merges the month's permit with permits found
# in the database, this makes sure a permit is not double uploaded, or double valuing

df_permit.rename(columns={'permit_num': 'Permit Number'}, inplace=True)
df_folio.rename(columns={'folio': "Parcel Number"}, inplace=True)

df1_1 = pd.merge(df, df_permit, on='Permit Number')
df.set_index('Permit Number', inplace=False)
df1_1.set_index('Permit Number', inplace=False)

# compares permits that are in CAMA vs ones that aren't, merges df and drops ones that are already in CAMA
df_not_up = df.loc[~df['Permit Number'].isin(df1_1['Permit Number'])]
df_not_up.drop_duplicates()

print('\n\n----- df_not_up -----\n')
print(df_not_up.head(2))
# print preview


# make one df that merges active accounts with the address associated with them
df_active_addr = pd.merge(df_active_acct, df_address, on='strap')
print('\n\n----- df_active_addr -----\n')
print(df_active_addr.head(2))
# print preview

# attempting to take situs address, concat, and compare with the Boulder permit address (only using active accts, no
# possessory interest)

df_active_addr.dropna(subset=['str_num'])
df_active_addr['str_num'] = df_active_addr['str_num'].astype(int).astype(str)
df_active_addr['str_pfx'] = df_active_addr['str_pfx'].fillna(np.nan).replace(np.nan, ' ', regex=True)
df_active_addr['str_pfx'] = df_active_addr['str_pfx'].replace('  ', ' ', regex=True)
df_active_addr['str_pfx'] = df_active_addr['str_pfx'].replace('S', ' S', regex=True)
df_active_addr['str_pfx'] = df_active_addr['str_pfx'].replace('N', ' N', regex=True)
df_active_addr['str_pfx'] = df_active_addr['str_pfx'].replace('E', ' E', regex=True)
df_active_addr['str_pfx'] = df_active_addr['str_pfx'].replace('W', ' W', regex=True)
df_active_addr['str_sfx'] = df_active_addr['str_sfx'].fillna(np.nan).replace(np.nan, ' ', regex=True)
df_active_addr['str_sfx'] = df_active_addr['str_sfx'].replace('  ', '', regex=True)
df_active_addr['str_sfx_dir'] = df_active_addr['str_sfx_dir'].fillna(np.nan).replace(np.nan, ' ', regex=True)
df_active_addr['str_sfx_dir'] = df_active_addr['str_sfx_dir'].replace('  ', ' ', regex=True)
df_active_addr['str_unit'] = df_active_addr['str_unit'].fillna(np.nan).replace(np.nan, '', regex=True)

# creates a column called Address that is set up in the same format as the Boulder permits table
df_active_addr['Address'] = df_active_addr['str_num'] + df_active_addr['str_pfx'] + df_active_addr['str'] + \
                            ' ' + df_active_addr['str_sfx'] + df_active_addr['str_sfx_dir'] + df_active_addr['str_unit']
df_active_addr['Address'] = df_active_addr['Address'].str.rstrip()

# merges the Boulder accounts database (strap) with the created Address field with the monthly COB permit spreadsheet
df_permit_addr = df.merge(df_active_addr.drop_duplicates('Address'), how='left', on='Address')

# takes the unmerged addresses and makes a spreadsheet to be checked by hand
df_permit_addr_nostrap = df_permit_addr.loc[df_permit_addr['strap'].isna()]

# merging the account number to the permit using the parcel number if the permit did not get successfully merged based
# on the address
df_permit_addr['strap_final'] = df_permit_addr['strap'].where(df_permit_addr['strap'].notnull(),
                                                              df_active_addr['strap'])

# merging the final permit spreadsheet with the parcel number data frame
df_perm_addr_folio = df_permit_addr.merge(df_folio, on='Parcel Number')

# this takes the strap from the folio data frame and fills in the strap with the permit/address data frame if the merge
# couldn't be completed via the address data frame
df_perm_addr_folio['strap_final'] = df_perm_addr_folio['strap_x'].where(df_perm_addr_folio['strap_x'].notna(),
                                                                        df_perm_addr_folio['strap_y'])
df_perm_addr_folio.fillna('')

# this is cleaning up the columns to prepare it to be exported for xlsx
df_final = df_perm_addr_folio.drop(['strap_y', 'strap_x', 'status_cd', 'dor_cd', 'nh_cd'], axis=1)
df_final.rename(columns={'strap_final': "strap"}, inplace=True)
df_final.rename(columns={'str_num': "StreetNo_txt"}, inplace=True)
df_final['StreetNo_txt'] = df_final['StreetNo_txt'].astype(float)
df_final.rename(columns={'str_pfx': "StreetDir"}, inplace=True)
df_final.rename(columns={'str': "StreetName"}, inplace=True)
df_final.rename(columns={'str_sfx': "StreetType"}, inplace=True)
df_final.rename(columns={'str_unit': "Unit"}, inplace=True)
df_final['StreetType'] = df_final['StreetType'].fillna('')
df_final['Unit'] = df_final['Unit'].fillna('')
df_final['StreetDir'] = df_final['StreetDir'].fillna('')

# sometimes the address field doesn't merge correctly and fill correctly with the street number, direction, name, type
# and unit so I took the address data frame and merged it, then filled it based on whether it was NaN
df_final = pd.merge(df_final, df_address, on='strap')
df_final['strap'] = df_final['strap'].str.rstrip()
df_final.drop_duplicates(subset='Permit Number', keep='first', inplace=True)
df_final['StreetNo_txt'] = df_final['StreetNo_txt'].where(df_final['StreetNo_txt'].notna(), df_final['str_num'])
df_final['StreetDir'] = df_final['StreetDir'].where(df_final['StreetDir'].notna(), df_final['str_pfx'])
df_final['StreetName'] = df_final['StreetName'].where(df_final['StreetName'].notna(), df_final['str'])
df_final['StreetType'] = df_final['StreetType'].where(df_final['StreetType'].notna(), df_final['str_sfx'])
df_final['Unit'] = df_final['Unit'].where(df_final['Unit'].notna(), df_final['str_unit'])

# preparing the data frame to be exported into a format that will be imported into the permit.exe
df_final = df_final[["Permit Number", "Parent Permit Number", "strap", "Description", "StreetNo_txt", "StreetDir",
                     "StreetName", "StreetType", "Unit", "Value Total", "Issued Date", "Finaled Date", "Work Class",
                     "SCOPE"]]

# a simple way to check to see if an already uploaded permit is in CAMA, it's checked in an earlier line,
# but if for some reason the CAMA permit upload system doesn't upload the permit successfully,
# this code can be run again and it will pick up any not uploaded permits at this point
# During the first run, these two lines are commented out so that it doesn't interfere with the initial upload

df_final = df_final.loc[~df_final['Permit Number'].isin(df1_1['Permit Number'])]
df_final.drop_duplicates()

print('\n\n----- df_final (1) -----\n')
print(df_final.head(2))
# print preview

df_final = df_final.fillna('')

# spreadsheet for app.
df_spread_for_app['strap'] = df_spread_for_app['strap'].str.rstrip()
df_final = pd.merge(df_final, df_spread_for_app, on='strap')
df_final.to_excel(SetDate + "_permits_Appraiser.xlsx", index=False)

# remove map_id, nh_cd, and dor_cd from the text file
df_final = df_final.drop(['map_id', 'nh_cd', 'dor_cd'], axis=1)

# export final data to a txt file to be imported
header = ''  # first, create the header
for s in list(df_final):
    header += '"' + s + '"|'
header = header[:-1]  # to take the final | off, as it's unnecessary
# take the values of each column and add double quotes
df_final.update(df_final[["Permit Number", "Parent Permit Number", "strap", "Description", "StreetNo_txt", "StreetDir",
                          "StreetName", "StreetType", "Unit", "Value Total", "Issued Date", "Finaled Date",
                          "Work Class", "SCOPE"]].applymap('"{}"'.format))

print('\n\n----- df_final (2) -----\n')
print(df_final.head(2))
# print preview

# now, save to a text file with a | separator
np.savetxt(SetDate + '_permits.txt', df_final.values, fmt='%s', header=header, comments='', delimiter='|')
