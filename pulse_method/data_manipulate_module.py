# define function
import pandas as pd
import sys
import numpy as np

def load_prepare_data(data_path):
    # author - D.Q. Huang 20180406
    # this function takes each equipment dataset (Excel) and parse data into pandas df
    # and add second feature into Data Frame
    # input: data path
    # output: '设备数据' df and '操作记录' df if exist
    
    # note - for now, it can only load '设备数据' and '操作记录' which I am intersted
    # code can be easily modifed to load other data
    data = pd.ExcelFile(data_path)
    equip_data = data.parse('设备数据')
    try:
        operation_data = data.parse('操作记录')
    except:
        print("操作记录 does not exsit")
        operation_data = None
    equip_data = fill_missing_data(equip_data)
    
    if operation_data is None:
        equip_data = add_time_s_equip_data(equip_data)
    else:
        [equip_data,operation_data] = add_time_s(equip_data, operation_data)
        
    return [equip_data, operation_data]


def fill_missing_data(equip_data):
    # input "设备数据" dataFrame and this function automatically fill all missing values
    full_range = pd.date_range(start=equip_data['time'].min(), end=equip_data['time'].max(), freq='S')
    equip_data.set_index(['time'], inplace=True)
    equip_data = equip_data.sort_index().reindex(full_range, method='bfill')
    equip_data = equip_data.reset_index()
    equip_data.rename(columns={'index': 'time'}, inplace=True)
    return equip_data

def add_time_s(equip_data, operation_data):
    # input "设备数据" dataFrame and this function add time from 0 sec to end into dataFrame
    # this function only works for equip_data data
    time_temp = ((equip_data['time'][0:]-equip_data['time'][0]))
    time_sec = np.zeros(len(time_temp))
    for i in range(0,len(time_temp)):
        time_sec[i] = time_temp[i].seconds
    equip_data['time_sec'] = time_sec
    
    operation_time_temp = ((operation_data['时间'][0:]-equip_data['time'][0]))
    time_sec = np.zeros(len(operation_time_temp))
    for i in range(0,len(operation_time_temp)):
        time_sec[i] = operation_time_temp[i].seconds
    operation_data['time_sec'] = time_sec
    
    return [equip_data, operation_data]


def add_time_s_equip_data(equip_data):
    # input "设备数据" dataFrame and this function add time from 0 sec to end into dataFrame
    # this function only works for equip_data data
    time_temp = ((equip_data['time'][0:]-equip_data['time'][0]))
    time_sec = np.zeros(len(time_temp))
    for i in range(0,len(time_temp)):
        time_sec[i] = time_temp[i].seconds
    equip_data['time_sec'] = time_sec
    
    return equip_data
