# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
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
df=pd.DataFrame({'Image': [],'Lat_DD': [],'Long_DD': [],'Elev_ft': []})

#%% create widget for uploading multiple files (<200mb each)
uploaded_files = st.file_uploader("Upload your image files here:",accept_multiple_files=True)

project = st.text_input(
    "Enter short project name (to be used in csv file name):")

#uploaded_file=Image.open("/Users/mattsparacino/Downloads/IMG_3962.jpg")
for uploaded_file in uploaded_files:

#%% load images and loop through to extract data
    exif = get_exif(uploaded_file)

    #%% convert to decimals
    try:
        lat=exif["GPSInfo"]["GPSLatitude"]
        lat_DD=lat[0].numerator+lat[1].numerator/60+lat[2].numerator/lat[2].denominator/3600
        long=exif["GPSInfo"]["GPSLongitude"]
        long_DD=(long[0].numerator+long[1].numerator/60+long[2].numerator/long[2].denominator/3600)*-1
        alt=exif["GPSInfo"]["GPSAltitude"]
        alt_ft=alt.numerator/alt.denominator*3.28084
            
        im_data=pd.DataFrame({'Image': [uploaded_file.name],'Lat_DD': [lat_DD],'Long_DD': [long_DD],'Elev_ft': [alt_ft]}) 
    except:
        im_data=pd.DataFrame({'Image': [uploaded_file.name],'Lat_DD': [np.nan],'Long_DD': [np.nan],'Elev_ft': [np.nan]})
        
# #%% concat dataframe
    df=pd.concat([df,im_data])

#%% Display datatable
st.dataframe(
    df,
    hide_index=True)

@st.cache_data
def convert_df(df):
    return df.to_csv().encode('utf-8')

csv=convert_df(df)

st.download_button(
    label="Download GPS photo points as CSV",
    data=csv,
    file_name="%s.csv" % project,
    mime='text/csv')
