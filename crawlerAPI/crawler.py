__author__ = 'XiangyuSun'

from urlparse import urljoin, urlparse
from collections import deque
import re
import traceback
import requests
import logging
import time

from databaseAPI import database
from BeautifulSoup import BeautifulSoup as bs
from threadPool import ThreadPool

log = logging.getLogger('crawler')

class Crawler(object):

    def __init__(self, args):
        self.depth = args.depth
        self.currentDepth = 1
        self.database = database(args.dbFile)
        self.threadPool = ThreadPool(args.threadNum)
        self.visitUrls = set()
        self.unvisitedUrls = deque()
        self.unvisitedUrls.append(args.url)
        self.isCrawling = False
        self.maxWebPages = args.maxWebPages

    def requestPage(self, url, retry=2):
        try:
            h = self.customerHeader(url)
            content = requests.get(url, headers=h, timeout=10)
            self.handleEncoding(content)
            if content.status_code == requests.codes.ok:
                if 'html' in content.headers['Content-Type']:
                    return content.text
            log.warning('Page not available. Status code:%d URL:%s\n' % (content.status_code, url))
        except Exception:
            if retry > 0:
                return self.requestPage(url, retry-1)
            else:
                log.debug('request Fail URL:%s' % url)
        return None

    def extractUrls(self, content, url):
        allUrls = self.getAllHrefs(url, content)
        for href in allUrls:
            if self.isHttpProtocol(href):
                if href not in self.visitUrls and href not in self.unvisitedUrls:
                    self.unvisitedUrls.append(href)

    def saveResult(self, content, url):
        self.database.saveWeb(url, content)

    def taskHandler(self, url):
        content = self.requestPage(url)
        self.saveResult(content, url)
        self.extractUrls(content, url)

    def assignTask(self):
        while self.unvisitedUrls:
            url = self.unvisitedUrls.popleft()
            self.threadPool.putTask(self.taskHandler, url)
            self.visitUrls.add(url)

    def start(self):
        print '\n Start Crawling\n'
        if self.database.con:
            self.isCrawling = True
            self.threadPool.startThreads()
            while self.currentDepth < self.depth+1:
                self.assignTask()
                while self.threadPool.getAllTaskCount():
                    time.sleep(4)
                print 'Depth %d Finish' % self.currentDepth
                print 'Totally crawled %d links' % len(self.visitUrls)
                log.info('Depth %d Finish. Totally crawled %d links' % (self.currentDepth, len(self.visitUrls)))
                if len(self.visitUrls) > self.maxWebPages:
                    break
                self.currentDepth += 1
            self.stop()

    def stop(self):
        self.isCrawling = False
        self.threadPool.stopThreads()
        self.database.close()
        self.database.close()

    def customerHeader(self, url):
        headers = {
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset' : 'gb18030,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding' : 'gzip,deflate,sdch',
            'Accept-Language' : 'en-US,en;q=0.8',
            'Connection': 'keep-alive',
            'User-Agent' : 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.4 (KHTML, like Gecko) Chrome/22.0.1229.79 Safari/537.4',
            'Referer' : url,
        }
        return headers

    def getAllHrefs(self, url, content):
        hrefs = []
        s = bs(content)
        res = s.findAll('a', href=True)
        for r in res:
            href = r.get('href').encode('utf8')
            if not href.startswith('http'):
                href = urljoin(url, href)
            hrefs.append(href)
        return hrefs

    def isHttpProtocol(self, href):
        protocal = urlparse(href).scheme
        if protocal == 'http' or protocal == 'https':
            return True
        return False

    def handleEncoding(self, response):
        if response.encoding == 'ISO-8859-1':
            charset_re = re.compile("((^|;)\s*charset\s*=)([^\"']*)", re.M)
            charset=charset_re.search(response.text)
            charset=charset and charset.group(3) or None
            response.encoding = charset