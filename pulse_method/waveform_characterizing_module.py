#import pandas as pd
#import sys
import numpy as np
#import matplotlib
#import matplotlib.pyplot as plt

def characterize_pulse(equip_x_data, feature, posi_thresh, nega_thresh):
    # author - D.Q. Huang 20180406
    # this function is used to find and characterize pulse in each instrument
    # input:
    #       - instrument data
    #       - feature - what feature to use for pulse
    #       - positive threshold
    #       - negative threshold
    # output:
    pulse_wf = [] # pulse waveform, this is not part of output
    pulse_area = [] # pulse area
    pulse_trig_t = [] # time of first point that is triggered
    pulse_heith_t = [] # height point time
    pulse_end_t = [] # time of last point that is triggered
    pulse_h = [] # pulse height
    
    time_s = equip_x_data['time_sec'].values
    wf = equip_x_data[feature].values
    cut_p = (wf > posi_thresh)
    cut_p_diff = np.diff(cut_p*1) # convert boolean to number 
    pp_start_idx = np.where(cut_p_diff == 1)[0] + 1 # first index cutted out by diff - python index (starts with 0)
    pp_end_idx = np.where(cut_p_diff == -1)[0] # we don't need +1 here somehow - python index (starts with 0)

    for i in range(0, min([len(pp_start_idx),len(pp_end_idx)])):
        temp_pulse_wf = wf[np.array(range(pp_start_idx[i],pp_end_idx[i]+1))]
        temp_pulse_time_s = time_s[np.array(range(pp_start_idx[i],pp_end_idx[i]+1))]
        pulse_wf.append(temp_pulse_wf)
        pulse_area.append(temp_pulse_wf.sum())
        pulse_h.append(temp_pulse_wf.max())
        pulse_trig_t.append(temp_pulse_time_s[0])
        cut_pulse_heigh_t = np.where(temp_pulse_wf == temp_pulse_wf.max())
        pulse_heith_t.append(temp_pulse_time_s[cut_pulse_heigh_t[0][0]])
        pulse_end_t.append(temp_pulse_time_s[-1])
        
    cut_n = (wf < nega_thresh)
    cut_n_diff = np.diff(cut_n*1)
    np_start_idx = np.where(cut_n_diff == 1)[0] + 1
    np_end_idx = np.where(cut_n_diff == -1)[0]
    
    for i in range(0, min([len(np_start_idx),len(np_end_idx)])):
        temp_pulse_wf = wf[np.array(range(np_start_idx[i],np_end_idx[i]+1))]
        temp_pulse_time_s = time_s[np.array(range(np_start_idx[i],np_end_idx[i]+1))]
        pulse_wf.append(temp_pulse_wf)
        pulse_area.append(temp_pulse_wf.sum())
        pulse_h.append(temp_pulse_wf.min())
        pulse_trig_t.append(temp_pulse_time_s[0])
        cut_pulse_heigh_t = np.where(temp_pulse_wf == temp_pulse_wf.min())
        pulse_heith_t.append(temp_pulse_time_s[cut_pulse_heigh_t[0][0]])
        pulse_end_t.append(temp_pulse_time_s[-1])
        
    pulse_area = np.array(pulse_area)
    pulse_trig_t = np.array(pulse_trig_t)
    pulse_heith_t = np.array(pulse_heith_t)
    pulse_end_t = np.array(pulse_end_t)
    pulse_h = np.array(pulse_h)
    
    index = np.argsort(pulse_trig_t)
    pulse_area = pulse_area[index]
    pulse_trig_t = pulse_trig_t[index]
    pulse_heith_t = pulse_heith_t[index]
    pulse_end_t = pulse_end_t[index]
    pulse_h = pulse_h[index]
    
    return [pulse_area,pulse_trig_t,pulse_heith_t,pulse_end_t,pulse_h]    