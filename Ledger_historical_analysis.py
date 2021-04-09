import pandas as pd
import numpy as np
import streamlit as st
import datetime
import os
import base64
from io import BytesIO
import altair as alt

# from Ledger_helper_functions import*
from Ledger_helper_functions import (Budget_Raw_Clean_File,NL_Raw_Clean_File, date_selection_for_PL, PL_generation, merge_pl_dataframe,clean_format_PL_presentation,
pretty_PL_format,ytd_column_forecast,month_column_forecast,pl_dept_generation, end_of_year_forecast, end_of_year_forecast_dept, gp_by_project,
long_format_budget,long_format_nl, format_gp, gp_nl_budget_comp, budget_forecast_gp,gp_by_project_sales_cos,
budget_forecast_gp_sales_cos, get_total_by_month,credit_notes_resolve,UK_clean_921,company_ee_project,combined_921_headcount,pivot_headcount,
final_headcount,create_pivot_comparing_production_headcount,load_ledger_data,month_period_clean,load_data,load_16_19_clean,forecast_resourcing_function,df_concat,
headcount_actual_plus_forecast,headcount_actual_plus_forecast_with_subtotal,data_for_graphing, group_by_monthly_by_production, acc_schedule_find,
test_gp_by_project,gp_percent_by_project,gp_revenue_concat,format_table,headcount_921_940,format_dataframe,pivot_headcount_dept,forecast_resourcing_dept,
test_forecast_resourcing_dept,new_headcount_actual_plus_forecast, data_for_graphing_dept,headcount_concat,forecast_resourcing_test,to_excel,
test_pivot_headcount,get_table_download_link,chart_gp,
)

st.set_page_config(layout="wide")

st.write('CLEAN UP THE TESTS AND RE-RUN THEN CHECK EXPORT TO EXCEL')


st.write('Select start of forecast period below and actual')
with st.echo():
    start_forecast_period_resourcing_tool='2021-03-01 00:00:00'
    data_2021='C:/Users/Darragh/Documents/Python/Work/Data/NL_2021_06.xlsx'

data_2020='C:/Users/Darragh/Documents/Python/Work/Data/NL_2020.xlsx'
data_2016_19='C:/Users/Darragh/Documents/Python/Work/Data/NL_2016_2019.xlsx'
forecast_resourcing_file=('C:/Users/Darragh/Documents/Python/Work/Data/Resource_Planner_v0005_2021-03-18 11_14_58.xlsx')
forecast_test=load_ledger_data('C:/Users/Darragh/Documents/Python/Work/Data/Resource_Planner_v0005_2021-03-18 11_14_58.xlsx')
st.write('Check these after importing new data should try with Forecast 2')
with st.echo():
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

# # https://stackoverflow.com/questions/14745022/how-to-split-a-dataframe-string-column-into-two-columns
# # https://stackoverflow.com/questions/49795825/skip-nan-and-shift-elements-in-a-pandas-dataframe-row  

with st.beta_expander('Actual Headcount for 940'):
    new_headcount=pivot_headcount_dept(headcount_921_940(consol_headcount_data))
    prelim_data=headcount_921_940(consol_headcount_data)
    data_headcount_921=prelim_data.query('`Acc_Schedule`==921')
    data_headcount_940=prelim_data.query('`Acc_Schedule`==940')
    st.write(format_dataframe(pivot_headcount(data_headcount_940)))
    st.markdown(get_table_download_link(pivot_headcount(data_headcount_940)), unsafe_allow_html=True)

with st.beta_expander('Overall Headcount to date broken down by Department'):
    data_graphing_actual_to_date=headcount_921_940(consol_headcount_data)
    actual_pivot=pivot_headcount_dept(data_graphing_actual_to_date)
    st.write(format_dataframe(actual_pivot))
    st.markdown(get_table_download_link(format_dataframe(actual_pivot)), unsafe_allow_html=True)

with st.beta_expander('Overall Headcount by Dept for Actual + Forecast'):
    forecast_pivot=test_forecast_resourcing_dept(forecast_test,forecast_project_mapping,start_forecast_period_resourcing_tool)
    updated=new_headcount_actual_plus_forecast(actual_pivot,forecast_pivot).ffill(axis=1)
    updated_subtotal=headcount_actual_plus_forecast_with_subtotal(updated)
    st.write(format_dataframe(updated_subtotal))
    st.markdown(get_table_download_link(updated_subtotal), unsafe_allow_html=True)
    st.write('Data friendly version for graphing below')
    data_graph=data_for_graphing_dept(updated)
    st.write(data_graph.head())
    st.markdown(get_table_download_link(data_graph), unsafe_allow_html=True)
    st.write('check sum should match total of above', data_graph['headcount'].sum())
    st.write('sum of above dataframe', updated_subtotal.loc['All','All'])
    st.write('True means both amounts match',data_graph['headcount'].sum()==updated_subtotal.loc['All','All'])

with st.beta_expander('Overall Headcount to date broken down by Project'):
    st.write(format_dataframe(test_pivot_headcount(data_graphing_actual_to_date)))
    st.markdown(get_table_download_link(pivot_headcount(data_graphing_actual_to_date)), unsafe_allow_html=True)

with st.beta_expander('921 Headcount by Project - actual + forecast'):
    forecast_headcount_direct=forecast_resourcing_function(forecast_test,forecast_project_mapping,start_forecast_period_resourcing_tool)
    test_forecast_headcount_direct=forecast_resourcing_test(forecast_test,forecast_project_mapping,start_forecast_period_resourcing_tool)
    pivot_921_actual=pivot_headcount(data_headcount_921)
    test_pivot_921_actual=test_pivot_headcount(data_headcount_921)
    concat_df = headcount_actual_plus_forecast(pivot_921_actual,forecast_headcount_direct)
    test_concat_df = headcount_actual_plus_forecast(test_pivot_921_actual,test_forecast_headcount_direct)
    with_subtotal = headcount_actual_plus_forecast_with_subtotal(concat_df)
    test_with_subtotal = headcount_actual_plus_forecast_with_subtotal(test_concat_df)
    # st.write(format_dataframe(with_subtotal))
    st.write(format_dataframe(test_with_subtotal))
    st.markdown(get_table_download_link(test_with_subtotal), unsafe_allow_html=True)
    st.write(with_subtotal.loc['All','All'])
    st.write('test',test_with_subtotal.loc['All','All'])

with st.beta_expander('Click to see Actual + Forecast Direct Headcount from Month 1 to Month End to compare productions from Month 1'):
    st.write ('Use this for graphing')
    actual_plus_forecast_headcount = create_pivot_comparing_production_headcount(with_subtotal.sort_values(by='All',ascending=False))
    test_actual_plus_forecast_headcount = create_pivot_comparing_production_headcount(test_with_subtotal.sort_values(by='All',ascending=False))
    st.write(format_gp(test_actual_plus_forecast_headcount))
    st.markdown(get_table_download_link(test_actual_plus_forecast_headcount), unsafe_allow_html=True)
    st.write ('Check that total equals 921 in above')
    st.write('test check below')
    st.write(test_actual_plus_forecast_headcount.sum().sum())
    st.write('921 dataframe',test_with_subtotal.loc['All','All'])

with st.beta_expander('Historical GP Analysis'):
    st.write('Historical GP Table')
    data_2016_current=consol_headcount_data
    production_revenue=(acc_schedule_find(data_2016_current, 'Revenue'))
    production_gross_profit =test_gp_by_project(data_2016_current)
    production_gp_percent=gp_percent_by_project(production_gross_profit,production_revenue)
    revenue_gp_gp_percent_table = (gp_revenue_concat(production_gross_profit, production_revenue,production_gp_percent))
    graphing_gp = revenue_gp_gp_percent_table.query('`Revenue`>5200000').reset_index()
    st.write(graphing_gp.sort_values(by='GP %', ascending=False))
    st.write(revenue_gp_gp_percent_table.query('`Revenue`>5200000').sort_values(by='Revenue',ascending=False))
    st.write(format_gp(revenue_gp_gp_percent_table))
    st.markdown(get_table_download_link(revenue_gp_gp_percent_table), unsafe_allow_html=True)
    st.altair_chart(chart_gp(graphing_gp),use_container_width=True)


# def chart_gp(x):
#     return alt.Chart(x).mark_circle(size=200).encode(
#         alt.X('GP %',scale=alt.Scale(zero=False)),
#         y='Gross_Profit',
#         color='Project_Name',
#         tooltip='Project_Name',
#     ).interactive()

