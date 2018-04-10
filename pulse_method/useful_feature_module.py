#import pandas as pd
#import sys
import numpy as np

def sweep_get_std(input_array, m):
    # author - D.Q. Huang 20180406
    # sweep through each point and compute the std of m point near this point
    # input_array is an numpy array
    # m: m point near current point
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
    # author - D.Q. Huang 20180406
    # sweep through each point and select m point near this point compute the diff of first and last point
    # input_array is an numpy array
    # m: m point near current point
    # method = 0 or 1
    #    0 --> current point as center point
    #    1 --> current point as start point and m-1 point ahead of this point
    # example: output_array = sweep_get_diff(input_array, 3, 1)
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
            if m == 1:
                pass
            else:
                m = m - 1 # fix the miss 1 bug - so code is consistent
                for i in range(0,len(input_array)):
                    if i <= (m-1):
                        i_start = 0
                        i_end = i
                        diff_array[i] = input_array[i_end] - input_array[i_start]
                    else:
                        i_start = i-m
                        i_end = i
                        ind = np.array(range(i_start,i_end+1))
                        ind = ind[(ind>-1)&(ind<len(input_array))]
                        diff_array[i] = input_array[ind[-1]] - input_array[ind[0]]

    return diff_array
def sweep_get_mean(input_array, m):
    # author - D.Q. Huang 20180406
    # sweep through each point and compute the diff of m point near this point
    # m: m point near current point
    
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


def compute_useful_feature(equip_data, diff = 0, std = 0, mean = 0, input_feature = ['PC', 'QC']):
    # author - D.Q. Huang 20180406
    # this function collects all functions that compute other useful features such as 
    # diff, std, and mean of waveform in this case
    # if you want compute other features, simply define that function and insert it into here
    # and change relevant inputs
    # input (for now):
    # diff - a list: n points including the current point - see sweep_get_diff function for detail
    # std - a list:: n points including the current point - see sweep_get_std function for detail
    # mean - a list:: n points including the current point - see sweep_get_mean function for detail
    # exmaple:
    # equip_data = compute_useful_feature(equip_data, [1,2,3,4], [1,2,3], 0, ['PC', 'QC']):
    
    if type(input_feature) is not list:
        input_feature = [input_feature]    
    
    # diff section
    if type(diff) is not list:
        diff = [diff]
    if (len(diff) == 1) & (diff[0] == 0):
        pass
    else:
        for feature in input_feature:
            for i in diff:
                lable = feature + '_' + str(i) + 'pDiff'
                equip_data[lable] = sweep_get_diff(equip_data[feature].values,i)
    
    # std section
    if type(std) is not list:
        std = [std]
    if (len(std) == 1) & (std[0] == 0):
        pass
    else:
        for feature in input_feature:
            for i in std:
                lable = feature + '_' + str(i) + 'pStd'
                equip_data[lable] = sweep_get_std(equip_data[feature].values,i)


    # mean section
    if type(mean) is not list:
         mean = [mean]
    if (len(mean) == 1) & (mean[0] == 0):
        pass
    else:
        for feature in input_feature:
            for i in mean:
                lable = feature + '_' + str(i) + 'pMean'
                equip_data[lable] = sweep_get_mean(equip_data[feature].values,i)

                
                
     # add other useful features?
    
    return equip_data


