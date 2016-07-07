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
class Profiler(object):
    def __enter__(self):
        self._startTime = time.time()

    def __exit__(self, type, value, traceback):
        #print "Elapsed time:",time.time() - self._startTime # {:.3f} sec".form$
        st=u"Время выполнения:"+str(time.time() - self._startTime) # {:.3f} sec$
        print st
        logging.info(st)
def preprocess (sql):
 s=sql.replace('%not_equal','<>')
 return s
def quoted(a):
 try:
  st=u"'"+a+u"'"
 except:
  st='Null'
 return st
def crowl1(pp,sql):
 try:
  con = fdb.connect (host=pp['host'], database=pp['db'], user='SYSDBA', password=pp['password'],charset='WIN1251')
 except  Exception, e:
  print pp['host'],pp['db'],pp['password'],'FAIL',e
 else:
  cur=con.cursor()
  print sql
  cur.execute (sql)
  r=cur.fetchall()
 return r
def crowl(dbm,sql):
 rez=[]
 i=0
 for pp in dbm:
  i+=1
  print i,pp['year'],pp['alias'],pp['db'],len (dbm)
  try:
   con = fdb.connect (host=pp['host'], database=pp['db'], user='SYSDBA', password=pp['password'],charset='WIN1251')
  except  Exception, e:
   print pp['host'],pp['db'],pp['password'],'FAIL',e
  else:
   cur=con.cursor()
   print sql
   if sql=='test':
    print  i,pp['host'],pp['db'],'OK'
   else:
    cur.execute (sql)
    r=cur.fetchall()
    #print  i,pp['host'],pp['db'],'OK'
    rez.append(r)
   con.close()
 return rez
def main():
 logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s',level = logging.DEBUG, filename = './logging.log')
 fileconfig=file('./sverka.xml')
 xml=etree.parse(fileconfig) 
 xmlroot=xml.getroot()
 print xmlroot.tag
 #conf=xmlroot.find('config')
 #dbmass={}
 dbs={}
 dbm=[]
 #выбираем годы
 if len(sys.argv)<=1:
  print ("getfromint: нехватает параметров\nИспользование: sverka.py sverka d2007,d2008")
  print "sverka.py sverka all по всем годам"
  sys.exit(2)
 print sys.argv[2],sys.argv[3]
 try:
  filefilter=file(sys.argv[3])
 except:
  sys.exit(2)
  print 'файл фильтра не найден'
 dbm=[]
 if sys.argv[2]=='all':
  years=['d2007','d2008','d2009','d2010','d2011']
 else:
  years=sys.argv[2].split(',')
 print years
 for d  in xmlroot.getchildren():
  print d.tag
  #выбираем базы за год
  if d.tag in years:
   #dbs['year']=d.tag
   print len(d.getchildren())
   for a in d.getchildren():
    print a.tag
    #перебор атрибутов
    dbs={}
    dbs['year']=d.tag
    dbs['alias']=a.tag
    for itms in a.attrib.items():
     dbs[itms[0]]=itms[1]
    dbm.append(dbs)
 print dbm,len(dbm)
 print 'TEST CONN'
 crowl(dbm,'test')
 fltxml=etree.parse(filefilter)
 fltroot=fltxml.getroot()
 print fltroot.tag
 grids=fltroot.find('grids')
 header=grids.find('header')
 body=grids.find('body')
 for pp in dbm:
  d=datetime.now().strftime('%d.%m.%y')
  df=datetime.now().strftime('%Y_%m_%d')
  fn2=pp['year']+'_'+pp['alias']+'_'+df+'.ods'
  textdoc=initdoc()
  table,tablecontents,textdoc=inittable(textdoc)
  for ch in header:
   if ch.tag=='text':
    print ch.text 
    table=addrow( ('',ch.text),table,tablecontents)
   elif ch.tag=='sql':
    sql=ch.text
    if 'text' in ch.attrib.keys():
     text=ch.attrib['text']
    else:
     text=''
    r=crowl1(pp,sql)
    table=addrow( (text,r[0][0]),table,tablecontents)
    #print len(r)
   
  for ch in body:
   if ch.tag=='sql':
    sql=preprocess(ch.text)
    r=crowl1(pp,sql)
    for rr in r:
     print len(rr)
     try:
      table=addrow(rr,table,tablecontents)
     except:
      print rr
  savetable(table,textdoc,'/home/all/1'+'/'+fn2)
if __name__ == "__main__":
    main()

