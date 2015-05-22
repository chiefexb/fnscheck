#!/usr/bin/python
#coding: utf8
from lxml import etree
import sys
from os import *
import fdb
import logging
import datetime
import timeit
import time
from odsmod import *
def getgenerator(cur,gen):
 sq="SELECT GEN_ID("+gen+", 1) FROM RDB$DATABASE"
 try:
  cur.execute(sq)
 except:
  print "err"
  g=-1
 else:
  r=cur.fetchall()
  g=r[0][0]
 return g
def inform(st):
 logging.info(st)
 print st
 return
class Profiler(object):
    def __enter__(self):
        self._startTime = time.time()

    def __exit__(self, type, value, traceback):
        #print "Elapsed time:",time.time() - self._startTime # {:.3f} sec".form$
        st=u"Время выполнения:"+str(time.time() - self._startTime) # {:.3f} sec$
        print st
        logging.info(st)
def quoted(a):
 st=u"'"+a+u"'"
 return st
def main():
 st=''
if __name__ == "__main__":
    main()
