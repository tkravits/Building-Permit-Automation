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


def file_opener():
    # imports the permit sheet to be cleaned up
    print('Opening file window...\n')
    Tk().withdraw()  # this prevents root tkinter window from appearing
    # this opens a window to choose out excel sheet
    filename = askopenfilename(filetypes=[('Excel', ('*.xls', '*.xlsx')), ('CSV', ('*.csv')), ('DBF', ('*.dbf'))])

    if filename.endswith(('.xlsx', '.xls')):
        try:
            df = pd.read_excel(filename)  # assign df to the chosen
        except:
            print('Potentially corrupt excel file, please open in Excel to check')
    elif filename.endswith('.dbf'):
        try:
            dbf = DBF(filename, char_decode_errors='ignore')
            df = DataFrame(iter(dbf))
        except:
            print("Potentially corrupt dbf file, please attempt to export via ArcMap")
    elif filename.endswith('.csv'):
        try:
            df = pd.read_csv(filename, sep=",", error_bad_lines=False, index_col=False, encoding='ISO-8859-1',
                            lineterminator='\n', low_memory=False)
        except:
            print('Potentially corrupt csv file, please open in Excel to check')

    elif not filename.endswith(('.xls', '.xlsx', '.csv', '.dbf')):
        print('Please input a valid Excel, CSV, or DBF file format')

    # print status
    print('Data loading...\n')
    return df


def municipal_chooser():
    while True:
        print('Please input the municipality whose permits you would like to upload')
        city = input('Municipality: ')
        try:
            if city is 'Boulder':
                city = 'Boulder'

            elif city is 'Longmont':
                city = 'Longmont'

            elif city is 'Superior':
                city = 'Superior'

            elif city not in ['Boulder', 'Longmont', 'Superior']:
                print('Please input a valid city or use format (ex: Boulder, Longmont)')
                continue

        except TypeError:
            print('Please input city in format using "City" (ex: Boulder, Longmont)')
            continue

        return city


def spreadsheet_formatter(df):
    if 'PIN' in df.columns:
        df = df.rename(columns={'PIN': 'Parcel Number'})  # else if named pin, rename it

    if 'Parcel' in df.columns:
        df = df.rename(columns={'Parcel': 'Parcel Number'})

    if 'OriginalAddress' in df.columns:
        df = df.rename(columns={'OriginalAddress': 'Address'})

    if 'BuildingAd' in df.columns:
        df = df.rename(columns={'BuildingAd': 'Address'})

    if 'StatusCurrent' in df.columns:
        df = df.rename(columns={'StatusCurrent': 'Status'})

    if 'PermitWorkType' in df.columns:
        df = df.rename(columns={'PermitWorkType': 'Work Class'})

    if 'Alias' in df.columns:
        df = df.rename(columns={'Alias': 'Work Class'})

    if 'PermitType' in df.columns:
        df = df.rename(columns={'PermitType': 'Permit Type'})

    if 'CompletedDate' in df.columns:
        df = df.rename(columns={'CompletedDate': 'Finaled Date'})

    if 'Issued_Dat' in df.columns:
        df = df.rename(columns={'Issued_Dat': 'Issued Date'})
    elif 'IssuedDate' in df.columns:
        df = df.rename(columns={'IssuedDate': 'Issued Date'})
    elif 'Issued_Date' or 'IssuedDate' in ~df.columns:
        df['Issued Date'] = pd.to_datetime(df.iloc[:, 0], errors='coerce')

    if 'FinaledDat' in df.columns:
        df = df.rename(columns={'FinaledDat': 'Final Date'})

    if 'PermitNum' in df.columns:
        df = df.rename(columns={'PermitNum': 'Permit Number'})

    if 'Permit' in df.columns:
        df = df.rename(columns={'Permit': 'Permit Number'})

    if 'MasterPermitNum' in df.columns:
        df = df.rename(columns={'MasterPermitNum': 'Parent Permit Number'})

    if 'Descriptio' in df.columns:
        df = df.rename(columns={'Descriptio': 'Description'})

        # removes *, ", and carriage returns
        df['Description'].replace(regex=True, inplace=True, to_replace=r'\*', value=r'')
        df['Description'].replace(regex=True, inplace=True, to_replace=r'\n', value=r'')
        df['Description'].replace(regex=True, inplace=True, to_replace=r'\r', value=r'')
        df['Description'].replace(regex=True, inplace=True, to_replace=r'\"', value=r'')

    if 'OBJECTID' in df.columns:
        df.drop(columns=['OBJECTID'], inplace=True)

    if 'jobValue' in df.columns:
        df = df.rename(columns={'jobValue': 'Value Total'})
        df['Value Total'] = df['Value Total'].astype('int')
    elif 'Valuation' in df.columns:
        df = df.rename(columns={'Valuation': 'Value Total'})
        df['Value Total'] = df['Value Total'].astype('int')
    elif 'Value Total' in df.columns:
        pass

    df.dropna(subset=['Issued Date'], how='all', inplace=True)
    return df


def superior_spreadsheet_formatter(df):

    df['Issued Date'] = pd.to_datetime(df.iloc[:, 0], errors='coerce')

    df['Permit Number'] = pd.DataFrame(df.iloc[:, 1])

    df['Permit Applicant'] = pd.DataFrame(df.iloc[:, 2])
    df['Address'] = pd.DataFrame(df.iloc[:, 3])
    df['Address'] = df['Address'].str.upper()
    df['Description'] = pd.DataFrame(df.iloc[:, 6])

    # convert the permit value column
    df['Value Total'] = pd.DataFrame(df.iloc[:, 7])

    # removes *, ", and carriage returns
    df['Description'].replace(regex=True, inplace=True, to_replace=r'\*', value=r'')
    df['Description'].replace(regex=True, inplace=True, to_replace=r'\n', value=r'')
    df['Description'].replace(regex=True, inplace=True, to_replace=r'\r', value=r'')
    df['Description'].replace(regex=True, inplace=True, to_replace=r'\"', value=r'')

    # cleans up the dataframe
    df = df[['Date', 'Permit Number', 'Permit Applicant', 'Address', 'Description', 'Value Total']]

    # Address cleanup
    df['Address'] = df['Address'].str.replace('SO ', 'S ', regex=True)
    df['Address'] = df['Address'].str.replace('NO ', 'N ', regex=True)
    df['Address'] = df['Address'].str.replace('BLVE', 'BLVD', regex=True)
    df['Address'] = df['Address'].str.replace('WAT', 'WAY', regex=True)
    df['Address'] = df['Address'].str.replace('PK', 'PEAK', regex=True)
    df['Address'] = df['Address'].str.replace('#', '', regex=True)
    df['Address'] = df['Address'].str.replace('SHAVAN', 'SHAVANO', regex=True)
    df['Address'] = df['Address'].str.replace('HEARTSTONG', 'HEARTSTRONG', regex=True)
    df['Address'] = df['Address'].str.replace('GOLDENEY', 'GOLDENEYE', regex=True)
    df['Address'] = df['Address'].str.replace('TORREYS PK', 'TORREYS PEAK', regex=True)

    # drop any rows that did not convert to a datetime
    df.dropna(subset=['Issued Date'], how='all', inplace=True)
    return df


def issued_date_filter(df):
    while True:
        # create an input to select the earliest date the user wants to upload
        print('Please input the earliest date you would like (ex: 09/26/2020)')
        date = input('Date: ')
        try:
            if 'Issued Date' in df.columns:
                df['Issued Date'] = pd.to_datetime(df['Issued Date'])
                df = df[df['Issued Date'] > date]

        except TypeError:
            print('Please input date in format using month/day/year')
            continue

        return df

def database_connection(df):
    print('Establishing connection...\n')
    c_str = open('connection_string.txt', 'r').read()  # can be removed once connection string is added
    cnxn = pyodbc.connect(c_str)


    city_sql = """SELECT distinct parcel.strap, strap_idx.folio, parcel.status_cd, parcel.dor_cd, parcel.nh_cd, 
        parcel.map_id, site.str_num, site.str_pfx, site.str, site.str_sfx, site.str_sfx_dir, site.str_unit
	    FROM r_prod.dbo.parcel
        INNER JOIN r_prod.dbo.site ON parcel.strap = site.strap
        INNER JOIN r_prod.dbo.strap_idx ON parcel.strap = strap_idx.strap
        WHERE (parcel.dor_cd <> 'POSS') AND parcel.status_cd = 'A'
        AND (site.city IN (?, 'UNINCORPORATED'))"""

    permit_sql = '''SELECT distinct permit_num FROM r_prod.dbo.permit'''

    city_sql_df = pd.read_sql(city_sql, cnxn, params=[city.upper()])
    permit_sql_df = pd.read_sql(permit_sql, cnxn)

    # Takes the permit database, renames the column to Permit Number, and then merges the month's permit with permits found
    # in the database, this makes sure a permit is not double uploaded, or double valuing

    permit_sql_df.rename(columns={'permit_num': 'Permit Number'}, inplace=True)
    city_sql_df.rename(columns={'folio': 'Parcel Number'}, inplace=True)
    city_sql_df['strap'] = city_sql_df['strap'].str.rstrip()

    return permit_sql_df, city_sql_df

def address_formatter(df):
    # attempting to take our situs address, concat, and compare with the city's permit address
    # (only using active accts, no possessory interest)
    df.dropna(subset=['str_num'])
    df['str_num'] = df['str_num'].astype(int).astype(str)
    df['str_pfx'] = df['str_pfx'].fillna(np.nan).replace(np.nan, ' ', regex=True)
    df['str_pfx'] = df['str_pfx'].replace('  ', ' ', regex=True)
    df['str_pfx'] = df['str_pfx'].replace('S', ' S', regex=True)
    df['str_pfx'] = df['str_pfx'].replace('N', ' N', regex=True)
    df['str_pfx'] = df['str_pfx'].replace('E', ' E', regex=True)
    df['str_pfx'] = df['str_pfx'].replace('W', ' W', regex=True)
    df['str_sfx'] = df['str_sfx'].fillna(np.nan).replace(np.nan, ' ', regex=True)
    df['str_sfx'] = df['str_sfx'].replace('  ', '', regex=True)
    df['str_sfx'] = df['str_sfx'].replace('WAY', 'WY', regex=True)
    df['str_sfx_dir'] = df['str_sfx_dir'].fillna(np.nan).replace(np.nan, ' ', regex=True)
    df['str_sfx_dir'] = df['str_sfx_dir'].replace('  ', ' ', regex=True)
    df['str_unit'] = df['str_unit'].fillna(np.nan).replace(np.nan, '', regex=True)

    # creates a column called Address that is set up in the same format as the Superior permits table
    df['Address'] = df['str_num'] + df['str_pfx'] + df['str'] + ' ' \
                    + df['str_sfx'] + df['str_sfx_dir'] + df['str_unit']
    df['Address'] = df['Address'].str.rstrip()

    return df


# Run the file opener function
df = file_opener()

# Run the municipal chooser
city = municipal_chooser()

# Format the spreadsheet based on the type of municipality selected, different municipalities have different
# styles to format
if city == 'Superior':
    df = superior_spreadsheet_formatter(df)
elif city in ['Boulder', 'Longmont']:
    df = spreadsheet_formatter(df)

# Run issued date function
df = issued_date_filter(df)

# Create a permit dataframe and an address dataframe
permit, city_address = database_connection(df)

# Merge the queried building permits with the ones already uploaded in CAMA
df_uploaded = pd.merge(df, permit, on='Permit Number')

# Check to see if an already uploaded permit is in CAMA
df = df.loc[~df['Permit Number'].isin(df_uploaded['Permit Number'])]
df.drop_duplicates()

city_address = address_formatter(city_address)
