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
HOSTS_FILE="hosts"
SENSITIVE_FILE="directory_small"
hosts=open(HOSTS_FILE).readlines()
files=open(SENSITIVE_FILE).readlines()
requests.adapters.DEFAULT_RETRIES = 3

testx=0

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
def get_title(resp):
    r = re.findall("<title>([\s\S]+?)</title>", resp.content)
    title = lambda r : r and r[0] or ""
    return title(r)  
	
'''
save request,response to mysql database
'''
def http_to_database(req_uri,r,flag):
    try:
	    conn=MySQLdb.connect(host='localhost',user='root',passwd='donothackme1',port=3306,charset='utf8')
	    cur=conn.cursor()
	     
	    conn.select_db('fuzz_http')
	    #cur.execute('create table iqiyi(req_uri varchar(80),res_title varchar(100),res_status_code varchar(5),res_reason varchar(20),res_headers varchar(1000),res_text varchar(1000000),flag int(1))')
	    cur.execute('insert into iqiyi(req_uri,res_title,res_status_code,res_reason,res_headers,res_text,flag) values(%s,%s,%s,%s,%s,%s,%s)',(req_uri,get_title(r),r.status_code,r.reason,r.headers,r.text[:400],flag))
	    conn.commit()
	    conn.close()
    except Exception,e:
	    print e
     
'''
1.if  port==443 then,we need change http://x.x.x.x:443 to https://x.x.x.x
2.save request,response to mysql database
'''    
def fuzz_response(uri,filename):
    global testx
    testx=testx+1
    headers={'Connection':'keep-alive',"User-Agent":"Mozilla/5.0 (X11; Linux i686) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36","Origin":"http://www.oschina.net",'Accept-Encoding':'gzip,deflate,sdch','Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4','X-Requested-With':'XMLHttpRequest','Accept':'application/json,text/javascript,*/*;q=0.01'}
    if uri.split(":")[2]=="443":
        uri="https:"+uri.split(":")[1]
	#http_to_database(uri+"/"+filename,r.status_code,r.text,r.headers)
        #timeout
        #allow_redirects
    	r=requests.get(uri+"/"+filename,headers=headers,timeout=10,allow_redirects = False)
	return r
    else:
    	r=requests.get(uri+"/"+filename,headers=headers,timeout=10,allow_redirects = False)
    	return r

'''
filter some result:
such as,if we find x.x.x.x/etc/passwd,the response should contain string "root:......................./bin/bash",so we can fiter "root" string to identify "/etc/passwd" file
return value:
0   must not be the one
1   not sure,should be checked munually
2   must be the one
'''
def fuzz_filter(filename,r):
    #notice "etc/passwd" should not be "/etc/passwd",otherwise will die
    #"php version",can not be "PHP Version"
    #support ! to exclude,and the string should not contanin "!"
    t=[("etc/passwd","root"),("win.ini","[files]"),(".bashrc","alias"),("web.xml","<servlet>"),("p.php","php version"),("phpinfo.php","php version"),("zip","!text/html"),("tar.gz","!text/html"),("rar","!text/html"),("jmx-console","jboss"),("web-console","serverinfo.jsp"),("invoker/","jboss"),("svn/entries","svn"),("git/config","git"),("manage/html","tomcat")]
    flag=1
    if r.status_code!=200:
        return 0
    for tt in t:
        if tt[1].startswith("!"):
		tt[1]=tt[1].strip("!")
		if filename.find(tt[0])!=-1 and r.text.lower().find(tt[1])==-1 and str(r.headers).find(tt[1])==-1:
			flag=2
			break
		if filename.find(tt[0])!=-1 and (r.text.lower().find(tt[1])!=-1 or str(r.headers).find(tt[1])!=-1):
			flag=0
			break
	else:
		if filename.find(tt[0])!=-1 and r.text.lower().find(tt[1])==-1 and str(r.headers).find(tt[1])==-1:
			flag=0
			break
		if filename.find(tt[0])!=-1 and (r.text.lower().find(tt[1])!=-1 or str(r.headers).find(tt[1])!=-1):
			flag=2
			break
    return flag
'''

'''
def do_job(args):
    #time.sleep(0.1)
    #print threading.current_thread(), list(args)
    for file in files:
	if not hosts[args[0]].startswith("http:"):
		hosts[args[0]]="http://"+hosts[args[0]]
	uri=hosts[args[0]].strip("\r").strip("\n")+"/"+file.strip("\r").strip("\n")
    	r=fuzz_response(hosts[args[0]].strip("\r").strip("\n"),file.strip("\r").strip("\n")
)
	flag=fuzz_filter(file.strip("\r").strip("\n"),r)
	if flag!=0:
	   http_to_database(hosts[args[0]].strip("\r").strip("\n")+"/"+file.strip("\r").strip("\n")
,r,flag)
	   print hosts[args[0]].strip("\r").strip("\n")+"/"+file.strip("\r").strip("\n")

if __name__ == '__main__':
    start = time.time()
    work_manager =  WorkManager(len(hosts), 1000)
    work_manager.wait_allcomplete()
    end = time.time()
    print "cost all time: %s" % (end-start)
