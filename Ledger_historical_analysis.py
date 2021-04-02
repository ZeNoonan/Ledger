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
headcount_actual_plus_forecast,headcount_actual_plus_forecast_with_subtotal,data_for_graphing, group_by_monthly_by_production, acc_schedule_find,
test_gp_by_project,gp_percent_by_project,gp_revenue_concat,format_table,headcount_921_940,format_dataframe,pivot_headcount_dept,forecast_resourcing_dept,
test_forecast_resourcing_dept,new_headcount_actual_plus_forecast,
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

cached_2021=load_ledger_data(data_2021).copy()
cached_2020=load_ledger_data(data_2020).copy()
cached_2016_19=load_ledger_data(data_2016_19).copy()

NL_Data_21=load_data(cached_2021,coding_acc_schedule) # MUTATION
NL_Data_20=load_data(cached_2020,coding_acc_schedule) # MUTATION
NL_Data_16_19=load_16_19_clean(cached_2016_19,coding_acc_schedule) # MUTATION

consol_headcount_data=df_concat(NL_Data_16_19,NL_Data_20,NL_Data_21).copy()

with st.beta_expander('Click to see Actual Direct Headcount from 2015 to Current Date broken down by production'):
    actual_headcount_direct=(pivot_headcount(final_headcount(consol_headcount_data,'921-0500')))
    st.write('pivot by month of headcount')
    st.write(format_gp(actual_headcount_direct))

# https://stackoverflow.com/questions/14745022/how-to-split-a-dataframe-string-column-into-two-columns
# https://stackoverflow.com/questions/49795825/skip-nan-and-shift-elements-in-a-pandas-dataframe-row  

with st.beta_expander('Click to see Forecast Direct Headcount from Current Date onwards broken down by production'):
    forecast_headcount_direct=forecast_resourcing_function(forecast_test,forecast_project_mapping,start_forecast_period_resourcing_tool)
    st.write(format_gp(headcount_actual_plus_forecast_with_subtotal(forecast_headcount_direct)))

with st.beta_expander('Click to see Actual + Forecast Direct Headcount from 2015 onwards broken down by production'):

    full_headcount_actual_forecast_no_subtotal=headcount_actual_plus_forecast(actual_headcount_direct,forecast_headcount_direct)
    full_headcount_actual_forecast_yes_subtotal=headcount_actual_plus_forecast_with_subtotal(full_headcount_actual_forecast_no_subtotal)
    st.write('Actual plus Forecast',format_gp(full_headcount_actual_forecast_yes_subtotal))

with st.beta_expander('Click to see Actual + Forecast Direct Headcount from Month 1 to Month end to compare productions'):
    st.write ('Possibly could use this for graphing')
    actual_plus_forecast_headcount = create_pivot_comparing_production_headcount(full_headcount_actual_forecast_yes_subtotal.sort_values(by='All',ascending=False))
    st.write(format_gp(actual_plus_forecast_headcount))

with st.beta_expander('Click to see Actual + Forecast Direct Headcount from Month 1 to Month end to compare productions'):
    st.write('will need to think about graphing only the top 25 projects or something like that, will see when I do the graphs')
    st.write(data_for_graphing(full_headcount_actual_forecast_no_subtotal))

with st.beta_expander('Overhead Headcount'):
    st.write('overhead headcount')
    # st.write('consol headcount data', consol_headcount_data.head())
    # overhead_headcount=pivot_headcount(final_headcount(consol_headcount_data,'940-0500'))
    # st.write(format_gp(overhead_headcount))
    new_headcount=pivot_headcount_dept(headcount_921_940(consol_headcount_data))
    prelim_data=headcount_921_940(consol_headcount_data)
    st.write('new 921 and 940 total')
    st.write(format_dataframe(new_headcount))
    # st.write('need to seperate out amounts between 921 and 940')
    # st.write(prelim_data.head())
    data_headcount_921=prelim_data.query('`Acc_Schedule`==921')
    data_headcount_940=prelim_data.query('`Acc_Schedule`==940')
    # st.write(data_headcount_921.head())
    st.write('this is updated headcount for 921 and 940 broken down by Project')
    st.write(format_dataframe(pivot_headcount(data_headcount_921)))
    st.write(format_dataframe(pivot_headcount(data_headcount_940)))
    st.write('this is updated headcount for 921 and 940 broken down by Department')
    st.write(format_dataframe(pivot_headcount_dept(data_headcount_921)))
    st.write(format_dataframe(pivot_headcount_dept(data_headcount_940)))


with st.beta_expander('Historical GP Analysis'):
    # NL_Revenue = gp_by_project_sales_cos(NL_Data_21, coding_acc_schedule,Schedule_Name='Revenue', Department=None)
    # Revenue_alt = group_by_monthly_by_production(NL_Data_21,coding_acc_schedule,Schedule_Name='Revenue',Department=None)
    st.write('Historical GP Table')
    data_2016_current=consol_headcount_data
    production_revenue=(acc_schedule_find(data_2016_current, 'Revenue'))
    production_gross_profit =test_gp_by_project(data_2016_current)
    production_gp_percent=gp_percent_by_project(production_gross_profit,production_revenue)
    revenue_gp_gp_percent_table = gp_revenue_concat(production_gross_profit, production_revenue,production_gp_percent)
    st.write(format_gp(revenue_gp_gp_percent_table))

with st.beta_expander('Overall Headcount to date broken down by Department'):
    data_graphing_actual_to_date=headcount_921_940(consol_headcount_data)
    # st.write(data_graphing_actual_to_date.head())
    actual_pivot=pivot_headcount_dept(data_graphing_actual_to_date)
    st.write(format_dataframe(actual_pivot))

with st.beta_expander('Overall Headcount to date broken down by Project'):
    st.write(format_dataframe(pivot_headcount(data_graphing_actual_to_date)))

with st.beta_expander('Try and work with the forecast data'):
    forecast_pivot=test_forecast_resourcing_dept(forecast_test,forecast_project_mapping,start_forecast_period_resourcing_tool)
    # st.write('is there an All subtotal in this dont think there should be', forecast_pivot)
    # with_subtotal=headcount_actual_plus_forecast_with_subtotal(forecast_pivot)
    # st.write(format_dataframe(with_subtotal))

    # merging actual plus forecast
    # st.write('actual pivot check for all',actual_pivot.head())
    # st.write('forecast pivot check for all',forecast_pivot.head())
    test_merge=new_headcount_actual_plus_forecast(actual_pivot,forecast_pivot).ffill(axis=1)
    # st.write('test concat', test_merge)
    st.write(format_dataframe(headcount_actual_plus_forecast_with_subtotal(test_merge)))


