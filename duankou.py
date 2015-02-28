#!/usr/bin/env python
# name IsOpen.py

import os
import socket
socket.setdefaulttimeout(1)
def readfile(filename):
    return open(filename).readlines()
def IsOpen(ip,port):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        s.connect((ip,int(port)))
        s.shutdown(2)
        #print '%d is open' % port
        return True
    except:
        #print '%d is down' % port
        return False
def main():
    for yuming in readfile("yuming.txt"):
	yuming=yuming.strip()
	for port in (80,443,8080):
		if IsOpen(yuming,port)==True:
			print "%s:%d"%(yuming,port)
if __name__ == '__main__':
    main()

