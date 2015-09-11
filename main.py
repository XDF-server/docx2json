#!/usr/local/python2.7/bin/python
#encoding=UTF-8

import MySQLdb
import gl
import os
import json
import sys
from docxml import Docxml
from subprocess import call

host="10.60.0.151"
user="root"
passw="1a2s3dqwe"
dbase="test"
db = MySQLdb.connect(host,user,passw,dbase,charset="utf8" )

cursor = db.cursor()
#sql = '''SELECT o.id,question_docx,question_type,s.fullname,o.grade_id
#         FROM entity_question_old as o
#         LEFT JOIN entity_subject as s
#         on o.subject_id=s.id
#         where o.id='996599' and question_type='%(s)s' and question_docx is not null and state='1' ''' % dict(s=gl.q_type)

#files=open(sys.argv[1],'r')
#idlist=files.readline().strip()
#files.close()
sql = '''SELECT o.id,question_docx,question_type,s.fullname,o.grade_id
         FROM entity_question_old as o
         Left join entity_question_new_f as n
         on o.id=n.oldid
         LEFT JOIN entity_subject as s
         on o.subject_id=s.id
         where question_type='%(s)s' 
           and o.parent_question_id = 0
           and n.oldid is null
           and question_docx is not null and state='ENABLED' ''' % dict(s=gl.main_q_type)
#           and n.oldid is null
#           and question_docx is not null and state='ENABLED' ''' % dict(s=gl.q_type,i=idlist)
#           and o.id in (%(i)s) 
#           and n.oldid is null and question_docx is not null and is_single=1 and subject_id in (1,2,19,5,6,21) and state='ENABLED' ''' % dict(s=gl.q_type)
#           and o.id = 21326
#           and o.id = 17701
#           and o.id = 24463 最后一种题型
#print sql

cursor.execute(sql)
results = cursor.fetchall()
for row in results:
	###全局变量初始化 start
	question={'topic_type':{},'body':[],'options':[],'answer':[],'analysis':[]}
	content={'material':[],'translation':[],'questions':[]}
	gl.sub_status = 0
	gl.type_status = ""
	gl.main_type_status = ""
	gl.type_change = ""
	gl.option_stat = ""
	gl.blank_num = 0
	gl.blank_cnt = 0
	gl.q_type=""
	###异常flg初始化
	gl.excep=0
	###全局变量初始化 end
	num = row[0]
	gl.oldid = num
	print "num: " + str(num)
	docfile = row[1]
	#qtype = row[2]
	qtype = gl.main_q_type
	suject = row[3]
	grade = row[4]
	if grade:
		#print "grade OK"
		grade=grade
	else:	
		grade = 0 
	#cmd = "wget -t 10 -T 20 -P /home/work/wzj/docx/ http://qd.okjiaoyu.cn/" + docfile
	docfile2 = ".ori.".join(docfile.split('.'))
	file_o = "/home/work/wzj/docx/" + docfile
	#retn=call(cmd,shell=True)
	if os.path.isfile(file_o) is False:
		#cmd = "wget -P /home/work/wzj/docx/ http://qd.okjiaoyu.cn/" + docfile2
		file_o = "/home/work/wzj/docx/" + docfile2
		#retn=call(cmd,shell=True)
		if os.path.isfile(file_o) is False:
			continue
	#print cmd

	docx = Docxml(file_o, '','')
	if gl.excep!=0:
		sql = '''insert into entity_question_new_f(oldid,detail) 
                    values('%(n)d','%(t)s')
                    on duplicate key update detail= '%(t)s' ''' % dict(n=num, t=str(gl.excep))
		cursor.execute(sql)
		db.commit()
		continue
	docx.parse()
	if gl.excep!=0:
		sql = '''insert into entity_question_new_f(oldid,detail) 
                    values('%(n)d','%(t)s')
                    on duplicate key update detail= '%(t)s' ''' % dict(n=num, t=str(gl.excep))
		cursor.execute(sql)
		db.commit()
		continue

	docx.subject(gl.main_q_type)
        if gl.excep!=0:
		sql = '''insert into entity_question_new_f(oldid,detail) 
                    values('%(n)d','%(t)s')
                    on duplicate key update detail= '%(t)s' ''' % dict(n=num, t=str(gl.excep))
		cursor.execute(sql)
		db.commit()
		continue

	if gl.question["topic_type"].has_key("id") and gl.question["topic_type"]["id"]:
		gl.content["questions"].append(gl.question)
	
	try:
		js=json.dumps(gl.content, ensure_ascii=0)
		sql = '''insert into entity_question_new_f(oldid,type,json,subject,grade_id) 
                         values('%(n)d','%(t)s','%(j)s','%(s)s','%(g)d')
                         on duplicate key update type= '%(t)s' , json='%(j)s' , subject='%(s)s' , 
                         grade_id='%(g)d' , detail = null ''' % dict(n=num, t=qtype, j=js, s=suject, g=grade)
		#print "###oldnum:" + str(num)
		#try:
		#print sql
		cursor.execute(sql)
		db.commit()
		#except:
		#	db.rollback()
		#	print "insert NG"
	except:
		gl.excep=9
		sql = '''insert into entity_question_new_f(oldid,detail) 
                    values('%(n)d','%(t)s')
                    on duplicate key update detail= '%(t)s' ''' % dict(n=num, t=str(gl.excep))
		cursor.execute(sql)
		db.commit()


db.close()

#docx = Docxml('/home/wzj/docx/test3.docx', '/home/wzj/docx2json/template','tag')
#docx = Docxml('/home/wzj/docx/AFD234asdfasdf.docx', '','')
#docx = Docxml('/home/work/wzj/docx/test4.docx', '','')

#print json.dumps(gl.question, ensure_ascii=0)
