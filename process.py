#!/usr/bin/python
#coding: utf8
flds=[
"DEBTR_INN",
"DEBTR_NAME",
'NUM_ID',
'DATE_ID',
'SUM_ALL',
'NUM_SV',
'OSP'
]
fldstype={
"DEBTR_INN":"intstr",
"DEBTR_NAME":"str",
'NUM_ID':'intstr',
'DATE_ID':'date',
'SUM_ALL':'float',
'NUM_SV':'str',
'OSP':'str'
}
xlsflds={u"инн":"DEBTR_INN",
u"плательщик":"DEBTR_NAME",
u"номер документа":"NUM_ID",
u"дата документа":"DATE_ID",
u"сумма по документу":"SUM_ALL",
u"лицо (адресат)":"OSP",
u"13. номер постановления по 47ст.":"NUM_ID",
u"14. дата постановления по 47ст.":"DATE_ID",
u"наименование плательщика ":"DEBTR_NAME",
u"номер постановления":"NUM_ID",
u"дата постановления":"DATE_ID",
u"сумма":"SUM_ALL",
u"лицо адресат":"OSP",
}
#xlrd const cell type
#xlrd.XL_CELL_BLANK    xlrd.XL_CELL_DATE     xlrd.XL_CELL_ERROR    xlrd.XL_CELL_TEXT     
#xlrd.XL_CELL_BOOLEAN  xlrd.XL_CELL_EMPTY    xlrd.XL_CELL_NUMBER
#xlrd.xldate_as_tuple(d,wb.datemode)
#
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
def conv (val,vtype,xltype,wb):
 rez=''
 #print a,type(a),vtype
 if vtype=='intstr':
  try:
   #print int(val)
   rez=str(int(val))
  except:
   rez=None
 elif vtype=='str':
  if str (type(val))=="<type 'unicode'>" or str(type(val))=="<type 'str'>":
   rez=val
  else:
   try:
    rez=str(val)
   except:
    rez=None
 elif vtype=='float':
  if str (type(val))=="<type 'float'>":
   rez=val
  else:
   try:
    rez=float(val)
   except:
    rez=None
 elif vtype=='date':
  #print "date", val,type(val),xltype
  if xltype==xlrd.XL_CELL_DATE:   #str(type(val))=="<type 'datetime.datetime'>" or  str(type(val))=="<type 'float'>" :
   year, month, day, hour, minute, second =xlrd.xldate_as_tuple(val,wb.datemode)
   rez=datetime(year, month, day, hour, minute, 0)
  elif str(type(val))=="<type 'str'>" or  str (type(val))=="<type 'unicode'>":
   if len (val)>0:
    rez=datetime.strptime(val,'%d.%m.%Y')
   else:
    rez=None
 return rez
def getgenerator(cur,gen):
 sq="SELECT GEN_ID("+gen+", 1) FROM RDB$DATABASE"
 try:
  cur.execute(sq)
 except:
  #print "err"
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
 nd=xmlroot.find('input_err_path')
 input_err_path=nd.text

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
 fileconfig.close()
 st=''
 print input_path
 if sys.argv[1]=='upload':
  try:
   con = fdb.connect (host=main_host, database=main_dbname, user=main_user, password=main_password,charset='WIN1251')
  except  Exception, e:
   print("Ошибка при открытии базы данных:\n"+str(e))
   sys.exit(2)
  cur=con.cursor()
  fff=listdir(input_path)
  st=u'Загружаем файлы для сверки. Найдено '+unicode( len (fff) )
  inform(st)
  for ff in listdir(input_path):
   #print ff
   #открыть файл
   st=u'Загружаем файл: '+unicode(ff)
   inform(st)
   #Проверяем был ли загружен файл.
   sq='select count(pk) from fromfns    where fromfns.filename='+quoted(ff)
   cur.execute(sq)
   r=cur.fetchall()
   cnt= r[0][0]
   if cnt==0:
    wb=xlrd.book.open_workbook_xls(input_path+ff)
    ws=wb.sheet_by_index(0)
    m={}
    #st=u'Найдено '+unicode( ws.row_len(0) ) +u' строк.'
    #inform(st)
    for i in range(0,ws.row_len(0)):
     t=ws.cell_value(0,i)
     t.lstrip(' ').rstrip(' ')
     t2=t.lower()
     if (t2 in xlsflds.keys()):
      m[ xlsflds[t2] ]=i
    #print m
   
       #INSERT INTO FROMFNS (PK, DEBTR_INN, DEBTR_NAME, NUM_ID, DATE_ID, SUM_ALL, NUM_SV, OSP, FILENAME) VALUES (NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
    sql="INSERT INTO FROMFNS (PK, DEBTR_INN, DEBTR_NAME, NUM_ID, DATE_ID, SUM_ALL, NUM_SV, OSP, FILENAME) VALUES (?,?,?,?,?,?,?,?,?)" 
    st=u'Найдено '+unicode( ws.nrows ) +u' строк.'
    inform(st)
    for i in range(2,ws.nrows):
     t=[]
     t2=[] 
     #print "FF",i
     for mm in flds:
      #print "Поле",mm,i
      if mm in m.keys():
       #print "!",'ПОле',mm,m[mm]
       #"тип m[mm],type(mm),type(m[mm])
       s=ws.cell_value(i,m[mm])
       xltype=ws.cell_type(i,m[mm])
       #print mm,xltype,s
       s2=conv(s,fldstype[mm],xltype,wb)
       if mm=='DEBTR_INN':
        #print 'INN'
        if s2 <> None:
       	 if len(s2) in (9,11):
          s2='0'+s2
       #print  mm, s,s2
       #print type(s),str(s),fldstype[mm],conv(s,fldstype[mm])
       t.append(s2)
      else:
       t.append(None)
      #print t
     id=getgenerator(cur,"PK_FNS")
     t.append(ff)
     t2=[id] 
     t2.extend(t)
     #print t
     #print t2,len(t2)
     #for tt in t2:
     #print t2,i
     try:
      cur.execute (sql,t2)
     except:
      st=u'Ошибка в скрипте' 
      inform (st)
      st=unicode(sql)
      inform (st)
      st=unicode(t2)
      inform (st)
      #sys.exit(2)
    con.commit()
    sq=''
    rename(input_path+ff, input_arc_path+ff)
   else:
    st=u'Файл ' +unicode(ff)+u' уже загружался раньше, пропускаю.'
    inform(st)
    rename(input_path+ff, input_err_path+ff)
  st=u'=======  РАБОТА ЗАКОНЧЕНА  ================================================'
  inform(st)
  con.close()
 if sys.argv[1]=='loadrbd':
  try:
   con = fdb.connect (host=main_host, database=main_dbname, user=main_user, password=main_password,charset='WIN1251')
  except  Exception, e:
   print("Ошибка при открытии базы данных:\n"+str(e))
   sys.exit(2)
  try:
   con2 = fdb.connect (host=rbd_host, database=rbd_dbname, user=rbd_user,  password=rbd_password,charset='WIN1251')
  except  Exception, e:
   print("Ошибка при открытии базы данных:\n"+str(e))
   sys.exit(2)
  cur = con.cursor()  
if __name__ == "__main__":
    main()
