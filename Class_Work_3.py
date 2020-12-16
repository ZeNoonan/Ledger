import pandas as pd
import numpy as np
import streamlit as st

from Class_Work_2 import (Budget_Raw_Clean_File,NL_Raw_Clean_File, date_selection_for_PL, PL_generation, merge_pl_dataframe,clean_format_PL_presentation,
pretty_PL_format,ytd_column_forecast,month_column_forecast,new_group_dept)

Budget_2020_Raw, F1_2020_Raw, F2_2020_Raw, F3_2020_Raw = [pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/Budget_2020.xlsx',sheet_name=x) for x in ['Budget','F1', 'F2', 'F3']]
Employee_numbers=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/EE.xlsx')
Project_codes=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/Project Codes.xlsx').rename(columns = {'User Code' : 'SUBANALYSIS 0'})
# NL_2016_2019=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/NL_2016_2019.xlsx')
NL_2020=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/NL_2020_06.xlsx')
coding_acc_schedule = (pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/account_numbers.xlsx')).iloc[:,:3]
coding_sort=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/account_numbers.xlsx', sheet_name='Sheet2')

NL_Data = NL_Raw_Clean_File(NL_2020, coding_acc_schedule)
# https://stackoverflow.com/questions/64563976/how-to-store-result-of-function-run-multiple-times-in-different-variables-pyth
Budget_Data,F1_Data, F2_Data,F3_Data = [Budget_Raw_Clean_File(x, coding_acc_schedule, Project_codes) for x in [Budget_2020_Raw, F1_2020_Raw, F2_2020_Raw, F3_2020_Raw]]




class Budget_v_Actual():

    def __init__(self,ytd_selection):
        self.ytd_selection=ytd_selection
        
        # self.forecast_selection=forecast_selection if forecast_selection is not None else None

    # def test(self, ytd_selection):
    #     NL, Budget, F1, F2, F3 = [date_selection_for_PL(x, ytd_selection) for x in [NL_Data, Budget_Data, F1_Data, F2_Data, F3_Data]]
    #     Budget_PL = PL_generation( Budget,'Name', YTD_Amount = 'Budget_YTD', Month_Amount = 'Budget_Month' )
    #     F1_PL = PL_generation( F1,'Name', YTD_Amount = 'F1_YTD', Month_Amount = 'F1_Month' )
    #     F2_PL = PL_generation( F2,'Name', YTD_Amount = 'F2_YTD', Month_Amount = 'F2_Month' )
    #     F3_PL = PL_generation( F3,'Name', YTD_Amount = 'F3_YTD', Month_Amount = 'F3_Month' )
    #     NL_PL = PL_generation( NL,'Name', YTD_Amount = 'NL_YTD', Month_Amount = 'NL_Month' )
    #     merged_pl_dataframe = merge_pl_dataframe('Name',NL_PL, Budget_PL, F1_PL, F2_PL, F3_PL)
    #     PL_mgt_acct = clean_format_PL_presentation(merged_pl_dataframe, coding_sort)        
    #     PL = PL_mgt_acct.loc[:,['NL_YTD','Budget_YTD','YTD_Variance']]
    #     return pretty_PL_format(PL)

    def merged_pl_budget_data(self):
            NL, Budget, F1, F2, F3 = [date_selection_for_PL(x, self.ytd_selection) for x in [NL_Data, Budget_Data, F1_Data, F2_Data, F3_Data]]
            Budget_PL = PL_generation( Budget,'Name', YTD_Amount = 'Budget_YTD', Month_Amount = 'Budget_Month' )
            F1_PL = PL_generation( F1,'Name', YTD_Amount = 'F1_YTD', Month_Amount = 'F1_Month' )
            F2_PL = PL_generation( F2,'Name', YTD_Amount = 'F2_YTD', Month_Amount = 'F2_Month' )
            F3_PL = PL_generation( F3,'Name', YTD_Amount = 'F3_YTD', Month_Amount = 'F3_Month' )
            NL_PL = PL_generation( NL,'Name', YTD_Amount = 'NL_YTD', Month_Amount = 'NL_Month' )
            merged_pl_dataframe = merge_pl_dataframe('Name',NL_PL, Budget_PL, F1_PL, F2_PL, F3_PL)
            return clean_format_PL_presentation(merged_pl_dataframe, coding_sort)        

    def actual_v_budget_ytd(self):
            PL = self.merged_pl_budget_data().loc[:,['NL_YTD','Budget_YTD','YTD_Variance']]
            return pretty_PL_format(PL)

    def actual_v_budget_month(self):
            PL = self.merged_pl_budget_data().loc[:,['NL_Month','Budget_Month','Month_Variance']]
            return pretty_PL_format(PL)

    def actual_v_forecast_ytd(self, forecast_selection):
            return pretty_PL_format ( ytd_column_forecast(self.merged_pl_budget_data(),forecast_selection))

    def actual_v_forecast_month(self, forecast1_selection):
            return pretty_PL_format ( month_column_forecast(self.merged_pl_budget_data(),forecast1_selection))

ytd_selection = st.selectbox("For what period would you like to run - from September up to?",options = ["Sep_YTD", "Oct_YTD",
    "Nov_YTD","Dec_YTD","Jan_YTD","Feb_YTD","Mar_YTD","Apr_YTD","May_YTD","Jun_YTD","Jul_YTD","Aug_YTD"], index=5) 
    # index=5 sets default to period 6 fix up with a variable for this

Budget_Actual = Budget_v_Actual(ytd_selection)

st.write ('This is the YTD PL')
first_slot=st.empty() 
# first_slot.dataframe ( Budget_Actual.test(ytd_selection) )
first_slot.dataframe ( Budget_Actual.actual_v_budget_ytd() )

if st.checkbox('Would you like to see the Forecast included in YTD above?'):
    forecast_selection = st.selectbox("Which Forecast do you want to see?",options = ["Forecast Q1", "Forecast Q2","Forecast Q3"],index=1) # use index to default
    # first_slot.dataframe (pretty_PL_format ( ytd_column_forecast(PL_mgt_acct,forecast_selection)))
    first_slot.dataframe (Budget_Actual.actual_v_forecast_ytd(forecast_selection))

    if st.checkbox('Check box to see results for Month'):
        st.write ('This is the Month PL')
        second_slot = st.empty()
        second_slot.dataframe (Budget_Actual.actual_v_budget_month())
        if st.checkbox('Would you like to see the Forecast included in above?'):
            forecast1_selection = st.selectbox("Which Forecast do you want to see included above?",options = ["Forecast Q1", "Forecast Q2","Forecast Q3"],index=1) # use index to default
            second_slot.dataframe (Budget_Actual.actual_v_forecast_month(forecast1_selection))

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