import pandas as pd
import numpy as np
import streamlit as st

raw1='C:/Users/Darragh/Documents/Python/Work/Data/Budget_2020.xlsx'
raw2='C:/Users/Darragh/Documents/Python/Work/Data/EE.xlsx'
raw3='C:/Users/Darragh/Documents/Python/Work/Data/Project Codes.xlsx'
raw4='C:/Users/Darragh/Documents/Python/Work/Data/NL_2016_2019.xlsx'
raw5='C:/Users/Darragh/Documents/Python/Work/Data/NL_2020_06.xlsx'

# So I need to replicate the Budget Upload file I think and then do a comparison?


def main():
    Budget = Budget_2020()
    EE = EE_numbers()
    Project = Project_codes()
    NL = NL_2020()
    st.write('this is the Budget 2020',Budget)
    st.write(Project)
    st.write ('this is the nominal ledger',NL)
    test = group ( Budget )
    st.write ('this is the Budget grouped', test)

def group(x):
    return x.groupby(['Acc_Schedule']).agg ( Budget_YTD = ( 'Budget_YTD_7','sum' ) )


# @st.cache
def prep_data(url):
    data = pd.read_excel(url)
    return data

@st.cache
def Budget_2020():
    Budget_2020=prep_data(raw1)
    Budget_2020['Acc_Schedule']=Budget_2020['ACCOUNT'].str[-8:-5]
    Budget_2020['Acc_Number']=Budget_2020['ACCOUNT'].str[-8:]
    Budget_2020['Dept'] = Budget_2020['ACCOUNT'].str[-14:-9]
    Budget_2020['Budget_YTD_1'] = Budget_2020.loc[:,'BUDGET 1': 'BUDGET 1'].sum(axis=1)
    Budget_2020['Budget_YTD_2'] = Budget_2020.loc[:,'BUDGET 1': 'BUDGET 2'].sum(axis=1)
    Budget_2020['Budget_YTD_3'] = Budget_2020.loc[:,'BUDGET 1': 'BUDGET 3'].sum(axis=1)
    Budget_2020['Budget_YTD_4'] = Budget_2020.loc[:,'BUDGET 1': 'BUDGET 4'].sum(axis=1)
    Budget_2020['Budget_YTD_5'] = Budget_2020.loc[:,'BUDGET 1': 'BUDGET 5'].sum(axis=1)
    Budget_2020['Budget_YTD_6'] = Budget_2020.loc[:,'BUDGET 1': 'BUDGET 6'].sum(axis=1)
    Budget_2020['Budget_YTD_7'] = Budget_2020.loc[:,'BUDGET 1': 'BUDGET 7'].sum(axis=1)
    Budget_2020['Budget_YTD_8'] = Budget_2020.loc[:,'BUDGET 1': 'BUDGET 8'].sum(axis=1)
    Budget_2020['Budget_YTD_9'] = Budget_2020.loc[:,'BUDGET 1': 'BUDGET 9'].sum(axis=1)
    Budget_2020['Budget_YTD_10'] = Budget_2020.loc[:,'BUDGET 1': 'BUDGET 10'].sum(axis=1)
    Budget_2020['Budget_YTD_11'] = Budget_2020.loc[:,'BUDGET 1': 'BUDGET 11'].sum(axis=1)
    Budget_2020['Budget_YTD_12'] = Budget_2020.loc[:,'BUDGET 1': 'BUDGET 12'].sum(axis=1)
    cols_to_move = ['Acc_Schedule','Acc_Number','Dept','Budget_YTD_1','Budget_YTD_2']
    Budget_2020 = Budget_2020[ cols_to_move + [ col for col in Budget_2020 if col not in cols_to_move ] ]
    return Budget_2020

def EE_numbers():
    EE_numbers=prep_data(raw2)
    return EE_numbers

def Project_codes():
    Project_codes=prep_data(raw3)
    return Project_codes

@st.cache
def NL_2020():
    # NL_2016_2019=prep_data(raw4)
    NL_2020=prep_data(raw5)
    NL_2020['Acc_Schedule']=NL_2020['Account Code'].str[:3]
    # NL_2020.assign(Acc_Schedule=NL_2020['Account Code'].str[:3])
    NL_2020['Project_Code'] = NL_2020['Project'].str[:8]
    NL_2020['Project_Name'] = NL_2020['Project'].str[8:]
    # NL_2020.assign(Project_Code=NL_2020['Project'].str[:8]) # Why doesn't this work, it worked before!
    cols_to_move = ['Acc_Schedule', 'Project_Code','Project_Name','Description','Debit','Credit','Journal Amount','Yr.','Per.','Account Code','Project','Employee','Department','Posting Code']
    NL_2020 = NL_2020[ cols_to_move + [ col for col in NL_2020 if col not in cols_to_move ] ]
    return NL_2020

main()