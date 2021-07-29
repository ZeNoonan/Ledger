import pandas as pd
import numpy as np
import streamlit as st
import datetime
import altair as alt

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

@st.cache
def load_ledger_data(x):
    return pd.read_csv(x,header=[0,1],thousands=',')

df=load_ledger_data('C:/Users/Darragh/Documents/Python/Work/Data/quarterly_all.csv').copy()
# df=pd.concat([all_dfs],ignore_index=True)
# st.write('this is df all')
df=df.drop('Unnamed: 0_level_1',axis=1,level=1)
# cols_to_move = ['fiscal_year']
# cols_to_move = [('Unnamed: 0_level_0', 'fiscal_year'),('Unnamed: 1_level_0', 'calendar_year'),('Unnamed: 2_level_0', 'quarter'),
# ('Unnamed: 3_level_0', 'date'), ('Unnamed: 4_level_0', 'Account Code'), ('Unnamed: 5_level_0', 'Description'), ('Unnamed: 6_level_0', 'Code'),
#  ('Unnamed: 7_level_0', 'Classification 9SMG'), ('Unnamed: 8_level_0', 'Classification Stats'), ('Unnamed: 9_level_0', 'Sub-Classification Stats')]
# cols = cols_to_move + [col for col in df if col not in cols_to_move]
# df=df[cols]
df=df.rename(columns={"Unnamed: 0_level_0":'fiscal_year',"Unnamed: 1_level_0":'calendar_year',"Unnamed: 2_level_0":'quarter',
"Unnamed: 3_level_0":'date',"Unnamed: 4_level_0":'Account Code',"Unnamed: 5_level_0":'Description',"Unnamed: 5_level_0":'Description',
"Unnamed: 6_level_0":'Code',"Unnamed: 7_level_0":'Classification 9SMG',"Unnamed: 8_level_0":'Classification Stats',
"Unnamed: 9_level_0":'Sub-Classification Stats'},level=0)

df[('acc_sch','acc_sch')]=df[('Account Code','Account Code')].astype(str).str[:3]

cols_to_move = [('fiscal_year', 'fiscal_year'),('calendar_year', 'calendar_year'),('quarter', 'quarter'),
('date', 'date'), ('Account Code', 'Account Code'), ('acc_sch', 'acc_sch'), ('Description', 'Description'), ('Code', 'Code'),
 ('Classification 9SMG', 'Classification 9SMG'), ('Classification Stats', 'Classification Stats'), ('Sub-Classification Stats', 'Sub-Classification Stats')]
cols = cols_to_move + [col for col in df if col not in cols_to_move]
df=df[cols]
df[('date', 'date')]=df[('date', 'date')].replace('31/08/2021','31/08/2020')
# df=df.replace(np.NaN,0)
# https://stackoverflow.com/questions/18470323/selecting-columns-from-pandas-multiindex
st.write('checking below')
st.write((df.columns.get_level_values(0).isin({"TB", "consol_jnl"})))
st.write('use pd to numeric to fix dtypes')
filter_df=(df.loc[:,df.columns.get_level_values(0).isin({"TB", "consol_jnl"})]).apply(pd.to_numeric,errors='coerce')
df['total']=filter_df.sum(axis=1)
# df['new_total']=df.sum(axis=1)
# df['test_total']=df.loc[:,df.columns.get_level_values(0).isin({"TB", "consol_jnl"})].sum(axis=1)
st.write('before errors coerce just check that its ok',df)
st.write('Cannot get sum to work maybe just abandon multiindex or apply pd to numeric to individual columsn to see if that works')
st.write('do not think it has worked')
df[('TB','BBF Irl')]=pd.to_numeric(df[('TB','BBF Irl')],errors='coerce')

# st.write(df.dtypes)


# df.to_csv('C:/Users/Darragh/Documents/Python/Work/Data/quarterly_all_updated.csv')
st.write('all',df)
st.write('filter', filter_df)


quarter_4=df.loc[df[('quarter','quarter')]==4]
st.write('q4',quarter_4)
