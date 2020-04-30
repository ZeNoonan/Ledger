import pandas as pd
import numpy as np
import streamlit as st

# https://stackoverflow.com/questions/47494720/python-pandas-subtotals-on-groupby
# https://stackoverflow.com/questions/45971751/appending-grandtotal-and-subtotal-rows-to-two-level-row-and-column-index-datafra
# GET RID OF 920 Sch - want to see what it looks like without it.  Maybe could have detail in another tab
#df.columns.to_list() https://stackoverflow.com/questions/54114449/pandas-column-names-to-list-correct-method


raw1='C:/Users/Darragh/Documents/Python/Work/Data/Budget_2020.xlsx'
raw2='C:/Users/Darragh/Documents/Python/Work/Data/EE.xlsx'
raw3='C:/Users/Darragh/Documents/Python/Work/Data/Project Codes.xlsx'
raw4='C:/Users/Darragh/Documents/Python/Work/Data/NL_2016_2019.xlsx'
raw5='C:/Users/Darragh/Documents/Python/Work/Data/NL_2020_06.xlsx'
coding_acc_schedule = (pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/account_numbers.xlsx'))
# st.write(coding_acc_schedule)
coding_acc_schedule = coding_acc_schedule.iloc[:,:3]
coding_sort=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/account_numbers.xlsx', sheet_name='Sheet2')
# st.write (coding_sort)
# st.write (coding_acc_schedule)

def main():
    Budget = Budget_2020()
    # st.table (Budget)
    EE = EE_numbers()
    Project = Project_codes()
    # ytd_selection = st.sidebar.number_input ("For what period would you like to run - period 1 up to period?", 1,12,value=6, step=1)
    ytd_selection = st.sidebar.selectbox("For what period would you like to run - period 1 up to period?",["Sep_YTD", "Oct_YTD", "Nov_YTD","Dec_YTD","Jan_YTD","Feb_YTD","Mar_YTD","Apr_YTD","May_YTD","Jun_YTD","Jul_YTD","Aug_YTD"])
    NL = NL_2020(ytd_selection)
    # https://github.com/streamlit/streamlit/issues/729   This is for converting period 6 into say YTD_Feb uses a dictionary
    # maybe keep it simple first, just use 6 as period 6

    # st.write (NL.dtypes)
    # st.write('this is the Budget 2020',Budget)
    # st.write(Project)
    # st.write ('this is the nominal ledger',NL)
    
    test = group ( Budget,ytd_selection )
    st.write ('this is the Budget grouped', test)

    nl_group_test = nl_group(NL)
    st.write ('this is the NL grouped', nl_group_test)
    # st.write ('dtypes of budget group', test.dtypes)
    # st.write ('dtypes of nl group', nl_group_test.dtypes)
    # nl_group_test.to_excel("C:/Users/Darragh/Documents/Python/Work/Data/account_numbers.xlsx")
    compare_df = compare (nl_group_test, test)
    # st.write ('this is the comparison', compare_df)
    subtotal1 = subtotal(compare_df)
    st.write ('This is the Overall PL')
    st.write (subtotal1)
    st.write ('now lets go make a PL that filters by Dept and by Date....')


def subtotal(x):
    gross_profit = x.loc['Revenue':'Cost of Sales',:].sum()
    sub_total_overheads = x.loc['Payroll':'Other',:].sum()
    x.loc['Gross Profit'] = gross_profit
    x.loc['Gross Profit %'] = gross_profit / x.loc['Revenue']
    x.loc['Sub-Total Overheads'] = sub_total_overheads
    x.loc['EBITDA'] = gross_profit + sub_total_overheads + x.loc['IP Capitalisation']
    x.loc['Net Profit before Tax'] = x.loc['EBITDA'] + x.loc['Depreciation'] + x.loc['Finance Lease Interest'] 
    x.loc['Net Profit %'] = x.loc['Net Profit before Tax'] / x.loc['Revenue']
    x['YTD_Variance'] = x['NL_YTD_Amount'] - x['Budget_YTD']
    x = pd.merge (x,coding_sort, on=['Name'],how='inner')
    x = x.drop(columns =['Sorting_x'])
    x = x.rename(columns = {'Sorting_y' : 'Sorting'}).sort_values(by ='Sorting', ascending=True)

    return x
    
    # EBITDA = gross_profit + sub_total_overheads + x.loc['IP Capitalisation']

def compare(x,y):
    # c = pd.merge (x,y, on=['Name','Acc_Schedule','Sorting'], how='outer')
    c = pd.merge (x,y, on=['Name','Sorting'], how='outer')
    c = c.set_index('Name')
    c['Budget_YTD'].fillna(0, inplace=True)
    # st.write( c.loc[c['Name'].isnull()] )
    # st.write( c.loc[c['Acc_Schedule'].isnull()] )
    return c

def group(x,ytd_month_number):
    # x = x.groupby(['Name','Acc_Schedule']).agg ( Budget_YTD = ( 'Budget_YTD_6','sum' ),
    # Sorting = ('Sorting','first')  ).sort_values(by=['Acc_Schedule','Sorting'], ascending = [True,True])
    x = x.groupby(['Name']).agg ( Budget_YTD = ( ytd_month_number,'sum' ),
    Sorting = ('Sorting','first')  ).sort_values(by=['Sorting'], ascending = [True])
    all_sum = x.sum()
    x = x.reset_index()
    # x.loc[('Total')] = all_sum
    # x.at['Total','Name'] = 'Grand' #https://stackoverflow.com/questions/13842088/set-value-for-particular-cell-in-pandas-dataframe-using-index
    return x

def nl_group(x):
    # x = x.groupby(['Name','Acc_Schedule']).agg ( NL_YTD_Amount = ( 'Journal Amount','sum' ),
    # Sorting = ('Sorting','first') ).sort_values(by=['Sorting','Acc_Schedule'], ascending = [True,True])
    x = x.groupby(['Name']).agg ( NL_YTD_Amount = ( 'Journal Amount','sum' ),
    Sorting = ('Sorting','first') ).sort_values(by=['Sorting'], ascending = [True])
    all_sum = x.sum()
    x = x.reset_index()
    # x.loc[('Total')] = all_sum
    # x.at['Total','Name'] = 'Grand' 
    return x

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
    Budget_2020.loc[:,'BUDGET 1':'BUDGET 12'] = Budget_2020.loc[:,'BUDGET 1':'BUDGET 12'] *-1
    Budget_2020 = Budget_2020.merge (coding_acc_schedule, on='Acc_Number',how='outer')
    st.write( Budget_2020.loc[Budget_2020['Name'].isnull()] ) # Always test after merge my issue was with the spreadsheet didn't have full coding https://stackoverflow.com/questions/53645882/pandas-merging-101
    # Budget_2020['Budget_YTD_1'] = Budget_2020.loc[:,'BUDGET 1': 'BUDGET 1'].sum(axis=1)
    # Budget_2020['Budget_YTD_2'] = Budget_2020.loc[:,'BUDGET 1': 'BUDGET 2'].sum(axis=1)
    # Budget_2020['Budget_YTD_3'] = Budget_2020.loc[:,'BUDGET 1': 'BUDGET 3'].sum(axis=1)
    # Budget_2020['Budget_YTD_4'] = Budget_2020.loc[:,'BUDGET 1': 'BUDGET 4'].sum(axis=1)
    # Budget_2020['Budget_YTD_5'] = Budget_2020.loc[:,'BUDGET 1': 'BUDGET 5'].sum(axis=1)
    # Budget_2020['Budget_YTD_6'] = Budget_2020.loc[:,'BUDGET 1': 'BUDGET 6'].sum(axis=1)
    # Budget_2020['Budget_YTD_7'] = Budget_2020.loc[:,'BUDGET 1': 'BUDGET 7'].sum(axis=1)
    # Budget_2020['Budget_YTD_8'] = Budget_2020.loc[:,'BUDGET 1': 'BUDGET 8'].sum(axis=1)
    # Budget_2020['Budget_YTD_9'] = Budget_2020.loc[:,'BUDGET 1': 'BUDGET 9'].sum(axis=1)
    # Budget_2020['Budget_YTD_10'] = Budget_2020.loc[:,'BUDGET 1': 'BUDGET 10'].sum(axis=1)
    # Budget_2020['Budget_YTD_11'] = Budget_2020.loc[:,'BUDGET 1': 'BUDGET 11'].sum(axis=1)
    # Budget_2020['Budget_YTD_12'] = Budget_2020.loc[:,'BUDGET 1': 'BUDGET 12'].sum(axis=1)
    Budget_2020['Sep_YTD'] = Budget_2020.loc[:,'BUDGET 1': 'BUDGET 1'].sum(axis=1)
    Budget_2020['Oct_YTD'] = Budget_2020.loc[:,'BUDGET 1': 'BUDGET 2'].sum(axis=1)
    Budget_2020['Nov_YTD'] = Budget_2020.loc[:,'BUDGET 1': 'BUDGET 3'].sum(axis=1)
    Budget_2020['Dec_YTD'] = Budget_2020.loc[:,'BUDGET 1': 'BUDGET 4'].sum(axis=1)
    Budget_2020['Jan_YTD'] = Budget_2020.loc[:,'BUDGET 1': 'BUDGET 5'].sum(axis=1)
    Budget_2020['Feb_YTD'] = Budget_2020.loc[:,'BUDGET 1': 'BUDGET 6'].sum(axis=1)
    Budget_2020['Mar_YTD'] = Budget_2020.loc[:,'BUDGET 1': 'BUDGET 7'].sum(axis=1)
    Budget_2020['Apr_YTD'] = Budget_2020.loc[:,'BUDGET 1': 'BUDGET 8'].sum(axis=1)
    Budget_2020['May_YTD'] = Budget_2020.loc[:,'BUDGET 1': 'BUDGET 9'].sum(axis=1)
    Budget_2020['Jun_YTD'] = Budget_2020.loc[:,'BUDGET 1': 'BUDGET 10'].sum(axis=1)
    Budget_2020['Jul_YTD'] = Budget_2020.loc[:,'BUDGET 1': 'BUDGET 11'].sum(axis=1)
    Budget_2020['Aug_YTD'] = Budget_2020.loc[:,'BUDGET 1': 'BUDGET 12'].sum(axis=1)
    cols_to_move = ['Acc_Schedule','Name','Sorting','Acc_Number','Dept']
    Budget_2020 = Budget_2020[ cols_to_move + [ col for col in Budget_2020 if col not in cols_to_move ] ]
    return Budget_2020

def EE_numbers():
    EE_numbers=prep_data(raw2)
    return EE_numbers

def Project_codes():
    Project_codes=prep_data(raw3)
    return Project_codes

# @st.cache
def NL_2020(ytd_month_number):
    # NL_2016_2019=prep_data(raw4)
    NL_2020=prep_data(raw5)
    NL_2020['Acc_Schedule']=NL_2020['Account Code'].str[:3]
    NL_2020['Acc_Schedule']=pd.to_numeric(NL_2020['Acc_Schedule'])
    # NL_2020.assign(Acc_Schedule=NL_2020['Account Code'].str[:3])
    NL_2020['Project_Code'] = NL_2020['Project'].str[:8]
    NL_2020['Project_Name'] = NL_2020['Project'].str[8:]
    NL_2020['Acc_Number'] = NL_2020['Account Code']
    NL_2020['Journal Amount'] = NL_2020['Journal Amount'] * -1
    # NL_2020.assign(Project_Code=NL_2020['Project'].str[:8]) # Why doesn't this work, it worked before!
    # NL_2020 = NL_2020 [ (NL_2020['Per.'] < ytd_month_number) & (NL_2020['Per.'] == ytd_month_number) ] this doesn't appear to work don't know why
    date_dict= {"Sep_YTD":1,"Oct_YTD":2,"Nov_YTD":3,"Dec_YTD":4,"Jan_YTD":5,"Feb_YTD":6,"Mar_YTD":7,"Apr_YTD":8,"May_YTD":9,"Jun_YTD":10,"Jul_YTD":11,"Aug_YTD":12}
    NL_2020 = NL_2020 [ (NL_2020['Per.'] <= date_dict[ytd_month_number]) ] 
    # NL_2020 = NL_2020.loc [ NL_2020['Per.'].le(ytd_month_number) ]
    NL_2020 = NL_2020.merge (coding_acc_schedule, on='Acc_Number',how='outer')
    
    cols_to_move = ['Acc_Schedule','Acc_Number','Sorting','Project_Code','Project_Name','Description','Debit','Credit','Journal Amount',
    'Yr.','Per.','Account Code','Project','Employee','Department','Posting Code']
    NL_2020 = NL_2020[ cols_to_move + [ col for col in NL_2020 if col not in cols_to_move ] ]
    
    return NL_2020

main()