
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def two_features(data_input='example_data',
        A_char_1_name = 'A_char_1',
        A_char_2_name = 'A_char_2',
        A_mrs_name = 'A_mrs',
        B_char_1_name = 'B_char_1',
        B_char_2_name = 'B_char_2',
        B_mrs_name = 'B_mrs',
        A_name='A',
        B_name='B',
        files_name='dap_mrs_two_features'):
        
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
    files_name : str, optional
        The name of the files to save. Default is 'dap_mrs_two_features'.

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
                    files_name='dap_mrs_two_features')
    """
    
    # default dataset
    if data_input == 'example_data':
        np.random.seed(0)
        data_input = pd.DataFrame({'A_char_1': np.random.normal(1, 100, 200),
                                'A_char_2': np.random.normal(1, 5, 200),
                                'A_mrs': [5.25] * 200,
                                'B_char_1': np.random.normal(1, 100, 200),
                                'B_char_2': np.random.normal(1, 5, 200),
                                'B_mrs': [7.75] * 200})
        
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
                # generate i's netwrok
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
                        # i stays u nmatched and qth best reviewer stays matched with the current applicant
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
    data_output['initial_index'] = data_input.index
    data_output['A_observed_utility'] = B['char_1'] + (B['char_2'] * A['mrs'])
    data_output['A_dap_match'] = A['match']
    data_output['A_dap_utility'] = A['match_utility']
    data_output['B_observed_utility'] = A['char_1'] + (A['char_2'] * B['mrs'])
    data_output['B_dap_match'] = B['match']
    data_output['B_dap_utility'] = B['match_utility']

    # calculate z-scores for observed utilities
    data_output['A_observed_utility_z'] = (data_output['A_observed_utility'] - data_output['A_observed_utility'].mean())/data_output['A_observed_utility'].std()
    data_output['B_observed_utility_z'] = (data_output['B_observed_utility'] - data_output['B_observed_utility'].mean())/data_output['B_observed_utility'].std()

    # calculate z-scores for dap utilities
    data_output['A_dap_utility_z'] = (data_output['A_dap_utility'] - data_output['A_dap_utility'].mean())/data_output['A_dap_utility'].std()
    data_output['B_dap_utility_z'] = (data_output['B_dap_utility'] - data_output['B_dap_utility'].mean())/data_output['B_dap_utility'].std()

    # calculate difference between observed and dap utilities
    data_output['diff_A'] = data_output['A_observed_utility'] - data_output['A_dap_utility']
    data_output['diff_B'] = data_output['B_observed_utility'] - data_output['B_dap_utility']

    # calculate z-scores for diff_A and diff_B
    data_output['diff_A_z'] = (data_output['diff_A'] - data_output['diff_A'].mean())/data_output['diff_A'].std()
    data_output['diff_B_z'] = (data_output['diff_B'] - data_output['diff_B'].mean())/data_output['diff_B'].std() 

    # ---------------------------------------------------------------
    # GRAPH 1: Available payoffs
    # ---------------------------------------------------------------

    # in the same style as below plot histogram for z-scores of observed utilities
    plt.figure(figsize=(10, 6))
    plt.gca().set_facecolor((240/255, 240/255, 240/255))
    plt.gcf().set_facecolor((240/255, 240/255, 240/255))

    # Define bin edges to ensure same bin width
    bins = np.linspace(min(data_output['A_observed_utility_z'].min(), data_output['B_observed_utility_z'].min()), 
                    max(data_output['A_observed_utility_z'].max(), data_output['B_observed_utility_z'].max()), 51)

    sns.histplot(data_output['A_observed_utility_z'], bins=bins, color='mediumpurple', alpha=0.5, label=A_name, stat='percent', kde=True)
    sns.histplot(data_output['B_observed_utility_z'], bins=bins, color='green', alpha=0.5, label=B_name, stat='percent', kde=True)

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
    plt.savefig('available_payoffs.pdf')

    plt.show()

    # ---------------------------------------------------------------
    # GRAPH 2: Observed vs. A-Optimal
    # ---------------------------------------------------------------

    plt.figure(figsize=(10, 6))
    plt.gca().set_facecolor((240/255, 240/255, 240/255))
    plt.gcf().set_facecolor((240/255, 240/255, 240/255))

    # Define bin edges to ensure same bin width
    bins = np.linspace(data_output['diff_A_z'].min(), data_output['diff_A_z'].max(), 51)

    sns.histplot(data_output['diff_A_z'], bins=bins, color='mediumpurple', alpha=0.5, label=A_name, stat='percent', kde=True)

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
    plt.xticks(np.arange(int(data_output['diff_A_z'].min()), int(data_output['diff_A_z'].max()) + 1, 1))

    # Calculate statistics for Workers
    above_one_std_A = (data_output['diff_A_z'] > 1).mean() * 100
    below_one_std_A = (data_output['diff_A_z'] < -1).mean() * 100

    # Add text for statistics
    textstr = f'Above 1 STD: {above_one_std_A:.1f}%\nBelow -1 STD: {below_one_std_A:.1f}%'

    # Add text box to the plot
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    plt.gca().text(0.05, 0.95, textstr, transform=plt.gca().transAxes, fontsize=26,
                verticalalignment='top', bbox=props)

    # export the graph as pdf
    plt.tight_layout()
    plt.savefig('obs_vs_dap.pdf')

    plt.show()

    # ---------------------------------------------------------------
    # SAVE OUTPUT FILES
    # ---------------------------------------------------------------

    data_output.to_csv(files_name + '_data_output.csv', index=False)
    print()
    print(files_name + '_data_output.csv is saved to ', os.getcwd())
    log.to_csv(files_name + '_log.csv', index=False)
    print(files_name + '_log.csv is saved to ', os.getcwd())
    
    return data_output, log
