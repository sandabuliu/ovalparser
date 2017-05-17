#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__ = 'tongbin'

import values
import datatype

version_info = (1, 0, 0)
version = '.'.join(str(n) for n in version_info[:2])
release = '.'.join(str(n) for n in version_info)

Item = type('Item', (dict, ), dict(status=None))


class OvalBase(object):
    __attrs__ = ()
    __root__ = None

    client = None
    tests = None
    objects = None
    states = None
    variables = None
    definitions = None
    records = None
    ev = None

    @staticmethod
    def type_check(item, type_name='string'):
        if type_name is None:
            type_name = 'string'
        type_name = type_name.upper()
        if not hasattr(datatype, type_name):
            raise Exception("The datatype doesn't support: %s" % type_name)

        force_type = getattr(datatype, type_name)
        try:
            return force_type(item)
        except Exception, e:
            return None

    @staticmethod
    def get_clsname(tag_node):
        tag_name = tag_node.get_tagname().lower()
        return tag_name.split('_')[0].capitalize()

    @staticmethod
    def get_mdlname(tag_node):
        field_name = tag_node.get_fieldname().lower()
        if field_name and '#' in field_name:
            return field_name.split('#')[-1]
        return None

    def set_item(self, attr_name):
        attr = self.node.get_attr(attr_name).lower()
        if hasattr(values, attr_name.upper()):
            content = getattr(values, attr_name.upper())
            attr = content[0] if attr == '' else attr
            if attr not in content:
                raise Exception("The attribute (%s='%s') only choose from %s" % (attr_name, attr, content))
        setattr(self, attr_name, attr)

    def __init__(self, node):
        self.node = node
        for item in self.__attrs__:
            self.set_item(item)

    def single(self, name=None):
        if name is None:
            tags = self.node.get_childtag_list()
        else:
            tags = self.node.get_child_tag(name)
        if len(tags) != 1:
            raise Exception('The count of tag <%s> should be 1' % name)
        return tags[0]

    def all(self, name=None):
        if name is None:
            tags = self.node.get_childtag_list()
        else:
            tags = self.node.get_child_tag(name)
        return tags

    def one_or_zero(self, name=None):
        if name is None:
            tags = self.node.get_childtag_list()
        else:
            tags = self.node.get_child_tag(name)
        count = len(tags)
        if count > 1:
            raise Exception('There is no tag <%s>' % name)
        return None if count == 0 else tags[0]


class Entity(OvalBase):
    __attrs__ = ('entity_check', )

    def __init__(self, node):
        super(Entity, self).__init__(node)
        self.name = self.node.get_tagname()

        item = self.node.get_attr('datatype').upper() or 'STRING'
        if not hasattr(datatype, item):
            raise Exception('Unsupport datatype: %s' % item)
        self.datatype = getattr(datatype, item)

        item = self.node.get_attr('operation')
        if item not in values.cmp_func:
            raise Exception('Unsupport operation: %s' % item)
        self.operator = values.cmp_func[item]

        var_ref = self.node.get_attr('var_ref')
        if var_ref and var_ref not in self.variables:
            raise Exception('Can not find the variable: %s' % var_ref)
        self.values = self.variables.get(var_ref, [self.node.get_data()])

        var_check = self.node.get_attr('var_check')
        if var_check and var_check not in values.CHECK:
            raise Exception('Bad variable check: %s' % var_check)
        var_check = var_check or None

        self.var_check = var_check or values.CHECK.all

    def operation(self, value1, value2):
        value1 = self.datatype(value1)
        value2 = self.datatype(value2)
        try:
            return self.operator(value1, value2)
        except:
            return False

    def result(self, value):
        list_res = [self.operation(value, v) for v in self.values]
        if self.var_check == values.CHECK.all:
            return all(list_res)
        if self.var_check == values.CHECK.at_least_one:
            return any(list_res)
        if self.var_check == values.CHECK.only_one:
            return list_res.count(True) == 1
        return not any(list_res)