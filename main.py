#!/usr/local/python2.7/bin/python
#encoding=UTF-8

import MySQLdb
import gl
import re
import os
import json
import sys
from docxml import Docxml
from subprocess import call

print sys.getdefaultencoding()
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
sql = '''SELECT o.id,question_docx,question_type,s.fullname,o.grade_id,o.parent_question_id
         FROM entity_question_old as o
         Left join entity_question_new_f as n
         on o.id=n.oldid
         LEFT JOIN entity_subject as s
         on o.subject_id=s.id
         where question_type='%(s)s' 
           and parent_question_id = 0 and n.detail='22' and is_single=1 and n.id is not null
           and question_docx is not null and state='ENABLED' ''' % dict(s=gl.q_type)
#and n.answer_num=1 and answer!='A' and answer!='B' and answer!='C' and answer!='D'
#           and n.detail ='7'
#         where question_type='%(s)s' 
#           and o.id in (%(i)s) 
#           and n.oldid is null 
#           and question_docx is not null and state='ENABLED' ''' % dict(s=gl.q_type,i=idlist)
#           and n.oldid is null and question_docx is not null and is_single=1 and subject_id in (1,2,5,6,9,10,11,12,13,14,15,16,17,18,19,21) and state='ENABLED' ''' % dict(s=gl.q_type)
print sql

cursor.execute(sql)
results = cursor.fetchall()
for row in results:
	###全局变量初始化 start
	gl.question.clear()
	if gl.q_type=="写作题" or gl.q_type=="书面表达":
		gl.question={'tag':'','interpret':[],'model_essay':[],'answer':[],'analysis':[]}
	else:
		gl.question={'tag':'','body':[],'options':[],'answer':[],'analysis':[]}
	gl.answer_sub={'index':0,'group':[]}
	gl.sub_status = 0
	gl.type_status = ""
	gl.option_stat = ""
	gl.blank_num = 0
	###全局变量初始化 end
	num = row[0]
	gl.oldid = num
	print "num: " + str(num)
	docfile = row[1]
	#qtype = row[2]
	qtype = gl.q_type_l
	suject = row[3]
	grade = row[4]
	parent_question_id = row[5]
	#if parent_question_id:
	#	gl.excep=15
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

	###异常flg初始化
	print file_o
	gl.excep=0
	docx = Docxml(file_o, '','')
	if gl.excep!=0:
		print "###gl.excep1: " + str(gl.excep)
		sql = '''insert into entity_question_new_f(oldid,detail) 
                    values('%(n)d','%(t)s')
                    on duplicate key update detail= '%(t)s' ''' % dict(n=num, t=str(gl.excep))
		cursor.execute(sql)
		db.commit()
		continue
	docx.parse()
	if gl.excep!=0:
		print "###gl.excep2: " + str(gl.excep)
		retn=call(cmd,shell=True)
		sql = '''insert into entity_question_new_f(oldid,detail) 
                    values('%(n)d','%(t)s')
                    on duplicate key update detail= '%(t)s' ''' % dict(n=num, t=str(gl.excep))
		cursor.execute(sql)
		db.commit()
		continue

	docx.subject(gl.q_type)
	if gl.excep!=0:
		print "###gl.excep3: " + str(gl.excep)
		sql = '''insert into entity_question_new_f(oldid,detail) 
                    values('%(n)d','%(t)s')
                    on duplicate key update detail= '%(t)s' ''' % dict(n=num, t=str(gl.excep))
		cursor.execute(sql)
		db.commit()
		continue

	if gl.q_type == "填空题" or gl.q_type == "词汇运用" or gl.q_type == "句型转换" or gl.q_type == "填空型完形填空" or gl.q_type == "填空型阅读理解":
		#print json.dumps(gl.question['answer'], ensure_ascii=0)
		index=0
		tmp_ans=[]
		tmp_ans_group=[]
		for elem in gl.question['answer']:
			if elem['type']=="text":
				count=0
				for arr in re.split('#####',elem['value']):	
					if count:	
						index+=1
						tmp_ans.append({'index':index,'group':tmp_ans_group})
						tmp_ans_group=[]
						count=0
					if arr:	
						tmp_ans_group.append({"style": elem['style'], "align": elem['style'], "value": arr, "font": "", "type": "text", "size": ""})
					count=1
			elif elem['type']=="newline":
				if tmp_ans_group:
					index+=1
					tmp_ans.append({'index':index,'group':tmp_ans_group})
					tmp_ans_group=[]
			else:
				tmp_ans_group.append(elem)
		gl.question['answer']=tmp_ans
		print "###blank "+ str(gl.b_num)
		print "###answer "+ str(index)+": " + json.dumps(gl.question['answer'], ensure_ascii=0)
		
	if gl.b_num!=index:
		gl.excep=22
		print "###gl.excep22: " + str(gl.excep)
		sql = '''insert into entity_question_new_f(oldid,detail) 
                    values('%(n)d','%(t)s')
                    on duplicate key update detail= '%(t)s' ''' % dict(n=num, t=str(gl.excep))
		cursor.execute(sql)
		db.commit()
		continue

	try:
		js=json.dumps(gl.question, ensure_ascii=0)
		js=db.escape_string(js)
		sql = '''insert into entity_question_new_f(oldid,type,json,subject,grade_id,answer_num) 
                         values('%(n)d','%(t)s','%(j)s','%(s)s','%(g)d','%(an)d')
                         on duplicate key update type= '%(t)s' , json='%(j)s' , subject='%(s)s' , 
                         grade_id='%(g)d' , detail = null , answer_num='%(an)d' ''' % dict(n=num, t=qtype, j=js, s=suject, g=grade, an=gl.b_num)
		cursor.execute(sql)
		db.commit()
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
