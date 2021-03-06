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
from sverka import *
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
def inform(st, mestype):
 if mestype=='info':
  logging.info(st)
 if mestype=='error':
  logging.error(st)
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
#def inform(st,'info'):
# logging.info(st)
# print st
# return
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
 fileconfig2=file('./sverka.xml')

 xml2=etree.parse(fileconfig2)
 xmlroot2=xml2.getroot()
 
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

 rbd_database=xmlroot.find('rbd')
 rbd_dbname=rbd_database.find('dbname').text
 rbd_user=rbd_database.find('user').text
 rbd_password=rbd_database.find('password').text
 rbd_host=rbd_database.find('hostname').text
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
  inform(st,'info')
  for ff in listdir(input_path):
   #print ff
   #открыть файл
   st=u'Загружаем файл: '+unicode(ff)
   inform(st,'info')
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
    inform(st,'info')
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
      inform (st,'info')
      st=unicode(sql)
      inform (st,'info')
      st=unicode(t2)
      inform (st,'info')
      #sys.exit(2)
    con.commit()
    sq=''
    rename(input_path+ff, input_arc_path+ff)
   else:
    st=u'Файл ' +unicode(ff)+u' уже загружался раньше, пропускаю.'
    inform(st,'info')
    rename(input_path+ff, input_err_path+ff)
  st=u'=======  РАБОТА ЗАКОНЧЕНА  ================================================'
  inform(st,'info')
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
  cur2=con2.cursor()
  sql="SELECT  doc_ip_doc.id ,doc_ip_doc.id_docno,doc_ip_doc.id_docdate,document.doc_number ,doc_ip.ip_risedate,doc_ip.ip_date_finish, doc_ip_doc.id_dbtr_name,doc_ip.id_debtsum, document.docstatusid,doc_ip.ip_exec_prist_name,doc_ip_doc.id_crdr_name,doc_ip.article,doc_ip.point,doc_ip.subpoint FROM DOC_IP_DOC DOC_IP_DOC JOIN DOC_IP ON DOC_IP_DOC.ID=DOC_IP.ID JOIN DOCUMENT ON DOC_IP.ID=DOCUMENT.ID  where document.docstatusid not in (-1,5,27,28) and  (CAST (doc_ip_doc.id_crdr_entid as varchar(10))) starting with '1' and doc_ip_doc.id_crdr_entid <>1695"
  sql2="INSERT INTO DOCIPDOC (ID, ID_DOCNO, ID_DOCDATE, DOC_NUMBER, IP_RISE_DATR, IP_DATE_FINISH, ID_DBTR_NAME, ID_DEBTSUM, DOCSTATUSID, IP_EXEC_PRIST_NAME, ID_CRDR_NAME, ARTICLE, POINT, SUBPOINT) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
  with Profiler() as p:
   cur2.execute(sql)
   try:
    r=cur2.fetchall()
   except:
    print sql
    sys.exit(2)
   for rr in r:
    try:
     cur.execute( sql2,rr)
    except Exception, e:
     print("Ошибка при открытии базы данных:\n"+str(e))
     print sql2
     for rrr in rr:
      print rrr
     sys.exit(2)
   con.commit()
 if sys.argv[1]=='loadold': 
  st=u'Загружаем старые базы '
  inform(st,'info')
  try:
   con = fdb.connect (host=main_host, database=main_dbname, user=main_user, password=main_password,charset='WIN1251')
  except  Exception, e:
   print("Ошибка при открытии базы данных:\n"+str(e))
   sys.exit(2)
  cur=con.cursor()
  #print 'loadOld'
  years= ['d2007','d2008','d2009','d2011']
  dbm=[] 
  for d  in xmlroot2.getchildren():
   if d.tag in years:
    for a in d.getchildren():
     print a.tag, a.text
     dbs={}
     dbs['year']=d.tag
     dbs['alias']=a.tag
     for itms in a.attrib.items():
      dbs[itms[0]]=itms[1]
     dbm.append(dbs)
  print 'DBM ',len(dbm)
  #print dbm[0]
  sql="select     ip.num_ip ,ip.date_ip_in,ip.date_ip_out,ip.num_id,ip.date_id_send,ip.name_d ,name_v,adr_d,adr_v,innd,name_id,name_org_id,why,sum_,sum_is,ip.nump26,num_pp,ip.reason_out,ip.text_pp ,fio_spi,date_spi_take,total_sum ,main_dolg ,fakt_sum_is,pk,fk from ip  where ip.num_ip not containing 'СД' and ip.num_ip not containing 'СВ'"
  sql2='select sd,p_address from s_subdividings'
  sql3='INSERT INTO OLD_IP (ID, NUM_IP, DATE_IP_IN, DATE_IP_OUT, NUM_ID, DATE_ID_SEND, NAME_D, NAME_V, ADR_D, ADR_V, INND, NAME_ID, NAME_ORG_ID, WHY, SUM_, SUM_IS, NUMP26, NUM_PP, REASON_OUT, TEXT_PP, FIO_SPI, DATE_SPI_TAKE, TOTAL_SUM, MAIN_DOLG, FAKT_SUM_IS, PK, FK, NAME_DB, SUBDIV, YEAR_) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
  sql4='ALTER SEQUENCE OLDIP_ID RESTART WITH 1'
  sql5='delete from OLD_IP'
  #ставим
  
  print "DBM",  len (dbm),dbm
  with Profiler() as p:
   for dd in dbm:
    #with Profiler() as p:
     r=crowl1(dd,sql)
     name_db=dd['db']
     subdiv=getreq(dd,sql2)[0]
     year=(dd['year']).replace('d','')
     st=u'Загружаем старые базы '+unicode(subdiv)+'; '+unicode(name_db)+'; '+unicode(year)+'; '+unicode(len(r))+u' записей.'
     inform(st,'info')
     for rr in r: 
      #print len(r)
      #print rr
      #расширяем строку и вставляем в БД
      id=getgenerator(cur,'oldip_id')
      #print "YEAR",year,'SUB',subdiv
      #print type( id)
      pp=[]
      pp.append(id)
      #print pp
      pp.extend(rr)
      pp.extend([name_db,subdiv,year])
      try:
       cur.execute(sql3,pp)
      except Exception, e:
       st=u'Ошибка при выполении запроса'+unicode(name_db)+';'+sql3+unicode(e)
       inform(st,'error') 
       inform(unicode(pp),'error')
       sys.exit(2)
      
     con.commit()
  con.close()
  #print pp
 if sys.argv[1]=='process':
  try:
    con = fdb.connect (host=main_host, database=main_dbname, user=main_user, password=main_password,charset='WIN1251')
  except  Exception, e:
   print("Ошибка при открытии базы данных:\n"+str(e))
   sys.exit(2)
  cur=con.cursor()
  sql="select  docipdoc.id from fromfns f1   join  docipdoc on ( (docipdoc.id_docno=f1.num_id  ) and ( docipdoc.id_docdate=f1.date_id) and      ( docipdoc.id_debtsum = f1.sum_all)  ) group by docipdoc.id"
  sql2="select  first 1 * from fromfns f1   join  docipdoc on ( (docipdoc.id_docno=f1.num_id  ) and ( docipdoc.id_docdate=f1.date_id) and      ( docipdoc.id_debtsum = f1.sum_all)  ) where id="
  cur.execute(sql)
  rec=cur.fetchall()
  rec2=[]
  i=0
  #rt='('
  #for rr in rec :
  # i=i+1
  # print i
  #  cur.execute(sql2+str(rr[0]))
  # rt=rt+str(rr[0]
 #  rec2.append(rt)

  print len (rec), len (rec2)
  print rec[1]
if __name__ == "__main__":
    main()
