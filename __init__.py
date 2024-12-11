"""
Deferred acceptance with marginal rate of substitution

This module is a python implementation of the deferred acceptance procedure (DAP) developed 
by Gale and Shapley (1962). The algorithm computes an applicant-optimal assignment based on 
the data for the agents' characteristics and the marginal rate of substitution (MRS) between 
the characteristics of their counterparts.

For more information, see https://github.com/vsevolodiakovlev/dap_mrs/blob/main/README.md.

The module is a work in progress. The current version of the algorithm, `two_features`, 
is implemented for agents characterised by two variables. To learn more about the parameters,
run `help(dam_mrs.two_features)`.

author: Vsevolod Iakovlev
email: vsevolod.v.iakovlev@gmail.com
"""

from .src.main import two_features
