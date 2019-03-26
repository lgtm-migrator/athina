#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime, timezone
import os
from peewee import *

# Global database object
DB = SqliteDatabase(None)


class Database:
    db = None
    same_url_limit = 1  # Defines how many same urls are allowed, e.g., in cases of group projects this may be 2
    logger = None
    db_filename = None

    def __init__(self, db_filename='database.sqlite3', logger=None):
        self.db = DB
        self.db_filename = db_filename
        self.logger = logger

        if self.logger is not None:
            self.logger.logger.debug("Connecting to db file: %s" % db_filename)
        DB.init(self.db_filename)
        DB.connect()
        DB.create_tables([Users])
        # TODO: check if table exists otherwise output this
        # if self.logger is not None:
        #    self.logger.logger.error("Warning: Cannot load Users db (probably this is a
        #    first run for a new assignment).")
        os.chmod(db_filename, 0o666)

    def __del__(self):
        DB.close()

    @staticmethod
    def check_duplicate_url(same_url_limit=1):
        """Checks if there are duplicate urls submitted.

        @param same_url_limit: number of occurrences to be found to be considered plagiarism
        @return: None
        """
        urls = dict()
        for val in Users.select().where(Users.repository_url != ""):
            if urls.get(val.repository_url, 0) == 0:
                urls[val.repository_url] = [val.user_id]
            else:
                urls[val.repository_url].append(val.user_id)

            if len(urls[val.repository_url]) > same_url_limit:
                for i in urls[val.repository_url]:
                    obj = Users.get(Users.user_id == i)
                    if obj.same_url_flag is not True:
                        obj.same_url_flag = True
                        obj.save()
            else:
                if val.same_url_flag is not False:
                    val.same_url_flag = False
                    val.save()


class Users(Model):
    """
    The class containing local information obtained through canvas about each user, assignment status, last commit,
    plagiarism status and other important information for ATHINA to function.
    """
    user_id = BigIntegerField(primary_key=True)
    course_id = BigIntegerField(default=0)
    user_fullname = TextField(default="")
    secondary_id = TextField(default="")
    repository_url = TextField(default="", null=True)
    url_date = DateTimeField(default=datetime(1, 1, 1, 0, 0))  # When a new url was found
    new_url = BooleanField(default=False)  # Switched when new url is discovered on e-learning site
    commit_date = DateTimeField(default=datetime(1, 1, 1, 0, 0))  # Day of the last commit
    same_url_flag = BooleanField(default=False)  # Is repo url found to be similar with N other students?
    plagiarism_to_grade = BooleanField(default=False)  # Signifies whether a user received a new grade (plagiarism)
    last_plagiarism_check = DateTimeField(default=datetime.now(timezone.utc).replace(tzinfo=None))
    last_graded = DateTimeField(default=datetime(1, 1, 1, 0, 0))
    last_grade = SmallIntegerField(null=True)
    changed_state = BooleanField(default=False)

    class Meta:
        database = DB
