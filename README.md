# Deferred Acceptance with Marginal Rate of Substitution

[Algorithm](#the-algorithm) | [Usage](#to-use-the-module) | [Codebook](#codebook) | [References](#references)

![figure](./figures/dap_mrs_preview.png)

This module is a python implementation of the *deferred acceptance procedure (DAP)* developed by Gale and Shapley (1962). The algorithm computes an applicant-optimal assignment based on the data for the agents' characteristics and the *marginal rate of substitution (MRS)* between the characteristics of their counterparts.

*Any suggestions regarding either the code or economics are most welcome!*

## The algorithm

Suppose a set of applicants (A) and a set of reviewers (B) participate in a two-sided matching market. Assume the sets are equally sized and each reviewer can only match with one applicant and vice versa. An *A-Optimal* assignment can be achieved through the following steps:

1. Each applicant approaches their first best reviewer
2. Each reviewer tentatively accepts the most preferred applicant and rejects the rest
3. Each unmatched applicant approaches their next best reviewer
4. Each reviewer tentatively accepts the most preferred applicant and rejects the rest

... repeat until no unmatched reviewers are left, at which point the matches are finalised.

An assignment is called **A-Optimal** if all applicants are at least as well off under it as under any other *stable assignment*. 

An assignment is called **stable** if there are no two pairs of matched agents who would prefer to switch with each other.

## To use the module

1. Create a new directory with the input data make it your working directory
2. Clone the repository to that directory
3. Make sure the following packages are installed: ``pandas``, ``matplotlib``, ``seaborn``
4. Import the module:
```python
import dap_mrs
```
5. Type ``help(dap_mrs)`` to view the module's description or ``help(dap_mrs.two_features)`` for the default parameters
6. Specify the input parameters
7. Run the algorithm
```python
data_output, log = dap_mrs.two_features(data_input=my_dataframe, 
                                        A_char_1_name = 'A_char_1',
                                        A_char_2_name = 'A_char_2',
                                        A_mrs_name = 'A_mrs',
                                        B_char_1_name = 'B_char_1',
                                        B_char_2_name = 'B_char_2',
                                        B_mrs_name = 'B_mrs',
                                        A_name='A',
                                        B_name='B',
                                        files_name='dap_mrs_two_features')
```
If no input parameters are specified, the function runs the algorithm on simulated data:
```python
data_output, log = dap_mrs.two_features()
```


This produces 2 data frames and 2 graphs:
 - **data_output** — modified input data file with the matching results added as new columns
 - **log** — additional file containing information about each iteration of the algorithm
 - **available_payoffs** - available payoffs for applicants and reviewers
 - **obs_vs_dap** - difference between the payoffs of the applicants in the observed (original) and the A-Optimal (dap-computed) allocations

<img src="./figures/available_payoffs.png" width="400"> <img src="./figures/obs_vs_dap.png" width="400">

## Codebook

### Output data

| **Variable Name**         | **Description**                                                                                     | **Source Components**                     |
|----------------------------|-----------------------------------------------------------------------------------------------------|-------------------------------------------|
| `initial_index`           | The original index of A and B in the input dataset `data_input`                                             | `data_input.index`                        |
| `A_observed_utility`      | Observed utility for A, calculated as `B['char_1']` + `B['char_2']` * `A['mrs']` | `B['char_1']`, `B['char_2']`, `A['mrs']` |
| `A_dap_match`             | The index of B matched with A as the result of the DAP                                                                 | `A['match']`                              |
| `A_dap_utility`           | The payoff for A from matching with B                                               | `A['match_utility']`                      |
| `B_observed_utility`      | Observed utility for B, calculated as `A['char_1']` + `A['char_2']` * `B['mrs']` | `A['char_1']`, `A['char_2']`, `B['mrs']` |
| `B_dap_match`             | The index of A matched with B as the result of the DAP                                                                 | `B['match']`                              |
| `B_dap_utility`           | The payoff for B from matching with A                                              | `B['match_utility']`                      |
| `A_observed_utility_z`    | Z-score of the observed utility for A, normalized using its mean and standard deviation | `A_observed_utility`                                      |
| `B_observed_utility_z`    | Z-score of the observed utility for B, normalized using its mean and standard deviation | `B_observed_utility`                                      |
| `A_dap_utility_z`         | Z-score of the DAP-derived utility for A, normalized using its mean and standard deviation    | `A_dap_utility`                                           |
| `B_dap_utility_z`         | Z-score of the DAP-derived utility for B, normalized using its mean and standard deviation    | `B_dap_utility`                                           |
| `diff_A`                  | The difference between the observed utility and the DAP-derived utility for A                                 | `A_observed_utility`, `A_dap_utility`                    |
| `diff_B`                  | The difference between the observed utility and the DAP-derived utility for B                                 | `B_observed_utility`, `B_dap_utility`                    |
| `diff_A_z`                | Z-score of `diff_A`, normalized using its mean and standard deviation                          | `diff_A`                                                 |
| `diff_B_z`                | Z-score of `diff_B`, normalized using its mean and standard deviation                          | `diff_B`                                                 |

### Log

| **Variable Name**           | **Description**                                                                                                   | **Source Components**               |
|------------------------------|-------------------------------------------------------------------------------------------------------------------|-------------------------------------|
| `iterat`                    | The current iteration number                                                        | itself                            |
| `A_match_count`             | The total number of matched As | `A['match']` |
| `A_unmatch_count`           | The total number of unmatched As | `A['match']`           |
| `B_match_count`             | The total number of matched Bs | `B['match']` |
| `B_unmatch_count`           | The total number of unmatched Bs | `B['match']`           |
| `A_match_utlity_mean`       | The average payoffs of As | `A['match_utility']`         |
| `B_match_utlity_mean`       | The average payoffs of Bs | `B['match_utility']`         |
| `breakups_count`            | The total number of breakups recorded during the iteration. | itself                    |
| `q_reset_count`             | The total number of resets performed on the preference rank during the iteration.                          | itself                     |
| `rejections_count`          | The total number of rejections recorded during the iteration                                                  | itself                  |
| `pass_matched_count`        | The total number of matched As that did not need to apply this iteration | itself |

## References

- David Gale and Lloyd S Shapley. College admissions and the stability of marriage. The American Mathematical Monthly, 69(1):9–15, 1962.
