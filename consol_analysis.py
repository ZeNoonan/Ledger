import pandas as pd
import numpy as np
import streamlit as st
import datetime
import altair as alt
import base64
from io import BytesIO


st.set_page_config(layout="wide")

    # sheet_1=pd.read_csv('C:/Users/Darragh/Documents/Python/Work/Data/may_2021.csv',header=[0,1])
    # sheet_2=pd.read_csv('C:/Users/Darragh/Documents/Python/Work/Data/feb_2021.csv',header=[0,1])
    # sheet_3=pd.read_csv('C:/Users/Darragh/Documents/Python/Work/Data/nov_2020.csv',header=[0,1])
    # sheet_4=pd.read_csv('C:/Users/Darragh/Documents/Python/Work/Data/aug_2020.csv',header=[0,1])
    # sheet_5=pd.read_csv('C:/Users/Darragh/Documents/Python/Work/Data/may_2020.csv',header=[0,1])
    # sheet_6=pd.read_csv('C:/Users/Darragh/Documents/Python/Work/Data/feb_2020.csv',header=[0,1])
    # sheet_7=pd.read_csv('C:/Users/Darragh/Documents/Python/Work/Data/nov_2019.csv',header=[0,1])
    # sheet_8=pd.read_csv('C:/Users/Darragh/Documents/Python/Work/Data/aug_2019.csv',header=[0,1])
    # sheet_9=pd.read_csv('C:/Users/Darragh/Documents/Python/Work/Data/may_2019.csv',header=[0,1])
    # sheet_10=pd.read_csv('C:/Users/Darragh/Documents/Python/Work/Data/feb_2019.csv',header=[0,1])
    # sheet_11=pd.read_csv('C:/Users/Darragh/Documents/Python/Work/Data/nov_2018.csv',header=[0,1])
    # sheet_12=pd.read_csv('C:/Users/Darragh/Documents/Python/Work/Data/aug_2018.csv',header=[0,1])
    # sheet_13=pd.read_csv('C:/Users/Darragh/Documents/Python/Work/Data/may_2018.csv',header=[0,1])
    # sheet_14=pd.read_csv('C:/Users/Darragh/Documents/Python/Work/Data/feb_2018.csv',header=[0,1])
    # sheet_15=pd.read_csv('C:/Users/Darragh/Documents/Python/Work/Data/nov_2017.csv',header=[0,1])
    # sheet_16=pd.read_csv('C:/Users/Darragh/Documents/Python/Work/Data/aug_2017.csv',header=[0,1])
    # sheet_17=pd.read_csv('C:/Users/Darragh/Documents/Python/Work/Data/may_2017.csv',header=[0,1])
    # sheet_18=pd.read_csv('C:/Users/Darragh/Documents/Python/Work/Data/feb_2017.csv',header=[0,1])
    # sheet_19=pd.read_csv('C:/Users/Darragh/Documents/Python/Work/Data/nov_2016.csv',header=[0,1])
    # sheet_20=pd.read_csv('C:/Users/Darragh/Documents/Python/Work/Data/aug_2016.csv',header=[0,1])
    # df=pd.concat([sheet_1,sheet_2,sheet_3,sheet_4,sheet_5,sheet_6,sheet_7,sheet_8,sheet_9,sheet_10,
    # sheet_11,sheet_12,sheet_13,sheet_14,sheet_15,sheet_16,sheet_17,sheet_18,sheet_19,sheet_20],axis=0)
    # st.write('check',df)
    # df.to_csv('C:/Users/Darragh/Documents/Python/Work/Data/quarterly_all.csv')

def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    val = to_excel(df)
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="extract.xlsx">Download csv file</a>' # decode b'abc' => abc

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    processed_data = output.getvalue()
    return processed_data

# https://stackoverflow.com/questions/18470323/selecting-columns-from-pandas-multiindex

@st.cache
def load_excel():
    return pd.concat(pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/Consol TB.xlsx',header=[0,1],sheet_name=None),ignore_index=True)

df=load_excel().copy()
df[('acc_sch','acc_sch')]=df[('Account Code','Account Code')].astype(str).str[:3].astype(int)
# st.write(df.dtypes)
df[('TB','9 Story Dist.')]=pd.to_numeric(df[('TB','9 Story Dist.')],errors='coerce')
# df[('acc_sch','acc_sch')]=pd.to_numeric(df[('acc_sch','acc_sch')],errors='coerce')



cols_to_move = [('fiscal_year', 'fiscal_year'),('calendar_year', 'calendar_year'),('quarter', 'quarter'),
('date', 'date'), ('Account Code', 'Account Code'), ('acc_sch', 'acc_sch'), ('Description', 'Description'), ('Code', 'Code'),
 ('Classification 9SMG', 'Classification 9SMG'), ('Classification Stats', 'Classification Stats'), ('Sub-Classification Stats', 'Sub-Classification Stats')]
cols = cols_to_move + [col for col in df if col not in cols_to_move]
df=df[cols]
# st.write('dataframe',df.head())
# st.write(df.dtypes)

df.loc[:,df.columns.get_level_values(0).isin({"TB", "consol_jnl"})]=df.loc[:,df.columns.get_level_values(0).isin({"TB", "consol_jnl"})]*-1
st.write(df)

filter_df=(df.loc[:,df.columns.get_level_values(0).isin({"TB", "consol_jnl"})])
filter_in_dil=(filter_df.loc[:,filter_df.columns.get_level_values(1).isin({"9 Story Dist.", "9SDIL"})])
filter_out_dil=(filter_df.loc[:,~filter_df.columns.get_level_values(1).isin({"9 Story Dist.", "9SDIL"})])
filter_out_uk=(filter_out_dil.loc[:,~filter_out_dil.columns.get_level_values(1).isin({"BBF UK","NK2","PRS","VMP 2D","Knight","NK2","UK","KPL"})])
filter_in_uk=(filter_out_dil.loc[:,filter_out_dil.columns.get_level_values(1).isin({"BBF UK","NK2","PRS","VMP 2D","Knight","NK2","UK","KPL"})])
df[('total','total')]=filter_df.sum(axis=1)
# df[('total','total')]=-df[('total','total')]
df[('total','9sdil_total')]=filter_in_dil.sum(axis=1)
df[('total','bbf_group_total')]=filter_out_dil.sum(axis=1)
df[('total','bbf_irl_group_total')]=filter_out_uk.sum(axis=1)
df[('total','bbf_uk_group_total')]=filter_in_uk.sum(axis=1)

st.write('check total equals zero',df['total'].sum(),'close enough its 11')

quarter_4=df.loc[df[('quarter','quarter')]==4]
st.write('check q4 totals',quarter_4['total'].sum(),"that works equal to 3")

# st.write('check q4',quarter_4.head())

coding_acc_schedule = (pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/account_numbers_updated.xlsx')).iloc[:,:3]
# coding_acc_schedule['Acc_Number']=coding_acc_schedule['Acc_Number'].str.replace("-",'').astype(float)

coding_acc_schedule=coding_acc_schedule.rename(columns={'Acc_Number':'Account Code'})
coding_sort=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/account_numbers_updated.xlsx', sheet_name='Sheet2')
# st.write('coding acc sch', coding_acc_schedule)
# st.write('coding sort', coding_sort)


def filter_total(df):
    df=df.droplevel(0,axis=1)
    df=df.loc[:,['fiscal_year','calendar_year','quarter','date','Account Code','acc_sch','total','9sdil_total','bbf_group_total','bbf_irl_group_total',
    'bbf_uk_group_total',
    'Description','Code','Classification 9SMG','Classification Stats','Sub-Classification Stats']]
    df = df.merge (coding_acc_schedule, on='Account Code',how='outer')

    return df

annual=filter_total(quarter_4)
x=annual.query('`acc_sch`>919')
x=x[x['Sorting'].isna()]
st.write('should be blank!! below',x)
pl_data=annual.query('`acc_sch`>919')

# st.markdown(get_table_download_link(x), unsafe_allow_html=True)

# st.write('check this',pl_data)    

def pl_generation(clean_data,category_to_filter_on,total): 
    clean_data = clean_data.groupby(category_to_filter_on).agg ( YTD_Amount = ( total,'sum' ),
    Sorting = ('Sorting','first') ).sort_values(by=['Sorting'], ascending = [True])
    clean_data = clean_data.reset_index()
    # clean_data=clean_data.rename(columns=kwargs)
    return clean_data

def pl_generation_multiple(clean_data,category_to_filter_on): 
    clean_data = clean_data.groupby(category_to_filter_on).agg ( YTD_Amount = ( 'total','sum' ), bbf_total=( 'bbf_group_total','sum' ),
    dil_total=( '9sdil_total','sum' ),bbf_uk_group_total=( 'bbf_uk_group_total','sum' ),bbf_irl_group_total=( 'bbf_irl_group_total','sum' ),
    Sorting = ('Sorting','first') ).sort_values(by=['Sorting'], ascending = [True])
    clean_data = clean_data.reset_index()
    # clean_data=clean_data.rename(columns=kwargs)
    return clean_data

check_data=pl_generation(pl_data,category_to_filter_on=['fiscal_year','Name'],total='total')
totals_data=pl_generation_multiple(pl_data,category_to_filter_on=['fiscal_year','Name'])
# st.write(check_data)
check_data_acc_code=pl_generation(pl_data,category_to_filter_on=['fiscal_year','Account Code'],total='total')

# need to filter by year
pl_2020=check_data.query('`fiscal_year`==2020').set_index('Name').drop('fiscal_year',axis=1)
pl_2019=check_data.query('`fiscal_year`==2019').set_index('Name').drop('fiscal_year',axis=1)
pl_2018=check_data.query('`fiscal_year`==2018').set_index('Name').drop('fiscal_year',axis=1)
pl_2017=check_data.query('`fiscal_year`==2017').set_index('Name').drop('fiscal_year',axis=1)
pl_2016=check_data.query('`fiscal_year`==2016').set_index('Name').drop('fiscal_year',axis=1)

pl_2020_totals=totals_data.query('`fiscal_year`==2020').set_index('Name').drop('fiscal_year',axis=1)
pl_2019_totals=totals_data.query('`fiscal_year`==2019').set_index('Name').drop('fiscal_year',axis=1)
pl_2018_totals=totals_data.query('`fiscal_year`==2018').set_index('Name').drop('fiscal_year',axis=1)
pl_2017_totals=totals_data.query('`fiscal_year`==2017').set_index('Name').drop('fiscal_year',axis=1)
pl_2016_totals=totals_data.query('`fiscal_year`==2016').set_index('Name').drop('fiscal_year',axis=1)




st.write('checking pl 2017',pl_2017)
pl_2017_acc_code=check_data_acc_code.query('`fiscal_year`==2017').set_index('Account Code').drop('fiscal_year',axis=1)
st.write('PL by account code for 2020', pl_2017_acc_code)
st.markdown(get_table_download_link(pl_2017_acc_code), unsafe_allow_html=True)

def clean_format_PL_presentation(x, coding_sort):
    gross_profit = x.reindex(['Revenue','Cost of Sales']).sum()
    sub_total_overheads = x.reindex(['Payroll','Recruitment & HR','Rent & Service Charges','Building Expenses','Office Expenses','Travel',
    'Computer costs','Audit, Legal & Consulting','Committees','Insurance','Bank Charges','FX','Other']).sum()
    x.loc['Gross Profit'] = gross_profit
    # st.write('checking inner function',x)
    x.loc['Gross Profit %'] = ( (gross_profit / x.loc['Revenue'])*100.00 ).astype(float)
    x.loc['Sub-Total Overheads'] = sub_total_overheads
    def check(x,account):
        if account in x.index:
            return x.loc[account]
        else:
            return 0 #also tryed N
    x.loc['EBITDA'] = gross_profit + sub_total_overheads + check(x,'IP Capitalisation')
    x.loc['Net Profit before Tax'] = x.loc['EBITDA'] + check(x,'Depreciation') + check(x,'Finance Lease Interest')
    x.loc['Net Profit after Tax'] = x.loc['Net Profit before Tax'] + x.loc['Tax']
    x.loc['Net Profit %'] = (x.loc['Net Profit after Tax'] / x.loc['Revenue'])*100
    x = pd.merge (x,coding_sort, on=['Name'],how='inner')
    x = x.drop(columns =['Sorting_x'])
    x = x.rename(columns = {'Sorting_y' : 'Sorting'}).sort_values(by ='Sorting', ascending=True)
    # cols_to_move = ['Name','NL_YTD','Budget_YTD','YTD_Variance','NL_Month','Budget_Month','Month_Variance']
    # x = x[ cols_to_move + [ col for col in x if col not in cols_to_move ] ]
    x = x.set_index('Name')
    return x

def clean(data,year_column,coding_sort):
    x=clean_format_PL_presentation(data,coding_sort)
    return x.rename(columns={'YTD_Amount':year_column})

pl_2020=clean(pl_2020,year_column='2020',coding_sort=coding_sort)
pl_2019=clean(pl_2019,year_column='2019',coding_sort=coding_sort)
pl_2018=clean(pl_2018,year_column='2018',coding_sort=coding_sort)
pl_2017=clean(pl_2017,year_column='2017',coding_sort=coding_sort)
pl_2016=clean(pl_2016,year_column='2016',coding_sort=coding_sort)
all_pl=pd.concat([pl_2020,pl_2019,pl_2018,pl_2017,pl_2016],axis=1).drop('Sorting',axis=1)

st.write('all', all_pl)
st.write('pl after tax per stats',{'2020':'4,388,598','2019':'4,602,008','2018':'5,800,713','2017':'5,193,050','2016':'5,193,050'})
# st.write('2016', pl_2016)
# df = df.merge (coding_acc_schedule, on='Acc_Number',how='outer')

pl_2020_totals=clean(pl_2020_totals,year_column='2020',coding_sort=coding_sort)
subtotal=pl_2020_totals[['dil_total','bbf_uk_group_total','bbf_irl_group_total']]
pl_2020_totals['check_total']=subtotal.sum(axis=1)
pl_2020_totals['check']=pl_2020_totals['check_total']-pl_2020_totals['2020']
# st.write(subtotal)
st.write(pl_2020_totals)
