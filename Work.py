import pandas as pd
import numpy as np
import streamlit as st

# Just do check on totals of grouped NL and Budget for Feb 2020, just to make sure grouping is working right



raw1='C:/Users/Darragh/Documents/Python/Work/Data/Budget_2020.xlsx'
raw2='C:/Users/Darragh/Documents/Python/Work/Data/EE.xlsx'
raw3='C:/Users/Darragh/Documents/Python/Work/Data/Project Codes.xlsx'
raw4='C:/Users/Darragh/Documents/Python/Work/Data/NL_2016_2019.xlsx'
raw5='C:/Users/Darragh/Documents/Python/Work/Data/NL_2020_06.xlsx'
coding_acc_schedule = (pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/account_numbers.xlsx'))
coding_acc_schedule = coding_acc_schedule.iloc[:,:3]
# st.write (coding_acc_schedule)

# coding_acc_schedule = pd.DataFrame( {'Acc_Schedule':[920,921,924,926,940,941,942,943,946,947,948,951,953,954,955,956,971,972,973,999],'Name':[
#     'Revenue','Cost of Sales','Cost of Sales','Office Expenses',
#     'Payroll','Rent','Facilities','Travel','Office','Audit Legal & Consulting',
#     'Computer','Depreciation','??','no idea','no clue','dont know at all','Bank charges i think','Lease i think','FX',
#     'Overhead Capitalisation IP']},
#     columns=['Acc_Schedule','Name'] )
# st.write (coding_acc_schedule)

def main():
    Budget = Budget_2020()
    EE = EE_numbers()
    Project = Project_codes()
    NL = NL_2020()
    st.write (Budget.dtypes)
    st.write('this is the Budget 2020',Budget)
    st.write(Project)
    st.write ('this is the nominal ledger',NL)
    test = group ( Budget )
    st.write ('this is the Budget grouped', test)
    nl_group_test = nl_group(NL)
    st.write ('this is the NL grouped', nl_group_test)
    # nl_group_test.to_excel("C:/Users/Darragh/Documents/Python/Work/Data/account_numbers.xlsx")

def group(x):
    x = x.groupby(['Name','Acc_Schedule']).agg ( Budget_YTD = ( 'Budget_YTD_6','sum' ),
    Sorted_acc = ('Sorting','first')  ).sort_values(by=['Sorted_acc','Acc_Schedule'], ascending = [True,True])
    all_sum = x.sum()
    x = x.reset_index()
    x.loc[('Total')] = all_sum
    return x

def nl_group(x):
    return x.groupby(['Name','Acc_Schedule']).agg ( NL_YTD_Amount = ( 'Journal Amount','sum' ),
    Sorted_acc = ('Sorting','first') ).sort_values(by=['Sorted_acc','Acc_Schedule'], ascending = [True,True])

# @st.cache
def prep_data(url):
    data = pd.read_excel(url)
    return data

@st.cache
def Budget_2020():
    Budget_2020=prep_data(raw1)
    Budget_2020['Acc_Schedule']=Budget_2020['ACCOUNT'].str[-8:-5]
    Budget_2020['Acc_Schedule']=pd.to_numeric(Budget_2020['Acc_Schedule'])
    Budget_2020['Acc_Number']=Budget_2020['ACCOUNT'].str[-8:]
    Budget_2020['Dept'] = Budget_2020['ACCOUNT'].str[-14:-9]
    Budget_2020 = Budget_2020.merge (coding_acc_schedule, on='Acc_Number',how='outer')
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
    cols_to_move = ['Acc_Schedule','Name','Sorting','Acc_Number','Dept','Budget_YTD_1','Budget_YTD_2']
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
    NL_2020['Acc_Number'] = NL_2020['Account Code']
    # NL_2020.assign(Project_Code=NL_2020['Project'].str[:8]) # Why doesn't this work, it worked before!
    NL_2020 = NL_2020.merge (coding_acc_schedule, on='Acc_Number',how='outer')
    
    cols_to_move = ['Acc_Schedule','Acc_Number','Sorting','Project_Code','Project_Name','Description','Debit','Credit','Journal Amount',
    'Yr.','Per.','Account Code','Project','Employee','Department','Posting Code']
    NL_2020 = NL_2020[ cols_to_move + [ col for col in NL_2020 if col not in cols_to_move ] ]
    
    return NL_2020

main()