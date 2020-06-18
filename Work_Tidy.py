import pandas as pd
import numpy as np
import streamlit as st
from helper_functions import (Budget_1,date_selection, NL_2020, new_group, new_group_dept, compare, compare_alternative,
subtotal, ytd_column_forecast, prep_data, month_column_forecast, end_of_year_forecast, end_of_year_forecast_dept, date_selection_year, 
format_dataframe, new_group_project)

# https://docs.streamlit.io/advanced_concepts.html
# use the st.empty as a way of putting in the first dataframe, then when update for forecast, it overwrites the first empty

# Bring in historical figures to do the trend on revenue? adjust for bbf uk revenue get spreadsheet which reconciles this

# https://stackoverflow.com/questions/47494720/python-pandas-subtotals-on-groupby
# https://stackoverflow.com/questions/45971751/appending-grandtotal-and-subtotal-rows-to-two-level-row-and-column-index-datafra


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

# def main():
st.sidebar.title("Navigation")
# EE = EE_numbers()
# Project = Project_codes()
Budget_Data = Budget_1('C:/Users/Darragh/Documents/Python/Work/Data/Budget_2020.xlsx','Budget')
F1_Data = Budget_1('C:/Users/Darragh/Documents/Python/Work/Data/Budget_2020.xlsx','F1')
F2_Data = Budget_1('C:/Users/Darragh/Documents/Python/Work/Data/Budget_2020.xlsx','F2')
F3_Data = Budget_1('C:/Users/Darragh/Documents/Python/Work/Data/Budget_2020.xlsx','F3')
ytd_selection = st.selectbox("For what period would you like to run - from September up to?",options = ["Sep_YTD", "Oct_YTD",
    "Nov_YTD","Dec_YTD","Jan_YTD","Feb_YTD","Mar_YTD","Apr_YTD","May_YTD","Jun_YTD","Jul_YTD","Aug_YTD"], index=5) 
    # index=5 sets default to period 6 fix up with a variable for this
NL = date_selection(NL_2020(raw5), ytd_selection, coding_acc_schedule)
Budget = date_selection(Budget_Data, ytd_selection, coding_acc_schedule)
F1 = date_selection(F1_Data, ytd_selection, coding_acc_schedule)
F2 = date_selection(F2_Data, ytd_selection, coding_acc_schedule)
F3 = date_selection(F3_Data, ytd_selection, coding_acc_schedule)

# https://github.com/streamlit/streamlit/issues/729   This is for converting period 6 into say YTD_Feb uses a dictionary
Budget_PL = new_group( Budget, YTD_Amount = 'Budget_YTD', Month_Amount = 'Budget_Month' )
F1_PL = new_group( F1, YTD_Amount = 'F1_YTD', Month_Amount = 'F1_Month' )
F2_PL = new_group( F2, YTD_Amount = 'F2_YTD', Month_Amount = 'F2_Month' )
F3_PL = new_group( F3, YTD_Amount = 'F3_YTD', Month_Amount = 'F3_Month' )
NL_PL = new_group( NL, YTD_Amount = 'NL_YTD', Month_Amount = 'NL_Month' )

compare_df = compare (NL_PL, Budget_PL)

subtotal2 = subtotal(compare_alternative(NL_PL, Budget_PL, F1_PL, F2_PL, F3_PL), coding_sort)


st.write ('This is the YTD PL')
first_slot=st.empty() #st.write doesn't work with st.empty()
ytd_pl = subtotal2.loc[:,['NL_YTD','Budget_YTD','YTD_Variance']]
first_slot.dataframe ( format_dataframe(ytd_pl) )
# first_slot.dataframe ( format_dataframe(ytd_pl).applymap(color_negative_red) ) 
# COLOUR NEGATIVE RED NOT WORKING DUE TO STRING
# first_slot.dataframe ( ytd_pl.style.format("{:,.0f}").applymap(color_negative_red) ) 
# st.write (ytd_pl.index)
# first_slot.dataframe (ytd_pl.style.apply(lambda x: ['background: lightgreen' if (x.name =='Gross Profit %') else '' for i in x], axis =1) )


if st.checkbox('Would you like to see the Forecast included in YTD above?'):
    forecast_selection = st.selectbox("Which Forecast do you want to see?",options = ["Forecast Q1", "Forecast Q2","Forecast Q3"],index=1) # use index to default
    first_slot.dataframe (format_dataframe ( ytd_column_forecast(subtotal2,forecast_selection)))

    if st.checkbox('Check box to see results for Month'):
        st.write ('This is the Month PL')
        second_slot = st.empty()
        second_slot.dataframe (subtotal2.loc[:,['NL_Month','Budget_Month','Month_Variance']])
        if st.checkbox('Would you like to see the Forecast included in above?'):
            forecast1_selection = st.selectbox("Which Forecast do you want to see included above?",options = ["Forecast Q1", "Forecast Q2","Forecast Q3"],index=1) # use index to default
            second_slot.dataframe (month_column_forecast(subtotal2,forecast1_selection))

if st.checkbox('Would you like to see the Results for a specific Department?'):
    dept_selection = st.selectbox("Which Department do you want to see?",options = ["TV", "CG",
    "Post","IT","Pipeline","Admin","Development"],index=0)
    Budget_PL_Dept = new_group_dept( x=Budget, department=dept_selection, YTD_Amount = 'Budget_YTD', Month_Amount = 'Budget_Month' )
    NL_PL_Dept = new_group_dept( x=NL, department=dept_selection ,YTD_Amount = 'NL_YTD', Month_Amount = 'NL_Month' )
    F1_PL_Dept = new_group_dept( x=F1, department=dept_selection, YTD_Amount = 'F1_YTD', Month_Amount = 'F1_Month' )
    F2_PL_Dept = new_group_dept( x=F2, department=dept_selection, YTD_Amount = 'F2_YTD', Month_Amount = 'F2_Month' )
    F3_PL_Dept = new_group_dept( x=F3, department=dept_selection, YTD_Amount = 'F3_YTD', Month_Amount = 'F3_Month' )

    compare_df_dept = compare (NL_PL_Dept, Budget_PL_Dept)
    subtotal_dept = subtotal(compare_alternative(NL_PL_Dept, Budget_PL_Dept, F1_PL_Dept, F2_PL_Dept, F3_PL_Dept), coding_sort)

    third_slot=st.empty()
    third_slot.dataframe (subtotal_dept.loc[:,['NL_YTD','Budget_YTD','YTD_Variance']])
    if st.checkbox('Would you like to see the Forecast included in Department results above?'):
        forecast_selection = st.selectbox("Which Forecast do you want to include?",options = ["Forecast Q1", "Forecast Q2","Forecast Q3"],index=1, key='Dept YTD') # use index to default
        third_slot.dataframe (ytd_column_forecast(subtotal_dept,forecast_selection))

    if st.checkbox('Check box to see results for Departmental Month'):
        st.write ('This is the Month PL')
        fourth_slot = st.empty()
        fourth_slot.dataframe (subtotal_dept.loc[:,['NL_Month','Budget_Month','Month_Variance']])
        if st.checkbox('Would you like to see the Forecast included in Departmental Month Results?'):
            forecast1_selection = st.selectbox("Which Forecast do you want to see included above?",options = ["Forecast Q1", "Forecast Q2","Forecast Q3"],
            index=1, key='Dept Month') # use index to default https://discuss.streamlit.io/t/how-to-use-the-key-field-in-interactive-widgets-api/1007/11
            fourth_slot.dataframe (month_column_forecast(subtotal_dept,forecast1_selection))


if st.checkbox('Click for End of Year Projection'):
    projection_selection = st.selectbox("Which Budget/Forecast to use for rest of year?",options = ["Budget", "F1","F2","F3"],index=1)
    projection = end_of_year_forecast(projection_selection,ytd_selection, raw5, coding_acc_schedule, coding_sort)  # if i change this to projection selection it doesnt work due to string something
    fifth_slot = st.empty()
    fifth_slot.dataframe (format_dataframe ( projection.loc[:,['Projection','Budget','Var v. Budget', 'F1','F2','F3']]))
    if st.checkbox ('Select for Department'):
        dep_projection_sel=st.selectbox('Pick Department to run end of year projection', options = ["TV", "CG","Post","IT","Pipeline","Admin","Development"],index=0)
        dep_projection = end_of_year_forecast_dept( projection_selection, ytd_selection, dep_projection_sel, raw5, coding_acc_schedule, coding_sort)
        fifth_slot.dataframe (dep_projection.loc[:,['Projection','Budget','Var v. Budget', 'F1','F2','F3']])

# main()

st.write ('How about for Production, we do a monthly variance against Budget of each production')
st.write ('and we also do a monthly GP% variance, but do it on a rolling YTD against Budget')
st.write ('this is the NL PL after date selection function', NL.head())
st.write ('this is the NL PL BEFORE date selection function', NL_2020(raw5).head())
revenue_by_project = new_group_project(NL_2020(raw5),coding_acc_schedule,'Revenue', Month_Amount = 'NL_Month')
cos_by_project = new_group_project(NL_2020(raw5),coding_acc_schedule,'Cost of Sales', Month_Amount = 'NL_Month')
gp_by_project = revenue_by_project.add (cos_by_project, fill_value=0)
st.write ('need to do the groupby on NL', revenue_by_project )
st.write ('this is revenue amoutn produced which matches PL',revenue_by_project.sum().sum())
st.write ('this is cos amoutn produced which matches PL',cos_by_project.sum().sum())
st.write ('this is gp amoutn produced which matches PL',gp_by_project.sum().sum())
st.write ('trying to get gross profit', gp_by_project)