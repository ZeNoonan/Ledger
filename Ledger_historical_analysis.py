import pandas as pd
import numpy as np
import streamlit as st

# from Ledger_helper_functions import*
from Ledger_helper_functions import (Budget_Raw_Clean_File,NL_Raw_Clean_File, date_selection_for_PL, PL_generation, merge_pl_dataframe,clean_format_PL_presentation,
pretty_PL_format,ytd_column_forecast,month_column_forecast,pl_dept_generation, end_of_year_forecast, end_of_year_forecast_dept, gp_by_project,
long_format_budget,long_format_nl, format_gp, gp_nl_budget_comp, budget_forecast_gp,gp_by_project_sales_cos,
budget_forecast_gp_sales_cos, get_total_by_month,credit_notes_resolve,UK_clean_921,company_ee_project,combined_921_headcount,pivot_headcount,final_headcount)

st.set_page_config(layout="wide")

Project_codes=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/Project_Codes_2021_.xlsx').rename(columns = {'User Code' : 'SUBANALYSIS 0'})

data_2021='C:/Users/Darragh/Documents/Python/Work/Data/NL_2021_06.xlsx'
data_2016_20='C:/Users/Darragh/Documents/Python/Work/Data/NL_2016_2019.xlsx'

@st.cache
def load_ledger_data(data_2021):
    return pd.read_excel(data_2021)

NL = load_ledger_data(data_2021).copy()
coding_acc_schedule = (pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/account_numbers.xlsx')).iloc[:,:3]
coding_sort=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/account_numbers.xlsx', sheet_name='Sheet2')
NL_Data = NL_Raw_Clean_File(NL, coding_acc_schedule)

NL_16_20 = load_ledger_data(data_2016_20).copy()
NL_Data_16_20 = NL_Raw_Clean_File(NL_16_20, coding_acc_schedule)

headcount_filtered=final_headcount(NL_Data).groupby('date').head(2)
pivot_headcount_summary=format_gp(pivot_headcount(final_headcount(NL_Data)))
st.write(headcount_filtered)
st.write(pivot_headcount_summary)

st.write('xxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
NL_Data_16_20=NL_Data_16_20.join(NL_Data_16_20['Employee'].str.split(' ', expand=True).rename(columns={0:'EE',1:'Name_EE'}))
# https://stackoverflow.com/questions/14745022/how-to-split-a-dataframe-string-column-into-two-columns
NL_Data_16_20['Employee - Ext. Code']=NL_Data_16_20['EE']
# st.write(NL_Data_16_20.query('`Account Code`=="921-0500"'))

# st.write(NL_Data_16_20.query('`Account Code`=="921-0500"').loc[:,
# ['Yr.','Per.','Description','Employee - Ext. Code','Employee','Journal Amount','Src. Account','Jrn. No.','Project']])


historical_data=final_headcount(NL_Data_16_20)
# st.write(historical_data.head())

headcount_filtered_16=final_headcount(NL_Data_16_20).groupby('date').head(2)
# pivot_headcount_summary_16=format_gp(pivot_headcount(final_headcount(NL_Data_16_20)))
pivot_headcount_summary_16=(pivot_headcount(final_headcount(NL_Data_16_20)))
st.write(headcount_filtered_16)
st.write(pivot_headcount_summary_16)