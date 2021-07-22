# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 23:55:14 2020

@author: PC
"""

import pandas as pd
import numpy as np
import time


def meses(mes):
    mes_dict = {
        1: 0, 2: 31, 3: 59, 4: 90, 5: 120, 6: 151,
        7: 181, 8: 212, 9: 243, 10: 273, 11: 304, 12: 334,
    }
    return mes_dict[mes]


def main(lat, lon, year):
    #lat, lon, year = 33.2164, -97.1292, 2010
    # You must request an NSRDB api key from the link above
    api_key = 'JAXAOv9h87Ed6Vp0Q0WTREr65XyCYHk1RnWatqza'
    # Set the attributes to extract (e.g., dhi, ghi, etc.), separated by commas.
    attributes = 'ghi,dhi,dni,wind_speed,air_temperature,solar_zenith_angle'
    # Choose year of data
    year = '2010'
    # Set leap year to true or false. True will return leap day data if present, false will not.
    leap_year = 'false'
    # Set time interval in minutes, i.e., '30' is half hour intervals. Valid intervals are 30 & 60.
    interval = '30'
    # Specify Coordinated Universal Time (UTC), 'true' will use UTC, 'false' will use the local time zone of the data.
    # NOTE: In order to use the NSRDB data in SAM, you must specify UTC as 'false'. SAM requires the data to be in the
    # local time zone.
    utc = 'false'
    # Your full name, use '+' instead of spaces.
    your_name = 'Eleazar+Castro'
    # Your reason for using the NSRDB.
    reason_for_use = 'beta+testing'
    # Your affiliation
    your_affiliation = 'cienciasbcs'
    # Your email address
    your_email = 'ecastro@cienciasbcs.org'
    # Please join our mailing list so we can keep you up-to-date on new developments.
    mailing_list = 'true'
    # Declare url string
    # url = 'https://developer.nrel.gov/api/solar/nsrdb_psm3_download.csv?wkt=POINT({lon}%20{lat})&names={year}&leap_day={leap}&interval={interval}&utc={utc}&full_name={name}&email={email}&affiliation={affiliation}&mailing_list={mailing_list}&reason={reason}&api_key={api}&attributes={attr}'.format(
    #     year=year, lat=lat, lon=lon, leap=leap_year, interval=interval, utc=utc, name=your_name, email=your_email, mailing_list=mailing_list, affiliation=your_affiliation, reason=reason_for_use, api=api_key, attr=attributes)
    # # Return just the first 2 lines to get metadata:
    # print(url)
    # start = time.time()
    # info = pd.read_csv(url, nrows=1)
    # end = time.time()
    # print(end - start)
    # lati = info["Latitude"].item()
    # long = info["Longitude"].item()
    # See metadata for specified properties, e.g., timezone and elevation
    
    start = time.time()
    url = 'https://developer.nrel.gov/api/solar/nsrdb_psm3_download.csv?wkt=POINT({lon}%20{lat})&names={year}&leap_day={leap}&interval={interval}&utc={utc}&full_name={name}&email={email}&affiliation={affiliation}&mailing_list={mailing_list}&reason={reason}&api_key={api}&attributes={attr}'.format(
        year=year, lat=lat, lon=lon, leap=leap_year, interval=interval, utc=utc, name=your_name, email=your_email, mailing_list=mailing_list, affiliation=your_affiliation, reason=reason_for_use, api=api_key, attr=attributes)
    print(url)
    df = pd.read_csv(url, skiprows=2)
    end = time.time()
    print(end - start)
    # Set the time index in the pandas dataframe:
    a = df.set_index(pd.date_range(
        '1/1/{yr}'.format(yr=year), freq=interval+'Min', periods=525600/int(interval)))

    a['ind'] = a.index
    ce = []
    for i in a["Month"]:
        ce.append(meses(i))
    a["Day acum"] = ce
    a["Declination Angle"] = -lat * \
        np.sin(np.radians((360/365)*(a["Day acum"]+a["Day"]+10)))
    a["elevation angle"] = 90 - a["Solar Zenith Angle"]
    a["HRA"] = 15*(a["Hour"]+a["Minute"]/60-12)
    a["Elv Angle"] = np.degrees(np.arcsin((np.sin(np.radians(a["Declination Angle"]))*np.sin(np.radians(
        lat)) + np.cos(np.radians(a["Declination Angle"]))*np.cos(np.radians(lat))*np.cos(np.radians(a["HRA"])))))
    a["Azimuth"] = np.degrees(np.arccos((np.sin(np.radians(a["Declination Angle"]))*np.cos(np.radians(lat)) - np.cos(
        np.radians(a["Declination Angle"]))*np.sin(np.radians(lat))*np.cos(np.radians(a["HRA"])))/np.cos(np.radians(a["Elv Angle"]))))
    a["Azimuth"] = a["Azimuth"].interpolate()
    a["Irra"] = a["DNI"]*(np.cos(np.radians(lat))*np.cos(np.radians(a["Elv Angle"]))*np.cos(np.radians(180-a["Azimuth"]))+np.cos(np.radians(
        lat))*np.sin(np.radians(a["Elv Angle"])))+a["DHI"]*((1+np.sin(np.radians(lat)))/2)+a["GHI"]*.1*(1-((1+np.cos(np.radians(lat)))/2))
    a["HSP"] = a["Irra"]/2000
    a["HSP"].sum()
    return a
