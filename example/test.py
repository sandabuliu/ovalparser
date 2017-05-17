#!/usr/bin/python
# -*- coding: UTF-8 -*-


from sqlalchemy import create_engine
from ovalparser.oval import OvalParser


def get_link(filepath):
    class _Link(object):
        def link(self):
            mysql_param = "sqlite:///" + filepath
            mysql_engine = create_engine(mysql_param)
            self.db = mysql_engine.connect()
            self._status = self.db.execute("select * from ObjectStatus").fetchall()
            self._flags = self.db.execute("select * from ObjectFlag").fetchall()

        def objects(self, name):
            try:
                return self.db.execute("select * from %s" % name).fetchall()
            except Exception:
                return []

        def status(self, name, item):
            for ste in self._status:
                if name == ste['name'] and item['id'] == ste['object_id']:
                    return ste['status']
            return 'exists'

        def flag(self, name):
            for flag in self._flags:
                if name == flag['object']:
                    return flag['flag']
            return 'complete'

        def unlink(self):
            self.db.close()

    return _Link

if __name__ == '__main__':
    Link = get_link('test.db')
    OvalParser('test2', Link).result()
