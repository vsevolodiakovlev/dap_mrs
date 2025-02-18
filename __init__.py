"""
Deferred acceptance with marginal rate of substitution

This module is a python implementation of the deferred acceptance procedure (DAP) developed 
by Gale and Shapley (1962). The algorithm computes an applicant-optimal assignment based on 
the data for the agents' characteristics and the marginal rate of substitution (MRS) between 
the characteristics of their counterparts.

For more information, see https://github.com/vsevolodiakovlev/dap_mrs/blob/main/README.md.

The module is a work in progress. The two current versions of the algorithm are `two_features`
and `four_features`. The former is implemented for agents characterised by two variables, while
the latter is implemented for agents characterised by four variables. To learn more about the
parameters, run `help(dam_mrs.two_features)` or `help(dam_mrs.four_features)`. 

author: Vsevolod Iakovlev
email: vsevolod.v.iakovlev@gmail.com
"""

from .src.main import two_features
from .src.main import four_features
from .src.main import rematcher
