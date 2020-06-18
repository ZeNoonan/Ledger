import pandas as pd
import numpy as np
import streamlit as st

@st.cache
def Budget_1(url_address, sheetname):
    Budget_2020=prep_data(url_address,sheetname)
    Budget_2020['Acc_Schedule']=Budget_2020['ACCOUNT'].str[-8:-5]
    Budget_2020['Acc_Schedule']=pd.to_numeric(Budget_2020['Acc_Schedule'])
    Budget_2020['Acc_Number']=Budget_2020['ACCOUNT'].str[-8:]
    Budget_2020['Department'] = Budget_2020['ACCOUNT'].str[-14:-9]
    Budget_2020.loc[:,'BUDGET 1':'BUDGET 12'] = Budget_2020.loc[:,'BUDGET 1':'BUDGET 12'] *-1
    Budget_2020 = Budget_2020.melt(id_vars=['ACCOUNT', 'SUBANALYSIS 0','Acc_Schedule','Acc_Number','Department'],value_name='Journal Amount',var_name='Per.')
    Budget_2020['Per.'] = Budget_2020['Per.'].str[7:]
    Budget_2020['Per.'] = pd.to_numeric(Budget_2020['Per.'])
    return Budget_2020

@st.cache
def NL_2020(raw5):
    NL_2020=pd.read_excel(raw5,sheet_name='Sheet1')
    NL_2020['Acc_Schedule']=NL_2020['Account Code'].str[:3]
    NL_2020['Acc_Schedule']=pd.to_numeric(NL_2020['Acc_Schedule'])
    NL_2020['Project_Code'] = NL_2020['Project'].str[:8]
    NL_2020['Project_Name'] = NL_2020['Project'].str[8:]
    NL_2020['Acc_Number'] = NL_2020['Account Code']
    NL_2020['Journal Amount'] = NL_2020['Journal Amount'] * -1
    # NL_2020.assign(Project_Code=NL_2020['Project'].str[:8]) # Why doesn't this work, it worked before!
    return NL_2020

def date_selection(df, ytd_month_number, coding_acc_schedule):
    # def date_selection(df, ytd_month_number, department=None):
    date_dict= {"Sep_YTD":1,"Oct_YTD":2,"Nov_YTD":3,"Dec_YTD":4,"Jan_YTD":5,"Feb_YTD":6,"Mar_YTD":7,
    "Apr_YTD":8,"May_YTD":9,"Jun_YTD":10,"Jul_YTD":11,"Aug_YTD":12}
    df = df [ (df['Per.'] <= date_dict[ytd_month_number]) ] 
    filter = df['Per.']==date_dict[ytd_month_number]
    df ['Month_Amount'] = df.loc[:,'Journal Amount'].where(filter)
    df = df.merge (coding_acc_schedule, on='Acc_Number',how='outer')
    # st.write( df.loc[df['Name'].isnull()] ) # Always test after merge my issue was with the DONT DELETE THIS COMMENT!
    # spreadsheet didn't have full coding https://stackoverflow.com/questions/53645882/pandas-merging-101
    return df

def new_group(x,**kwargs): # 16 jUNE Replace Name with a function argument so that i can reuse this function not going to work
    x = x.groupby(['Name']).agg ( YTD_Amount = ( 'Journal Amount','sum' ), Month_Amount = ('Month_Amount','sum'),
    Sorting = ('Sorting','first') ).sort_values(by=['Sorting'], ascending = [True])
    all_sum = x.sum()
    x = x.reset_index()
    x=x.rename(columns=kwargs)
    return x

def compare(x,y):
    c = pd.merge (x,y, on=['Name','Sorting'], how='outer')
    c = c.set_index('Name')
    c['Budget_YTD'].fillna(0, inplace=True)
    # st.write( c.loc[c['Name'].isnull()] )
    # st.write( c.loc[c['Acc_Schedule'].isnull()] )
    return c

# GOTTA USE MERGE I THINK FOR A CLEAN MERGING
def compare_alternative(a,b,c,d,e):
    x = pd.merge (a,b, on=['Name','Sorting'], how='outer')
    y = pd.merge (x,c, on=['Name','Sorting'], how='outer')
    z = pd.merge (y,d, on=['Name','Sorting'], how='outer')
    xx = pd.merge (z,e, on=['Name','Sorting'], how='outer')
    f = xx.set_index('Name')
    f.fillna(0, inplace=True)
    # st.write( c.loc[c['Name'].isnull()] )
    # st.write( c.loc[c['Acc_Schedule'].isnull()] )
    return f

def subtotal(x, coding_sort):
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

def format_dataframe(df):
    # df= df.applymap(color_negative_red)
    df= df.applymap('{:,.0f}'.format)
    df.loc['Gross Profit %']= df.loc['Gross Profit %'].str.replace('€','').str.replace(',','').astype(float).apply('{:,.0f}%'.format)
    df.loc['Net Profit %']= df.loc['Net Profit %'].str.replace('€','').str.replace(',','').astype(float).apply('{:,.0f}%'.format)
    # df= df.applymap(color_negative_red).applymap('{:,.0f}'.format)
    # df.loc['Gross Profit %']= df.loc['Gross Profit %'].apply('{:,.0f}%'.format)
    return df

def ytd_column_forecast(df,forecast_select):
    forecast_dict= {"Forecast Q1":'F1_YTD',"Forecast Q2":'F2_YTD',"Forecast Q3":'F3_YTD'}
    forecast_var= {"Forecast Q1":'F1_YTD_Variance',"Forecast Q2":'F2_YTD_Variance',"Forecast Q3":'F3_YTD_Variance'}
    selection = forecast_dict[forecast_select]
    selection_1 = forecast_var[forecast_select]
    return df.loc[:,['NL_YTD','Budget_YTD','YTD_Variance',selection,selection_1]]

def month_column_forecast(df,forecast_select):
    forecast_dict= {"Forecast Q1":'F1_Month',"Forecast Q2":'F2_Month',"Forecast Q3":'F3_Month'}
    forecast_var= {"Forecast Q1":'F1_Month_Variance',"Forecast Q2":'F2_Month_Variance',"Forecast Q3":'F3_Month_Variance'}
    selection = forecast_dict[forecast_select]
    selection_1 = forecast_var[forecast_select]
    return df.loc[:,['NL_Month','Budget_Month','Month_Variance',selection,selection_1]]

def new_group_dept(x,department,**kwargs): # NOW CHANGE THE COLUMN NAMES BY USING A FUNCTION?
    date_dict= {"TV":'T0000',"CG":'CG000',"Post":'P0000',"Admin":'A0000',"Development":'D0000',"IT":'I0000',"Pipeline":'R0000'}
    x = x [ (x.loc[:,'Department'] == date_dict[department]) ]
    x = x.groupby(['Name']).agg ( YTD_Amount = ( 'Journal Amount','sum' ), Month_Amount = ('Month_Amount','sum'),
    Sorting = ('Sorting','first') ).sort_values(by=['Sorting'], ascending = [True])
    all_sum = x.sum()
    x = x.reset_index()
    x=x.rename(columns=kwargs)
    return x

def end_of_year_forecast(forecast,nl_ytd_selection, raw5, coding_acc_schedule, coding_sort):
    NL = date_selection(NL_2020(raw5), nl_ytd_selection, coding_acc_schedule)
    ytd_selection='Aug_YTD'
    Budget = date_selection(Budget_1('C:/Users/Darragh/Documents/Python/Work/Data/Budget_2020.xlsx','Budget'), ytd_selection, coding_acc_schedule)
    F1 = date_selection(Budget_1('C:/Users/Darragh/Documents/Python/Work/Data/Budget_2020.xlsx','F1'), ytd_selection, coding_acc_schedule)
    F2 = date_selection(Budget_1('C:/Users/Darragh/Documents/Python/Work/Data/Budget_2020.xlsx','F2'), ytd_selection, coding_acc_schedule)
    F3 = date_selection(Budget_1('C:/Users/Darragh/Documents/Python/Work/Data/Budget_2020.xlsx','F3'), ytd_selection, coding_acc_schedule)
    Forecast_rest_year = date_selection_year (Budget_1('C:/Users/Darragh/Documents/Python/Work/Data/Budget_2020.xlsx',forecast), nl_ytd_selection, coding_acc_schedule)
    # I had trouble passing above variable from st.checkbox from function to function, you'll see if you try and shorten it up....
    Actual_plus_Forecast = pd.concat([NL,Forecast_rest_year], axis=0)
    Actual_plus_Forecast = new_group( Actual_plus_Forecast, YTD_Amount = 'NL_YTD', Month_Amount = 'NL_Month' )
    Budget_PL = new_group( Budget, YTD_Amount = 'Budget_YTD', Month_Amount = 'Budget_Month' )
    F1_PL = new_group( F1, YTD_Amount = 'F1_YTD', Month_Amount = 'F1_Month' )
    F2_PL = new_group( F2, YTD_Amount = 'F2_YTD', Month_Amount = 'F2_Month' )
    F3_PL = new_group( F3, YTD_Amount = 'F3_YTD', Month_Amount = 'F3_Month' )
    NL_PL = new_group( NL, YTD_Amount = 'NL_YTD', Month_Amount = 'NL_Month' )
    compare_df = compare (NL_PL, Budget_PL)
    subtotal2 = subtotal(test_compare(Actual_plus_Forecast, Budget_PL, F1_PL, F2_PL, F3_PL), coding_sort)
    subtotal2 = subtotal2.rename(columns = {'NL_YTD' : 'Projection', 'Budget_YTD': 'Budget', 'F1_YTD':'F1', 'F2_YTD':'F2','F3_YTD':'F3','YTD_Variance':'Var v. Budget'})
    return subtotal2

def end_of_year_forecast_dept(forecast,nl_ytd_selection, dep_selection, raw5, coding_acc_schedule, coding_sort):
    NL = date_selection(NL_2020(raw5), nl_ytd_selection, coding_acc_schedule)
    ytd_selection='Aug_YTD'
    Budget = date_selection(Budget_1('C:/Users/Darragh/Documents/Python/Work/Data/Budget_2020.xlsx','Budget'), ytd_selection, coding_acc_schedule)
    F1 = date_selection(Budget_1('C:/Users/Darragh/Documents/Python/Work/Data/Budget_2020.xlsx','F1'), ytd_selection, coding_acc_schedule)
    F2 = date_selection(Budget_1('C:/Users/Darragh/Documents/Python/Work/Data/Budget_2020.xlsx','F2'), ytd_selection, coding_acc_schedule)
    F3 = date_selection(Budget_1('C:/Users/Darragh/Documents/Python/Work/Data/Budget_2020.xlsx','F3'), ytd_selection, coding_acc_schedule)
    Forecast_rest_year = date_selection_year (Budget_1('C:/Users/Darragh/Documents/Python/Work/Data/Budget_2020.xlsx',forecast), nl_ytd_selection, coding_acc_schedule)
    # I had trouble passing above variable from st.checkbox from function to function, you'll see if you try and shorten it up....
    Actual_plus_Forecast = pd.concat([NL,Forecast_rest_year], axis=0)
    Actual_plus_Forecast = new_group_dept(x=Actual_plus_Forecast, department=dep_selection, YTD_Amount = 'NL_YTD', Month_Amount = 'NL_Month' )
    Budget_PL = new_group_dept(x= Budget, department=dep_selection, YTD_Amount = 'Budget_YTD', Month_Amount = 'Budget_Month' )
    F1_PL = new_group_dept(x= F1,department=dep_selection, YTD_Amount = 'F1_YTD', Month_Amount = 'F1_Month' )
    F2_PL = new_group_dept(x= F2,department=dep_selection, YTD_Amount = 'F2_YTD', Month_Amount = 'F2_Month' )
    F3_PL = new_group_dept(x= F3,department=dep_selection, YTD_Amount = 'F3_YTD', Month_Amount = 'F3_Month' )
    NL_PL = new_group_dept(x= NL,department=dep_selection, YTD_Amount = 'NL_YTD', Month_Amount = 'NL_Month' )
    subtotal2 = subtotal(test_compare(Actual_plus_Forecast, Budget_PL, F1_PL, F2_PL, F3_PL), coding_sort)
    subtotal2 = subtotal2.rename(columns = {'NL_YTD' : 'Projection', 'Budget_YTD': 'Budget', 'F1_YTD':'F1', 'F2_YTD':'F2','F3_YTD':'F3','YTD_Variance':'Var v. Budget'})
    return subtotal2




def date_selection_year(df, ytd_month_number, coding_acc_schedule):
    # def date_selection(df, ytd_month_number, department=None):
    date_dict= {"Sep_YTD":1,"Oct_YTD":2,"Nov_YTD":3,"Dec_YTD":4,"Jan_YTD":5,"Feb_YTD":6,"Mar_YTD":7,
    "Apr_YTD":8,"May_YTD":9,"Jun_YTD":10,"Jul_YTD":11,"Aug_YTD":12}
    df = df [ (df['Per.'] > date_dict[ytd_month_number]) ] 
    filter = df['Per.']==date_dict[ytd_month_number]
    df ['Month_Amount'] = df.loc[:,'Journal Amount'].where(filter)
    df = df.merge (coding_acc_schedule, on='Acc_Number',how='outer')
    # st.write( df.loc[df['Name'].isnull()] ) # Always test after merge my issue was with the DONT DELETE THIS COMMENT!
    # spreadsheet didn't have full coding https://stackoverflow.com/questions/53645882/pandas-merging-101
    return df





def new_group_project(x,coding_acc_schedule,Schedule_Name,**kwargs): # 16 jUNE Replace Name with a function argument so that i can reuse this function not going to work
    x = x.merge (coding_acc_schedule, on='Acc_Number',how='outer')
    x = x[x['Name']==Schedule_Name]
    st.write (x.head())
    return x.groupby(['Project_Name','Per.']).agg ( Month_Amount = ('Journal Amount','sum')).unstack()
    # return pd.pivot_table(x, index=["Project_Name"], columns=["Per."], values=["Month_Amount"], aggfunc=np.sum)
    # all_sum = x.sum()
    # x = x.reset_index()
    # x=x.rename(columns=kwargs)
    # return x








def test_compare(*args):
    df = pd.merge(args[0],args[1], on=['Name','Sorting'], how='outer')
    for d in args[2:]:
        df = pd.merge(df,d, on=['Name','Sorting'], how='outer')
    f = df.set_index('Name')
    f.fillna(0, inplace=True)
    # st.write( c.loc[c['Name'].isnull()] )
    # st.write( c.loc[c['Acc_Schedule'].isnull()] )
    return f









    





# @st.cache
def prep_data(url,sheet):
    return pd.read_excel(url,sheet_name=sheet)

def EE_numbers():
    return prep_data(raw2,'Sheet1')

def Project_codes():
    return prep_data(raw3,'Sheet1')



# subtotal2 = subtotal2.style.format("{:.0}")
# subtotal2.loc['Gross Profit %'] = subtotal2.loc['Gross Profit %'].apply("{:.0%}".format)
# https://discuss.streamlit.io/t/cant-adjust-dataframes-decimal-places/1949
# https://discuss.streamlit.io/t/styling-a-row-in-a-dataframe/2245
# https://github.com/streamlit/streamlit/issues/1125
# https://github.com/streamlit/streamlit/blob/develop/e2e/scripts/st_dataframe.py
# https://github.com/streamlit/streamlit/blob/develop/e2e/scripts/st_table_styling.py
# https://stackoverflow.com/questions/50100635/highlight-color-a-panda-data-frame-row-by-index
# https://stackoverflow.com/questions/57574409/applying-style-to-a-pandas-dataframe-row-wise

# https://stackoverflow.com/questions/10567644/if-else-based-on-existence-of-python-function-optional-arguments
# https://stackoverflow.com/questions/52494128/call-function-without-optional-arguments-if-they-are-none
# https://stackoverflow.com/questions/9539921/how-do-i-create-a-python-function-with-optional-arguments
