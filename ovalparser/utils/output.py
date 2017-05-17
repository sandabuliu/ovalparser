#!/usr/bin/env python
# -*-coding:utf8-*-

__author__ = 'tongbin'

from functools import wraps
from .. import Item


class Output(object):
    def __init__(self, source=None):
        self._source = source

    def __call__(self, **kwargs):
        for key in kwargs:
            print '%s: %s' % (key.upper(), kwargs[key])
        print

    def error(self, msg):
        print '<%s>' % self._source, msg

    def info(self, msg):
        pass


class LinkBase(object):
    class LinkError(Exception):
        def __init__(self, e=''):
            self.e = e

        def __str__(self):
            return str(self.e)

    @staticmethod
    def get(self, name):
        ret = []
        items = self.objects(name)
        for item in items:
            item = Item(item)
            item.status = self.status(name, item)
            ret.append(item)
        return ret

    @staticmethod
    def _catch(f):
        @wraps(f)
        def func(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception, e:
                raise LinkBase.LinkError('%s: %s' % (func.__name__, e))
        return func

    @staticmethod
    def check(cls):
        n_attrs = ('flag', 'get', 'link', 'unlink')
        c_attrs = ('flag', 'get', 'status', 'objects')
        for attr in n_attrs:
            if not hasattr(cls, attr):
                raise LinkBase.LinkError('Link class has no %s attribute' % attr)

        for attr in c_attrs:
            if hasattr(cls, attr):
                func = getattr(cls, attr)
                setattr(cls, attr, LinkBase._catch(func))
        return cls