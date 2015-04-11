__author__ = 'XiangyuSun'

import sqlite3
import sys
reload(sys)
sys.setdefaultencoding('utf8')
class database():
    def __init__(self, dbFile):
        try:
            self.con = sqlite3.connect(dbFile, isolation_level=None, check_same_thread=False)
            self.con.execute('Create Table if not exists '
                             'webContent (id Integer Primary key autoincrement, url Text, content Text)')
        except:
            self.con = None

    def saveWeb(self, url, content):
        if self.con:
            sql = '''Insert into webContent (url, content) values (?, ?);'''
            self.con.execute(sql, (unicode(url), unicode(content)))
        else:
            raise sqlite3.OperationalError

    def close(self):
        if self.con:
            self.con.close()
        else:
            raise sqlite3.OperationalError