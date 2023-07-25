import sys
import numpy as np
import math

from fairness.metrics.utils import calc_pos_protected_percents
from fairness.metrics.UtilityMetric import UtilityMetric

class ExpCost(UtilityMetric):

    def __init__(self, welfare_fn, cost_fn):
        UtilityMetric.__init__(self, welfare_fn, cost_fn)
        self.name = f'ExpCost_{cost_fn.__name__}'

    def calc(self, actual, predicted, dict_of_sensitive_lists, single_sensitive_name,
            unprotected_vals, positive_pred, dict_of_nonclass_attrs):

        # Compute cost for each sensitive class
        prot_cost, unprot_cost = self.calc_cost(actual,
                                                predicted,
                                                dict_of_sensitive_lists,
                                                single_sensitive_name,
                                                unprotected_vals,
                                                positive_pred,
                                                dict_of_nonclass_attrs)

        comb_cost = np.concatenate([prot_cost, unprot_cost])
        exp_cost = np.mean(comb_cost)
        print(f'exp_cost: {exp_cost}')

        return exp_cost