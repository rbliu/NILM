# define function
import pandas as pd
import sys
import numpy as np

def sweep_get_std(input_array, m):
    # sweep through each point and compute the std of m point near this point
    # input_array is an numpy array
    std_array = np.zeros(len(input_array))
    if m == 0:
        print('Error:n can not be 0')
        return -1
    else:
        for i in range(0,len(input_array)):
            if m % 2 == 0:
                i_start = int(i-(m/2-1))
                i_end = int(i+m/2)
            else:
                i_start = int(i-(m-1)/2)
                i_end = int(i+(m-1)/2)
            ind = np.array(range(i_start,i_end+1))
            ind = ind[(ind>-1)&(ind<len(input_array))]
            std_array[i] = np.std(input_array[ind])
    return std_array

def sweep_get_diff(input_array, m, method=1):
    # sweep through each point and select m point near this point and compute the diff of first and last point
    # input_array is an numpy array
    # method = 0 or 1
    #    0 --> current point as center point
    #    1 --> current point as start point
    
    diff_array = np.zeros(len(input_array))
    if m == 0:
        print('Error:n can not be 0')
        return -1
    #elif m == 1:
    #    pass
    else:
        if method == 0:
            for i in range(0,len(input_array)):
                if m % 2 == 0:
                    i_start = int(i-(m/2-1))
                    i_end = int(i+m/2)
                else:
                    i_start = int(i-(m-1)/2)
                    i_end = int(i+(m-1)/2)
                ind = np.array(range(i_start,i_end+1))
                ind = ind[(ind>-1)&(ind<len(input_array))]
                diff_array[i] = input_array[ind[-1]] - input_array[ind[0]]
        else:
            for i in range(0,len(input_array)):
                i_start = i
                i_end = i + m
                ind = np.array(range(i_start,i_end+1))
                ind = ind[(ind>-1)&(ind<len(input_array))]
                diff_array[i] = input_array[ind[-1]] - input_array[ind[0]]
    return diff_array
def sweep_get_mean(input_array, m):
    # sweep through each point and compute the diff of m point near this point
    mean_array = np.zeros(len(input_array))
    if m == 0:
        print('Error:n can not be 0')
        return -1
    else:
        for i in range(0,len(input_array)):
            if m % 2 == 0:
                i_start = int(i-(m/2-1))
                i_end = int(i+m/2)
            else:
                i_start = int(i-(m-1)/2)
                i_end = int(i+(m-1)/2)
            ind = np.array(range(i_start,i_end+1))
            ind = ind[(ind>-1)&(ind<len(input_array))]
            mean_array[i] = np.mean(input_array[ind])
        return mean_array

def fill_missing_data(equip_data):
    # input "设备数据" dataFrame and this function automatically fill all missing values
    full_range = pd.date_range(start=equip_data['time'].min(), end=equip_data['time'].max(), freq='S')
    equip_data.set_index(['time'], inplace=True)
    equip_data = equip_data.sort_index().reindex(full_range, method='bfill')
    equip_data = equip_data.reset_index()
    equip_data.rename(columns={'index': 'time'}, inplace=True)
    return equip_data

def add_time_s(equip_data):
    # input "设备数据" dataFrame and this function add time from 0 sec to end into dataFrame
    time_temp = ((equip_data['time'][0:]-equip_data['time'][0]))
    time_sec = np.zeros(len(time_temp))
    for i in range(0,len(time_temp)):
        time_sec[i] = time_temp[i].seconds
    equip_data['time_sec'] = time_sec
    return equip_data
    