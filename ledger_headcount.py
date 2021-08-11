import pandas as pd
import numpy as np
import streamlit as st
import datetime
import altair as alt
from streamlit_echarts import st_echarts

st.set_page_config(layout="wide")

# st.header('Get detail listing of employees by Department good sense check')


st.write('Select start of forecast period below and actual')
with st.echo():
    # start_forecast_period_resourcing_tool='2021-07-01 00:00:00'
    data_2021='C:/Users/Darragh/Documents/Python/Work/Data/NL_2021_11.xlsx'
    data_2020='C:/Users/Darragh/Documents/Python/Work/Data/NL_2020.xlsx'
    data_2019='C:/Users/Darragh/Documents/Python/Work/Data/NL_2019.xlsx'
    data_2018='C:/Users/Darragh/Documents/Python/Work/Data/nl_18.xlsx'
    data_2017='C:/Users/Darragh/Documents/Python/Work/Data/nl_17.xlsx'
    data_2016='C:/Users/Darragh/Documents/Python/Work/Data/nl_16.xlsx'
    data_2015='C:/Users/Darragh/Documents/Python/Work/Data/nl_15.xlsx'
    data_2014='C:/Users/Darragh/Documents/Python/Work/Data/nl_14.xlsx'

@st.cache
def load_ledger_data(x):
    return pd.read_excel(x,na_values=np.nan)

forecast_resourcing=load_ledger_data('C:/Users/Darragh/Documents/Python/Work/Data/resource_planner_export_11_06_2021.xlsx')
cached_2021=load_ledger_data(data_2021).copy()
cached_2020=load_ledger_data(data_2020).copy()
# cached_2019=load_ledger_data(data_2019).copy()
# cached_2018=load_ledger_data(data_2018).copy()
# cached_2017=load_ledger_data(data_2017).copy()
# cached_2016=load_ledger_data(data_2016).copy()
# cached_2015=load_ledger_data(data_2015).copy()
# cached_2014=load_ledger_data(data_2014).copy()

with st.echo():
    start_forecast_period_resourcing_tool='2021-07-31 00:00:00'
    forecast_project_mapping=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/Project_Codes_2021_.xlsx', sheet_name='Sheet2')
    coding_acc_schedule = (pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/account_numbers.xlsx')).iloc[:,:3]
    coding_sort=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/account_numbers.xlsx', sheet_name='Sheet2')
    Project_codes=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/Project_Codes_2021_.xlsx').rename(columns = {'User Code' : 'SUBANALYSIS 0'})



@st.cache
def nl_raw_clean_file(x, coding_acc_schedule):
    # st.write(x.head())
    x['Acc_Schedule']=x['Account Code'].str[:3]
    x['Acc_Schedule']=pd.to_numeric(x['Acc_Schedule'])
    x['Project']=x['Project'].replace({'1-Z-253 Eureka 2':'1-Z-209 Eureka'}) # replace Eureka 2 with Eureka 1 as tag-on
    x['Project_Code'] = x['Project'].str[:8]
    x['Project_Name'] = x['Project'].str[8:]
    x['Acc_Number'] = x['Account Code']
    x['Journal Amount'] = x['Journal Amount'] * -1
    x = x.merge (coding_acc_schedule, on='Acc_Number',how='outer')
    x['Department'] = x['Department'].replace( {'T0000':"TV",'CG000':"CG",
    'P0000':"Post",'A0000':"Admin",'D0000':"Development",'I0000':"IT",'R0000':"Pipeline",'HR000':"HR"})
    x['calendar_month']=x['Per.'].map({1:9,2:10,3:11,4:12,5:1,6:2,7:3,8:4,9:5,10:6,11:7,12:8,19:8})
    x['calendar_year'] = np.where((x['Per.'] > 4.1), x['Yr.'], x['Yr.']-1)
    x['calendar_year']=x['calendar_year']+2000
    x=x.rename(columns={'calendar_year':'year', 'calendar_month':'month'})
    x['month']=np.where(x['Jrn. No.']=='BUK0000979', 3, x['month']) # CLEAN UK SIDE WHERE MARCH AND APRIL WERE ENTERED IN SAME PERIOD
    x['month']=np.where(x['Jrn. No.']=='BUK0000913', 4, x['month'])
    x['month']=np.where(x['Jrn. No.']=='BUK0000914', 4, x['month'])
    x['month']=np.where(x['Jrn. No.']=='BUK0000903', 3, x['month'])
    x['month']=np.where(x['Jrn. No.']=='2021', 5, x['month'])
    x['month']=np.where(x['Jrn. No.']=='2770', 5, x['month'])
    x['month']=np.where(x['Jrn. No.']=='2771', 5, x['month'])
    x['month']=np.where(x['Jrn. No.']=='2772', 5, x['month'])
    x['month']=np.where(x['Jrn. No.']=='1249', 5, x['month'])
    x['month']=np.where(x['Jrn. No.']=='1250', 5, x['month'])
    x['month']=np.where(x['Jrn. No.']=='643312', 4, x['month'])
    x['month']=np.where(x['Jrn. No.']=='647032', 4, x['month'])
    x['month']=np.where(x['Jrn. No.']=='649352', 5, x['month'])
    x['month']=np.where(x['Jrn. No.']=='651620', 5, x['month'])
    x['month']=np.where(x['Jrn. No.']=='657659', 5, x['month'])
    x['month']=np.where(x['Jrn. No.']=='1115', 5, x['month'])
    x['month']=np.where(x['Jrn. No.']=='INV1871', 5, x['month'])
    x['month']=np.where(x['Jrn. No.']=='INV1874', 5, x['month'])
    x['month']=np.where(x['Jrn. No.']=='3037', 11, x['month'])
    x['month']=np.where(x['Jrn. No.']=='1600', 11, x['month'])
    x['month']=np.where(x['Jrn. No.']=='WCCINV2325', 11, x['month'])
    x['month']=np.where(x['Jrn. No.']=='WCCINV2326', 11, x['month'])
    x['month']=np.where(x['Jrn. No.']=='WCCINV2367', 11, x['month'])
    x['month']=np.where(x['Jrn. No.']=='2861', 8, x['month'])
    x['month']=np.where(x['Jrn. No.']=='2862', 7, x['month'])
    x['month']=np.where(x['Jrn. No.']=='2918', 9, x['month'])
    x['month']=np.where(x['Jrn. No.']=='694628', 9, x['month'])
    x['month']=np.where(x['Jrn. No.']=='696682', 9, x['month'])
    x['month']=np.where(x['Jrn. No.']=='2795', 6, x['month'])
    x['month']=np.where(x['Jrn. No.']=='2796', 6, x['month'])
    x['month']=np.where(x['Jrn. No.']=='2797', 6, x['month'])
    x['month']=np.where(x['Jrn. No.']=='1264', 6, x['month'])
    x['month']=np.where(x['Jrn. No.']=='666802', 6, x['month'])
    x['month']=np.where(x['Jrn. No.']=='INV1891', 6, x['month'])
    x['month']=np.where(x['Jrn. No.']=='INV1948', 6, x['month'])
    x['month']=np.where(x['Jrn. No.']=='WCCINV1910', 6, x['month'])
    x=x.query('`Jrn. No.`!="000003862"') # Jan 18 correcting journal
    x=x.query('`Jrn. No.`!="000003939"') # Jan 18 correcting journal
    x=x.query('`Jrn. No.`!="000003861"') # Jan 18 correcting journal
    x=x.query('`Jrn. No.`!="000003932"') # Jan 18 correcting journal
    x['day']=1
    x['date']=pd.to_datetime(x[['year','month','day']],infer_datetime_format=True)
    # x['calendar_month']=x['Per.'].map({1:9,2:10,3:11,4:12,5:1,6:2,7:3,8:4,9:5,10:6,11:7,12:8,19:8})
    # x['calendar_year'] = np.where((x['Per.'] > 4.1), x['Yr.'], x['Yr.']-1)
    x_1=x.join(x['Employee'].str.split(' ', expand=True).rename(columns={0:'EE',1:'Name_EE'}))
    x_1['Employee - Ext. Code']=x_1['EE']

    return x_1


NL_Data_21=nl_raw_clean_file(cached_2021,coding_acc_schedule) # MUTATION
NL_Data_20=nl_raw_clean_file(cached_2020,coding_acc_schedule) # MUTATION
# NL_Data_19=nl_raw_clean_file(cached_2019,coding_acc_schedule)
# NL_Data_18=nl_raw_clean_file(cached_2018,coding_acc_schedule)
# NL_Data_17=nl_raw_clean_file(cached_2017,coding_acc_schedule)
# NL_Data_16=nl_raw_clean_file(cached_2016,coding_acc_schedule)
# NL_Data_15=nl_raw_clean_file(cached_2015,coding_acc_schedule)
# NL_Data_14=nl_raw_clean_file(cached_2014,coding_acc_schedule)

# st.write(NL_Data_19.head())

# consol_headcount_data=pd.concat([NL_Data_19,NL_Data_20,NL_Data_21],ignore_index=True)
# consol_headcount_data=pd.concat([NL_Data_14,NL_Data_15,NL_Data_16,NL_Data_17,NL_Data_18,NL_Data_19,NL_Data_20,NL_Data_21],ignore_index=True)
consol_headcount_data=pd.concat([NL_Data_20,NL_Data_21],ignore_index=True)


# cleaned_data=clean_wrangle_headcount(consol_headcount_data)

def headcount_paye_account(data):
    # Using 
    x=data.query('(`Account Code`=="909-0210")')
    journal_list = x['Jrn. No.'].unique()
    filter_paye=data['Jrn. No.'].isin(journal_list)
    data['filtered_paye_headcount'] = data['Jrn. No.'].where(filter_paye)
    data=data[data['filtered_paye_headcount'].notna()]
    return data.query('(`Account Code`=="921-0500") or (`Account Code`=="940-0500")').loc[:,
    ['Journal Amount','Employee','Src. Account','Jrn. No.','year','month','date','Project','Employee - Ext. Code',
    'Acc_Schedule','Project_Name','Department','Description']]

# st.write('PAYE Journal data')
headcount_paye=headcount_paye_account(consol_headcount_data)
# st.write(headcount_paye_account(consol_headcount_data))

def bbf_employees(x):
    x['Employee - Ext. Code'] = pd.to_numeric(x['Employee - Ext. Code'])
    x= x.query('`Employee - Ext. Code`>0.5')
    x = x.query('`Src. Account`!="BUK02"')
    x['Payroll_Amt'] = x.groupby (['year','month','Employee - Ext. Code','Jrn. No.'])['Journal Amount'].transform('sum')
    x['Headcount'] = x['Journal Amount'] / x['Payroll_Amt']
    x=x.replace([np.inf, -np.inf], np.nan) # due to 0 dividing by the journal amount
    x['Category']='BBF'
    x['Headcount']=pd.to_numeric(x['Headcount'])
    return x

bbf_headcount_data=bbf_employees(headcount_paye)
# st.write('to check Jan 18 headcount looks wrong')
# st.write(bbf_headcount_data.head())
# st.write( bbf_headcount_data[(bbf_headcount_data['year']==2018) & (bbf_headcount_data['month']==7) & (bbf_headcount_data['Employee'].str.contains('Cornally')) ] )
# st.write( bbf_headcount_data[(bbf_headcount_data['year']==2018) ] )
# st.write( bbf_headcount_data[(bbf_headcount_data['year']==2018) & (bbf_headcount_data['month']==1) & (bbf_headcount_data['Employee'].str.contains('Higgins')) ] )

def pivot_report(bbf_headcount_data,filter='Employee'):
    summary= pd.pivot_table(bbf_headcount_data, values='Headcount',index=[filter], columns=['date'],margins=True,aggfunc='sum',fill_value=0)
    summary = summary.sort_values(by=['All'],ascending=False)
    return summary.reset_index().set_index(filter)

# st.write('paye data')
with st.beta_expander('BBF Staff by Employee by Month'):
    bbf_pivot=pivot_report(bbf_headcount_data,filter='Employee')
    st.write(bbf_pivot)
# david = headcount_paye[ (headcount_paye['Employee'].str.contains('Camle') &( headcount_paye['month']==12) &( headcount_paye['year']==2018) ) ]
# st.write(david)

def clean_wrangle_headcount(data):
    x=data.query('(`Account Code`=="921-0500") or (`Account Code`=="940-0500")').loc[:,
    ['Journal Amount','Employee','Src. Account','Jrn. No.','year','month','date','Project','Employee - Ext. Code',
    'Acc_Schedule','Project_Name','Department','Description']]
    x=x.query('`Jrn. No.`!="000007362"') # Accrual made in march '21 which has UK employee numbers
    x=x.query('`Jrn. No.`!="X00007362"') # reversal of above accrual
    x=x.query('`Jrn. No.`!="000007470"') # pension might need to fix in may will see
    x=x.query('`Jrn. No.`!="000007465"') # pension might need to fix in may will see
    x['month']=np.where(x['Jrn. No.']=='9SM-BBF146', 3, x['month'])
    x['month']=np.where(x['Jrn. No.']=='9SM-BBF144', 1, x['month'])
    x['month']=np.where(x['Jrn. No.']=='9SM-BBF142', 12, x['month'])
    x['year']=np.where(x['Jrn. No.']=='9SM-BBF142', 20, x['year'])
    x['month']=np.where(x['Jrn. No.']=='9SM-BBF141', 11, x['month'])
    x['year']=np.where(x['Jrn. No.']=='9SM-BBF141', 20, x['year'])
    x['month']=pd.to_numeric(x['month'])
    x=x.query('`Jrn. No.`!="9SM-BBF1CN"') # J Reeves credit note and invoice
    x=x.query('`Jrn. No.`!="9SMBBF139"') # J Reeves credit note and invoice
    x=x.query('`Jrn. No.`!="000007163"') # Malcolm vanA reclass
    x=x.query('`Jrn. No.`!="000007208"') # Malcolm vanA deposit
    x=x.query('`Jrn. No.`!="000007459"') # Luke reclass in April 21 from IT to Pipeline
    x=x.query('`Jrn. No.`!="BUK00009IN"')
    x=x.query('`Jrn. No.`!="BUK00009CN"')
    
    return x

cleaned_data=clean_wrangle_headcount(consol_headcount_data)

def mauve_staff(x):
    group_supplier=x.groupby(['Src. Account','Jrn. No.','year','month','Project','Acc_Schedule',
    'Project_Name','Department','Description','date'])['Journal Amount'].sum().reset_index()
    # group_UK = x.query('`Src. Account`=="BUK02"')
    mauve = group_supplier.query('`Src. Account`!="BUK02"')
    # credit_filter=(mauve['Jrn. No.'].str.contains('CN')) or (mauve['Jrn. No.'].str.contains('CR'))
    credit_filter=(mauve['Jrn. No.'].str.contains('CN'))
    credit_filter_cr=(mauve['Jrn. No.'].str.contains('CR'))
    filter_bbf_recharge=(mauve['Jrn. No.'].str.contains('BBF'))
    mauve['credit_notes']=mauve['Jrn. No.'].where(credit_filter)
    mauve=mauve[mauve['credit_notes'].isna()]
    mauve['credit_notes']=mauve['Jrn. No.'].where(credit_filter_cr)
    mauve=mauve[mauve['credit_notes'].isna()]
    mauve['credit_notes']=mauve['Jrn. No.'].where(filter_bbf_recharge)
    mauve=mauve[mauve['credit_notes'].isna()]
    # st.write(mauve[mauve['Jrn. No.'].str.contains('CR')])
    # Mauve_2021=credit_notes_resolve(group_no_UK).reset_index()
    mauve['Payroll_Amt'] = mauve.groupby (['Jrn. No.'])['Journal Amount'].transform('sum')
    mauve['Headcount'] = mauve['Journal Amount'] / mauve['Payroll_Amt']
    mauve['Category']='Mauve'
    # mauve = headcount_date_clean(Mauve_2021)
    return mauve

mauve=mauve_staff(cleaned_data)
# st.write(mauve)

mauve_pivot=pivot_report(mauve,filter='Jrn. No.')
# st.write(mauve[(mauve['month']==7) & (mauve['year']==2020)] )
with st.beta_expander('Mauve Staff by Invoice Number by Month'):
    st.write(mauve_pivot)
    st.write('to check that only invoices from mauve are included',mauve[mauve['Src. Account']=='']) # to check that only invoices from suppliers are included, don't want journals included

group_UK = cleaned_data.query('`Src. Account`=="BUK02"')
# st.write(group_UK[(group_UK['month']==12) & (group_UK['year']==2020)] )
# st.write(group_UK[group_UK['Description'].str.contains('BBF UK recharge for Leigh Fieldhouse Payroll April 20')])
# st.write(group_UK[group_UK['Jrn. No.'].str.contains('000914')])
group_UK['Payroll_Amt'] = group_UK.groupby (['Jrn. No.','Description'])['Journal Amount'].transform('sum')
group_UK['Headcount'] = group_UK['Journal Amount'] / group_UK['Payroll_Amt']
# group_UK['month']=np.where(group_UK['Jrn. No.']=='BUK0000979', 3, group_UK['month'])
group_UK['Category']='BBF_UK'
group_UK['Headcount']=pd.to_numeric(group_UK['Headcount'])
uk_pivot=pivot_report(group_UK,filter='Description')
with st.beta_expander('UK Staff by Description by Month'):
    st.write(uk_pivot)

with st.beta_expander('Totals by location by month'):
    uk_pivot_data=uk_pivot.reset_index()
    summary=pd.concat([uk_pivot.loc['All'],mauve_pivot.loc['All'],bbf_pivot.loc['All']],axis=1)
    summary.columns=['uk','mauve','bbf']
    summary['total']=summary.sum(axis=1)
    summary=summary.reset_index()
    summary = summary[summary['date']!='All']
    # st.write(summary)
    summary['date']=pd.to_datetime(summary['date'])
    graphing_location_dept = summary.drop('total',axis=1).copy()
    # st.write('graphing data', graphing_location_dept)
    summary=summary.set_index('date').sort_index(ascending=False)
    st.write(summary.style.format("{:,.0f}"))
    test_test=summary.drop('total',axis=1).copy()
    test_melt = pd.melt(test_test,var_name='location',value_name='headcount',ignore_index=False).reset_index()
    # st.write(test_melt)

    selection_3 = alt.selection_multi(fields=['location'], bind='legend')
    scale_3=alt.Scale(domain=['bbf','mauve','uk'],range=['blue','red','lime'])
    test_run_3=alt.Chart(test_melt).mark_area().encode(
    alt.X('yearmonth(date):T', axis=alt.Axis(title='date',labelAngle=90)),
    alt.Y('headcount:Q'),
    color=alt.Color('location:N',scale=scale_3,sort=alt.SortField("location", "descending")),order="location:O",
    opacity=alt.condition(selection_3, alt.value(1), alt.value(0.1)))
    overlay = pd.DataFrame({'headcount': [300]})
    vline = alt.Chart(overlay).mark_rule(color='black', strokeWidth=2).encode(y='headcount:Q')
    updated_test_chart = alt.layer(test_run_3,vline)
    # rule = test_run_3.mark_rule(color="black",strokeWidth=3).encode(y=300)

    st.write('Select and press shift to highlight locations')
    # st.altair_chart((test_run_3).add_selection(selection_3),use_container_width=True)

    st.altair_chart((updated_test_chart).add_selection(selection_3),use_container_width=True)




# st.write(summary.style.format("{:,.0f}"))

with st.beta_expander('Actuals by Dept'):
    # st.write('Overall Headcount to date broken down by Department',bbf_headcount_data.head(5))
    # st.write('mauve', mauve.head(5))
    # st.write('uk', group_UK.head(5))
    headcount_combined=pd.concat([bbf_headcount_data.reset_index().drop('index',axis=1),mauve.reset_index().drop('index',axis=1),
    group_UK.reset_index().drop('index',axis=1)])
    dept_pivot=pivot_report(headcount_combined,filter='Department')
    st.write(dept_pivot.style.format("{:,.1f}"))



    # headcount_combined_test=headcount_combined.reset_index().reset_index()
    # st.write(headcount_combined_test.head())
    headcount_combined_test=headcount_combined.reset_index().reset_index().rename(columns={'level_0':'id_tracker'}).drop('index',axis=1)

    # st.write('first',headcount_combined_test)
    # st.write('data for graph??',headcount_combined_test[headcount_combined_test['Employee']==' '])
    # st.write('data for graph??',headcount_combined_test[headcount_combined_test['Employee'].isnull()])
    
    headcount_combined_test['Employee']=headcount_combined_test['Employee'].replace(' ',np.nan)
    headcount_combined_test['Employee']=headcount_combined_test['Employee'].fillna(headcount_combined_test['Description'])

    # st.write('last',headcount_combined_test)
    staff_dept_pivot=summary= pd.pivot_table(headcount_combined_test, values='Headcount',index=['Department','Employee'],
    columns=['date'],margins=True,aggfunc='sum',fill_value=0)

    option=st.selectbox('Select',options=('TV','CG','Post','Admin','HR','IT','Pipeline','Development'),index=3)
    st.write('Below is Department Detail headcount')
    st.write(staff_dept_pivot.loc[option])

    def data_for_graphing_dept(x, select_level):
        return x.unstack(level=select_level).reset_index().rename(columns={0:'headcount'}).set_index('date').drop(['All'])\
        .reset_index().set_index(select_level).drop(['All']).reset_index()

    graph_data=data_for_graphing_dept(dept_pivot,select_level='Department')
    test_data={'Department':['TV','CG','Post','Admin','HR','IT','Pipeline','Development']} # CUSTOM SORTING
    test_df=pd.DataFrame(test_data).reset_index().rename(columns={'index':'order'})
    graph_data=pd.merge(graph_data,test_df,on='Department',how='outer')

    # https://stackoverflow.com/questions/61342355/altair-stacked-area-with-custom-sorting
    # https://altair-viz.github.io/user_guide/customization.html
    # https://vega.github.io/vega/docs/schemes/

    # https://altair-viz.github.io/gallery/stacked_bar_chart_with_text.html

    def chart_area_headcount(x,select_coding,tooltip_selection):
        #.transform_calculate(order="{'TV':0, 'CG': 1,'Post':2,'Admin':3,'HR':4,'IT':5,'Pipeline':6,'Development':7}[datum.Department]")
        return alt.Chart(x).mark_area().encode(
            alt.X('yearmonth(date):T',axis=alt.Axis(title='date',labelAngle=90)),
            y='headcount',
            color=alt.Color(select_coding, legend=alt.Legend(title=select_coding),sort=alt.SortField("order", "ascending"),scale=alt.Scale(scheme='tableau10')),
            # order=alt.Order('Department', sort=['TV', 'CG', 'Post', 'Admin', 'IT', 'HR', 'Pipeline','Development']),
            tooltip=tooltip_selection,
            order="order:O",
        )
    st.altair_chart(chart_area_headcount(x=graph_data,select_coding='Department',tooltip_selection='headcount'),use_container_width=True)

    # Couldn't get labels to work properly
    # https://github.com/altair-viz/altair/issues/921
    # chart_power=alt.Chart(graph_data).mark_area().encode(
    #         alt.X('yearmonth(date):T',axis=alt.Axis(title='date',labelAngle=90)),y='headcount',
    #         color=alt.Color('Department', sort=alt.SortField("order", "ascending"),
    #         scale=alt.Scale(domain=['CG', 'Post', 'Admin', 'IT', 'HR'],range=['red','green'])),
    #         order="order:O")
    # # text=chart_power.mark_text().encode(text=alt.Text('Department:N'),order="order:O",color=alt.value('black'))
    # st.altair_chart(chart_power,use_container_width=True)

def forecast_headcount_function(x,start_forecast_period_resourcing_tool,drop_column,keep_column):
    x.columns= x.columns.astype(str)
    col = x.pop("Department")
    x.insert(x.columns.get_loc('Project') + 1, col.name, col)
    sliced_x=x.loc[:,start_forecast_period_resourcing_tool:]
    sliced_x = sliced_x.drop(columns=[drop_column])
    sliced_x=sliced_x.set_index(keep_column).unstack(level=keep_column).reset_index().rename(columns={'level_0':'date',0:'headcount'})
    sliced_x=sliced_x.groupby([keep_column,'date'])['headcount'].sum().reset_index()
    x = pd.pivot_table(sliced_x, values='headcount',index=[keep_column], columns=['date'],fill_value=0)
    return x

# st.write('before function',forecast_resourcing)
with st.beta_expander('Dept: Actual + Forecast'):
    # st.write('resourcing tool export',forecast_resourcing.head())
    # st.write('project codes',forecast_project_mapping.head())

    x= pd.merge(forecast_resourcing,forecast_project_mapping,on='Project',how='outer').drop('Project',axis=1).rename(columns={'Project_name':'Project','Division':'Department'})
    # st.write('after merge',x.head())
        # st.write('this is wierd x thing', x.head())

    forecast_headcount=forecast_headcount_function(x,start_forecast_period_resourcing_tool,drop_column='Project',keep_column='Department')
    # st.write('this is formula result',forecast_headcount.head())

    def headcount_actual_plus_forecast(actual_headcount,forecast_headcount):
        actual=actual_headcount.drop('All',axis=1).drop(['All'])
        return pd.concat([actual,forecast_headcount],axis=1).ffill(axis=1)

    def headcount_actual_plus_forecast_with_subtotal(merged):
        merged.loc['All']= merged.sum(numeric_only=True, axis=0)
        merged.loc[:,'All'] = merged.sum(numeric_only=True, axis=1)
        return merged.sort_values(by='All',ascending=False)

    total_headcount_no_subtotal=headcount_actual_plus_forecast(actual_headcount=dept_pivot,forecast_headcount=forecast_headcount)
    total_headcount_with_subtotal=headcount_actual_plus_forecast_with_subtotal(total_headcount_no_subtotal)
    st.write(total_headcount_with_subtotal.style.format("{:,.1f}"))

    graph_data_1=data_for_graphing_dept(total_headcount_with_subtotal,select_level='Department')
    test_data_1={'Department':['TV','CG','Post','Admin','HR','IT','Pipeline','Development']}
    test_df_1=pd.DataFrame(test_data_1).reset_index().rename(columns={'index':'order'})
    graph_data_1=pd.merge(graph_data_1,test_df_1,on='Department',how='outer')
    base=chart_area_headcount(x=graph_data_1,select_coding='Department',tooltip_selection='headcount')
    st.altair_chart(base,use_container_width=True)

    selection_4 = alt.selection_multi(fields=['Department'], bind='legend')
    # scale_4=alt.Scale(domain=['bbf','mauve','uk'],range=['blue','red','lime'])
    test_run_4=alt.Chart(graph_data_1).mark_area().encode(
    alt.X('yearmonth(date):T',axis=alt.Axis(title='date',labelAngle=90)),
    alt.Y('headcount:Q'),
    color=alt.Color('Department:N',sort=alt.SortField("order", "descending"),scale=alt.Scale(scheme='tableau10')),
    order="order:O",
    opacity=alt.condition(selection_4, alt.value(1), alt.value(0.1)))
    overlay = pd.DataFrame({'headcount': [300]})
    vline = alt.Chart(overlay).mark_rule(color='black', strokeWidth=2).encode(y='headcount:Q')
    updated_test_chart_1 = alt.layer(test_run_4,vline)
    st.write('Select and press shift to highlight Departments')
    st.altair_chart((updated_test_chart_1).add_selection(selection_4),use_container_width=True)


with st.beta_expander('Actuals by Project for 921'):
    # st.write(headcount_combined[headcount_combined['Acc_Schedule']==921])
    headcount_921_actual_date=headcount_combined[headcount_combined['Acc_Schedule']==921].copy()
    # st.write(headcount_921_actual_date[headcount_921_actual_date['Category'].isna()])
    proj_pivot_921_actual = pivot_report(headcount_921_actual_date,filter='Project')
    st.write(proj_pivot_921_actual.style.format("{:,.1f}"))
    
    project_graph_data=data_for_graphing_dept(proj_pivot_921_actual,select_level='Project')
    # st.write('data for graph',project_graph_data.head())
    # st.altair_chart(chart_area_headcount(x=project_graph_data,select_coding='Project',tooltip_selection='Project'),use_container_width=True)

    project_graph_data['SUBANALYSIS 0'] = project_graph_data['Project'].str[:8]
    project_codes_merge=Project_codes.loc[:,['SUBANALYSIS 0','Description','client','showrunner','project_all_seasons']]
    project_codes_merge['SUBANALYSIS 0']=project_codes_merge['SUBANALYSIS 0'].str.strip()
    project_graph_data['SUBANALYSIS 0']=project_graph_data['SUBANALYSIS 0'].str.strip()
    project_graph_data_all = pd.merge(project_graph_data,project_codes_merge,on='SUBANALYSIS 0',how='left')
    project_graph_data_updated=project_graph_data_all.loc[:,['date','headcount','client','Description']].rename(columns={'Description':'Project','headcount':'Headcount'})
    # st.write(project_graph_data_updated)
    group_client_data=pivot_report(project_graph_data_updated,filter='client')
    # st.write(group_client_data)
    group_client_data=data_for_graphing_dept(group_client_data,select_level='client')
    st.altair_chart(chart_area_headcount(x=group_client_data,select_coding='client',tooltip_selection='client'),use_container_width=True)

    project_graph_data_showrunner=project_graph_data_all.loc[:,['date','headcount','showrunner','Description']].rename(columns={'Description':'Project','headcount':'Headcount'})
    group_client_data_1=pivot_report(project_graph_data_showrunner,filter='showrunner')
    group_client_data_1=data_for_graphing_dept(group_client_data_1,select_level='showrunner')
    st.altair_chart(chart_area_headcount(x=group_client_data_1,select_coding='showrunner',tooltip_selection='showrunner'),use_container_width=True)

    project_graph_descrip=project_graph_data_all.loc[:,['date','headcount','project_all_seasons']].rename(columns={'project_all_seasons':'Project','headcount':'Headcount'})
    group_client_data_1=pivot_report(project_graph_descrip,filter='Project')
    group_client_data_1=data_for_graphing_dept(group_client_data_1,select_level='Project')
    st.altair_chart(chart_area_headcount(x=group_client_data_1,select_coding='Project',tooltip_selection='Project'),use_container_width=True)


# st.write(x)
with st.beta_expander('Project: Actual + Forecast'):
    # st.write(x.head())
    forecast_headcount_project=forecast_headcount_function(x,start_forecast_period_resourcing_tool,drop_column='Department',keep_column='Project')
    # st.write('this is formula result',forecast_headcount_project)

    project_headcount_no_subtotal=headcount_actual_plus_forecast(actual_headcount=proj_pivot_921_actual,forecast_headcount=forecast_headcount_project)
    project_headcount_with_subtotal=headcount_actual_plus_forecast_with_subtotal(project_headcount_no_subtotal)
    st.write(project_headcount_with_subtotal.style.format("{:,.1f}"))
    project_graph_data_actual_forecast_1=data_for_graphing_dept(project_headcount_with_subtotal,select_level='Project')
    project_graph_data_actual_forecast_1['SUBANALYSIS 0'] = project_graph_data_actual_forecast_1['Project'].str[:8]
    project_graph_data_actual_forecast_1['SUBANALYSIS 0']=project_graph_data_actual_forecast_1['SUBANALYSIS 0'].str.strip()
    # st.write('project graph data',project_graph_data_actual_forecast_1)
    # st.write('project codes merge spreadsheet',project_codes_merge)

    project_graph_data_all_1 = pd.merge(project_graph_data_actual_forecast_1,project_codes_merge,on='SUBANALYSIS 0',how='left')
    # st.write('test 1',project_graph_data_all_1)
    project_graph_data_updated_1=project_graph_data_all_1.loc[:,['date','headcount','client','Description']].rename(columns={'Description':'Project','headcount':'Headcount'})
    # st.write('test 2',project_graph_data_updated_1)
    group_client_data_1=pivot_report(project_graph_data_updated_1,filter='client')
    # st.write('test 3',group_client_data)
    group_client_data_1=data_for_graphing_dept(group_client_data_1,select_level='client')
    st.altair_chart(chart_area_headcount(x=group_client_data_1,select_coding='client',tooltip_selection='client'),use_container_width=True)

    project_graph_descrip_1=project_graph_data_all_1.loc[:,['date','headcount','project_all_seasons']].rename(columns={'project_all_seasons':'Project','headcount':'Headcount'})
    group_client_data_2=pivot_report(project_graph_descrip_1,filter='Project')
    group_client_data_2=data_for_graphing_dept(group_client_data_2,select_level='Project')
    st.altair_chart(chart_area_headcount(x=group_client_data_2,select_coding='Project',tooltip_selection='Project'),use_container_width=True)
    # project_names=["Doc McStuffins","Vampirina",""]

    st.write('Headcount by shows that have Chris Nee as showrunner/creator')
    project_graph_data_showrunner_1=project_graph_data_all_1.loc[:,['date','headcount','showrunner','Description']].rename(columns={'Description':'Project','headcount':'Headcount'})
    group_client_data_3=pivot_report(project_graph_data_showrunner_1,filter='showrunner')
    group_client_data_3=data_for_graphing_dept(group_client_data_3,select_level='showrunner')
    st.altair_chart(chart_area_headcount(x=group_client_data_3,select_coding='showrunner',tooltip_selection='showrunner'),use_container_width=True)



with st.beta_expander('Actuals split by 921/940'):
    acc_sch_pivot=pivot_report(headcount_combined,filter='Acc_Schedule')
    # st.write(acc_sch_pivot.reset_index().head())
    # st.write(acc_sch_pivot.style.format("{:,.1f}"))
    # st.write('check the ratio of overhead staff to direct headcount')
    graph_data_2=data_for_graphing_dept(acc_sch_pivot,select_level='Acc_Schedule')
    graph_data_2['Acc_Schedule']=graph_data_2['Acc_Schedule'].astype(str)
    # st.write(graph_data_2.head())
    base_1=chart_area_headcount(x=graph_data_2,select_coding='Acc_Schedule',tooltip_selection='headcount')
    # st.altair_chart(base_1,use_container_width=True)
    
    data_clean=acc_sch_pivot.reset_index()
    data_clean['Acc_Schedule']=data_clean['Acc_Schedule'].astype(str)
    data_clean=data_clean.set_index('Acc_Schedule')
    # st.write(data_clean)
    data_clean.loc['% Overhead'] = data_clean.loc['940.0'] / data_clean.loc['All']
    st.write(data_clean.style.format("{:,.2f}"))
    graph_data_3=data_for_graphing_dept(data_clean,select_level='Acc_Schedule')
    graph_data_3=graph_data_3[graph_data_3['Acc_Schedule']=='% Overhead'].drop('Acc_Schedule',axis=1).copy()
    # st.write(graph_data_3)
    line = alt.Chart(graph_data_3).mark_line().encode(alt.X('yearmonth(date):T',axis=alt.Axis(title='date',labelAngle=90)),
    alt.Y('headcount'),color=alt.value("lime"))
    # https://www.w3schools.com/cssref/css_colors.asp
    # st.altair_chart(line,use_container_width=True)
    dual=alt.layer(base_1, line).resolve_scale(y = 'independent')
    st.altair_chart(dual,use_container_width=True)



with st.beta_expander('Actual Direct Headcount from Month 1 to Month End to compare productions from Month 1'):
    def create_pivot_comparing_production_headcount(shifted_df):
        shifted_df=shifted_df.drop('All',axis=1).drop(['All'])
        shifted_df.columns = np.arange(len(shifted_df.columns))
        shifted_df=shifted_df.replace(0,np.NaN)
        return shifted_df.apply(lambda x: pd.Series(x.dropna().values), axis=1).fillna(0)
    data_month_1=create_pivot_comparing_production_headcount(proj_pivot_921_actual)
    # st.write(data_month_1.style.format("{:,.0f}",na_rep="-"))

    data_month_2=create_pivot_comparing_production_headcount(project_headcount_no_subtotal)
    data_month_2['Total']=data_month_2.sum(axis=1)
    data_month_2=data_month_2.sort_values(by='Total',ascending=False)
    st.write(data_month_2.style.format("{:,.0f}",na_rep="-"))
    # st.write(data_month_2.reset_index())
    filter_projects = data_month_2.iloc[:22,:].copy()
    
    # graph_data_4=data_for_graphing_dept(filter_top_10,select_level='Project')
    def clean_pivot(filter_projects):
        return filter_projects.unstack().reset_index().rename(columns={0:'headcount','level_0':'date'}).set_index('date').drop(['Total']).reset_index()
    filter_projects=clean_pivot(filter_projects)
    filter_projects['headcount']=filter_projects['headcount'].replace(0,np.NaN)
    # st.write(filter_projects)
    

    line_chart = alt.Chart(filter_projects).mark_line(interpolate='basis').encode(alt.X('date',axis=alt.Axis(title='date')),
    alt.Y('headcount'),color=alt.Color('Project:N'))
    # st.altair_chart(line_chart,use_container_width=True)

    # https://altair-viz.github.io/gallery/multiline_tooltip.html

    nearest = alt.selection(type='single', nearest=True, on='mouseover',fields=['date'], empty='none')
    line_sel = alt.Chart(filter_projects).mark_line(interpolate='basis').encode(x='date:Q',y='headcount:Q',color='Project:N')
    selectors = alt.Chart(filter_projects).mark_point().encode(x='date:Q',opacity=alt.value(0)).add_selection(nearest)
    points = line_sel.mark_point().encode(opacity=alt.condition(nearest, alt.value(1), alt.value(0)))
    text = line_sel.mark_text(align='left', dx=5, dy=-5).encode(text=alt.condition(nearest, 'Project:N', alt.value(' ')))
    rules = alt.Chart(filter_projects).mark_rule(color='gray').encode(x='date:Q').transform_filter(nearest)
    updated_chart = alt.layer(line_sel, selectors, points, rules, text)
    st.write('This puts a line over graph which selects the data points')
    st.altair_chart(updated_chart,use_container_width=True)

    sequels=["1-Z-149 Vampirina","1-Z-181 Vampirina 2","1-Z-197 Vampirina 3","1-Z-144 Doc McStuffins IV",'1-Z-179 Doc McStuffins 5',
            '1-Z-213 Ryder Jones',"1-Z-203 Ridley Jones 2","1-Z-217 Twisty","1-Z-227 Twisty 2",
            "1-Z-163 Karma's World","1-Z-781 KarmasWorld2"]
    sequel_filter=clean_pivot(data_month_2.loc[sequels,:].copy())
    sequel_filter['headcount']=sequel_filter['headcount'].replace(0,np.NaN)

    # highlight = alt.selection(type='single', on='mouseover',fields=['Project'], nearest=True)
    # base=alt.Chart(sequel_filter).encode(
    #         alt.X('date:Q'),y='headcount:Q',color=alt.Color('Project:N',
    #         scale=alt.Scale(domain=sequels,range=['red','red','red','black','black','lime','lime','blue','blue','orange','orange']))
    #         )
    # points = base.mark_circle().encode(opacity=alt.value(0)).add_selection(highlight)
    # lines = base.mark_line().encode(size=alt.condition(~highlight, alt.value(1), alt.value(3)))
    # st.write('This highlights a line on graph when you hover mouse over it')
    # st.altair_chart(points+lines,use_container_width=True)

    # https://stackoverflow.com/questions/65226756/altair-layered-line-chart-with-legend-and-custom-colors
    # https://altair-viz.github.io/gallery/interactive_legend.html
    st.write('Please shift to select multiple lines for multiple season Productions')
    selection_1 = alt.selection_multi(fields=['Project'], bind='legend')
    scale=alt.Scale(domain=sequels,range=['red','red','red','black','black','lime','lime','blue','blue','orange','orange'])
    test_run=alt.Chart(sequel_filter).mark_line().encode(
    alt.X('date:Q', axis=alt.Axis(domain=False, tickSize=0)),
    alt.Y('headcount:Q'),
    color=alt.Color('Project:N',scale=scale),
    opacity=alt.condition(selection_1, alt.value(1), alt.value(0.1)))
    st.altair_chart(test_run.add_selection(selection_1),use_container_width=True)

    list_projects=["1-Z-149 Vampirina","1-Z-181 Vampirina 2","1-Z-197 Vampirina 3","1-Z-128 Doc McStuffins III","1-Z-144 Doc McStuffins IV",'1-Z-179 Doc McStuffins 5',
    '1-Z-213 Ryder Jones',"1-Z-203 Ridley Jones 2","1-Z-217 Twisty","1-Z-227 Twisty 2","1-Z-163 Karma's World","1-Z-781 KarmasWorld2",
    "1-Z-111 Angela's Christmas","1-Z-212 Angela's Wishes",
    "1-Z-249 Eva the Owlet (Tree)",
    "1-Z-211 Friends in Oz","1-Z-233 O.G (previously Otis)",'1-Z-209 Eureka','1-Z-155 Butterbean Bakery',"1-Z-196 Chico Bon Bon",
    "1-Z-175 Stinky & Dirty 2","1-Z-195 Bing Bunny 4","1-Z-255 The Worry Monster","1-Z-107 Octo IV","1-Z-185 Ladybird Lu (Ladybird Dot)"]

    # data_filtered = data_month_2.reset_index().loc[data_month_2['Project'].isin(list_projects)]
    filter_projects_updated=clean_pivot(data_month_2)
    filter_projects_updated['headcount']=filter_projects_updated['headcount'].replace(0,np.NaN)
    # st.write(filter_projects_updated)
    data_filtered = filter_projects_updated.loc[filter_projects_updated['Project'].isin(list_projects)]


    selection_2 = alt.selection_multi(fields=['Project'], bind='legend')
    scale_2=alt.Scale(domain=list_projects,range=['red','red','red','black','black','black','lime','lime','blue','blue','orange','orange','purple','purple',
    'grey','grey','grey','grey','grey','grey','grey','grey','grey','grey','grey'])
    test_run_2=alt.Chart(data_filtered).mark_line().encode(
    alt.X('date:Q', axis=alt.Axis(domain=False, tickSize=0)),
    alt.Y('headcount:Q'),
    color=alt.Color('Project:N',scale=scale_2),
    opacity=alt.condition(selection_2, alt.value(1), alt.value(0.1)))
    st.write('Select and press shift to highlight Productions - All')
    st.altair_chart(test_run_2.add_selection(selection_2),use_container_width=True)



with st.beta_expander('Trying out echarts'):
    # with open("https://github.com/andfanilo/streamlit-echarts-demo/blob/master/data/life-expectancy-table.json") as f:
    #     raw_data = json.load(f)
    # countries = [
    #     "Finland",
    #     "France",
    #     "Germany",
    #     "Iceland",
    #     "Norway",
    #     "Poland",
    #     "Russia",
    #     "United Kingdom",
    # ]

    # datasetWithFilters = [
    #     {
    #         "id": f"dataset_{country}",
    #         "fromDatasetId": "dataset_raw",
    #         "transform": {
    #             "type": "filter",
    #             "config": {
    #                 "and": [
    #                     {"dimension": "Year", "gte": 1950},
    #                     {"dimension": "Country", "=": country},
    #                 ]
    #             },
    #         },
    #     }
    #     for country in countries
    # ]

    # seriesList = [
    #     {
    #         "type": "line",
    #         "datasetId": f"dataset_{country}",
    #         "showSymbol": False,
    #         "name": country,
    #         "endLabel": {
    #             "show": True,
    #             "formatter": JsCode(
    #                 "function (params) { return params.value[3] + ': ' + params.value[0];}"
    #             ).js_code,
    #         },
    #         "labelLayout": {"moveOverlap": "shiftY"},
    #         "emphasis": {"focus": "series"},
    #         "encode": {
    #             "x": "Year",
    #             "y": "Income",
    #             "label": ["Country", "Income"],
    #             "itemName": "Year",
    #             "tooltip": ["Income"],
    #         },
    #     }
    #     for country in countries
    # ]

    # option = {
    #     "animationDuration": 10000,
    #     "dataset": [{"id": "dataset_raw", "source": raw_data}] + datasetWithFilters,
    #     "title": {"text": "Income in Europe since 1950"},
    #     "tooltip": {"order": "valueDesc", "trigger": "axis"},
    #     "xAxis": {"type": "category", "nameLocation": "middle"},
    #     "yAxis": {"name": "Income"},
    #     "grid": {"right": 140},
    #     "series": seriesList,
    # }
    # st_echarts(options=option, height="600px")

    options_1 = {
        "title": {"text": "headcount by dept"},
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "cross", "label": {"backgroundColor": "#6a7985"}},
        },
        "legend": {"data": ["TV", "CG", "视频广告", "直接访问", "搜索引擎"]},
        "toolbox": {"feature": {"saveAsImage": {}}},
        "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
        "xAxis": [
            {
                "type": "category",
                "boundaryGap": False,
                "data": ["2015", "2016", "2017", "2018", "2019", "2020", "2021"],
            }
        ],
        "yAxis": [{"type": "value"}],
        "series": [
            {
                "name": "TV",
                "type": "line",
                "stack": "headcount",
                "areaStyle": {},
                "emphasis": {"focus": "series"},
                "data": [120, 132, 101, 134, 90, 230, 210],
            },
            {
                "name": "CG",
                "type": "line",
                "stack": "headcount",
                "areaStyle": {},
                "emphasis": {"focus": "series"},
                "data": [220, 182, 191, 234, 290, 330, 310],
            },
            {
                "name": "视频广告",
                "type": "line",
                "stack": "headcount",
                "areaStyle": {},
                "emphasis": {"focus": "series"},
                "data": [150, 232, 201, 154, 190, 330, 410],
            },
            {
                "name": "直接访问",
                "type": "line",
                "stack": "headcount",
                "areaStyle": {},
                "emphasis": {"focus": "series"},
                "data": [320, 332, 301, 334, 390, 330, 320],
            },
            {
                "name": "搜索引擎",
                "type": "line",
                "stack": "headcount",
                "label": {"show": True, "position": "top"},
                "areaStyle": {},
                "emphasis": {"focus": "series"},
                "data": [820, 932, 901, 934, 1290, 1330, 1320],
            },
        ],
    }

    st_echarts(options=options_1, height="400px")

    options_2 = {
        "title": {"text": "折线图堆叠"},
        "tooltip": {"trigger": "axis"},
        "legend": {"data": ["邮件营销", "联盟广告", "视频广告", "直接访问", "搜索引擎"]},
        "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
        "toolbox": {"feature": {"saveAsImage": {}}},
        "xAxis": {
            "type": "category",
            "boundaryGap": False,
            "data": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
        },
        "yAxis": {"type": "value"},
        "series": [
            {
                "name": "邮件营销",
                "type": "line",
                "stack": "总量",
                "data": [120, 132, 101, 134, 90, 230, 210],
            },
            {
                "name": "联盟广告",
                "type": "line",
                "stack": "总量",
                "data": [220, 182, 191, 234, 290, 330, 310],
            },
            {
                "name": "视频广告",
                "type": "line",
                "stack": "总量",
                "data": [150, 232, 201, 154, 190, 330, 410],
            },
            {
                "name": "直接访问",
                "type": "line",
                "stack": "总量",
                "data": [320, 332, 301, 334, 390, 330, 320],
            },
            {
                "name": "搜索引擎",
                "type": "line",
                "stack": "总量",
                "data": [820, 932, 901, 934, 1290, 1330, 1320],
            },
        ],
    }
    st_echarts(options=options_2, height="400px")