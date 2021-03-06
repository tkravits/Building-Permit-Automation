import pandas as pd
import pyodbc
import numpy as np
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from openpyxl import Workbook
import glob
import csv

# TODO - when a CSV, the folio gets truncated which doesn't allow for an accurate merge, converting the csv to xlsx
# TODO - has fixed this but would like to get CSV to work

# sets the display so that when the code prints, it is readable
pd.set_option('display.max_rows', 1500)
pd.set_option('display.max_columns', 50)
pd.set_option('display.width', 1500)

# set the time for exported excel spreadsheets
CurrentDate = pd.Timestamp.today().strftime("%B%Y")

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

# create an input to select the earliest date the user wants to upload
print('Please input the earilest date you would like (ex: 09/26/2020)')
df = df[df['AppliedDate'] > input()]

# remove if starts with
df = df.dropna(how='all')
df = df[~df['Parcel Number'].str.contains('BLK', na=False)]
df = df[~df['Parcel Number'].str.contains('INT', na=False)]
# remove missing values
df.dropna(subset=['Parcel Number', 'Address'])
df_review = df[df['Status'].str.contains('In Review', na=False)]
df = df[~df['Work Class'].str.contains('Information', na=False)]
df = df[~df['Work Class'].str.contains('Temporary Event', na=False)]

# these are the permits that are in review (aren't uploaded to cama)
df_review.to_excel("Permits_In_Review_from" + CurrentDate + '.xlsx')

# removes Pending, Void, In Review, Withdrawn, Approved for permits in the Status. We only want permits that
# either have been issued or are already completed since permit value and other areas can change.

df = df[df['Status'].str.contains('Issued|Letter|Certificate|Closed', na=False)]
df = df[df['Issued Date'].notna()]

# removes *, ", and carriage returns
df['Description'].replace(regex=True, inplace=True, to_replace=r'\*', value=r'')
df['Description'].replace(regex=True, inplace=True, to_replace=r'\n', value=r'')
df['Description'].replace(regex=True, inplace=True, to_replace=r'\r', value=r'')
df['Description'].replace(regex=True, inplace=True, to_replace=r'\"', value=r'')

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

df.loc[df['Work Class'].str.contains('Temporary', case=False, na=False), 'SCOPE'] = 'ELM'
df.loc[df['Work Class'].str.contains('Construction', case=False, na=False), 'SCOPE'] = 'OTH'
df.loc[df['Description'].str.contains('RTU', case=False, na=False), 'SCOPE'] = 'HTG'
df.loc[df['Description'].str.contains('RTUs', case=False, na=False), 'SCOPE'] = 'HTG'
df.loc[df['Work Class'].str.contains('Mechanical', na=False), 'SCOPE'] = 'ELM'
df.loc[df['Work Class'].str.contains('Electrical', case=False, na=False), 'SCOPE'] = 'ELM'
df.loc[df['Work Class'].str.contains('Grading', na=False), 'SCOPE'] = 'OTH'
df.loc[df['Work Class'].str.contains('Groundwater', na=False), 'SCOPE'] = 'OTH'
df.loc[df['Work Class'].str.contains('Erosion', na=False), 'SCOPE'] = 'OTH'
df.loc[df['Work Class'].str.contains('Roofing', na=False), 'SCOPE'] = 'RRR'
df.loc[df['Description'].str.contains('heat', case=False, na=False), 'SCOPE'] = 'OTH'
df.loc[df['Work Class'].str.contains('Non-Public', na=False), 'SCOPE'] = 'OTH'
df.loc[df['Work Class'].str.contains('Public', na=False), 'SCOPE'] = 'OTH'
df.loc[df['Description'].str.contains('boiler', case=False, na=False), 'SCOPE'] = 'OTH'
df.loc[df['Description'].str.contains('ductless', case=False, na=False), 'SCOPE'] = 'HTG'
df.loc[df['Description'].str.contains('furnace', case=False, na=False), 'SCOPE'] = 'HTG'
df.loc[df['Description'].str.contains('heater', case=False, na=False), 'SCOPE'] = 'OTH'
df.loc[df['Description'].str.contains('PV', case=False, na=False), 'SCOPE'] = 'ENR'
df.loc[df['Description'].str.contains('solar', case=False, na=False), 'SCOPE'] = 'ENR'
df.loc[df['Description'].str.contains('photo', case=False, na=False), 'SCOPE'] = 'ENR'
df.loc[df['Description'].str.contains('P.V.', case=False, na=False), 'SCOPE'] = 'ENR'
df.loc[df['Description'].str.contains('photovoltaic', case=False, na=False), 'SCOPE'] = 'ENR'
df.loc[df['Description'].str.contains('geotherm', case=False, na=False), 'SCOPE'] = 'ENR'
df.loc[df['Description'].str.contains('flush-mounted', case=False, na=False), 'SCOPE'] = 'ENR'
df.loc[(df['Work Class'].str.contains('Mechanical', na=False)) & (
    df['Description'].str.contains('gas fireplace', case=False, na=False)), 'SCOPE'] = 'GFP'
df.loc[(df['Work Class'].str.contains('Mechanical', na=False)) & (
    df['Description'].str.contains('existing wood-burning', case=False, na=False)), 'SCOPE'] = 'GFP'
df.loc[(df['Work Class'].str.contains('Mechanical', na=False)) & (
    df['Description'].str.contains('wood burning', case=False, na=False)
    & (df['Description'].str.contains('replace', case=False, na=False))), 'SCOPE'] = 'GFP'
df.loc[df['Work Class'].str.contains('Repair', na=False), 'SCOPE'] = 'GRP'
df.loc[(df['Work Class'].str.contains('Repair', na=False)) & (
    df['Description'].str.contains('foundation', case=False, na=False)), 'SCOPE'] = 'SRP'
df.loc[(df['Work Class'].str.contains('Repair', na=False)) & (
    df['Description'].str.contains('structural', case=False, na=False)), 'SCOPE'] = 'SRP'
df.loc[
    (df['Work Class'].str.contains('Repair', na=False)) & (df['Description'].str.contains('fire', case=False, na=False)), 'SCOPE'] = 'FRP'
df.loc[(df['Work Class'].str.contains('Mechanical HVAC', na=False)) & (
    df['Description'].str.contains('gas fireplace', case=False, na=False)), 'SCOPE'] = 'GFP'
df.loc[(df['Work Class'].str.contains('Mechanical HVAC', na=False)) & (
    df['Description'].str.contains('mini-split', case=False, na=False)), 'SCOPE'] = 'AIR'
df.loc[(df['Work Class'].str.contains('Mechanical HVAC', na=False)) & (
    df['Description'].str.contains('mini split', case=False, na=False)), 'SCOPE'] = 'AIR'
df.loc[(df['Work Class'].str.contains('Mechanical HVAC', na=False)) & (
    df['Description'].str.contains('condenser', case=False, na=False)), 'SCOPE'] = 'AIR'
df.loc[(df['Work Class'].str.contains('Mechanical HVAC', na=False)) & (
    df['Description'].str.contains('air condition', case=False, na=False)), 'SCOPE'] = 'AIR'
df.loc[(df['Work Class'].str.contains('Mechanical HVAC', na=False)) & (
    df['Description'].str.contains('a/c', case=False, na=False)), 'SCOPE'] = 'AIR'
df.loc[(df['Work Class'].str.contains('Mechanical HVAC', na=False)) & (
    df['Description'].str.contains(' ac ', case=False, na=False)), 'SCOPE'] = 'AIR'
df.loc[(df['Work Class'].str.contains('Mechanical HVAC', na=False)) & (
    df['Description'].str.contains(' ac', case=False, na=False)), 'SCOPE'] = 'AIR'
df.loc[(df['Work Class'].str.contains('Mechanical HVAC', na=False)) & (
    df['Description'].str.contains(' a/c ', case=False, na=False)), 'SCOPE'] = 'AIR'
df.loc[df['Work Class'].str.contains('Mechanical Sub-', na=False), 'SCOPE'] = 'ELM'
df.loc[df['Work Class'].str.contains('Plumbing', na=False), 'SCOPE'] = 'ELM'
df.loc[df['Work Class'].str.contains('Electrical Sub-', na=False), 'SCOPE'] = 'ELM'
df.loc[df['Work Class'].str.contains('Utility', na=False), 'SCOPE'] = 'OTH'
df.loc[df['Work Class'].str.contains('Siding', na=False), 'SCOPE'] = 'SDG'
df.loc[df['Work Class'].str.contains('Right', na=False), 'SCOPE'] = 'OTH'
df.loc[(df['Work Class'].str.contains('Right', na=False)) & (
    df['Description'].str.contains('sewer', case=False, na=False)), 'SCOPE'] = 'RWSRPR'
df.loc[df['Work Class'].str.contains('Fence', na=False), 'SCOPE'] = 'FEN'
df.loc[df['Work Class'].str.contains('Tenant', na=False), 'SCOPE'] = 'TFN'
df.loc[df['Work Class'].str.contains('Remodel', na=False), 'SCOPE'] = 'REM'
df.loc[(df['Work Class'].str.contains('Remodel', na=False)) & (
    df['Description'].str.contains('finished basement', case=False, na=False)), 'SCOPE'] = 'BFN'
df.loc[(df['Work Class'].str.contains('Remodel', na=False)) & (
    df['Description'].str.contains('basement finish', case=False, na=False)), 'SCOPE'] = 'BFN'
df.loc[(df['Work Class'].str.contains('Remodel', na=False)) & (
    df['Description'].str.contains('basement remodel', case=False, na=False)), 'SCOPE'] = 'BFN'
df.loc[(df['Work Class'].str.contains('Remodel', na=False)) & (
    df['Description'].str.contains('bathroom remodel', case=False, na=False)), 'SCOPE'] = 'BTH'
df.loc[(df['Work Class'].str.contains('Remodel', na=False)) & (
    df['Description'].str.contains('bath remodel', case=False, na=False)), 'SCOPE'] = 'BTH'
df.loc[(df['Work Class'].str.contains('Remodel', na=False)) & (
    df['Description'].str.contains('tenant', case=False, na=False)), 'SCOPE'] = 'TFN'
df.loc[df['Work Class'].str.contains('New', na=False), 'SCOPE'] = 'NEW'
df.loc[(df['Work Class'].str.contains('New', na=False)) & (
    df['Description'].str.contains('garage built', case=False, na=False)), 'SCOPE'] = 'GAR'
df.loc[df['Work Class'].str.contains('Addition', na=False), 'SCOPE'] = 'ADD'
df.loc[(df['Work Class'].str.contains('Addition', na=False)) & (
    df['Description'].str.contains(' deck', case=False, na=False)), 'SCOPE'] = 'DEC'
df.loc[(df['Work Class'].str.contains('Addition', na=False)) & (
    df['Description'].str.contains('new porch', case=False, na=False)), 'SCOPE'] = 'POR'
df.loc[(df['Work Class'].str.contains('Addition', na=False)) & (
    df['Description'].str.contains('pergola', case=False, na=False)), 'SCOPE'] = 'POR'
df.loc[(df['Work Class'].str.contains('Addition', na=False)) & (
    df['Description'].str.contains(' shed', case=False, na=False)), 'SCOPE'] = 'OUT'
df.loc[df['Work Class'].str.contains('Addition and', na=False), 'SCOPE'] = 'ADD'
df.loc[df['Work Class'].str.contains('Wireless', na=False), 'SCOPE'] = 'OTH'
df.loc[df['Work Class'].str.contains('Demo', na=False), 'SCOPE'] = 'DEM'
df.loc[df['Work Class'].str.contains('Sign', na=False), 'SCOPE'] = 'SGN'
df.loc[df['Work Class'].str.contains('Fire', na=False), 'SCOPE'] = 'SPK'
df.loc[(df['Permit Type'].str.contains('Mobile Home', na=False)) & (
    df['Description'].str.contains('replacement', case=False, na=False)), 'SCOPE'] = 'MHN'
df.loc[(df['Permit Type'].str.contains('Mobile Home', na=False)) & (
    df['Description'].str.contains('new', case=False, na=False)), 'SCOPE'] = 'MHN'
df.loc[
    (df['Work Class'].str.contains('Roofing', na=False)) & (df['Description'].str.contains('roof', case=False, na=False)), 'SCOPE'] = 'RRR'
df.loc[(df['Work Class'].str.contains('Roofing', na=False)) & (
    df['Description'].str.contains('single', case=False, na=False)), 'SCOPE'] = 'RRR'
df.loc[
    (df['Work Class'].str.contains('Roofing', na=False)) & (df['Description'].str.contains('SFD', case=False, na=False)), 'SCOPE'] = 'RRR'
df.loc[(df['Work Class'].str.contains('Roofing', na=False)) & (
    df['Description'].str.contains('residential', case=False, na=False)), 'SCOPE'] = 'RRR'
df.loc[
    (df['Work Class'].str.contains('Roofing', na=False)) & (df['Description'].str.contains('multi', case=False, na=False)), 'SCOPE'] = 'RRR'
df.loc[(df['Work Class'].str.contains('Roofing', na=False)) & (
    df['Description'].str.contains('duplex', case=False, na=False)), 'SCOPE'] = 'RRR'
df.loc[(df['Work Class'].str.contains('Roofing', na=False)) & (
    df['Description'].str.contains('re-roof', case=False, na=False)), 'SCOPE'] = 'RRR'
df.loc[(df['Work Class'].str.contains('Roofing', na=False)) & (
    df['Description'].str.contains('re roof', case=False, na=False)), 'SCOPE'] = 'RRR'
df.loc[(df['Work Class'].str.contains('Roofing', na=False)) & (
    df['Description'].str.contains('shingle', case=False, na=False)), 'SCOPE'] = 'RRR'
df.loc[(df['Work Class'].str.contains('Roofing', na=False)) & (
    df['Description'].str.contains('commercial', case=False, na=False)), 'SCOPE'] = 'CRR'

# creates an Excel file based on blank parcel fields, this is done as an edit check for the COB permit process just to
# make sure that there's nothing we're missing. Unfortunately, these will most likely need to be manually entered into
# CAMA, especially if they have some sort of larger value

df_blank = df[df['Parcel Number'].isna()]
# df_blank.to_excel("Permits_w_no_parcel_num_" + SetDate + '.xlsx')# df_blank.to_excel("Permits_w_no_parcel_num_" + SetDate + '.xlsx')

# sets the parcel column type to a string
df['Parcel Number'] = df['Parcel Number'].astype('str')

# establishes a connection to the permit database
print('Establishing connection...\n')
c_str = open('connection_string.txt', 'r').read()  # can be removed once connection string is added
cnxn = pyodbc.connect(c_str)  # add connection string here

# various SQLs that select from the database
sql = '''SELECT distinct parcel.strap, parcel.status_cd, parcel.dor_cd, parcel.nh_cd FROM r_prod.dbo.parcel
WHERE (parcel.dor_cd <> 'POSS') AND parcel.status_cd = 'A' '''

sql1 = '''SELECT distinct folio, strap FROM r_prod.dbo.strap_idx'''

sql2 = '''SELECT distinct permit_num FROM r_prod.dbo.permit WHERE permit.agency_id = 'BLD' '''

sql3 = '''SELECT distinct site.strap, site.str_num, site.str_pfx, site.str, site.str_sfx, site.str_sfx_dir,
site.str_unit FROM r_prod.dbo.site WHERE (site.city IN ('BOULDER', 'UNINCORPORATED'))'''

sql4 = '''SELECT distinct parcel.map_id, parcel.nh_cd, parcel.dor_cd, parcel.strap FROM r_prod.dbo.parcel'''

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

df_uploaded = pd.merge(df, df_permit, on='Permit Number')

# compares permits that are in CAMA vs ones that aren't, merges df and drops ones that are already in CAMA
df_not_up = df.loc[~df['Permit Number'].isin(df_uploaded['Permit Number'])]
df_not_up.drop_duplicates()

# make one df that merges active accounts with the address associated with them
df_address['strap'] = df_address['strap'].str.rstrip()
df_active_acct['strap'] = df_active_acct['strap'].str.rstrip()
df_active_addr = pd.merge(df_active_acct, df_address, on='strap')

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
df_active_addr = df_active_addr.replace('\s+', ' ', regex=True)

# merges the Boulder accounts database (strap) with the created Address field with the monthly COB permit spreadsheet
df_permit_addr = df.merge(df_active_addr, on='Address', how='left')

# takes the unmerged addresses and makes a spreadsheet to be checked by hand
df_permit_addr_nostrap = df_permit_addr.loc[df_permit_addr['strap'].isna()]

# merging the account number to the permit using the parcel number if the permit did not get successfully merged based
# on the address
df_folio['strap'] = df_folio['strap'].str.rstrip()
df_folio['Parcel Number'] = df_folio['Parcel Number'].str.rstrip()

# merging the final permit spreadsheet with the parcel number data frame
df_permit_addr_folio = df_permit_addr.merge(df_folio, on='Parcel Number')

# this takes the strap from the folio data frame and fills in the strap with the permit/address data frame if the merge
# couldn't be completed via the address data frame

df_permit_addr_folio['strap_final'] = df_permit_addr_folio['strap_x'].where(df_permit_addr_folio['strap_x'].notnull(),
                                                                        df_permit_addr_folio['strap_y'])
df_permit_addr_folio.fillna('')

# this is cleaning up the columns to prepare it to be exported for xlsx
df_final = df_permit_addr_folio.drop(['strap_y', 'strap_x', 'status_cd', 'dor_cd', 'nh_cd'], axis=1)
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
df_final['StreetNo_txt'] = df_final['StreetNo_txt'].where(df_final['StreetNo_txt'].notna(), df_final['str_num']).astype(int)
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

df_final = df_final.loc[~df_final['Permit Number'].isin(df_uploaded['Permit Number'])]
df_final.drop_duplicates()

df_final = df_final.fillna('')

# spreadsheet for app.
df_spread_for_app['strap'] = df_spread_for_app['strap'].str.rstrip()
df_final = pd.merge(df_final, df_spread_for_app, on='strap')

print('Please name the spreadsheet to be sent to the appraisers')
df_final.to_excel(input() + ".xlsx", index=False)

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


# now, save to a text file with a | separator
print("Please name the txt file that will be uploaded to CAMA")
np.savetxt(input() + '.txt', df_final.values, fmt='%s', header=header, comments='', delimiter='|')
