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
            df = pd.read_csv(filename, sep=",", error_bad_lines=False, index_col=False, encoding="utf-8",
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

            elif city is 'Louisville':
                city = 'Louisville'

            elif city is 'Unincorporated':
                city = 'Unincorporated'

            elif city is 'Erie':
                city = 'Erie'

            elif city not in ['Boulder', 'Longmont', 'Superior', 'Lafayette', 'Louisville', 'Unincorporated', 'Erie']:
                print('Please choose a municipality from this list: '
                      'Boulder, Longmont, Superior, Lafayette, Louisville, Unincorporated, Erie')
                continue

        except TypeError:
            print('Please input city in format using "City" (ex: Boulder, Longmont)')
            continue

        return city


def spreadsheet_formatter(df):
    df.columns = df.columns.str.strip()
    cleanup = df.columns
    df = df.replace({r'\r': ''}, regex=True)
    df[cleanup] = df[cleanup].replace('[\$,]', '', regex = True)
    if 'PIN' in df.columns:
        df = df.rename(columns={'PIN': 'Parcel Number'})  # else if named pin, rename it
    if 'Parcel #\r' in df.columns:
        df = df.rename(columns={'Parcel #\r': 'Parcel Number'})
        df['Parcel Number'] = df['Parcel Number'].str.split('\r').str[0].astype(str).str.lstrip('0')
    if 'Parcel #' in df.columns:
        df = df.rename(columns={'Parcel #': 'Parcel Number'})
    if 'Parcel' in df.columns:
        df = df.rename(columns={'Parcel': 'Parcel Number'})
    if 'Parcel Number' in df.columns:
        df['Parcel Number'] = df['Parcel Number'].astype(str)
        df['Parcel Number'] = df['Parcel Number'].str.lstrip('0')

    if 'OriginalAddress' in df.columns:
        df = df.rename(columns={'OriginalAddress': 'Address'})
    if 'Address / Legal' in df.columns:
        df = df.rename(columns={'Address / Legal': 'Address'})
    if 'BuildingAd' in df.columns:
        df = df.rename(columns={'BuildingAd': 'Address'})
    if {'Full Address', 'Address'}.issubset(df.columns):
        df.drop(columns=['Address'], inplace=True)
        df = df.rename(columns={'Full Address': 'Address'})
    if 'Address' in df.columns:
        df['Address'] = df['Address'].str.upper()

    if 'StatusCurrent' in df.columns:
        df = df.rename(columns={'StatusCurrent': 'Status'})

    if 'PermitWorkType' in df.columns:
        df = df.rename(columns={'PermitWorkType': 'Work Class'})
    elif 'Alias' in df.columns:
        df = df.rename(columns={'Alias': 'Work Class'})
    elif 'Project Type' in df.columns:
        df = df.rename(columns={'Project Type': 'Work Class'})

    if 'PermitType' in df.columns:
        df = df.rename(columns={'PermitType': 'Permit Type'})

    if 'CompletedDate' in df.columns:
        df = df.rename(columns={'CompletedDate': 'Finaled Date'})

    if 'Issued_Dat' in df.columns:
        df = df.rename(columns={'Issued_Dat': 'Issued Date'})
    if 'IssuedDate' in df.columns:
        df = df.rename(columns={'IssuedDate': 'Issued Date'})
    if 'Issue Date' in df.columns:
        df = df.rename(columns={'Issue Date': 'Issued Date'})
    if 'Permit Issued Date' in df.columns:
        df = df.rename(columns={'Permit Issued Date': 'Issued Date'})
    if 'Date Issued' in df.columns:
        df = df.rename(columns={'Date Issued': 'Issued Date'})

    if 'FinaledDat' in df.columns:
        df = df.rename(columns={'FinaledDat': 'Final Date'})

    if 'PermitNum' in df.columns:
        df = df.rename(columns={'PermitNum': 'Permit Number'})
    if 'Project Number' in df.columns:
        df = df.rename(columns={'Project Number': 'Permit Number'})
    if 'Permit' in df.columns:
        df = df.rename(columns={'Permit': 'Permit Number'})
    if 'Permit #' in df.columns:
        df = df.rename(columns={'Permit #': 'Permit Number'})
    df['Permit Number'] = df['Permit Number'].astype(str)

    if 'MasterPermitNum' in df.columns:
        df = df.rename(columns={'MasterPermitNum': 'Parent Permit Number'})

    if 'Descriptio' in df.columns:
        df = df.rename(columns={'Descriptio': 'Description'})
        df['Description'].replace(regex=True, inplace=True, to_replace=r'\*', value=r'')
        df['Description'].replace(regex=True, inplace=True, to_replace=r'\n', value=r'')
        df['Description'].replace(regex=True, inplace=True, to_replace=r'\r', value=r'')
        df['Description'].replace(regex=True, inplace=True, to_replace=r'\"', value=r'')
    if 'Description' in df.columns:
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
    if 'Type of Permit' in df.columns:
        df = df.rename(columns={'Type of Permit': 'Description'})
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
    if 'Construction Value' in df.columns:
        df = df.rename(columns={'Construction Value': 'Value Total'})
        df['Value Total'] = df['Value Total'].astype('int')
    if 'Valuation' in df.columns:
        df = df.rename(columns={'Valuation': 'Value Total'})
        df['Value Total'] = df['Value Total'].fillna(0).astype('int')
    if 'EstProjectCost' in df.columns:
        df = df.rename(columns={'EstProjectCost': 'Value Total'})
        df['Value Total'] = df['Value Total'].astype('float').fillna(0).astype('int')
    if 'Value Total' in df.columns:
        pass

    df.dropna(subset=['Issued Date'], how='all', inplace=True)
    return df


def superior_spreadsheet_formatter(df):
    df.columns = df.columns.str.strip()
    df['Issued Date'] = pd.to_datetime(df.iloc[:, 0], errors='coerce')

    df['Permit Number'] = pd.DataFrame(df.iloc[:, 1])

    df['Permit Applicant'] = pd.DataFrame(df.iloc[:, 2])
    df['Address'] = pd.DataFrame(df.iloc[:, 3])
    df['Address'] = pd.DataFrame(df['Address'].str.upper())
    df['Description'] = pd.DataFrame(df.iloc[:, 6])

    # convert the permit value column
    df['Value Total'] = pd.DataFrame(df.iloc[:, 7])

    # removes *, ", and carriage returns
    df['Description'].replace(regex=True, inplace=True, to_replace=r'\*', value=r'')
    df['Description'].replace(regex=True, inplace=True, to_replace=r'\n', value=r'')
    df['Description'].replace(regex=True, inplace=True, to_replace=r'\r', value=r'')
    df['Description'].replace(regex=True, inplace=True, to_replace=r'\"', value=r'')

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
    df['Value Total'] = df['Value Total'].astype(int)
    df['Permit Number'] = df['Permit Number'].astype(str)
    df['Parcel Number'] = df['Parcel Number'].astype(str)
    # cleans up the dataframe
    df = df[['Issued Date', 'Permit Number', 'Address', 'Description', 'Value Total']]
    return df


def louisville_spreadsheet_formatter(df):
    df.columns = ["Permit Number", "Permit Code", "Work Class", "Parcel Number", 'Address', 'Issued Date',
                  'Value Total', 'Contractor']
    df.columns = df.columns.str.strip()
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
    df = df.dropna(subset=['Permit Number', 'Issued Date'])
    df = df.drop(['Contractor', 'Permit Code'], axis=1)
    df['Permit Number'] = df['Permit Number'].astype(str)
    df['Parcel Number'] = df['Parcel Number'].astype(str)
    df['Value Total'] = df['Value Total'].astype(int)
    # removes *, ", and carriage returns
    df['Description'].replace(regex=True, inplace=True, to_replace=r'\*', value=r'')
    df['Description'].replace(regex=True, inplace=True, to_replace=r'\n', value=r'')
    df['Description'].replace(regex=True, inplace=True, to_replace=r'\r', value=r'')
    df['Description'].replace(regex=True, inplace=True, to_replace=r'\"', value=r'')
    return df


def erie_spreadsheet_formatter(df):
    df.columns = df.columns.str.strip()
    df['Address_final'] = df['Address'].str.extract(r'(.*(?=ERIE|Erie))')
    df = df.drop(['Address'], axis=1)
    df.rename(columns={'Address_final': 'Address'}, inplace=True)
    df['Permit Number'] = df['Permit Number'].astype(str)
    df['Parcel Number'] = df['Parcel Number'].astype(str)

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
        df.loc[df['Description'].str.contains('PV', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Description'].str.contains('solar', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Description'].str.contains('photo', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Description'].str.contains('P.V.', case=False, na=False), 'SCOPE'] = 'ENR'
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
        df.loc[df['Description'].str.contains('bath remodel', case=False, na=False), 'SCOPE'] = 'BTH'
        df.loc[df['Description'].str.contains('tenant', case=False, na=False), 'SCOPE'] = 'TFN'
        df.loc[df['Work Class'].str.contains('tenant', case=False, na=False), 'SCOPE'] = 'TFN'
        df.loc[(df['Work Class'].str.contains('interior', case=False, na=False) &
                df['Work Class'].str.contains('commercial', case=False, na=False)), 'SCOPE'] = 'TFN'
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
        df.loc[df['Description'].str.contains('photovoltaic', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Description'].str.contains('geotherm', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Description'].str.contains('flush-mounted', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Description'].str.contains('wood fireplace', case=False, na=False), 'SCOPE'] = 'WFP'
        df.loc[df['Description'].str.contains('wood stove', case=False, na=False), 'SCOPE'] = 'WFP'
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
        df.loc[(df['Work Class'].str.contains('Remodel', case=False, na=False)) & (
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
        df.loc[(df['Work Class'].str.contains('Interior', case=False, na=False) & (
            df['Work Class'].str.contains('remodel', case=False, na=False) &
            (df['Work Class'].str.contains('commercial', case=False, na=False)))), 'SCOPE'] = 'TFN'
        df.loc[(df['Work Class'].str.contains('New Construction', case=False, na=False)), 'SCOPE'] = 'NEW'
        df.loc[(df['Work Class'].str.contains('New', case=False, na=False)), 'SCOPE'] = 'NEW'
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
        df.loc[(df['Work Class'].str.contains('commercial', case=False, na=False)) & (
            df['Work Class'].str.contains('roof', case=False, na=False)), 'SCOPE'] = 'CRR'
        df['SCOPE'] = df['SCOPE'].fillna('OTH')


    else:
        print('Please provide a permit description column titled "Description"')

    return df


def unincorp_permit_classifier(df):
    if 'Description' in df.columns:
        # Classifies the description into a format that CAMA can understand
        df.loc[df['Description'].str.contains('valve', case=False, na=False), 'SCOPE'] = 'OTH'
        df.loc[df['Description'].str.contains('pipe', case=False, na=False), 'SCOPE'] = 'OTH'
        df.loc[df['Description'].str.contains('boiler', case=False, na=False), 'SCOPE'] = 'OTH'
        df.loc[df['Description'].str.contains('ductless', case=False, na=False), 'SCOPE'] = 'HTG'
        df.loc[df['Description'].str.contains('furnace', case=False, na=False), 'SCOPE'] = 'HTG'
        df.loc[df['Description'].str.contains('heater', case=False, na=False), 'SCOPE'] = 'OTH'
        df.loc[df['Description'].str.contains('Wireless', na=False), 'SCOPE'] = 'OTH'
        df.loc[df['Description'].str.contains('Water line', case=False, na=False), 'SCOPE'] = 'OTH'
        df.loc[df['Description'].str.contains('Gas line', case=False, na=False), 'SCOPE'] = 'OTH'
        df.loc[(df['Description'].str.contains('gas', case=False, na=False)) & (
            df['Description'].str.contains('repair', case=False, na=False)), 'SCOPE'] = 'OTH'
        df.loc[df['Description'].str.contains('radon', case=False, na=False), 'SCOPE'] = 'OTH'
        df.loc[df['Description'].str.contains('generator', case=False, na=False), 'SCOPE'] = 'ELM'
        df.loc[df['Description'].str.contains('outlet', case=False, na=False), 'SCOPE'] = 'ELM'
        df.loc[(df['Description'].str.contains('emergency', case=False, na=False)) & (
            df['Description'].str.contains('repair', case=False, na=False)), 'SCOPE'] = 'OTH'
        df.loc[df['Description'].str.contains('RTU', case=False, na=False), 'SCOPE'] = 'HTG'
        df.loc[df['Description'].str.contains('RTUs', case=False, na=False), 'SCOPE'] = 'HTG'
        df.loc[df['Description'].str.contains('Mechanical', na=False), 'SCOPE'] = 'ELM'
        df.loc[df['Description'].str.contains('Electrical', case=False, na=False), 'SCOPE'] = 'ELM'
        df.loc[df['Description'].str.contains('electric', case=False, na=False), 'SCOPE'] = 'ELM'
        df.loc[df['Description'].str.contains('electrical', case=False, na=False), 'SCOPE'] = 'ELM'
        df.loc[df['Description'].str.contains('wire', case=False, na=False), 'SCOPE'] = 'ELM'
        df.loc[(df['Description'].str.contains('amp', case=False, na=False)) & (
            df['Description'].str.contains('service', case=False, na=False)), 'SCOPE'] = 'ELM'
        df.loc[(df['Description'].str.contains('meter', case=False, na=False)) & (
            df['Description'].str.contains('amp', case=False, na=False)), 'SCOPE'] = 'ELM'
        df.loc[df['Description'].str.contains(' amp ', case=False, na=False), 'SCOPE'] = 'ELM'
        df.loc[df['Description'].str.contains('Roofing', na=False), 'SCOPE'] = 'RRR'
        df.loc[df['Description'].str.contains('heat', case=False, na=False), 'SCOPE'] = 'OTH'
        df.loc[df['Description'].str.contains('boiler', case=False, na=False), 'SCOPE'] = 'OTH'
        df.loc[df['Description'].str.contains('Wireless', na=False), 'SCOPE'] = 'OTH'
        df.loc[(df['Description'].str.contains('Cell', case=False, na=False)), 'SCOPE'] = 'OTH'
        df.loc[df['Description'].str.contains('ductless', case=False, na=False), 'SCOPE'] = 'HTG'
        df.loc[df['Description'].str.contains('furnace', case=False, na=False), 'SCOPE'] = 'HTG'
        df.loc[df['Description'].str.contains('heater', case=False, na=False), 'SCOPE'] = 'OTH'
        df.loc[df['Description'].str.contains('Window', case=False, na=False), 'SCOPE'] = 'W/D'
        df.loc[df['Description'].str.contains('doors', case=False, na=False), 'SCOPE'] = 'W/D'
        df.loc[df['Description'].str.contains('PV', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Description'].str.contains('geotherm', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Description'].str.contains('flush-mounted', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Description'].str.contains('wood fireplace', case=False, na=False), 'SCOPE'] = 'WFP'
        df.loc[df['Description'].str.contains('wood stove', case=False, na=False), 'SCOPE'] = 'WFP'
        df.loc[df['Description'].str.contains('gas fireplace', case=False, na=False), 'SCOPE'] = 'GFP'
        df.loc[df['Description'].str.contains('existing wood-burning', case=False, na=False), 'SCOPE'] = 'GFP'
        df.loc[(df['Description'].str.contains('wood burning', case=False, na=False)
                & (df['Description'].str.contains('replace', case=False, na=False))), 'SCOPE'] = 'GFP'
        df.loc[df['Description'].str.contains('Interior', case=False, na=False) &
               df['Description'].str.contains('repair', case=False, na=False), 'SCOPE'] = 'GRP'
        df.loc[df['Description'].str.contains('Repair', na=False), 'SCOPE'] = 'GRP'
        df.loc[(df['Description'].str.contains('Interior', case=False, na=False)) & (
            df['Description'].str.contains('foundation', case=False, na=False)), 'SCOPE'] = 'SRP'
        df.loc[(df['Description'].str.contains('Interior', na=False)) & (
            df['Description'].str.contains('stabilization', case=False, na=False)), 'SCOPE'] = 'SRP'
        df.loc[(df['Description'].str.contains('Repair', na=False)) & (
            df['Description'].str.contains('foundation', case=False, na=False)), 'SCOPE'] = 'SRP'
        df.loc[(df['Description'].str.contains('Interior', na=False)) & (
            df['Description'].str.contains('structural', case=False, na=False)), 'SCOPE'] = 'SRP'
        df.loc[(df['Description'].str.contains('Interior', na=False)) & (
            df['Description'].str.contains('stabilize', case=False, na=False)), 'SCOPE'] = 'SRP'
        df.loc[(df['Description'].str.contains('Remodel', case=False, na=False)) & (
                df['Description'].str.contains('fire', case=False, na=False)), 'SCOPE'] = 'FRP'
        df.loc[df['Description'].str.contains('gas fireplace', case=False, na=False), 'SCOPE'] = 'GFP'
        df.loc[df['Description'].str.contains('gas log', case=False, na=False), 'SCOPE'] = 'GFP'
        df.loc[df['Description'].str.contains('Elevator', case=False, na=False), 'SCOPE'] = 'ELE'
        df.loc[df['Description'].str.contains('Siding', na=False), 'SCOPE'] = 'SDG'
        df.loc[(df['Description'].str.contains('Right', na=False)) & (
            df['Description'].str.contains('sewer', case=False, na=False)), 'SCOPE'] = 'RWSRPR'
        df.loc[df['Description'].str.contains('Fence', case=False, na=False), 'SCOPE'] = 'FEN'
        df.loc[df['Description'].str.contains('Tenant', na=False), 'SCOPE'] = 'TFN'
        df.loc[(df['Description'].str.contains('Remodel', case=False, na=False)) & (
            df['Description'].str.contains('finished basement', case=False, na=False)), 'SCOPE'] = 'BFN'
        df.loc[(df['Description'].str.contains('build out', case=False, na=False)) & (
            df['Description'].str.contains('basement', case=False, na=False)), 'SCOPE'] = 'BFN'
        df.loc[(df['Description'].str.contains('Remodel', case=False, na=False)) & (
            df['Description'].str.contains('basement finish', case=False, na=False)), 'SCOPE'] = 'BFN'
        df.loc[(df['Description'].str.contains('Remodel', case=False, na=False)) & (
            df['Description'].str.contains('basement', case=False, na=False)), 'SCOPE'] = 'BFN'
        df.loc[(df['Description'].str.contains('Remodel', case=False, na=False)) & (
            df['Description'].str.contains('bathroom', case=False, na=False)), 'SCOPE'] = 'BTH'
        df.loc[(df['Description'].str.contains('update', case=False, na=False)) & (
            df['Description'].str.contains('bathroom', case=False, na=False)), 'SCOPE'] = 'BTH'
        df.loc[(df['Description'].str.contains('Remodel', na=False)) & (
            df['Description'].str.contains('bath', case=False, na=False)), 'SCOPE'] = 'BTH'
        df.loc[(df['Description'].str.contains('commercial', case=False, na=False)) & (
            df['Description'].str.contains('remodel', case=False, na=False)), 'SCOPE'] = 'TFN'
        df.loc[(df['Description'].str.contains('detached', na=False)) & (
            df['Description'].str.contains('garage', case=False, na=False)), 'SCOPE'] = 'GAR'
        df.loc[df['Description'].str.contains('Addition', na=False), 'SCOPE'] = 'ADD'
        df.loc[(df['Description'].str.contains('Addition', na=False)) & (
            df['Description'].str.contains(' deck', case=False, na=False)), 'SCOPE'] = 'DEC'
        df.loc[(df['Description'].str.contains('Deck', case=False, na=False)) & (
            df['Description'].str.contains('deck', case=False, na=False)), 'SCOPE'] = 'DEC'
        df.loc[(df['Description'].str.contains('Addition', na=False)) & (
            df['Description'].str.contains('new porch', case=False, na=False)), 'SCOPE'] = 'POR'
        df.loc[(df['Description'].str.contains('Addition', na=False)) & (
            df['Description'].str.contains('pergola', case=False, na=False)), 'SCOPE'] = 'POR'
        df.loc[(df['Description'].str.contains('Addition', na=False)) & (
            df['Description'].str.contains(' shed', case=False, na=False)), 'SCOPE'] = 'OUT'
        df.loc[df['Description'].str.contains('Demo', case=False, na=False), 'SCOPE'] = 'DEM'
        df.loc[(df['Description'].str.contains('Demo', case=False, na=False)) & (
            df['Description'].str.contains('interior', case=False, na=False)), 'SCOPE'] = 'REM'
        df.loc[df['Description'].str.contains('Remodel', case=False, na=False), 'SCOPE'] = 'REM'
        df.loc[df['Description'].str.contains('Sign', na=False), 'SCOPE'] = 'SGN'
        df.loc[(df['Description'].str.contains('Mobile Home', na=False)) & (
            df['Description'].str.contains('replacement', case=False, na=False)), 'SCOPE'] = 'MHN'
        df.loc[(df['Description'].str.contains('Mobile Home', na=False)) & (
            df['Description'].str.contains('new', case=False, na=False)), 'SCOPE'] = 'MHN'
        df.loc[(df['Description'].str.contains('Roofing', na=False)) & (
                df['Description'].str.contains('roof', case=False, na=False)), 'SCOPE'] = 'RRR'
        df.loc[(df['Description'].str.contains('Roofing', na=False)) & (
            df['Description'].str.contains('single', case=False, na=False)), 'SCOPE'] = 'RRR'
        df.loc[(df['Description'].str.contains('Roofing', na=False)) & (
                df['Description'].str.contains('SFD', case=False, na=False)), 'SCOPE'] = 'RRR'
        df.loc[(df['Description'].str.contains('Roofing', na=False)) & (
            df['Description'].str.contains('residential', case=False, na=False)), 'SCOPE'] = 'RRR'
        df.loc[(df['Description'].str.contains('Roofing', na=False)) & (
                df['Description'].str.contains('multi', case=False, na=False)), 'SCOPE'] = 'RRR'
        df.loc[(df['Description'].str.contains('Roofing', na=False)) & (
            df['Description'].str.contains('duplex', case=False, na=False)), 'SCOPE'] = 'RRR'
        df.loc[(df['Description'].str.contains('Roofing', na=False)) & (
            df['Description'].str.contains('re-roof', case=False, na=False)), 'SCOPE'] = 'RRR'
        df.loc[(df['Description'].str.contains('Roofing', na=False)) & (
            df['Description'].str.contains('re roof', case=False, na=False)), 'SCOPE'] = 'RRR'
        df.loc[(df['Description'].str.contains('Roofing', na=False)) & (
            df['Description'].str.contains('shingle', case=False, na=False)), 'SCOPE'] = 'RRR'
        df.loc[(df['Description'].str.contains('Roofing', case=False, na=False)) & (
            df['Description'].str.contains('EPDM', case=False, na=False)), 'SCOPE'] = 'RRR'
        df.loc[df['Description'].str.contains('EPDM', case=False, na=False), 'SCOPE'] = 'RRR'
        df.loc[df['Description'].str.contains('/AC', case=False, na=False), 'SCOPE'] = 'AIR'
        df.loc[df['Description'].str.contains('A/C', case=False, na=False), 'SCOPE'] = 'AIR'
        df.loc[df['Description'].str.contains('cooler', case=False, na=False), 'SCOPE'] = 'AIR'
        df.loc[df['Description'].str.contains('AC ', case=False, na=False), 'SCOPE'] = 'AIR'
        df.loc[df['Description'].str.contains(' AC', na=False), 'SCOPE'] = 'AIR'
        df.loc[df['Description'].str.contains('mini-split', case=False, na=False), 'SCOPE'] = 'AIR'
        df.loc[df['Description'].str.contains('mini split', case=False, na=False), 'SCOPE'] = 'AIR'
        df.loc[df['Description'].str.contains('condenser', case=False, na=False), 'SCOPE'] = 'AIR'
        df.loc[df['Description'].str.contains('air condition', case=False, na=False), 'SCOPE'] = 'AIR'
        df.loc[df['Description'].str.contains('a/c', case=False, na=False), 'SCOPE'] = 'AIR'
        df.loc[df['Description'].str.contains(' ac ', case=False, na=False), 'SCOPE'] = 'AIR'
        df.loc[df['Description'].str.contains(' a/c ', case=False, na=False), 'SCOPE'] = 'AIR'
        df.loc[df['Description'].str.contains(' shed ', case=False, na=False), 'SCOPE'] = 'OUT'
        df.loc[(df['Description'].str.contains('Roof', case=False, na=False)), 'SCOPE'] = 'RRR'
        df.loc[(df['Description'].str.contains('asphalt', na=False)) & (
            df['Description'].str.contains('replace', case=False, na=False)), 'SCOPE'] = 'RRR'
        df.loc[df['Description'].str.contains('patio', case=False, na=False), 'SCOPE'] = 'POR'
        df.loc[df['Description'].str.contains('porch', case=False, na=False), 'SCOPE'] = 'POR'
        df.loc[df['Description'].str.contains('pergola', case=False, na=False), 'SCOPE'] = 'POR'
        df.loc[df['Description'].str.contains(' PV ', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Description'].str.contains('solar', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Description'].str.contains('photo', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Description'].str.contains('P.V.', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Description'].str.contains('photovoltaic', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Description'].str.contains('geotherm', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Description'].str.contains('flush-mounted', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[df['Description'].str.contains('flush mounted', case=False, na=False), 'SCOPE'] = 'ENR'
        df.loc[(df['Description'].str.contains('reroof', case=False, na=False)), 'SCOPE'] = 'RRR'
        df.loc[(df['Description'].str.contains('shingles', case=False, na=False)), 'SCOPE'] = 'RRR'
        df.loc[(df['Description'].str.contains('re-roof', case=False, na=False)), 'SCOPE'] = 'RRR'
        df.loc[(df['Description'].str.contains('owens', case=False, na=False)), 'SCOPE'] = 'RRR'
        df.loc[(df['Description'].str.contains('TPO', case=False, na=False)), 'SCOPE'] = 'RRR'
        df.loc[(df['Description'].str.contains('R&R', case=False, na=False)), 'SCOPE'] = 'RRR'
        df.loc[(df['Description'].str.contains('commercial', case=False, na=False)) & (
            df['Description'].str.contains('roof', case=False, na=False)), 'SCOPE'] = 'CRR'
        df.loc[(df['Description'].str.contains('Commercial', case=False, na=False)) & (
            df['Description'].str.contains('re-roof', case=False, na=False)), 'SCOPE'] = 'CRR'
        df.loc[df['Description'].str.contains('privacy', case=False, na=False), 'SCOPE'] = 'FEN'
        df.loc[df['Description'].str.contains('fencing', case=False, na=False), 'SCOPE'] = 'FEN'
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
        df.loc[df['Description'].str.contains('tenant', case=False, na=False), 'SCOPE'] = 'TFN'
        df.loc[(df['Description'].str.contains('interior', case=False, na=False) &
                df['Description'].str.contains('commercial', case=False, na=False)), 'SCOPE'] = 'TFN'
        df.loc[df['Description'].str.contains('retaining wall', case=False, na=False), 'SCOPE'] = 'RTW'
        df.loc[df['Description'].str.contains('New Construction', case=False, na=False), 'SCOPE'] = 'NEW'
        df.loc[df['Description'].str.contains('New Single Family', case=False, na=False), 'SCOPE'] = 'NEW'
        df.loc[(df['Description'].str.contains('Residential', case=False, na=False) &
                df['Description'].str.contains('Single Family', case=False, na=False)), 'SCOPE'] = 'NEW'
        df.loc[(df['Description'].str.contains('Residential', case=False, na=False) &
                df['Description'].str.contains('Duplex', case=False, na=False)), 'SCOPE'] = 'NEW'
        df.loc[(df['Description'].str.contains('Residential', case=False, na=False) &
                df['Description'].str.contains('Condo', case=False, na=False)), 'SCOPE'] = 'NEW'
        df.loc[(df['Description'].str.contains('Residential', case=False, na=False) &
                df['Description'].str.contains('Triplex', case=False, na=False)), 'SCOPE'] = 'NEW'
        df.loc[(df['Description'].str.contains('Residential', case=False, na=False) &
                df['Description'].str.contains('Apartment', case=False, na=False)), 'SCOPE'] = 'NEW'
        df.loc[df['Description'].str.contains('BWOP', case=False, na=False), 'SCOPE'] = 'NEW'
        df.loc[df['Description'].str.contains('(SPR', case=False, na=False, regex=False), 'SCOPE'] = 'NEW'
        df.loc[df['Description'].str.contains('(LE', case=False, na=False, regex=False), 'SCOPE'] = 'NEW'
        df.loc[df['Description'].str.contains('carport', case=False, na=False) & (
            df['Value Total'] > 10000), 'SCOPE'] = 'NEW'
        df.loc[df['Description'].str.contains('garage', case=False, na=False) & (
            df['Description'].str.contains("(SPR", case=False, na=False, regex=False)), 'SCOPE'] = 'GAR'
        df.loc[df['Description'].str.contains('Barn', case=False, na=False) & (
            df['Description'].str.contains('BWOP', case=False, na=False)), 'SCOPE'] = 'BRN'
        df.loc[df['Description'].str.contains('Structural', case=False, na=False) & (
            df['Description'].str.contains('repair', case=False, na=False)), 'SCOPE'] = 'SRP'
        df.loc[df['Description'].str.contains('foundation', case=False, na=False) & (
            df['Description'].str.contains('repair', case=False, na=False)), 'SCOPE'] = 'SRP'
        df.loc[df['Description'].str.contains('siding', case=False, na=False), 'SCOPE'] = 'SDG'
        df.loc[df['Description'].str.contains('pool', case=False, na=False), 'SCOPE'] = 'POL'
        df.loc[df['Description'].str.contains('hot tub', case=False, na=False), 'SCOPE'] = 'HTS'
        df.loc[df['Description'].str.contains('Spa ', case=False, na=False), 'SCOPE'] = 'HTS'
        df.loc[df['Description'].str.contains(' Spa ', case=False, na=False), 'SCOPE'] = 'HTS'
        df['SCOPE'] = df['SCOPE'].fillna('OTH')


    else:
        print('Please provide a permit description column titled "Description"')

    return df


def database_connection():
    print('Establishing connection...\n')
    while True:
        try:
            c_str = open('connection_string.txt', 'r').read()  # can be removed once connection string is added
            cnxn = pyodbc.connect(c_str)
            return cnxn

        except pyodbc.InterfaceError:
            print('Invalid password, please input new password:')
            password = input()
            cnxn = pyodbc.connect(driver="{SQL Server}",SERVER="server", DSN="prod", UID="db",
                                  PWD=password)
            print('Connected to the CAMA database')
            return cnxn


def permit_check_and_address_creation(df, cnxn):
    if city == 'Unincorporated':
        city_sql = """SELECT distinct parcel.strap, strap_idx.folio, parcel.status_cd, parcel.dor_cd, parcel.nh_cd, 
                parcel.map_id, site.str_num, site.str_pfx, site.str, site.str_sfx, site.str_sfx_dir, site.str_unit
                FROM r_prod.dbo.parcel
                INNER JOIN r_prod.dbo.site ON parcel.strap = site.strap
                INNER JOIN r_prod.dbo.strap_idx ON parcel.strap = strap_idx.strap
                WHERE (parcel.dor_cd <> 'POSS') AND parcel.status_cd = 'A'
                AND (site.city IN (?, 'Boulder', 'Lyons', 'Ward', 'Allenspark', 'Lafayette', 'Niwot', 
                'Louisville', 'Superior', 'Jamestown'))"""
    else:
        city_sql = """SELECT distinct parcel.strap, strap_idx.folio, parcel.status_cd, parcel.dor_cd, parcel.nh_cd, 
        parcel.map_id, site.str_num, site.str_pfx, site.str, site.str_sfx, site.str_sfx_dir, site.str_unit
        FROM r_prod.dbo.parcel
        INNER JOIN r_prod.dbo.site ON parcel.strap = site.strap
        INNER JOIN r_prod.dbo.strap_idx ON parcel.strap = strap_idx.strap
        WHERE (parcel.dor_cd <> 'POSS') AND parcel.status_cd = 'A'
        AND (site.city IN (?))"""

    permit_sql = '''SELECT distinct permit_num FROM r_prod.dbo.permit'''

    city_sql_df = pd.read_sql(city_sql, cnxn, params=[city.upper()])
    permit_sql_df = pd.read_sql(permit_sql, cnxn)

    # Takes the permit database, renames the column to Permit Number, and then merges the month's permit with permits found
    # in the database, this makes sure a permit is not double uploaded, or double valuing

    permit_sql_df.rename(columns={'permit_num': 'Permit Number'}, inplace=True)
    permit_sql_df['Permit Number'] = permit_sql_df['Permit Number'].astype(str)
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

    elif city in ['Boulder', 'Erie', 'Louisville']:
        df = df.merge(city_address, on='Address', how='left')
        df.drop(columns=['Parcel Number_y'])
        df = df.rename(columns={'Parcel Number_x': 'Parcel Number'})
        df_merge_perm = df.merge(city_address, on='Parcel Number', how='left')
        df_merge_perm['strap_final'] = df_merge_perm['strap_x'].where(
        df_merge_perm['strap_x'].notnull(), df_merge_perm['strap_y'])
        df_merge_perm.drop_duplicates(subset=['Permit Number'], keep='last', inplace=True)

    if city == 'Superior':
        df = df.merge(city_address, on='Address', how='left')
        df_merge_perm = df.merge(city_address, on='Parcel Number', how='left')
        df_merge_perm['strap_final'] = df_merge_perm['strap_x'].where(
            df_merge_perm['strap_x'].notnull(), df_merge_perm['strap_y'])
        df_merge_perm.drop_duplicates(subset=['Permit Number'], keep='last', inplace=True)

    elif city == 'Lafayette':
        df['Address'] = df['Address'].str.split('.').str[0]
        df['Address'] = df['Address'].str.replace('  ', ' ')
        df = df.merge(city_address, on='Address', how='left')
        df.drop(columns=['Parcel Number_y'])
        df = df.rename(columns={'Parcel Number_x': 'Parcel Number'})
        df_merge_perm = df.merge(city_address, on='Parcel Number', how='left')
        df_merge_perm['strap_final'] = df_merge_perm['strap_x'].where(
            df_merge_perm['strap_x'].notnull(), df_merge_perm['strap_y'])
        df_merge_perm.drop_duplicates(subset=['Permit Number'], keep='last', inplace=True)

    elif city == 'Unincorporated':
        df['Street Number'] = df['Street Number'].astype(str)
        df['Street Direction'] = df['Street Direction'].fillna(np.nan).replace(np.nan, ' ')
        df['Street Unit'] = df['Street Unit'].fillna(np.nan).replace(np.nan, ' ')
        df['Address'] = df['Street Number'].astype(str) + df['Street Direction'].astype(str) + \
                        df['Street Name'].astype(str) + ' ' + df['Street Suffix'].astype(str) + df['Street Unit'].astype(str)
        df['Address'] = df['Address'].str.replace(' DRIVE ', ' DR ')
        df['Address'] = df['Address'].str.replace(' STREET ', ' ST ')
        df['Address'] = df['Address'].str.replace(' ROAD ', ' RD ')
        df['Address'] = df['Address'].str.replace(' COURT ', ' CT ')
        df['Address'] = df['Address'].str.replace(' WAY ', ' WY ')
        df['Address'] = df['Address'].str.replace(' CIRCLE ', ' CIR ')
        df['Address'] = df['Address'].str.replace(' PLACE ', ' PL ')
        df['Address'] = df['Address'].str.replace(' LANE ', ' LN ')
        df['Address'] = df['Address'].str.replace(' TRAIL ', ' TRL ')
        df['Address'] = df['Address'].str.replace(' AVENUE ', ' AVE ')
        df['Address'] = df['Address'].str.rstrip()
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
    df_unmerged_addresses.to_excel('HandEnter_' + city + '_permits.xlsx', index=False)

    return df, df_merge_perm, df_unmerged_addresses


def final_cleanup_and_export(df):
    df['strap'] = df['strap_final'].str.rstrip()
    df['str_num_x'] = df['str_num_x'].where(df['str_num_x'].notnull(), df['str_num_y'])
    df['str_pfx_x'] = df['str_pfx_x'].where(df['str_pfx_x'].notnull(), df['str_pfx_y'])
    df['str_x'] = df['str_x'].where(df['str_x'].notnull(), df['str_y'])
    df['str_sfx_x'] = df['str_sfx_x'].where(df['str_sfx_x'].notnull(), df['str_sfx_y'])
    df['str_unit_x'] = df['str_unit_x'].where(df['str_unit_x'].notnull(), df['str_unit_y'])
    df['nh_cd_x'] = df['nh_cd_x'].where(df['nh_cd_x'].notnull(), df['nh_cd_y'])
    df['dor_cd_x'] = df['dor_cd_x'].where(df['dor_cd_x'].notnull(), df['dor_cd_y'])
    df.rename(columns={'nh_cd_x': 'nh_cd'}, inplace=True)
    df.rename(columns={'dor_cd_x': 'dor_cd'}, inplace=True)
    df.rename(columns={'map_id_x': 'map_id'}, inplace=True)
    df.rename(columns={'str_num_x': 'str_num'}, inplace=True)
    df.rename(columns={'str_pfx_x': 'str_pfx'}, inplace=True)
    df.rename(columns={'str_x': 'str'}, inplace=True)
    df.rename(columns={'str_sfx_x': 'str_sfx'}, inplace=True)
    df.rename(columns={'str_unit_x': 'str_unit'}, inplace=True)
    df = df.fillna('')
    # create spreadsheet for app.
    print("Please name the exported spreadsheet for the Appraiser staff")
    if city == 'Longmont':
        df = df[["Permit Number", "strap", "Description", "str_num", "str_pfx",
             "str", "str_sfx", "str_unit", "Value Total", "Issued Date", "Final Date", "SQFT", "SCOPE",
             "nh_cd", "dor_cd"]]
    elif city == 'Boulder':
        df = df[["Permit Number", "Parent Permit Number", "strap", "Description", "str_num", "str_pfx",
                 "str", "str_sfx", "str_unit", "Value Total", "Issued Date", "Finaled Date", "Work Class", "SCOPE",
                 "nh_cd", "dor_cd"]]
    elif city == 'Superior':
        df = df[["Permit Number", "strap", "Description", "str_num", "str_pfx",
                 "str", "str_sfx", "str_unit", "Value Total", "Issued Date", "SCOPE", "nh_cd", "dor_cd"]]
    elif city in ['Lafayette', 'Louisville', 'Unincorporated', 'Erie']:
        df = df[["Permit Number", "strap", "Description", "str_num", "str_pfx",
                 "str", "str_sfx", "str_unit", "Value Total", "Issued Date", "SCOPE",
                 "nh_cd", "dor_cd", "map_id"]]
    df.to_excel(input() + "_" + city +"Permits_Appraiser.xlsx", index=False)

    if city == 'Longmont':
        df = df[["Permit Number", "strap", "Description", "str_num", "str_pfx",
            "str", "str_sfx", "str_unit", "Value Total", "Issued Date", "Final Date", "SQFT", "SCOPE"]]

    elif city == 'Boulder':
        df = df[["Permit Number", "Parent Permit Number", "strap", "Description", "str_num", "str_pfx",
                 "str", "str_sfx", "str_unit", "Value Total", "Issued Date", "Finaled Date", "Work Class", "SCOPE"]]

    elif city == 'Superior':
        df = df[["Permit Number", "strap", "Description", "str_num", "str_pfx",
            "str", "str_sfx", "str_unit", "Value Total", "Issued Date", "SCOPE"]]

    elif city in ['Lafayette', 'Louisville', 'Unincorporated', 'Erie']:
        df = df[["Permit Number", "strap", "Description", "str_num", "str_pfx",
            "str", "str_sfx", "str_unit", "Value Total", "Issued Date", "SCOPE"]]

    # export final data to a txt file to be imported
    header = ''  # first, create the header
    for s in list(df):
        header += '"' + s + '"|'
    header = header[:-1]  # to take the final | off, as it's unnecessary
    # take the values of each column and add double quotes
    if city == 'Longmont':
        df.update(df[["Permit Number", "strap", "Description", "str_num", "str_pfx",
            "str", "str_sfx", "str_unit", "Value Total", "Issued Date", "Final Date", "SQFT", "SCOPE"]].applymap('"{}"'.format))

    elif city in ['Superior']:
        df.update(df[["Permit Number", "strap", "Description", "str_num", "str_pfx",
            "str", "str_sfx", "str_unit", "Value Total", "Issued Date", "SCOPE"]].applymap('"{}"'.format))

    elif city in ['Boulder']:
        df.update(df[["Permit Number", "Parent Permit Number", "strap", "Description", "str_num", "str_pfx",
                 "str", "str_sfx", "str_unit", "Value Total", "Issued Date", "Finaled Date", "Work Class",
                      "SCOPE"]].applymap('"{}"'.format))

    elif city in ['Lafayette', 'Louisville', 'Unincorporated', 'Erie']:
        df.update(df[["Permit Number", "strap", "Description", "str_num", "str_pfx",
            "str", "str_sfx", "str_unit", "Value Total", "Issued Date", "SCOPE"]].applymap('"{}"'.format))

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
elif city == 'Louisville':
    df = louisville_spreadsheet_formatter(df)
elif city == 'Erie':
    df = spreadsheet_formatter(df)
    df = erie_spreadsheet_formatter(df)
elif city in ['Boulder', 'Longmont', 'Lafayette', 'Unincorporated']:
    df = spreadsheet_formatter(df)

# Run issued date function
df = issued_date_filter(df)

# Classify the permits using the three letter scope code
if city in ['Unincorporated', 'Erie', 'Superior', 'Louisville']:
    df = unincorp_permit_classifier(df)
else:
    df = permit_classifier(df)

# Create a permit dataframe and an address dataframe
cnxn = database_connection()
permit, city_address = permit_check_and_address_creation(df, cnxn)

# Merge the queried building permits with the ones already uploaded in CAMA
df_uploaded = pd.merge(df, permit, on='Permit Number')

# Check to see if an already uploaded permit is in CAMA
df = df.loc[~df['Permit Number'].isin(df_uploaded['Permit Number'])]
df.drop_duplicates()

city_address = address_formatter(city_address)

df, df_merge_perm, df_unmerged_addresses = address_and_parcel_merge(df)

final_cleanup_and_export(df_merge_perm)
