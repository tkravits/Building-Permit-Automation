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
            print('Please rerun program and input date in format using month/day/year')
            continue

        return df


df = file_opener()

# Run the spreadsheet formatter
df = spreadsheet_formatter(df)

# Run issued date function
#df = issued_date_filter(df)