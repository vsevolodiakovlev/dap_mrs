# Deferred Acceptance with Marginal Rate of Substitution

[Algorithm](#the-algorithm) | [Usage](#to-use-the-module) | [Example](#other-examples) | [Codebook](#codebook) | [References](#references)

This module is a python implementation of the *Deferred Acceptance Procedure (DAP)* developed by Gale and Shapley (1962). The algorithm computes an applicant-optimal assignment based on the data for the agents' characteristics and the *marginal rate of substitution (MRS)* between the characteristics of their counterparts.

## The algorithm

Suppose a set of applicants (A) and a set of reviewers (B) participate in a two-sided matching market. Assume the sets are equally sized and each reviewer can only match with one applicant and vice versa. An *A-Optimal* assignment can be achieved through the following steps:

1. Each applicant approaches their first best reviewer
2. Each reviewer tentatively accepts the most preferred applicant and rejects the rest
3. Each unmatched applicant approaches their next best reviewer
4. Each reviewer tentatively accepts the most preferred applicant and rejects the rest

... repeat until no unmatched reviewers are left, at which point the matches are finalised.

An assignment is called **A-Optimal** if all applicants are at least as well off under it as under any other *stable assignment*. 

An assignment is called **stable** if there are no two pairs of matched agents who would prefer to switch with each other.

## Usage

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
data_output, log = dap_mrs.two_features()
```
This produces 2 dataframes and 2 graphs:
 - **data_output** — ...
 - **log** — additional file containing matching outcomes for each iteration of the matching procedure for the last repetition illustrating the algorithm

## Example

## Codebook

## References

- David Gale and Lloyd S Shapley. College admissions and the stability of marriage. The American Mathematical Monthly, 69(1):9–15, 1962.
