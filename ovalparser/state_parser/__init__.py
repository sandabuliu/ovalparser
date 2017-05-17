#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__ = 'tongbin'

from .. import OvalBase, Entity
from ..values import check_order, ResultEnum
from ..evaluate import check_evaluated


class StateBase(OvalBase):
    def __init__(self, node):
        super(StateBase, self).__init__(node)
        self.entities = {}
        for node in self.all():
            tagname = node.get_tagname()
            self.entities[tagname] = Entity(node)

    def result(self, check, obj_results):
        counter = dict(zip(check_order, (0, )*len(check_order)))

        list_res = []
        for item in obj_results:
            res = ResultEnum.true
            for name, entity in self.entities.items():
                args = item[name] if isinstance(item[name], list) else [item[name]]
                entity_res = [entity.result(arg) for arg in args]
                result = {ResultEnum.true: entity_res.count(True),
                          ResultEnum.false: entity_res.count(False)}
                res = check_evaluated(result, entity.entity_check)
                if res == ResultEnum.false:
                    break
            counter[res] += 1
            if res == ResultEnum.true:
                list_res.append(item)

        return check_evaluated(counter, check), list_res


def get_state(module, name):
    cls_name = name.capitalize()+'State'
    if module not in locals():
        return StateBase
    if not hasattr(locals()[module], cls_name):
        return StateBase
    return getattr(locals()[module], cls_name)
