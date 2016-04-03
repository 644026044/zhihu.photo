#!/usr/bin/env python
# encoding=utf-8

from pymongo import MongoClient
import sqlite3
import time
from xtls.timeparser import now

from config import *

SQLITE = sqlite3.connect(SQLITE_DB_PATH)
SQLITE_SELETE = 'SELECT * FROM imgs ORDER BY id DESC LIMIT %d OFFSET {start}' % PAGE_SIZE

MONGO = MongoClient(MONGO_HOST, MONGO_PORT)


def select(coll, filter, limit=20, skip=0, sort=('updateTime', -1)):
    datas = MONGO[DB][coll].find(filter).sort(*sort)
    count = datas.count()
    return [x for x in datas.skip(skip).limit(limit)], count


def select_one(coll, filter):
    return MONGO[DB][coll].find_one(filter)


def insert(coll, data):
    data['updateTime'] = now()
    MONGO[DB][coll].find_one_and_update(
        {'_id': data['_id']},
        {'$set': data},
        upsert=True
    )


def get_qbcr_imgs(page):
    sql = SQLITE_SELETE.format(start=PAGE_SIZE * (page - 1))
    c = SQLITE.cursor()
    result = [item for item in c.execute(sql)]
    c.close()
    return result


count = last_change_time = 0


def get_qbcr_count():
    global count, last_change_time
    if time.time() - last_change_time > 86400:
        c = SQLITE.cursor()
        count = c.execute('select count(id) from imgs').next()[0]
        c.close()
        last_change_time = time.time()
    return count


if __name__ == '__main__':
    print get_qbcr_imgs(1)
