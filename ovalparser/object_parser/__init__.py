#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__ = 'tongbin'

from .. import OvalBase, Item, Entity
from ..values import exist_order, FlagEnum, ResultEnum, StatusEnum, ExistenceEnum, FilterActionEnum, CheckEnum
from ..evaluate import exist_evaluated, set_evaluated
from ..state_parser import get_state


class Filter(OvalBase):
    __attrs__ = ('action', )

    def result(self, object_res):
        state_ref = self.node.get_data()
        node = self.states[state_ref]

        sta_name = self.get_clsname(node)
        module_name = self.get_mdlname(node)
        sta_cls = get_state(module_name, sta_name)
        res, list_res = sta_cls(node).result(CheckEnum.at_least_one, object_res)

        if self.action == FilterActionEnum.exclude:
            return [i for i in object_res if i not in list_res]

        return list_res


class Set(OvalBase):
    __attrs__ = ('set_operator', )

    def result(self):
        res = []
        filters = []
        for node in self.all():
            tagname = node.get_tagname()
            if tagname == 'filter':
                filters.append(node)
            elif tagname == 'set':
                res.append(Set(node).result())
            elif tagname == 'object_reference':
                object_node = self.objects[node.get_data()]
                module = self.get_mdlname(object_node)
                name = self.get_clsname(object_node)
                obj = get_object(module, name)(object_node)
                mark, result = obj.result(ExistenceEnum.any_exist)
                res.append((obj.flag(), result))
            else:
                raise Exception('The tag <set> does not support sub tag <%s>' % tagname)

        count = len(res)
        if count == 1:
            res = list(res[0])
        elif count == 2:
            res = list(set_evaluated(res, self.set_operator))
        else:
            raise Exception('Tag <set> error')

        for filt in filters:
            res[1] = Filter(filt).result(res[1])
        return res


class ObjectBase(OvalBase):
    def __init__(self, out_node):
        super(ObjectBase, self).__init__(out_node)
        self.counter = dict(zip(exist_order, (0, )*len(exist_order)))
        self.results = []
        self.filters = []
        self.entities = {}
        self.name = self.node.get_tagname().split('_')[0]
        self._items = None
        self._flag = None
        for node in self.all():
            tagname = node.get_tagname()
            if tagname == 'filter':
                self.filters.append(node)
            elif tagname == 'set':
                self._flag, self._items = Set(node).result()
            elif tagname == 'behaviors':
                continue
            else:
                self.entities[tagname] = Entity(node)

        if self._items and self.entities:
            raise Exception('<%s_object> error' % self.name)

    def items(self):
        ret = []
        items = self.client.get(self.name)
        for item in items:
            if not all(key in item.keys() for key in self.entities.keys()):
                item = Item()
                item.status = StatusEnum.error
                return [item]
            if all([entity.result(item.get(name)) for name, entity in self.entities.items()]):
                ret.append(item)
        return ret

    def products(self):
        if self._items is None:
            self._items = self.items()

        for filt in self.filters:
            self._items = Filter(filt).result(self._items)

    def collections(self):
        if not self._items:
            self.counter[StatusEnum.does_not_exist] = 1
        for item in self._items:
            self.counter[item.status] += 1
            if item.status == StatusEnum.exists:
                self.results.append(item)

    def flag(self):
        return self.client.flag(self.name)

    def ret(self, check_existence):
        flag = self._flag or self.flag()
        if flag == FlagEnum.error:
            return ResultEnum.error
        if flag == FlagEnum.not_collected:
            return ResultEnum.unknown
        if flag == FlagEnum.not_applicable:
            return ResultEnum.not_applicable
        if flag == FlagEnum.does_not_exist:
            self._items = [(StatusEnum.does_not_exist, None)]
            self.collections()
            return exist_evaluated(self.counter, check_existence)

        self.products()
        self.collections()
        if flag == FlagEnum.complete:
            return exist_evaluated(self.counter, check_existence)
        if check_existence == ExistenceEnum.none_exist and self.counter[StatusEnum.exists]:
            return ResultEnum.false
        if check_existence == ExistenceEnum.only_one_exists and self.counter[StatusEnum.exists] > 1:
            return ResultEnum.false

        return ResultEnum.unknown

    def result(self, check_existence):
        return self.ret(check_existence), self.results


def get_object(module, name):
    import independent
    cls_name = name.capitalize()+'Object'
    if module not in locals():
        return ObjectBase
    if not hasattr(locals()[module], cls_name):
        return ObjectBase
    return getattr(locals()[module], cls_name)