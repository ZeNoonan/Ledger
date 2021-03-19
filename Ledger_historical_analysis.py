import pandas as pd
import numpy as np
import streamlit as st
import datetime

# from Ledger_helper_functions import*
from Ledger_helper_functions import (Budget_Raw_Clean_File,NL_Raw_Clean_File, date_selection_for_PL, PL_generation, merge_pl_dataframe,clean_format_PL_presentation,
pretty_PL_format,ytd_column_forecast,month_column_forecast,pl_dept_generation, end_of_year_forecast, end_of_year_forecast_dept, gp_by_project,
long_format_budget,long_format_nl, format_gp, gp_nl_budget_comp, budget_forecast_gp,gp_by_project_sales_cos,
budget_forecast_gp_sales_cos, get_total_by_month,credit_notes_resolve,UK_clean_921,company_ee_project,combined_921_headcount,pivot_headcount,
final_headcount,create_pivot_comparing_production_headcount)

st.set_page_config(layout="wide")

Project_codes=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/Project_Codes_2021_.xlsx').rename(columns = {'User Code' : 'SUBANALYSIS 0'})

data_2021='C:/Users/Darragh/Documents/Python/Work/Data/NL_2021_06.xlsx'
data_2020='C:/Users/Darragh/Documents/Python/Work/Data/NL_2020.xlsx'
data_2016_20='C:/Users/Darragh/Documents/Python/Work/Data/NL_2016_2019.xlsx'
forecast_resourcing_file='C:/Users/Darragh/Documents/Python/Work/Data/Resource_Planner_v0005_2021-03-18 11_14_58.xlsx'
forecast_project_mapping=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/Project_Codes_2021_.xlsx', sheet_name='Sheet2')

@st.cache
def load_ledger_data(data_2021):
    return pd.read_excel(data_2021)

NL = load_ledger_data(data_2021).copy()
coding_acc_schedule = (pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/account_numbers.xlsx')).iloc[:,:3]
coding_sort=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/account_numbers.xlsx', sheet_name='Sheet2')
NL_Data = NL_Raw_Clean_File(NL, coding_acc_schedule)

NL_16_20 = load_ledger_data(data_2016_20).copy()
NL_Data_16_20 = NL_Raw_Clean_File(NL_16_20, coding_acc_schedule)
NL_Data_16_20=NL_Data_16_20.join(NL_Data_16_20['Employee'].str.split(' ', expand=True).rename(columns={0:'EE',1:'Name_EE'}))
NL_Data_16_20['Employee - Ext. Code']=NL_Data_16_20['EE']

NL_20 = load_ledger_data(data_2020).copy()
NL_Data_20 = NL_Raw_Clean_File(NL_20, coding_acc_schedule)

@st.cache
def df_concat():
    return pd.concat([NL_Data_16_20,NL_Data_20,NL_Data],ignore_index=True)

consol_headcount_data=df_concat().copy()
headcount_filtered=final_headcount(consol_headcount_data).groupby('date').head(2)
pivot_headcount_summary=format_gp(pivot_headcount(final_headcount(consol_headcount_data)))
st.write('headcount filtered by top 2 in every month')
st.write(headcount_filtered)
st.write('pivot by month of headcount')
st.write(pivot_headcount_summary)
st.write('data to plot headcount numbers')
st.write(format_gp(create_pivot_comparing_production_headcount(pivot_headcount(final_headcount(consol_headcount_data)))))
# https://stackoverflow.com/questions/14745022/how-to-split-a-dataframe-string-column-into-two-columns
# # https://stackoverflow.com/questions/49795825/skip-nan-and-shift-elements-in-a-pandas-dataframe-row  

st.write('xxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
forecast_resourcing=load_ledger_data(forecast_resourcing_file).copy()
forecast_resourcing=(pd.merge(forecast_resourcing,forecast_project_mapping,on='Project',how='outer')).drop('Project',axis=1).rename(columns={'Project_name':'Project'})
st.write(forecast_resourcing.head())
st.write('xxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
# st.write(pd.wide_to_long(forecast_resourcing,i='Project'))
# st.write(forecast_resourcing.set_index('Project').unstack(level='Project').reset_index())
# st.write(forecast_resourcing.set_index('Project').unstack())
st.write('xxxxxxxxxxxxxxxxxxxxxxxxxxxxx')

forecast_resourcing.columns= forecast_resourcing.columns.astype(str)
# st.write(forecast_resourcing.columns)
# st.write(forecast_resourcing.loc[:,['Title','Total Months']])
# st.write(forecast_resourcing.loc[:,['2021-03-01 00:00:00']])
sliced_headcount_df=(forecast_resourcing.loc[:,'2021-03-01 00:00:00':])
sliced_headcount=sliced_headcount_df.set_index('Project').unstack(level='Project').reset_index().rename(columns={'level_0':'date',0:'headcount'})
st.write(sliced_headcount)

st.write('xxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
# Project_col=forecast_resourcing.iloc[:,-1:] # to select Project
# months_headcount=forecast_resourcing.iloc[:,25:-1] # to select from march '21 to 2nd last column as last column has Project column
# st.write(months_headcount)
# df=pd.concat([Project_col, months_headcount],axis=1)
# st.write(df)
# st.write('xxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
# st.write(forecast_resourcing['Project'].unique())
