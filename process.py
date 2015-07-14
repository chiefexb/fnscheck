#!/usr/bin/python
#coding: utf8
flds={
"DEBTR_INN":1,
"DEBTR_NAME":2,
'NUM_ID':3,
'DATE_ID':4,
'SUM_ALL':5,
'NUM_SV':6,
'OSP':7
}
xlsflds={u"инн":"DEBTR_INN",
u"плательщик":"DEBTR_NAME",
u"номер документа":"NUM_ID",
u"дата документа":"DATE_ID",
u"сумма по документу":"SUM_ALL",
u"лицо (адресат)":"OSP"
}
from lxml import etree
import sys
from os import *
import fdb
import logging
import datetime
import timeit
import time
import xlrd
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
def inform(st):
 logging.info(st)
 print st
 return
def main():
 #лог
 logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s',level = logging.DEBUG, filename = './process.log')
 print  len(sys.argv)
 if len(sys.argv) <2:
  print "Для запуска набери: ./process.py upload|loadrbd|process|get"
  print '	loadrbd - Загрузка новых данных из РБД и очистка таблицы от предыдущей версии'
  print '	process - Поиск соответвий реестров из ГИБДД с данными из РБД'
  print '	upload     - Загрузка файлов для проверки'
  print '	get     - Выгрузка реестров для загрузки в подразделениях'
  sys.exit(2)

 fileconfig=file('./config.xml')
 xml=etree.parse(fileconfig)
 xmlroot=xml.getroot()
 nd=xmlroot.find('input_path')
 input_path=nd.text

 nd=xmlroot.find('input_arc_path')
 input_arc_path=nd.text

 main_database=xmlroot.find('main_database')
 main_dbname=main_database.find('dbname').text
 main_user=main_database.find('user').text
 main_password=main_database.find('password').text
 main_host=main_database.find('hostname').text

# rbd_database=xmlroot.find('rbd')
# rbd_dbname=rbd_database.find('dbname').text
# rbd_user=rbd_database.find('user').text
# rbd_password=rbd_database.find('password').text
# rbd_host=rbd_database.find('hostname').text
 st=''
 print input_path
 if sys.argv[1]=='upload':
  for ff in listdir(input_path):
   print ff
   #открыть файл
   wb=xlrd.book.open_workbook_xls(input_path+ff)
   ws=wb.sheet_by_index(0)
   m={}
   for i in range(0,ws.row_len(0)):
    t=ws.cell_value(0,i)
    t.lstrip(' ').rstrip(' ')
    t2=t.lower()
    if (t2 in xlsflds.keys()):
     m[ xlsflds[t2] ]=i
   print m
if __name__ == "__main__":
    main()
