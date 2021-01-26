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
    # g = df.groupby('Permit Number').Address
    # pd.concat([g.apply(list), g.count()], axis=1, keys=['Permit Number'])
    # Data is mostly clean but need to figure out how to get description column to fill in the correct location
    # df = df.groupby(['Permit Number'])['Description'].apply(','.join).reset_index()
    # df['Permit Number'] = df['Permit Number'].ffill()
    # df = df.groupby(["Permit Number", "Permit Code", "Permit Type", "Parcel Number", 'Address', 'Issued Date',
    #               'Permit Value', 'Contractor'])['Description'].cummax().reset_index()
    return df

df = file_opener()
df = louisville_spreadsheet_formatter(df)
# This is my attempt at taking the PDF and using pdfplumber to parse out into a dataframe. In the essence of time
# I opted to use the old system of Able2Extract and put it in an excel format as seen above
# df = []
# with pdfplumber.open(r"C:\Users\tkravits\Github\Building-Permit-Automation\Louisville_December2020.pdf") as pdf:
#     for page in pdf.pages:
#         text = page.extract_text()
#         df.append(text)
#         str1 = ''.join(df)
# #        core_pat = re.compile(r"CONTACTS", re.DOTALL)
# #        core = re.search(core_pat, str1).group(0)
#
# # converts the list into a dataframe
# df = pd.DataFrame(df)
#
# # Use negative look behind basically anything after "Concession Amt:" will be pulled
# df['Concession Amt'] = df.apply(''.join, axis=1).str.extract('((?<=80027 ).*)')
#
# # TODO - need to use regex to remove the header and footers of the total pdf to make one large list
# # TODO - then I need to group the permits by each new line (aka the permit info and the description)