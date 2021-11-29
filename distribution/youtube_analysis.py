import pandas as pd
import numpy as np
import streamlit as st
from io import BytesIO
import base64

@st.cache
def youtube(filename,id_file):
    data=pd.read_excel(filename)
    data['Custom ID']=data['Custom ID'].str.lower()
    master=pd.read_excel(id_file)
    master['Custom ID']=master['Custom ID'].str.lower()
    new=data.merge(master,how='left', on='Custom ID')
    new['Show_Season'] = new['New Show Name'].map(str) + " - " + new['New Season']
    new['Territory'] = np.where(new['Country']=='CA', 'CA', np.where(new['New Show ']=='SUPW', '9SUSA', 'INTL'))
    new['Territory'] = np.where(new['New Show Name']=='Peep','CA',new['Territory'])
    return new
video=youtube(filename='C:/Users/Darragh/Documents/Python/Work/distribution/red_rawdata_asset_nov.xlsx',
id_file='C:/Users/Darragh/Documents/Python/Work/distribution/Youtube October Analysis - Master List.xlsx')

non_music_asset=youtube(filename='C:/Users/Darragh/Documents/Python/Work/distribution/rev_views_by_asset_nov.xlsx',
id_file='C:/Users/Darragh/Documents/Python/Work/distribution/Youtube October Analysis - Master List.xlsx')

asset=youtube(filename='C:/Users/Darragh/Documents/Python/Work/distribution/red_music_raw_data_video_nov.xlsx',
id_file='C:/Users/Darragh/Documents/Python/Work/distribution/Youtube October Analysis - Master List.xlsx')


# merge the docs together
combo_youtube=pd.merge(video,non_music_asset,how='outer')
combo_youtube=pd.merge(combo_youtube,asset,how='outer')
# st.write(combo_youtube.head())
# combo_youtube.loc['total']=combo_youtube.sum()
# show the NANs for the titles that don't have an ID matching up
missing_codes=combo_youtube[combo_youtube['Show_Season'].isnull()]
missing_codes=missing_codes[missing_codes['Partner Revenue']>0.01]
# missing_codes.loc['total']=missing_codes.sum()
st.write('any missing codes - is it material?', missing_codes)
st.write('sum', missing_codes['Partner Revenue'].sum())
# missing_codes.to_excel("C:/Users/Darragh/Documents/Python/Work/distribution/output/Missing_Codes_Monthly_Youtube.xlsx")
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


st.write('check that both match all good if says True below')
st.write(youtube_summary['INTL'].sum()==youtube_summary['usd_9SDIL'].sum())
st.write(youtube_summary['CA'].sum()==youtube_summary['usd_9SMG'].sum())
st.write(youtube_summary['9SUSA'].sum()==youtube_summary['usd_9SUSA'].sum())


season_code=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/distribution/journal_codes.xlsx',sheet_name='Sheet1')
project_code=pd.read_excel('C:/Users/Darragh/Documents/Python/Work/distribution/journal_codes.xlsx',sheet_name='Sheet2')
youtube_summary=pd.merge(youtube_summary,season_code,on='New Season',how='outer')
youtube_summary=pd.merge(youtube_summary,project_code,on='New Show Name',how='outer')

youtube_summary=youtube_summary.loc[:,['New Show Name','project_code','season_code','usd_9SUSA','usd_9SMG','usd_9SDIL','New Season']]

st.write('summary',youtube_summary)
st.write(youtube_summary.sum())
# st.write(youtube_summary['New Show Name'].unique())

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

st.markdown(get_table_download_link(youtube_summary), unsafe_allow_html=True)
# st.markdown(get_table_download_link(youtube_summary), unsafe_allow_html=True)
