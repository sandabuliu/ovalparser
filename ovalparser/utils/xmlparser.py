#!/usr/bin/python
# -*- coding: UTF-8 -*-
__author__ = 'tongbin'

import re
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


class TagNode:
    def __init__(self, tag_node, tree):
        self.__root = tag_node
        self.__tree = tree
        tag = self.__root.tag
        self.__prog = re.compile(r'(\{(?P<field>.*)\})?(?P<name>.*)')
        res = self.__prog.match(tag)
        self.__tagname = res.group('name')
        self.__field = res.group('field')

    def __repr__(self):
        return '<TagNode:%s>' % self.get_tagname()

    def get_tagname(self):
        return self.__tagname

    def get_fieldname(self):
        return self.__field

    def get_childtag_list(self):
        return [TagNode(tag, self.__tree) for tag in self.__root]

    def get_data(self):
        return self.__root.text

    def get_child_tag(self, str_name):
        ret = []
        for tag in self.__root:
            ntag = TagNode(tag, self.__tree)
            if ntag.get_tagname() == str_name:
                ret.append(ntag)
        return ret

    def set_attr(self, str_var, str_data):
        self.__root.set(str_var, str_data)

    def get_attr(self, str_attrname):
        if str_attrname in self.__root.attrib:
            return self.__root.get(str_attrname)
        for name, value in self.__root.attrib.items():
            res = self.__prog.match(name)
            if str_attrname == res.group('name'):
                return value
        return ''

    def get_all_attrs(self):
        ret = {}
        for name, value in self.__root.attrib.items():
            res = self.__prog.match(name)
            ret[res.group('name')] = value
        return ret

    def write_xml(self, str_path):
        self.__tree.write(str_path)

    def find_tag(self, str_tagname):
        ret = []

        def _iter(tags, res):
            if tags is None:
                return
            for tag in tags:
                ntag = TagNode(tag, self.__tree)
                if ntag.get_tagname() == str_tagname:
                    res.append(ntag)
                _iter(tag, res)
        _iter(self.__root, ret)
        return ret

    @classmethod
    def load(cls, filename):
        tree = ET.parse(filename)
        return cls(tree.getroot(), tree)
