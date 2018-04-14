def yd2_detector(pulse_area,pulse_trig_t,pulse_heith_t,pulse_end_t,pulse_h):
    '''
    Author - D.Q. Huang - 20180413
    Input : pulse_area, pulse_trig_t, pulse_heith_t, pulse_end_t, pulse_h,  i.e.
            The characteristics of the pulses identified by the characterize_pulse function. 
    Output : Exist: boolean. If True, then yd3 is decteted. If False, then yd3 is not detected.
             operation : list of tuples. Each tuple contains two values: one is the operation, the other is the operation time.
             mask : numpy array that put False at the location where yd3 pulse is.
    Note: version with paring
    '''
    # parameter section *****************
    area_ub1 = 12000 # total pulse upper bound
    area_lb1 = 9500  # total pulse lower bound
    mw_pulse_thresh = 7000
    #area_ub2 = 9700  # second biggest pulse uppper bound
    #area_lb2 = 8500  # second biggest pulse lower bound
    #area_ub3 = 2000  # smallest pulse upper bound
    #area_lb3 = 1200  # smallest pulse lower bound
    area_criteria = 500 # lowest bound
    
    s_m_p_t_diff_lb = 2
    s_m_p_t_diff_ub = 4
    
    # to check whether mw is stoped or not. This parameter need to be varied due to a non-fixalbe bug
    mw_turn_off_t_criteria = 60
    
    # this parameter is to just whether the mv in 高火 state
    mv_high_stop_criteria = 25
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
    for i in range(0, len(p_height_t)):
        if p_area_indef[i] < 0:
            if (p_area_indef[i] < -area_lb1) & (p_area_indef[i] > -area_ub1):
                continue
            else:
                mask_pre[i] = False
                continue
        if p_area_indef[i] > 0:
            t_temp = p_height_t_indef[i]
            t_w = [t_temp-s_m_p_t_diff_ub, t_temp-s_m_p_t_diff_lb]
            window_cut = (pulse_heith_t >= t_w[0]) & (pulse_heith_t <= t_w[1])
            if any(pulse_area[window_cut] > area_criteria):
                tot_s = pulse_area[window_cut] + p_area_indef[i]
                if any((tot_s < area_ub1) & (tot_s > area_lb1)):
                    s_p_ind.append(np.where(window_cut & (pulse_area > 500))[0][0])
                    m_p_ind.append(p_index_indef[i])
                    # print(p_area_indef[i])
                    continue
                else:
                    mask_pre[i] = False
                    continue
            elif (p_area_indef[i] < area_ub1) & (p_area_indef[i] > area_lb1):
                continue

    p_index_semi_def = p_index_indef[mask_pre]
    p_height_t_semi_def = p_height_t_indef[mask_pre]
    p_area_semi_def = p_area_indef[mask_pre]
    
    # second round of microwave pulse index check - pulse paring, i.e. first positive pulse pairs up with first negative pulse and then continue
    temp_p_ind_final = []
    i = 0
    while i < len(p_area_semi_def):
        if (i == 0) & (p_area_semi_def[i] < 0):
            temp_p_ind_final.append(i)
            i=i+1
        elif (p_area_semi_def[i] > 0):
            for j in range(1,len(p_area_semi_def)):
                if i+j >= len(p_area_semi_def):
                    break
                if p_area_semi_def[i+j] < 0:
                    break
            if i+j >= len(p_area_semi_def):
                temp_p_ind_final.append(i)
                break
            temp_p_ind_final.append(i)
            temp_p_ind_final.append(i+j)
            i=i+j+1
        else:
            i=i+1
            pass

    # test whether microwave exsit nor not by checking how many pulses are
    p_ind_final = p_index_semi_def[temp_p_ind_final]
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
                if t_window1 > mv_high_stop_criteria:
                    temp_operaton.append('高火')
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
                    if t_window1 > mv_high_stop_criteria:
                        tmp_ope = '高火'
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
                    tmp_ope = '低火'
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
                    tmp_ope = '中低火'
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
                    tmp_ope = '中火'
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
                elif (t_window1 >=20 ) & (t_window1 <=23 ):
                    tmp_ope = '中高火'
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
                elif t_window1 > mv_high_stop_criteria:
                    tmp_ope = '高火'
                    temp_operaton.append(tmp_ope)
                    temp_operation_t.append(p_trigger_t_final[i])
                    temp_operation_ind.append(p_ind_final[i])
            i = i + 1
    
    # add the first pulse if it is negative
    if p_area_final[0] < 0:
        if p_height_t_final[0] > mv_high_stop_criteria:
            temp_operaton = ['高火'] + temp_operaton
            temp_operation_t = [p_trigger_t_final[0]] + temp_operation_t
            temp_operation_ind = [p_ind_final[0]] + temp_operation_ind
        
        
    
    
    
    # If there is small pulse ahead of medium size pulse, find the time of small pulse
    temp_operation_ind = np.array(temp_operation_ind)
    for i, j in enumerate(m_p_ind):
        if j in temp_operation_ind:
            ind = np.where(temp_operation_ind == j)[0][0]
            temp_operation_t[ind] = pulse_trig_t[s_p_ind[i]]
    
    
    
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
    return exist, operation, operation_t