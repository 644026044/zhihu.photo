#!/usr/bin/env python
# encoding=utf-8

import os
import re

from pymongo import MongoClient
from xtls.basecrawler import BaseCrawler
from xtls.codehelper import no_exception
from xtls.logger import get_logger
from xtls.timeparser import now
from xtls.util import BeautifulSoup
from xtls.util import sha1

from config import *

logger = get_logger(__file__)
MONGO = MongoClient(MONGO_HOST, MONGO_PORT)
CATEGORY_PATTERN = re.compile(ur'\[(.+?)\](.+?)\[(\d+)[P|p]\]')
HOST = 'http://www.t66y.com/'


def save(content, filename):
    save_path = os.path.join('/data/t66y', filename[:4])
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    file_path = os.path.join(save_path, filename)
    with open(file_path, 'wb') as fp:
        fp.write(content)


class ClCrawler(BaseCrawler):
    def __init__(self, start=1, end=1):
        super(ClCrawler, self).__init__(start=start, end=end)

    @no_exception(on_exception=None)
    def find_imgs(self, uri):
        url = HOST + uri
        soup = BeautifulSoup(self.get(url))
        img_list = []
        for input in soup.find_all('input', type="image"):
            img = input['src']
            content = self.get(img)
            filename = sha1(content) + img[img.rfind('.'):]
            save(content, filename)
            img_list.append({
                'url': img,
                'hash': filename,
            })
        return img_list

    @classmethod
    def mapping_category(cls, category):
        if category in (u'动漫cos第三期', u'其他'):
            return category
        if u'真' in category:
            return u'写真'
        if u'洲' in category:
            return u'亚洲'
        if u'漫' in category:
            return u'动漫'
        if u'美' in category:
            return u'欧美'
        return u'其他'

    @no_exception(on_exception=None)
    def parse_cat_tr(self, tr):
        tds = tr.find_all('td')
        if len(tds) != 5:
            return None
        title = tds[1].getText().strip().replace('\n', '').replace('\t', '')
        title_sp = CATEGORY_PATTERN.findall(title)
        if not title_sp:
            return None
        data = {
            '_id': sha1(title),
            'category': self.mapping_category(title_sp[0][0]),
            'title': title_sp[0][1],
            'img_count': int(title_sp[0][2]),
            'raw_path': tds[1].find('a')['href'],
            'pub_date': tds[2].find('div', class_='f10').getText()
        }
        if self.check_exists(data['_id']):
            return None
        imgs = self.find_imgs(data['raw_path'])
        if not imgs:
            return None
        data['images'] = imgs
        return data

    @classmethod
    def check_exists(cls, id_):
        return MONGO[DB][T66Y_COLL].find_one({'_id': id_})

    @classmethod
    def save(cls, data):
        data['update'] = now()
        try:
            MONGO[DB][T66Y_COLL].insert_one(data)
        except:
            pass

    def parse_catalog(self, soup):
        for idx, tr in enumerate(soup.find_all('tr', class_='tr3 t_one'), 1):
            data = self.parse_cat_tr(tr)
            if not data:
                continue
            self.save(data)
            # print json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4)
            # break

    def run(self):
        for page in xrange(self.end, self.start - 1, -1):
            logger.info('crawl t66y page %s' % page)
            html = self.get(HOST + 'thread0806.php?fid=8&search=&page=' + str(page))
            soup = BeautifulSoup(html)
            self.parse_catalog(soup)


def main():
    crawler = ClCrawler()
    crawler.run()


if __name__ == '__main__':
    main()
