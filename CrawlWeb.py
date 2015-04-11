#!/usr/bin/env python
# coding=utf-8
__author__ = 'XiangyuSun'

from crawlerAPI import crawler as crawl
import argparse

def url(rawValue):
    if not rawValue.startswith('http'):
        value = 'http://' + rawValue
        return value
    return rawValue

def positiveInt(rawValue):
    errorInfo = "Must be a positive integer."
    try:
        value = int(rawValue)
    except ValueError:
        raise argparse.ArgumentTypeError(errorInfo)
    if value < 1:
        raise argparse.ArgumentTypeError(errorInfo)
    else:
        return value

_default = dict(
    logfile = 'spider.log',
    dbFile = 'data.db',
    loglevel = 3,
    threadNum = 10,
    keyword = '',
    maxWebPages=10000,
    )

def startCrawl():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', type=url, required=True, metavar='URL', dest='url',
                   help='Specify the begin url')
    parser.add_argument('-d', type=positiveInt, required=True, metavar='DEPTH', dest='depth',
                   help='Specify the crawling depth')
    parser.add_argument('--dbfile', type=str, metavar='FILE', default=_default['dbFile'], dest='dbFile',
                   help='The SQLite file path. Default:%s' % _default['dbFile'])
    parser.add_argument('--thread', type=positiveInt, metavar='NUM', default=_default['threadNum'], dest='threadNum',
                   help='The amount of threads. Default:%d' % _default['threadNum'])
    parser.add_argument('--maxWebPages', type=positiveInt, metavar='NUM', default=_default['maxWebPages'], dest='maxWebPages',
                   help='The amount of web pages. Default:%d' % _default['maxWebPages'])
    args = parser.parse_args()
    crawlMachine = crawl.Crawler(args)
    crawlMachine.start()

if __name__ == '__main__':
    startCrawl()