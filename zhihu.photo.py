#!/usr/bin/env python
# encoding=utf-8

import sys

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer
from xtls.logger import get_logger

from app import create_app

app = create_app()
logger = get_logger(__file__)

if __name__ == '__main__':
    host = '0.0.0.0'
    port = 1994 if len(sys.argv) < 2 else int(sys.argv[1])
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(port=port, address=host)
    logger.info('lawyer asst server start at {}:{}'.format(host, port))
    IOLoop.instance().start()
