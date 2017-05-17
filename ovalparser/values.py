#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__ = 'tongbin'


class ListEnum(list):
    def __init__(self, *args):
        super(ListEnum, self).__init__(args)
        for item in args:
            setattr(self, '_'.join(str(item).split()), item)

STATE_OPERATOR = OPERATOR = ListEnum('and', 'and', 'one', 'or', 'xor')

NEGATE = ListEnum('false', 'false', 'true')

CHECK_EXISTENCE = ListEnum('at_least_one_exists', 'at_least_one_exists', 'all_exist',
                           'any_exist', 'none_exist', 'only_one_exists')

ENTITY_CHECK = CHECK = ListEnum('all', 'all', 'at least one', 'none satisfy', 'only one')

OPERATION = ListEnum('equals', 'equals', 'not equals', 'case insensitive equals', 'case insensitive not equal',
                     'greater than', 'less than', 'greater than or equal', 'less than or equal', 'bitwise and',
                     'pattern match', 'subset of', 'superset of')

DEPRECATED = ListEnum('false', 'false', 'true')

SET_OPERATOR = ListEnum('union', 'union', 'intersection', 'complement')

DATATYPE = ListEnum('string', 'string', 'binary', 'boolean', 'evr_string', 'fileset_revision', 'float',
                    'ios_version', 'int', 'ipv4_address', 'ipv6_address')

FilterActionEnum = ACTION = ListEnum('exclude', 'exclude', 'include')

FlagEnum = ListEnum('error', 'complete', 'incomplete', 'does not exist', 'not collected', 'not applicable')
StatusEnum = exist_order = ListEnum('exists', 'does not exist', 'error', 'not collected')
ResultEnum = check_order = operator_order = ListEnum('true', 'false', 'error', 'unknown',
                                                     'not evaluated', 'not applicable')
set_order = ListEnum('error', 'complete', 'incomplete', 'does not exist', 'not collected', 'not applicable')

exist_rule = {
    'all_exist': {('1+', '0', '0', '0'): 'true',
                  ('0', '0', '0', '0'): 'false',
                  ('0+', '1+', '0+', '0+'): 'false',
                  ('0+', '0', '1+', '0+'): 'error',
                  ('0+', '0', '0', '1+'): 'unknown'},
    'at_least_one_exists': {('1+', '0+', '0+', '0+'): 'true',
                            ('0', '1+', '0', '0'): 'false',
                            ('0', '0+', '1+', '0+'): 'error',
                            ('0', '0+', '0', '1+'): 'unknown'},
    'none_exist': {('0', '0+', '0', '0'): 'true',
                   ('1+', '0+', '0+', '0+'): 'false',
                   ('0', '0+', '1+', '0+'): 'error',
                   ('0', '0+', '0', '1+'): 'unknown'},
    'any_exist': {('0+', '0+', '0', '0+'): 'true',
                  ('1+', '0+', '1+', '0+'): 'true',
                  ('0', '0+', '1+', '0+'): 'error'},
    'only_one_exists': {('1', '0+', '0', '0'): 'true',
                        ('2+', '0+', '0+', '0+'): 'false',
                        ('0', '0+', '0', '0'): 'false',
                        ('0,1', '0+', '1+', '0+'): 'error',
                        ('0,1', '0+', '0', '1+'): 'unknown'}
}
ExistenceEnum = ListEnum(*list(exist_rule))

check_rule = {
    'all': {('1+', '0', '0', '0', '0', '0+'): 'true',
            ('0+', '1+', '0+', '0+', '0+', '0+'): 'false',
            ('0+', '0', '1+', '0+', '0+', '0+'): 'error',
            ('0+', '0', '0', '1+', '0+', '0+'):  'unknown',
            ('0+', '0', '0', '0', '1+', '0+'): 'not evaluated',
            ('0',  '0', '0', '0', '0', '1+'): 'not applicable'},
    'at least one': {('1+', '0+', '0+', '0+', '0+', '0+'): 'true',
                     ('0', '1+', '0', '0', '0', '0+'): 'false',
                     ('0', '0+', '1+', '0+', '0+', '0+'): 'error',
                     ('0', '0+', '0', '1+', '0+', '0+'): 'unknown',
                     ('0', '0+', '0', '0', '1+', '0+'): 'not evaluated',
                     ('0', '0', '0', '0', '0', '1+'): 'not applicable'},
    'none satisfy': {('0', '1+', '0', '0', '0', '0+'): 'true',
                     ('1+', '0+', '0+', '0+', '0+', '0+'): 'false',
                     ('0', '0+', '1+', '0+', '0+', '0+'): 'error',
                     ('0', '0+', '0', '1+', '0+', '0+'): 'unknown',
                     ('0', '0+', '0', '0', '1+', '0+'): 'not evaluated',
                     ('0', '0', '0', '0', '0', '1+'): 'not applicable'},
    'only one': {('1', '0+', '0', '0', '0', '0+'): 'true',
                 ('2+', '0+', '0+', '0+', '0+', '0+'): 'false',
                 ('0', '1+', '0', '0', '0', '0+'): 'false',
                 ('0,1', '0+', '1+', '0+', '0+', '0+'): 'error',
                 ('0,1', '0+', '0', '1+', '0+', '0+'): 'unknown',
                 ('0,1', '0+', '0', '0', '1+', '0+'): 'not evaluated',
                 ('0', '0', '0', '0', '0', '1+'): 'not applicable'}
}
CheckEnum = ListEnum(*list(check_rule))

operator_rule = {
    'and': {('1+', '0', '0', '0', '0', '0+'): 'true',
            ('0+', '1+', '0+', '0+', '0+', '0+'): 'false',
            ('0+', '0', '1+', '0+', '0+', '0+'): 'error',
            ('0+', '0', '0', '1+', '0+', '0+'): 'unknown',
            ('0+', '0', '0', '0', '1+', '0+'): 'not evaluated',
            ('0',  '0', '0', '0', '0', '1+'): 'not applicable'},
    'or': {('1+', '0+', '0+', '0+', '0+', '0+'): 'true',
           ('0', '1+', '0', '0', '0', '0+'): 'false',
           ('0', '0+', '1+', '0+', '0+', '0+'): 'error',
           ('0', '0+', '0', '1+', '0+', '0+'): 'unknown',
           ('0', '0+', '0', '0', '1+', '0+'): 'not evaluated',
           ('0', '0', '0', '0', '0', '1+'): 'not applicable'},
    'one': {('1+', '0+', '0', '0', '0', '0+'): 'true',
            ('2+', '0+', '0+', '0+', '0+', '0+'): 'false',
            ('0', '1+', '0', '0', '0', '0+'): 'false',
            ('0,1', '0+', '1+', '0+', '0+', '0+'): 'error',
            ('0,1', '0+', '0', '1+', '0+', '0+'): 'unknown',
            ('0,1', '0+', '0', '0', '1+', '0+'): 'not evaluated',
            ('0', '0', '0', '0', '0', '1+'): 'not applicable'},
    'xor': {('odd', '0+', '0', '0', '0', '0+'): 'true',
            ('even', '0+', '0', '0', '0', '0+'): 'false',
            ('0+', '0+', '1+', '0+', '0+', '0+'): 'error',
            ('0+', '0+', '0', '1+', '0+', '0+'): 'unknown',
            ('0+', '0+', '0', '0', '1+', '0+'): 'not evaluated',
            ('0', '0', '0', '0', '0', '1+'): 'not applicable'}
}

set_rule = {
    'COMPLEMENT': (
        ('error', 'error', 'error', 'does not exist', 'error', 'error'),
        ('error', 'complete', 'incomplete', 'does not exist', 'not collected', 'error'),
        ('error', 'error', 'error', 'does not exist', 'not collected', 'error'),
        ('error', 'complete', 'incomplete', 'does not exist', 'not collected', 'error'),
        ('error', 'not collected', 'not collected', 'does not exist', 'not collected', 'error'),
        ('error', 'error', 'error', 'error', 'error', 'error')
    ),
    'INTERSECTION': (
        ('error', 'error', 'error', 'does not exist', 'error', 'error'),
        ('error', 'complete', 'incomplete', 'does not exist', 'not collected', 'complete'),
        ('error', 'incomplete', 'incomplete', 'does not exist', 'not collected', 'incomplete'),
        ('does not exist', 'does not exist', 'does not exist', 'does not exist', 'does not exist', 'does not exist'),
        ('error', 'not collected', 'not collected', 'does not exist', 'not collected', 'not collected'),
        ('error', 'complete', 'incomplete', 'does not exist', 'not collected', 'not applicable')
    ),
    'UNION': (
        ('error', 'error', 'error', 'error', 'error', 'error'),
        ('error', 'complete', 'incomplete', 'complete', 'incomplete', 'complete'),
        ('error', 'incomplete', 'incomplete', 'incomplete', 'incomplete', 'incomplete'),
        ('error', 'complete', 'incomplete', 'does not exist', 'incomplete', 'does not exist'),
        ('error', 'incomplete', 'incomplete', 'incomplete', 'not collected', 'not collected'),
        ('error', 'complete', 'incomplete', 'does not exist', 'not collected', 'not applicable')
    )
}

import re
cmp_func = {
    '': lambda a, b: a == b,
    'pattern match': lambda a, b: re.match(str(b), str(a)) is not None,
    'equals': lambda a, b: a == b,
    'not equal': lambda a, b: a != b,
    'less than or equal': lambda a, b: a <= b,
    'less than': lambda a, b: a < b,
    'greater than or equal': lambda a, b: a >= b,
    'greater than': lambda a, b: a > b,
    'case insensitive equals': lambda a, b: str(a).lower() == str(b).lower(),
    'case insensitive not equals': lambda a, b: str(a).lower() != str(b).lower()
}

arithmetic_func = {
    'add': lambda a: sum(a),
    'multiply': lambda a: reduce(lambda x, y: x*y, a)
}

Negate = {'true': 'false', 'false': 'true', 'error': 'error', 'unknown': 'unknown',
          'not evaluated': 'not evaluated', 'not applicable': 'not applicable'}

set_operation = {
    'COMPLEMENT': lambda a, b: [i for i in a if i not in b],
    'INTERSECTION': lambda a, b: [i for i in a if i in b],
    'UNION': lambda a, b: a+b
}