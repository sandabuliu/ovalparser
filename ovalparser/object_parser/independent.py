#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__ = 'l'


import re
from lxml import etree
from . import ObjectBase, Item
from ..values import StatusEnum, FlagEnum


class VariableObject(ObjectBase):
    def items(self):
        ret = []
        var_ref = self.entities['var_ref'].values[0]

        for variable in self.variables[var_ref]:
            item = Item()
            item['var_ref'] = var_ref
            item['value'] = variable
            item.status = StatusEnum.exists
            ret.append(item)
        return ret

    def flag(self):
        var_ref = self.entities['var_ref'].values[0]
        if var_ref in self.variables:
            return FlagEnum.complete
        return FlagEnum.error


class XmlfilecontentObject(ObjectBase):
    def items(self):
        ret = []
        items = self.client.get(self.name)
        for item in items:
            info = dict(filepath=item['filepath'])
            info['path'], info['filename'] = info['filepath'].rsplit('/', 1)
            info['xpath'] = self.entities['xpath'].values[0]

            if not all([entity.result(info.get(name)) for name, entity in self.entities.items()]):
                continue

            tree = etree.fromstring(item['content'])
            value_ofs = tree.xpath(info['xpath'])

            for value_of in value_ofs:
                term = Item(info)
                term.status = item.status
                term['value_of'] = value_of
                ret.append(term)
        return ret


class Textfilecontent54Object(ObjectBase):
    def items(self):
        items = self.client.get(self.name)
        instance = int(self.entities.pop('instance').values[0])
        if instance < 0:
            raise Exception('Instance error: %s' % instance)

        ret = []
        for item in items:
            info = dict(filepath=item['filepath'])
            info['path'], info['filename'] = info['filepath'].rsplit('/', 1)
            patterns = self.entities['pattern'].values
            info['pattern'] = patterns[0] if patterns else ''

            if not all([entity.result(info.get(name)) for name, entity in self.entities.items()]):
                continue

            reg = re.findall(r'(%s)' % info['pattern'], item['content'])
            if not reg:
                continue

            if instance > len(reg):
                continue

            term = Item(info)
            term.status = item.status
            term['text'] = reg[instance-1][0]
            term['subexpression'] = list(reg[instance-1][1:])
            ret.append(term)
        return ret