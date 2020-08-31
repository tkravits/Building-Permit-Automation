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
CurrentDate = pd.Timestamp.today()
SetDate = (CurrentDate - pd.DateOffset(months=1)).strftime("%B%Y")

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

df = df.dropna(how='all')

df['Permit_No'] = df.filter(regex='PERMIT #', axis=1)