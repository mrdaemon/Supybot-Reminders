""" Database interface and storage backend for the reminders """
import os
import sys

import sqlite3 as sqlite


class dbstore(object):
    def __init__(self, filepath):
        self.filepath = filepath
        _dbinit()


    def get_reminders():
        with sqlite.connect(self.filepath) as conn:
            query = "SELECT * FROM reminders"

    def _dbinit(self):
        """ Initialize and setup database """

        if not os.path.exists(self.filepath):
            try:
                f = open(self.filepath, 'w')
                f.close()
            except IOError as exc:
                raise IOError(("Unable to create database at %s: %s" %
                    self.filepath, exc.message))
        else:
            return

        with sqlite.connect(self.filepath) as conn:
            query = """
            CREATE TABLE IF NOT EXISTS `reminders`
                `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                `sender` TEXT NOT NULL,
                `target` TEXT NOT NULL,
                `time` DATETIME NOT NULL,
                `message` TEXT NOT NULL
            );
            """

            cursor = conn.cursor()
            cursor.executescript(query)
            cursor.commit()


