#!/usr/bin/env python
# encoding=utf-8

"""
抓取知乎所有话题列表
"""
import HTMLParser
import datetime

from pymongo import MongoClient
from xtls.basecrawler import BaseCrawler
from xtls.codehelper import trytry
from xtls.logger import get_logger
from xtls.timeparser import now, parse_time
from xtls.util import BeautifulSoup

from config import *

logger = get_logger(__file__)
ZHIHU_URL = 'http://www.zhihu.com'
TOPIC_URL = 'http://www.zhihu.com/topic/{tid}/top-answers?page='
MONGO = MongoClient(MONGO_HOST, MONGO_PORT)


class TopicHotCrawler(BaseCrawler):
    def __init__(self, topic_id):
        super(TopicHotCrawler, self).__init__(topic_id=topic_id)

    @classmethod
    def save(cls, data):
        MONGO[DB][TOPIC_COLL].update_one({'_id': data['_id']}, {'$set': data}, upsert=True)

    @classmethod
    def unescape(cls, string):
        html_parser = HTMLParser.HTMLParser()
        html = html_parser.unescape(string)
        html = html[1 + html.find('>'):html.rfind('<')].strip()
        e_time = ''
        try:
            text = BeautifulSoup(html).find('a', class_='answer-date-link last_updated meta-item').getText().strip()
            if text.startswith(u'编辑于'):
                e_time = parse_time(text)
        except:
            pass
        return html, e_time

    @classmethod
    def parse_answer(cls, soup):
        title_a = soup.find('a', class_='question_link')
        body = soup.find('div', class_="entry-body")

        author = soup.find('div', class_='zm-item-answer-author-info')
        comment_cnt, a_name, a_desc, a_link, r_time = 0, u'匿名用户', '', '', ''

        with trytry():
            r_time = datetime.datetime.fromtimestamp(int(body['data-created'])).strftime('%Y-%m-%d %H:%M:%S')

        with trytry():
            a = author.find('a', class_='author-link')
            if a:
                a_name = a.getText().strip()
                a_link = ZHIHU_URL + a['href']
            else:
                a_name = author.find('span', class_='name').getText().strip()
            a_desc = author.find('span', class_='bio')['title']
        with trytry():
            comment_cnt = int(soup.find('a', class_=' meta-item toggle-comment').getText().replace(u'条评论', '').strip())

        content, e_time = cls.unescape(unicode(soup.find('textarea', class_='content hidden')))
        if not e_time:
            e_time = r_time
        result = {
            'a_name': a_name,
            'a_link': a_link,
            'a_desc': a_desc,
            'r_time': r_time,
            'e_time': e_time,
            'comment_cnt': comment_cnt,
            'question': title_a.getText().strip(),
            'agree_cnt': int(soup.find('a', class_='zm-item-vote-count')['data-votecount']),
            '_id': ZHIHU_URL + title_a['href'] + '/answer/' + body['data-atoken'],
            'content': content,
            'topics': []
        }
        return result

    def _run(self, soup):
        for index, item in enumerate(soup.find_all('div', class_='feed-item')):
            yield self.parse_answer(item)

    def save(self, data):
        logger.info('saving %s' % data['_id'])
        coll = MONGO[DB][HOT_ANSWER_COLL]
        old = coll.find_one({'_id': data['_id']})
        if not old:
            MONGO[DB][TOPIC_COLL].update_one({'_id': self.topic_id}, {'$inc': {'count': 1}})
            coll.insert_one(data)
            return 0
        elif self.topic_id not in old['topics']:
            MONGO[DB][TOPIC_COLL].update_one({'_id': self.topic_id}, {'$inc': {'count': 1}})
            data['topics'].extend(old['topics'])
            coll.update_one({'_id': data['_id']}, {'$set': data})
            return 1
        else:
            return -1

    def run(self):
        base_url = TOPIC_URL.format(tid=self.topic_id)
        for page in xrange(1, 10):
            url = base_url + str(page)
            logger.info('crawling topic %s, page %s' % (self.topic_id, page))

            try:
                html = self.get(url)
                soup = BeautifulSoup(html)
            except:
                return

            for answer in self._run(soup):
                answer['topics'].append(self.topic_id)
                answer['updateTime'] = now()
                result = self.save(answer)
                if result < 0:
                    return


def main():
    # TopicHotCrawler('19552832').run()
    for index, item in enumerate(MONGO[DB][TOPIC_COLL].find().batch_size(1)):
        logger.info('now topic %s-%s' % (index, item['_id']))
        TopicHotCrawler(item['_id']).run()


if __name__ == '__main__':
    main()
