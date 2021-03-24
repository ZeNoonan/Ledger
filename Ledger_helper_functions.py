import pandas as pd
import numpy as np
import streamlit as st

@st.cache
def Budget_Raw_Clean_File(Budget_Raw_Clean,coding_acc_schedule, Project_codes):
    Budget_Raw_Clean['Acc_Schedule']=Budget_Raw_Clean['ACCOUNT'].str[-8:-5]
    Budget_Raw_Clean['Acc_Schedule']=pd.to_numeric(Budget_Raw_Clean['Acc_Schedule'])
    Budget_Raw_Clean['Acc_Number']=Budget_Raw_Clean['ACCOUNT'].str[-8:]
    Budget_Raw_Clean['Department'] = Budget_Raw_Clean['ACCOUNT'].str[-14:-9]
    Budget_Raw_Clean.loc[:,'BUDGET 1':'BUDGET 12'] = Budget_Raw_Clean.loc[:,'BUDGET 1':'BUDGET 12'] *-1
    Budget_Raw_Clean = Budget_Raw_Clean.melt(id_vars=['ACCOUNT', 'SUBANALYSIS 0','Acc_Schedule','Acc_Number','Department'],value_name='Journal Amount',var_name='Per.')
    Budget_Raw_Clean['Per.'] = Budget_Raw_Clean['Per.'].str[7:]
    Budget_Raw_Clean['Per.'] = pd.to_numeric(Budget_Raw_Clean['Per.'])
    Budget_Raw_Clean = Budget_Raw_Clean.merge (coding_acc_schedule, on='Acc_Number',how='outer')
    Budget_Raw_Clean['Department'] =Budget_Raw_Clean['Department'].replace( {'T0000':"TV",'CG000':"CG",
    'P0000':"Post",'A0000':"Admin",'D0000':"Development",'I0000':"IT",'R0000':"Pipeline"})
    Budget_Raw_Clean = pd.merge(Budget_Raw_Clean, Project_codes, on=['SUBANALYSIS 0'], how='outer').rename(columns = {'Description' : 'Project_Name'})
    return Budget_Raw_Clean

@st.cache
def NL_Raw_Clean_File(NL_Raw_Clean, coding_acc_schedule):
    NL_Raw_Clean['Acc_Schedule']=NL_Raw_Clean['Account Code'].str[:3]
    NL_Raw_Clean['Acc_Schedule']=pd.to_numeric(NL_Raw_Clean['Acc_Schedule'])
    NL_Raw_Clean['Project_Code'] = NL_Raw_Clean['Project'].str[:8]
    NL_Raw_Clean['Project_Name'] = NL_Raw_Clean['Project'].str[8:]
    NL_Raw_Clean['Acc_Number'] = NL_Raw_Clean['Account Code']
    NL_Raw_Clean['Journal Amount'] = NL_Raw_Clean['Journal Amount'] * -1
    NL_Raw_Clean = NL_Raw_Clean.merge (coding_acc_schedule, on='Acc_Number',how='outer')
    NL_Raw_Clean['Department'] = NL_Raw_Clean['Department'].replace( {'T0000':"TV",'CG000':"CG",
    'P0000':"Post",'A0000':"Admin",'D0000':"Development",'I0000':"IT",'R0000':"Pipeline"})
    return NL_Raw_Clean

@st.cache
def date_selection_for_PL(df, ytd_month_number):
    # def date_selection(df, ytd_month_number, department=None):
    date_dict= {"Sep_YTD":1,"Oct_YTD":2,"Nov_YTD":3,"Dec_YTD":4,"Jan_YTD":5,"Feb_YTD":6,"Mar_YTD":7,
    "Apr_YTD":8,"May_YTD":9,"Jun_YTD":10,"Jul_YTD":11,"Aug_YTD":12}
    df = df [ (df['Per.'] <= date_dict[ytd_month_number]) ] 
    filter = df['Per.']==date_dict[ytd_month_number]
    df ['Month_Amount'] = df.loc[:,'Journal Amount'].where(filter)
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
    x.loc['Gross Profit %'] = ( (gross_profit / x.loc['Revenue'])*100 )
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
    df= df.applymap('{:,.0f}'.format)
    df.loc['Gross Profit %']= df.loc['Gross Profit %'].str.replace('€','').str.replace(',','').astype(float).apply('{:,.0f}%'.format)
    df.loc['Net Profit %']= df.loc['Net Profit %'].str.replace('€','').str.replace(',','').astype(float).apply('{:,.0f}%'.format)
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

# @st.cache
def group_by_monthly_by_production(x,coding_acc_schedule,Schedule_Name,Department=None,**kwargs):
    """
    Basically produces a table showing the monthly revenue or cost of sales by Project
    But you can pick to use revenue or cost of sales or anything else as that is an argument in the function called Schedule_Name e.g. Revenue
    """
    x = x.merge (coding_acc_schedule, on=['Acc_Number','Name','Sorting'],how='outer')
    x = x[x['Name']==Schedule_Name]
    if Department !=None:
        x = x[x['Department']==Department]
    return x.groupby(['Project_Name','Per.']).agg ( Month_Amount = ('Journal Amount','sum')).unstack()


# @st.cache
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



# @st.cache
def gp_by_project_sales_cos(data, coding_acc_schedule,Schedule_Name='Revenue',Department=None):
    df_gp = group_by_monthly_by_production(data,coding_acc_schedule,Schedule_Name,Department, Month_Amount = 'NL_Month')
    df_gp = pd.DataFrame (df_gp.to_records()).set_index('Project_Name')
    df_gp.columns = [x.replace("('Month_Amount', ", "").replace(")", "") for x in df_gp.columns] 
    return df_gp

# @st.cache
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

@st.cache
def long_format_nl(df_gp):
    df_gp = df_gp.reset_index().melt(id_vars=['Project_Name'], value_name='Journal_Amount', var_name='Per.')
    df_gp['Per.'] = pd.to_numeric(df_gp['Per.'])
    return df_gp

@st.cache
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

def credit_notes_resolve(x):

    credit_notes=x['Jrn. No.'].str.contains('CN|CR')
    filter_credit_notes=x[credit_notes]
    filter_non_credit_notes=x[~credit_notes]
    non_UK_contractor_921=pd.concat([filter_credit_notes,filter_non_credit_notes])
    non_UK_contractor_921['Payroll_Amt'] = non_UK_contractor_921.groupby (['Jrn. No.'])['Journal Amount'].transform('sum')
    non_UK_contractor_921['Headcount'] = non_UK_contractor_921['Journal Amount'] / non_UK_contractor_921['Payroll_Amt']
    return non_UK_contractor_921

def UK_clean_921(x):
    x['Payroll_Amt'] = x.groupby (['Jrn. No.','Description'])['Journal Amount'].transform('sum')
    x['Headcount'] = x['Journal Amount'] / x['Payroll_Amt']
    return x

def company_ee_project(x):
    # x['Employee']=x['Employee'].replace('" "','',regex=True).astype(float)
    # x['Employee']=x['Employee'].str.replace(" ","")
    x['Employee - Ext. Code'] = pd.to_numeric(x['Employee - Ext. Code'])
    x= x.query('`Employee - Ext. Code`>0.5')
    x['Payroll_Amt'] = x.groupby (['calendar_year','calendar_month','Employee - Ext. Code'])['Journal Amount'].transform('sum')
    x['Headcount'] = x['Journal Amount'] / x['Payroll_Amt']
    x=x.replace([np.inf, -np.inf], np.nan) # due to 0 dividing by the journal amount
    return x


def combined_921_headcount(ee,UK,Mauve):
    employee_921=company_ee_project(ee).drop(['Employee - Ext. Code'], axis=1).reset_index()
    UK_921=UK_clean_921(UK).drop(['Description'], axis=1).reset_index()
    Mauve_2021=credit_notes_resolve(Mauve).reset_index()
    combined = pd.concat([employee_921, UK_921, Mauve_2021]).drop(['index'],axis=1)
    combined['Headcount']=pd.to_numeric(combined['Headcount'])
    # combined=combined.groupby(['Yr.','Per.','Project'])['Headcount'].head(2).sum()
    # combined=combined.reset_index()
    combined=combined.groupby(['calendar_year','calendar_month','Project'])['Headcount'].sum().reset_index()
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

def final_headcount(data):
    sch_921=data.query('`Account Code`=="921-0500"').loc[:,
    ['Description','Journal Amount','Src. Account','Jrn. No.','calendar_year','calendar_month','Project']]
    # st.write ('nl', sch_921.head()) #https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.query.html
    group_supplier=sch_921.groupby(['Src. Account','Jrn. No.','calendar_year','calendar_month','Project'])['Journal Amount'].sum().reset_index()
    group_UK = sch_921.query('`Src. Account`=="BUK02"')
    group_no_UK = group_supplier.query('`Src. Account`!="BUK02"')
    sch_921_ee=data.query('`Account Code`=="921-0500"').loc[:,
    ['Journal Amount','Src. Account','Jrn. No.','calendar_year','calendar_month','Project','Employee - Ext. Code']]
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

def load_data(x,coding_acc_schedule):
    NL = load_ledger_data(x)
    stop_mutating_df = NL_Raw_Clean_File(NL, coding_acc_schedule)
    return month_period_clean(stop_mutating_df)

def load_16_19_clean(x,coding_acc_schedule):
    NL = load_ledger_data(x)
    NL_update = NL_Raw_Clean_File(NL, coding_acc_schedule)
    NL_update=NL_update.join(NL_update['Employee'].str.split(' ', expand=True).rename(columns={0:'EE',1:'Name_EE'}))
    NL_update['Employee - Ext. Code']=NL_update['EE']
    return month_period_clean(NL_update)

def forecast_resourcing_function(x,forecast_project_mapping,start_forecast_period_resourcing_tool):
    # x=load_ledger_data(forecast_resourcing_file).copy()
    # forecast_project_mapping=pd.
    x=pd.merge(x,forecast_project_mapping,on='Project',how='outer').drop('Project',axis=1).rename(columns={'Project_name':'Project'})
    x.columns= x.columns.astype(str)
    sliced_x=x.loc[:,start_forecast_period_resourcing_tool:]
    sliced_x=sliced_x.set_index('Project').unstack(level='Project').reset_index().rename(columns={'level_0':'date',0:'headcount'})
    sliced_x=sliced_x.groupby(['Project','date'])['headcount'].sum().reset_index()    
    x = pd.pivot_table(sliced_x, values='headcount',index=['Project'], columns=['date'],fill_value=0)
    return x

@st.cache
def df_concat(NL_Data_16_19,NL_Data_20,NL_Data_21):
    return pd.concat([NL_Data_16_19,NL_Data_20,NL_Data_21],ignore_index=True)

def headcount_actual_plus_forecast(actual_headcount_direct,forecast_headcount_direct):
    actual=actual_headcount_direct.drop('All',axis=1).drop(['All'])
    merged=pd.concat([actual,forecast_headcount_direct],axis=1)
    merged.loc['All']= merged.sum(numeric_only=True, axis=0)
    merged.loc[:,'All'] = merged.sum(numeric_only=True, axis=1)
    return merged.sort_values(by='All',ascending=False)