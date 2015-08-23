#!/usr/local/python2.7/bin/python
#encoding=UTF-8

import MySQLdb
import gl
import os
import json
from docxml import Docxml
from subprocess import call

host="10.60.0.151"
user="root"
passw="1a2s3dqwe"
dbase="test"
db = MySQLdb.connect(host,user,passw,dbase,charset="utf8" )

#subject_type="单项选择"
#subject_type="选择题"

#subject_type="判断题"

subject_type="简答题"
#subject_type="解答题"
#subject_type="填空题"

cursor = db.cursor()
#sql = '''SELECT o.id,question_docx,question_type,s.fullname,o.grade_id
#         FROM entity_question_old as o
#         LEFT JOIN entity_subject as s
#         on o.subject_id=s.id
#         where o.id='996599' and question_type='%(s)s' and question_docx is not null and state='1' ''' % dict(s=subject_type)

sql = '''SELECT o.id,question_docx,question_type,s.fullname,o.grade_id
         FROM entity_question_old as o
         Left join entity_question_new as n
         on o.id=n.oldid
         LEFT JOIN entity_subject as s
         on o.subject_id=s.id
         where question_type='%(s)s' 
           and o.id = 216379
           and question_docx is not null and state='1' ''' % dict(s=subject_type)
#         where n.oldid is null and question_type='%(s)s' and question_docx is not null and state='1' ''' % dict(s=subject_type)
#           and o.id != 139905

cursor.execute(sql)
results = cursor.fetchall()
for row in results:
	###全局变量初始化 start
	gl.question={'tag':'','body':[],'options':[],'answer':[],'analysis':[]}
	gl.sub_status = 0
	gl.type_status = ""
	gl.option_stat = ""
	gl.blank_num = 0
	###全局变量初始化 end
	num = row[0]
	print "num: " + str(num)
	docfile = row[1]
	qtype = row[2]
	suject = row[3]
	grade = row[4]
	if grade:
		print "grade OK"
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
	docx.parse()
	docx.subject(subject_type)
	
	sql = '''insert into entity_question_new(oldid,type,json,subject,grade_id) 
                 values('%(n)d','%(t)s','%(j)s','%(s)s','%(g)d')
                 on duplicate key update type= '%(t)s' , json='%(j)s' , subject='%(s)s' , 
                 grade_id='%(g)d' ''' % dict(n=num, t=qtype, j=json.dumps(gl.question, ensure_ascii=0), s=suject, g=grade)
	print "###oldnum:" + str(num)
	print sql
	#try:
	cursor.execute(sql)
	db.commit()
	#except:
	#	db.rollback()
	#	print "insert NG"

db.close()

#docx = Docxml('/home/wzj/docx/test3.docx', '/home/wzj/docx2json/template','tag')
#docx = Docxml('/home/wzj/docx/AFD234asdfasdf.docx', '','')
#docx = Docxml('/home/work/wzj/docx/test4.docx', '','')

#print json.dumps(gl.question, ensure_ascii=0)
