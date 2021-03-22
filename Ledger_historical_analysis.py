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

st.write('Select start of forecast period below and actual')
with st.echo():
    start_forecast_period_resourcing_tool='2021-03-01 00:00:00'
    data_2021='C:/Users/Darragh/Documents/Python/Work/Data/NL_2021_06.xlsx'

data_2020='C:/Users/Darragh/Documents/Python/Work/Data/NL_2020.xlsx'
data_2016_19='C:/Users/Darragh/Documents/Python/Work/Data/NL_2016_2019.xlsx'
forecast_resourcing_file='C:/Users/Darragh/Documents/Python/Work/Data/Resource_Planner_v0005_2021-03-18 11_14_58.xlsx'
forecast_project_mapping=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/Project_Codes_2021_.xlsx', sheet_name='Sheet2')

@st.cache
def load_ledger_data(data_2021):
    return pd.read_excel(data_2021)


coding_acc_schedule = (pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/account_numbers.xlsx')).iloc[:,:3]
coding_sort=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/account_numbers.xlsx', sheet_name='Sheet2')


def month_period_clean(x):
    x['calendar_month']=x['Per.'].map({1:9,2:10,3:11,4:12,5:1,6:2,7:3,8:4,9:5,10:6,11:7,12:8,19:8})
    x['calendar_year'] = np.where((x['Per.'] > 4.1), x['Yr.'], x['Yr.']-1)
    return x



# this is 2021 YEAR
st.write('this is mutating below for 2021 data')
NL = load_ledger_data(data_2021).copy()
stop_mutating_df = NL_Raw_Clean_File(NL, coding_acc_schedule)

NL_Data = month_period_clean(stop_mutating_df).copy()

st.write('but looks like 2016-2019 data is not being mutatated WHY')
NL_16_19 = load_ledger_data(data_2016_19).copy()
NL_Data_16_19 = NL_Raw_Clean_File(NL_16_19, coding_acc_schedule)

NL_Data_16_19=NL_Data_16_19.join(NL_Data_16_19['Employee'].str.split(' ', expand=True).rename(columns={0:'EE',1:'Name_EE'}))
NL_Data_16_19['Employee - Ext. Code']=NL_Data_16_19['EE']
NL_Data_16_19=month_period_clean(NL_Data_16_19)

st.write('2020 data is mutating')
NL_20 = load_ledger_data(data_2020).copy()
stop_mutating_df_20=NL_Raw_Clean_File(NL_20, coding_acc_schedule)
NL_Data_20 = month_period_clean(stop_mutating_df_20)


@st.cache
def df_concat():
    return pd.concat([NL_Data_16_19,NL_Data_20,NL_Data],ignore_index=True)
# BUT I HAVE THE PROBLEM OF YEAR for example, period 3 which is equal to November in year 2016 will be made to Nov '16 when it should be Nov '15


consol_headcount_data=df_concat().copy()
headcount_filtered=final_headcount(consol_headcount_data).groupby('date').head(2)
st.write('headcount filtered by top 2 in every month')
st.write(headcount_filtered)

pivot_headcount_summary=(pivot_headcount(final_headcount(consol_headcount_data)))
st.write('pivot by month of headcount')
st.write(format_gp(pivot_headcount_summary))

st.write('data to plot headcount numbers')
st.write(format_gp(create_pivot_comparing_production_headcount(pivot_headcount_summary)))
# https://stackoverflow.com/questions/14745022/how-to-split-a-dataframe-string-column-into-two-columns
# https://stackoverflow.com/questions/49795825/skip-nan-and-shift-elements-in-a-pandas-dataframe-row  

st.write('xxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
st.write('this is forecast headcount section')
forecast_resourcing=load_ledger_data(forecast_resourcing_file).copy()
forecast_resourcing=(pd.merge(forecast_resourcing,forecast_project_mapping,on='Project',how='outer')).drop('Project',axis=1).rename(columns={'Project_name':'Project'})

forecast_resourcing.columns= forecast_resourcing.columns.astype(str)
sliced_headcount_df=(forecast_resourcing.loc[:,start_forecast_period_resourcing_tool:])
sliced_headcount=sliced_headcount_df.set_index('Project').unstack(level='Project').reset_index().rename(columns={'level_0':'date',0:'headcount'})
# st.write(sliced_headcount)

forecast_headcount=sliced_headcount.groupby(['Project','date'])['headcount'].sum().reset_index()
summary_pivot= pd.pivot_table(forecast_headcount, values='headcount',index=['Project'], columns=['date'],fill_value=0)
# st.write(forecast_headcount)
st.write(summary_pivot)

st.write('xxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
st.write('this is section for actual plus forecast')
pivot_headcount_summary=pivot_headcount_summary.drop('All',axis=1).drop(['All'])
merged_headcount_forecast=pd.concat([pivot_headcount_summary,summary_pivot],axis=1)

st.write('Need to get the pivot data in a long format I think so that I can graph it')
long_headcount_data = merged_headcount_forecast
long_headcount_data=long_headcount_data.unstack(level='Project').reset_index().rename(columns={0:'headcount'})
st.write('will need to think about graphing only the top 25 projects or something like that, will see when I do the graphs')
st.write(long_headcount_data)


merged_headcount_forecast.loc['All']= merged_headcount_forecast.sum(numeric_only=True, axis=0)
merged_headcount_forecast.loc[:,'All'] = merged_headcount_forecast.sum(numeric_only=True, axis=1)
st.write(format_gp(merged_headcount_forecast.sort_values(by='All',ascending=False)))

actual_plus_forecast_headcount = create_pivot_comparing_production_headcount(merged_headcount_forecast.sort_values(by='All',ascending=False)) 
st.write(format_gp(actual_plus_forecast_headcount))



