import pandas as pd
import numpy as np
import streamlit as st
from io import BytesIO
import base64

st.set_page_config(layout="wide")

@st.cache
def youtube(filename,id_file):
    # data=pd.read_excel(filename)
    data=pd.read_csv(filename)
    data['Custom ID']=data['Custom ID'].str.lower()
    master=pd.read_excel(id_file)
    master['Custom ID']=master['Custom ID'].str.lower()
    # st.write('data sum before merge:',data['Partner Revenue'].sum())
    new=data.merge(master,how='left', on='Custom ID')
    # st.write('Partner Revenue after merge:', new['Partner Revenue'].sum())
    new['Show_Season'] = new['New Show Name'].map(str) + " - " + new['New Season']
    new['Territory'] = np.where(new['Country']=='CA', 'CA', np.where(new['New Show ']=='SUPW', '9SUSA', 'INTL'))
    new['Territory'] = np.where(new['New Show Name']=='Peep','CA',new['Territory'])
    return new

@st.cache
def youtube_load(filename):
    # data=pd.read_excel(filename)
    return pd.read_csv(filename)

@st.cache
def youtube_master_filename(filename):
    # data=pd.read_excel(filename)
    return pd.read_excel(filename)

@st.cache
def merge_files(data,master):
    master['Custom ID']=master['Custom ID'].str.lower()
    # st.write('data sum before merge:',data['Partner Revenue'].sum())
    new=data.merge(master,how='left', on='Custom ID')
    # st.write('Partner Revenue after merge:', new['Partner Revenue'].sum())
    new['Show_Season'] = new['New Show Name'].map(str) + " - " + new['New Season']
    new['Territory'] = np.where(new['Country']=='CA', 'CA', np.where(new['New Show ']=='SUPW', '9SUSA', 'INTL'))
    new['Territory'] = np.where(new['New Show Name']=='Peep','CA',new['Territory'])
    return new



video=youtube(filename='C:/Users/Darragh/Documents/Python/Work/distribution/YouTube_9StoryIreland_M_20220101_20220131_red_rawdata_asset_v1-1.csv',
id_file='C:/Users/Darragh/Documents/Python/Work/distribution/Youtube Analysis - Master List.xlsx')
# df_1=youtube_load(filename='C:/Users/Darragh/Documents/Python/Work/distribution/YouTube_9StoryIreland_M_20220101_20220131_red_rawdata_asset_v1-1.csv').copy()
# df_2=youtube_master_filename(filename='C:/Users/Darragh/Documents/Python/Work/distribution/Youtube Analysis - Master List.xlsx').copy()
# video=merge_files(df_1,df_2).copy()


non_music_asset=youtube(filename='C:/Users/Darragh/Documents/Python/Work/distribution/YouTube_9StoryIreland_M_20220101_20220131_rev_views_by_asset_v1-0.csv',
id_file='C:/Users/Darragh/Documents/Python/Work/distribution/Youtube Analysis - Master List.xlsx')
# st.write(non_music_asset['Partner Revenue'].sum())
# test_data=pd.read_csv('C:/Users/Darragh/Documents/Python/Work/distribution/YouTube_9StoryIreland_M_20220101_20220131_rev_views_by_asset_v1-0.csv')
# st.write('raw data correct figure:',test_data['Partner Revenue'].sum())

asset=youtube(filename='C:/Users/Darragh/Documents/Python/Work/distribution/YouTube_9StoryIreland_M_20220101_20220131_red_music_rawdata_video_v1-1.csv',
id_file='C:/Users/Darragh/Documents/Python/Work/distribution/Youtube Analysis - Master List.xlsx')

@st.cache
def convert_df(df):
     # IMPORTANT: Cache the conversion to prevent computation on every rerun
     return df.to_csv().encode('utf-8')

# merge the docs together
combo_youtube=pd.merge(video,non_music_asset,how='outer')
combo_youtube=pd.merge(combo_youtube,asset,how='outer')
combo_youtube['Partner Revenue']=pd.to_numeric(combo_youtube['Partner Revenue'])
# st.write(combo_youtube.head())
# combo_youtube.loc['total']=combo_youtube.sum()
# show the NANs for the titles that don't have an ID matching up
missing_codes=combo_youtube[combo_youtube['Show_Season'].isnull()]
summary_missing_codes=missing_codes.groupby(['Custom ID','Asset Title'])['Partner Revenue'].sum().reset_index()
# for future use below to get the big ticket items a string which contains e.g. tiger, karma, convert everything to lowercase first
# summary_missing_codes['Asset Title']=summary_missing_codes['Asset Title'].lower()
with st.expander('This shows breakdown of lines that have missing codes/titles'):
    st.write('below is the grouped by title/ID version to compare')
    st.write(summary_missing_codes.reset_index().sort_values(by=['Partner Revenue'], ascending=False))

    # missing_codes.loc['total']=missing_codes.sum()
    missing_codes.groupby(['Custom ID','Asset Title'])['Partner Revenue'].sum()
    # st.write('below is the non grouped missing titles/codes')
    # st.write(missing_codes.sort_values(by='Partner Revenue', ascending=False))
    st.write('missing codes', missing_codes)
    st.write('Amount of revenue with missing titles', missing_codes['Partner Revenue'].sum())
# missing_codes.to_excel("C:/Users/Darragh/Documents/Python/Work/distribution/output/Missing_Codes_Monthly_Youtube.xlsx")

with st.expander('Missing title with Fugget/FAIT'):
    df=summary_missing_codes[summary_missing_codes['Custom ID'].str.contains('fait') | summary_missing_codes['Asset Title'].str.contains('Fugget')\
         | summary_missing_codes['Asset Title'].str.contains('fugget')| summary_missing_codes['Custom ID'].str.contains('FAIT')]\
        .sort_values(by=['Partner Revenue'], ascending=False)
    df['New Show Name']='Fugget About It'
    df['New Show'] = 'FAIT'
    cols_to_move=['Custom ID','New Show','New Show Name']
    cols = cols_to_move + [col for col in df if col not in cols_to_move]
    df=df[cols]
    st.write(df)
    csv = convert_df(df)
    st.download_button(label="Download data as CSV",data=csv,file_name='df.csv',mime='text/csv',key='fugget')

with st.expander('Missing title with Barney'):
    df=summary_missing_codes[summary_missing_codes['Custom ID'].str.contains('barn') | summary_missing_codes['Asset Title'].str.contains('Barney')\
         | summary_missing_codes['Asset Title'].str.contains('BARNEY')| summary_missing_codes['Custom ID'].str.contains('BARN')]\
        .sort_values(by=['Partner Revenue'], ascending=False)
    df['New Show Name']='Barney & Friends'
    df['New Show'] = 'BARN'
    cols_to_move=['Custom ID','New Show','New Show Name']
    cols = cols_to_move + [col for col in df if col not in cols_to_move]
    df=df[cols]
    st.write(df)
    csv = convert_df(df)
    st.download_button(label="Download data as CSV",data=csv,file_name='df.csv',mime='text/csv',key='barney')

with st.expander('Missing title with Garfield'):
    df=summary_missing_codes[summary_missing_codes['Custom ID'].str.contains('garf') | summary_missing_codes['Asset Title'].str.contains('Garfield')\
         | summary_missing_codes['Asset Title'].str.contains('garfield')| summary_missing_codes['Custom ID'].str.contains('Garf')]\
        .sort_values(by=['Partner Revenue'], ascending=False)
    df['New Show Name']='Garfield & Friends'
    df['New Show'] = 'GARF'
    cols_to_move=['Custom ID','New Show','New Show Name']
    cols = cols_to_move + [col for col in df if col not in cols_to_move]
    df=df[cols]
    st.write(df)
    csv = convert_df(df)
    st.download_button(label="Download data as CSV",data=csv,file_name='df.csv',mime='text/csv',key='garfield')

with st.expander('Missing title with Daniel Tiger'):
    df=summary_missing_codes[summary_missing_codes['Custom ID'].str.contains('dtnb') | summary_missing_codes['Asset Title'].str.contains('Daniel Tiger')\
         | summary_missing_codes['Asset Title'].str.contains('Daniel')| summary_missing_codes['Custom ID'].str.contains('DTNB')]\
        .sort_values(by=['Partner Revenue'], ascending=False)
    df['New Show Name']="Daniel Tiger's Neighborhood"
    df['New Show'] = 'DTNB'
    cols_to_move=['Custom ID','New Show','New Show Name']
    cols = cols_to_move + [col for col in df if col not in cols_to_move]
    df=df[cols]
    st.write(df)
    csv = convert_df(df)
    st.download_button(label="Download data as CSV",data=csv,file_name='df.csv',mime='text/csv',key='daniel_tiger')

with st.expander('Missing title with Wild Kratts'):
    df=summary_missing_codes[summary_missing_codes['Custom ID'].str.contains('wkrt') | summary_missing_codes['Asset Title'].str.contains('Wild Kratts')\
         | summary_missing_codes['Asset Title'].str.contains('Kratts')| summary_missing_codes['Custom ID'].str.contains('WKRT')]\
        .sort_values(by=['Partner Revenue'], ascending=False)
    df['New Show Name']="Wild Kratts"
    df['New Show'] = 'WKRT'
    cols_to_move=['Custom ID','New Show','New Show Name']
    cols = cols_to_move + [col for col in df if col not in cols_to_move]
    df=df[cols]
    st.write(df)
    csv = convert_df(df)
    st.download_button(label="Download data as CSV",data=csv,file_name='df.csv',mime='text/csv',key='kratts')

with st.expander('Missing title with Karmas World'):
    df=summary_missing_codes[summary_missing_codes['Custom ID'].str.contains('krma') | summary_missing_codes['Asset Title'].str.contains("Karma's World")\
         | summary_missing_codes['Asset Title'].str.contains('Karma')| summary_missing_codes['Custom ID'].str.contains('KRMA')]\
        .sort_values(by=['Partner Revenue'], ascending=False)
    df['New Show Name']="Karma's World"
    df['New Show'] = 'KRMA'
    cols_to_move=['Custom ID','New Show','New Show Name']
    cols = cols_to_move + [col for col in df if col not in cols_to_move]
    df=df[cols]
    st.write(df)
    csv = convert_df(df)
    st.download_button(label="Download data as CSV",data=csv,file_name='df.csv',mime='text/csv',key='karma')

with st.expander('Missing title with Clifford Puppy Days'):
    df=summary_missing_codes[summary_missing_codes['Custom ID'].str.contains('cpdy') ]\
        .sort_values(by=['Partner Revenue'], ascending=False)
    df['New Show Name']="Clifford Puppy Days"
    df['New Show'] = 'CPDY'
    cols_to_move=['Custom ID','New Show','New Show Name']
    cols = cols_to_move + [col for col in df if col not in cols_to_move]
    df=df[cols]
    st.write(df)
    csv = convert_df(df)
    st.download_button(label="Download data as CSV",data=csv,file_name='df.csv',mime='text/csv',key='clifford_puppy')

with st.expander('Missing title with Clifford Classic'):
    df=summary_missing_codes[summary_missing_codes['Custom ID'].str.contains('cbdc') ]\
        .sort_values(by=['Partner Revenue'], ascending=False)
    df['New Show Name']="Clifford The Big Red Dog (Classic)"
    df['New Show'] = 'CBDC'
    cols_to_move=['Custom ID','New Show','New Show Name']
    cols = cols_to_move + [col for col in df if col not in cols_to_move]
    df=df[cols]
    st.write(df)
    csv = convert_df(df)
    st.download_button(label="Download data as CSV",data=csv,file_name='df.csv',mime='text/csv',key='clifford_classic')

with st.expander('Missing title with Camp Lakebottom'):
    df=summary_missing_codes[summary_missing_codes['Custom ID'].str.contains('cplb') | summary_missing_codes['Asset Title'].str.contains("Camp Lakebottom")\
         | summary_missing_codes['Asset Title'].str.contains('Lakebottom')| summary_missing_codes['Custom ID'].str.contains('CPLB')]\
        .sort_values(by=['Partner Revenue'], ascending=False)
    df['New Show Name']="Camp Lakebottom"
    df['New Show'] = 'CPLB'
    cols_to_move=['Custom ID','New Show','New Show Name']
    cols = cols_to_move + [col for col in df if col not in cols_to_move]
    df=df[cols]
    st.write(df)
    csv = convert_df(df)
    st.download_button(label="Download data as CSV",data=csv,file_name='df.csv',mime='text/csv',key='camp_lakebottom')

with st.expander('Missing title with Astroblast'):
    df=summary_missing_codes[summary_missing_codes['Custom ID'].str.contains('astr') | summary_missing_codes['Asset Title'].str.contains("Astroblast")]\
        .sort_values(by=['Partner Revenue'], ascending=False)
    df['New Show Name']="Astroblast"
    df['New Show'] = 'ASTR'
    cols_to_move=['Custom ID','New Show','New Show Name']
    cols = cols_to_move + [col for col in df if col not in cols_to_move]
    df=df[cols]
    st.write(df)
    csv = convert_df(df)
    st.download_button(label="Download data as CSV",data=csv,file_name='df.csv',mime='text/csv',key='astroblast')

with st.expander('Missing title with Wandering Wenda'):
    df=summary_missing_codes[summary_missing_codes['Custom ID'].str.contains('wawe') | summary_missing_codes['Asset Title'].str.contains("Wandering Wenda")]\
        .sort_values(by=['Partner Revenue'], ascending=False)
    df['New Show Name']="Wandering Wenda"
    df['New Show'] = 'WAWE'
    cols_to_move=['Custom ID','New Show','New Show Name']
    cols = cols_to_move + [col for col in df if col not in cols_to_move]
    df=df[cols]
    st.write(df)
    csv = convert_df(df)
    st.download_button(label="Download data as CSV",data=csv,file_name='df.csv',mime='text/csv',key='wenda')



youtube_summary=combo_youtube.groupby(['New Show Name','New Season','Territory'])['Partner Revenue'].sum().unstack().fillna(0).sort_values(by='CA', ascending=False)\
.reset_index().sort_values(by='New Show Name').reset_index().drop('index',axis=1)

youtube_summary['non_other'] = np.where(youtube_summary['New Season']=='Other',0,1)
youtube_summary['other'] = np.where(youtube_summary['New Season']=='Other',1,0)
youtube_summary['count_other']=youtube_summary.groupby('New Show Name')['non_other'].transform('sum')
youtube_summary['check'] = np.where(((youtube_summary['count_other']>2)*(youtube_summary['other'])),0,1)
youtube_summary['apply_here'] = np.where(((youtube_summary['count_other']>2)*(youtube_summary['other'])),1,0)*youtube_summary['count_other']

youtube_summary['intl_other']=youtube_summary['INTL'] / youtube_summary['apply_here']
youtube_summary.replace([np.inf, -np.inf], np.nan, inplace=True)
youtube_summary['intl_other_add'] = ((youtube_summary.groupby(['New Show Name'], sort=False)['intl_other'].apply(lambda x: x.ffill().bfill()))\
    *youtube_summary['non_other']).fillna(0)
youtube_summary['usd_9SDIL']=(youtube_summary['INTL'] + youtube_summary['intl_other_add'])*youtube_summary['check']

youtube_summary['can_other']=youtube_summary['CA'] / youtube_summary['apply_here']
youtube_summary.replace([np.inf, -np.inf], np.nan, inplace=True)
youtube_summary['can_other_add'] = ((youtube_summary.groupby(['New Show Name'], sort=False)['can_other'].apply(lambda x: x.ffill().bfill()))\
    *youtube_summary['non_other']).fillna(0)
youtube_summary['usd_9SMG']=(youtube_summary['CA'] + youtube_summary['can_other_add'])*youtube_summary['check']

youtube_summary['usa_other']=youtube_summary['9SUSA'] / youtube_summary['apply_here']
youtube_summary.replace([np.inf, -np.inf], np.nan, inplace=True)
youtube_summary['usa_other_add'] = ((youtube_summary.groupby(['New Show Name'], sort=False)['usa_other'].apply(lambda x: x.ffill().bfill()))\
    *youtube_summary['non_other']).fillna(0)
youtube_summary['usd_9SUSA']=(youtube_summary['9SUSA'] + youtube_summary['usa_other_add'])*youtube_summary['check']

check_youtube=youtube_summary.copy()

with st.expander('Checks #1'):
    st.write('check that both match all good if says True below')
    st.write('if False prob out by a penny need to find the check for test that rounds....')
    st.write(youtube_summary['INTL'].sum()==youtube_summary['usd_9SDIL'].sum())
    st.write(youtube_summary['CA'].sum()==youtube_summary['usd_9SMG'].sum())
    st.write(youtube_summary['9SUSA'].sum()==youtube_summary['usd_9SUSA'].sum())

    payment_data=pd.read_csv('C:/Users/Darragh/Documents/Python/Work/distribution/YouTube_9StoryIreland_M_20220101_payment_summary_v1-0.csv')
    st.write(payment_data)


season_code=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/distribution/journal_codes.xlsx',sheet_name='Sheet1')
project_code=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/distribution/journal_codes.xlsx',sheet_name='Sheet2')
youtube_summary=pd.merge(youtube_summary,season_code,on='New Season',how='outer')
youtube_summary=pd.merge(youtube_summary,project_code,on='New Show Name',how='outer')

youtube_summary=youtube_summary.loc[:,['New Show Name','project_code','season_code','usd_9SUSA','usd_9SMG','usd_9SDIL','New Season','CA','INTL','9SUSA']]


youtube_summary['usd_9SUSA']=pd.to_numeric(youtube_summary['usd_9SUSA'])
youtube_summary['usd_9SMG']=pd.to_numeric(youtube_summary['usd_9SMG'])
youtube_summary['usd_9SDIL']=pd.to_numeric(youtube_summary['usd_9SDIL'])
youtube_summary['total']=youtube_summary['usd_9SUSA']+youtube_summary['usd_9SMG']+youtube_summary['usd_9SDIL']
youtube_summary=youtube_summary[youtube_summary['total']!=0]
youtube_summary['description']=youtube_summary['New Show Name'] + " " + youtube_summary['New Season']
report=youtube_summary.loc[:,['description','project_code','season_code','usd_9SUSA','usd_9SMG','usd_9SDIL','New Season']]
report['total']=youtube_summary['usd_9SUSA']+youtube_summary['usd_9SMG']+youtube_summary['usd_9SDIL']

# youtube_summary['territory']=np.where(youtube_summary['usd_9SMG']>0,'Canada',np.where(youtube_summary['usd_9SUSA']>0,'New York','International'))
# youtube_summary['description']=youtube_summary['New Show Name'] + " " + youtube_summary['New Season'] + " " +youtube_summary['territory']

with st.expander('Checks #2'):

    payment_data=pd.read_csv('C:/Users/Darragh/Documents/Python/Work/distribution/YouTube_9StoryIreland_M_20220101_payment_summary_v1-0.csv')
    st.write(payment_data)
    total=youtube_summary['usd_9SUSA'].sum()+youtube_summary['usd_9SMG'].sum()+youtube_summary['usd_9SDIL'].sum()
    st.write('total',total)
    st.write('non music asset total',non_music_asset['Partner Revenue'].sum())

    st.write('video total',video['Partner Revenue'].sum())
    st.write('asset total',asset['Partner Revenue'].sum())
    st.write('video+asset total',video['Partner Revenue'].sum()+asset['Partner Revenue'].sum())

    st.write('maybe need to bring in the adjustments spreadsheet')

with st.expander('Final Summary Version of YT'):
    st.write('version of report #1', report)
    st.write('total:',report['total'].sum())
    csv = convert_df(report)
    st.download_button(label="Download data as CSV",data=csv,file_name='youtube_summary_report.csv',mime='text/csv',key='youtube_summary_report')
    
    journal=youtube_summary.loc[:,['description','project_code','season_code','usd_9SUSA','usd_9SMG','usd_9SDIL']].copy()
    usa=journal.loc[:,['description','project_code','season_code','usd_9SUSA']].rename(columns={'usd_9SUSA':'amount'})
    usa['territory']='NY'
    toronto=journal.loc[:,['description','project_code','season_code','usd_9SMG']].rename(columns={'usd_9SMG':'amount'})
    toronto['territory']='CAN'
    dil=journal.loc[:,['description','project_code','season_code','usd_9SDIL']].rename(columns={'usd_9SDIL':'amount'})
    dil['territory']='INTL'
    journal=pd.concat([usa,toronto,dil],axis=0)
    journal['description']=journal['description'] + " " + journal['territory']
    journal=journal[journal['amount']!=0].dropna(subset=['amount']).drop('territory',axis=1)
    

    st.write('Journal Report',journal)
    st.write('journal total:',journal['amount'].sum())

    csv = convert_df(journal)
    st.download_button(label="Download data as CSV",data=csv,file_name='journal.csv',mime='text/csv',key='journal')
    


