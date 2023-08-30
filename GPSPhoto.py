# -*- coding: utf-8 -*-
"""
2023/07/28

Created by Matt Sparacino (Matt.Sparacino@Greeleygov.com)

"""
import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

#%% define function
def get_exif(filename):
    exif_data = {}
    image = Image.open(filename)
    info = image._getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                gps_data = {}
                for gps_tag in value:
                    sub_decoded = GPSTAGS.get(gps_tag, gps_tag)
                    gps_data[sub_decoded] = value[gps_tag]
                exif_data[decoded] = gps_data
            else:
                exif_data[decoded] = value

    return exif_data    

#%% create empty dataframe
df=pd.DataFrame({'Image': [],'Lat_DD': [],'Long_DD': [],'Elev_ft': [],'Bearing_deg': [],'Date_time': []})

#%% create widget for uploading multiple files (<200mb each)
with st.form("my-form", clear_on_submit =True):
    uploaded_files = st.file_uploader("Upload your image files here:",accept_multiple_files=True)
    submitted = st.form_submit_button("Upload!")
        
    if submitted and uploaded_files is not None:
        st.write("Uploaded!")
        
for uploaded_file in uploaded_files:
    
#%% load images and loop through to extract data
    exif = get_exif(uploaded_file)

    #%% convert to decimals
    try:
        lat=exif["GPSInfo"]["GPSLatitude"]
        lat_DD=lat[0].numerator+lat[1].numerator/60+lat[2].numerator/lat[2].denominator/3600
    except:
        lat_DD=np.nan
    try:
        long=exif["GPSInfo"]["GPSLongitude"]
        long_DD=(long[0].numerator+long[1].numerator/60+long[2].numerator/long[2].denominator/3600)*-1
    except:
        long_DD=np.nan
    try:
        alt=exif["GPSInfo"]["GPSAltitude"]
        alt_ft=alt.numerator/alt.denominator*3.28084
    except:
        alt_ft=np.nan
    try:
        brg=exif["GPSInfo"]["GPSImgDirection"]
        brgdeg=brg.numerator/brg.denominator
    except:
        brgdeg=np.nan
    try:
        dt=exif["DateTimeDigitized"]
        date=dt[0:10]
        date=date.replace(":", "-")
        time=dt[11:]
        dt1=date+" "+time
        dt1=pd.to_datetime(dt1)

    except:
        dt=np.nan
            
    im_data=pd.DataFrame({'Image': [uploaded_file.name],
                          'Lat_DD': [lat_DD],
                          'Long_DD': [long_DD],
                          'Elev_ft': [alt_ft],
                          'Bearing_deg' : [brgdeg],
                          'Date_Time': [dt1]}) 
        
# #%% concat dataframe
    df=pd.concat([df,im_data])
    
#%% Display datatable

project = st.text_input(
    "Enter short project name (to be used in csv file name):")

df=df.set_index("Image")
st.dataframe(df)

@st.cache_data
def convert_df(df):
    return df.to_csv().encode('utf-8')
csv=convert_df(df)

st.download_button(
    label="Download GPS photo points as CSV",
    data=csv,
    file_name="%s.csv" % project,
    mime='text/csv')
