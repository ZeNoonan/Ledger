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

# changing signs of accounting entries below
df.loc[:,df.columns.get_level_values(0).isin({"TB", "consol_jnl"})]=df.loc[:,df.columns.get_level_values(0).isin({"TB", "consol_jnl"})]*-1

filter_df=(df.loc[:,df.columns.get_level_values(0).isin({"TB", "consol_jnl"})])
filter_in_dil=(filter_df.loc[:,filter_df.columns.get_level_values(1).isin({"9 Story Dist.", "9SDIL"})])
filter_out_dil=(filter_df.loc[:,~filter_df.columns.get_level_values(1).isin({"9 Story Dist.", "9SDIL"})])
filter_out_uk=(filter_out_dil.loc[:,~filter_out_dil.columns.get_level_values(1).isin({"BBF UK","NK2","PRS","VMP 2D","Knight","NK2","UK","KPL"})])
filter_in_uk=(filter_out_dil.loc[:,filter_out_dil.columns.get_level_values(1).isin({"BBF UK","NK2","PRS","VMP 2D","Knight","NK2","UK","KPL"})])
df[('total','total')]=filter_df.sum(axis=1)
df[('total','9sdil_total')]=filter_in_dil.sum(axis=1)
df[('total','bbf_group_total')]=filter_out_dil.sum(axis=1)
df[('total','bbf_irl_group_total')]=filter_out_uk.sum(axis=1)
df[('total','bbf_uk_group_total')]=filter_in_uk.sum(axis=1)

with st.beta_expander('Checking Totals'):
    st.write('check total equals zero',df['total'].sum(),'close enough its 11')
    quarter_4=df.loc[df[('quarter','quarter')]==4]
    st.write('check q4 totals',quarter_4['total'].sum(),"that works equal to 3")

# st.write('check q4',quarter_4)

coding_acc_schedule = (pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/account_numbers_updated.xlsx')).iloc[:,:3]
# coding_acc_schedule['Acc_Number']=coding_acc_schedule['Acc_Number'].str.replace("-",'').astype(float)

coding_acc_schedule=coding_acc_schedule.rename(columns={'Acc_Number':'Account Code'})
coding_sort=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/account_numbers_updated.xlsx', sheet_name='Sheet2')
# st.write('coding acc sch', coding_acc_schedule)
# st.write('coding sort', coding_sort)


def filter_total(df,coding_acc_schedule):
    df=df.droplevel(0,axis=1)
    df=df.loc[:,['fiscal_year','calendar_year','quarter','date','Account Code','acc_sch','total','9sdil_total','bbf_group_total','bbf_irl_group_total',
    'bbf_uk_group_total',
    'Description','Code','Classification 9SMG','Classification Stats','Sub-Classification Stats']]
    df = df.merge (coding_acc_schedule, on='Account Code',how='outer')

    return df

annual=filter_total(quarter_4,coding_acc_schedule)

# st.markdown(get_table_download_link(annual), unsafe_allow_html=True)
# st.write('checking',annual[annual['Classification 9SMG'].isna()])
# st.write('checking',annual[annual['Classification Stats'].isna()])

x=annual.query('`acc_sch`>919')
x=x[x['Sorting'].isna()]
st.write('should be blank!! below',x)
pl_data=annual.query('`acc_sch`>919')
# st.write('checking pl data', pl_data)


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
pl_2021=check_data.query('`fiscal_year`==2021').set_index('Name').drop('fiscal_year',axis=1)
pl_2020=check_data.query('`fiscal_year`==2020').set_index('Name').drop('fiscal_year',axis=1)
pl_2019=check_data.query('`fiscal_year`==2019').set_index('Name').drop('fiscal_year',axis=1)
pl_2018=check_data.query('`fiscal_year`==2018').set_index('Name').drop('fiscal_year',axis=1)
pl_2017=check_data.query('`fiscal_year`==2017').set_index('Name').drop('fiscal_year',axis=1)
pl_2016=check_data.query('`fiscal_year`==2016').set_index('Name').drop('fiscal_year',axis=1)

pl_2021_data=pl_2021.copy()
pl_2020_data=pl_2020.copy()
pl_2019_data=pl_2019.copy()
pl_2018_data=pl_2018.copy()
pl_2017_data=pl_2017.copy()
pl_2016_data=pl_2016.copy()

pl_2021_totals=totals_data.query('`fiscal_year`==2021').set_index('Name').drop('fiscal_year',axis=1)
pl_2020_totals=totals_data.query('`fiscal_year`==2020').set_index('Name').drop('fiscal_year',axis=1)
pl_2019_totals=totals_data.query('`fiscal_year`==2019').set_index('Name').drop('fiscal_year',axis=1)
pl_2018_totals=totals_data.query('`fiscal_year`==2018').set_index('Name').drop('fiscal_year',axis=1)
pl_2017_totals=totals_data.query('`fiscal_year`==2017').set_index('Name').drop('fiscal_year',axis=1)
pl_2016_totals=totals_data.query('`fiscal_year`==2016').set_index('Name').drop('fiscal_year',axis=1)




# st.write('checking pl 2017',pl_2017)
# pl_2017_acc_code=check_data_acc_code.query('`fiscal_year`==2017').set_index('Account Code').drop('fiscal_year',axis=1)
# st.write('PL by account code for 2020', pl_2017_acc_code)
# st.markdown(get_table_download_link(pl_2017_acc_code), unsafe_allow_html=True)

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
    x.loc['Net Profit before Tax and Amortisation'] = x.loc['EBITDA'] + check(x,'Depreciation') + check(x,'Finance Lease Interest')
    x.loc['Net Profit before Tax'] = x.loc['EBITDA'] + check(x,'Depreciation') + check(x,'Finance Lease Interest')+check(x,'Amortisation Intangible Asset')
    x.loc['Net Profit after Tax'] = x.loc['Net Profit before Tax'] + x.loc['Tax']
    x.loc['Net Profit %'] = (x.loc['Net Profit after Tax'] / x.loc['Revenue'])*100
    x.loc['Net Profit before Tax %'] = (x.loc['Net Profit before Tax and Amortisation'] / x.loc['Revenue'])*100    
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

def pretty_pl_format(df):
    # If you want to see GP % at one decimal point just change the below to 0.1f it will change everything but is a workaround
    df= df.applymap('{:,.0f}'.format)
    df.loc['Gross Profit %']= df.loc['Gross Profit %'].str.replace('€','').str.replace(',','').astype(float).apply('{:,.0f}%'.format)
    df.loc['Net Profit %']= df.loc['Net Profit %'].str.replace('€','').str.replace(',','').astype(float).apply('{:,.0f}%'.format)
    df.loc['Net Profit before Tax %']= df.loc['Net Profit before Tax %'].str.replace('€','').str.replace(',','').astype(float).apply('{:,.0f}%'.format)
    # df= df.applymap('{:,.0f}'.format)
    return df

def format_pl(x):
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

with st.beta_expander('Full group by year'):
    pl_2021=clean(pl_2021,year_column='2021',coding_sort=coding_sort)
    pl_2020=clean(pl_2020,year_column='2020',coding_sort=coding_sort)
    pl_2019=clean(pl_2019,year_column='2019',coding_sort=coding_sort)
    pl_2018=clean(pl_2018,year_column='2018',coding_sort=coding_sort)
    pl_2017=clean(pl_2017,year_column='2017',coding_sort=coding_sort)
    pl_2016=clean(pl_2016,year_column='2016',coding_sort=coding_sort)
    all_pl=pd.concat([pl_2021,pl_2020,pl_2019,pl_2018,pl_2017,pl_2016],axis=1).drop('Sorting',axis=1)

    st.write('all', format_pl(all_pl))
    st.write('pl after tax per stats',{'2021':'6,868,694','2020':'4,388,598','2019':'4,602,008','2018':'5,800,713','2017':'5,193,050','2016':'4,398,294'})


with st.beta_expander('PL for each group for each year'):
    # https://stackoverflow.com/questions/40225683/how-to-simply-add-a-column-level-to-a-pandas-dataframe
    pl_2021_totals=clean(pl_2021_totals,year_column='2021',coding_sort=coding_sort).drop(['2021','bbf_total'],axis=1).assign(newlevel='2021')\
        .set_index('newlevel', append=True).unstack('newlevel').sort_values(by=('Sorting','2021'))
    pl_2020_totals=clean(pl_2020_totals,year_column='2020',coding_sort=coding_sort).drop(['2020','bbf_total'],axis=1).assign(newlevel='2020')\
        .set_index('newlevel', append=True).unstack('newlevel').sort_values(by=('Sorting','2020'))
    pl_2019_totals=clean(pl_2019_totals,year_column='2019',coding_sort=coding_sort).drop(['2019','bbf_total'],axis=1).assign(newlevel='2019')\
        .set_index('newlevel', append=True).unstack('newlevel').sort_values(by=('Sorting','2019'))
    pl_2018_totals=clean(pl_2018_totals,year_column='2018',coding_sort=coding_sort).drop(['2018','bbf_total'],axis=1).assign(newlevel='2018')\
        .set_index('newlevel', append=True).unstack('newlevel').sort_values(by=('Sorting','2018'))
    pl_2017_totals=clean(pl_2017_totals,year_column='2017',coding_sort=coding_sort).drop(['2017','bbf_total'],axis=1).assign(newlevel='2017')\
        .set_index('newlevel', append=True).unstack('newlevel').sort_values(by=('Sorting','2017'))
    pl_2016_totals=clean(pl_2016_totals,year_column='2016',coding_sort=coding_sort).drop(['2016','bbf_total'],axis=1).assign(newlevel='2016')\
        .set_index('newlevel', append=True).unstack('newlevel').sort_values(by=('Sorting','2016'))

    def test_total():
        subtotal=pl_2020_totals[['dil_total','bbf_uk_group_total','bbf_irl_group_total']]
        pl_2020_totals['check_total']=subtotal.sum(axis=1)
        pl_2020_totals['check']=pl_2020_totals['check_total']-pl_2020_totals['2020']
        return pl_2020_totals

    st.write(format_pl( pl_2021_totals ))
    st.write(format_pl( pl_2020_totals ))
    st.write(format_pl( pl_2019_totals ))
    st.write(format_pl( pl_2018_totals ))
    st.write(format_pl( pl_2017_totals ))
    st.write(format_pl( pl_2016_totals ))

    test_concat=pd.concat([pl_2021_totals,pl_2020_totals,pl_2019_totals,pl_2018_totals,pl_2017_totals,pl_2016_totals],axis=1)
    # st.write('test',test_concat)
    check_test=test_concat.loc['Net Profit before Tax and Amortisation'].reset_index()
    check_test_1=test_concat.loc['Net Profit before Tax and Amortisation'].reset_index().rename(columns={'level_0':'index','newlevel':'date'}).set_index('index')\
        .drop(index=['Sorting','dil_total']).reset_index().rename(columns={'index':'location','Net Profit before Tax and Amortisation':'net_profit'})\
            .sort_values(by='location').reset_index().drop('index',axis=1)
    # check_test_1['date']=pd.to_datetime(check_test_1['date'])
    st.write('check_test')
    st.write(check_test_1)

    selection_3 = alt.selection_multi(fields=['location'], bind='legend')
    scale_3=alt.Scale(domain=['bbf_irl_group_total','bbf_uk_group_total'],range=['blue','red'])
    test_run_3=alt.Chart(check_test_1,title='Net Profit by Year by Location').mark_bar(size=80).encode(
    # https://stackoverflow.com/questions/64032908/altair-chart-reads-more-information-from-timestamps-than-it-should
    alt.X('date:O',axis=alt.Axis(title='date')),
    # alt.X('date:T',timeUnit="year", axis=alt.Axis(labelAlign='right',title='date',labelAngle=360,tickMinStep=1000*60*60*24*360)),
    alt.Y('net_profit:Q'),
    color=alt.Color('location:N',scale=scale_3,sort=alt.SortField("location", "descending")),order="location:O",
    opacity=alt.condition(selection_3, alt.value(1), alt.value(0.1)))
    overlay = pd.DataFrame({'net_profit': [5000000]})
    vline = alt.Chart(overlay).mark_rule(color='black', strokeWidth=2).encode(y='net_profit:Q')
    # text=test_run_3.mark_text(align='left',baseline='middle',dx=5).encode(text=alt.Text('net_profit:Q',format = ",.0f"))
    # text=test_run_3.mark_text().encode(x=alt.X('date:O'),y=alt.Y('net_profit:Q'),detail='location:N',text=alt.Text('net_profit:Q',format = ",.0f"))
    # updated_test_chart = alt.layer(test_run_3,vline,text)
    updated_test_chart = alt.layer(test_run_3)

    st.write('Select and press shift to highlight locations')

    st.altair_chart((updated_test_chart).add_selection(selection_3),use_container_width=True)
    net_profit_table=check_test_1.pivot(index='date',values='net_profit',columns='location').reset_index()
    # st.write(net_profit_table.sort_values(by='date',ascending=False).style.format({'bbf_irl_group_total':"{:,.0f}",'bbf_uk_group_total':"{:,.0f}",'date':"{:%Y}"}))
    st.write(net_profit_table.sort_values(by='date',ascending=False).style.format({'bbf_irl_group_total':"{:,.0f}",'bbf_uk_group_total':"{:,.0f}"}))


    np_data=test_concat.loc['Net Profit before Tax %'].reset_index().rename(columns={'level_0':'index','newlevel':'date'}).set_index('index')\
        .drop(index=['Sorting','dil_total']).reset_index().rename(columns={'index':'location','Net Profit before Tax %':'net_profit_%'})\
            .sort_values(by='location').reset_index().drop('index',axis=1)
    np_data['net_profit_%']=np_data['net_profit_%']/100
    net_profit_table_percent=np_data.pivot(index='date',values='net_profit_%',columns='location').reset_index()
    # st.write('np data', np_data)
    test_np_data=np_data.copy()
    # st.header('see below')
    test_np_data.loc[6,['net_profit_%']]=0
    # st.write(test_np_data)
    # st.write(test_np_data.loc[(test_np_data['location']=='bbf_uk_group_total')&(test_np_data['date']=='2021')])
    # st.write(test_np_data.loc['2021','bbf_uk_group_total'])
    

    line=alt.Chart(test_np_data).mark_line().encode(
        alt.X('date:O',axis=alt.Axis(title='date')),
        alt.Y('net_profit_%:Q'),
        color=alt.Color('location:N'),
        opacity=alt.OpacityValue(0.3)
    )
    labels=alt.Chart(test_np_data).mark_text().encode(
        alt.X('date:O',axis=alt.Axis(title='date')),
        alt.Y('net_profit_%:Q'),
        alt.Text('net_profit_%:Q',format='.0%')
        # color=alt.Color('location:N')
    )
    updated_test_chart_1=alt.layer(test_run_3,line,labels)
    updated_test_chart_2=alt.layer(line,labels)
    st.altair_chart((updated_test_chart_1).resolve_scale(y='independent').add_selection(selection_3),use_container_width=True)
    # st.altair_chart((updated_test_chart_2).add_selection(selection_3),use_container_width=True)
    st.write(net_profit_table_percent.style.format({'bbf_irl_group_total':"{:,.0%}",'bbf_uk_group_total':"{:,.0%}"}))

with st.beta_expander('Net Profit %'):

    check_test_profit=test_concat.loc['Net Profit before Tax and Amortisation'].reset_index().rename(columns={'level_0':'index','newlevel':'date'}).set_index('index')\
        .drop(index=['Sorting','dil_total']).reset_index().rename(columns={'index':'location','Net Profit before Tax and Amortisation':'net_profit'})\
            .sort_values(by='location').reset_index().drop('index',axis=1)
    check_test_revenue=test_concat.loc['Revenue'].reset_index().rename(columns={'level_0':'index','newlevel':'date'}).set_index('index')\
        .drop(index=['Sorting','dil_total']).reset_index().rename(columns={'index':'location','Revenue':'total_revenue'})\
            .sort_values(by='location').reset_index().drop('index',axis=1)
    # st.write('check_test')
    revenue_profit = pd.merge(check_test_profit,check_test_revenue,on=['location','date'],how='outer')
    # st.write(revenue_profit)
    total_revenue_profit = revenue_profit.groupby('date').agg ( net_profit = ( 'net_profit','sum' ), revenue=( 'total_revenue','sum' )).reset_index()
    
    total_revenue_profit['total_profit_%']= (total_revenue_profit['net_profit']/total_revenue_profit['revenue'])
    # st.write(total_revenue_profit)
    select=total_revenue_profit.loc[:,['date','total_profit_%']]
    profit_table = pd.merge(net_profit_table_percent,select, on='date',how='outer').rename(columns={'bbf_irl_group_total':'bbf_irl_profit_%','bbf_uk_group_total':'bbf_uk_profit_%'})
    # st.write(profit_table)
    data_table=pd.melt(profit_table,id_vars='date',value_vars=['bbf_irl_profit_%','bbf_uk_profit_%','total_profit_%'],value_name='net_profit',var_name='location')
    data_table.loc[11,['net_profit']]=0
    # st.write(data_table)
    st.write("2021 would have been best net profit percentage ever only for 1.39m of losses in UK which reduced IRL percent from 20.5% to 17.4%")
    st.write("check this after re-importing 2021 file")
    # selection_3 = alt.selection_multi(fields=['location'], bind='legend')
    # scale_3=alt.Scale(domain=['bbf_irl_profit_%','bbf_uk_profit_%','total_profit_%'],range=['blue','red','green'])
    test_run_3=alt.Chart(data_table,title='Net Profit percent by Year').mark_bar().encode(
    # https://stackoverflow.com/questions/64032908/altair-chart-reads-more-information-from-timestamps-than-it-should
    alt.X('date:O',axis=alt.Axis(title='year')),
    # alt.X('date:T',timeUnit="year", axis=alt.Axis(labelAlign='right',title='date',labelAngle=360,tickMinStep=1000*60*60*24*360)),
    alt.Y('net_profit:Q',axis=alt.Axis(title='net_profit percentage')),
    color=alt.Color('date:N'),
    column='location:N',
    ).properties(width=350)
    # overlay = pd.DataFrame({'net_profit': [5000000]})
    # vline = alt.Chart(overlay).mark_rule(color='black', strokeWidth=2).encode(y='net_profit:Q')
    text=test_run_3.mark_text(align='left',baseline='middle',dx=5).encode(text=alt.Text('net_profit:Q',format = ",.0f"))
    # text=test_run_3.mark_text().encode(x=alt.X('date:O'),y=alt.Y('net_profit:Q'),detail='location:N',text=alt.Text('net_profit:Q',format = ",.0f"))
    # updated_test_chart = alt.layer(test_run_3,text)
    # updated_test_chart = alt.layer(test_run_3)

    # st.write('Select and press shift to highlight locations')

    st.altair_chart((test_run_3))
    # st.altair_chart((test_run_3 + text))

    st.write("Let's run the Analysis without BBF UK as the 2021 losses were not operating losses")
    
    data_table_no_uk = data_table.copy()
    data_table_no_uk.loc[17,['net_profit']]=data_table_no_uk.loc[5,['net_profit']]
    # st.write(data_table_no_uk)
    test_run_3=alt.Chart(data_table_no_uk,title='Net Profit percent by Year with no 2021 UK Losses').mark_bar().encode(
    alt.X('date:O',axis=alt.Axis(title='year')),
    alt.Y('net_profit:Q',axis=alt.Axis(title='net_profit percentage')),
    color=alt.Color('date:N'),
    column='location:N',
    ).properties(width=350)
    st.altair_chart((test_run_3))
    st.write("So what is saying ")








with st.beta_expander('Revenue Analysis'):
    check_test=test_concat.loc['Revenue'].reset_index()
    check_test_1=test_concat.loc['Revenue'].reset_index().rename(columns={'level_0':'index','newlevel':'date'}).set_index('index')\
        .drop(index=['Sorting','dil_total']).reset_index().rename(columns={'index':'location','Revenue':'Revenue'})\
            .sort_values(by='location').reset_index().drop('index',axis=1)
    # check_test_1['date']=pd.to_datetime(check_test_1['date'])
    # st.write(check_test)
    # st.write(check_test_1)

    selection_3 = alt.selection_multi(fields=['location'], bind='legend')
    scale_3=alt.Scale(domain=['bbf_irl_group_total','bbf_uk_group_total'],range=['blue','red'])
    test_run_3=alt.Chart(check_test_1,title='Revenue by Year by Location').mark_bar(size=80).encode(
    # https://stackoverflow.com/questions/64032908/altair-chart-reads-more-information-from-timestamps-than-it-should
    alt.X('date:O',axis=alt.Axis(title='date')),
    # alt.X('date:T',timeUnit="year", axis=alt.Axis(labelAlign='right',title='date',labelAngle=360,tickMinStep=1000*60*60*24*360)),
    alt.Y('Revenue:Q'),
    color=alt.Color('location:N',scale=scale_3,sort=alt.SortField("location", "descending")),order="location:O",
    opacity=alt.condition(selection_3, alt.value(1), alt.value(0.1)))
    overlay = pd.DataFrame({'Revenue': [40000000]})
    vline = alt.Chart(overlay).mark_rule(color='black', strokeWidth=2).encode(y='Revenue:Q')
    # text=test_run_3.mark_text(align='left',baseline='middle',dx=5).encode(text=alt.Text('net_profit:Q',format = ",.0f"))
    # text=test_run_3.mark_text().encode(x=alt.X('date:O'),y=alt.Y('net_profit:Q'),detail='location:N',text=alt.Text('net_profit:Q',format = ",.0f"))
    # updated_test_chart = alt.layer(test_run_3,vline,text)
    updated_test_chart = alt.layer(test_run_3)

    st.write('Select and press shift to highlight locations')

    st.altair_chart((updated_test_chart).add_selection(selection_3),use_container_width=True)

with st.beta_expander('Gross Profit Analysis'):

    check_test_profit=test_concat.loc['Gross Profit'].reset_index().rename(columns={'level_0':'index','newlevel':'date'}).set_index('index')\
        .drop(index=['Sorting','dil_total']).reset_index().rename(columns={'index':'location','Gross Profit':'net_profit'})\
            .sort_values(by='location').reset_index().drop('index',axis=1)
    check_test_revenue=test_concat.loc['Revenue'].reset_index().rename(columns={'level_0':'index','newlevel':'date'}).set_index('index')\
        .drop(index=['Sorting','dil_total']).reset_index().rename(columns={'index':'location','Revenue':'total_revenue'})\
            .sort_values(by='location').reset_index().drop('index',axis=1)
    # st.write('check_test')
    revenue_profit = pd.merge(check_test_profit,check_test_revenue,on=['location','date'],how='outer')
    # st.write(revenue_profit)
    total_revenue_profit = revenue_profit.groupby('date').agg ( net_profit = ( 'net_profit','sum' ), revenue=( 'total_revenue','sum' )).reset_index()
    
    total_revenue_profit['total_profit_%']= (total_revenue_profit['net_profit']/total_revenue_profit['revenue'])
    # st.write(total_revenue_profit)
    select=total_revenue_profit.loc[:,['date','total_profit_%']]
    np_data=test_concat.loc['Gross Profit %'].reset_index().rename(columns={'level_0':'index','newlevel':'date'}).set_index('index')\
        .drop(index=['Sorting','dil_total']).reset_index().rename(columns={'index':'location','Gross Profit %':'gross_profit_%'})\
            .sort_values(by='location').reset_index().drop('index',axis=1)
    np_data['gross_profit_%']=np_data['gross_profit_%']/100
    net_profit_table_percent=np_data.pivot(index='date',values='gross_profit_%',columns='location').reset_index()
    profit_table = pd.merge(net_profit_table_percent,select, on='date',how='outer').rename(columns={'bbf_irl_group_total':'bbf_irl_profit_%','bbf_uk_group_total':'bbf_uk_profit_%'})
    # st.write(profit_table)
    data_table=pd.melt(profit_table,id_vars='date',value_vars=['bbf_irl_profit_%','bbf_uk_profit_%','total_profit_%'],value_name='net_profit',var_name='location')
    # st.write("before zero out",data_table)
    data_table.loc[11,['net_profit']]=0
    # st.write("after zero out",data_table)
    # st.write("2021 would have been best net profit percentage ever only for 1.39m of losses in UK which reduced IRL percent from 20.5% to 17.4%")
    st.write("check this after re-importing 2021 file")
    # selection_3 = alt.selection_multi(fields=['location'], bind='legend')
    # scale_3=alt.Scale(domain=['bbf_irl_profit_%','bbf_uk_profit_%','total_profit_%'],range=['blue','red','green'])
    test_run_3=alt.Chart(data_table,title='Gross Profit percent by Year').mark_bar().encode(
    # https://stackoverflow.com/questions/64032908/altair-chart-reads-more-information-from-timestamps-than-it-should
    alt.X('date:O',axis=alt.Axis(title='year')),
    # alt.X('date:T',timeUnit="year", axis=alt.Axis(labelAlign='right',title='date',labelAngle=360,tickMinStep=1000*60*60*24*360)),
    alt.Y('net_profit:Q',axis=alt.Axis(title='gross_profit percentage')),
    color=alt.Color('date:N'),
    column='location:N',
    ).properties(width=350)

    st.altair_chart((test_run_3))

with st.beta_expander('Headcount'):
    with st.echo():
        # comes from headcount python file
        headcount_data = pd.read_pickle('C:/Users/Darragh/Documents/Python/Work/Data/headcount_summary.pkl').reset_index()
    # st.write(headcount_data)
    headcount_data['calendar_year']=headcount_data['date'].dt.year
    headcount_data['calendar_month']=headcount_data['date'].dt.month
    headcount_data['fiscal_month']=headcount_data['calendar_month'].map({9:1,10:2,11:3,12:4,1:5,2:6,3:7,4:8,5:9,6:10,7:11,8:12})
    headcount_data['fiscal_year'] = np.where((headcount_data['fiscal_month'] > 4.1), headcount_data['calendar_year'], headcount_data['calendar_year']+1)
    average_data = headcount_data.groupby('fiscal_year').agg ( bbf_irl = ( 'bbf','mean' ), uk=( 'uk','mean' ), mauve=( 'mauve','mean' )).reset_index()
    # drop 2014 -2015 as don't need those
    average_data=average_data.loc[(average_data['fiscal_year']>2015),:].reset_index().drop('index',axis=1).rename(columns={'fiscal_year':'date'})
    # st.write(average_data)
    data_table=pd.melt(average_data,id_vars='date',value_vars=['bbf_irl','uk','mauve'],value_name='net_profit',var_name='location')
    # st.write(data_table)

    selection_3 = alt.selection_multi(fields=['location'], bind='legend')
    scale_3=alt.Scale(domain=['bbf_irl','uk','mauve'],range=['blue','red','green'])
    test_run_3=alt.Chart(data_table,title='Headcount by Year').mark_bar(size=80).encode(
    # https://stackoverflow.com/questions/64032908/altair-chart-reads-more-information-from-timestamps-than-it-should
    alt.X('date:O',axis=alt.Axis(title='year')),
    # alt.X('date:T',timeUnit="year", axis=alt.Axis(labelAlign='right',title='date',labelAngle=360,tickMinStep=1000*60*60*24*360)),
    alt.Y('net_profit:Q'),
    color=alt.Color('location:N',scale=scale_3,sort=alt.SortField("location", "descending")),order="location:O",
    opacity=alt.condition(selection_3, alt.value(1), alt.value(0.1)))
    overlay = pd.DataFrame({'net_profit': [300]})
    vline = alt.Chart(overlay).mark_rule(color='black', strokeWidth=2).encode(y='net_profit:Q')
    # text=test_run_3.mark_text(align='left',baseline='middle',dx=5).encode(text=alt.Text('net_profit:Q',format = ",.0f"))
    # text=test_run_3.mark_text().encode(x=alt.X('date:O'),y=alt.Y('net_profit:Q'),detail='location:N',text=alt.Text('net_profit:Q',format = ",.0f"))
    # updated_test_chart = alt.layer(test_run_3,vline,text)
    updated_test_chart = alt.layer(test_run_3,vline)
    # updated_test_chart = alt.layer(test_run_3)

    st.write('Select and press shift to highlight locations')

    st.altair_chart((updated_test_chart).add_selection(selection_3),use_container_width=True)

with st.beta_expander('Cashflow'):
    st.write('cashflow')
    acc_schedule = (pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/account_numbers_updated.xlsx', sheet_name='Sheet3')).iloc[:,:3]
    acc_schedule=acc_schedule.rename(columns={'Acc_Number':'Account Code'})
    # st.write(quarter_4)
    
    annual_data=filter_total(quarter_4,acc_schedule)
    annual_data_bs=annual_data.query('`acc_sch`<920')
    # st.write(annual_data)
    annual_data=pl_generation(annual_data_bs,category_to_filter_on=['fiscal_year','Name'],total='total')

    # cash_2021=annual_data.query('`fiscal_year`==2021').set_index('Name').drop('fiscal_year',axis=1)
    # cash_2020=annual_data.query('`fiscal_year`==2020').set_index('Name').drop('fiscal_year',axis=1)
    cash_2021=annual_data.query('`fiscal_year`==2021').set_index('Name').drop('fiscal_year',axis=1)
    cash_2020=annual_data.query('`fiscal_year`==2020').set_index('Name').drop('fiscal_year',axis=1)
    cash_2019=annual_data.query('`fiscal_year`==2019').set_index('Name').drop('fiscal_year',axis=1)
    cash_2018=annual_data.query('`fiscal_year`==2018').set_index('Name').drop('fiscal_year',axis=1)
    cash_2017=annual_data.query('`fiscal_year`==2017').set_index('Name').drop('fiscal_year',axis=1)
    cash_2016=annual_data.query('`fiscal_year`==2016').set_index('Name').drop('fiscal_year',axis=1)
    pl_2021_data=pl_2021_data.rename(columns={'YTD_Amount':'bank'}).drop('Sorting',axis=1).reset_index()
    pl_2020_data=pl_2020_data.rename(columns={'YTD_Amount':'bank'}).drop('Sorting',axis=1).reset_index()
    pl_2019_data=pl_2019_data.rename(columns={'YTD_Amount':'bank'}).drop('Sorting',axis=1).reset_index()
    pl_2018_data=pl_2018_data.rename(columns={'YTD_Amount':'bank'}).drop('Sorting',axis=1).reset_index()
    pl_2017_data=pl_2017_data.rename(columns={'YTD_Amount':'bank'}).drop('Sorting',axis=1).reset_index()
    pl_2016_data=pl_2016_data.rename(columns={'YTD_Amount':'bank'}).drop('Sorting',axis=1).reset_index()
    # st.write('cash 2021', cash_2021)
    st.write('cash 2020', cash_2020)


    def cashflow_working(cash_current,cash_prior):

        new_df=pd.concat([cash_current,cash_prior],axis=1).drop('Sorting',axis=1).reset_index()
        filt=~new_df['Name'].isin({'Cash at Bank','Profit and Loss Account','Dividends'})
        new_df['YTD_Amount']=new_df['YTD_Amount'].fillna(0)
        new_df['diff']=new_df.iloc[:,1]-new_df.iloc[:,2]
        new_df['bank']=new_df['diff'].where(filt)
        # new_df['YTD_Amount']=new_df['YTD_Amount'].fillna(0)
        return new_df

    cashflow_workings_2021 = cashflow_working(cash_current=cash_2021,cash_prior=cash_2020).fillna(0)
    cashflow_workings_2020 = cashflow_working(cash_current=cash_2020,cash_prior=cash_2019)
    st.write('cashflow workings',cashflow_workings_2020)
    st.markdown(get_table_download_link(cashflow_workings_2020), unsafe_allow_html=True)

    def cashflow_statement(cash_workings_returned=cashflow_workings_2021,pl=pl_2021_data):
        dividends=cash_workings_returned.loc[(cash_workings_returned['Name']=='Dividends')].drop('bank',axis=1)
        dividends['bank']=dividends.iloc[:,1]
        dividends=dividends.loc[:,['Name','bank']].reset_index().drop('index',axis=1)
        bs_cash = cash_workings_returned.loc[:,['Name','bank']]
        cashflow_statement=pd.concat([pl,dividends,bs_cash],axis=0).reset_index().drop('index',axis=1)
        return cashflow_statement
    
    cashflow_2021=cashflow_statement(cash_workings_returned=cashflow_workings_2021,pl=pl_2021_data)
    cashflow_2020=cashflow_statement(cash_workings_returned=cashflow_workings_2020,pl=pl_2020_data)
    st.write('cashflow 2020',cashflow_2020)

    def cashflow_check(cashflow_statement=cashflow_2021,cash_workings=cashflow_workings_2021):
        test_df=pd.DataFrame(columns=['bank'],data=[cashflow_statement['bank'].sum()])
        test_df['Name']='Cash at Bank'
        # st.write('cash workings',cash_workings)
        # st.write('check cash workings to drop 2021 2020 and bank', cash_workings.drop(cash_workings.iloc[:,1],axis=1))
        # FIX BELOW COLUMSN
        # st.write('check cash workings to drop 2021 2020 and bank', cash_workings.drop(cash_workings.columns[[1,2,4]],axis=1))
        cash_check=cash_workings.loc[(cash_workings['Name']=='Cash at Bank')].drop(cash_workings.columns[[1,2,4]],axis=1).rename(columns={'diff':'bank'})
        checking_cash_test = pd.concat([cash_check,test_df],axis=0).set_index('Name')
        checking_cash_test.loc['total']=checking_cash_test['bank'].sum()
        return checking_cash_test

    check_cash_2021=cashflow_check(cashflow_statement=cashflow_2021,cash_workings=cashflow_workings_2021)
    check_cash_2020=cashflow_check(cashflow_statement=cashflow_2020,cash_workings=cashflow_workings_2020)

    st.write(check_cash_2021.reset_index().style.format("{:,.0f}",subset=['bank']))
    st.write(check_cash_2020.reset_index().style.format("{:,.0f}",subset=['bank']))
    # st.write('pl 2021 total', pl_2021_data.sum())
    # st.write('bs 2020', cash_2020)


with st.beta_expander('Check PL v. Stats'):
    result_2021=[{'index':'bbf_irl_group_total','Net Profit after Tax':6121790},{'index':'bbf_uk_group_total',
    'Net Profit after Tax':-1391583},{'index':'dil_total','Net Profit after Tax':2138487}]

    result_2020=[{'index':'bbf_irl_group_total','Net Profit after Tax':1902048},{'index':'bbf_uk_group_total',
    'Net Profit after Tax':682433},{'index':'dil_total','Net Profit after Tax':1804120}]
    result_2019=[{'index':'bbf_irl_group_total','Net Profit after Tax':-309092},{'index':'bbf_uk_group_total',
    'Net Profit after Tax':2874602},{'index':'dil_total','Net Profit after Tax':2036498}]
    result_2018=[{'index':'bbf_irl_group_total','Net Profit after Tax':1007342},{'index':'bbf_uk_group_total',
    'Net Profit after Tax':1673615},{'index':'dil_total','Net Profit after Tax':3119755}]
    result_2017=[{'index':'bbf_irl_group_total','Net Profit after Tax':973928},{'index':'bbf_uk_group_total',
    'Net Profit after Tax':1038459},{'index':'dil_total','Net Profit after Tax':3180662}]
    result_2016=[{'index':'bbf_irl_group_total','Net Profit after Tax':1375500},{'index':'bbf_uk_group_total',
    'Net Profit after Tax':1349304},{'index':'dil_total','Net Profit after Tax':1673490}]

    check_2021=pl_2021_totals.loc['Net Profit after Tax'].reset_index().drop('newlevel',axis=1).rename(columns={'level_0':'index'}).set_index('index').drop(index=['Sorting'])
    check_2020=pl_2020_totals.loc['Net Profit after Tax'].reset_index().drop('newlevel',axis=1).rename(columns={'level_0':'index'}).set_index('index').drop(index=['Sorting'])
    check_2019=pl_2019_totals.loc['Net Profit after Tax'].reset_index().drop('newlevel',axis=1).rename(columns={'level_0':'index'}).set_index('index').drop(index=['Sorting'])
    check_2018=pl_2018_totals.loc['Net Profit after Tax'].reset_index().drop('newlevel',axis=1).rename(columns={'level_0':'index'}).set_index('index').drop(index=['Sorting'])
    check_2017=pl_2017_totals.loc['Net Profit after Tax'].reset_index().drop('newlevel',axis=1).rename(columns={'level_0':'index'}).set_index('index').drop(index=['Sorting'])
    check_2016=pl_2016_totals.loc['Net Profit after Tax'].reset_index().drop('newlevel',axis=1).rename(columns={'level_0':'index'}).set_index('index').drop(index=['Sorting'])

    def check_bottom_line(result_2020,check_2020):
        total_check=pd.DataFrame(result_2020).set_index('index').rename(columns={'Net Profit after Tax':'stats'})
        test_check=pd.concat([check_2020,total_check],axis=1)
        test_check['diff']=test_check['stats']-test_check['Net Profit after Tax']
        return test_check

    st.write('2021 check',format_pl(check_bottom_line(result_2021,check_2021)))
    st.write('2020 check',format_pl(check_bottom_line(result_2020,check_2020)))
    st.write('2019 check',format_pl(check_bottom_line(result_2019,check_2019)))
    st.write('2018 check',format_pl(check_bottom_line(result_2018,check_2018)))
    st.write('2017 check',format_pl(check_bottom_line(result_2017,check_2017)))
    st.write('2016 check',format_pl(check_bottom_line(result_2016,check_2016)))