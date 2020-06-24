# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 20:45:47 2020

@author: Tian
"""
import pandas as pd
import streamlit as st
import numpy as np
import pandas as pd
import math
from openpyxl import load_workbook
import datetime
from astral.sun import sun
from astral.geocoder import add_locations, database, lookup
import base64

st.title('B-C')

sheetname = 'TEMpost'
s = 'data' 
location = [107.433, 27.8] 

uploaded_file = st.file_uploader("Choose a file",
                                 type=["xlsx", ])

def deg_to_dms(deg, type='lat'):
    decimals, number = math.modf(deg)
    d = int(number)
    m = int(decimals * 60)
    s = round((deg - d - m / 60) * 3600.00)
    compass = {
        'lat': ('N', 'S'),
        'lon': ('E', 'W')
    }
    compass_str = compass[type][0 if d >= 0 else 1]
    #return '\''
    return str(abs(d)) + u"\u00b0" + str(abs(m))+ '\'' + str(abs(s)) + "\"" + compass_str
    #return "{}º{}'{:.0f}{}".format(abs(d), abs(m), abs(s), compass_str)
# 计算日照时间
def length_day(series,lon,lat):
    db = database()
    lon = deg_to_dms(lon, 'lon')  # 经度
    lat = deg_to_dms(lat, 'lat')
    add_locations("Somewhere,Secret Location,UTC," + lat + ',' + lon, db)
    s = sun(lookup("Somewhere", db).observer, date=series['date'])
    print(series['date'])

    len_day = s['sunset']-s['sunrise']
    return len_day.seconds/3600.0

if uploaded_file is not None:
    table=pd.read_excel(uploaded_file,
                    sheet_name = sheetname,
                    index_col= 0)
    #st.line_chart(table)  #绘图
    st.write(table.head())

    table1 = table.copy()

    data=table1[s] 
    
    table1['date'] = table1.apply(lambda x : datetime.datetime(int(x['年']),int(x['月']),int(x['日'])),
                              axis =1)
    table1['duration'] = table1.apply(length_day, axis=1, args=location)





# 计算每年日照时间
    length_year = table1.groupby('年')['duration'].sum()
# 将年日照时间加到table中
    table1['length_year'] =table1['年'].apply(lambda x:length_year[length_year.index==int(x)].values[0])
    table1['PPET'] = 0.85*table1['duration']/table1['length_year']*(0.46*table1['data']/10+8.13)*100

    st.write(table1.head())
    
    csv = table1.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}">Download CSV File</a> (right-click and save as &lt;some_name&gt;.csv)'
    st.markdown(href, unsafe_allow_html=True)








