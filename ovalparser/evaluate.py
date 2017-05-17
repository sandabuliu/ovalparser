#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__ = 'tongbin'

from values import (
    exist_rule, check_rule, operator_rule, exist_order,
    check_order, operator_order, set_operation, set_order, set_rule
)

check_res = {'0+': lambda a: a >= 0,
             '1+': lambda a: a >= 1,
             '2+': lambda a: a >= 2,
             '0': lambda a: a == 0,
             '1': lambda a: a == 1,
             '0,1': lambda a: a in [0, 1],
             'odd': lambda a: a % 2 == 1,
             'even': lambda a: a % 2 == 0}


def exist_evaluated(res_counter, check_type):
    if check_type not in exist_rule:
        return 'not applicable'

    for exist in exist_rule[check_type]:
        i = 0
        while i < 4 and check_res[exist[i]](res_counter.get(exist_order[i], 0)):
            i += 1
        if i == 4:
            return exist_rule[check_type][exist]

    return 'not evaluated'


def check_evaluated(res_counter, check_type):
    if check_type not in check_rule:
        return 'not applicable'

    for check in check_rule[check_type]:
        i = 0
        while i < 6 and check_res[check[i]](res_counter.get(check_order[i], 0)):
            i += 1
        if i == 6:
            return check_rule[check_type][check]

    return 'not evaluated'


def operator_evaluated(res_counter, check_type):
    for operator in operator_rule[check_type]:
        i = 0
        while i < 6 and check_res[operator[i]](res_counter.get(operator_order[i], 0)):
            i += 1
        if i == 6:
            return operator_rule[check_type][operator]


def set_evaluated(res, set_operator):
    set_operator = set_operator.upper()
    result1 = set_order.index(res[0][0])
    result2 = set_order.index(res[1][0])
    return set_rule[set_operator][result2][result1], set_operation[set_operator](res[0][1], res[1][1])
