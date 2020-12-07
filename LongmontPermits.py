import pandas as pd
import pyodbc
import numpy as np
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from openpyxl import Workbook
import glob
import csv
from dbfread import DBF
from pandas import DataFrame

# TODO - when a CSV, the folio gets truncated which doesn't allow for an accurate merge, converting the csv to xlsx
# TODO - has fixed this but would like to get CSV to work

# sets the display so that when the code prints, it is readable
pd.set_option('display.max_rows', 1500)
pd.set_option('display.max_columns', 50)
pd.set_option('display.width', 1500)

# set the time for exported excel spreadsheets
CurrentDate = pd.Timestamp.today()
SetDate = (CurrentDate - pd.DateOffset(months=1)).strftime("%B%Y")

#imports the permit sheet to be cleaned up
print('Opening file window...\n')
Tk().withdraw()  # this prevents root tkinter window from appearing
filename = askopenfilename(filetypes=[('Excel', ('*.xls', '*.xlsx')), ('CSV', ('*.csv')), ('DBF', ('*.dbf'))])  # this opens a window to choose out excel sheet
try:
    df = pd.read_excel(filename)  # assign df to the chosen
except:
    #df = pd.read_csv(filename, sep=",", error_bad_lines=False, index_col=False, encoding='ISO-8859-1')
    try:
        dbf = DBF(filename, char_decode_errors='ignore')
        df = DataFrame(iter(dbf))
    except:
        print('Please input a valid Excel, CSV, or DBF file format')
# print status
print('Data loading...\n')
def Spreadsheet_formater(df):

def Issued_Date_filter(df):
    # create an input to select the earliest date the user wants to upload
    print('Please input the earliest date you would like (ex: 09/26/2020)')
    date = input()
    if 'AppliedDate' in df.columns:
        df = df[df['AppliedDate'] > date]

    if 'Issued_Dat' in df.columns:
        df['Issued_Dat'] = pd.to_datetime(df['Issued_Dat'])
        df = df[df['Issued_Dat'] > date]

    else:
        print('No valid issue date column')

    return df


df = Issued_Date_filter(df)

def Permit_Classifier(df):
    if 'Description' in df.columns:
        # Classifies the description into a format that CAMA can understand
        df.loc[df['Description'].str.contains('valve', case=False, na=False), 'SCOPE'] = 'OTH'
        df.loc[df['Description'].str.contains('pipe', case=False, na=False), 'SCOPE'] = 'OTH'
        df.loc[df['Description'].str.contains('electric', case=False, na=False), 'SCOPE'] = 'ELM'
        df.loc[df['Description'].str.contains('electrical', case=False, na=False), 'SCOPE'] = 'ELM'
        df.loc[df['Description'].str.contains('boiler', case=False, na=False), 'SCOPE'] = 'OTH'
        df.loc[df['Description'].str.contains('ductless', case=False, na=False), 'SCOPE'] = 'HTG'
        df.loc[df['Description'].str.contains('furnace', case=False, na=False), 'SCOPE'] = 'HTG'
        df.loc[df['Description'].str.contains('heater', case=False, na=False), 'SCOPE'] = 'OTH'
        df.loc[df['Description'].str.contains('/AC', case=False, na=False), 'SCOPE'] = 'AIR'
        df.loc[df['Description'].str.contains('cooler', case=False, na=False), 'SCOPE'] = 'AIR'
        df.loc[df['Description'].str.contains(' AC ', case=False, na=False), 'SCOPE'] = 'AIR'
        df.loc[df['Description'].str.contains('AC ', case=False, na=False), 'SCOPE'] = 'AIR'
        df.loc[df['Description'].str.contains('AC', case=False, na=False), 'SCOPE'] = 'AIR'
        df.loc[df['Description'].str.contains('A/C', case=False, na=False), 'SCOPE'] = 'AIR'
        df.loc[df['Description'].str.contains('PV', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Description'].str.contains('solar', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Description'].str.contains('photo', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Description'].str.contains('P.V.', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Description'].str.contains('photovoltaic', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Description'].str.contains('geotherm', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Description'].str.contains('flush-mounted', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Description'].str.contains('Fence', case=False,na=False), 'SCOPE'] = 'FEN'
        df.loc[df['Description'].str.contains('Tenant', case=False,na=False), 'SCOPE'] = 'TFN'
        df.loc[df['Description'].str.contains('Kitchen' ,case=False, na=False), 'SCOPE'] = 'REM'
        df.loc[df['Description'].str.contains('Remodel' ,case=False, na=False), 'SCOPE'] = 'REM'
        df.loc[df['Description'].str.contains('sewer', case=False, na=False), 'SCOPE'] = 'RWSRPR'
        df.loc[df['Description'].str.contains('finished basement', case=False, na=False), 'SCOPE'] = 'BFN'
        df.loc[df['Description'].str.contains('basement finish', case=False, na=False), 'SCOPE'] = 'BFN'
        df.loc[df['Description'].str.contains('basement remodel', case=False, na=False), 'SCOPE'] = 'BFN'
        df.loc[df['Description'].str.contains('basement bathroom', case=False, na=False), 'SCOPE'] = 'BFN'
        df.loc[df['Description'].str.contains('bathroom remodel', case=False, na=False), 'SCOPE'] = 'BTH'
        df.loc[df['Description'].str.contains('bath remodel', case=False, na=False), 'SCOPE'] = 'BTH'
        df.loc[df['Description'].str.contains('tenant', case=False, na=False), 'SCOPE'] = 'TFN'
        df.loc[df['Description'].str.contains('New', na=False), 'SCOPE'] = 'NEW'
        df.loc[df['Description'].str.contains('SFR', case=False, na=False), 'SCOPE'] = 'NEW'
        df.loc[df['Description'].str.contains('Townhome', case=False, na=False), 'SCOPE'] = 'NEW'
        df.loc[df['Description'].str.contains('Foundation', case=False, na=False), 'SCOPE'] = 'NEW'
        df.loc[df['Description'].str.contains('Duplex', case=False, na=False), 'SCOPE'] = 'NEW'
        df.loc[df['Description'].str.contains('Structural', case=False,  na=False), 'SCOPE'] = 'SRP'
        df.loc[df['Description'].str.contains('garage', case=False, na=False), 'SCOPE'] = 'GAR'
        df.loc[df['Description'].str.contains('garage', case=False, na=False), 'SCOPE'] = 'GAR'
        df.loc[df['Description'].str.contains('Addition', na=False), 'SCOPE'] = 'ADD'
        df.loc[df['Description'].str.contains('patio', case=False, na=False), 'SCOPE'] = 'POR'
        df.loc[df['Description'].str.contains('porch', case=False, na=False), 'SCOPE'] = 'POR'
        df.loc[df['Description'].str.contains('pergola', case=False, na=False), 'SCOPE'] = 'POR'
        df.loc[df['Description'].str.contains('deck', case=False, na=False), 'SCOPE'] = 'DEC'
        df.loc[df['Description'].str.contains('shed', case=False, na=False), 'SCOPE'] = 'OUT'
        df.loc[df['Description'].str.contains('pool', case=False, na=False), 'SCOPE'] = 'POL'
        df.loc[df['Description'].str.contains('Wireless', na=False), 'SCOPE'] = 'OTH'
        df.loc[df['Description'].str.contains('Water line', case=False, na=False), 'SCOPE'] = 'OTH'
        df.loc[df['Description'].str.contains('Gas line', case=False, na=False), 'SCOPE'] = 'OTH'
        df.loc[df['Description'].str.contains('radon', case=False, na=False), 'SCOPE'] = 'OTH'
        df.loc[df['Description'].str.contains('Demo', na=False), 'SCOPE'] = 'DEM'
        df.loc[df['Description'].str.contains('Sign', na=False), 'SCOPE'] = 'SGN'
        df.loc[df['Description'].str.contains('Fire', na=False), 'SCOPE'] = 'SPK'
        df.loc[df['Description'].str.contains('Window', na=False), 'SCOPE'] = 'W/D'
        df.loc[df['Description'].str.contains('Door', na=False), 'SCOPE'] = 'W/D'
        df.loc[df['Description'].str.contains('mobile home', case=False, na=False), 'SCOPE'] = 'MHN'
        df.loc[df['Description'].str.contains('trailer', case=False, na=False), 'SCOPE'] = 'MHN'
        df.loc[(df['Description'].str.contains('Roof', na=False)), 'SCOPE'] = 'RRR'
        df.loc[(df['Description'].str.contains('Roofing', na=False)) & (
            df['Description'].str.contains('commercial', case=False, na=False)), 'SCOPE'] = 'CRR'

    else:
         print('Please provide a permit description column titled "Description"')

    return df

# TODO - make sure the value for the permit is an int
#
# print('Establishing connection...\n')
# c_str = open('connection_string.txt', 'r').read()  # can be removed once connection string is added
# cnxn = pyodbc.connect(c_str)
#
# sql = '''SELECT distinct parcel.strap, parcel.status_cd, parcel.dor_cd, parcel.nh_cd FROM r_prod.dbo.parcel
# WHERE (parcel.dor_cd <> 'POSS') AND parcel.status_cd = 'A' '''
#
# sql2 = '''SELECT distinct permit_num FROM r_prod.dbo.permit'''
#
# sql3 = '''SELECT distinct site.strap, site.str_num, site.str_pfx, site.str, site.str_sfx, site.str_sfx_dir,
# site.str_unit FROM r_prod.dbo.site WHERE (site.city IN ('LONGMONT', 'UNINCORPORATED'))'''
#
# sql4 = '''SELECT distinct parcel.map_id, parcel.nh_cd, parcel.dor_cd, parcel.strap FROM r_prod.dbo.parcel'''
#
# df_active_acct = pd.read_sql(sql, cnxn)
# df_permit = pd.read_sql(sql2, cnxn)
# df_address = pd.read_sql(sql3, cnxn)
# df_spread_for_app = pd.read_sql(sql4, cnxn)
#
# # Takes the permit database, renames the column to Permit Number, and then merges the month's permit with permits found
# # in the database, this makes sure a permit is not double uploaded, or double valuing
#
# df_permit.rename(columns={'permit_num': 'Permit Number'}, inplace=True)
#
# df_uploaded = pd.merge(df, df_permit, on='Permit Number')
#
# # a simple way to check to see if an already uploaded permit is in CAMA, it's checked in an earlier line,
# # but if for some reason the CAMA permit upload system doesn't upload the permit successfully,
# # this code can be run again and it will pick up any not uploaded permits at this point
# # During the first run, these two lines are commented out so that it doesn't interfere with the initial upload
#
# df = df.loc[~df['Permit Number'].isin(df_uploaded['Permit Number'])]
# df.drop_duplicates()
#
# # make one df that merges active accounts with the address associated with them
# df_active_addr = pd.merge(df_active_acct, df_address, on='strap')
#
# # attempting to take situs address, concat, and compare with the Boulder permit address (only using active accts, no
# # possessory interest)
#
# df_active_addr.dropna(subset=['str_num'])
# df_active_addr['str_num'] = df_active_addr['str_num'].astype(int).astype(str)
# df_active_addr['str_pfx'] = df_active_addr['str_pfx'].fillna(np.nan).replace(np.nan, ' ', regex=True)
# df_active_addr['str_pfx'] = df_active_addr['str_pfx'].replace('  ', ' ', regex=True)
# df_active_addr['str_pfx'] = df_active_addr['str_pfx'].replace('S', ' S', regex=True)
# df_active_addr['str_pfx'] = df_active_addr['str_pfx'].replace('N', ' N', regex=True)
# df_active_addr['str_pfx'] = df_active_addr['str_pfx'].replace('E', ' E', regex=True)
# df_active_addr['str_pfx'] = df_active_addr['str_pfx'].replace('W', ' W', regex=True)
# df_active_addr['str_sfx'] = df_active_addr['str_sfx'].fillna(np.nan).replace(np.nan, ' ', regex=True)
# df_active_addr['str_sfx'] = df_active_addr['str_sfx'].replace('  ', '', regex=True)
# df_active_addr['str_sfx_dir'] = df_active_addr['str_sfx_dir'].fillna(np.nan).replace(np.nan, ' ', regex=True)
# df_active_addr['str_sfx_dir'] = df_active_addr['str_sfx_dir'].replace('  ', ' ', regex=True)
# df_active_addr['str_unit'] = df_active_addr['str_unit'].fillna(np.nan).replace(np.nan, '', regex=True)
#
# # creates a column called Address that is set up in the same format as the Superior permits table
# df_active_addr['Address'] = df_active_addr['str_num'] + df_active_addr['str_pfx'] + df_active_addr['str'] + \
#                             ' ' + df_active_addr['str_sfx'] + df_active_addr['str_sfx_dir'] + df_active_addr['str_unit']
# df_active_addr['Address'] = df_active_addr['Address'].str.rstrip()
#
# # merges the Superior accounts database (strap) with the created Address field with the Superior permit spreadsheet
# df_permit_addr = df.merge(df_active_addr, on='Address', how='left')
#
# # takes the unmerged addresses and makes a spreadsheet to be checked by hand
# df_permit_addr_nostrap = df_permit_addr.loc[df_permit_addr['strap'].isna()]
# df_permit_addr_nostrap.to_excel('HandEnter_Longmont_permits.xlsx', index=False)
#
# df_final = df_permit_addr.drop(['status_cd', 'dor_cd', 'nh_cd'], axis=1)
# df_final['strap'] = df_final['strap'].str.rstrip()
# df_final.drop_duplicates(subset='Permit Number', keep='first', inplace=True)
#
# df_final = df_final[["Permit Number", "strap", "Description", "str_num", "str_pfx",
#                      "str", "str_sfx", "str_unit", "Value Total", "Date", "SCOPE"]]
#
# df_final = df_final.dropna(subset=['strap'])
#
# # spreadsheet for app.
# df_spread_for_app['strap'] = df_spread_for_app['strap'].str.rstrip()
# df_final = pd.merge(df_final, df_spread_for_app, on='strap')
# print('Please name the exported spreadsheet for the Appraiser staff')
# df_final.to_excel(input() + "_LongmontPermits_Appraiser.xlsx", index=False)
#
# # export final data to a txt file to be imported
# header = ''  # first, create the header
# for s in list(df_final):
#     header += '"' + s + '"|'
# header = header[:-1]  # to take the final | off, as it's unnecessary
# # take the values of each column and add double quotes
# df_final.update(df_final[["Permit Number", "strap", "Description", "str_num", "str_pfx",
#                      "str", "str_sfx", "str_unit", "Value Total", "Date", "SCOPE"]].applymap('"{}"'.format))
#
# # now, save to a text file with a | separator
# print("Please name the txt file that will be uploaded to CAMA")
# np.savetxt(input() + '.txt', df_final.values, fmt='%s', header=header, comments='', delimiter='|')