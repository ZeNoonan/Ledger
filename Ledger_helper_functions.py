import pandas as pd
import numpy as np
import streamlit as st
import base64
from io import BytesIO
import altair as alt

# @st.cache
def Budget_Raw_Clean_File(Budget_Raw_Clean,coding_acc_schedule, Project_codes):
    Budget_Raw_Clean['Acc_Schedule']=Budget_Raw_Clean['ACCOUNT'].str[-8:-5]
    Budget_Raw_Clean['Acc_Schedule']=pd.to_numeric(Budget_Raw_Clean['Acc_Schedule'])
    Budget_Raw_Clean['Acc_Number']=Budget_Raw_Clean['ACCOUNT'].str[-8:]
    Budget_Raw_Clean['Department'] = Budget_Raw_Clean['ACCOUNT'].str[-14:-9]
    Budget_Raw_Clean['SUBANALYSIS 0']= Budget_Raw_Clean['SUBANALYSIS 0'].replace({'1-Z-253':'1-Z-209'})
    Budget_Raw_Clean.loc[:,'BUDGET 1':'BUDGET 12'] = Budget_Raw_Clean.loc[:,'BUDGET 1':'BUDGET 12'] *-1
    Budget_Raw_Clean = Budget_Raw_Clean.melt(id_vars=['ACCOUNT', 'SUBANALYSIS 0','Acc_Schedule','Acc_Number','Department'],value_name='Journal Amount',var_name='Per.')
    Budget_Raw_Clean['Per.'] = Budget_Raw_Clean['Per.'].str[7:]
    Budget_Raw_Clean['Per.'] = pd.to_numeric(Budget_Raw_Clean['Per.'])
    Budget_Raw_Clean = Budget_Raw_Clean.merge (coding_acc_schedule, on='Acc_Number',how='outer')
    Budget_Raw_Clean['Department'] =Budget_Raw_Clean['Department'].replace( {'T0000':"TV",'CG000':"CG",
    'P0000':"Post",'A0000':"Admin",'D0000':"Development",'I0000':"IT",'R0000':"Pipeline",'HR000':"HR"})
    Budget_Raw_Clean = pd.merge(Budget_Raw_Clean, Project_codes, on=['SUBANALYSIS 0'], how='outer').rename(columns = {'Description' : 'Project_Name'})
    return Budget_Raw_Clean

# @st.cache
def NL_Raw_Clean_File(NL_Raw_Clean, coding_acc_schedule):
    # st.write(NL_Raw_Clean.head())
    NL_Raw_Clean['Acc_Schedule']=NL_Raw_Clean['Account Code'].str[:3]
    NL_Raw_Clean['Acc_Schedule']=pd.to_numeric(NL_Raw_Clean['Acc_Schedule'])
    NL_Raw_Clean['Project']=NL_Raw_Clean['Project'].replace({'1-Z-253 Eureka 2':'1-Z-209 Eureka'})
    NL_Raw_Clean['Project_Code'] = NL_Raw_Clean['Project'].str[:8]
    NL_Raw_Clean['Project_Name'] = NL_Raw_Clean['Project'].str[8:]
    NL_Raw_Clean['Acc_Number'] = NL_Raw_Clean['Account Code']
    NL_Raw_Clean['Journal Amount'] = NL_Raw_Clean['Journal Amount'] * -1
    NL_Raw_Clean = NL_Raw_Clean.merge (coding_acc_schedule, on='Acc_Number',how='outer')
    NL_Raw_Clean['Department'] = NL_Raw_Clean['Department'].replace( {'T0000':"TV",'CG000':"CG",
    'P0000':"Post",'A0000':"Admin",'D0000':"Development",'I0000':"IT",'R0000':"Pipeline",'HR000':"HR"})

    NL_Raw_Clean['calendar_month']=NL_Raw_Clean['Per.'].map({1:9,2:10,3:11,4:12,5:1,6:2,7:3,8:4,9:5,10:6,11:7,12:8,19:8})
    NL_Raw_Clean['calendar_year'] = np.where((NL_Raw_Clean['Per.'] > 4.1), NL_Raw_Clean['Yr.'], NL_Raw_Clean['Yr.']-1)
    NL_Raw_Clean['calendar_year']=NL_Raw_Clean['calendar_year']+2000
    NL_Raw_Clean=NL_Raw_Clean.rename(columns={'calendar_year':'year', 'calendar_month':'month'})
    NL_Raw_Clean['day']=1
    NL_Raw_Clean['date']=pd.to_datetime(NL_Raw_Clean[['year','month','day']],infer_datetime_format=True)

    return NL_Raw_Clean

@st.cache
def date_selection_for_PL(df, ytd_month_number):
    # def date_selection(df, ytd_month_number, department=None):
    date_dict= {"Sep_YTD":1,"Oct_YTD":2,"Nov_YTD":3,"Dec_YTD":4,"Jan_YTD":5,"Feb_YTD":6,"Mar_YTD":7,
    "Apr_YTD":8,"May_YTD":9,"Jun_YTD":10,"Jul_YTD":11,"Aug_YTD":12}
    df = df [ (df['Per.'] <= date_dict[ytd_month_number]) ] 
    filter = df['Per.']==date_dict[ytd_month_number]
    df ['Month_Amount'] = df.loc[:,'Journal Amount'].where(filter).copy()
    # st.write( df.loc[df['Name'].isnull()] ) # Always test after merge my issue was with the DONT DELETE THIS COMMENT!
    # spreadsheet didn't have full coding https://stackoverflow.com/questions/53645882/pandas-merging-101
    return df

@st.cache
def PL_generation(clean_data,category_to_filter_on,**kwargs): 
    clean_data = clean_data.groupby([category_to_filter_on]).agg ( YTD_Amount = ( 'Journal Amount','sum' ), Month_Amount = ('Month_Amount','sum'),
    Sorting = ('Sorting','first') ).sort_values(by=['Sorting'], ascending = [True])
    clean_data = clean_data.reset_index()
    clean_data=clean_data.rename(columns=kwargs)
    return clean_data

# @st.cache


# @st.cache
def merge_pl_dataframe(category_to_filter_on,a,b,c,d,e):
    one = pd.merge (a,b, on=[category_to_filter_on,'Sorting'], how='outer')
    two = pd.merge (one,c, on=[category_to_filter_on,'Sorting'], how='outer')
    three = pd.merge (two,d, on=[category_to_filter_on,'Sorting'], how='outer')
    merged_pl = pd.merge (three,e, on=[category_to_filter_on,'Sorting'], how='outer')
    merged_pl = merged_pl.set_index(category_to_filter_on)
    merged_pl.fillna(0, inplace=True)
    # st.write( c.loc[c['Name'].isnull()] )
    # st.write( c.loc[c['Acc_Schedule'].isnull()] )
    return merged_pl

@st.cache
def clean_format_PL_presentation(x, coding_sort):
    gross_profit = x.reindex(['Revenue','Cost of Sales']).sum()
    sub_total_overheads = x.reindex(['Payroll','Recruitment & HR','Rent & Service Charges','Building Expenses','Office Expenses','Travel',
    'Computer costs','Audit, Legal & Consulting','Committees','Insurance','Bank Charges','FX','Other','Other']).sum()
    x.loc['Gross Profit'] = gross_profit
    x.loc['Gross Profit %'] = ( (gross_profit / x.loc['Revenue'])*100.00 ).astype(float)
    x.loc['Sub-Total Overheads'] = sub_total_overheads
    def check(x,account):
        if account in x.index:
            return x.loc[account]
        else:
            return 0 #also tryed N
    x.loc['EBITDA'] = gross_profit + sub_total_overheads + check(x,'IP Capitalisation')
    x.loc['Net Profit before Tax'] = x.loc['EBITDA'] + check(x,'Depreciation') + check(x,'Finance Lease Interest')
    x.loc['Net Profit %'] = (x.loc['Net Profit before Tax'] / x.loc['Revenue'])*100
    x['YTD_Variance'] = x['NL_YTD'] - x['Budget_YTD']
    x['F1_YTD_Variance'] = x['NL_YTD'] - x['F1_YTD']
    x['F2_YTD_Variance'] = x['NL_YTD'] - x['F2_YTD']
    x['F3_YTD_Variance'] = x['NL_YTD'] - x['F3_YTD']
    x['Month_Variance'] = x['NL_Month'] - x['Budget_Month']
    x['F1_Month_Variance'] = x['NL_Month'] - x['F1_Month']
    x['F2_Month_Variance'] = x['NL_Month'] - x['F2_Month']
    x['F3_Month_Variance'] = x['NL_Month'] - x['F3_Month']
    x = pd.merge (x,coding_sort, on=['Name'],how='inner')
    x = x.drop(columns =['Sorting_x'])
    x = x.rename(columns = {'Sorting_y' : 'Sorting'}).sort_values(by ='Sorting', ascending=True)
    cols_to_move = ['Name','NL_YTD','Budget_YTD','YTD_Variance','NL_Month','Budget_Month','Month_Variance']
    x = x[ cols_to_move + [ col for col in x if col not in cols_to_move ] ]
    x = x.set_index('Name')
    return x

@st.cache
def pretty_PL_format(df):
    # If you want to see GP % at one decimal point just change the below to 0.1f it will change everything but is a workaround
    df= df.applymap('{:,.0f}'.format)
    df.loc['Gross Profit %']= df.loc['Gross Profit %'].str.replace('€','').str.replace(',','').astype(float).apply('{:,.0f}%'.format)
    df.loc['Net Profit %']= df.loc['Net Profit %'].str.replace('€','').str.replace(',','').astype(float).apply('{:,.0f}%'.format)
    # df= df.applymap('{:,.0f}'.format)
    return df

@st.cache
def ytd_column_forecast(df,forecast_select):
    forecast_dict= {"Forecast Q1":'F1_YTD',"Forecast Q2":'F2_YTD',"Forecast Q3":'F3_YTD'}
    forecast_var= {"Forecast Q1":'F1_YTD_Variance',"Forecast Q2":'F2_YTD_Variance',"Forecast Q3":'F3_YTD_Variance'}
    selection = forecast_dict[forecast_select]
    selection_1 = forecast_var[forecast_select]
    return df.loc[:,['NL_YTD','Budget_YTD','YTD_Variance',selection,selection_1]]

@st.cache
def month_column_forecast(df,forecast_select):
    forecast_dict= {"Forecast Q1":'F1_Month',"Forecast Q2":'F2_Month',"Forecast Q3":'F3_Month'}
    forecast_var= {"Forecast Q1":'F1_Month_Variance',"Forecast Q2":'F2_Month_Variance',"Forecast Q3":'F3_Month_Variance'}
    selection = forecast_dict[forecast_select]
    selection_1 = forecast_var[forecast_select]
    return df.loc[:,['NL_Month','Budget_Month','Month_Variance',selection,selection_1]]

@st.cache
def end_of_year_forecast(ytd_selection, NL, coding_acc_schedule,projection_selection,Budget_Data,F1_Data,F2_Data,F3_Data,coding_sort,Budget_PL,F1_PL,F2_PL,F3_PL):
    # ytd_selection='Aug_YTD'
    Forecast_rest_year = date_selection_year (projection_selection, ytd_selection, coding_acc_schedule,Budget_Data, F1_Data, F2_Data,F3_Data)
    Actual_plus_Forecast = pd.concat([NL,Forecast_rest_year], axis=0)
    Actual_plus_Forecast = PL_generation( Actual_plus_Forecast,'Name', YTD_Amount = 'NL_YTD', Month_Amount = 'NL_Month' )
    merge_all_projections = (dfs_merge(Actual_plus_Forecast, Budget_PL, F1_PL, F2_PL, F3_PL))
    clean_all_pl = clean_format_PL_presentation(merge_all_projections, coding_sort)
    return clean_all_pl.rename(columns = {'NL_YTD' : 'Projection', 'Budget_YTD': 'Budget', 'F1_YTD':'F1', 'F2_YTD':'F2','F3_YTD':'F3','YTD_Variance':'Var v. Budget'})

@st.cache
def end_of_year_forecast_dept(ytd_selection, NL, coding_acc_schedule,projection_selection,Budget_Data,F1_Data,F2_Data,F3_Data,
coding_sort,Budget_PL,F1_PL,F2_PL,F3_PL,department):
    # ytd_selection='Aug_YTD'
    Forecast_rest_year = date_selection_year (projection_selection, ytd_selection, coding_acc_schedule,Budget_Data, F1_Data, F2_Data,F3_Data)
    Actual_plus_Forecast = pd.concat([NL,Forecast_rest_year], axis=0)
    Actual_plus_Forecast = pl_dept_generation( clean_data=Actual_plus_Forecast, department=department, YTD_Amount = 'NL_YTD', Month_Amount = 'NL_Month' )
    Budget_PL_dept = pl_dept_generation( clean_data=Budget_PL, department=department, YTD_Amount = 'Budget_YTD', Month_Amount = 'Budget_Month' )
    F1_PL_dept = pl_dept_generation( clean_data=F1_PL, department=department, YTD_Amount = 'F1_YTD', Month_Amount = 'F1_Month' )
    F2_PL_dept = pl_dept_generation( clean_data=F2_PL, department=department, YTD_Amount = 'F2_YTD', Month_Amount = 'F2_Month' )
    F3_PL_dept = pl_dept_generation( clean_data=F3_PL, department=department, YTD_Amount = 'F3_YTD', Month_Amount = 'F3_Month' )
    merge_all_projections = (dfs_merge(Actual_plus_Forecast, Budget_PL_dept, F1_PL_dept, F2_PL_dept, F3_PL_dept))
    clean_all_pl = clean_format_PL_presentation(merge_all_projections, coding_sort)
    return clean_all_pl.rename(columns = {'NL_YTD' : 'Projection', 'Budget_YTD': 'Budget', 'F1_YTD':'F1', 'F2_YTD':'F2','F3_YTD':'F3','YTD_Variance':'Var v. Budget'})

@st.cache
def pl_dept_generation(clean_data,department,**kwargs): # NOW CHANGE THE COLUMN NAMES BY USING A FUNCTION?
    # date_dict= {"TV":'T0000',"CG":'CG000',"Post":'P0000',"Admin":'A0000',"Development":'D0000',"IT":'I0000',"Pipeline":'R0000'}
    # x = clean_data [ (clean_data.loc[:,'Department'] == date_dict[department]) ]
    x = clean_data [ (clean_data.loc[:,'Department'] == department )]
    x = x.groupby(['Name']).agg ( YTD_Amount = ( 'Journal Amount','sum' ), Month_Amount = ('Month_Amount','sum'),
    Sorting = ('Sorting','first') ).sort_values(by=['Sorting'], ascending = [True])
    all_sum = x.sum()
    x = x.reset_index()
    x=x.rename(columns=kwargs)
    return x

@st.cache
def date_selection_year(projection_selection, ytd_month_number, coding_acc_schedule,Budget_Data, F1_Data, F2_Data,F3_Data):
    df_dict = {"Budget":Budget_Data, "F1":F1_Data, "F2":F2_Data,"F3":F3_Data}
    df = df_dict[projection_selection]
    date_dict= {"Sep_YTD":1,"Oct_YTD":2,"Nov_YTD":3,"Dec_YTD":4,"Jan_YTD":5,"Feb_YTD":6,"Mar_YTD":7,
    "Apr_YTD":8,"May_YTD":9,"Jun_YTD":10,"Jul_YTD":11,"Aug_YTD":12}
    df = df [ (df['Per.'] > date_dict[ytd_month_number]) ] 
    filter = df['Per.']==date_dict[ytd_month_number]
    df ['Month_Amount'] = df.loc[:,'Journal Amount'].where(filter)
    # st.write( df.loc[df['Name'].isnull()] ) # Always test after merge my issue was with the DONT DELETE THIS COMMENT!
    # spreadsheet didn't have full coding https://stackoverflow.com/questions/53645882/pandas-merging-101
    return df

@st.cache
def dfs_merge(*args):
    df = pd.merge(args[0],args[1], on=['Name','Sorting'], how='outer')
    for d in args[2:]:
        df = pd.merge(df,d, on=['Name','Sorting'], how='outer')
    f = df.set_index('Name')
    f.fillna(0, inplace=True)
    # st.write( c.loc[c['Name'].isnull()] )
    # st.write( c.loc[c['Acc_Schedule'].isnull()] )
    return f



@st.cache
def gp_by_project(data, coding_acc_schedule,Department=None):
    revenue_by_project = group_by_monthly_by_production(data,coding_acc_schedule,'Revenue',Department=Department, Month_Amount = 'NL_Month')
    cos_by_project = group_by_monthly_by_production(data,coding_acc_schedule,'Cost of Sales',Department=Department, Month_Amount = 'NL_Month')
    gp_by_project = revenue_by_project.add (cos_by_project, fill_value=0)
    # st.write ('this is nl revenue amount produced which matches PL',revenue_by_project)
    # st.write ('this is nl cos amount produced which matches PL',cos_by_project)
    # st.write ('this is nl gp amount produced which matches PL',gp_by_project.sum().sum())
    df_gp = pd.DataFrame (gp_by_project.to_records()).set_index('Project_Name')
    df_gp.columns = [x.replace("('Month_Amount', ", "").replace(")", "") for x in df_gp.columns] 
    # https://stackoverflow.com/questions/42708193/pandas-pivot-table-to-data-frame
    return df_gp

@st.cache
def group_by_monthly_by_production(x,coding_acc_schedule,Schedule_Name,Department=None,**kwargs):
    """
    Basically produces a table showing the monthly revenue or cost of sales by Project
    But you can pick to use revenue or cost of sales or anything else as that is an argument in the function called Schedule_Name e.g. Revenue
    """
    x = x.merge (coding_acc_schedule, on=['Acc_Number','Name','Sorting'],how='outer')
    x = x[x['Name']==Schedule_Name]
    if Department !=None:
        x = x[x['Department']==Department]
    y = x.groupby(['Project_Name','Per.'])['Journal Amount'].sum()
    grouped_pivot = x.groupby(['Project_Name','Per.'])['Journal Amount'].sum().unstack()
    return x.groupby(['Project_Name','Per.']).agg ( Month_Amount = ('Journal Amount','sum')).unstack()
    # return y.reset_index()
    # return grouped_pivot.reset_index().set_index('Project').unstack(level='Project')    
    # return x.groupby(['Project_Name','date']).agg ( Month_Amount = ('Journal Amount','sum')).unstack()




@st.cache
def gp_by_project_sales_cos(data, coding_acc_schedule,Schedule_Name='Revenue',Department=None):
    df_gp = group_by_monthly_by_production(data,coding_acc_schedule,Schedule_Name,Department, Month_Amount = 'NL_Month')
    df_gp = pd.DataFrame (df_gp.to_records()).set_index('Project_Name')
    df_gp.columns = [x.replace("('Month_Amount', ", "").replace(")", "") for x in df_gp.columns] 
    return df_gp

@st.cache
def budget_forecast_gp(data, coding_acc_schedule,NL_melt):
    budget = gp_by_project(data, coding_acc_schedule)
    long_budget = long_format_budget(budget, NL_melt)
    x = gp_nl_budget_comp(NL_melt,long_budget)
    return format_gp(x)

def budget_forecast_gp_sales_cos(data, coding_acc_schedule,NL_melt,Schedule_Name='Revenue',Department=None):
    budget = gp_by_project_sales_cos(data, coding_acc_schedule,Schedule_Name,Department)
    long_budget = long_format_budget(budget, NL_melt)
    return gp_nl_budget_comp(NL_melt,long_budget)
    # return format_gp(x)
    # return x

def monthly_forecast_gp_sales_cos(data, coding_acc_schedule,NL_melt,Schedule_Name='Revenue',Department=None):
    budget = gp_by_project_sales_cos(data, coding_acc_schedule,Schedule_Name,Department)
    xx = long_format_budget(budget, NL_melt)
    x = pd.pivot_table(xx, index='Project_Name',columns = 'Per.')
    x.columns = x.columns.droplevel(0)
    # x['Total'] = x.sum(axis=1)
    # x.loc['Total']= x.sum(numeric_only=True, axis=0)
    x.loc[:,'Total'] = x.sum(numeric_only=True, axis=1)
    x=x.iloc[(-x['Total'].abs()).argsort()] #https://stackoverflow.com/questions/30486263/sorting-by-absolute-value-without-changing-the-data
    x.columns = x.columns.astype(str)
    x=x.reset_index().set_index('Project_Name')
    x=x.rename(columns={'1.0':'Sep','2.0':'Oct','3.0':'Nov','4.0':'Dec','5.0':'Jan','6.0':'Feb','7.0':'Mar','8.0':'Apr','9.0':'May',
    '10.0':'Jun','11.0':'Jul','12.0':'Aug'}) # CONTINUE THIS ON check to see if need above code
    return x


@st.cache
def long_format_budget(df_gp, NL):
    max_per = NL ['Per.'].max()
    df_gp = df_gp.reset_index().melt(id_vars=['Project_Name'], value_name='Journal_Amount', var_name='Per.')
    df_gp['Per.'] = pd.to_numeric(df_gp['Per.'])
    return df_gp [ df_gp ['Per.'] <= max_per ]



# def gp_analysis(data,coding_acc_schedule):
#     revenue_by_project = group_by_monthly_by_production(data,coding_acc_schedule,'Revenue', Month_Amount = 'NL_Month')
#     cos_by_project = group_by_monthly_by_production(data,coding_acc_schedule,'Cost of Sales', Month_Amount = 'NL_Month')








# @st.cache
def format_gp(x):
    # return x.style.format("{:,.0f}",na_rep="-")
    return x.style.format("{:,.0f}",na_rep="-").applymap(color_negative_red)
    # .format(background_gradient(cmap='Blues'))


def color_negative_red(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for negative
    strings, black otherwise.
    """
    color = 'red' if val < 0 else 'black'
    return 'color: %s' % color

# @st.cache
def long_format_nl(df_gp):
    df_gp = df_gp.reset_index().melt(id_vars=['Project_Name'], value_name='Journal_Amount', var_name='Per.')
    df_gp['Per.'] = pd.to_numeric(df_gp['Per.'])
    return df_gp

# @st.cache
def gp_nl_budget_comp(nl,budget):
    x = pd.merge(nl, budget, on=['Project_Name','Per.'], how='outer')
    x =x.fillna(value=0)
    x['Journal_Amount'] = x['Journal_Amount_x'] - x['Journal_Amount_y']
    xx = x.loc[:,['Project_Name','Per.','Journal_Amount']] 
    x=x.dropna(subset=['Journal_Amount'])
    x = x [ x['Journal_Amount'] != 0 ]
    x = x [(x['Journal_Amount'] < -0.5) | (x['Journal_Amount'] > 0.5)]
    x = pd.pivot_table(xx, index='Project_Name',columns = 'Per.')
    x.columns = x.columns.droplevel(0)
    x['Total'] = x.sum(axis=1)
    x=x.iloc[(-x['Total'].abs()).argsort()] #https://stackoverflow.com/questions/30486263/sorting-by-absolute-value-without-changing-the-data
    # x.loc['Total'] = x.sum()
    x.columns = x.columns.astype(str)
    x=x.reset_index().set_index('Project_Name')
    x=x.rename(columns={'1.0':'Sep','2.0':'Oct','3.0':'Nov','4.0':'Dec','5.0':'Jan','6.0':'Feb','7.0':'Mar','8.0':'Apr','9.0':'May',
    '10.0':'Jun','11.0':'Jul','12.0':'Aug'}) # CONTINUE THIS ON check to see if need above code
    return x

def get_total_by_month(x):
    return x.sum().reset_index().rename(columns={0:'Total_Amount_by_Month_','Per.':'Month'}).set_index('Month').transpose()



def UK_clean_921(x):
    x['Payroll_Amt'] = x.groupby (['Jrn. No.','Description'])['Journal Amount'].transform('sum')
    x['Headcount'] = x['Journal Amount'] / x['Payroll_Amt']
    return x




def combined_921_headcount(ee,UK,Mauve):
    employee_921=company_ee_project(ee).drop(['Employee - Ext. Code'], axis=1).reset_index()
    UK_921=UK_clean_921(UK).drop(['Description'], axis=1).reset_index()
    Mauve_2021=credit_notes_resolve(Mauve).reset_index()
    combined = pd.concat([employee_921, UK_921, Mauve_2021]).drop(['index'],axis=1)
    combined['Headcount']=pd.to_numeric(combined['Headcount'])
    # combined=combined.groupby(['Yr.','Per.','Project'])['Headcount'].head(2).sum()
    # combined=combined.reset_index()
    # st.write('this is Mauve any Description??', Mauve_2021.head())
    combined=combined.groupby(['calendar_year','calendar_month','Project','Project_Name'])['Headcount'].sum().reset_index()
    combined = combined.sort_values(by=['calendar_year','calendar_month','Headcount'], ascending=[True,True,False])
    combined['calendar_year']=combined['calendar_year']+2000
    combined=combined.rename(columns={'calendar_year':'year', 'calendar_month':'month'})
    combined['day']=1
    combined['date']=pd.to_datetime(combined[['year','month','day']],infer_datetime_format=True)
    # combined['date'] = pd.to_datetime(combined['date'], format='%Y-%m-%d')
    # combined['date']=combined['date'].dt.to_period('m')
    return combined

def pivot_headcount(x):
    summary= pd.pivot_table(x, values='Headcount',index=['Project'], columns=['date'],margins=True,aggfunc='sum',fill_value=0)
    summary = summary.sort_values(by=['All'],ascending=False)
    summary=summary.reset_index().set_index('Project')
    return summary

def final_headcount(data, account_code):
    sch_921=data.query('`Account Code`==@account_code').loc[:,
    ['Description','Journal Amount','Src. Account','Jrn. No.','calendar_year','calendar_month','Project_Name','Project']]
    # st.write ('nl', sch_921.head()) #https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.query.html
    group_supplier=sch_921.groupby(['Src. Account','Jrn. No.','calendar_year','calendar_month','Project','Project_Name'])['Journal Amount'].sum().reset_index()
    group_UK = sch_921.query('`Src. Account`=="BUK02"')
    group_no_UK = group_supplier.query('`Src. Account`!="BUK02"')
    sch_921_ee=data.query('`Account Code`==@account_code').loc[:,
    ['Journal Amount','Src. Account','Jrn. No.','calendar_year','calendar_month','Project','Employee - Ext. Code','Project_Name']]
    return combined_921_headcount(sch_921_ee,group_UK,group_no_UK)

def create_pivot_comparing_production_headcount(shifted_df):
    shifted_df=shifted_df.drop('All',axis=1).drop(['All'])
    shifted_df.columns = np.arange(len(shifted_df.columns))
    shifted_df=shifted_df.replace(0,np.NaN)
    return shifted_df.apply(lambda x: pd.Series(x.dropna().values), axis=1).fillna(0)

@st.cache
def load_ledger_data(x):
    return pd.read_excel(x)

def month_period_clean(x):
    x['calendar_month']=x['Per.'].map({1:9,2:10,3:11,4:12,5:1,6:2,7:3,8:4,9:5,10:6,11:7,12:8,19:8})
    x['calendar_year'] = np.where((x['Per.'] > 4.1), x['Yr.'], x['Yr.']-1)
    return x

# @st.cache
def load_data(x,coding_acc_schedule):
    # NL = load_ledger_data(x)
    stop_mutating_df = NL_Raw_Clean_File(x, coding_acc_schedule).copy()
    return month_period_clean(stop_mutating_df)

# @st.cache
def load_16_19_clean(x,coding_acc_schedule):
    # NL = load_ledger_data(x)
    NL_update = NL_Raw_Clean_File(x, coding_acc_schedule).copy()
    NL_update_1=NL_update.join(NL_update['Employee'].str.split(' ', expand=True).rename(columns={0:'EE',1:'Name_EE'}))
    NL_update_1['Employee - Ext. Code']=NL_update_1['EE']
    return month_period_clean(NL_update_1)

def forecast_resourcing_function(x,forecast_project_mapping,start_forecast_period_resourcing_tool):
    # x=load_ledger_data(forecast_resourcing_file).copy()
    # forecast_project_mapping=pd.
    x=pd.merge(x,forecast_project_mapping,on='Project',how='outer').drop('Project',axis=1).rename(columns={'Project_name':'Project'})
    # st.write(x)
    x.columns= x.columns.astype(str)
    sliced_x=x.loc[:,start_forecast_period_resourcing_tool:]
    sliced_x=sliced_x.set_index('Project').unstack(level='Project').reset_index().rename(columns={'level_0':'date',0:'headcount'})
    sliced_x=sliced_x.groupby(['Project','date'])['headcount'].sum().reset_index()    
    x = pd.pivot_table(sliced_x, values='headcount',index=['Project'], columns=['date'],fill_value=0)
    return x



@st.cache
def df_concat(NL_Data_16_19,NL_Data_20,NL_Data_21):
    return pd.concat([NL_Data_16_19,NL_Data_20,NL_Data_21],ignore_index=True)

@st.cache
def df_concat_20_21(NL_Data_20,NL_Data_21):
    return pd.concat([NL_Data_20,NL_Data_21],ignore_index=True)


def headcount_actual_plus_forecast(actual_headcount_direct,forecast_headcount_direct):
    actual=actual_headcount_direct.drop('All',axis=1).drop(['All'])
    return pd.concat([actual,forecast_headcount_direct],axis=1)

def headcount_actual_plus_forecast_with_subtotal(merged):
    merged.loc['All']= merged.sum(numeric_only=True, axis=0)
    merged.loc[:,'All'] = merged.sum(numeric_only=True, axis=1)
    return merged.sort_values(by='All',ascending=False)

def data_for_graphing(x):
    return x.unstack(level='Project').reset_index().rename(columns={0:'headcount'})

def acc_schedule_find(x, Schedule_Name):
    x = x[x['Name']==Schedule_Name]
    # return x.groupby(['Project_Name','Yr.'])['Journal Amount'].sum()
    return x.groupby(['Project_Name'])['Journal Amount'].sum()

def test_gp_by_project(data):
    revenue_by_project = acc_schedule_find(data,'Revenue')
    cos_by_project = acc_schedule_find(data,'Cost of Sales')
    gp_by_project = revenue_by_project.add (cos_by_project, fill_value=0)
    return gp_by_project

def acc_schedule_find_monthly(x, Schedule_Name):
    x = x[x['Name']==Schedule_Name]
    return x.groupby(['Project_Name','date'])['Journal Amount'].sum()

def test_gp_by_project_monthly(data):
    revenue_by_project = acc_schedule_find_monthly(data,'Revenue')
    cos_by_project = acc_schedule_find_monthly(data,'Cost of Sales')
    gp_by_project = revenue_by_project.add (cos_by_project, fill_value=0)
    return gp_by_project


def gp_percent_by_project(production_gross_profit,production_revenue):
    # gp_percent=production_gross_profit['Gross_Profit'] / production_revenue['Revenue']
    # gp_percent= production_gross_profit.divide(production_revenue)*100
    gp_percent= production_gross_profit.divide(production_revenue,fill_value=0)*100 # Can I get divdie to recognise the different columsn
    gp_percent=gp_percent.replace([np.inf, -np.inf], np.nan).fillna(0)
    return gp_percent

def gp_revenue_concat(production_gross_profit, production_revenue, production_gp_percent):
    production_gross_profit=production_gross_profit.reset_index().rename(columns={'Journal Amount':'Gross_Profit'}).set_index('Project_Name')
    production_revenue=production_revenue.reset_index().rename(columns={'Journal Amount':'Revenue'}).set_index('Project_Name')
    production_gp_percent=production_gp_percent.reset_index().rename(columns={'Journal Amount':'GP %'}).set_index('Project_Name')
    table= pd.concat([production_revenue, production_gross_profit, production_gp_percent],axis=1)
    return table.sort_values(by='Revenue',ascending=False)

def format_table(x):
    return x.style.format({'GP %': "{:,.0f}%", 'Revenue': '{:,.0f}', 'Gross_Profit': '{:,.0f}'})

def headcount_921_940(data):
    sch_921=data.query('(`Account Code`=="921-0500") or (`Account Code`=="940-0500")').loc[:,
    ['Description','Journal Amount','Src. Account','Jrn. No.','calendar_year','calendar_month','Project','Acc_Schedule','Project_Name','Department',]]
    # st.write('data',data.head())
    # st.write ('nl', sch_921.head()) #https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.query.html
    group_supplier=sch_921.groupby(['Src. Account','Jrn. No.','calendar_year','calendar_month','Project','Acc_Schedule','Project_Name','Department','Description'])['Journal Amount'].sum().reset_index()
    group_UK = sch_921.query('`Src. Account`=="BUK02"')
    group_no_UK = group_supplier.query('`Src. Account`!="BUK02"')
    sch_921_ee=data.query('(`Account Code`=="921-0500") or (`Account Code`=="940-0500")').loc[:,
    ['Journal Amount','Src. Account','Jrn. No.','calendar_year','calendar_month','Project','Employee - Ext. Code','Acc_Schedule','Project_Name','Department','Description']]
    sch_921_ee=sch_921_ee.query('`Jrn. No.`!="000007362"') # Accrual made in march '21 which has UK employee numbers
    sch_921_ee=sch_921_ee.query('`Jrn. No.`!="X00007362"') # reversal of above accrual

    # I COPIED THIS FROM BBF_EE FUNCTION BELOW
    sch_921_ee=sch_921_ee.query('`Jrn. No.`!="000007362"') # Accrual made in march '21 which has UK employee numbers
    sch_921_ee=sch_921_ee.query('`Jrn. No.`!="X00007362"') # reversal of above accrual
    sch_921_ee=sch_921_ee.query('`Jrn. No.`!="000007470"') # pension might need to fix in may will see
    sch_921_ee=sch_921_ee.query('`Jrn. No.`!="000007465"') # pension might need to fix in may will see
    sch_921_ee['calendar_month']=np.where(sch_921_ee['Jrn. No.']=='9SM-BBF146', 3, sch_921_ee['calendar_month'])
    sch_921_ee['calendar_month']=np.where(sch_921_ee['Jrn. No.']=='9SM-BBF144', 1, sch_921_ee['calendar_month'])
    sch_921_ee['calendar_month']=np.where(sch_921_ee['Jrn. No.']=='9SM-BBF142', 12, sch_921_ee['calendar_month'])
    sch_921_ee['calendar_year']=np.where(sch_921_ee['Jrn. No.']=='9SM-BBF142', 20, sch_921_ee['calendar_year'])
    sch_921_ee['calendar_month']=np.where(sch_921_ee['Jrn. No.']=='9SM-BBF141', 11, sch_921_ee['calendar_month'])
    sch_921_ee['calendar_year']=np.where(sch_921_ee['Jrn. No.']=='9SM-BBF141', 20, sch_921_ee['calendar_year'])
    sch_921_ee['calendar_month']=pd.to_numeric(sch_921_ee['calendar_month'])
    sch_921_ee=sch_921_ee.query('`Jrn. No.`!="9SM-BBF1CN"') # J Reeves credit note and invoice
    sch_921_ee=sch_921_ee.query('`Jrn. No.`!="9SMBBF139"') # J Reeves credit note and invoice
    sch_921_ee=sch_921_ee.query('`Jrn. No.`!="000007163"') # Malcolm vanA reclass
    sch_921_ee=sch_921_ee.query('`Jrn. No.`!="000007208"') # Malcolm vanA deposit
    # st.write('TESTING BBF EMPLOYEES WITHIN headcount 921_940 function',sch_921_ee.head())
    return headcount_function(sch_921_ee,group_UK,group_no_UK)   

def headcount_function(ee,UK,Mauve):
    # employee_921=company_ee_project(ee).drop(['Employee - Ext. Code'], axis=1).reset_index()
    employee_921=company_ee_project(ee).reset_index()
    employee_921['Category']='BBF'
    # employee_921['calendar_month']=np.where(employee_921['Jrn. No.']=='9SM-BBF146', 3, employee_921['calendar_month'])
    # employee_921['calendar_month']=np.where(employee_921['Jrn. No.']=='9SM-BBF144', 1, employee_921['calendar_month'])
    # employee_921['calendar_month']=np.where(employee_921['Jrn. No.']=='9SM-BBF142', 12, employee_921['calendar_month'])
    # employee_921['calendar_month']=np.where(employee_921['Jrn. No.']=='9SM-BBF141', 11, employee_921['calendar_month'])
    # test_ee = employee_921.copy()
    # st.write('TESTING the category within headcount_function should be same as below')
    # test_ee['Headcount']=pd.to_numeric(test_ee['Headcount'])
    # test_ee=test_ee.groupby(['calendar_year','calendar_month','Acc_Schedule','Department','Project_Name','Project','Description','Category'])['Headcount'].sum().reset_index()
    # test_ee = test_ee.sort_values(by=['calendar_year','calendar_month','Acc_Schedule','Department','Project_Name','Headcount'], ascending=[True,True,True,True,True,False])
    # test_ee['calendar_year']=test_ee['calendar_year']+2000
    # test_ee=test_ee.rename(columns={'calendar_year':'year', 'calendar_month':'month'})
    # test_ee['day']=1
    # test_ee['date']=pd.to_datetime(test_ee[['year','month','day']],infer_datetime_format=True)
    # st.write(pivot_headcount_category(test_ee))
    # st.write('xxxxxxxxxxxxxxxxxxxxxxxxx')
    # st.write('BBF description employee', employee_921.head())
    # st.write(UK)
    # UK_921=UK_clean_921(UK).drop(['Description'], axis=1).reset_index()
    UK_921=UK_clean_921(UK).reset_index()
    # st.write(UK_921.head())
    UK_921['calendar_month']=np.where(UK_921['Jrn. No.']=='BUK0000979', 3, UK_921['calendar_month'])
    UK_921['Category']='BBF_UK'
    # st.write('UK issue with March invoice entered in April', UK_921.groupby(['calendar_month'])['Headcount'].sum())
    Mauve_2021=credit_notes_resolve(Mauve).reset_index()
    Mauve_2021['Category']='Mauve'
    # st.write('Description with Mauve before function??',Mauve.head())
    # st.write('Description with Mauve??',Mauve_2021.head())
    # st.write('Mauve', Mauve_2021.groupby(['calendar_month'])['Headcount'].sum())
    combined = pd.concat([employee_921, UK_921, Mauve_2021]).drop(['index'],axis=1)
    combined['Headcount']=pd.to_numeric(combined['Headcount'])
    # combined=combined.groupby(['Yr.','Per.','Project'])['Headcount'].head(2).sum()
    # combined=combined.reset_index()
    # st.write('COMBINED This is combined what employee or description will i take',combined.head())
    combined=combined.groupby(['calendar_year','calendar_month','Acc_Schedule','Department','Project_Name','Project','Description','Category'])['Headcount'].sum().reset_index()
    combined = combined.sort_values(by=['calendar_year','calendar_month','Acc_Schedule','Department','Project_Name','Headcount'], ascending=[True,True,True,True,True,False])
    combined['calendar_year']=combined['calendar_year']+2000
    combined=combined.rename(columns={'calendar_year':'year', 'calendar_month':'month'})
    combined['day']=1
    combined['date']=pd.to_datetime(combined[['year','month','day']],infer_datetime_format=True)
    # combined['date'] = pd.to_datetime(combined['date'], format='%Y-%m-%d')
    # combined['date']=combined['date'].dt.to_period('m')
    return combined

def clean_wrangle_headcount(data):
    sch_921_ee=data.query('(`Account Code`=="921-0500") or (`Account Code`=="940-0500")').loc[:,
    ['Journal Amount','Employee','Src. Account','Jrn. No.','calendar_year','calendar_month','Project','Employee - Ext. Code','Acc_Schedule','Project_Name','Department','Description']]
    sch_921_ee=sch_921_ee.query('`Jrn. No.`!="000007362"') # Accrual made in march '21 which has UK employee numbers
    sch_921_ee=sch_921_ee.query('`Jrn. No.`!="X00007362"') # reversal of above accrual
    sch_921_ee=sch_921_ee.query('`Jrn. No.`!="000007470"') # pension might need to fix in may will see
    sch_921_ee=sch_921_ee.query('`Jrn. No.`!="000007465"') # pension might need to fix in may will see
    sch_921_ee['calendar_month']=np.where(sch_921_ee['Jrn. No.']=='9SM-BBF146', 3, sch_921_ee['calendar_month'])
    sch_921_ee['calendar_month']=np.where(sch_921_ee['Jrn. No.']=='9SM-BBF144', 1, sch_921_ee['calendar_month'])
    sch_921_ee['calendar_month']=np.where(sch_921_ee['Jrn. No.']=='9SM-BBF142', 12, sch_921_ee['calendar_month'])
    sch_921_ee['calendar_year']=np.where(sch_921_ee['Jrn. No.']=='9SM-BBF142', 20, sch_921_ee['calendar_year'])
    sch_921_ee['calendar_month']=np.where(sch_921_ee['Jrn. No.']=='9SM-BBF141', 11, sch_921_ee['calendar_month'])
    sch_921_ee['calendar_year']=np.where(sch_921_ee['Jrn. No.']=='9SM-BBF141', 20, sch_921_ee['calendar_year'])
    sch_921_ee['calendar_month']=pd.to_numeric(sch_921_ee['calendar_month'])
    sch_921_ee=sch_921_ee.query('`Jrn. No.`!="9SM-BBF1CN"') # J Reeves credit note and invoice
    sch_921_ee=sch_921_ee.query('`Jrn. No.`!="9SMBBF139"') # J Reeves credit note and invoice
    sch_921_ee=sch_921_ee.query('`Jrn. No.`!="000007163"') # Malcolm vanA reclass
    sch_921_ee=sch_921_ee.query('`Jrn. No.`!="000007208"') # Malcolm vanA deposit
    sch_921_ee=sch_921_ee.query('`Jrn. No.`!="000007459"') # Luke reclass in April 21 from IT to Pipeline
    return sch_921_ee

def mauve_staff(sch_921):
    group_supplier=sch_921.groupby(['Src. Account','Jrn. No.','calendar_year','calendar_month','Project','Acc_Schedule','Project_Name','Department','Description'])['Journal Amount'].sum().reset_index()
    # group_UK = sch_921.query('`Src. Account`=="BUK02"')
    group_no_UK = group_supplier.query('`Src. Account`!="BUK02"')
    Mauve_2021=credit_notes_resolve(group_no_UK).reset_index()
    Mauve_2021['Category']='Mauve'
    Mauve_2021 = headcount_date_clean(Mauve_2021)
    return Mauve_2021

def uk_staff(sch_921):
    group_UK = sch_921.query('`Src. Account`=="BUK02"')
    UK_921=UK_clean_921(group_UK).reset_index()
    # st.write(UK_921.head())
    UK_921['calendar_month']=np.where(UK_921['Jrn. No.']=='BUK0000979', 3, UK_921['calendar_month'])
    UK_921['Category']='BBF_UK'
    UK_921 = headcount_date_clean(UK_921)
    return UK_921



# def credit_notes_resolve_updated(x):
#     credit_notes=x['Jrn. No.'].str.contains('CN|CR')
#     filter_credit_notes=x[credit_notes]
#     filter_non_credit_notes=x[~credit_notes]
#     # non_UK_contractor_921=pd.concat([filter_credit_notes,filter_non_credit_notes])
#     non_UK_contractor_921['Payroll_Amt'] = filter_non_credit_notes.groupby (['Jrn. No.'])['Journal Amount'].transform('sum')
#     non_UK_contractor_921['Headcount'] = non_UK_contractor_921['Journal Amount'] / non_UK_contractor_921['Payroll_Amt']
#     return non_UK_contractor_921

def credit_notes_resolve(x):
    # don't understand this function but let's keep going....why add credit and non credit back together using concat
    credit_notes=x['Jrn. No.'].str.contains('CN|CR')
    filter_credit_notes=x[credit_notes]
    filter_non_credit_notes=x[~credit_notes]
    non_UK_contractor_921=pd.concat([filter_credit_notes,filter_non_credit_notes])
    non_UK_contractor_921['Payroll_Amt'] = non_UK_contractor_921.groupby (['Jrn. No.'])['Journal Amount'].transform('sum')
    non_UK_contractor_921['Headcount'] = non_UK_contractor_921['Journal Amount'] / non_UK_contractor_921['Payroll_Amt']
    return non_UK_contractor_921

def headcount_date_clean(employee_921):
    employee_921['Headcount']=pd.to_numeric(employee_921['Headcount'])
    employee_921['calendar_year']=employee_921['calendar_year']+2000
    employee_921=employee_921.rename(columns={'calendar_year':'year', 'calendar_month':'month'})
    employee_921['day']=1
    employee_921['date']=pd.to_datetime(employee_921[['year','month','day']],infer_datetime_format=True)
    return employee_921

def bbf_employees(employee_921):
    employee_921=company_ee_project(employee_921).reset_index()
    employee_921['Category']='BBF'
    employee_921 = headcount_date_clean(employee_921)
    return employee_921



def company_ee_project(x):
    x['Employee - Ext. Code'] = pd.to_numeric(x['Employee - Ext. Code'])
    x= x.query('`Employee - Ext. Code`>0.5')
    x = x.query('`Src. Account`!="BUK02"')
    x['Payroll_Amt'] = x.groupby (['calendar_year','calendar_month','Employee - Ext. Code','Jrn. No.'])['Journal Amount'].transform('sum')
    x['Headcount'] = x['Journal Amount'] / x['Payroll_Amt']
    x=x.replace([np.inf, -np.inf], np.nan) # due to 0 dividing by the journal amount
    return x

def format_dataframe(x):
    return x.style.format("{:,.2f}",na_rep="-")

def pivot_headcount_dept(x):
    summary= pd.pivot_table(x, values='Headcount',index=['Department'], columns=['date'],margins=True,aggfunc='sum',fill_value=0)
    summary = summary.sort_values(by=['All'],ascending=False)
    summary=summary.reset_index().set_index('Department')
    return summary

def pivot_headcount_category(x):
    summary= pd.pivot_table(x, values='Headcount',index=['Category'], columns=['date'],margins=True,aggfunc='sum',fill_value=0)
    summary = summary.sort_values(by=['All'],ascending=False)
    summary=summary.reset_index().set_index('Category')
    return summary

def pivot_headcount_ee(x):
    summary= pd.pivot_table(x, values='Headcount',index=['Employee'], columns=['date'],margins=True,aggfunc='sum',fill_value=0)
    summary = summary.sort_values(by=['All'],ascending=False)
    summary=summary.reset_index().set_index('Employee')
    return summary

def pivot_headcount_mauve(x):
    summary= pd.pivot_table(x, values='Headcount',index=['Jrn. No.'], columns=['date'],margins=True,aggfunc='sum',fill_value=0)
    summary = summary.sort_values(by=['All'],ascending=False)
    summary=summary.reset_index().set_index('Jrn. No.')
    return summary

def pivot_headcount_uk(x):
    summary= pd.pivot_table(x, values='Headcount',index=['Description'], columns=['date'],margins=True,aggfunc='sum',fill_value=0)
    summary = summary.sort_values(by=['All'],ascending=False)
    summary=summary.reset_index().set_index('Description')
    return summary


def forecast_resourcing_dept(x,forecast_project_mapping,start_forecast_period_resourcing_tool):
    x=pd.merge(x,forecast_project_mapping,on='Project',how='outer').drop('Project',axis=1).rename(columns={'Project_name':'Project','division':'Department'})
    x.columns= x.columns.astype(str)
    # st.write(x)
    col = x.pop("Department")
    last_position=47
    x=x.insert(last_position, col.name, col)
    st.write('after insert function')
    st.write(x)
    sliced_x=x.loc[:,start_forecast_period_resourcing_tool:]
    yy=sliced_x.copy()
    st.write(yy.head())
    sliced_x=sliced_x.set_index('Department').unstack(level='Department').reset_index().rename(columns={'level_0':'date',0:'headcount'})
    sliced_x=sliced_x.groupby(['Department','date'])['headcount'].sum().reset_index()    
    x = pd.pivot_table(sliced_x, values='headcount',index=['Department'], columns=['date'],fill_value=0)
    return x

def test_forecast_resourcing_dept(x,forecast_project_mapping,start_forecast_period_resourcing_tool):
    # st.write(x)
    x= pd.merge(x,forecast_project_mapping,on='Project',how='outer').drop('Project',axis=1).rename(columns={'Project_name':'Project','Division':'Department'})
    # st.write('full data for forecast is dept missing', x.head())
    # st.write(x[x['Department'].isnull()]) # ALWAYS CHECK FOR NAN VALUES
    # x['Department'] = x['Department'].replace({np.nan:'CG'})
    # st.write(x[x['Department'].isnull()])
    x.columns= x.columns.astype(str)
    col = x.pop("Department")
    x.insert(x.columns.get_loc('Project') + 1, col.name, col)
    sliced_x=x.loc[:,start_forecast_period_resourcing_tool:]
    sliced_x = sliced_x.drop(columns=['Project'])
    sliced_x=sliced_x.set_index('Department').unstack(level='Department').reset_index().rename(columns={'level_0':'date',0:'headcount'})
    sliced_x=sliced_x.groupby(['Department','date'])['headcount'].sum().reset_index()    
    x = pd.pivot_table(sliced_x, values='headcount',index=['Department'], columns=['date'],fill_value=0)
    return x

def new_headcount_actual_plus_forecast(actual_headcount_direct,forecast_headcount_direct):
    actual=actual_headcount_direct.drop('All',axis=1).drop(['All'])
    # forecast=forecast_headcount_direct.drop('All',axis=1).drop(['All'])
    merged_values = pd.concat([actual,forecast_headcount_direct],axis=1).ffill(axis=1)
    return merged_values

def data_for_graphing_dept(x, select_level):
    return x.unstack(level=select_level).reset_index().rename(columns={0:'headcount'}).set_index('date').drop(['All'])\
    .reset_index().set_index(select_level).drop(['All']).reset_index()

def data_for_graphing_overall(x, select_level):
    update = x.unstack(level=select_level).reset_index().rename(columns={0:'headcount'}).set_index('date').drop(['All'])\
    .reset_index().set_index(select_level).reset_index()
    return update[update['Department'].isin(['All'])].copy()

def headcount_concat(actual_headcount_direct,forecast_headcount_direct):
    actual=actual_headcount_direct.drop('All',axis=1).drop(['All'])
    forecast = forecast_headcount_direct.drop('All',axis=1).drop(['All'])
    return pd.concat([actual,forecast],axis=1)

def forecast_resourcing_test(x,forecast_project_mapping,start_forecast_period_resourcing_tool):
    # x=load_ledger_data(forecast_resourcing_file).copy()
    # forecast_project_mapping=pd.
    # x=pd.merge(x,forecast_project_mapping,on='Project',how='outer').drop('Project',axis=1).rename(columns={'Project_name':'Project'})
    # x=pd.merge(x,forecast_project_mapping,on='Project',how='outer').drop('Project_name',axis=1).rename(columns={'Project':'Project'})
    x=pd.merge(x,forecast_project_mapping,on='Project',how='outer')
    x['Project_update'] = x['Project_name'].str[8:]
    x= x.drop(['Project','Project_name'], axis=1).rename(columns={'Project_update':'Project'})
    # st.write('test project', x)
    x = x[ [ col for col in x.columns if col != 'Project' ] + ['Project'] ]
    # st.write(x)
    x.columns= x.columns.astype(str)
    sliced_x=x.loc[:,start_forecast_period_resourcing_tool:]
    sliced_x=sliced_x.set_index('Project').unstack(level='Project').reset_index().rename(columns={'level_0':'date',0:'headcount'})
    sliced_x=sliced_x.groupby(['Project','date'])['headcount'].sum().reset_index()    
    x = pd.pivot_table(sliced_x, values='headcount',index=['Project'], columns=['date'],fill_value=0)
    return x

def test_pivot_headcount(x):
    # st.write('this is input to test pivot headcount actual function',x)
    x= x.drop('Project', axis=1).rename(columns={'Project_Name':'Project'})
    summary= pd.pivot_table(x, values='Headcount',index=['Project'], columns=['date'],margins=True,aggfunc='sum',fill_value=0)
    summary = summary.sort_values(by=['All'],ascending=False)
    summary=summary.reset_index().set_index('Project')
    return summary

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    val = to_excel(df)
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="extract.xlsx">Download csv file</a>' # decode b'abc' => abc

def chart_gp(x):
    return alt.Chart(x).mark_circle(size=200).encode(
        alt.X('GP %',scale=alt.Scale(zero=False)),
        y='Gross_Profit',
        color='Project_Name',
        tooltip='Project_Name',
    ).interactive()

def chart_gp_test(x):
    base= alt.Chart(x).mark_circle(size=200).encode(
        alt.X('GP %',scale=alt.Scale(zero=False)),
        y='Gross_Profit',
        color='Project_Name',
        tooltip='Project_Name',
    ) #https://stackoverflow.com/questions/65503289/altair-selection-error-javascript-error-duplicate-signal-name-selector074-i
    text_on_base=base.mark_text(align='left',baseline='middle',dx=10,opacity=0.8).encode(text='Project_Name')
    return base.interactive() + text_on_base

def chart_gp_test_1(x):
    base = alt.Chart(x).mark_circle(size=200).encode(
        alt.X('GP %',scale=alt.Scale(zero=False)),
        y=alt.Y('Gross_Profit'),
        # text=alt.Text('Project_Name'),
        color='Project_Name',
        tooltip='Project_Name',
    ) #https://stackoverflow.com/questions/65503289/altair-selection-error-javascript-error-duplicate-signal-name-selector074-i
    text_on_base=base.mark_text(align='left',baseline='middle',dx=3).encode(text='Project_Name')
    # got rid of interactive()
    return base.interactive()
    # return (base+text_on_base)

def chart_area_headcount(x,select_coding,tooltip_selection):
    return alt.Chart(x).mark_area().encode(
        alt.X('yearmonth(date):T',axis=alt.Axis(title='date',labelAngle=90)),
        y='headcount',
        color=select_coding,
        tooltip=tooltip_selection,
    ).interactive()

def data_up_to_date(x,ytd_selection):
    return date_selection_for_PL(x,ytd_selection)

def long_format_function(x):
    # max_per = NL ['Per.'].max()
    x = x.drop(['Total'],axis=1)
    return x.cumsum(axis=1)
    # df_gp = df_gp.reset_index().melt(id_vars=['Project_Name'], value_name='Journal_Amount', var_name='Per.')

def format_table_percent(x):
    return x.style.format({ "{:,.0f}%"})
