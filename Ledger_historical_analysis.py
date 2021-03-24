import pandas as pd
import numpy as np
import streamlit as st
import datetime

# from Ledger_helper_functions import*
from Ledger_helper_functions import (Budget_Raw_Clean_File,NL_Raw_Clean_File, date_selection_for_PL, PL_generation, merge_pl_dataframe,clean_format_PL_presentation,
pretty_PL_format,ytd_column_forecast,month_column_forecast,pl_dept_generation, end_of_year_forecast, end_of_year_forecast_dept, gp_by_project,
long_format_budget,long_format_nl, format_gp, gp_nl_budget_comp, budget_forecast_gp,gp_by_project_sales_cos,
budget_forecast_gp_sales_cos, get_total_by_month,credit_notes_resolve,UK_clean_921,company_ee_project,combined_921_headcount,pivot_headcount,
final_headcount,create_pivot_comparing_production_headcount,load_ledger_data,month_period_clean,load_data,load_16_19_clean,forecast_resourcing_function,df_concat,
headcount_actual_plus_forecast,
)

st.set_page_config(layout="wide")

st.write('Select start of forecast period below and actual')
with st.echo():
    start_forecast_period_resourcing_tool='2021-03-01 00:00:00'
    data_2021='C:/Users/Darragh/Documents/Python/Work/Data/NL_2021_06.xlsx'

data_2020='C:/Users/Darragh/Documents/Python/Work/Data/NL_2020.xlsx'
data_2016_19='C:/Users/Darragh/Documents/Python/Work/Data/NL_2016_2019.xlsx'
forecast_resourcing_file=('C:/Users/Darragh/Documents/Python/Work/Data/Resource_Planner_v0005_2021-03-18 11_14_58.xlsx')
forecast_test=load_ledger_data('C:/Users/Darragh/Documents/Python/Work/Data/Resource_Planner_v0005_2021-03-18 11_14_58.xlsx')
forecast_project_mapping=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/Project_Codes_2021_.xlsx', sheet_name='Sheet2')
coding_acc_schedule = (pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/account_numbers.xlsx')).iloc[:,:3]
coding_sort=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/account_numbers.xlsx', sheet_name='Sheet2')
Project_codes=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/Project_Codes_2021_.xlsx').rename(columns = {'User Code' : 'SUBANALYSIS 0'})

NL_Data_21=load_data(data_2021,coding_acc_schedule)
NL_Data_20=load_data(data_2020,coding_acc_schedule)
NL_Data_16_19=load_16_19_clean(data_2016_19,coding_acc_schedule)

# @st.cache
# def df_concat(NL_Data_16_19,NL_Data_20,NL_Data_21):
#     return pd.concat([NL_Data_16_19,NL_Data_20,NL_Data_21],ignore_index=True)
# BUT I HAVE THE PROBLEM OF YEAR for example, period 3 which is equal to November in year 2016 will be made to Nov '16 when it should be Nov '15

consol_headcount_data=df_concat(NL_Data_16_19,NL_Data_20,NL_Data_21).copy()
# headcount_filtered=final_headcount(consol_headcount_data).groupby('date').head(2)
# st.write('headcount filtered by top 2 in every month')
# st.write(headcount_filtered)

actual_headcount_direct=(pivot_headcount(final_headcount(consol_headcount_data)))
st.write('pivot by month of headcount')
st.write(format_gp(actual_headcount_direct))

# st.write('data to plot headcount numbers')
# st.write(format_gp(create_pivot_comparing_production_headcount(pivot_headcount_summary)))
# https://stackoverflow.com/questions/14745022/how-to-split-a-dataframe-string-column-into-two-columns
# https://stackoverflow.com/questions/49795825/skip-nan-and-shift-elements-in-a-pandas-dataframe-row  

st.write('xxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
st.write('this is forecast headcount section')
st.write('this is a test of forecast function')
forecast_headcount_direct=forecast_resourcing_function(forecast_test,forecast_project_mapping,start_forecast_period_resourcing_tool)
st.write(forecast_headcount_direct)
st.write('xxxxxxxxxxxxxxxxxxxxxxxxxxxxx')

st.write('this is section for actual plus forecast')

# def headcount_actual_plus_forecast(actual_headcount_direct,forecast_headcount_direct):
#     actual=actual_headcount_direct.drop('All',axis=1).drop(['All'])
#     merged=pd.concat([actual,forecast_headcount_direct],axis=1)
#     merged.loc['All']= merged.sum(numeric_only=True, axis=0)
#     merged.loc[:,'All'] = merged_headcount_forecast.sum(numeric_only=True, axis=1)
#     return merged.sort_values(by='All',ascending=False)

pivot_headcount_summary=actual_headcount_direct.drop('All',axis=1).drop(['All'])
merged_headcount_forecast=pd.concat([pivot_headcount_summary,forecast_headcount_direct],axis=1)

st.write('Need to get the pivot data in a long format I think so that I can graph it')
long_headcount_data = merged_headcount_forecast
long_headcount_data=long_headcount_data.unstack(level='Project').reset_index().rename(columns={0:'headcount'})
st.write('will need to think about graphing only the top 25 projects or something like that, will see when I do the graphs')
st.write(long_headcount_data)


merged_headcount_forecast.loc['All']= merged_headcount_forecast.sum(numeric_only=True, axis=0)
merged_headcount_forecast.loc[:,'All'] = merged_headcount_forecast.sum(numeric_only=True, axis=1)
# st.write(format_gp(merged_headcount_forecast.sort_values(by='All',ascending=False)))
st.write('Actual plus Forecast',format_gp(headcount_actual_plus_forecast(actual_headcount_direct,forecast_headcount_direct)))

actual_plus_forecast_headcount = create_pivot_comparing_production_headcount(merged_headcount_forecast.sort_values(by='All',ascending=False)) 
st.write(format_gp(actual_plus_forecast_headcount))



