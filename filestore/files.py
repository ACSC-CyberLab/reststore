import os
import re
import hashlib
import tempfile
import sqlite3
import math
import random


DEFAULT_HASH_FUNCTION = hashlib.md5
DEFAULT_TUNE_SIZE = 100000000 # approx num of files we intend to reach


FILES_TABLE = "\
CREATE TABLE IF NOT EXISTS files (\
 hexdigest varchar,\
 filepath varchar,\
 created datetime DEFAULT current_timestamp);"
FILES_HEXDIGEST_IDX = "\
CREATE UNIQUE INDEX files_hexdigest_idx on files(hexdigest);"
LAST_ROWID = "SELECT MAX(rowid) from files;"
SELECT_FILEPATH = "SELECT filepath from files where hexdigest='?'"
INSERT_HEXDIGEST = "INSERT INTO files (hexdigest) value (?)"
UPDATE_FILEPATH = "UPDATE files set filepath='?' where hexdigest='?'"
SELECT_FILEPATH_HEXDIGEST = "\
SELECT (hexdigest, filepath) from files where rowid=?;"


class DataError(Exception): pass


class Files:
    def __init__(self, name='files', 
                       files_root=tempfile.gettempdir(),
                       hash_func=DEFAULT_HASH_FUNCTION,
                       tune_size=DEFAULT_TUNE_SIZE,
                       assert_data_ok=False):
        """
        
        """
        if os.path.sep in name or '..' in name:
            raise ValueError('name can not contain .. or %s' % os.path.sep)
        self.hash_func = hash_func
        self.hash_len = len(hash_func('').hexdigest())
        self._root = os.path.join(files_root, name)
        #create our db if it doesn't exist already
        self._db = os.path.join(self.root, 'files.db')
        if not os.path.exists(self._db):
            #new repo...  lets create it
            if not os.path.exists(self._root):
                os.makedirs(self._root)
            con = sqlite3.connect(self._db)
            con.execute(FILES_TABLE)
            con.execute(FILES_hexdigest_IDX)
            con.commit() 
            self.index = 0     
        self._width = math.ceil(math.pow(tune_size, 1.0/3))
        self._do_assert_data_ok = assert_data_ok

    def __len__(self):
        con = sqlite3.connect(self._db)
        c = con.execute(LAST_ROWID)
        res = c.fetchone()
        if res is None:
            i = 0
        else:
            i,_ = res
        return i
    
    def get(self, hexdigest):
        return self[hexdigest]

    def _assert_data_ok(self, hexdigest, filepath):
        if os.path.exists(filepath) is False:
            raise DataError('%s not found' % filepath)
        with open(filepath) as f:
            data = f.read()
        actual = self.hash_func(data).hexdigest()
        if hexdigest != actual:
            raise DataError('Expected %s, got %s' % (hexdigest, actual))

    def __getitem__(self, hexdigest):
        #look up hash in database
        con = sqlite3.connect(self._db)
        c = con.execute(LAST_ROWID)
        c = con.execute(SELECT_FILEPATH, (hexdigest,))
        res = c.fetchone()
        if res is None:
            raise KeyError('%s not found' % hexdigest)
        filepath, _ = res
        filepath = os.path.join(self._root, filepath)
        if self._do_assert_data_ok:
            self._assert_data_ok(hexdigest, filepath)          
        return filepath

    def __setitem__(self, hexdigest, data):
        #check if it already exists
        hexdigest = hexdigest.lower()
        try:
            self[hexdigest]
        except (KeyError, DataError):
            pass
        else:
            return
        #validate the data
        actual = self.hash_func(data).hexdigest()
        if hexdigest != actual:
            raise ValueError('actual hash %s != hexdigest %s' % \
                                (actual, hexdigest))
        #create our entry
        con = sqlite3.connect(self._db)
        c = con.execute(INSERT_HEXDIGEST, hexdigest) 
        rowid = c.lastrowid
        l1 = str(random.randint(0, self._width))
        l2 = str(random.randint(0, self._width))
        path = os.path.join(str(folder), str(folder), str(rowid))
        c = con.execute(INSERT_HEXDIGEST, path) 
        filepath = os.path.join(self._root, path)
        with open(filepath, 'wb') as f:
            f.write(data)
        con.commit()

    def __iter__(self):
        con = sqlite3.connect(self._db)
        c = con.execute("SELECT (hexdigest, filepath) from files")
        while True:
            rows = c.fetchmany()
            if not rows:
                break
            for row in rows:
                hexdigest, path = row
                filepath = os.path.join(self._root, path)
                if self._do_assert_data_ok:
                    self._assert_data_ok(hexdigest, filepath)
                yield (hexdigest, filepath)




