import pandas as pd
import numpy as np
import os
from datetime import datetime
from dap_mrs.src import graphs


def matching(data_input='example_data',
        A_char_number = 4,
        B_char_number = 4,
        bias = False,
        A_char_1_name = 'A_char_1',
        A_char_2_name = 'A_char_2',
        A_char_3_name = 'A_char_3',
        A_char_4_name = 'A_char_4',
        A_bias_char_name = 'A_bias_char',
        A_mrs12_name = 'A_mrs12',
        A_mrs13_name = 'A_mrs13',
        A_mrs14_name = 'A_mrs14',
        B_char_1_name = 'B_char_1',
        B_char_2_name = 'B_char_2',
        B_char_3_name = 'B_char_3',
        B_char_4_name = 'B_char_4',
        B_mrs12_name = 'B_mrs12',
        B_mrs13_name = 'B_mrs13',
        B_mrs14_name = 'B_mrs14',
        B_bias_mrs_name = 'B_bias_mrs',
        A_name = 'Applicants',
        B_name = 'Reviewers',
        spec_name = 'default',
        dap_allocation_vars = False,
        plot_graphs = True,
        save_files = True,
        seed = None):
        
    """
    Perform the Deferred Acceptance Procedure (DAP) based on the data for the agents' characteristics 
    and the marginal rates of substitution (MRS) between the characteristics of their counterparts.

    Parameters
    ----------
    data_input : str or pd.DataFrame, optional
        The dataset to use for the matching process. If 'example_data', a default dataset will be generated. Default is 'example_data'.
    A_char_number : int, optional
        The number of applicants' characteristics. Can take values of 2, 3, or 4. Default is 4.
    B_char_number : int, optional
        The number of reviewers' characteristics. Can take values of 2, 3, or 4. Default is 4.
    bias : bool, optional
        If True, the reviewers' bias will be included in the matching process. Default is False.
    A_char_1_name : str, optional
        The name of the first characteristic of applicants. Default is 'A_char_1'.
    A_char_2_name : str, optional
        The name of the second characteristic of applicants. Default is 'A_char_2'.
    A_char_3_name : str, optional
        The name of the third characteristic of applicants. Default is 'A_char_3'.
    A_char_4_name : str, optional
        The name of the fourth characteristic of applicants. Default is 'A_char_4'.
    A_bias_char_name : str, optional
        The name of the applicants' binary characteristic that the reviewers have a bias towards. Default is 'A_bias_char'.
    A_mrs12_name : str, optional
        The name of the applicants' marginal rate of substitution between the reviewers' first and second characteristics. Default is 'A_mrs12'.
    A_mrs13_name : str, optional
        The name of the applicants' marginal rate of substitution between the reviewers' first and third characteristics. Default is 'A_mrs13'.
    A_mrs14_name : str, optional
        The name of the applicants' marginal rate of substitution between the reviewers' first and fourth characteristics. Default is 'A_mrs14'.
    B_char_1_name : str, optional
        The name of the first characteristic of reviewers. Default is 'B_char_1'.
    B_char_2_name : str, optional
        The name of the second characteristic of reviewers. Default is 'B_char_2'.
    B_char_3_name : str, optional
        The name of the third characteristic of reviewers. Default is 'B_char_3'.
    B_char_4_name : str, optional
        The name of the fourth characteristic of reviewers. Default is 'B_char_4'.
    B_mrs12_name : str, optional
        The name of the reviewers' marginal rate of substitution between the applicants' first and second characteristics. Default is 'B_mrs12'.
    B_mrs13_name : str, optional
        The name of the reviewers' marginal rate of substitution between the applicants' first and third characteristics. Default is 'B_mrs13'.
    B_mrs14_name : str, optional
        The name of the reviewers' marginal rate of substitution between the applicants' first and fourth characteristics. Default is 'B_mrs14'.
    B_bias_mrs_name : str, optional
        The name of the reviewers' bias rate towards the applicants' bias characteristic. Default is 'B_bias_mrs'.
    A_name : str, optional
        The label for applicants in the graphs. Default is 'Applicants'.
    B_name : str, optional
        The label for reviewers in the graphs. Default is 'Reviewers'.
    spec_name : str, optional
        Specification name. Used to name the output files and new variables. Default is 'default'.
    dap_allocation_vars : bool, optional
        If True, in addition to the variables containing applicants' and reviewers' initially assigned indices, 
        the indices of their A-Optimal matches, as well as their characteristics. Default is False.
    plot_graphs : bool, optional
        If True, the output graphs will be plotted. Default is True.
    save_files : bool, optional
        If True, the output files will be saved. Default is True.
    seed : int, optional
        Random seed. If None, the seed will be generated based on the current time. Default is None.

    Returns
    -------
    data_output : pd.DataFrame
        The updated dataset with matching results.
    log : pd.DataFrame
        The log of the matching process.

    Examples
    --------
    >>> import dap_mrs
    >>> my_data_dap, log = dap_mrs.matching(data_input=my_data,
    ...                                     A_char_number=4,
    ...                                     B_char_number=4,
    ...                                     bias=False,
    ...                                     A_char_1_name='A_char_1',
    ...                                     A_char_2_name='A_char_2',
    ...                                     A_char_3_name='A_char_3',
    ...                                     A_char_4_name='A_char_4',
    ...                                     A_bias_char_name='A_bias_char',
    ...                                     A_mrs12_name='A_mrs12',
    ...                                     A_mrs13_name='A_mrs13',
    ...                                     A_mrs14_name='A_mrs14',
    ...                                     B_char_1_name='B_char_1',
    ...                                     B_char_2_name='B_char_2',
    ...                                     B_char_3_name='B_char_3',
    ...                                     B_char_4_name='B_char_4',
    ...                                     B_mrs12_name='B_mrs12',
    ...                                     B_mrs13_name='B_mrs13',
    ...                                     B_mrs14_name='B_mrs14',
    ...                                     B_bias_mrs_name='B_bias_mrs',
    ...                                     A_name='Applicants',
    ...                                     B_name='Reviewers',
    ...                                     spec_name='default',
    ...                                     dap_allocation_vars=False,
    ...                                     plot_graphs=True,
    ...                                     save_files=True,
    ...                                     seed=None)

    """

    print()
    print('Loading the data...')

    # default dataset
    if isinstance(data_input, str) and data_input == 'example_data':
        if seed == None:
            np.random.seed(int(str(datetime.now())[17:19]))
        else:
            np.random.seed(seed)
        data_input = pd.DataFrame({'A_char_1': np.random.normal(50, 10, 200),
                                    'A_char_2': np.random.normal(50, 10, 200),
                                    'A_char_3': np.random.normal(50, 10, 200),
                                    'A_char_4': np.random.normal(50, 10, 200),
                                    'A_mrs12': [1.75] * 200,
                                    'A_mrs13': [1.25] * 200,
                                    'A_mrs14': [0.75] * 200,
                                    'B_char_1': np.random.normal(50, 10, 200),
                                    'B_char_2': np.random.normal(50, 10, 200),
                                    'B_char_3': np.random.normal(50, 10, 200),
                                    'B_char_4': np.random.normal(50, 10, 200),
                                    'B_mrs12': [1.75] * 200,
                                    'B_mrs13': [1.25] * 200,
                                    'B_mrs14': [0.75] * 200,
                                    'A_bias_char': np.random.binomial(1, 0.5, 200),
                                    'B_bias_mrs': [-25] * 200})
        
    # All reviewers are unmatched indicator
    all_matched = False

    # Create log dataframe
    log = pd.DataFrame(columns=['iterat',
                                'A_match_count', 
                                'A_unmatch_count', 
                                'B_match_count', 
                                'B_unmatch_count', 
                                'A_match_utlity_mean', 
                                'B_match_utlity_mean'])

    # ---------------------------------------------------------------
    # DATA PREPARATION
    # ---------------------------------------------------------------

    if A_char_number == 3:
        data_input[A_char_4_name] = 0
        data_input[B_mrs14_name] = 0
    elif A_char_number == 2:
        data_input[A_char_3_name] = 0
        data_input[B_mrs13_name] = 0
        data_input[A_char_4_name] = 0
        data_input[B_mrs14_name] = 0

    if B_char_number == 3:
        data_input[B_char_4_name] = 0
        data_input[A_mrs14_name] = 0
    elif B_char_number == 2:
        data_input[B_char_3_name] = 0
        data_input[A_mrs13_name] = 0
        data_input[B_char_4_name] = 0
        data_input[A_mrs14_name] = 0

    if bias == False:
        data_input[A_bias_char_name] = 0
        data_input[B_bias_mrs_name] = 0

    A = {   'id'            : data_input.index,
            'char_1'        : data_input[A_char_1_name],
            'char_2'        : data_input[A_char_2_name],
            'char_3'        : data_input[A_char_3_name],
            'char_4'        : data_input[A_char_4_name],
            'bias_char'     : data_input[A_bias_char_name],
            'mrs12'         : data_input[A_mrs12_name],
            'mrs13'         : data_input[A_mrs13_name],
            'mrs14'         : data_input[A_mrs14_name],
            'match'         : [None] * len(data_input.index),
            'match_utility' : [0] * len(data_input.index)}
    A = pd.DataFrame(A)

    B = {   'id'            : data_input.index,
            'char_1'        : data_input[B_char_1_name],
            'char_2'        : data_input[B_char_2_name],
            'char_3'        : data_input[B_char_3_name],
            'char_4'        : data_input[B_char_4_name],
            'mrs12'         : data_input[B_mrs12_name],
            'mrs13'         : data_input[B_mrs13_name],
            'mrs14'         : data_input[B_mrs14_name],
            'bias_mrs'      : data_input[B_bias_mrs_name],
            'match'         : [None] * len(data_input.index),
            'match_utility' : [0] * len(data_input.index)}
    B = pd.DataFrame(B)

    # print a message acknowledging the input data
    print()
    print('Data is loaded')
    print('---------------------------------------------------------------')
    print(A_name + ' characteristics: ', A_char_1_name, A_char_2_name, A_char_3_name, A_char_4_name)
    print(A_name + ' MRS: ', A_mrs12_name, A_mrs13_name, A_mrs14_name)
    print(B_name + ' characteristics: ', B_char_1_name, B_char_2_name, B_char_3_name, B_char_4_name)
    print(B_name + ' MRS: ', B_mrs12_name, B_mrs13_name, B_mrs14_name)
    print('Market size: ', len(A['id']))
    print('Bias: ', bias)
    if bias == True:
        print(B_name + ' are biased towards ' + A_name + ' with ' + A_bias_char_name + ' = 1') 
        print('at the average rate of ' + str(round(B['bias_mrs'].mean(),2)))
    print('---------------------------------------------------------------')

    # ---------------------------------------------------------------
    # MATCHING
    # ---------------------------------------------------------------

    print()
    print('Starting the matching process...')
    print()

    # define applicant's choice rank
    q = 1

    # Initialize iteration counter
    iterat = 0 
    q_reset_count = 0
    
    # while not all reviewers are matched
    while all_matched == False:
        iterat += 1
        
        # print progress every 10 iterations
        if iterat % 10 == 0:
            print(f'Progress: {round(iterat/len(A)*100, 2)}%')

        breakups_count = 0
        rejections_count = 0
        pass_matched_count = 0
        # A apply for their qth best
        for i in A['id']:
            # if i is not matched
            if A['match'].loc[A['id'] == i].values[0] == None:
                # generate i's network
                network = {'id': B['id'],
                        'char_1': B['char_1'],
                        'char_2': B['char_2'],
                        'char_3': B['char_3'],
                        'char_4': B['char_4'],
                        'utility': B['char_1']  + (B['char_2'] * A['mrs12'])
                                                + (B['char_3'] * A['mrs13'])
                                                + (B['char_4'] * A['mrs14'])} 
                
                # sort network by utility
                network = pd.DataFrame(network).sort_values('utility', ascending=False)
                #print(network)

                # find the qth best reviewer's id
                qth_best_id = network.iloc[q-1]['id']

                # if the reviewer is available
                if B['match'][B['id'] == qth_best_id].values[0] == None:
                    # match occurs
                    A.loc[A['id'] == i, 'match'] = qth_best_id
                    A.loc[A['id'] == i, 'match_utility'] = (B.loc[B['id'] == qth_best_id, 'char_1'].values[0]
                                                         +  B.loc[B['id'] == qth_best_id, 'char_2'].values[0] *  A.loc[A['id'] == i, 'mrs12'].values[0]
                                                         +  B.loc[B['id'] == qth_best_id, 'char_3'].values[0] *  A.loc[A['id'] == i, 'mrs13'].values[0]
                                                         +  B.loc[B['id'] == qth_best_id, 'char_4'].values[0] *  A.loc[A['id'] == i, 'mrs14'].values[0])
                    B.loc[B['id'] == qth_best_id, 'match'] = i
                    B.loc[B['id'] == qth_best_id, 'match_utility'] = (A.loc[A['id'] == i, 'char_1'].values[0]
                                                                   +  A.loc[A['id'] == i, 'char_2'].values[0] * B.loc[B['id'] == qth_best_id, 'mrs12'].values[0]
                                                                   +  A.loc[A['id'] == i, 'char_3'].values[0] * B.loc[B['id'] == qth_best_id, 'mrs13'].values[0]
                                                                   +  A.loc[A['id'] == i, 'char_4'].values[0] * B.loc[B['id'] == qth_best_id, 'mrs14'].values[0]
                                                                   +  A.loc[A['id'] == i, 'bias_char'].values[0] * B.loc[B['id'] == qth_best_id, 'bias_mrs'].values[0])
                # else if the reviewer is matched
                if B['match'][B['id'] == qth_best_id].values[0] != None:
                    # find the current applicant
                    current_applicant = B['match'][B['id'] == qth_best_id].values[0]
                    # calc the utility of matching the current applicavnt
                    current_applicant_utility = (A['char_1'][A['id'] == current_applicant].values[0] 
                                              +  A['char_2'][A['id'] == current_applicant].values[0] * B['mrs12'][B['id'] == qth_best_id].values[0]
                                              +  A['char_3'][A['id'] == current_applicant].values[0] * B['mrs13'][B['id'] == qth_best_id].values[0]
                                              +  A['char_4'][A['id'] == current_applicant].values[0] * B['mrs14'][B['id'] == qth_best_id].values[0]
                                              +  A['bias_char'][A['id'] == current_applicant].values[0] * B['bias_mrs'][B['id'] == qth_best_id].values[0])
                    # calc the utility of matching i
                    i_utility = (A['char_1'][A['id'] == i].values[0] 
                              +  A['char_2'][A['id'] == i].values[0] * B['mrs12'][B['id'] == qth_best_id].values[0]
                              +  A['char_3'][A['id'] == i].values[0] * B['mrs13'][B['id'] == qth_best_id].values[0]
                              +  A['char_4'][A['id'] == i].values[0] * B['mrs14'][B['id'] == qth_best_id].values[0]
                              +  A['bias_char'][A['id'] == i].values[0] * B['bias_mrs'][B['id'] == qth_best_id].values[0])
                    # if i provides higher utility than the current applicant
                    if i_utility > current_applicant_utility:
                        # current applicant is unmatched
                        A.loc[A['id'] == current_applicant, 'match'] = None
                        A.loc[A['id'] == current_applicant, 'match_utility'] = 0
                        breakups_count += 1
                        # i is matched
                        A.loc[A['id'] == i, 'match'] = qth_best_id
                        A.loc[A['id'] == i, 'match_utility'] = (B.loc[B['id'] == qth_best_id, 'char_1'].values[0]
                                                             +  B.loc[B['id'] == qth_best_id, 'char_2'].values[0] * A.loc[A['id'] == i, 'mrs12'].values[0]
                                                             +  B.loc[B['id'] == qth_best_id, 'char_3'].values[0] * A.loc[A['id'] == i, 'mrs13'].values[0]
                                                             +  B.loc[B['id'] == qth_best_id, 'char_4'].values[0] * A.loc[A['id'] == i, 'mrs14'].values[0])
                        B.loc[B['id'] == qth_best_id, 'match'] = i
                        B.loc[B['id'] == qth_best_id, 'match_utility'] = i_utility
                    # else if i provides lower utility than the current applicant
                    if i_utility < current_applicant_utility:
                        # i stays u nmmatched and qth best reviewer stays matched with the current applicant
                        rejections_count += 1
            # if i is matched
            elif A['match'][A['id'] == i].values[0] != None:
                # move to the next applicant
                pass_matched_count += 1
        # update applicant's choice rank
        if q < len(B['id']):
            q += 1
        elif q == len(B['id']):
            q = 1
            q_reset_count += 1

        # update log
        log_entry = {'iterat': iterat,
                     'A_match_count': len(A['match'])-A['match'].isna().sum(),
                     'A_unmatch_count': A['match'].isna().sum(),
                     'B_match_count': len(B['match'])-B['match'].isna().sum(),
                     'B_unmatch_count': B['match'].isna().sum(),
                     'A_match_utlity_mean': A['match_utility'].mean(),
                     'B_match_utlity_mean': B['match_utility'].mean(),
                     'breakups_count': breakups_count,
                     'q_reset_count': q_reset_count,
                     'rejections_count': rejections_count,
                     'pass_matched_count': pass_matched_count}
        log = pd.concat([log, pd.DataFrame([log_entry]).dropna(axis=1, how='all')], ignore_index=True)

        # check if all reviewers are matched
        if None in B['match'].unique():
            all_matched = False
        else:
            all_matched = True

        if iterat > 1000:
            all_matched = True

    print()
    print(f'Progress: {iterat} iterations completed')
    print('All reviewers are matched')
    
    print()
    print('Compiling the results...')

    # ---------------------------------------------------------------
    # RESULTS
    # ---------------------------------------------------------------

    data_output = data_input.copy()
    
    # update the dataset with the matching results
    if dap_allocation_vars == True:
        B_dap_sorted = B.set_index('match', drop=False)
        B_dap_sorted.sort_index(inplace=True)
        data_output[spec_name + '_init_id'] = data_input.index
        data_output[spec_name + '_dap_asgn_B_id'] = A['match']
        data_output[spec_name + '_dap_' + B_char_1_name] = B_dap_sorted['char_1']
        data_output[spec_name + '_dap_' + B_char_2_name] = B_dap_sorted['char_2']
        data_output[spec_name + '_dap_' + B_char_3_name] = B_dap_sorted['char_3']
        data_output[spec_name + '_dap_' + B_char_4_name] = B_dap_sorted['char_4']
    
    # payoffs
    data_output[spec_name + '_A_obs_u'] = B['char_1'] + B['char_2'] * A['mrs12'] + B['char_3'] * A['mrs13'] + B['char_4'] * A['mrs14']
    data_output[spec_name + '_B_obs_u'] = A['char_1'] + A['char_2'] * B['mrs12'] + A['char_3'] * B['mrs13'] + A['char_4'] * B['mrs14']
    data_output[spec_name + '_A_dap_u'] = A['match_utility']
    data_output[spec_name + '_B_dap_u'] = B['match_utility']

    # post DAP biased allocation
    if bias == True:
        B_dap_sorted = B.set_index('match', drop=False)
        B_dap_sorted.sort_index(inplace=True)
        data_output[spec_name + '_init_id'] = data_input.index
        data_output[spec_name + '_bidap_asgn_B_id'] = A['match']
        data_output[spec_name + '_bidap_' + B_char_1_name] = B_dap_sorted['char_1']
        data_output[spec_name + '_bidap_' + B_char_2_name] = B_dap_sorted['char_2']
        data_output[spec_name + '_bidap_' + B_char_3_name] = B_dap_sorted['char_3']
        data_output[spec_name + '_bidap_' + B_char_4_name] = B_dap_sorted['char_4']
        data_output[spec_name + '_bidap_A_aprnt_v']        = B_dap_sorted['match_utility']
        data_output[spec_name + '_bidap_A_aprnt_crct_v']   = B_dap_sorted['match_utility'] - A['bias_char'] * B_dap_sorted['bias_mrs']

    # calculate z-scores for observed payoffs
    data_output[spec_name + '_A_obs_u_z'] = (data_output[spec_name + '_A_obs_u'] - data_output[spec_name + '_A_obs_u'].mean())/data_output[spec_name + '_A_obs_u'].std()
    data_output[spec_name + '_B_obs_u_z'] = (data_output[spec_name + '_B_obs_u'] - data_output[spec_name + '_B_obs_u'].mean())/data_output[spec_name + '_B_obs_u'].std()

    # calculate z-scores for dap payoffs
    data_output[spec_name + '_A_dap_u_z'] = (data_output[spec_name + '_A_dap_u'] - data_output[spec_name + '_A_dap_u'].mean())/data_output[spec_name + '_A_dap_u'].std()
    data_output[spec_name + '_B_dap_u_z'] = (data_output[spec_name + '_B_dap_u'] - data_output[spec_name + '_B_dap_u'].mean())/data_output[spec_name + '_B_dap_u'].std()

    # calculate difference between observed and dap payoffs
    data_output[spec_name + '_diff_A'] = data_output[spec_name + '_A_obs_u'] - data_output[spec_name + '_A_dap_u']
    data_output[spec_name + '_diff_B'] = data_output[spec_name + '_B_obs_u'] - data_output[spec_name + '_B_dap_u']

    # calculate z-scores for diff_A and diff_B
    data_output[spec_name + '_diff_A_z'] = (data_output[spec_name + '_diff_A'] - data_output[spec_name + '_diff_A'].mean())/data_output[spec_name + '_diff_A'].std()
    data_output[spec_name + '_diff_B_z'] = (data_output[spec_name + '_diff_B'] - data_output[spec_name + '_diff_B'].mean())/data_output[spec_name + '_diff_B'].std() 
    
    # calculate z-scores for apparent values
    if bias == True:
        data_output[spec_name + '_bidap_A_aprnt_v_z']           = (data_output[spec_name + '_bidap_A_aprnt_v'] - data_output[spec_name + '_bidap_A_aprnt_v'].mean())/data_output[spec_name + '_bidap_A_aprnt_v'].std()
        data_output[spec_name + '_bidap_A_aprnt_crct_v_z'] = (data_output[spec_name + '_bidap_A_aprnt_crct_v'] - data_output[spec_name + '_bidap_A_aprnt_crct_v'].mean())/data_output[spec_name + '_bidap_A_aprnt_crct_v'].std()

    # drop unnecessary columns
    if A_char_number == 3:
        data_output.drop(columns=[A_char_4_name, B_mrs14_name], inplace=True)
    
    elif A_char_number == 2:
        data_output.drop(columns=[A_char_3_name, B_mrs13_name, 
                                  A_char_4_name, B_mrs14_name], inplace=True)
    if B_char_number == 3:
        data_output.drop(columns=[B_char_4_name, A_mrs14_name], inplace=True)
        if dap_allocation_vars == True:
            data_output.drop(columns=[spec_name + '_dap_' + B_char_4_name], inplace=True)
        if bias == True:
            data_output.drop(columns=[spec_name + '_bidap_' + B_char_4_name], inplace=True)

    elif B_char_number == 2:
        data_output.drop(columns=[B_char_3_name, A_mrs13_name,
                                    B_char_4_name, A_mrs14_name], inplace=True)
        if dap_allocation_vars == True:
            data_output.drop(columns=[spec_name + '_dap_' + B_char_3_name,
                                      spec_name + '_dap_' + B_char_4_name], inplace=True)
        if bias == True:
            data_output.drop(columns=[spec_name + '_bidap_' + B_char_3_name,
                                      spec_name + '_bidap_' + B_char_4_name], inplace=True)

    if bias == False:
        data_output.drop(columns=[A_bias_char_name, B_bias_mrs_name], inplace=True)


    if plot_graphs == True:
        
        graphs.available_payoffs(data_input = data_output,
                                 spec_name = spec_name, 
                                 A_name = A_name,
                                 B_name = B_name,
                                 save_graph=save_files,
                                 extension='svg')
        
        graphs.observed_vs_dap(data_input = data_output,
                                 spec_name = spec_name, 
                                 A_name = A_name,
                                 B_name = B_name,
                                 save_graph=save_files,
                                 extension='svg')

        if bias == True:
            
            graphs.apparent_values(data_input = data_output,
                                   spec_name = spec_name, 
                                   A_name = A_name,
                                   A_bias_char_name = A_bias_char_name,
                                   save_graph=save_files,
                                   extension='svg')
            
            graphs.bias_effect(data_input = data_output,
                                spec_name = spec_name, 
                                A_name = A_name,
                                A_bias_char_name = A_bias_char_name,
                                save_graph=save_files,
                                extension='svg')
        
    # ---------------------------------------------------------------
    # SAVE OUTPUT FILES
    # ---------------------------------------------------------------

    if save_files == True:
        data_output.to_csv(spec_name + '_data_output.csv', index=False)
        print()
        print(spec_name + '_data_output.csv is saved to ', os.getcwd())
        log.to_csv(spec_name + '_log.csv', index=False)
        print(spec_name + '_log.csv is saved to ', os.getcwd())
    
    return data_output, log