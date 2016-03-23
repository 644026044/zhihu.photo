#!/usr/bin/env python
# encoding=utf-8

import json

from xtls.basecrawler import BaseCrawler
from xtls.codehelper import forever
from xtls.util import BeautifulSoup

from util import *

logger = get_logger(__file__)
QUESTION_XHR_URL = 'https://www.zhihu.com/node/QuestionAnswerListV2'
ZHIHU_URL = 'https://www.zhihu.com'
QUESTION_URL = 'https://www.zhihu.com/question/{id}'


class QuestionCrawler(BaseCrawler):

    def __init__(self):
        super(QuestionCrawler, self).__init__()
        self.xsrf = load_xsrf()
        self._request.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36'
        logger.info('init question crawler done.')

    def _run(self, question_id, offset):
        data = {
            'method': 'next',
            'params': '{"url_token":%s,"pagesize":20,"offset":%s}' % (question_id, offset),
            '_xsrf': self.xsrf,
        }
        rst_json = json.loads(self.post(QUESTION_XHR_URL, data=data, timeout=60))

        rst = []
        for index, item in enumerate(rst_json['msg']):
            soup = BeautifulSoup(item)
            answer = AnswerParser(self, soup).parse()  # self.build_answer_item(soup)
            if not answer:
                continue
            AnswerParser.save(answer)
            rst.append(answer['_id'])
        return rst, len(rst_json['msg']) == 20

    def run(self, question_id):
        html = self.get(QUESTION_URL.format(id=question_id))
        soup = BeautifulSoup(html)
        question = QuestionParser(self, soup).parse()
        question['_id'] = question_id

        for index in forever():
            ids, has_more = self._run(question_id, index * 20)
            question['answers'].extend(ids)
            QuestionParser.save(question)
            logger.info('update question %s' % question_id)
            if not has_more:
                break


def main():
    QuestionCrawler().run('24214727')


if __name__ == '__main__':
    main()
