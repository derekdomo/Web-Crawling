__author__ = 'XiangyuSun'
import traceback
from threading import Thread, Lock
from Queue import Queue, Empty
import logging

log = logging.getLogger('threadPool')


class ThreadPool(object):
    def __init__(self, threadNum):
        self.pool = []
        self.threadNum = threadNum
        self.lock = Lock()
        self.running = 0
        self.taskQueue = Queue()
        self.resultQueue = Queue()

    def startThreads(self):
        for i in xrange(self.threadNum):
            self.pool.append(ThreadWorker(self))

    def stopThreads(self):
        for thread in self.pool:
            thread.stop()
            thread.join()
        del self.pool[:]

    def putTask(self, func, *args, **kargs):
        self.taskQueue.put((func, args, kargs))

    def getTask(self, *args, **kargs):
        task = self.taskQueue.get(*args, **kargs)
        return task

    def taskJoin(self, *args, **kargs):
        self.taskQueue.join()

    def taskDone(self, *args, **kargs):
        self.taskQueue.task_done()

    def putTaskResult(self, *args):
        self.resultQueue.put(args)

    def getTaskResult(self, *args, **kargs):
        return self.resultQueue.get(*args, **kargs)

    def increaseRunsNum(self):
        self.lock.acquire()
        self.running += 1
        self.lock.release()

    def decreaseRunsNum(self):
        self.lock.acquire()
        self.running -= 1
        self.lock.release()

    def getAllTaskCount(self):
        return self.taskQueue.qsize() + self.resultQueue.qsize()+self.running


class ThreadWorker(Thread):
    def __init__(self, threadPool):
        Thread.__init__(self)
        self.threadPool = threadPool
        self.daemon = True
        self.state = None
        self.start()

    def stop(self):
        self.state = 'STOP'

    def run(self):
        while 1:
            if self.state == 'STOP':
                break
            try:
                func, args, kargs = self.threadPool.getTask(timeout=1)
            except Empty:
                continue
            try:
                self.threadPool.increaseRunsNum()
                result = func(*args, **kargs)
                self.threadPool.decreaseRunsNum()
                if result:
                    self.threadPool.putTaskResult(*result)
                self.threadPool.taskDone()
            except Empty:
                log.critical(traceback.format_exc())