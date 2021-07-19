import pandas as pd
import numpy as np
import streamlit as st
import datetime
import altair as alt

st.set_page_config(layout="wide")
st.write('Select start of forecast period below and actual')
with st.echo():
    start_forecast_period_resourcing_tool='2021-06-01 00:00:00'
    data_2021='C:/Users/Darragh/Documents/Python/Work/Data/NL_2021_10.xlsx'
    data_2020='C:/Users/Darragh/Documents/Python/Work/Data/NL_2020.xlsx'
    data_2019='C:/Users/Darragh/Documents/Python/Work/Data/NL_2019.xlsx'
    data_2018='C:/Users/Darragh/Documents/Python/Work/Data/nl_18.xlsx'
    data_2017='C:/Users/Darragh/Documents/Python/Work/Data/nl_17.xlsx'
    data_2016='C:/Users/Darragh/Documents/Python/Work/Data/nl_16.xlsx'
    data_2015='C:/Users/Darragh/Documents/Python/Work/Data/nl_15.xlsx'
    data_2014='C:/Users/Darragh/Documents/Python/Work/Data/nl_14.xlsx'

@st.cache
def load_ledger_data(x):
    return pd.read_excel(x)

forecast_resourcing=load_ledger_data('C:/Users/Darragh/Documents/Python/Work/Data/resource_planner_export_11_06_2021.xlsx')
cached_2021=load_ledger_data(data_2021).copy()
cached_2020=load_ledger_data(data_2020).copy()
cached_2019=load_ledger_data(data_2019).copy()
cached_2018=load_ledger_data(data_2018).copy()
cached_2017=load_ledger_data(data_2017).copy()
cached_2016=load_ledger_data(data_2016).copy()
cached_2015=load_ledger_data(data_2015).copy()
cached_2014=load_ledger_data(data_2014).copy()

with st.echo():
    start_forecast_period_resourcing_tool='2021-07-31 00:00:00'
    forecast_project_mapping=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/Project_Codes_2021_.xlsx', sheet_name='Sheet2')
    coding_acc_schedule = (pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/account_numbers.xlsx')).iloc[:,:3]
    coding_sort=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/account_numbers.xlsx', sheet_name='Sheet2')
    Project_codes=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/Data/Project_Codes_2021_.xlsx').rename(columns = {'User Code' : 'SUBANALYSIS 0'})

with st.beta_expander('check resourcing forecast'):
    st.write('resourcing tool export',forecast_resourcing.head())
    st.write('project codes',forecast_project_mapping.head())
    x= pd.merge(forecast_resourcing,forecast_project_mapping,on='Project',how='outer').drop('Project',axis=1).rename(columns={'Project_name':'Project','Division':'Department'})
    st.write('after merge',x.head())
    def forecast_headcount(x,start_forecast_period_resourcing_tool,drop_column,keep_column):
        x.columns= x.columns.astype(str)
        col = x.pop("Department")
        x.insert(x.columns.get_loc('Project') + 1, col.name, col)
        sliced_x=x.loc[:,start_forecast_period_resourcing_tool:]
        sliced_x = sliced_x.drop(columns=[drop_column])
        sliced_x=sliced_x.set_index(keep_column).unstack(level=keep_column).reset_index().rename(columns={'level_0':'date',0:'headcount'})
        sliced_x=sliced_x.groupby([keep_column,'date'])['headcount'].sum().reset_index()
        x = pd.pivot_table(sliced_x, values='headcount',index=[keep_column], columns=['date'],fill_value=0)
        return x
        # st.write('this is wierd x thing', x.head())

    forecast_headcount=forecast_headcount(x,start_forecast_period_resourcing_tool,drop_column='Project',keep_column='Department')
    st.write('this is formula result',forecast_headcount.head())


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
NL_Data_19=nl_raw_clean_file(cached_2019,coding_acc_schedule)
NL_Data_18=nl_raw_clean_file(cached_2018,coding_acc_schedule)
NL_Data_17=nl_raw_clean_file(cached_2017,coding_acc_schedule)
NL_Data_16=nl_raw_clean_file(cached_2016,coding_acc_schedule)
NL_Data_15=nl_raw_clean_file(cached_2015,coding_acc_schedule)
NL_Data_14=nl_raw_clean_file(cached_2014,coding_acc_schedule)

# st.write(NL_Data_19.head())

# consol_headcount_data=pd.concat([NL_Data_19,NL_Data_20,NL_Data_21],ignore_index=True)
consol_headcount_data=pd.concat([NL_Data_14,NL_Data_15,NL_Data_16,NL_Data_17,NL_Data_18,NL_Data_19,NL_Data_20,NL_Data_21],ignore_index=True)
# consol_headcount_data=pd.concat([NL_Data_20,NL_Data_21],ignore_index=True)


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
    summary=summary.set_index('date').sort_index(ascending=False)
    st.write(summary.style.format("{:,.0f}"))
# st.write(summary.style.format("{:,.0f}"))

with st.beta_expander('Actuals by Dept'):
    # st.write('Overall Headcount to date broken down by Department',bbf_headcount_data.head(5))
    # st.write('mauve', mauve.head(5))
    # st.write('uk', group_UK.head(5))
    headcount_combined=pd.concat([bbf_headcount_data.reset_index().drop('index',axis=1),mauve.reset_index().drop('index',axis=1),group_UK.reset_index().drop('index',axis=1)])
    # st.write('data for graph??',headcount_combined.head())
    dept_pivot=pivot_report(headcount_combined,filter='Department')
    st.write(dept_pivot.style.format("{:,.1f}"))

    def data_for_graphing_dept(x, select_level):
        return x.unstack(level=select_level).reset_index().rename(columns={0:'headcount'}).set_index('date').drop(['All'])\
        .reset_index().set_index(select_level).drop(['All']).reset_index()

    graph_data=data_for_graphing_dept(dept_pivot,select_level='Department')
    test_data={'Department':['TV','CG','Post','Admin','HR','IT','Pipeline','Development']}
    test_df=pd.DataFrame(test_data).reset_index().rename(columns={'index':'order'})
    # st.write(test_df)
    graph_data=pd.merge(graph_data,test_df,on='Department',how='outer')
    # st.write(test_graph_data.tail(10))
    # st.write(graph_data.head(32))
    

    # https://stackoverflow.com/questions/61342355/altair-stacked-area-with-custom-sorting
    # https://altair-viz.github.io/user_guide/customization.html
    # https://vega.github.io/vega/docs/schemes/

    # https://altair-viz.github.io/gallery/stacked_bar_chart_with_text.html

    def chart_area_headcount(x,select_coding,tooltip_selection):
        #.transform_calculate(order="{'TV':0, 'CG': 1,'Post':2,'Admin':3,'HR':4,'IT':5,'Pipeline':6,'Development':7}[datum.Department]")
        return alt.Chart(x).mark_area().encode(
            alt.X('yearmonth(date):T',axis=alt.Axis(title='date',labelAngle=90)),
            y='headcount',
            color=alt.Color(select_coding, sort=alt.SortField("order", "ascending"),scale=alt.Scale(scheme='tableau10')),
            # order=alt.Order('Department', sort=['TV', 'CG', 'Post', 'Admin', 'IT', 'HR', 'Pipeline','Development']),
            tooltip=tooltip_selection,
            order="order:O",
        )
    st.altair_chart(chart_area_headcount(x=graph_data,select_coding='Department',tooltip_selection='headcount'),use_container_width=True)

    # Couldn't get labels to work properly
    # https://github.com/altair-viz/altair/issues/921
    chart_power=alt.Chart(graph_data).mark_area().encode(
            alt.X('yearmonth(date):T',axis=alt.Axis(title='date',labelAngle=90)),y='headcount',
            color=alt.Color('Department', sort=alt.SortField("order", "ascending"),
            scale=alt.Scale(domain=['CG', 'Post', 'Admin', 'IT', 'HR'],range=['red','green'])),
            order="order:O")
    # text=chart_power.mark_text().encode(text=alt.Text('Department:N'),order="order:O",color=alt.value('black'))
    st.altair_chart(chart_power,use_container_width=True)

with st.beta_expander('Actuals split by 921/940'):
    acc_sch_pivot=pivot_report(headcount_combined,filter='Acc_Schedule')
    st.write(acc_sch_pivot.style.format("{:,.1f}"))

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



st.write('next step is to do the domain custom colors by client')
    # project_list = project_graph_data['Project'].unique()
    # st.write(project_list)
    # project_snapshot=proj_pivot_921_actual.loc[:,'All'].reset_index().reset_index().rename(columns={'index':'client'})
    # project_snapshot['client']=''
    # # project_snapshot['client']
    # # project_snapshot.loc['1-Z-155 Butterbean Bakery']='Nickelodeon'
    # st.write(project_snapshot)



with st.beta_expander('Actual Direct Headcount from Month 1 to Month End to compare productions from Month 1'):
    def create_pivot_comparing_production_headcount(shifted_df):
        shifted_df=shifted_df.drop('All',axis=1).drop(['All'])
        shifted_df.columns = np.arange(len(shifted_df.columns))
        shifted_df=shifted_df.replace(0,np.NaN)
        return shifted_df.apply(lambda x: pd.Series(x.dropna().values), axis=1).fillna(0)
    data_month_1=create_pivot_comparing_production_headcount(proj_pivot_921_actual)
    st.write(data_month_1.style.format("{:,.0f}",na_rep="-"))

st.write('add labels to headcount would be good')
# https://altair-viz.github.io/gallery/stacked_bar_chart_with_text.html
# nfl chart

