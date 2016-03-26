#!/usr/bin/env python
# encoding=utf-8

from pymongo import MongoClient
from config import *

MONGO = MongoClient(MONGO_HOST, MONGO_PORT)


def select(coll, filter, limit=20, skip=0, sort=('updateTime', -1)):
    datas = MONGO[DB][coll].find(filter).sort(*sort)
    count = datas.count()
    return [x for x in datas.skip(skip).limit(limit)], count


def select_one(coll, filter):
    return MONGO[DB][coll].find_one(filter)


if __name__ == '__main__':
    for item in select(ANSWER_COLL, {}):
        print item['updateTime']
