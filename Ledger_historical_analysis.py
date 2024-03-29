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
test_pivot_headcount,get_table_download_link,chart_gp,chart_area_headcount,data_for_graphing_overall,chart_gp_test,mauve_staff,pivot_headcount_mauve,
acc_schedule_find_monthly,test_gp_by_project_monthly,pivot_headcount_category,bbf_employees,pivot_headcount_ee,clean_wrangle_headcount,uk_staff,
pivot_headcount_uk,df_concat_20_21
)

st.set_page_config(layout="wide")

st.write('Only running 2021 numbers for the minute to debug and speed up')
st.header('check the headcount for month 1 to end of production to fix up that data')


st.write('Select start of forecast period below and actual')
with st.echo():
    start_forecast_period_resourcing_tool='2021-06-01 00:00:00'
    data_2021='C:/Users/Darragh/Documents/Python/Work/Data/NL_2021_10.xlsx'

data_2020='C:/Users/Darragh/Documents/Python/Work/Data/NL_2020.xlsx'
data_2019='C:/Users/Darragh/Documents/Python/Work/Data/NL_2019.xlsx'
data_2016_19='C:/Users/Darragh/Documents/Python/Work/Data/NL_2016_2019.xlsx'
data_2014_15='C:/Users/Darragh/Documents/Python/Work/Data/NL_2014_2015.xlsx'
# forecast_resourcing_file=('C:/Users/Darragh/Documents/Python/Work/Data/Resource_Planner_v0005_2021-03-18 11_14_58.xlsx')
# forecast_resourcing_file=('C:/Users/Darragh/Documents/Python/Work/Data/resourcing_planner_test.xlsx')
# forecast_test=load_ledger_data('C:/Users/Darragh/Documents/Python/Work/Data/Resource_Planner_v0005_2021-03-18 11_14_58.xlsx')
# forecast_test=load_ledger_data('C:/Users/Darragh/Documents/Python/Work/Data/resourcing_planner_test.xlsx')
forecast_test=load_ledger_data('C:/Users/Darragh/Documents/Python/Work/Data/resource_planner_export_11_06_2021.xlsx')

# st.write('is CG here', forecast_test)
st.write('Check these after importing new data should try with Forecast 2')
with st.echo():
    forecast_project_mapping=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/Project_Codes_2021_.xlsx', sheet_name='Sheet2')
    coding_acc_schedule = (pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/account_numbers.xlsx')).iloc[:,:3]
    coding_sort=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/account_numbers.xlsx', sheet_name='Sheet2')
    Project_codes=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/Project_Codes_2021_.xlsx').rename(columns = {'User Code' : 'SUBANALYSIS 0'})

cached_2021=load_ledger_data(data_2021).copy()
# st.write('cached_2021', cached_2021.head(2))
cached_2020=load_ledger_data(data_2020).copy()
cached_2019=load_ledger_data(data_2019).copy()
# cached_2016_19=load_ledger_data(data_2016_19).copy()
# cached_2014_15=load_ledger_data(data_2014_15).copy()
# cached_2016_19=pd.concat([cached_2016_19,cached_2014_15])

NL_Data_21=load_data(cached_2021,coding_acc_schedule) # MUTATION
NL_Data_20=load_data(cached_2020,coding_acc_schedule) # MUTATION
NL_Data_16_19=load_16_19_clean(cached_2019,coding_acc_schedule) # MUTATION
# NL_Data_16_19=load_16_19_clean(cached_2016_19,coding_acc_schedule) # MUTATION

with st.echo():
    # st.write('For Ease of loading no data before 2021 is loaded')
    consol_headcount_data=df_concat(NL_Data_16_19,NL_Data_20,NL_Data_21).copy()
    # consol_headcount_data=df_concat_20_21(NL_Data_20,NL_Data_21).copy()
    # consol_headcount_data=NL_Data_21.copy()

# # https://stackoverflow.com/questions/14745022/how-to-split-a-dataframe-string-column-into-two-columns
# # https://stackoverflow.com/questions/49795825/skip-nan-and-shift-elements-in-a-pandas-dataframe-row  

# with st.expander('Actual Headcount for 940'):
new_headcount=pivot_headcount_dept(headcount_921_940(consol_headcount_data))
prelim_data=headcount_921_940(consol_headcount_data)
data_headcount_921=prelim_data.query('`Acc_Schedule`==921')
data_headcount_940=prelim_data.query('`Acc_Schedule`==940')
st.write(format_dataframe(pivot_headcount(data_headcount_940)))
# st.markdown(get_table_download_link(pivot_headcount(data_headcount_940)), unsafe_allow_html=True)



with st.expander('Overall Headcount to date broken down by Location of Staff'):
    cleaned_data=clean_wrangle_headcount(consol_headcount_data)
    bbf_headcount_data=bbf_employees(cleaned_data)
    bbf_ee=pivot_headcount_ee(bbf_headcount_data)
    st.write('this is bbf employees',format_dataframe(bbf_ee))
    mauve_staff= mauve_staff(cleaned_data)
    st.write('mauve breakdown', pivot_headcount_mauve(mauve_staff))
    uk_staff = uk_staff(cleaned_data)
    st.write(pivot_headcount_uk(uk_staff))
    all_staff=pd.concat([bbf_headcount_data,mauve_staff,uk_staff])
    # test_1=all_staff.query('(`Department`=="IT") and (`month`==4)')
    # test_2=all_staff.query('(`Department`=="Pipeline") and (`month`==4)')
    # st.write('testing to see what IT issue in month 4 is', test_1)
    # st.write('testing to see what Pipeline issue in month 4 is', test_2)
    all_staff_pivot = format_dataframe(pivot_headcount_category(all_staff))
    st.write(all_staff_pivot)

with st.expander('Overall Headcount to date broken down by Department'):
    data_graphing_actual_to_date=headcount_921_940(consol_headcount_data)
    # st.write('consol headcount data',consol_headcount_data)
    # st.write('test data actual',data_graphing_actual_to_date.head())
    check=data_graphing_actual_to_date.groupby(['date'])['Headcount'].sum()
    # st.write('checking total', check)
    march=data_graphing_actual_to_date[data_graphing_actual_to_date['month']==3]
    # grouped_march=march.groupby(['Description','Employee - Ext. Code'])['Headcount'].sum().reset_index()
    # grouped_march=march.groupby(['Description','Category'])['Headcount'].sum().reset_index()
    # st.write(grouped_march.sort_values(by='Description'))
    # st.write('check this total matches',grouped_march['Headcount'].sum())
    # actual_pivot_category=pivot_headcount_category(data_graphing_actual_to_date)
    # st.write('category',format_dataframe(actual_pivot_category))
    # actual_pivot=pivot_headcount_dept(data_graphing_actual_to_date)
    # st.write(format_dataframe(actual_pivot))
    # st.markdown(get_table_download_link(format_dataframe(actual_pivot)), unsafe_allow_html=True)
    # check_dept_headcount = actual_pivot.loc['All','All']
    # st.write('testing using new functions xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    # cleaned_data=clean_wrangle_headcount(consol_headcount_data)
    # test_1=all_staff.query('(`Department`=="IT") and (`month`==4)')
    # test_2=all_staff.query('(`Department`=="Pipeline") and (`month`==4)')
    # st.write('testing to see what IT issue in month 4 is', test_1)
    # st.write('testing to see what Pipeline issue in month 4 is', test_2)
    
    actual_pivot=pivot_headcount_dept(all_staff)
    check_dept_headcount = actual_pivot.loc['All','All']
    st.write(format_dataframe(actual_pivot))
    # st.markdown(get_table_download_link(format_dataframe(actual_pivot)), unsafe_allow_html=True)
    
    # st.write('If True passes checked', check_dept_headcount==check_project_headcount)

with st.expander('Overall Headcount by Dept for Actual + Forecast'):
    forecast_pivot=test_forecast_resourcing_dept(forecast_test,forecast_project_mapping,start_forecast_period_resourcing_tool)
    # st.write(forecast_pivot)
    updated=new_headcount_actual_plus_forecast(actual_pivot,forecast_pivot).ffill(axis=1)
    updated_subtotal=headcount_actual_plus_forecast_with_subtotal(updated)
    st.write(format_dataframe(updated_subtotal))
    # st.markdown(get_table_download_link(updated_subtotal), unsafe_allow_html=True)
    st.write('Data friendly version for graphing below')
    data_graph=data_for_graphing_dept(x=updated, select_level='Department')
    st.write(data_graph.head())
    # st.markdown(get_table_download_link(data_graph), unsafe_allow_html=True)
    st.write('check sum should match total of above', data_graph['headcount'].sum())
    st.write('sum of above dataframe', updated_subtotal.loc['All','All'])
    st.write('True means both amounts match',data_graph['headcount'].sum()==updated_subtotal.loc['All','All'])
    st.altair_chart(chart_area_headcount(x=data_graph,select_coding='Department',tooltip_selection='headcount'),use_container_width=True)

with st.expander('Overall Headcount Total Actual + Forecast'):
    overall=data_for_graphing_overall(x=updated_subtotal, select_level='Department')
    # st.write(overall)
    st.altair_chart(chart_area_headcount(x=overall,select_coding='Department',tooltip_selection='headcount'),use_container_width=True)

with st.expander('Overall Headcount to date broken down by Project'):
    st.write(format_dataframe(test_pivot_headcount(data_graphing_actual_to_date)))
    # st.markdown(get_table_download_link(pivot_headcount(data_graphing_actual_to_date)), unsafe_allow_html=True)
    check_project_headcount = pivot_headcount(data_graphing_actual_to_date).loc['All','All']
    st.write('If True passes checked', check_dept_headcount==check_project_headcount)
    # st.write('sum of above dataframe', pivot_headcount(data_graphing_actual_to_date).loc['All','All'])

with st.expander('921 Headcount by Project - actual + forecast'):
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
    # st.markdown(get_table_download_link(test_with_subtotal), unsafe_allow_html=True)
    st.write(with_subtotal.loc['All','All'])
    st.write('test',test_with_subtotal.loc['All','All'])
    data_graph_project=data_for_graphing_dept(x=test_concat_df,select_level='Project').fillna(0)
    # st.write('check data for graphing', data_graph_project)
    st.altair_chart(chart_area_headcount(x=data_graph_project,select_coding='Project',tooltip_selection='Project'),use_container_width=True)
    

with st.expander('Click to see Actual + Forecast Direct Headcount from Month 1 to Month End to compare productions from Month 1'):
    st.write ('Use this for graphing')
    actual_plus_forecast_headcount = create_pivot_comparing_production_headcount(with_subtotal.sort_values(by='All',ascending=False))
    test_actual_plus_forecast_headcount = create_pivot_comparing_production_headcount(test_with_subtotal.sort_values(by='All',ascending=False))
    st.write(format_gp(test_actual_plus_forecast_headcount))
    # st.markdown(get_table_download_link(test_actual_plus_forecast_headcount), unsafe_allow_html=True)
    st.write ('Check that total equals 921 in above')
    st.write('test check below')
    st.write(test_actual_plus_forecast_headcount.sum().sum())
    st.write('921 dataframe',test_with_subtotal.loc['All','All'])

with st.expander('Historical GP Analysis'):
    st.write('Historical GP Table')
    data_2016_current=consol_headcount_data
    # st.write(data_2016_current.head())
    production_revenue=(acc_schedule_find(data_2016_current, 'Revenue'))
    production_gross_profit =test_gp_by_project(data_2016_current)
    production_gp_percent=gp_percent_by_project(production_gross_profit,production_revenue)
    revenue_gp_gp_percent_table = (gp_revenue_concat(production_gross_profit, production_revenue,production_gp_percent))
    revenue_gp_gp_percent_table=revenue_gp_gp_percent_table.reset_index()
    # revenue_gp_gp_percent_table=revenue_gp_gp_percent_table[ ~(revenue_gp_gp_percent_table['Project_Name']=='BBF UK Costs') |
    # ~(revenue_gp_gp_percent_table['Project_Name']=="Karma's World")]
    
    revenue_gp_gp_percent_table=revenue_gp_gp_percent_table[ ~(revenue_gp_gp_percent_table['Project_Name']=='BBF UK Costs')]
    revenue_gp_gp_percent_table=revenue_gp_gp_percent_table[ ~(revenue_gp_gp_percent_table['Project_Name']=="Karma's World")]

    revenue_gp_gp_percent_table=revenue_gp_gp_percent_table.set_index('Project_Name')
    graphing_gp = revenue_gp_gp_percent_table.query('`Revenue`>4000000').reset_index()
    # project_names_list =graphing_gp['Project_Name'].nunique()
    
    # st.write(project_names_list)
    st.write(format_gp(revenue_gp_gp_percent_table))
    # st.markdown(get_table_download_link(revenue_gp_gp_percent_table), unsafe_allow_html=True)
    # st.altair_chart(chart_gp(graphing_gp),use_container_width=True)
    st.altair_chart(chart_gp_test(graphing_gp),use_container_width=True)
    st.write('OG: had the Develop Exps write off in Aug 2020 recharged from 9S USA')

with st.expander('Historical GP Analysis by Month'):
    production_revenue_monthly=(acc_schedule_find_monthly(data_2016_current, 'Revenue'))
    # st.write(production_revenue_monthly.head())
    production_gross_profit_monthly =test_gp_by_project_monthly(data_2016_current)
    st.write('This is the Gross Profit by Month for top projects but filtered by:')
    # st.write(production_gross_profit_monthly.head())
    project_names_list =graphing_gp['Project_Name'].to_list()
    index_production_gross_profit_monthly=production_gross_profit_monthly.reset_index()
    top_production_gross_profit_monthly=index_production_gross_profit_monthly[index_production_gross_profit_monthly['Project_Name'].isin(project_names_list)]
    
    st.write(top_production_gross_profit_monthly[top_production_gross_profit_monthly['Project_Name'].str.contains('Eureka')])
    production_gp_percent_monthly=gp_percent_by_project(production_gross_profit_monthly,production_revenue_monthly)
    # st.write(production_gp_percent_monthly.head())
    
    st.write(project_names_list)
    production_gp_percent_monthly=production_gp_percent_monthly.reset_index()
    
    rslt_df = production_gp_percent_monthly[production_gp_percent_monthly['Project_Name'].isin(project_names_list)] 
    st.write('this is GP percent by month filtered by:')
    st.write(rslt_df[rslt_df['Project_Name'].str.contains('Eureka')])
    st.write("need to look at rolling GP percent analysis, think that's what I want to do look at main analysis")

    # st.write(production_gp_percent_monthly.head(20))
