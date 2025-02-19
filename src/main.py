import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from ridgeplot import ridgeplot
import kaleido
from datetime import datetime

def two_features(data_input='example_data',
        A_char_1_name = 'A_char_1',
        A_char_2_name = 'A_char_2',
        A_mrs_name = 'A_mrs',
        B_char_1_name = 'B_char_1',
        B_char_2_name = 'B_char_2',
        B_mrs_name = 'B_mrs',
        A_name='A',
        B_name='B',
        spec_name='default',
        extra_vars=False,
        graphs=True,
        save_files=True):
        
    """
    Perform the Deferred Acceptance Procedure (DAP) based on the data for the agents' characteristics and the marginal rate of substitution (MRS) between the characteristics of their counterparts.

    Parameters
    ----------
    data_input : str or pd.DataFrame, optional
        The dataset to use for the matching process. If 'example_data', a default dataset will be generated. Default is 'example_data'.
    A_char_1_name : str, optional
        The name of the first characteristic for applicants. Default is 'A_char_1'.
    A_char_2_name : str, optional
        The name of the second characteristic for applicants. Default is 'A_char_2'.
    A_mrs_name : str, optional
        The name of the marginal rate of substitution for applicants. Default is 'A_mrs'.
    B_char_1_name : str, optional
        The name of the first characteristic for reviewers. Default is 'B_char_1'.
    B_char_2_name : str, optional
        The name of the second characteristic for reviewers. Default is 'B_char_2'.
    B_mrs_name : str, optional
        The name of the marginal rate of substitution for reviewers. Default is 'B_mrs'.
    A_name : str, optional
        The label for applicants in the graphs. Default is 'A'.
    B_name : str, optional
        The label for reviewers in the graphs. Default is 'B'.
    spec_name : str, optional
        Specification name. Used to name the output files and new variables. Default is 'default'.
    extra_vars : bool, optional
        If True, in addition to the variables containing the payoffs, z-scores, and the difference 
        between the observed and DAP-generated payoffs and their z-scores, the output file will also 
        contain applicants' and reviewers' initially assigned indices and the indices of their matches. 
        Default is False.
    graphs : bool, optional
        If True, the output graphs will be displayed. Default is True.
    save_files : bool, optional
        If True, the output files will be saved. Default is True.

    Returns
    -------
    data_output : pd.DataFrame
        The updated dataset with matching results.
    log : pd.DataFrame
        The log of the matching process.

    Examples
    --------
    >>> two_features()
    >>> two_features(data_input=my_dataframe, 
                    A_char_1_name = 'A_char_1',
                    A_char_2_name = 'A_char_2',
                    A_mrs_name = 'A_mrs',
                    B_char_1_name = 'B_char_1',
                    B_char_2_name = 'B_char_2',
                    B_mrs_name = 'B_mrs',
                    A_name='A',
                    B_name='B',
                    spec_name='default',
                    extra_vars=False,
                    graphs=True,
                    save_files=True)
    """
    
    # default dataset
    if isinstance(data_input, str) and data_input == 'example_data':
        np.random.seed(0)
        data_input = pd.DataFrame({'A_char_1': np.random.normal(50, 10, 200),
                                    'A_char_2': np.random.normal(50, 10, 200),
                                    'A_mrs': [1.75] * 200,
                                    'B_char_1': np.random.normal(50, 10, 200),
                                    'B_char_2': np.random.normal(50, 10, 200),
                                    'B_mrs': [1.75] * 200})
        
    # All reviewers are unmatched indicator
    all_matched = False

    # Create log dataframe
    log = pd.DataFrame(columns=['iterat', 'A_match_count', 'A_unmatch_count', 'B_match_count', 'B_unmatch_count', 'A_match_utlity_mean', 'B_match_utlity_mean'])

    # ---------------------------------------------------------------
    # DATA PREPARATION
    # ---------------------------------------------------------------

    A = {'id': data_input.index,
         'char_1' : data_input[A_char_1_name],
         'char_2' : data_input[A_char_2_name],
         'mrs' : data_input[A_mrs_name],
         'first_best' : [None] * len(data_input.index),
         'match' : [None] * len(data_input.index),
         'match_utility' : [0] * len(data_input.index)}
    A = pd.DataFrame(A)

    B = {'id': data_input.index,
         'char_1' : data_input[B_char_1_name],
         'char_2' : data_input[B_char_2_name],
         'mrs' : data_input[B_mrs_name],
         'first_best' : [None] * len(data_input.index),
         'match' : [None] * len(data_input.index),
         'match_utility' : [0] * len(data_input.index)}
    B = pd.DataFrame(B)

    # print a message acknowledging the input data
    print()
    print('Data is loaded')
    print('Applicants characteristics: ', A_char_1_name, A_char_2_name)
    print('Applicants MRS: ', A_mrs_name)
    print('Reviewers characteristics: ', B_char_1_name, B_char_2_name)
    print('Reviewers MRS: ', B_mrs_name)
    print('Market size: ', len(A['id']))

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
                        'utility': B['char_1'] + (B['char_2'] * A['mrs'])}
                
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
                                                            + (B.loc[B['id'] == qth_best_id, 'char_2'].values[0] 
                                                            * A.loc[A['id'] == i, 'mrs'].values[0]))
                    B.loc[B['id'] == qth_best_id, 'match'] = i
                    B.loc[B['id'] == qth_best_id, 'match_utility'] = (A.loc[A['id'] == i, 'char_1'].values[0]
                                                                      + (A.loc[A['id'] == i, 'char_2'].values[0]
                                                                      * B.loc[B['id'] == qth_best_id, 'mrs'].values[0]))
                # else if the reviewer is matched
                if B['match'][B['id'] == qth_best_id].values[0] != None:
                    # find the current applicant
                    current_applicant = B['match'][B['id'] == qth_best_id].values[0]
                    # calc the utility of matching the current applicavnt
                    current_applicant_utility = (A['char_1'][A['id'] == current_applicant].values[0] 
                                                + ((A['char_2'][A['id'] == current_applicant].values[0] 
                                                * B['mrs'][B['id'] == qth_best_id].values[0])))
                    # calc the utility of matching i
                    i_utility = (A['char_1'][A['id'] == i].values[0] 
                                + ((A['char_2'][A['id'] == i].values[0] 
                                * B['mrs'][B['id'] == qth_best_id].values[0])))
                    # if i provides higher utility than the current applicant
                    if i_utility > current_applicant_utility:
                        # current applicant is unmatched
                        A.loc[A['id'] == current_applicant, 'match'] = None
                        A.loc[A['id'] == current_applicant, 'match_utility'] = 0
                        breakups_count += 1
                        # i is matched
                        A.loc[A['id'] == i, 'match'] = qth_best_id
                        A.loc[A['id'] == i, 'match_utility'] = (B.loc[B['id'] == qth_best_id, 'char_1'].values[0]
                                                                + (B.loc[B['id'] == qth_best_id, 'char_2'].values[0]
                                                                * A.loc[A['id'] == i, 'mrs'].values[0]))
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
    if extra_vars == True:
        data_output[spec_name + '_initial_index'] = data_input.index
        data_output[spec_name + '_A_dap_match'] = A['match']
        data_output[spec_name + '_B_dap_match'] = B['match']
    
    data_output[spec_name + '_A_obs_utility'] = B['char_1'] + (B['char_2'] * A['mrs'])
    data_output[spec_name + '_B_obs_utility'] = A['char_1'] + (A['char_2'] * B['mrs'])
    data_output[spec_name + '_A_dap_utility'] = A['match_utility']
    data_output[spec_name + '_B_dap_utility'] = B['match_utility']

    # calculate z-scores for observed utilities
    data_output[spec_name + '_A_obs_utility_z'] = (data_output[spec_name + '_A_obs_utility'] - data_output[spec_name + '_A_obs_utility'].mean())/data_output[spec_name + '_A_obs_utility'].std()
    data_output[spec_name + '_B_obs_utility_z'] = (data_output[spec_name + '_B_obs_utility'] - data_output[spec_name + '_B_obs_utility'].mean())/data_output[spec_name + '_B_obs_utility'].std()

    # calculate z-scores for dap utilities
    data_output[spec_name + '_A_dap_utility_z'] = (data_output[spec_name + '_A_dap_utility'] - data_output[spec_name + '_A_dap_utility'].mean())/data_output[spec_name + '_A_dap_utility'].std()
    data_output[spec_name + '_B_dap_utility_z'] = (data_output[spec_name + '_B_dap_utility'] - data_output[spec_name + '_B_dap_utility'].mean())/data_output[spec_name + '_B_dap_utility'].std()

    # calculate difference between observed and dap utilities
    data_output[spec_name + '_diff_A'] = data_output[spec_name + '_A_obs_utility'] - data_output[spec_name + '_A_dap_utility']
    data_output[spec_name + '_diff_B'] = data_output[spec_name + '_B_obs_utility'] - data_output[spec_name + '_B_dap_utility']

    # calculate z-scores for diff_A and diff_B
    data_output[spec_name + '_diff_A_z'] = (data_output[spec_name + '_diff_A'] - data_output[spec_name + '_diff_A'].mean())/data_output[spec_name + '_diff_A'].std()
    data_output[spec_name + '_diff_B_z'] = (data_output[spec_name + '_diff_B'] - data_output[spec_name + '_diff_B'].mean())/data_output[spec_name + '_diff_B'].std() 

    # ---------------------------------------------------------------
    # GRAPH 1: Available payoffs
    # ---------------------------------------------------------------

    # in the same style as below plot histogram for z-scores of observed utilities
    plt.figure(figsize=(10, 6))
    plt.gca().set_facecolor((240/255, 240/255, 240/255))
    plt.gcf().set_facecolor((240/255, 240/255, 240/255))

    # Define bin edges to ensure same bin width
    bins = np.linspace(min(data_output[spec_name + '_A_obs_utility_z'].min(), data_output[spec_name + '_B_obs_utility_z'].min()), 
                    max(data_output[spec_name + '_A_obs_utility_z'].max(), data_output[spec_name + '_B_obs_utility_z'].max()), 51)

    sns.histplot(data_output[spec_name + '_A_obs_utility_z'], bins=bins, color='mediumpurple', alpha=0.5, label=A_name, stat='percent', kde=True)
    sns.histplot(data_output[spec_name + '_B_obs_utility_z'], bins=bins, color='green', alpha=0.5, label=B_name, stat='percent', kde=True)

    plt.legend(frameon=False, fontsize=28)
    plt.ylabel('Percent', fontsize=28)
    plt.xlabel('Z-Score', fontsize=28)
    plt.title('Available payoffs', fontsize=32)

    # Add grid lines
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Remove axis box
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)

    # Set histogram contour lines to the same color as the background
    for patch in plt.gca().patches:
        patch.set_edgecolor((240/255, 240/255, 240/255))

    # Increase tick label size
    plt.xticks(fontsize=26)
    plt.yticks(fontsize=26)

    # export the graph as pdf
    plt.tight_layout()
    plt.savefig(spec_name + '_available_payoffs.pdf')

    if graphs == True:
        plt.show()

    # ---------------------------------------------------------------
    # GRAPH 2: Observed vs. A-Optimal
    # ---------------------------------------------------------------

    plt.figure(figsize=(10, 6))
    plt.gca().set_facecolor((240/255, 240/255, 240/255))
    plt.gcf().set_facecolor((240/255, 240/255, 240/255))

    # Define bin edges to ensure same bin width
    bins = np.linspace(data_output[spec_name + '_diff_A_z'].min(), data_output[spec_name + '_diff_A_z'].max(), 51)

    sns.histplot(data_output[spec_name + '_diff_A_z'], bins=bins, color='mediumpurple', alpha=0.5, label=A_name, stat='percent', kde=True)

    plt.legend(frameon=False, fontsize=28)
    plt.ylabel('Percent', fontsize=28)
    plt.xlabel('Z-Score', fontsize=28)
    plt.title('Observed vs. A-Optimal', fontsize=32)

    # Add grid lines
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Remove axis box
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)

    # Set histogram contour lines to the same color as the background
    for patch in plt.gca().patches:
        patch.set_edgecolor((240/255, 240/255, 240/255))

    # Increase tick label size
    plt.xticks(fontsize=26)
    plt.yticks(fontsize=26)

    # Set x-axis ticks with a step of 1
    plt.xticks(np.arange(int(data_output[spec_name + '_diff_A_z'].min()), int(data_output[spec_name + '_diff_A_z'].max()) + 1, 1))

    # Calculate statistics for Workers
    above_one_std_A = (data_output[spec_name + '_diff_A_z'] > 1).mean() * 100
    below_one_std_A = (data_output[spec_name + '_diff_A_z'] < -1).mean() * 100

    # Add text for statistics
    textstr = f'Above 1 STD: {above_one_std_A:.1f}%\nBelow -1 STD: {below_one_std_A:.1f}%'

    # Add text box to the plot
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    plt.gca().text(0.05, 0.95, textstr, transform=plt.gca().transAxes, fontsize=26,
                verticalalignment='top', bbox=props)

    # export the graph as pdf
    plt.tight_layout()
    plt.savefig(spec_name + '_obs_vs_dap.pdf')

    if graphs == True:
        plt.show()

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

def four_features(data_input='example_data',
        A_char_1_name = 'A_char_1',
        A_char_2_name = 'A_char_2',
        A_char_3_name = 'A_char_3',
        A_char_4_name = 'A_char_4',
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
        A_name='A',
        B_name='B',
        spec_name='default',
        extra_vars=False,
        graphs=True,
        save_files=True):
        
    """
    Perform the Deferred Acceptance Procedure (DAP) based on the data for the agents' characteristics and the marginal rates of substitution (MRS) between the characteristics of their counterparts.

    Parameters
    ----------
    data_input : str or pd.DataFrame, optional
        The dataset to use for the matching process. If 'example_data', a default dataset will be generated. Default is 'example_data'.
    A_char_1_name : str, optional
        The name of the first characteristic of applicants. Default is 'A_char_1'.
    A_char_2_name : str, optional
        The name of the second characteristic of applicants. Default is 'A_char_2'.
    A_char_3_name : str, optional
        The name of the third characteristic of applicants. Default is 'A_char_3'.
    A_char_4_name : str, optional
        The name of the fourth characteristic of applicants. Default is 'A_char_4'.
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
    A_name : str, optional
        The label for applicants in the graphs. Default is 'A'.
    B_name : str, optional
        The label for reviewers in the graphs. Default is 'B'.
    spec_name : str, optional
        Specification name. Used to name the output files and new variables. Default is 'default'.
    extra_vars : bool, optional
        If True, in addition to the variables containing the payoffs, z-scores, and the difference 
        between the observed and DAP-generated payoffs and their z-scores, the output file will also 
        contain applicants' and reviewers' initially assigned indices and the indices of their matches. 
        Default is False.
    graphs : bool, optional
        If True, the output graphs will be displayed. Default is True.
    save_files : bool, optional
        If True, the output files will be saved. Default is True.

    Returns
    -------
    data_output : pd.DataFrame
        The updated dataset with matching results.
    log : pd.DataFrame
        The log of the matching process.

    Examples
    --------
    >>> four_features()
    >>> four_features(data_input=my_dataframe, 
                    A_char_1_name = 'A_char_1',
                    A_char_2_name = 'A_char_2',
                    A_char_3_name = 'A_char_3',
                    A_char_4_name = 'A_char_4',
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
                    A_name='A',
                    B_name='B',
                    spec_name='default',
                    extra_vars=False,
                    graphs=True,
                    save_files=True)
    """
    
    # default dataset
    if isinstance(data_input, str) and data_input == 'example_data':
        np.random.seed(0)
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
                                    'B_mrs14': [0.75] * 200})
        
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

    A = {   'id': data_input.index,
            'char_1' : data_input[A_char_1_name],
            'char_2' : data_input[A_char_2_name],
            'char_3' : data_input[A_char_3_name],
            'char_4' : data_input[A_char_4_name],
            'mrs12' : data_input[A_mrs12_name],
            'mrs13' : data_input[A_mrs13_name],
            'mrs14' : data_input[A_mrs14_name],
            'first_best' : [None] * len(data_input.index),
            'match' : [None] * len(data_input.index),
            'match_utility' : [0] * len(data_input.index)}
    A = pd.DataFrame(A)

    B = {   'id': data_input.index,
            'char_1' : data_input[B_char_1_name],
            'char_2' : data_input[B_char_2_name],
            'char_3' : data_input[B_char_3_name],
            'char_4' : data_input[B_char_4_name],
            'mrs12' : data_input[B_mrs12_name],
            'mrs13' : data_input[B_mrs13_name],
            'mrs14' : data_input[B_mrs14_name],
            'first_best' : [None] * len(data_input.index),
            'match' : [None] * len(data_input.index),
            'match_utility' : [0] * len(data_input.index)}
    B = pd.DataFrame(B)

    # print a message acknowledging the input data
    print()
    print('Data is loaded')
    print('Applicants characteristics: ', A_char_1_name, A_char_2_name, A_char_3_name, A_char_4_name)
    print('Applicants MRS: ', A_mrs12_name, A_mrs13_name, A_mrs14_name)
    print('Reviewers characteristics: ', B_char_1_name, B_char_2_name, B_char_3_name, B_char_4_name)
    print('Reviewers MRS: ', B_mrs12_name, B_mrs13_name, B_mrs14_name)
    print('Market size: ', len(A['id']))

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
                                                                   +  A.loc[A['id'] == i, 'char_4'].values[0] * B.loc[B['id'] == qth_best_id, 'mrs14'].values[0])
                # else if the reviewer is matched
                if B['match'][B['id'] == qth_best_id].values[0] != None:
                    # find the current applicant
                    current_applicant = B['match'][B['id'] == qth_best_id].values[0]
                    # calc the utility of matching the current applicavnt
                    current_applicant_utility = (A['char_1'][A['id'] == current_applicant].values[0] 
                                              +  A['char_2'][A['id'] == current_applicant].values[0] * B['mrs12'][B['id'] == qth_best_id].values[0]
                                              +  A['char_3'][A['id'] == current_applicant].values[0] * B['mrs13'][B['id'] == qth_best_id].values[0]
                                              +  A['char_4'][A['id'] == current_applicant].values[0] * B['mrs14'][B['id'] == qth_best_id].values[0])
                    # calc the utility of matching i
                    i_utility = (A['char_1'][A['id'] == i].values[0] 
                              +  A['char_2'][A['id'] == i].values[0] * B['mrs12'][B['id'] == qth_best_id].values[0]
                              +  A['char_3'][A['id'] == i].values[0] * B['mrs13'][B['id'] == qth_best_id].values[0]
                              +  A['char_4'][A['id'] == i].values[0] * B['mrs14'][B['id'] == qth_best_id].values[0])
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
    if extra_vars == True:
        data_output[spec_name + '_initial_index'] = data_input.index
        data_output[spec_name + '_A_dap_match'] = A['match']
        data_output[spec_name + '_B_dap_match'] = B['match']
    
    data_output[spec_name + '_A_obs_utility'] = B['char_1'] + B['char_2'] * A['mrs12'] + B['char_3'] * A['mrs13'] + B['char_4'] * A['mrs14']
    data_output[spec_name + '_B_obs_utility'] = A['char_1'] + A['char_2'] * B['mrs12'] + A['char_3'] * B['mrs13'] + A['char_4'] * B['mrs14']
    data_output[spec_name + '_A_dap_utility'] = A['match_utility']
    data_output[spec_name + '_B_dap_utility'] = B['match_utility']

    # calculate z-scores for observed utilities
    data_output[spec_name + '_A_obs_utility_z'] = (data_output[spec_name + '_A_obs_utility'] - data_output[spec_name + '_A_obs_utility'].mean())/data_output[spec_name + '_A_obs_utility'].std()
    data_output[spec_name + '_B_obs_utility_z'] = (data_output[spec_name + '_B_obs_utility'] - data_output[spec_name + '_B_obs_utility'].mean())/data_output[spec_name + '_B_obs_utility'].std()

    # calculate z-scores for dap utilities
    data_output[spec_name + '_A_dap_utility_z'] = (data_output[spec_name + '_A_dap_utility'] - data_output[spec_name + '_A_dap_utility'].mean())/data_output[spec_name + '_A_dap_utility'].std()
    data_output[spec_name + '_B_dap_utility_z'] = (data_output[spec_name + '_B_dap_utility'] - data_output[spec_name + '_B_dap_utility'].mean())/data_output[spec_name + '_B_dap_utility'].std()

    # calculate difference between observed and dap utilities
    data_output[spec_name + '_diff_A'] = data_output[spec_name + '_A_obs_utility'] - data_output[spec_name + '_A_dap_utility']
    data_output[spec_name + '_diff_B'] = data_output[spec_name + '_B_obs_utility'] - data_output[spec_name + '_B_dap_utility']

    # calculate z-scores for diff_A and diff_B
    data_output[spec_name + '_diff_A_z'] = (data_output[spec_name + '_diff_A'] - data_output[spec_name + '_diff_A'].mean())/data_output[spec_name + '_diff_A'].std()
    data_output[spec_name + '_diff_B_z'] = (data_output[spec_name + '_diff_B'] - data_output[spec_name + '_diff_B'].mean())/data_output[spec_name + '_diff_B'].std() 

    # ---------------------------------------------------------------
    # GRAPH 1: Available payoffs
    # ---------------------------------------------------------------

    # in the same style as below plot histogram for z-scores of observed utilities
    plt.figure(figsize=(10, 6))
    plt.gca().set_facecolor((240/255, 240/255, 240/255))
    plt.gcf().set_facecolor((240/255, 240/255, 240/255))

    # Define bin edges to ensure same bin width
    bins = np.linspace(min(data_output[spec_name + '_A_obs_utility_z'].min(), data_output[spec_name + '_B_obs_utility_z'].min()), 
                    max(data_output[spec_name + '_A_obs_utility_z'].max(), data_output[spec_name + '_B_obs_utility_z'].max()), 51)

    sns.histplot(data_output[spec_name + '_A_obs_utility_z'], bins=bins, color='mediumpurple', alpha=0.5, label=A_name, stat='percent', kde=True)
    sns.histplot(data_output[spec_name + '_B_obs_utility_z'], bins=bins, color='green', alpha=0.5, label=B_name, stat='percent', kde=True)

    plt.legend(frameon=False, fontsize=28)
    plt.ylabel('Percent', fontsize=28)
    plt.xlabel('Z-Score', fontsize=28)
    plt.title('Available payoffs', fontsize=32)

    # Add grid lines
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Remove axis box
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)

    # Set histogram contour lines to the same color as the background
    for patch in plt.gca().patches:
        patch.set_edgecolor((240/255, 240/255, 240/255))

    # Increase tick label size
    plt.xticks(fontsize=26)
    plt.yticks(fontsize=26)

    # export the graph as pdf
    plt.tight_layout()
    plt.savefig(spec_name + '_available_payoffs.pdf')

    if graphs == True:
        plt.show()

    # ---------------------------------------------------------------
    # GRAPH 2: Observed vs. A-Optimal
    # ---------------------------------------------------------------

    plt.figure(figsize=(10, 6))
    plt.gca().set_facecolor((240/255, 240/255, 240/255))
    plt.gcf().set_facecolor((240/255, 240/255, 240/255))

    # Define bin edges to ensure same bin width
    bins = np.linspace(data_output[spec_name + '_diff_A_z'].min(), data_output[spec_name + '_diff_A_z'].max(), 51)

    sns.histplot(data_output[spec_name + '_diff_A_z'], bins=bins, color='mediumpurple', alpha=0.5, label=A_name, stat='percent', kde=True)

    plt.legend(frameon=False, fontsize=28)
    plt.ylabel('Percent', fontsize=28)
    plt.xlabel('Z-Score', fontsize=28)
    plt.title('Observed vs. A-Optimal', fontsize=32)

    # Add grid lines
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Remove axis box
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)

    # Set histogram contour lines to the same color as the background
    for patch in plt.gca().patches:
        patch.set_edgecolor((240/255, 240/255, 240/255))

    # Increase tick label size
    plt.xticks(fontsize=26)
    plt.yticks(fontsize=26)

    # Set x-axis ticks with a step of 1
    plt.xticks(np.arange(int(data_output[spec_name + '_diff_A_z'].min()), int(data_output[spec_name + '_diff_A_z'].max()) + 1, 1))

    # Calculate statistics for Workers
    above_one_std_A = (data_output[spec_name + '_diff_A_z'] > 1).mean() * 100
    below_one_std_A = (data_output[spec_name + '_diff_A_z'] < -1).mean() * 100

    # Add text for statistics
    textstr = f'Above 1 STD: {above_one_std_A:.1f}%\nBelow -1 STD: {below_one_std_A:.1f}%'

    # Add text box to the plot
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    plt.gca().text(0.05, 0.95, textstr, transform=plt.gca().transAxes, fontsize=26,
                verticalalignment='top', bbox=props)

    # export the graph as pdf
    plt.tight_layout()
    plt.savefig(spec_name + '_obs_vs_dap.pdf')

    if graphs == True:
        plt.show()

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

def rematcher(data_input='example_data',
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
        A_name='Applicants',
        B_name='Reviewers',
        spec_name='default',
        extra_vars=False,
        graphs=True,
        save_files=True):
        
    """
    Perform the Deferred Acceptance Procedure (DAP) based on the data for the agents' characteristics 
    and the marginal rates of substitution (MRS) between the characteristics of their counterparts given 
    a pre-defined reviewers' bias. The bias characteristic is used by the reviewers to make the matching 
    decision, however, is not included in the final payoff calculation.

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
    extra_vars : bool, optional
        If True, in addition to the variables containing the payoffs, z-scores, and the difference 
        between the observed and DAP-generated payoffs and their z-scores, the output file will also 
        contain applicants' and reviewers' initially assigned indices and the indices of their matches. 
        Default is False.
    graphs : bool, optional
        If True, the output graphs will be displayed. Default is True.
    save_files : bool, optional
        If True, the output files will be saved. Default is True.

    Returns
    -------
    data_output : pd.DataFrame
        The updated dataset with matching results.
    log : pd.DataFrame
        The log of the matching process.

    Examples
    --------
    >>> four_features_biased()
    >>> four_features_biased(data_input = my_dataframe,
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
                            extra_vars = False,
                            graphs = True,
                            save_files = True)
    """

    print()
    print('Loading the data...')

    A_bias_char_name = spec_name + '_' + A_bias_char_name
    B_bias_mrs_name = spec_name + '_' + B_bias_mrs_name

    # default dataset
    if isinstance(data_input, str) and data_input == 'example_data':
        np.random.seed(int(str(datetime.now())[17:19]))
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
            'first_best'    : [None] * len(data_input.index),
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
            'first_best'    : [None] * len(data_input.index),
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

    if A_char_number == 3:
        data_input.drop(columns=[A_char_4_name, B_mrs14_name], inplace=True)
    elif A_char_number == 2:
        data_input.drop(columns=[A_char_3_name, B_mrs13_name, 
                                 A_char_4_name, B_mrs14_name], inplace=True)

    if B_char_number == 3:
        data_input.drop(columns=[B_char_4_name, A_mrs14_name], inplace=True)
    elif B_char_number == 2:
        data_input.drop(columns=[B_char_3_name, A_mrs13_name,
                                    B_char_4_name, A_mrs14_name], inplace=True)
    if bias == False:
        data_input.drop(columns=[A_bias_char_name, B_bias_mrs_name], inplace=True)

    data_output = data_input.copy()
    
    # update the dataset with the matching results
    if extra_vars == True:
        data_output[spec_name + '_initial_index'] = data_input.index
        data_output[spec_name + '_A_dap_match'] = A['match']
        data_output[spec_name + '_B_dap_match'] = B['match']
    
    # received payoffs
    data_output[spec_name + '_A_obs_u'] = B['char_1'] + B['char_2'] * A['mrs12'] + B['char_3'] * A['mrs13'] + B['char_4'] * A['mrs14']
    data_output[spec_name + '_B_obs_u'] = A['char_1'] + A['char_2'] * B['mrs12'] + A['char_3'] * B['mrs13'] + A['char_4'] * B['mrs14']
    data_output[spec_name + '_A_dap_u'] = A['match_utility']
    data_output[spec_name + '_B_dap_u'] = B['match_utility']

    # apparent payoffs
    if bias == True:
        B_dap_sorted = B.sort_values('match', ascending=True, ignore_index=True)
        data_output[spec_name + '_A_apparent_u']           = B_dap_sorted['match_utility']
        data_output[spec_name + '_A_apparent_corrected_u'] = B_dap_sorted['match_utility'] - A['bias_char'] * B_dap_sorted['bias_mrs']

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
    
    if bias == True:
        data_output[spec_name + '_A_apparent_u_z'] = (data_output[spec_name + '_A_apparent_u'] - data_output[spec_name + '_A_apparent_u'].mean())/data_output[spec_name + '_A_apparent_u'].std()
        data_output[spec_name + '_A_apparent_corrected_u_z'] = (data_output[spec_name + '_A_apparent_corrected_u'] - data_output[spec_name + '_A_apparent_corrected_u'].mean())/data_output[spec_name + '_A_apparent_corrected_u'].std()

    if graphs == True:
        # ---------------------------------------------------------------
        # GRAPH 1: Available payoffs
        # ---------------------------------------------------------------

        fig = ridgeplot(samples=[data_output[spec_name + '_A_obs_u_z'],
                            data_output[spec_name + '_B_obs_u_z']],
                            labels = [A_name, B_name],
                            colorscale = "viridis", nbins=20,
                            colormode = "row-index",
                            opacity=0.6)
        fig.update_layout(
            height=560,
            width=800,
            font_size=16,
            plot_bgcolor="white",
            xaxis_gridcolor="rgba(0, 0, 0, 0.1)",
            yaxis_gridcolor="rgba(0, 0, 0, 0.1)",
            title="Available payoffs",
            xaxis_title="Z-Score",
            showlegend=False,
        )
        fig.write_image(spec_name + '_available_payoffs.pdf')

        fig.show()

        # ---------------------------------------------------------------
        # GRAPH 2: Observed vs. A-Optimal
        # ---------------------------------------------------------------
        fig = ridgeplot(samples=[data_output[spec_name + '_diff_A_z'],
                            data_output[spec_name + '_diff_B_z']],
                            labels = [A_name, B_name],
                            colorscale = "viridis", nbins=20,
                            colormode = "row-index",
                            opacity=0.6)
        fig.update_layout(
            height=560,
            width=800,
            font_size=16,
            plot_bgcolor="white",
            xaxis_gridcolor="rgba(0, 0, 0, 0.1)",
            yaxis_gridcolor="rgba(0, 0, 0, 0.1)",
            title="Observed vs. A-Optimal",
            xaxis_title="Z-Score",
            showlegend=False,
        )
        fig.write_image(spec_name + '_obs_vs_dap.pdf')

        fig.show()

        if bias == True:
            # ---------------------------------------------------------------
            # GRAPH 3: Bias and reviewes' perceived payoffs
            # ---------------------------------------------------------------
            fig = ridgeplot(samples=[data_output[spec_name + '_A_apparent_u_z'][data_output[A_bias_char_name] == 0],
                                    data_output[spec_name + '_A_apparent_u_z'][data_output[A_bias_char_name] == 1],
                                    data_output[spec_name + '_A_apparent_corrected_u_z'][data_output[A_bias_char_name] == 0],
                                    data_output[spec_name + '_A_apparent_corrected_u_z'][data_output[A_bias_char_name] == 1]],
                                labels = ['Biased: Group 0', 'Biased: Group 1', 'Corrected: Group 0', 'Corrected: Group 1'],
                                colorscale = "viridis", nbins=20,
                                colormode = "row-index",
                                opacity=0.6)
            fig.update_layout(
                height=560,
                width=800,
                font_size=16,
                plot_bgcolor="white",
                xaxis_gridcolor="rgba(0, 0, 0, 0.1)",
                yaxis_gridcolor="rgba(0, 0, 0, 0.1)",
                title= B_name +"' perceived payoffs",
                xaxis_title="Z-Score",
                showlegend=False,
            )
            fig.write_image(spec_name + '_bias1.pdf')

            fig.show()

            # ---------------------------------------------------------------
            # GRAPH 4: Bias effect on the applicants' payoffs
            # ---------------------------------------------------------------
            fig = ridgeplot(samples=[data_output[spec_name + '_A_obs_u_z'][data_output[A_bias_char_name] == 0],
                                    data_output[spec_name + '_A_obs_u_z'][data_output[A_bias_char_name] == 1],
                                    data_output[spec_name + '_A_dap_u_z'][data_output[A_bias_char_name] == 0],
                                    data_output[spec_name + '_A_dap_u_z'][data_output[A_bias_char_name] == 1],
                                    data_output[spec_name + '_diff_A_z'][data_output[A_bias_char_name] == 0],
                                    data_output[spec_name + '_diff_A_z'][data_output[A_bias_char_name] == 1]],
                                labels = ['Observed: Group 0', 'Observed: Group 1', 'DAP: Group 0', 'DAP: Group 1', 'Difference: Group 0', 'Difference: Group 1'],
                                colorscale = "viridis", nbins=20,
                                colormode = "row-index",
                                opacity=0.6)
            fig.update_layout(
                height=560,
                width=800,
                font_size=16,
                plot_bgcolor="white",
                xaxis_gridcolor="rgba(0, 0, 0, 0.1)",
                yaxis_gridcolor="rgba(0, 0, 0, 0.1)",
                title="Bias effect on the " + A_name + "' payoffs",
                xaxis_title="Z-Score",
                showlegend=False,
            )
            fig.write_image(spec_name + '_bias2.pdf')

            fig.show()

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
