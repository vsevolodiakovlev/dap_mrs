"""
Deferred acceptance with marginal rate of substitution

This module is a python implementation of the deferred acceptance procedure (DAP) developed 
by Gale and Shapley (1962). The algorithm computes an applicant-optimal assignment based on 
the data for the agents' characteristics and the marginal rate of substitution (MRS) between 
the characteristics of their counterparts.

The module includes the following functions:
    - matching 
        Perform the Deferred Acceptance Procedure (DAP) based on the data for the agents' characteristics 
        and the marginal rates of substitution (MRS) between the characteristics of their counterparts.
    - graphs.available_payoffs
        Plot the observed payoffs vs. the A-Optimal payoffs for the Applicants and Reviewers.
    - graphs.observed_vs_dap
        Plot the Reviewers' apparent values for the two groups of agents defined by the bias characteristic.
    - graphs.apparent_values
        Plot the Reviewers' apparent values for the two groups of agents defined by the bias characteristic.
    - graphs.bias_effect
        Plot the Applicants' payoffs for the two groups of agents defined by the bias characteristic.

For more information, see https://github.com/vsevolodiakovlev/dap_mrs/blob/main/README.md.

author: Vsevolod Iakovlev
email: vsevolod.v.iakovlev@gmail.com
"""

from .src.main import matching
from .src import graphs
