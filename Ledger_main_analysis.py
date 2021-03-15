import pandas as pd
import numpy as np
import streamlit as st

# from Ledger_helper_functions import*
from Ledger_helper_functions import (Budget_Raw_Clean_File,NL_Raw_Clean_File, date_selection_for_PL, PL_generation, merge_pl_dataframe,clean_format_PL_presentation,
pretty_PL_format,ytd_column_forecast,month_column_forecast,pl_dept_generation, end_of_year_forecast, end_of_year_forecast_dept, gp_by_project,
long_format_budget,long_format_nl, format_gp, gp_nl_budget_comp, budget_forecast_gp,gp_by_project_sales_cos,budget_forecast_gp_sales_cos, get_total_by_month)

st.set_page_config(layout="wide")

Budget_2020_Raw, F1_2020_Raw, F2_2020_Raw, F3_2020_Raw = [pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/Budget_2021.xlsx',sheet_name=x) 
for x in ['Budget','F1', 'F2', 'F3']]

Employee_numbers=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/EE.xlsx')
Project_codes=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/Project_Codes_2021_.xlsx').rename(columns = {'User Code' : 'SUBANALYSIS 0'})
# NL_2016_2019=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/NL_2016_2019.xlsx')

@st.cache
def load_ledger_data():
    return pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/NL_2021_06.xlsx')
NL = load_ledger_data().copy()
coding_acc_schedule = (pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/account_numbers.xlsx')).iloc[:,:3]
coding_sort=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/account_numbers.xlsx', sheet_name='Sheet2')
NL_Data = NL_Raw_Clean_File(NL, coding_acc_schedule)
# https://stackoverflow.com/questions/64563976/how-to-store-result-of-function-run-multiple-times-in-different-variables-pyth

Budget_Data,F1_Data, F2_Data,F3_Data = [Budget_Raw_Clean_File(x, coding_acc_schedule, Project_codes) for x in [Budget_2020_Raw, F1_2020_Raw, F2_2020_Raw, F3_2020_Raw]]

class Budget_v_Actual():

    def __init__(self,ytd_selection):
        self.ytd_selection=ytd_selection
        self.NL, self.Budget, self.F1, self.F2, self.F3 = [date_selection_for_PL(x, self.ytd_selection) for x in [NL_Data, Budget_Data, F1_Data, F2_Data, F3_Data]]
        self.Budget_PL = PL_generation( self.Budget,'Name', YTD_Amount = 'Budget_YTD', Month_Amount = 'Budget_Month' )
        self.F1_PL = PL_generation( self.F1,'Name', YTD_Amount = 'F1_YTD', Month_Amount = 'F1_Month' )
        self.F2_PL = PL_generation( self.F2,'Name', YTD_Amount = 'F2_YTD', Month_Amount = 'F2_Month' )
        self.F3_PL = PL_generation( self.F3,'Name', YTD_Amount = 'F3_YTD', Month_Amount = 'F3_Month' )
        self.NL_PL = PL_generation( self.NL,'Name', YTD_Amount = 'NL_YTD', Month_Amount = 'NL_Month' )
        self.NL_yr, self.Budget_yr, self.F1_yr, self.F2_yr, self.F3_yr = [date_selection_for_PL(x, 'Aug_YTD') for x in [NL_Data, Budget_Data, F1_Data, F2_Data, F3_Data]]
        self.Budget_PL_yr = PL_generation( self.Budget_yr,'Name', YTD_Amount = 'Budget_YTD', Month_Amount = 'Budget_Month' )
        self.F1_PL_yr = PL_generation( self.F1_yr,'Name', YTD_Amount = 'F1_YTD', Month_Amount = 'F1_Month' )
        self.F2_PL_yr = PL_generation( self.F2_yr,'Name', YTD_Amount = 'F2_YTD', Month_Amount = 'F2_Month' )
        self.F3_PL_yr = PL_generation( self.F3_yr,'Name', YTD_Amount = 'F3_YTD', Month_Amount = 'F3_Month' )
        self.NL_PL_yr = PL_generation( self.NL_yr,'Name', YTD_Amount = 'NL_YTD', Month_Amount = 'NL_Month' )
        
    @st.cache
    def merged_pl_budget_data(self):
        merged_pl_dataframe = merge_pl_dataframe('Name',self.NL_PL, self.Budget_PL, self.F1_PL, self.F2_PL, self.F3_PL)
        return clean_format_PL_presentation(merged_pl_dataframe, coding_sort)        

    def merged_dept_data(self,dept_selection):
        Budget_PL_Dept = pl_dept_generation( clean_data=self.Budget, department=dept_selection, YTD_Amount = 'Budget_YTD', Month_Amount = 'Budget_Month' )
        NL_PL_Dept = pl_dept_generation( clean_data=self.NL, department=dept_selection ,YTD_Amount = 'NL_YTD', Month_Amount = 'NL_Month' )
        F1_PL_Dept = pl_dept_generation( clean_data=self.F1, department=dept_selection, YTD_Amount = 'F1_YTD', Month_Amount = 'F1_Month' )
        F2_PL_Dept = pl_dept_generation( clean_data=self.F2, department=dept_selection, YTD_Amount = 'F2_YTD', Month_Amount = 'F2_Month' )
        F3_PL_Dept = pl_dept_generation( clean_data=self.F3, department=dept_selection, YTD_Amount = 'F3_YTD', Month_Amount = 'F3_Month' )        
        merged_pl_dataframe = (merge_pl_dataframe('Name',NL_PL_Dept, Budget_PL_Dept, F1_PL_Dept, F2_PL_Dept, F3_PL_Dept)).copy()
        return clean_format_PL_presentation(merged_pl_dataframe, coding_sort)   

    def actual_v_budget_ytd(self):
        PL = self.merged_pl_budget_data().loc[:,['NL_YTD','Budget_YTD','YTD_Variance']]
        return pretty_PL_format(PL)

    def actual_v_budget_ytd_dept(self,dept_selection):
        # st.write ('testing to see that dept returns in actual v budget function class', dept_selection)
        PL = self.merged_dept_data(dept_selection).loc[:,['NL_YTD','Budget_YTD','YTD_Variance']]
        return pretty_PL_format(PL)

    def actual_v_budget_month(self):
        PL = self.merged_pl_budget_data().loc[:,['NL_Month','Budget_Month','Month_Variance']]
        return pretty_PL_format(PL)

    def actual_v_budget_month_dept(self,dept_selection):
        PL = self.merged_dept_data(dept_selection).loc[:,['NL_Month','Budget_Month','Month_Variance']]
        return pretty_PL_format(PL)

    def actual_v_forecast_ytd(self, forecast_selection):
        return pretty_PL_format ( ytd_column_forecast(self.merged_pl_budget_data(),forecast_selection))

    def actual_v_forecast_ytd_dept(self, dept_selection, forecast_selection):
        PL = ytd_column_forecast(self.merged_dept_data(dept_selection),forecast_selection)
        return pretty_PL_format(PL)

    def actual_v_forecast_month(self, forecast1_selection):
        return pretty_PL_format ( month_column_forecast(self.merged_pl_budget_data(),forecast1_selection))

    def actual_v_forecast_month_dept(self, dept_selection, forecast1_selection):
        PL = month_column_forecast(self.merged_dept_data(dept_selection),forecast1_selection)
        return pretty_PL_format(PL)

    def actual_v_forecast_year_projection(self,ytd_selection, coding_acc_schedule,projection_selection):
        full_year_forecast = end_of_year_forecast(ytd_selection, self.NL, coding_acc_schedule,projection_selection,Budget_Data, F1_Data, F2_Data,F3_Data,
        coding_sort,self.Budget_PL_yr,self.F1_PL_yr,self.F2_PL_yr,self.F3_PL_yr)
        projection_slice = full_year_forecast.loc[:,['Projection','Budget','Var v. Budget', 'F1','F2','F3']]
        return pretty_PL_format ( projection_slice)

    def actual_v_forecast_year_projection_dept(self,ytd_selection, coding_acc_schedule,projection_selection,department):
        full_year_forecast = end_of_year_forecast_dept(ytd_selection, self.NL, coding_acc_schedule,projection_selection,Budget_Data, F1_Data, F2_Data,F3_Data,
        coding_sort,self.Budget_yr,self.F1_yr,self.F2_yr,self.F3_yr,department)
        projection_slice = full_year_forecast.loc[:,['Projection','Budget','Var v. Budget', 'F1','F2','F3']]
        return pretty_PL_format ( projection_slice)

    def variance_by_month_by_production_by_dept(self, NL_data, coding_acc_schedule, forecast_selection, Schedule_Name, Department=None):
        NL_Revenue = gp_by_project_sales_cos(NL_Data, coding_acc_schedule,Schedule_Name,Department)
        NL_melt_Revenue = long_format_nl(NL_Revenue)
        return budget_forecast_gp_sales_cos (forecast_selection, coding_acc_schedule, NL_melt_Revenue,Schedule_Name,Department)
        # return format_gp(revenue_actual_budget)


    



with st.beta_expander('Click to see Company YTD and Month PL'):
    ytd_selection = st.selectbox("For what period would you like to run - from September up to?",options = ["Sep_YTD", "Oct_YTD",
    "Nov_YTD","Dec_YTD","Jan_YTD","Feb_YTD","Mar_YTD","Apr_YTD","May_YTD","Jun_YTD","Jul_YTD","Aug_YTD"], index=5)
    Budget_Actual = Budget_v_Actual(ytd_selection)
    col1,col2=st.beta_columns(2)
    with col1:
        st.write ('Results for YTD PL below')
        # first_slot=st.empty() 
        first_slot=st.beta_container()
        first_slot.dataframe ( Budget_Actual.actual_v_budget_ytd() )
        if st.checkbox('Would you like to see the Forecast included in YTD above?'):
            forecast_selection = st.selectbox("Which Forecast do you want to see?",options = ["Forecast Q1", "Forecast Q2","Forecast Q3"],index=0,key='NL_YTD') # use index to default
            first_slot.dataframe (Budget_Actual.actual_v_forecast_ytd(forecast_selection))

    with col2:
        st.write('Results for Month PL')
        # second_slot = st.empty()
        second_slot = st.beta_container()
        second_slot.dataframe (Budget_Actual.actual_v_budget_month())
        if st.checkbox('Would you like to see the Forecast included in above?'):
            forecast1_selection = st.selectbox("Which Forecast do you want to see included above?",options = ["Forecast Q1", "Forecast Q2","Forecast Q3"],index=0) # use index to default
            second_slot.dataframe (Budget_Actual.actual_v_forecast_month(forecast1_selection))


with st.beta_expander('Would you like to see the Results for a specific Department?'):
    dept_selection = st.selectbox("Which Department do you want to see?",options = ["TV", "CG",
    "Post","IT","Pipeline","Admin","Development"],index=0)
    col3,col4 = st.beta_columns(2)
    with col3:
        st.write ('Results for Dept YTD PL below')
        third_slot=st.empty()
        third_slot.dataframe (Budget_Actual.actual_v_budget_ytd_dept(dept_selection))
        if st.checkbox('Would you like to see the Forecast included in Department results above?'):
            forecast_selection = st.selectbox("Which Forecast do you want to include?",options = ["Forecast Q1", "Forecast Q2","Forecast Q3"],index=0, key='Dept YTD') # use index to default
            third_slot.dataframe (Budget_Actual.actual_v_forecast_ytd_dept(dept_selection, forecast_selection))

    with col4:    
        st.write ('This is the Dept Month PL')
        fourth_slot = st.empty()
        fourth_slot.dataframe (Budget_Actual.actual_v_budget_month_dept(dept_selection))
        if st.checkbox('Would you like to see the Forecast included in Departmental Month Results?'):
            forecast2_selection = st.selectbox("Which Forecast do you want to see included above?",options = ["Forecast Q1", "Forecast Q2","Forecast Q3"],
            index=0, key='Dept Month') # use index to default https://discuss.streamlit.io/t/how-to-use-the-key-field-in-interactive-widgets-api/1007/11
            fourth_slot.dataframe (Budget_Actual.actual_v_forecast_month_dept(dept_selection,forecast2_selection))

with st.beta_expander('Click for End of Year Projection'):
    projection_selection = st.selectbox("Which Budget/Forecast to use for rest of year?",options = ["Budget", "F1","F2","F3"],index=1)
    fifth_slot = st.empty()
    fifth_slot.dataframe (Budget_Actual.actual_v_forecast_year_projection(ytd_selection, coding_acc_schedule,projection_selection))
    if st.checkbox ('Select for Department'):
        dep_projection_sel=st.selectbox('Pick Department to run end of year projection', options = ["TV", "CG","Post","IT","Pipeline","Admin","Development"],index=0)
        st.dataframe (Budget_Actual.actual_v_forecast_year_projection_dept(ytd_selection, coding_acc_schedule,projection_selection,dep_projection_sel))


#     with st.beta_expander('Click to see the Gross Profit Variance for YTD v. Budget'):
#         st.selectbox("Budget is below",options = ["Budget"],index=0, key='budget_index')
#         NL_GP = gp_by_project(NL_Data, coding_acc_schedule)
#         Budget_GP = gp_by_project(Budget_Data, coding_acc_schedule)
#         NL_melt = long_format_nl(NL_GP)
#         Budget_melt = long_format_budget(Budget_GP, NL_melt)
#         st.dataframe ( format_gp (gp_nl_budget_comp(NL_melt, Budget_melt )) )

# with col4:
with st.beta_expander('Click to see the Gross Profit Variance for YTD v. Budget'):
    one_selection = st.selectbox("Which Budget/Forecast do you want to see?",options = ["Budget","Forecast Q1", "Forecast Q2","Forecast Q3"],index=0,key='forecast_for_gp') # use index to default
    forecast_var= {"Budget":Budget_Data,"Forecast Q1":F1_Data,"Forecast Q2":F2_Data,"Forecast Q3":F3_Data}
    # dep_sel=st.selectbox("Which Department do you want to see?",options = ['None',"TV", "CG",
    # "Post","IT","Pipeline","Admin","Development"],index=0, key='department selection for GP')
    st.write('GP Variance by Production')
    forecast_selection = forecast_var[one_selection]

    Revenue_variance=Budget_Actual.variance_by_month_by_production_by_dept(NL_Data, coding_acc_schedule, forecast_selection,Schedule_Name='Revenue', Department=None)
    COS_variance=Budget_Actual.variance_by_month_by_production_by_dept(NL_Data, coding_acc_schedule, forecast_selection,Schedule_Name='Cost of Sales', Department=None)
    actual_v__forecast = Revenue_variance.add (COS_variance, fill_value=0)
    actual_v__forecast = actual_v__forecast.iloc[(-actual_v__forecast['Total'].abs()).argsort()]
    sort = actual_v__forecast.index.values.tolist()
    st.dataframe(format_gp(actual_v__forecast))    
    st.write (format_gp(get_total_by_month(actual_v__forecast)))

    col_sales,col_cos = st.beta_columns(2)
    with col_sales:
            st.write('Revenue Variance by Production')
            revenue_variance=Budget_Actual.variance_by_month_by_production_by_dept(NL_Data, coding_acc_schedule, forecast_selection,Schedule_Name='Revenue', Department=None)
            st.write (format_gp((revenue_variance).reindex(sort)))
            st.write (format_gp(get_total_by_month(revenue_variance)))

    with col_cos:
            st.write('COS Variance by Production')
            cos_variance=Budget_Actual.variance_by_month_by_production_by_dept(NL_Data, coding_acc_schedule,
            forecast_selection,Schedule_Name='Cost of Sales', Department=None)
            st.write (format_gp((cos_variance).reindex(sort)))
            st.write (format_gp(get_total_by_month(cos_variance)))

st.write('TIME TO DO SOME GRAPHS JUST TO HAVE ON HAND HEADCOUNT BY PROJECT OVER THE YEARS')
st.write ('nl', NL_Data.query('`Account Code`=="921-0500"').sort_values(by='Employee',ascending=False).head())
sch_921=NL_Data.query('`Account Code`=="921-0500"').loc[:,
['Description','Journal Amount','Src. Account','Jrn. No.','Yr.','Per.','Project']]
# st.write ('nl', sch_921.head()) #https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.query.html
group_supplier=sch_921.groupby(['Src. Account','Jrn. No.','Yr.','Per.','Project'])['Journal Amount'].sum().reset_index()
# st.write('group supplier project',group_supplier.head())
# st.write(sch_921.query('`Per.`==1 and `Src. Account`=="BUK02"').head()) # will need to filter out UK seperately and add back in groupby on description
# st.write(sch_921.query('`Per.`==2 and `Src. Account`=="FPL01"'))
# First thing first, filter out BBF UK
group_UK = sch_921.query('`Src. Account`=="BUK02"')
group_no_UK = group_supplier.query('`Src. Account`!="BUK02"')

def credit_notes_resolve(x):
    credit_notes=x['Jrn. No.'].str.contains('CN|CR')
    filter_credit_notes=x[credit_notes]
    filter_non_credit_notes=x[~credit_notes]
    non_UK_contractor_921=pd.concat([filter_credit_notes,filter_non_credit_notes])
    non_UK_contractor_921['Payroll_Amt'] = non_UK_contractor_921.groupby (['Jrn. No.'])['Journal Amount'].transform('sum')
    non_UK_contractor_921['Headcount'] = non_UK_contractor_921['Journal Amount'] / non_UK_contractor_921['Payroll_Amt']
    return non_UK_contractor_921

st.write('this is Non UK contractor Ready', credit_notes_resolve(group_no_UK).head())

def UK_clean_921(x):
    x['Payroll_Amt'] = x.groupby (['Jrn. No.','Description'])['Journal Amount'].transform('sum')
    x['Headcount'] = x['Journal Amount'] / x['Payroll_Amt']
    return x

st.write('UK Ready', UK_clean_921(group_UK).drop(['Description'], axis=1).head())

sch_921_ee=NL_Data.query('`Account Code`=="921-0500"').loc[:,
['Journal Amount','Src. Account','Jrn. No.','Yr.','Per.','Project','Employee - Ext. Code']]

# st.write('new way finding string')
# st.write(sch_921_ee[sch_921_ee['Employee'].apply(lambda x: isinstance(x, str))])

def company_ee_project(x):
    # x['Employee']=x['Employee'].replace('" "','',regex=True).astype(float)
    # x['Employee']=x['Employee'].str.replace(" ","")
    x['Employee - Ext. Code'] = pd.to_numeric(x['Employee - Ext. Code'])
    x= x.query('`Employee - Ext. Code`>0.5')
    x['Payroll_Amt'] = x.groupby (['Yr.','Per.','Employee - Ext. Code'])['Journal Amount'].transform('sum')
    x['Headcount'] = x['Journal Amount'] / x['Payroll_Amt']
    return x

st.write('employee ready')
st.write(company_ee_project(sch_921_ee).drop(['Employee - Ext. Code'], axis=1).head())

def combined_921_headcount(ee,UK,Mauve):
    employee_921=company_ee_project(ee).drop(['Employee - Ext. Code'], axis=1).reset_index()
    UK_921=UK_clean_921(UK).drop(['Description'], axis=1).reset_index()
    Mauve_2021=credit_notes_resolve(Mauve).reset_index()
    combined = pd.concat([employee_921, UK_921, Mauve_2021]).drop(['index'],axis=1)
    combined['Headcount']=pd.to_numeric(combined['Headcount'])
    return combined

headcount_ready=combined_921_headcount(sch_921_ee,group_UK,group_no_UK)
st.write ('combined 921',headcount_ready) 
st.write(headcount_ready.sum(axis=0, skipna=True))



# just need to add the two dataframes and group on year and period
# then add in UK headcount
# but need to filter by project so we can see how many people working on each project
# should I start a new file?
# probably as it's going to look at historical analysis in terms of headcount to understand that



# https://stackoverflow.com/questions/12572362/how-to-get-a-string-after-a-specific-substring

# use groupby on Source Account, then groupby on journal no. but exclude CR in journal no.
