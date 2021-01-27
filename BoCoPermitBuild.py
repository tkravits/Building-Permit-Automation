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

            elif city is 'Lafayette':
                city = 'Lafayette'

            elif city not in ['Boulder', 'Longmont', 'Superior', 'Lafayette']:
                print('Please input a valid city or use format (ex: Boulder, Longmont)')
                continue

        except TypeError:
            print('Please input city in format using "City" (ex: Boulder, Longmont)')
            continue

        return city


def spreadsheet_formatter(df):
    if 'PIN' in df.columns:
        df = df.rename(columns={'PIN': 'Parcel Number'})  # else if named pin, rename it

    if 'Parcel #\r' in df.columns:
        df = df.rename(columns={'Parcel #\r': 'Parcel Number'})
        df['Parcel Number'] = df['Parcel Number'].str.split('\r').str[0].astype(str).str.lstrip('0')

    if 'Parcel' in df.columns:
        df = df.rename(columns={'Parcel': 'Parcel Number'})

    if 'OriginalAddress' in df.columns:
        df = df.rename(columns={'OriginalAddress': 'Address'})

    if 'Address / Legal' in df.columns:
        df = df.rename(columns={'Address / Legal': 'Address'})

    if 'BuildingAd' in df.columns:
        df = df.rename(columns={'BuildingAd': 'Address'})

    if 'StatusCurrent' in df.columns:
        df = df.rename(columns={'StatusCurrent': 'Status'})

    if 'PermitWorkType' in df.columns:
        df = df.rename(columns={'PermitWorkType': 'Work Class'})

    if 'Alias' in df.columns:
        df = df.rename(columns={'Alias': 'Work Class'})

    if 'Project Type' in df.columns:
        df = df.rename(columns={'Project Type': 'Work Class'})

    if 'PermitType' in df.columns:
        df = df.rename(columns={'PermitType': 'Permit Type'})

    if 'CompletedDate' in df.columns:
        df = df.rename(columns={'CompletedDate': 'Finaled Date'})

    if 'Issued_Dat' in df.columns:
        df = df.rename(columns={'Issued_Dat': 'Issued Date'})
    elif 'IssuedDate' in df.columns:
        df = df.rename(columns={'IssuedDate': 'Issued Date'})
    elif 'Permit Issued Date' in df.columns:
        df = df.rename(columns={'Permit Issued Date': 'Issued Date'})
    elif 'Issued_Date' or 'IssuedDate' in ~df.columns:
        df['Issued Date'] = pd.to_datetime(df.iloc[:, 0], errors='coerce')

    if 'FinaledDat' in df.columns:
        df = df.rename(columns={'FinaledDat': 'Final Date'})

    if 'PermitNum' in df.columns:
        df = df.rename(columns={'PermitNum': 'Permit Number'})
    if 'Project Number' in df.columns:
        df = df.rename(columns={'Project Number': 'Permit Number'})
    if 'Permit' in df.columns:
        df = df.rename(columns={'Permit': 'Permit Number'})

    if 'MasterPermitNum' in df.columns:
        df = df.rename(columns={'MasterPermitNum': 'Parent Permit Number'})

    if 'Descriptio' in df.columns:
        df = df.rename(columns={'Descriptio': 'Description'})
        df['Description'].replace(regex=True, inplace=True, to_replace=r'\*', value=r'')
        df['Description'].replace(regex=True, inplace=True, to_replace=r'\n', value=r'')
        df['Description'].replace(regex=True, inplace=True, to_replace=r'\r', value=r'')
        df['Description'].replace(regex=True, inplace=True, to_replace=r'\"', value=r'')
    if 'Project Description' in df.columns:
        df = df.rename(columns={'Project Description': 'Description'})
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
        df['Value Total'] = df['Value Total'].fillna(0).astype('int')
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


def permit_classifier(df):
    if 'Description' in df.columns:
        # Classifies the description into a format that CAMA can understand
        df.loc[df['Work Class'].str.contains('Temporary', case=False, na=False), 'SCOPE'] = 'ELM'
        df.loc[df['Description'].str.contains('generator', case=False, na=False), 'SCOPE'] = 'ELM'
        df.loc[df['Description'].str.contains('outlet', case=False, na=False), 'SCOPE'] = 'ELM'
        df.loc[df['Work Class'].str.contains('Construction', case=False, na=False), 'SCOPE'] = 'OTH'
        df.loc[(df['Description'].str.contains('emergency', case=False, na=False)) & (
            df['Description'].str.contains('repair', case=False, na=False)), 'SCOPE'] = 'OTH'
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
        df.loc[df['Description'].str.contains('Window', case=False, na=False), 'SCOPE'] = 'W/D'
        df.loc[(df['Work Class'].str.contains('Combo', na=False)) & (
            df['Description'].str.contains('doors', case=False, na=False)), 'SCOPE'] = 'W/D'
        df.loc[(df['Work Class'].str.contains('Remodel', case=False, na=False)), 'SCOPE'] = 'REM'
        df.loc[df['Description'].str.contains('PV', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Description'].str.contains('solar', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Description'].str.contains('photo', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Description'].str.contains('P.V.', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Description'].str.contains('photovoltaic', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Description'].str.contains('geotherm', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Description'].str.contains('flush-mounted', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[(df['Work Class'].str.contains('Combo', na=False)) & (
            df['Description'].str.contains('gas fireplace', case=False, na=False)), 'SCOPE'] = 'GFP'
        df.loc[(df['Work Class'].str.contains('Mechanical', na=False)) & (
            df['Description'].str.contains('gas fireplace', case=False, na=False)), 'SCOPE'] = 'GFP'
        df.loc[(df['Work Class'].str.contains('Mechanical', na=False)) & (
            df['Description'].str.contains('existing wood-burning', case=False, na=False)), 'SCOPE'] = 'GFP'
        df.loc[(df['Work Class'].str.contains('Mechanical', na=False)) & (
                df['Description'].str.contains('wood burning', case=False, na=False)
                & (df['Description'].str.contains('replace', case=False, na=False))), 'SCOPE'] = 'GFP'
        df.loc[df['Work Class'].str.contains('Interior', case=False, na=False) &
               df['Description'].str.contains('repair', case=False, na=False), 'SCOPE'] = 'GRP'
        df.loc[df['Work Class'].str.contains('Repair', na=False), 'SCOPE'] = 'GRP'
        df.loc[(df['Work Class'].str.contains('Interior', case=False, na=False)) & (
            df['Description'].str.contains('foundation', case=False, na=False)), 'SCOPE'] = 'SRP'
        df.loc[(df['Work Class'].str.contains('Interior', na=False)) & (
            df['Description'].str.contains('stabilization', case=False, na=False)), 'SCOPE'] = 'SRP'
        df.loc[(df['Description'].str.contains('Repair', na=False)) & (
            df['Description'].str.contains('foundation', case=False, na=False)), 'SCOPE'] = 'SRP'
        df.loc[(df['Work Class'].str.contains('Interior', na=False)) & (
            df['Description'].str.contains('structural', case=False, na=False)), 'SCOPE'] = 'SRP'
        df.loc[(df['Work Class'].str.contains('Interior', na=False)) & (
            df['Description'].str.contains('stabilize', case=False, na=False)), 'SCOPE'] = 'SRP'
        df.loc[
            (df['Work Class'].str.contains('Remodel', case=False, na=False)) & (
                df['Description'].str.contains('fire', case=False, na=False)), 'SCOPE'] = 'FRP'
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
        df.loc[df['Work Class'].str.contains('Elevator', case=False, na=False), 'SCOPE'] = 'ELE'
        df.loc[df['Work Class'].str.contains('Siding', na=False), 'SCOPE'] = 'SDG'
        df.loc[df['Work Class'].str.contains('Right', na=False), 'SCOPE'] = 'OTH'
        df.loc[(df['Work Class'].str.contains('Right', na=False)) & (
            df['Description'].str.contains('sewer', case=False, na=False)), 'SCOPE'] = 'RWSRPR'
        df.loc[df['Work Class'].str.contains('Fence', na=False), 'SCOPE'] = 'FEN'
        df.loc[df['Work Class'].str.contains('Tenant', na=False), 'SCOPE'] = 'TFN'
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
        df.loc[(df['Work Class'].str.contains('commercial', case=False, na=False)) & (
            df['Description'].str.contains('remodel', case=False, na=False)), 'SCOPE'] = 'TFN'
        df.loc[(df['Work Class'].str.contains('New', na=False)) & (
            df['Description'].str.contains('garage built', case=False, na=False)), 'SCOPE'] = 'GAR'
        df.loc[df['Work Class'].str.contains('Addition', na=False), 'SCOPE'] = 'ADD'
        df.loc[(df['Work Class'].str.contains('Addition', na=False)) & (
            df['Description'].str.contains(' deck', case=False, na=False)), 'SCOPE'] = 'DEC'
        df.loc[(df['Work Class'].str.contains('Deck', case=False, na=False)) & (
            df['Description'].str.contains('deck', case=False, na=False)), 'SCOPE'] = 'DEC'
        df.loc[(df['Work Class'].str.contains('Addition', na=False)) & (
            df['Description'].str.contains('new porch', case=False, na=False)), 'SCOPE'] = 'POR'
        df.loc[(df['Work Class'].str.contains('Addition', na=False)) & (
            df['Description'].str.contains('pergola', case=False, na=False)), 'SCOPE'] = 'POR'
        df.loc[(df['Work Class'].str.contains('Addition', na=False)) & (
            df['Description'].str.contains(' shed', case=False, na=False)), 'SCOPE'] = 'OUT'
        df.loc[df['Work Class'].str.contains('Addition and', na=False), 'SCOPE'] = 'ADD'
        df.loc[df['Work Class'].str.contains('Wireless', na=False), 'SCOPE'] = 'OTH'
        df.loc[(df['Work Class'].str.contains('Cell', case=False, na=False)), 'SCOPE'] = 'OTH'
        df.loc[df['Work Class'].str.contains('Demo', case=False, na=False), 'SCOPE'] = 'DEM'
        df.loc[(df['Work Class'].str.contains('Demo', case=False, na=False)) & (
            df['Work Class'].str.contains('interior', case=False, na=False)), 'SCOPE'] = 'REM'
        df.loc[df['Work Class'].str.contains('Sign', na=False), 'SCOPE'] = 'SGN'
        df.loc[df['Work Class'].str.contains('Fire', na=False), 'SCOPE'] = 'SPK'
        df.loc[(df['Work Class'].str.contains('Mobile Home', na=False)) & (
            df['Description'].str.contains('replacement', case=False, na=False)), 'SCOPE'] = 'MHN'
        df.loc[(df['Work Class'].str.contains('Mobile Home', na=False)) & (
            df['Description'].str.contains('new', case=False, na=False)), 'SCOPE'] = 'MHN'
        df.loc[
            (df['Work Class'].str.contains('Roofing', na=False)) & (
                df['Description'].str.contains('roof', case=False, na=False)), 'SCOPE'] = 'RRR'
        df.loc[(df['Work Class'].str.contains('Roofing', na=False)) & (
            df['Description'].str.contains('single', case=False, na=False)), 'SCOPE'] = 'RRR'
        df.loc[
            (df['Work Class'].str.contains('Roofing', na=False)) & (
                df['Description'].str.contains('SFD', case=False, na=False)), 'SCOPE'] = 'RRR'
        df.loc[(df['Work Class'].str.contains('Roofing', na=False)) & (
            df['Description'].str.contains('residential', case=False, na=False)), 'SCOPE'] = 'RRR'
        df.loc[
            (df['Work Class'].str.contains('Roofing', na=False)) & (
                df['Description'].str.contains('multi', case=False, na=False)), 'SCOPE'] = 'RRR'
        df.loc[(df['Work Class'].str.contains('Roofing', na=False)) & (
            df['Description'].str.contains('duplex', case=False, na=False)), 'SCOPE'] = 'RRR'
        df.loc[(df['Work Class'].str.contains('Roofing', na=False)) & (
            df['Description'].str.contains('re-roof', case=False, na=False)), 'SCOPE'] = 'RRR'
        df.loc[(df['Work Class'].str.contains('Roofing', na=False)) & (
            df['Description'].str.contains('re roof', case=False, na=False)), 'SCOPE'] = 'RRR'
        df.loc[(df['Work Class'].str.contains('Roofing', na=False)) & (
            df['Description'].str.contains('shingle', case=False, na=False)), 'SCOPE'] = 'RRR'
        df.loc[(df['Work Class'].str.contains('Commercial', case=False, na=False)) & (
            df['Description'].str.contains('re-roof', case=False, na=False)), 'SCOPE'] = 'CRR'
        df.loc[df['Description'].str.contains('valve', case=False, na=False), 'SCOPE'] = 'OTH'
        df.loc[df['Description'].str.contains('pipe', case=False, na=False), 'SCOPE'] = 'OTH'
        df.loc[df['Description'].str.contains('electric', case=False, na=False), 'SCOPE'] = 'ELM'
        df.loc[df['Description'].str.contains('electrical', case=False, na=False), 'SCOPE'] = 'ELM'
        df.loc[df['Description'].str.contains('wire', case=False, na=False), 'SCOPE'] = 'ELM'
        df.loc[df['Description'].str.contains('boiler', case=False, na=False), 'SCOPE'] = 'OTH'
        df.loc[df['Description'].str.contains('ductless', case=False, na=False), 'SCOPE'] = 'HTG'
        df.loc[df['Description'].str.contains('furnace', case=False, na=False), 'SCOPE'] = 'HTG'
        df.loc[df['Description'].str.contains('heater', case=False, na=False), 'SCOPE'] = 'OTH'
        df.loc[df['Description'].str.contains('/AC', case=False, na=False), 'SCOPE'] = 'AIR'
        df.loc[df['Description'].str.contains('mini split', case=False, na=False), 'SCOPE'] = 'AIR'
        df.loc[df['Description'].str.contains('cooler', case=False, na=False), 'SCOPE'] = 'AIR'
        df.loc[df['Description'].str.contains(' AC ', case=False, na=False), 'SCOPE'] = 'AIR'
        df.loc[df['Description'].str.contains('AC ', case=False, na=False), 'SCOPE'] = 'AIR'
        df.loc[df['Description'].str.contains(' AC', na=False), 'SCOPE'] = 'AIR'
        df.loc[df['Description'].str.contains('A/C', case=False, na=False), 'SCOPE'] = 'AIR'
        df.loc[df['Description'].str.contains('air condition', case=False, na=False), 'SCOPE'] = 'AIR'

        df.loc[df['Description'].str.contains(' shed ', case=False, na=False), 'SCOPE'] = 'OUT'
        df.loc[(df['Description'].str.contains('Roof', case=False, na=False)), 'SCOPE'] = 'RRR'
        df.loc[(df['Description'].str.contains('asphalt', na=False)) & (
            df['Description'].str.contains('replace', case=False, na=False)), 'SCOPE'] = 'RRR'
        df.loc[(df['Description'].str.contains('reroof', case=False, na=False)), 'SCOPE'] = 'RRR'
        df.loc[(df['Description'].str.contains('shingles', case=False, na=False)), 'SCOPE'] = 'RRR'
        df.loc[(df['Description'].str.contains('re-roof', case=False, na=False)), 'SCOPE'] = 'RRR'
        df.loc[(df['Description'].str.contains('owens', case=False, na=False)), 'SCOPE'] = 'RRR'
        df.loc[(df['Description'].str.contains('TPO', case=False, na=False)), 'SCOPE'] = 'RRR'
        df.loc[(df['Description'].str.contains('R&R', case=False, na=False)), 'SCOPE'] = 'RRR'
        df.loc[df['Description'].str.contains('patio', case=False, na=False), 'SCOPE'] = 'POR'
        df.loc[df['Description'].str.contains('porch', case=False, na=False), 'SCOPE'] = 'POR'
        df.loc[df['Description'].str.contains('pergola', case=False, na=False), 'SCOPE'] = 'POR'
        df.loc[(df['Work Class'].str.contains('commercial', case=False, na=False)) & (
            df['Work Class'].str.contains('roof', case=False, na=False)), 'SCOPE'] = 'CRR'
        df.loc[df['Description'].str.contains('PV', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Description'].str.contains('solar', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Description'].str.contains('photo', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Description'].str.contains('P.V.', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Description'].str.contains('photovoltaic', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Description'].str.contains('geotherm', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Description'].str.contains('flush-mounted', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Work Class'].str.contains('PV', na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Work Class'].str.contains('PV', na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Description'].str.contains('Fence', case=False, na=False), 'SCOPE'] = 'FEN'
        df.loc[df['Description'].str.contains('privacy', case=False, na=False), 'SCOPE'] = 'FEN'
        df.loc[df['Work Class'].str.contains('fence', case=False, na=False), 'SCOPE'] = 'FEN'
        df.loc[df['Description'].str.contains('Tenant', case=False, na=False), 'SCOPE'] = 'TFN'
        df.loc[df['Description'].str.contains('sewer', case=False, na=False), 'SCOPE'] = 'RWSRPR'
        df.loc[df['Description'].str.contains('finished basement', case=False, na=False), 'SCOPE'] = 'BFN'
        df.loc[df['Description'].str.contains('basement finish', case=False, na=False), 'SCOPE'] = 'BFN'
        df.loc[df['Description'].str.contains('basement remodel', case=False, na=False), 'SCOPE'] = 'BFN'
        df.loc[df['Description'].str.contains('BSMT finish', case=False, na=False), 'SCOPE'] = 'BFN'
        df.loc[df['Description'].str.contains('basement bathroom', case=False, na=False), 'SCOPE'] = 'BFN'
        df.loc[df['Description'].str.contains('bathroom remodel', case=False, na=False), 'SCOPE'] = 'BTH'
        df.loc[df['Description'].str.contains('bath remodel', case=False, na=False), 'SCOPE'] = 'BTH'
        df.loc[df['Description'].str.contains('tenant', case=False, na=False), 'SCOPE'] = 'TFN'
        df.loc[df['Work Class'].str.contains('tenant', case=False, na=False), 'SCOPE'] = 'TFN'
        df.loc[(df['Work Class'].str.contains('interior', case=False, na=False) &
                df['Work Class'].str.contains('commercial', case=False, na=False)), 'SCOPE'] = 'TFN'
        df.loc[(df['Work Class'].str.contains('New Construction', na=False)), 'SCOPE'] = 'NEW'
        df.loc[df['Description'].str.contains('Structural', case=False, na=False) & (
            df['Description'].str.contains('repair', case=False, na=False)), 'SCOPE'] = 'SRP'
        df.loc[~(df['Work Class'].str.contains('Combo', case=False, na=False)) & (
            df['Description'].str.contains('garage', case=False, na=False)), 'SCOPE'] = 'GAR'
        df.loc[df['Description'].str.contains('siding', case=False, na=False), 'SCOPE'] = 'SDG'
        df.loc[df['Work Class'].str.contains('Addition', na=False), 'SCOPE'] = 'ADD'
        df.loc[df['Description'].str.contains('pool', case=False, na=False), 'SCOPE'] = 'POL'
        df.loc[df['Description'].str.contains('Wireless', na=False), 'SCOPE'] = 'OTH'
        df.loc[df['Description'].str.contains('Water line', case=False, na=False), 'SCOPE'] = 'OTH'
        df.loc[df['Description'].str.contains('Gas line', case=False, na=False), 'SCOPE'] = 'OTH'
        df.loc[(df['Description'].str.contains('gas', case=False, na=False)) & (
            df['Description'].str.contains('repair', case=False, na=False)), 'SCOPE'] = 'OTH'
        df.loc[df['Description'].str.contains('radon', case=False, na=False), 'SCOPE'] = 'OTH'
        df.loc[df['Work Class'].str.contains('Sign', case=False, na=False), 'SCOPE'] = 'SGN'
        df.loc[df['Description'].str.contains('Fire', na=False), 'SCOPE'] = 'SPK'
        df.loc[(df['Work Class'].str.contains('New', na=False)) & (
            df['Description'].str.contains('mobile home', case=False, na=False)), 'SCOPE'] = 'MHN'
        df['SCOPE'] = df['SCOPE'].fillna('OTH')


    else:
        print('Please provide a permit description column titled "Description"')

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


def address_and_parcel_merge(df):
    if city == 'Longmont':
        # merges the CAMA accounts database (strap) with the created Address field with the city's permit spreadsheet
        df['Address'] = df['Address'].str.replace(' UNIT ', ' ')
        df['Address'] = df['Address'].str.replace(' STE ', ' ')
        df['Address'] = df['Address'].str.replace(' MB ', ' ')
        df = df.merge(city_address, on='Address', how='left')
        df.drop(columns=['Parcel Number_y'])
        df = df.rename(columns={'Parcel Number_x': 'Parcel Number'})
        df_merge_perm = df.merge(city_address, on='Parcel Number', how='left')
        df_merge_perm['strap_final'] = df_merge_perm['strap_x'].where(
            df_merge_perm['strap_x'].notnull(), df_merge_perm['strap_y'])
        df_merge_perm.drop_duplicates(subset=['Permit Number'], keep='last', inplace=True)

    elif city in ['Boulder', 'Superior']:
        df = df.merge(city_address, on='Address', how='left')
        df.drop(columns=['Parcel Number_y'])
        df = df.rename(columns={'Parcel Number_x': 'Parcel Number'})
        df_merge_perm = df.merge(city_address, on='Parcel Number', how='left')
        df_merge_perm['strap_final'] = df_merge_perm['strap_x'].where(
        df_merge_perm['strap_x'].notnull(), df_merge_perm['strap_y'])
        df_merge_perm.drop_duplicates(subset=['Permit Number'], keep='last', inplace=True)

    elif city == 'Lafayette':
        df['Address'] = df['Address'].str.split('.').str[0]
        df = df.merge(city_address, on='Address', how='left')
        df.drop(columns=['Parcel Number_y'])
        df = df.rename(columns={'Parcel Number_x': 'Parcel Number'})
        df_merge_perm = df.merge(city_address, on='Parcel Number', how='left')
        df_merge_perm['strap_final'] = df_merge_perm['strap_x'].where(
            df_merge_perm['strap_x'].notnull(), df_merge_perm['strap_y'])
        df_merge_perm.drop_duplicates(subset=['Permit Number'], keep='last', inplace=True)

        # takes the unmerged addresses and makes a spreadsheet to be checked by hand
    df_unmerged_addresses = df_merge_perm.loc[df_merge_perm['strap_final'].isna()]
    df_merge_perm.dropna(subset=['strap_final'], inplace=True)
    df_unmerged_addresses.to_excel('HandEnter_' + city + '_permits_12_16.xlsx', index=False)

    return df, df_merge_perm, df_unmerged_addresses


def final_cleanup_and_export(df):
    df['strap'] = df['strap_final'].str.rstrip()
    df.rename(columns={'nh_cd_y': 'nh_cd'}, inplace=True)
    df.rename(columns={'dor_cd_y': 'dor_cd'}, inplace=True)
    df.rename(columns={'map_id_y': 'map_id'}, inplace=True)
    df.rename(columns={'str_num_y': 'str_num'}, inplace=True)
    df.rename(columns={'str_pfx_y': 'str_pfx'}, inplace=True)
    df.rename(columns={'str_y': 'str'}, inplace=True)
    df.rename(columns={'str_sfx_y': 'str_sfx'}, inplace=True)
    df.rename(columns={'str_unit_y': 'str_unit'}, inplace=True)
    # create spreadsheet for app.
    print("Please name the exported spreadsheet for the Appraiser staff")
    if city == 'Longmont':
        df = df[["Permit Number", "strap", "Description", "str_num", "str_pfx",
             "str", "str_sfx", "str_unit", "Value Total", "Issued Date", "Final Date", "SQFT", "SCOPE",
             "nh_cd", "dor_cd", "map_id"]]
    elif city in ['Boulder', 'Superior']:
        df = df[["Permit Number", "strap", "Description", "str_num", "str_pfx",
                 "str", "str_sfx", "str_unit", "Value Total", "Issued Date", "Final Date", "SCOPE",
                 "nh_cd", "dor_cd", "map_id"]]
    elif city == 'Lafayette':
        df = df[["Permit Number", "strap", "Description", "str_num", "str_pfx",
                 "str", "str_sfx", "str_unit", "Value Total", "Issued Date", "SCOPE",
                 "nh_cd", "dor_cd", "map_id"]]
    df.to_excel(input() + "_" + city +"Permits_Appraiser.xlsx", index=False)

    if city == 'Longmont':
        df = df[["Permit Number", "strap", "Description", "str_num", "str_pfx",
            "str", "str_sfx", "str_unit", "Value Total", "Issued Date", "Final Date", "SQFT", "SCOPE"]]

    elif city in ['Boulder', 'Superior']:
        df = df[["Permit Number", "strap", "Description", "str_num", "str_pfx",
            "str", "str_sfx", "str_unit", "Value Total", "Issued Date", "Final Date", "SCOPE"]]

    elif city == 'Lafayette':
        df = df[["Permit Number", "strap", "Description", "str_num", "str_pfx",
            "str", "str_sfx", "str_unit", "Value Total", "Issued Date", "SCOPE"]]

    # export final data to a txt file to be imported
    header = ''  # first, create the header
    for s in list(df):
        header += '"' + s + '"|'
    header = header[:-1]  # to take the final | off, as it's unnecessary
    # take the values of each column and add double quotes
    if city == 'Longmont':
        df = df[["Permit Number", "strap", "Description", "str_num", "str_pfx",
            "str", "str_sfx", "str_unit", "Value Total", "Issued Date", "Final Date", "SQFT", "SCOPE"]]

    elif city in ['Boulder', 'Superior']:
        df = df[["Permit Number", "strap", "Description", "str_num", "str_pfx",
            "str", "str_sfx", "str_unit", "Value Total", "Issued Date", "Final Date", "SCOPE"]]

    elif city == 'Lafayette':
        df = df[["Permit Number", "strap", "Description", "str_num", "str_pfx",
            "str", "str_sfx", "str_unit", "Value Total", "Issued Date", "SCOPE"]]

#    df.update(df[["Permit Number", "strap", "Description", "str_num", "str_pfx",
#                  "str", "str_sfx", "str_unit", "Value Total", "Issued Date", "Final Date", "SQFT", "SCOPE"]].applymap('"{}"'.format))

    # now, save to a text file with a | separator
    print("Please name the txt file that will be uploaded to CAMA")
    np.savetxt(input() + city +'_permits.txt', df.values, fmt='%s', header=header, comments='', delimiter='|')

    return df

# Run the file opener function
df = file_opener()

# Run the municipal chooser
city = municipal_chooser()

# Format the spreadsheet based on the type of municipality selected, different municipalities have different
# styles to format
if city == 'Superior':
    df = superior_spreadsheet_formatter(df)
elif city in ['Boulder', 'Longmont', 'Lafayette']:
    df = spreadsheet_formatter(df)

# Run issued date function
df = issued_date_filter(df)

# Classify the permits using the three letter scope code
df = permit_classifier(df)

# Create a permit dataframe and an address dataframe
permit, city_address = database_connection(df)

# Merge the queried building permits with the ones already uploaded in CAMA
df_uploaded = pd.merge(df, permit, on='Permit Number')

# Check to see if an already uploaded permit is in CAMA
df = df.loc[~df['Permit Number'].isin(df_uploaded['Permit Number'])]
df.drop_duplicates()

city_address = address_formatter(city_address)

df, df_merge_perm, df_unmerged_addresses = address_and_parcel_merge(df)

final_cleanup_and_export(df_merge_perm)