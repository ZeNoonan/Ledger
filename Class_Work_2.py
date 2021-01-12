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

# @st.cache
def end_of_year_forecast(ytd_selection, NL, coding_acc_schedule,projection_selection,Budget_Data,F1_Data,F2_Data,F3_Data,coding_sort,Budget_PL,F1_PL,F2_PL,F3_PL):
    # NL = date_selection_for_PL(NL_2020(raw5), nl_ytd_selection, coding_acc_schedule)
    ytd_selection='Aug_YTD'
    # Budget = date_selection(Budget_1('C:/Users/Darragh/Documents/Python/Work/Data/Budget_2020.xlsx','Budget'), ytd_selection, coding_acc_schedule)
    # F1 = date_selection(Budget_1('C:/Users/Darragh/Documents/Python/Work/Data/Budget_2020.xlsx','F1'), ytd_selection, coding_acc_schedule)
    # F2 = date_selection(Budget_1('C:/Users/Darragh/Documents/Python/Work/Data/Budget_2020.xlsx','F2'), ytd_selection, coding_acc_schedule)
    # F3 = date_selection(Budget_1('C:/Users/Darragh/Documents/Python/Work/Data/Budget_2020.xlsx','F3'), ytd_selection, coding_acc_schedule)
    Forecast_rest_year = date_selection_year (projection_selection, ytd_selection, coding_acc_schedule,Budget_Data, F1_Data, F2_Data,F3_Data)
    # I had trouble passing above variable from st.checkbox from function to function, you'll see if you try and shorten it up....
    Actual_plus_Forecast = pd.concat([NL,Forecast_rest_year], axis=0)
    # return Actual_plus_Forecast
    # st.write (Actual_plus_Forecast)
    Actual_plus_Forecast = PL_generation( Actual_plus_Forecast,'Name', YTD_Amount = 'NL_YTD', Month_Amount = 'NL_Month' )
    # return Actual_plus_Forecast

    # Budget_PL = new_group( Budget, YTD_Amount = 'Budget_YTD', Month_Amount = 'Budget_Month' )
    # F1_PL = new_group( F1, YTD_Amount = 'F1_YTD', Month_Amount = 'F1_Month' )
    # F2_PL = new_group( F2, YTD_Amount = 'F2_YTD', Month_Amount = 'F2_Month' )
    # F3_PL = new_group( F3, YTD_Amount = 'F3_YTD', Month_Amount = 'F3_Month' )
    # NL_PL = new_group( NL, YTD_Amount = 'NL_YTD', Month_Amount = 'NL_Month' )
    # compare_df = compare (NL_PL, Budget_PL)
    subtotal2 = (dfs_merge(Actual_plus_Forecast, Budget_PL, F1_PL, F2_PL, F3_PL), coding_sort)
    return subtotal2
    # subtotal2 = clean_format_PL_presentation(subtotal2)
    # subtotal2 = subtotal2.rename(columns = {'NL_YTD' : 'Projection', 'Budget_YTD': 'Budget', 'F1_YTD':'F1', 'F2_YTD':'F2','F3_YTD':'F3','YTD_Variance':'Var v. Budget'})
    # return subtotal2

# @st.cache
def date_selection_year(projection_selection, ytd_month_number, coding_acc_schedule,Budget_Data, F1_Data, F2_Data,F3_Data):
    # def date_selection(df, ytd_month_number, department=None):
    df_dict ={"Budget":Budget_Data, "F1":F1_Data, "F2":F2_Data}
    df = df_dict[projection_selection]
    date_dict= {"Sep_YTD":1,"Oct_YTD":2,"Nov_YTD":3,"Dec_YTD":4,"Jan_YTD":5,"Feb_YTD":6,"Mar_YTD":7,
    "Apr_YTD":8,"May_YTD":9,"Jun_YTD":10,"Jul_YTD":11,"Aug_YTD":12}
    df = df [ (df['Per.'] > date_dict[ytd_month_number]) ] 
    filter = df['Per.']==date_dict[ytd_month_number]
    df ['Month_Amount'] = df.loc[:,'Journal Amount'].where(filter)
    df = df.merge (coding_acc_schedule, on='Acc_Number',how='outer')
    # st.write( df.loc[df['Name'].isnull()] ) # Always test after merge my issue was with the DONT DELETE THIS COMMENT!
    # spreadsheet didn't have full coding https://stackoverflow.com/questions/53645882/pandas-merging-101
    return df

def dfs_merge(*args):
    df = pd.merge(args[0],args[1], on=['Name','Sorting'], how='outer')
    for d in args[2:]:
        df = pd.merge(df,d, on=['Name','Sorting'], how='outer')
    f = df.set_index('Name')
    f.fillna(0, inplace=True)
    # st.write( c.loc[c['Name'].isnull()] )
    # st.write( c.loc[c['Acc_Schedule'].isnull()] )
    return f