import pandas as pd
import numpy as np
import os

def init_feature_frame(instruOp=[], n=10):
    # author - D.Q. Huang
    # this funtion initilize feature(pulse) pandas dataFrame
    # the dataFrame is initilized based on provided data
    # some of the operation that no exsit in provided data and will be manually added into the dataFrame
    # each operation name is coded in a way: "instrument: preState_operation_postState"
    # input: 
    #       instruOp - a [list] of instruction operation
    #       n - maximum number of pulses in each transition
    # output:
    #       pulse_area_df (0 at invalid values)
    #       pulse_time_df (999999 at invalid values)
    #       pulse_width_df (999999 at invalid values)
    #       pulse_height_df (0 at invalid values)
    # Note that this function is no longer used to creat the database but just dataFrame in ipython notebook
    # use init_feature_db to initilize the databaes
    if type(instruOp) is pd.core.frame.DataFrame:
        instruOp = instruOp['设备操作']
    d = {'设备操作': instruOp}
    pulse_area_df = pd.DataFrame(d)
    pulse_time_df= pd.DataFrame(d)
    pulse_width_df = pd.DataFrame(d)
    pulse_height_df = pd.DataFrame(d)
    for i in range(1,n+1): 
        pulse_area_df['pulse'+str(i)] = np.zeros(len(pulse_area_df))
        pulse_time_df['pulse'+str(i)] = np.ones(len(pulse_time_df))*999999
        pulse_width_df['pulse'+str(i)] = np.ones(len(pulse_width_df))*999999
        pulse_height_df['pulse'+str(i)] = np.zeros(len(pulse_height_df))
    
    return [pulse_area_df,pulse_time_df,pulse_width_df,pulse_height_df]


def init_feature_db(database_file, n=10):
    # author - D.Q. Huang
    # most same as init_feature_frame
    # input:
    #      database_file --> data file
    #      n --> maximum number of pulses to store in each operation
    # output:
    #       save the following into db
    #           pulse_area_df (0 at invalid values)
    #           pulse_time_df (999999 at invalid values)
    #           pulse_width_df (999999 at invalid values)
    #           pulse_height_df (0 at invalid values)
    #       return True
    d = {'设备操作': []}
    pulse_area_df = pd.DataFrame(d)
    pulse_time_df= pd.DataFrame(d)
    pulse_width_df = pd.DataFrame(d)
    pulse_height_df = pd.DataFrame(d)
    for i in range(1,n+1): 
        pulse_area_df['pulse'+str(i)] = np.zeros(len(pulse_area_df))
        pulse_time_df['pulse'+str(i)] = np.ones(len(pulse_time_df))*999999
        pulse_width_df['pulse'+str(i)] = np.ones(len(pulse_width_df))*999999
        pulse_height_df['pulse'+str(i)] = np.zeros(len(pulse_height_df))
    writer = pd.ExcelWriter(database_file)
    pulse_area_df.to_excel(writer,'pulse_area_df')
    pulse_width_df.to_excel(writer,'pulse_width_df')
    pulse_height_df.to_excel(writer,'pulse_height_df')
    pulse_time_df.to_excel(writer,'pulse_time_df')
    writer.save()
    
    return True

def read_feature_db(database_file):
    # author - D.Q. Huang
    # read feature database if exist
    # otherwise, initilize feature database
    # input:
    #      database_file --> database file path
    # Readme:
    #       type in: Yes ---> database dones not exsit and create an new database
    #       type in: No ----> database dones not exsit and does not create an new database
    if os.path.isfile(database_file) is True:
        db = pd.ExcelFile(database_file)
        pulse_area_df = db.parse('pulse_area_df')
        pulse_width_df = db.parse('pulse_width_df')
        pulse_height_df = db.parse('pulse_height_df')
        pulse_time_df = db.parse('pulse_time_df')
    else:
        '''
        yn = input("Database does not exsit. \nDo you want to initilize feature database Excel?(only Yes/No) ")
        if yn == 'Yes':
            [pulse_area_df,pulse_time_df,pulse_width_df,pulse_height_df] = init_feature_frame()
            writer = pd.ExcelWriter(database_file)
            pulse_area_df.to_excel(writer,'pulse_area_df')
            pulse_width_df.to_excel(writer,'pulse_width_df')
            pulse_height_df.to_excel(writer,'pulse_height_df')
            pulse_time_df.to_excel(writer,'pulse_time_df')
            writer.save()
            return [pulse_area_df, pulse_width_df, pulse_height_df,pulse_time_df]
        else:
            print('Database is not initilized')
            pulse_area_df = None
            pulse_width_df = None
            pulse_height_df = None
            pulse_time_df = None
        '''
        print('Warninng!!!: Database does not exsit or Wrong input file name \nPlease check or Initilize DB')
        pulse_area_df = None
        pulse_width_df = None
        pulse_height_df = None
        pulse_time_df = None
    return [pulse_area_df, pulse_width_df, pulse_height_df,pulse_time_df]


def get_operation_list(operation_data):
    # author: D.Q. Huang
    # input: 
    #       operation_data - a list of operation_data pandas df (loaded from Excel)
    if type(operation_data) is not list:
        operation_data = [operation_data]
    instruOp = []
    for i in range(0, len(operation_data)):
        op_n = len(operation_data[i])
        for j in range(1, op_n):
            each_Op = operation_data[i]['设备'][j] + ': ' + operation_data[i]['工作状态'][j-1] \
            + ' ' + operation_data[i]['操作'][j] + ' ' + operation_data[i]['工作状态'][j]
            instruOp.append(each_Op)
    d = {'设备操作': instruOp}
    return pd.DataFrame(d)






def insert_entry_into_database(database_file, op, p_area_df, p_width_df, p_height_df, p_time_df, input_ind = -1):
    # author - D.Q. Huang
    # This function insert an given entry, i.e. operation with pulse area, etc. into database
    # steps: 
    # this function (only allow insert one entry once)
    #             1. read database (Excel) into pandas df 
    #             2.insert an entry into df
    #             3. save updated df into database (Excel) by replacing the old one 
    # inputs:
    #       db_file (str) - database path
    #       op (str) - operation, obtained from operation_data (from Excel)
    #       p_area_df, p_width_df, p_height_df, p_time_df (numpy array) - obtained mannually
    #          - these are the four features relevant to the pulses for a given operaiton
    #          - pulse_area_df (0 at invalid values)
    #          - pulse_time_df (999999 at invalid values)
    #          - pulse_width_df (999999 at invalid values)
    #          - pulse_height_df (0 at invalid values)
    # output:
    #        if insert successfully, return True; otherwise return False
    if type(p_area_df) is not np.ndarray:
        p_area_df = np.array(p_area_df)
    if type(p_width_df) is not np.ndarray:
        p_width_df = np.array(p_width_df)
    if type(p_height_df) is not np.ndarray:
        p_height_df = np.array(p_height_df)
    if type(p_time_df) is not np.ndarray:
        p_time_df = np.array(p_time_df)
    if type(input_ind) is not int:
        print('input_ind must be integer')
        return -1
    
    if os.path.isfile(database_file) is False:
        print('Warning, Database does not exsit, please initilize database first by \nusing init_feature_db function')
        return_value = False
    else:
        [pulse_area_df, pulse_width_df, pulse_height_df,pulse_time_df] = read_feature_db(database_file)
        if (pulse_area_df['设备操作'].values == op).any():
            yn = input(op +' has existed in database. Do you want to replace it? \n(Yes/No)')
            if yn == 'Yes':
                ind = np.where(pulse_area_df['设备操作'].values == op)
                
                area_initial_entry = np.zeros(pulse_area_df.shape[1]-1)
                area_initial_entry[0:len(p_area_df)] = p_area_df
                pulse_area_df.loc[ind] = [op] + list(area_initial_entry)
                
                width_initial_entry = 999999*np.ones(pulse_width_df.shape[1]-1)
                width_initial_entry[0:len(p_width_df)] = p_width_df
                pulse_width_df.loc[ind] = [op] + list(width_initial_entry)
                
                height_initial_entry = np.zeros(pulse_height_df.shape[1]-1)
                height_initial_entry[0:len(p_height_df)] = p_height_df
                pulse_height_df.loc[ind] = [op] + list(height_initial_entry)
                
                time_initial_entry = 999999*np.ones(pulse_time_df.shape[1]-1)
                time_initial_entry[0:len(p_time_df)] = p_time_df
                pulse_time_df.loc[ind] = [op] + list(time_initial_entry)
                
                writer = pd.ExcelWriter(database_file)
                pulse_area_df.to_excel(writer,'pulse_area_df')
                pulse_width_df.to_excel(writer,'pulse_width_df')
                pulse_height_df.to_excel(writer,'pulse_height_df')
                pulse_time_df.to_excel(writer,'pulse_time_df')
                writer.save()
                
                return_value = True
            else:
                print('Data is not inserted into database')
                return_value = False
        else:
            ind = pulse_area_df.shape[0]
            
            area_initial_entry = np.zeros(pulse_area_df.shape[1]-1)
            area_initial_entry[0:len(p_area_df)] = p_area_df
            pulse_area_df.loc[ind] = [op] + list(area_initial_entry)

            width_initial_entry = 999999*np.ones(pulse_width_df.shape[1]-1)
            width_initial_entry[0:len(p_width_df)] = p_width_df
            pulse_width_df.loc[ind] = [op] + list(width_initial_entry)

            height_initial_entry = np.zeros(pulse_height_df.shape[1]-1)
            height_initial_entry[0:len(p_height_df)] = p_height_df
            pulse_height_df.loc[ind] = [op] + list(height_initial_entry)

            time_initial_entry = 999999*np.ones(pulse_time_df.shape[1]-1)
            time_initial_entry[0:len(p_time_df)] = p_time_df
            pulse_time_df.loc[ind] = [op] + list(time_initial_entry)
            
            if input_ind > 0:
                pulse_area_df.iloc[(input_ind+1):] = pulse_area_df.iloc[input_ind:-1]
                pulse_area_df.iloc[input_ind] = area_initial_entry
                
                pulse_width_df.iloc[(input_ind+1):] = pulse_width_df.iloc[input_ind:-1]
                pulse_width_df.iloc[input_ind] = width_initial_entry
                
                pulse_height_df.iloc[(input_ind+1):] = pulse_height_df.iloc[input_ind:-1]
                pulse_height_df.iloc[input_ind] = height_initial_entry
                
                pulse_time_df.iloc[(input_ind+1):] = pulse_time_df.iloc[input_ind:-1]
                pulse_time_df.iloc[input_ind] = time_initial_entry
                
            writer = pd.ExcelWriter(database_file)
            pulse_area_df.to_excel(writer,'pulse_area_df')
            pulse_width_df.to_excel(writer,'pulse_width_df')
            pulse_height_df.to_excel(writer,'pulse_height_df')
            pulse_time_df.to_excel(writer,'pulse_time_df')
            writer.save()

    return return_value



