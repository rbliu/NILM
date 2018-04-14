def yd2_detector(pulse_area,pulse_trig_t,pulse_heith_t,pulse_end_t,pulse_h):
    '''
    Author - D.Q. Huang - 20180413
    Input : pulse_area, pulse_trig_t, pulse_heith_t, pulse_end_t, pulse_h,  i.e.
            The characteristics of the pulses identified by the characterize_pulse function. 
    Output : Exist: boolean. If True, then yd3 is decteted. If False, then yd3 is not detected.
             operation : list of tuples. Each tuple contains two values: one is the operation, the other is the operation time.
             mask : numpy array that put False at the location where yd3 pulse is.
    Note: version with paring
    update - 20180413: 
        - fix a small bug that miss to veto pulse that has size less than 9300 but greater than 7000
        - add parts to veto potential printer signal
        - add mask, pulse occupied as False, others, True
        - change chinese character to English
        - use consecutive pulse height difference to determine mv start and stop instead of time gap
            - this is not completed, because of complication,decide to switch back to use time again
            - some legacy in the code, such as tot_pulse_area, and section "# instead of using time gap..."
        - fix the bug due to miss downward big pulse due to overlapping with other big pulse
        - remaining bugs: 1. missing upward big pulse due to overlapping
                          2. If there is a non-High state between start and High, it is missed
    '''
    # parameter section *****************
    area_ub1 = 12000 # total pulse upper bound
    area_lb1 = 9300  # total pulse lower bound
    mw_pulse_thresh = 7000
    area_criteria = 500 # lowest bound
    
    s_m_p_t_diff_lb = 2
    s_m_p_t_diff_ub = 4
    
    # to check whether mw is stoped or not. This parameter need to be varied due to a non-fixalbe bug
    mw_turn_off_t_criteria = 28 # defaul value = 28-30
    #mv_tunr_off_area_diff_criteria = 200 # postive value 
    
    # this parameter is to just whether the mv in 高火 state
    mv_high_to_stop_criteria = 25 # defaul value = 25
    # parameter section *****************
    
    
    
    
    
    
    
    # first round of selection using pulse area
    cut_p_indef = (np.abs(pulse_area)<area_ub1)&(np.abs(pulse_area)>mw_pulse_thresh)
    p_index_indef = np.where(cut_p_indef)[0]

    p_height_t_indef = pulse_heith_t[p_index_indef]
    p_area_indef = pulse_area[p_index_indef]
    p_height_t = pulse_heith_t[p_index_indef]

    mask_pre = np.ones(len(p_area_indef),dtype=bool)
    s_p_ind = []
    m_p_ind = []
    tot_pulse_area = []
    for i in range(0, len(p_height_t)):
        if p_area_indef[i] < 0:
            t_temp = p_height_t_indef[i]
            t_w = [t_temp-s_m_p_t_diff_ub, t_temp-s_m_p_t_diff_lb]
            window_cut = (pulse_heith_t >= t_w[0]) & (pulse_heith_t <= t_w[1])
            if any((pulse_area[window_cut] < -area_criteria) & (pulse_area[window_cut] > -3000)):
                tot_s = pulse_area[window_cut] + p_area_indef[i]
                if any((tot_s > -area_ub1) & (tot_s < -area_lb1)):
                    cut_s_p = window_cut & (pulse_area < -500) & (pulse_area > -3000)
                    s_p_ind.append(np.where(cut_s_p)[0][0])
                    m_p_ind.append(p_index_indef[i])
                    # print(p_area_indef[i])
                    #tot_pulse_area.append((p_area_indef[i] + pulse_area[cut_s_p])[0])
                    tot_pulse_area.append(tot_s[0])
                    continue
                else:
                    mask_pre[i] = False
                    continue
            elif (p_area_indef[i] < -area_lb1) & (p_area_indef[i] > -area_ub1):
                tot_pulse_area.append(p_area_indef[i])
                continue
            else:
                mask_pre[i] = False
                continue
        if p_area_indef[i] > 0:
            t_temp = p_height_t_indef[i]
            t_w = [t_temp-s_m_p_t_diff_ub, t_temp-s_m_p_t_diff_lb]
            window_cut = (pulse_heith_t >= t_w[0]) & (pulse_heith_t <= t_w[1])
            if any((pulse_area[window_cut] > area_criteria) & (pulse_area[window_cut] < 3000)):
                tot_s = pulse_area[window_cut] + p_area_indef[i]
                if any((tot_s < area_ub1) & (tot_s > area_lb1)):
                    cut_s_p = window_cut & (pulse_area > 500) & (pulse_area < 3000)
                    s_p_ind.append(np.where(cut_s_p)[0][0])
                    m_p_ind.append(p_index_indef[i])
                    # print(p_area_indef[i])
                    #tot_pulse_area.append((p_area_indef[i] + pulse_area[cut_s_p])[0])
                    tot_pulse_area.append(tot_s[0])
                    continue
                else:
                    mask_pre[i] = False
                    continue
            elif (p_area_indef[i] < area_ub1) & (p_area_indef[i] > area_lb1):
                t_w = [t_temp, t_temp+10] # # to discriminate with printer
                window_cut = (pulse_heith_t >= t_w[0]) & (pulse_heith_t <= t_w[1]) # # to discriminate with printer
                if any((np.abs(pulse_area[window_cut]) > 800) & (np.abs(pulse_area[window_cut]) < 3000)): # to discriminate with printer
                    if (pulse_area[window_cut] > 7500).sum() == 0: # to discriminate with printer
                        mask_pre[i] = False
                        continue
                else:
                    tot_pulse_area.append(p_area_indef[i])
                    continue
            else:
                mask_pre[i] = False
                continue

    p_index_semi_def = p_index_indef[mask_pre]
    p_height_t_semi_def = p_height_t_indef[mask_pre]
    p_area_semi_def = p_area_indef[mask_pre]
    
    # second round of microwave pulse index check - pulse paring, i.e. first positive pulse pairs up with first negative pulse and then continue
    temp_p_ind_final_addition = []
    temp_p_ind_final = []
    i = 0
    k = 0
    while i < len(p_area_semi_def):
        k = 0
        if (i == 0) & (p_area_semi_def[i] < 0):
            temp_p_ind_final.append(p_index_semi_def[i])
            i=i+1
        elif (p_area_semi_def[i] > 0):
            for j in range(1,len(p_area_semi_def)):
                if i+j >= len(p_area_semi_def):
                    break
                if p_area_semi_def[i+j] < 0:
                    break
            if i+j >= len(p_area_semi_def):
                temp_p_ind_final.append(p_index_semi_def[i])
                break
            if j == 2: # fix the bug that when downward spike greater than usual size during overlab
                t_w = [p_height_t_semi_def[i], p_height_t_semi_def[i+1]]
                cut_t_window = (pulse_heith_t > t_w[0]) & (pulse_heith_t < t_w[1])
                if any(np.abs(pulse_area[cut_t_window]) > area_ub1):
                    temp_p_ind_final.append(p_index_semi_def[i+1])
                    addi_ind = np.where(cut_t_window)[0][0]
                    temp_p_ind_final.append(addi_ind)
                    temp_p_ind_final_addition.append(addi_ind)
            temp_p_ind_final.append(p_index_semi_def[i])
            temp_p_ind_final.append(p_index_semi_def[i+j])
            i=i+j+1
        else:
            i=i+1
            k=k+1
            print(k)
            pass

    # test whether microwave exsit nor not by checking how many pulses are
    p_ind_final = np.array(temp_p_ind_final)
    p_ind_final.sort()
    p_ind_final_addition = np.array(temp_p_ind_final_addition)
    p_ind_final_addition.sort()

    
    # find small pulses ahead of those addtional big pulse
    for i, ind in enumerate(p_ind_final_addition):
        if pulse_area[ind] > 0:
            t_temp = pulse_heith_t[ind]
            t_w = [t_temp-s_m_p_t_diff_ub, t_temp-s_m_p_t_diff_lb]
            window_cut = (pulse_heith_t >= t_w[0]) & (pulse_heith_t <= t_w[1])
            if any((pulse_area[window_cut] > area_criteria) & (pulse_area[window_cut] < 3000)):
                cut_s_p = window_cut & (pulse_area > 500) & (pulse_area < 3000)
                s_p_ind.append(np.where(cut_s_p)[0][0])
                m_p_ind.append(ind)
            else:
                pass
        if pulse_area[ind] < 0:
            t_temp = pulse_heith_t[ind]
            t_w = [t_temp-s_m_p_t_diff_ub, t_temp-s_m_p_t_diff_lb]
            window_cut = (pulse_heith_t >= t_w[0]) & (pulse_heith_t <= t_w[1])
            if any((pulse_area[window_cut] < -area_criteria) & (pulse_area[window_cut] > -3000)):
                cut_s_p = window_cut & (pulse_area < -500) & (pulse_area > -3000)
                s_p_ind.append(np.where(cut_s_p)[0][0])
                m_p_ind.append(ind)
            else:
                pass

                
    
    if len(p_ind_final) <= 1: # need to double check
        exist = False
    else:
        exist = True
        p_area_final = pulse_area[p_ind_final]
        p_height_t_final = pulse_heith_t[p_ind_final]
        p_trigger_t_final = pulse_trig_t[p_ind_final]
        p_end_t_final = pulse_end_t[p_ind_final]
        
        start_ind = []
        stop_ind = []
        # turn off to upgrade the algorithum
        for i, ind in enumerate(p_ind_final):
            if pulse_area[ind] > 0:
                if i == 0:
                    start_ind.append(i)
                else:
                    if (pulse_heith_t[ind] - pulse_heith_t[p_ind_final[i-1]]) > mw_turn_off_t_criteria: # by checking data, 27,28 seems OK, use 30 for safe
                        start_ind.append(i)
                        stop_ind.append(i-1)
            else:
                pass
        if p_area_final[-1] < 0:
            stop_ind.append(len(p_ind_final)-1)
        '''
        # instead of using time gap, using consecutive pulse height difference to determine pulse start and end
        for i in range(0,len(p_ind_final)):
            if p_area_final[i] > 0:
                if i == 0:
                    start_ind.append(i)
                elif (i+1) < len(p_ind_final):
                    if np.abs(p_area_final[i+1] + p_area_final[i]) > mv_tunr_off_area_diff_criteria:
                        stop_ind.append(i+1)
                        if (i+2) < len(p_ind_final):
                            start_ind.append(i+2)
                else:
                    pass
            else:
                pass
        if p_area_final[-1] < 0:
            stop_ind.append(len(p_ind_final)-1)
        '''
        temp_operaton = []
        temp_operation_t = []
        temp_operation_ind = []
        i = 0
        while i < len(p_area_final):
            if i in start_ind:
                temp_operaton.append('start')
                temp_operation_t.append(p_trigger_t_final[i])
                temp_operation_ind.append(p_ind_final[i])
                t_window1 = p_height_t_final[i+1] - p_height_t_final[i]
                if t_window1 > mv_high_to_stop_criteria:
                    temp_operaton.append('High')
                    temp_operaton.append('stop')
                    temp_operation_t.append(p_trigger_t_final[i+1])
                    temp_operation_ind.append(p_ind_final[i+1])
                    temp_operation_t.append(p_trigger_t_final[i+1])
                    temp_operation_ind.append(p_ind_final[i+1])
                i = i + 2
                continue
            elif i in stop_ind:
                temp_operaton.append('stop')
                temp_operation_t.append(p_trigger_t_final[i])
                temp_operation_ind.append(p_ind_final[i])
            elif (p_area_final[i] > 0):
                if i+1 in stop_ind:
                    t_window1 = p_height_t_final[i+1] - p_height_t_final[i]
                    if t_window1 > mv_high_to_stop_criteria:
                        tmp_ope = 'High'
                        temp_operaton.append(tmp_ope)
                        temp_operation_t.append(p_trigger_t_final[i])
                        temp_operation_ind.append(p_ind_final[i])
                        i = i+1
                        continue
                    else:
                        i = i+1
                        continue
                t_window1 = p_height_t_final[i+1] - p_height_t_final[i]
                if (t_window1 >=2 ) & (t_window1 <=5 ):
                    tmp_ope = 'Low'
                    if len(temp_operaton) == 0:
                        temp_operaton.append(tmp_ope)
                        temp_operation_t.append(p_trigger_t_final[i])
                        temp_operation_ind.append(p_ind_final[i])
                    else:
                        if temp_operaton[-1] == tmp_ope:
                            i = i+1
                            continue
                        else:
                            temp_operaton.append(tmp_ope)
                            temp_operation_t.append(p_trigger_t_final[i])
                            temp_operation_ind.append(p_ind_final[i])
                elif (t_window1 >=7 ) & (t_window1 <=11 ):
                    tmp_ope = 'MediumLow'
                    if len(temp_operaton) == 0:
                        temp_operaton.append(tmp_ope)
                        temp_operation_t.append(p_trigger_t_final[i])
                        temp_operation_ind.append(p_ind_final[i])
                    else:
                        if temp_operaton[-1] == tmp_ope:
                            i = i+1
                            continue
                        else:
                            temp_operaton.append(tmp_ope)
                            temp_operation_t.append(p_trigger_t_final[i])
                            temp_operation_ind.append(p_ind_final[i])
                elif (t_window1 >=13 ) & (t_window1 <=17 ):
                    tmp_ope = 'Medium'
                    if len(temp_operaton) == 0:
                        temp_operaton.append(tmp_ope)
                        temp_operation_t.append(p_trigger_t_final[i])
                        temp_operation_ind.append(p_ind_final[i])
                    else:
                        if temp_operaton[-1] == tmp_ope:
                            i = i+1
                            continue
                        else:
                            temp_operaton.append(tmp_ope)
                            temp_operation_t.append(p_trigger_t_final[i])
                            temp_operation_ind.append(p_ind_final[i])
                elif (t_window1 >=20 ) & (t_window1 <=mv_high_to_stop_criteria ):
                    tmp_ope = 'MediumHigh'
                    if len(temp_operaton) == 0:
                        temp_operaton.append(tmp_ope)
                        temp_operation_t.append(p_trigger_t_final[i])
                        temp_operation_ind.append(p_ind_final[i])
                    else:
                        if temp_operaton[-1] == tmp_ope:
                            i = i+1
                            continue
                        else:
                            temp_operaton.append(tmp_ope)
                            temp_operation_t.append(p_trigger_t_final[i])
                            temp_operation_ind.append(p_ind_final[i])
                elif t_window1 > mv_high_to_stop_criteria:
                    tmp_ope = 'High'
                    temp_operaton.append(tmp_ope)
                    temp_operation_t.append(p_trigger_t_final[i])
                    temp_operation_ind.append(p_ind_final[i])
                else:
                    pass
            i = i + 1
    
    # add the first pulse if it is negative
    if p_area_final[0] < 0:
        if p_height_t_final[0] > mv_high_to_stop_criteria:
            temp_operaton = ['High'] + temp_operaton
            temp_operation_t = [p_trigger_t_final[0]] + temp_operation_t
            temp_operation_ind = [p_ind_final[0]] + temp_operation_ind
        

    
    # If there is small pulse ahead of medium size pulse, find the time of small pulse
    temp_operation_ind = np.array(temp_operation_ind)
    for i, j in enumerate(m_p_ind):
        if j in temp_operation_ind:
            ind = np.where(temp_operation_ind == j)[0][0]
            temp_operation_t[ind] = pulse_trig_t[s_p_ind[i]]
    
    
    # compute mask
    mask_out = np.ones(len(pulse_area),dtype=bool)
    mast_ind = []
    for i in range(0,len(s_p_ind)):
        mast_ind = mast_ind + list(range(s_p_ind[i],m_p_ind[i]))
    mast_ind = mast_ind + list(p_ind_final)
    mast_ind.sort()
    mask_out[mast_ind] = False
    
    
    
    
    operation_comb = []
    operation_t_com = []
    for i, k in enumerate(temp_operaton):
        if i < (len(temp_operaton)-1):
            operation_comb.append(temp_operaton[i] + ' to ' + temp_operaton[i+1])
            operation_t_com.append([temp_operation_t[i],temp_operation_t[i+1]])
    
    operation = []
    operation_t = []
    for i, k in enumerate(operation_comb):
        if (i == 0) & ('start' not in k):
            operation.append(k)
            operation_t.append(operation_t_com[i][0])
        else:
            if 'start' in k:
                if ('stop to start' != k) & ('start to stop' != k):
                    operation.append(k)
                    operation_t.append(operation_t_com[i][0])
                else:
                    continue
            elif 'stop' in k:
                if ('stop to start' != k) & ('start to stop' != k):
                    operation.append(k)
                    operation_t.append(operation_t_com[i][1])
                else:
                    continue
            else:
                operation.append(k)
                operation_t.append(operation_t_com[i][1])
    return exist, operation, operation_t,mask_out