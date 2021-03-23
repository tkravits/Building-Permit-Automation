import pdfplumber
import re
import pandas as pd
import pyodbc
import numpy as np
from tkinter import Tk
from tkinter.filedialog import askopenfilename
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


def louisville_spreadsheet_formatter(df):
    df.columns = ["Permit Number", "Permit Code", "Permit Type", "Parcel Number", 'Address', 'Issued Date',
                  'Permit Value', 'Contractor']
    # using regex to do a negative lookbehind '?<=' to capture all text .* behind 'Description: ', '[]' is an either/or,
    # need to group the lookbehind and the capture all text in ()
    df['Description'] = df['Permit Number'].str.extract('((?<=[dD]escription: ).*)')
    # using regex to replace Description with nan, ^ looks for Description at the beginning on a string
    # then looks for 1 or more matches (+), | looks for all possible matches
    df['Permit Number'] = df['Permit Number'].replace('(^[dD]escription:)+', np.nan, regex=True)
    df['Permit Number'] = df['Permit Number'].replace('(^[^(MEP|MISC|TEMP|COM|RES)])+', np.nan, regex=True)
    # Creates two masks, mask is the column that will change positions, fmask is going to be the column that stays the same
    mask = df['Description'].notnull()
    fmask = (df['Permit Number'].notnull() & df['Description'].isnull())
    # Create two masking one representing the rows where the current Description value is now.
    # And, the second mask puts True on the first record where you want the Description value to move too.
    # Group on the first mask with cumsum and put that current value on all records, then use the second mask with where
    df = df.assign(Description=df.groupby(mask[::-1].cumsum())['Description'].transform(lambda x: x.iloc[-1]).where(fmask))
    df = df.dropna(subset=['Permit Number'])
    return df

df = file_opener()
df = louisville_spreadsheet_formatter(df)
