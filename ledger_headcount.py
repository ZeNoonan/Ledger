import pandas as pd
import numpy as np
import streamlit as st
import datetime
import altair as alt

st.set_page_config(layout="wide")
st.write('Select start of forecast period below and actual')
with st.echo():
    start_forecast_period_resourcing_tool='2021-06-01 00:00:00'
    data_2021='C:/Users/Darragh/Documents/Python/Work/Data/NL_2021_09.xlsx'
    data_2020='C:/Users/Darragh/Documents/Python/Work/Data/NL_2020.xlsx'
    data_2019='C:/Users/Darragh/Documents/Python/Work/Data/NL_2019.xlsx'

@st.cache
def load_ledger_data(x):
    return pd.read_excel(x)

forecast_resourcing=load_ledger_data('C:/Users/Darragh/Documents/Python/Work/Data/resource_planner_export_11_06_2021.xlsx')
cached_2021=load_ledger_data(data_2021).copy()
cached_2020=load_ledger_data(data_2020).copy()
cached_2019=load_ledger_data(data_2019).copy()

with st.echo():
    forecast_project_mapping=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/Project_Codes_2021_.xlsx', sheet_name='Sheet2')
    coding_acc_schedule = (pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/account_numbers.xlsx')).iloc[:,:3]
    coding_sort=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/account_numbers.xlsx', sheet_name='Sheet2')
    Project_codes=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/Project_Codes_2021_.xlsx').rename(columns = {'User Code' : 'SUBANALYSIS 0'})

@st.cache
def nl_raw_clean_file(x, coding_acc_schedule):
    # st.write(x.head())
    x['Acc_Schedule']=x['Account Code'].str[:3]
    x['Acc_Schedule']=pd.to_numeric(x['Acc_Schedule'])
    x['Project']=x['Project'].replace({'1-Z-253 Eureka 2':'1-Z-209 Eureka'}) # replace Eureka 2 with Eureka 1 as tag-on
    x['Project_Code'] = x['Project'].str[:8]
    x['Project_Name'] = x['Project'].str[8:]
    x['Acc_Number'] = x['Account Code']
    x['Journal Amount'] = x['Journal Amount'] * -1
    x = x.merge (coding_acc_schedule, on='Acc_Number',how='outer')
    x['Department'] = x['Department'].replace( {'T0000':"TV",'CG000':"CG",
    'P0000':"Post",'A0000':"Admin",'D0000':"Development",'I0000':"IT",'R0000':"Pipeline",'HR000':"HR"})
    x['calendar_month']=x['Per.'].map({1:9,2:10,3:11,4:12,5:1,6:2,7:3,8:4,9:5,10:6,11:7,12:8,19:8})
    x['calendar_year'] = np.where((x['Per.'] > 4.1), x['Yr.'], x['Yr.']-1)
    x['calendar_year']=x['calendar_year']+2000
    x=x.rename(columns={'calendar_year':'year', 'calendar_month':'month'})
    x['month']=np.where(x['Jrn. No.']=='BUK0000979', 3, x['month']) # CLEAN UK SIDE WHERE MARCH AND APRIL WERE ENTERED IN SAME PERIOD
    x['month']=np.where(x['Jrn. No.']=='BUK0000913', 4, x['month'])
    x['month']=np.where(x['Jrn. No.']=='BUK0000914', 4, x['month'])
    x['month']=np.where(x['Jrn. No.']=='BUK0000903', 3, x['month'])
    x['day']=1
    x['date']=pd.to_datetime(x[['year','month','day']],infer_datetime_format=True)
    # x['calendar_month']=x['Per.'].map({1:9,2:10,3:11,4:12,5:1,6:2,7:3,8:4,9:5,10:6,11:7,12:8,19:8})
    # x['calendar_year'] = np.where((x['Per.'] > 4.1), x['Yr.'], x['Yr.']-1)
    x_1=x.join(x['Employee'].str.split(' ', expand=True).rename(columns={0:'EE',1:'Name_EE'}))
    x_1['Employee - Ext. Code']=x_1['EE']

    return x_1


NL_Data_21=nl_raw_clean_file(cached_2021,coding_acc_schedule) # MUTATION
NL_Data_20=nl_raw_clean_file(cached_2020,coding_acc_schedule) # MUTATION
NL_Data_19=nl_raw_clean_file(cached_2019,coding_acc_schedule)
# st.write(NL_Data_19.head())

consol_headcount_data=pd.concat([NL_Data_19,NL_Data_20,NL_Data_21],ignore_index=True)



# cleaned_data=clean_wrangle_headcount(consol_headcount_data)

def headcount_paye_account(data):
    # Using 
    x=data.query('(`Account Code`=="909-0210")')
    journal_list = x['Jrn. No.'].unique()
    filter_paye=data['Jrn. No.'].isin(journal_list)
    data['filtered_paye_headcount'] = data['Jrn. No.'].where(filter_paye)
    data=data[data['filtered_paye_headcount'].notna()]
    return data.query('(`Account Code`=="921-0500") or (`Account Code`=="940-0500")').loc[:,
    ['Journal Amount','Employee','Src. Account','Jrn. No.','year','month','date','Project','Employee - Ext. Code',
    'Acc_Schedule','Project_Name','Department','Description']]

# st.write('PAYE Journal data')
headcount_paye=headcount_paye_account(consol_headcount_data)
# st.write(headcount_paye_account(consol_headcount_data))

def bbf_employees(x):
    x['Employee - Ext. Code'] = pd.to_numeric(x['Employee - Ext. Code'])
    x= x.query('`Employee - Ext. Code`>0.5')
    x = x.query('`Src. Account`!="BUK02"')
    x['Payroll_Amt'] = x.groupby (['year','month','Employee - Ext. Code','Jrn. No.'])['Journal Amount'].transform('sum')
    x['Headcount'] = x['Journal Amount'] / x['Payroll_Amt']
    x=x.replace([np.inf, -np.inf], np.nan) # due to 0 dividing by the journal amount
    x['Category']='BBF'
    x['Headcount']=pd.to_numeric(x['Headcount'])
    return x

bbf_headcount_data=bbf_employees(headcount_paye)
def pivot_report(bbf_headcount_data,filter='Employee'):
    summary= pd.pivot_table(bbf_headcount_data, values='Headcount',index=[filter], columns=['date'],margins=True,aggfunc='sum',fill_value=0)
    summary = summary.sort_values(by=['All'],ascending=False)
    return summary.reset_index().set_index(filter)
# st.write('paye data')
with st.beta_expander('BBF Staff by Employee by Month'):
    st.write(pivot_report(bbf_headcount_data,filter='Employee'))
# david = headcount_paye[ (headcount_paye['Employee'].str.contains('Camle') &( headcount_paye['month']==12) &( headcount_paye['year']==2018) ) ]
# st.write(david)

def clean_wrangle_headcount(data):
    x=data.query('(`Account Code`=="921-0500") or (`Account Code`=="940-0500")').loc[:,
    ['Journal Amount','Employee','Src. Account','Jrn. No.','year','month','date','Project','Employee - Ext. Code',
    'Acc_Schedule','Project_Name','Department','Description']]
    x=x.query('`Jrn. No.`!="000007362"') # Accrual made in march '21 which has UK employee numbers
    x=x.query('`Jrn. No.`!="X00007362"') # reversal of above accrual
    x=x.query('`Jrn. No.`!="000007470"') # pension might need to fix in may will see
    x=x.query('`Jrn. No.`!="000007465"') # pension might need to fix in may will see
    x['month']=np.where(x['Jrn. No.']=='9SM-BBF146', 3, x['month'])
    x['month']=np.where(x['Jrn. No.']=='9SM-BBF144', 1, x['month'])
    x['month']=np.where(x['Jrn. No.']=='9SM-BBF142', 12, x['month'])
    x['year']=np.where(x['Jrn. No.']=='9SM-BBF142', 20, x['year'])
    x['month']=np.where(x['Jrn. No.']=='9SM-BBF141', 11, x['month'])
    x['year']=np.where(x['Jrn. No.']=='9SM-BBF141', 20, x['year'])
    x['month']=pd.to_numeric(x['month'])
    x=x.query('`Jrn. No.`!="9SM-BBF1CN"') # J Reeves credit note and invoice
    x=x.query('`Jrn. No.`!="9SMBBF139"') # J Reeves credit note and invoice
    x=x.query('`Jrn. No.`!="000007163"') # Malcolm vanA reclass
    x=x.query('`Jrn. No.`!="000007208"') # Malcolm vanA deposit
    x=x.query('`Jrn. No.`!="000007459"') # Luke reclass in April 21 from IT to Pipeline
    x=x.query('`Jrn. No.`!="BUK00009IN"')
    x=x.query('`Jrn. No.`!="BUK00009CN"')
    return x

cleaned_data=clean_wrangle_headcount(consol_headcount_data)

def mauve_staff(x):
    group_supplier=x.groupby(['Src. Account','Jrn. No.','year','month','Project','Acc_Schedule',
    'Project_Name','Department','Description','date'])['Journal Amount'].sum().reset_index()
    # group_UK = x.query('`Src. Account`=="BUK02"')
    mauve = group_supplier.query('`Src. Account`!="BUK02"')
    # credit_filter=(mauve['Jrn. No.'].str.contains('CN')) or (mauve['Jrn. No.'].str.contains('CR'))
    credit_filter=(mauve['Jrn. No.'].str.contains('CN'))
    credit_filter_cr=(mauve['Jrn. No.'].str.contains('CR'))
    filter_bbf_recharge=(mauve['Jrn. No.'].str.contains('BBF'))
    mauve['credit_notes']=mauve['Jrn. No.'].where(credit_filter)
    mauve=mauve[mauve['credit_notes'].isna()]
    mauve['credit_notes']=mauve['Jrn. No.'].where(credit_filter_cr)
    mauve=mauve[mauve['credit_notes'].isna()]
    mauve['credit_notes']=mauve['Jrn. No.'].where(filter_bbf_recharge)
    mauve=mauve[mauve['credit_notes'].isna()]
    # st.write(mauve[mauve['Jrn. No.'].str.contains('CR')])
    # Mauve_2021=credit_notes_resolve(group_no_UK).reset_index()
    mauve['Payroll_Amt'] = mauve.groupby (['Jrn. No.'])['Journal Amount'].transform('sum')
    mauve['Headcount'] = mauve['Journal Amount'] / mauve['Payroll_Amt']
    mauve['Category']='Mauve'
    # mauve = headcount_date_clean(Mauve_2021)
    return mauve

mauve=mauve_staff(cleaned_data)
# st.write(mauve)
st.write(mauve[mauve['Src. Account']=='']) # to check that only invoices from suppliers are included, don't want journals included
mauve_pivot=pivot_report(mauve,filter='Jrn. No.')
with st.beta_expander('Mauve Staff by Invoice Number by Month'):
    st.write(mauve_pivot)

group_UK = cleaned_data.query('`Src. Account`=="BUK02"')
# st.write(group_UK[(group_UK['month']==12) & (group_UK['year']==2020)] )
# st.write(group_UK[group_UK['Description'].str.contains('BBF UK recharge for Leigh Fieldhouse Payroll April 20')])
# st.write(group_UK[group_UK['Jrn. No.'].str.contains('000914')])
group_UK['Payroll_Amt'] = group_UK.groupby (['Jrn. No.','Description'])['Journal Amount'].transform('sum')
group_UK['Headcount'] = group_UK['Journal Amount'] / group_UK['Payroll_Amt']
# group_UK['month']=np.where(group_UK['Jrn. No.']=='BUK0000979', 3, group_UK['month'])
group_UK['Category']='BBF_UK'
group_UK['Headcount']=pd.to_numeric(group_UK['Headcount'])
uk_pivot=pivot_report(group_UK,filter='Description')
with st.beta_expander('UK Staff by Description by Month'):
    st.write(uk_pivot)
