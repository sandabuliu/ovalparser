#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__ = 'tongbin'

import re
import os
import itertools
from values import Negate, check_order, arithmetic_func, ResultEnum, DEPRECATED, NEGATE
from evaluate import operator_evaluated
from utils.xmlparser import TagNode
from utils.output import Output, LinkBase
from object_parser import get_object
from state_parser import get_state
from . import OvalBase


class Object(OvalBase):
    __attrs__ = ('object_ref', )

    def result(self, check_existence='at_least_one_exists'):
        node = self.objects[self.object_ref]
        obj_name = self.get_clsname(node)
        module_name = self.get_mdlname(node)
        obj_cls = get_object(module_name, obj_name)
        self.records['object'][self.object_ref] = obj_cls(node).result(check_existence)
        return self.records['object'][self.object_ref]


class State(OvalBase):
    __attrs__ = ('state_ref', )

    def result(self, check, obj_res):
        node = self.states[self.state_ref]
        sta_name = self.get_clsname(node)
        module_name = self.get_mdlname(node)
        sta_cls = get_state(module_name, sta_name)
        self.records['state'][self.state_ref], list_res = sta_cls(node).result(check, obj_res)
        return self.records['state'][self.state_ref]


class Test(OvalBase):
    __attrs__ = ('check_existence', 'check', 'id', 'state_operator')

    def result(self):
        if self.records['test'][self.id] is not None:
            return self.records['test'][self.id]

        object_node = self.one_or_zero('object')
        if object_node is None:
            self.records['test'][self.id] = ResultEnum.unknown
            return self.records['test'][self.id]

        res, obj_res = Object(object_node).result(self.check_existence)

        if res != ResultEnum.true or not obj_res:
            self.records['test'][self.id] = res
            return self.records['test'][self.id]

        state_nodes = self.all('state')
        if state_nodes:
            counter = dict(zip(check_order, (0, )*len(check_order)))
            for state_node in state_nodes:
                ret = State(state_node).result(self.check, obj_res)
                counter[ret] += 1
            res = operator_evaluated(counter, self.state_operator)

        self.records['test'][self.id] = res
        return self.records['test'][self.id]


class Criterion(OvalBase):
    __attrs__ = ('test_ref', 'negate')

    def result(self):
        test = self.tests[self.test_ref]
        res = Test(test).result()
        return Negate[res] if self.negate == NEGATE.true else res


class Extend_definition(OvalBase):
    __attrs__ = ('definition_ref', 'negate')

    def result(self):
        definition = self.definitions[self.definition_ref]
        result = Definition(definition).result()
        return Negate[result] if self.negate == NEGATE.true else result


class Criteria(OvalBase):
    __attrs__ = ('operator', 'negate')

    def result(self):
        counter = dict(zip(check_order, (0, )*len(check_order)))

        for node in self.all():
            tagname = node.get_tagname()
            res = globals()[tagname.capitalize()](node).result()
            counter[res] += 1

        res = operator_evaluated(counter, self.operator)
        return Negate[res] if self.negate == NEGATE.true else res


class Metadata(OvalBase):
    def result(self):
        ret = {'reference': {}}
        for ref in self.all('reference'):
            ret['reference'][ref.get_attr('source')] = ref.get_attr('ref_id')
        ret['title'] = self.single('title').get_data()
        return ret


class Definition(OvalBase):
    __attrs__ = ('deprecated', 'id')

    def description(self):
        if not hasattr(self, '_desc'):
            metadata = self.single('metadata')
            self._desc = Metadata(metadata).result()
        return self._desc

    def result(self):
        if self.records['definition'][self.id] is None:
            criteria = self.one_or_zero('criteria')
            if criteria is None:
                self.records['definition'][self.id] = ResultEnum.unknown
            else:
                self.records['definition'][self.id] = Criteria(criteria).result()
        return self.records['definition'][self.id]


class Variable(OvalBase):
    __attrs__ = ('datatype', 'id')

    def result(self):
        if self.records['variable'][self.id] is not None:
            return self.records['variable'][self.id]

        cls_name = self.node.get_tagname().capitalize()
        obj = globals()[cls_name](self.node)
        list_res = obj.result()
        res = []
        append = lambda a: None if a is None else res.append(a)
        for item in list_res:
            if isinstance(item, list):
                for i in item:
                    append(i)
            else:
                append(item)
        self.records['variable'][self.id] = res
        return self.records['variable'][self.id]


class External_variable(OvalBase):
    __attrs__ = ('id', )

    def result(self):
        value = self.ev.get(self.id, [])
        if not isinstance(value, list):
            value = [value]
        return value


class Local_variable(OvalBase):
    def result(self):
        list_res = []
        for sub_tag in self.all():
            cls_name = sub_tag.get_tagname().capitalize()
            obj = globals()[cls_name](sub_tag)
            list_res.append(obj.result())
        return list_res


class Constant_variable(OvalBase):
    def result(self):
        list_res = []
        for value in self.all():
            list_res.append(value.get_data())
        return list_res


class Object_component(Object):
    __attrs__ = ('object_ref', 'item_field')

    def result(self):
        res, obj_res = super(Object_component, self).result()
        list_res = []
        for item in obj_res:
            if isinstance(item, dict) and self.item_field in item:
                if isinstance(item[self.item_field], list):
                    list_res += item[self.item_field]
                else:
                    list_res.append(item[self.item_field])

        return list_res


class Variable_component(OvalBase):
    __attrs__ = ('var_ref', )

    def result(self):
        variable = self.variables[self.var_ref]
        return Variable(variable).result()


class Literal_component(OvalBase):
    __attrs__ = ('datatype', )

    def result(self):
        res = self.type_check(self.node.get_data(), self.datatype)
        return [res]


class Arithmetic(OvalBase):
    __attrs__ = ('arithmetic_operation', )

    def result(self):
        list_res = Local_variable(self.node).result()
        if not list_res:
            return []

        operator = self.arithmetic_operation
        get_number = lambda a: self.type_check(a, 'int') or self.type_check(a, 'float')
        get_numbers = lambda a: [get_number(i) for i in a if i is not None]
        res = []
        for values in itertools.product(*list_res):
            res.append(arithmetic_func[operator](get_numbers(values)))
        return res


class Begin(OvalBase):
    __attrs__ = ('character', )

    def result(self):
        sub_tag = self.single()
        cls_name = sub_tag.get_tagname().capitalize()
        obj = globals()[cls_name](sub_tag)
        list_res = obj.result()

        return [res for res in list_res if res.lower().startswith(self.character.lower())]


class Concat(OvalBase):
    def result(self):
        list_res = Local_variable(self.node).result()
        if not list_res:
            return []

        res = []
        get_strings = lambda a: [str(i) for i in a]
        for values in itertools.product(*list_res):
            res.append(''.join(get_strings(values)))
        return res


class Count(OvalBase):
    def result(self):
        list_res = Local_variable(self.node).result()
        return [sum([len(l) for l in list_res])]


class End(OvalBase):
    __attrs__ = ('character', )

    def result(self):
        sub_tag = self.single()
        cls_name = sub_tag.get_tagname().capitalize()
        obj = globals()[cls_name](sub_tag)
        list_res = obj.result()

        return [res for res in list_res[0] if res.lower().endswith(self.character.lower())]


class Escape_regex(OvalBase):
    def result(self):
        sub_tag = self.single()
        cls_name = sub_tag.get_tagname().capitalize()
        obj = globals()[cls_name](sub_tag)
        list_res = obj.result()

        res = []
        for item in list_res:
            reg_marks = '^$\.[](){}*+?|'
            for mark in reg_marks:
                item = str(item).replace(mark, '')
            res.append(item)
        return res


class Split(OvalBase):
    __attrs__ = ('delimiter', )

    def result(self):
        sub_tag = self.single()
        cls_name = sub_tag.get_tagname().capitalize()
        obj = globals()[cls_name](sub_tag)
        list_res = obj.result()

        res = []
        for item in list_res[0]:
            item = item.split(self.delimiter)
            res += item
        return res


class Substring(OvalBase):
    __attrs__ = ('substring_start', 'substring_length')

    def result(self):
        sub_tag = self.single()
        cls_name = sub_tag.get_tagname().capitalize()
        obj = globals()[cls_name](sub_tag)
        list_res = obj.result()

        start = int(self.substring_start)-1
        length = int(self.substring_length)
        res = []
        for item in list_res:
            item = None if item is None else item[start:start+length]
            res.append(item)
        return res


class Unique(OvalBase):
    def result(self):
        list_res = Local_variable(self.node).result()
        return list(set(reduce(lambda x, y: x+y, list_res)))


class Regex_capture(OvalBase):
    __attrs__ = ('pattern', )

    def result(self):
        sub_tag = self.single()
        cls_name = sub_tag.get_tagname().capitalize()
        obj = globals()[cls_name](sub_tag)
        list_res = obj.result()

        res = []
        for item in list_res[0]:
            item = re.search(self.pattern, item)
            if item is None:
                res.append('')
                continue
            try:
                res.append(item.group(1))
            except Exception, e:
                raise Exception('The pattern SHOULD contain a single capturing sub-pattern (using parentheses).')
        return res


class Oval_definition(OvalBase):
    key_element = ('definition', 'test', 'object', 'state', 'variable')

    @staticmethod
    def init_oval(client, external_variable=None):
        OvalBase.tests = {}
        OvalBase.objects = {}
        OvalBase.states = {}
        OvalBase.variables = {}
        OvalBase.definitions = {}
        OvalBase.records = dict(zip(Oval_definition.key_element, ({}, {}, {}, {}, {})))
        OvalBase.ev = external_variable if external_variable else {}
        OvalBase.client = client

    def __init__(self, filepath, source='AXTX'):
        self.__root__ = TagNode.load(filepath)
        self.source = source
        self.output = Output()
        super(Oval_definition, self).__init__(self.__root__)

        for element in self.key_element:
            res = getattr(self, element+'s')
            for items in self.all(element+'s'):
                for item in items.get_childtag_list():
                    itemid = item.get_attr('id')
                    res[itemid] = item
                    if itemid not in self.records[element]:
                        self.records[element][itemid] = None

        for key, value in self.variables.items():
            if isinstance(value, list):
                continue
            self.variables[key] = Variable(value).result()

    def result(self):
        oval_res = {}
        for def_id, definition in self.definitions.items():
            definition = Definition(definition)
            if definition.deprecated == DEPRECATED.true:
                continue
            metadata = definition.description()
            ref_id = metadata['reference'].get(self.source)
            oval_res[ref_id] = definition.result()
            self.output(id=ref_id, result=oval_res[ref_id], title=metadata['title'])

        return oval_res


class OvalParser(object):
    def __init__(self, path, link_cls):
        self.path = path
        if not hasattr(link_cls, 'get'):
            self.link_cls = type('Link', (link_cls, ), dict(get=LinkBase.get))
        else:
            self.link_cls = link_cls
        self.link_cls = LinkBase.check(self.link_cls)
        self.results = {}

    def run(self):
        client = self.link_cls()
        client.link()
        Oval_definition.init_oval(client)
        for root, dirs, files in os.walk(self.path):
            for filepath in files:
                try:
                    if not filepath.endswith('.xml'):
                        continue
                    self.results.update(Oval_definition(root+'/'+filepath).result())
                except LinkBase.LinkError, e:
                    Output('Link').error(e)
                except Exception, e:
                    Output(filepath).error(e)
        client.unlink()

    def result(self):
        if not self.results:
            self.run()
        return self.results