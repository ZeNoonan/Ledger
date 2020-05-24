import pandas as pd
import numpy as np
import streamlit as st

st.write ('  ')
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

def main():
    EE = EE_numbers()
    Project = Project_codes()
    Budget_Data = Budget_1('C:/Users/Darragh/Documents/Python/Work/Data/Budget_2020.xlsx','Budget')
    F1_Data = Budget_1('C:/Users/Darragh/Documents/Python/Work/Data/Budget_2020.xlsx','F1')
    F2_Data = Budget_1('C:/Users/Darragh/Documents/Python/Work/Data/Budget_2020.xlsx','F2')
    F3_Data = Budget_1('C:/Users/Darragh/Documents/Python/Work/Data/Budget_2020.xlsx','F3')
    ytd_selection = st.sidebar.selectbox("For what period would you like to run - from September up to?",options = ["Sep_YTD", "Oct_YTD",
     "Nov_YTD","Dec_YTD","Jan_YTD","Feb_YTD","Mar_YTD","Apr_YTD","May_YTD","Jun_YTD","Jul_YTD","Aug_YTD"], index=5) 
     # index=5 sets default to period 6 fix up with a variable for this
    NL = date_selection(NL_2020(), ytd_selection)
    Budget = date_selection(Budget_Data, ytd_selection)
    F1 = date_selection(F1_Data, ytd_selection)
    F2 = date_selection(F2_Data, ytd_selection)
    F3 = date_selection(F3_Data, ytd_selection)

    # https://github.com/streamlit/streamlit/issues/729   This is for converting period 6 into say YTD_Feb uses a dictionary
    Budget_PL = new_group( Budget, YTD_Amount = 'Budget_YTD', Month_Amount = 'Budget_Month' )
    F1_PL = new_group( F1, YTD_Amount = 'F1_YTD', Month_Amount = 'F1_Month' )
    F2_PL = new_group( F2, YTD_Amount = 'F2_YTD', Month_Amount = 'F2_Month' )
    F3_PL = new_group( F3, YTD_Amount = 'F3_YTD', Month_Amount = 'F3_Month' )
    NL_PL = new_group( NL, YTD_Amount = 'NL_YTD', Month_Amount = 'NL_Month' )

    compare_df = compare (NL_PL, Budget_PL)

    subtotal2 = subtotal(compare_alternative(NL_PL, Budget_PL, F1_PL, F2_PL, F3_PL))

    st.write ('This is the YTD PL')
    first_slot=st.empty()
    first_slot.dataframe (subtotal2.loc[:,['NL_YTD','Budget_YTD','YTD_Variance']]) #st.write doesn't work with st.empty()

    if st.checkbox('Would you like to see the Forecast included in YTD above?'):
        forecast_selection = st.selectbox("Which Forecast do you want to see?",options = ["Forecast Q1", "Forecast Q2","Forecast Q3"],index=1) # use index to default
        first_slot.dataframe (ytd_column_forecast(subtotal2,forecast_selection))
    
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
        subtotal_dept = subtotal(compare_alternative(NL_PL_Dept, Budget_PL_Dept, F1_PL_Dept, F2_PL_Dept, F3_PL_Dept))

        third_slot=st.empty()
        third_slot.dataframe (subtotal_dept.loc[:,['NL_YTD','Budget_YTD','YTD_Variance']])
        if st.checkbox('Would you like to see the Forecast included in Department results above?'):
            forecast_selection = st.selectbox("Which Forecast do you want to include?",options = ["Forecast Q1", "Forecast Q2","Forecast Q3"],index=1) # use index to default
            third_slot.dataframe (ytd_column_forecast(subtotal_dept,forecast_selection))

        if st.checkbox('Check box to see results for Departmental Month'):
            st.write ('This is the Month PL')
            fourth_slot = st.empty()
            fourth_slot.dataframe (subtotal_dept.loc[:,['NL_Month','Budget_Month','Month_Variance']])
            if st.checkbox('Would you like to see the Forecast included in Departmental Month Results?'):
                forecast1_selection = st.selectbox("Which Forecast do you want to see included above?",options = ["Forecast Q1", "Forecast Q2","Forecast Q3"],index=1) # use index to default
                fourth_slot.dataframe (month_column_forecast(subtotal_dept,forecast1_selection))


    if st.checkbox('Click for End of Year Comparison'):
        projection_selection = st.selectbox("Which Budget/Forecast to use for rest of year?",options = ["Budget", "F1","F2","F3"],index=1)
        projection = end_of_year_forecast(projection_selection,ytd_selection)  # if i change this to projection selection it doesnt work due to string something
        st.write (projection.loc[:,['Projection','Budget','Var v. Budget', 'F1','F2','F3']])

    

# Function which summarises first half so that I can reuse it for the end of year section....
def end_of_year_forecast(forecast,nl_ytd_selection):
    NL = date_selection(NL_2020(), nl_ytd_selection)
    ytd_selection='Aug_YTD'
    Budget = date_selection(Budget_1('C:/Users/Darragh/Documents/Python/Work/Data/Budget_2020.xlsx','Budget'), ytd_selection)
    F1 = date_selection(Budget_1('C:/Users/Darragh/Documents/Python/Work/Data/Budget_2020.xlsx','F1'), ytd_selection)
    F2 = date_selection(Budget_1('C:/Users/Darragh/Documents/Python/Work/Data/Budget_2020.xlsx','F2'), ytd_selection)
    F3 = date_selection(Budget_1('C:/Users/Darragh/Documents/Python/Work/Data/Budget_2020.xlsx','F3'), ytd_selection)
    # selection_dict = {'Budget': 'Budget_Data', 'F1':'F1_Data','F2':'F2_Data', 'F3':'F3_Data'}
    # forecast_sel = selection_dict[forecast]
    # HOW DO I GET THE BELOW TO CONVERT TO THE STREAMLIT 
    Forecast_rest_year = date_selection_year (Budget_1('C:/Users/Darragh/Documents/Python/Work/Data/Budget_2020.xlsx',forecast), nl_ytd_selection) 
    Actual_plus_Forecast = pd.concat([NL,Forecast_rest_year], axis=0)
    Actual_plus_Forecast = new_group( Actual_plus_Forecast, YTD_Amount = 'NL_YTD', Month_Amount = 'NL_Month' )
    Budget_PL = new_group( Budget, YTD_Amount = 'Budget_YTD', Month_Amount = 'Budget_Month' )
    F1_PL = new_group( F1, YTD_Amount = 'F1_YTD', Month_Amount = 'F1_Month' )
    F2_PL = new_group( F2, YTD_Amount = 'F2_YTD', Month_Amount = 'F2_Month' )
    F3_PL = new_group( F3, YTD_Amount = 'F3_YTD', Month_Amount = 'F3_Month' )
    NL_PL = new_group( NL, YTD_Amount = 'NL_YTD', Month_Amount = 'NL_Month' )
    compare_df = compare (NL_PL, Budget_PL)
    subtotal2 = subtotal(test_compare(Actual_plus_Forecast, Budget_PL, F1_PL, F2_PL, F3_PL))
    subtotal2 = subtotal2.rename(columns = {'NL_YTD' : 'Projection', 'Budget_YTD': 'Budget', 'F1_YTD':'F1', 'F2_YTD':'F2','F3_YTD':'F3','YTD_Variance':'Var v. Budget'})
    return subtotal2


def date_selection_year(df, ytd_month_number):
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

def date_selection(df, ytd_month_number):
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

def test_compare(*args):
    df = pd.merge(args[0],args[1], on=['Name','Sorting'], how='outer')
    for d in args[2:]:
        df = pd.merge(df,d, on=['Name','Sorting'], how='outer')
    f = df.set_index('Name')
    f.fillna(0, inplace=True)
    # st.write( c.loc[c['Name'].isnull()] )
    # st.write( c.loc[c['Acc_Schedule'].isnull()] )
    return f

@st.cache
def NL_2020():
    NL_2020=prep_data(raw5, 'Sheet1')
    NL_2020['Acc_Schedule']=NL_2020['Account Code'].str[:3]
    NL_2020['Acc_Schedule']=pd.to_numeric(NL_2020['Acc_Schedule'])
    NL_2020['Project_Code'] = NL_2020['Project'].str[:8]
    NL_2020['Project_Name'] = NL_2020['Project'].str[8:]
    NL_2020['Acc_Number'] = NL_2020['Account Code']
    NL_2020['Journal Amount'] = NL_2020['Journal Amount'] * -1
    # NL_2020.assign(Project_Code=NL_2020['Project'].str[:8]) # Why doesn't this work, it worked before!
    return NL_2020

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

# https://stackoverflow.com/questions/10567644/if-else-based-on-existence-of-python-function-optional-arguments
# https://stackoverflow.com/questions/52494128/call-function-without-optional-arguments-if-they-are-none
# https://stackoverflow.com/questions/9539921/how-do-i-create-a-python-function-with-optional-arguments



def new_group_dept(x,department,**kwargs): # NOW CHANGE THE COLUMN NAMES BY USING A FUNCTION?
    date_dict= {"TV":'T0000',"CG":'CG000',"Post":'P0000',"Admin":'A0000',"Development":'D0000',"IT":'I0000',"Pipeline":'R0000'}
    x = x [ (x.loc[:,'Department'] == date_dict[department]) ]
    x = x.groupby(['Name']).agg ( YTD_Amount = ( 'Journal Amount','sum' ), Month_Amount = ('Month_Amount','sum'),
    Sorting = ('Sorting','first') ).sort_values(by=['Sorting'], ascending = [True])
    all_sum = x.sum()
    x = x.reset_index()
    x=x.rename(columns=kwargs)
    return x

def subtotal(x):
    # gross_profit = x.loc['Revenue':'Cost of Sales',:].sum()
    gross_profit = x.reindex(['Revenue','Cost of Sales']).sum()
    # sub_total_overheads = x.loc['Payroll':'Other',:].sum()
    sub_total_overheads = x.reindex(['Payroll','Recruitment & HR','Rent & Service Charges','Building Expenses','Office Expenses','Travel',
    'Computer costs','Audit, Legal & Consulting','Committees','Insurance','Bank Charges','FX','Other','Other']).sum()
    x.loc['Gross Profit'] = gross_profit
    x.loc['Gross Profit %'] = gross_profit / x.loc['Revenue']
    x.loc['Sub-Total Overheads'] = sub_total_overheads

    # CHECK FROM HERE    
    def check(x,account):
        if account in x.index:
            return x.loc[account]
        else:
            return 0 #also tryed N
    # st.write ('this is a check of check function checking depreciation', check(x,'Depreciation'))
    # x.loc['EBITDA'] = gross_profit + sub_total_overheads + x.loc['IP Capitalisation']
    x.loc['EBITDA'] = gross_profit + sub_total_overheads + check(x,'IP Capitalisation')
    # x.loc['Net Profit before Tax'] = x.loc['EBITDA'] + x.loc['Depreciation'] + x.loc['Finance Lease Interest']
    x.loc['Net Profit before Tax'] = x.loc['EBITDA'] + check(x,'Depreciation') + check(x,'Finance Lease Interest')
    # CHECK UP ABOVE

    x.loc['Net Profit %'] = x.loc['Net Profit before Tax'] / x.loc['Revenue']
    
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
    
    # EBITDA = gross_profit + sub_total_overheads + x.loc['IP Capitalisation']

def compare(x,y):
    c = pd.merge (x,y, on=['Name','Sorting'], how='outer')
    c = c.set_index('Name')
    c['Budget_YTD'].fillna(0, inplace=True)
    # st.write( c.loc[c['Name'].isnull()] )
    # st.write( c.loc[c['Acc_Schedule'].isnull()] )
    return c

# def compare_alternative(x,y):
#     # x = args.set_index('Name')
#     x = x.set_index('Name')
#     y = y.set_index('Name')
#     x=pd.concat([x,y],axis=0, sort=True)
#     return x



def new_group(x,**kwargs): # NOW CHANGE THE COLUMN NAMES BY USING A FUNCTION?
    x = x.groupby(['Name']).agg ( YTD_Amount = ( 'Journal Amount','sum' ), Month_Amount = ('Month_Amount','sum'),
    Sorting = ('Sorting','first') ).sort_values(by=['Sorting'], ascending = [True])
    all_sum = x.sum()
    x = x.reset_index()
    x=x.rename(columns=kwargs)
    return x

# @st.cache
def prep_data(url,sheet):
    data = pd.read_excel(url,sheet_name=sheet)
    return data

def EE_numbers():
    EE_numbers=prep_data(raw2,'Sheet1')
    return EE_numbers

def Project_codes():
    Project_codes=prep_data(raw3,'Sheet1')
    return Project_codes




main()
