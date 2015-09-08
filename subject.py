#! *-* coding:utf-8 *-*

import gl
import re

import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )


class Subject(object):
	
	def __init__(self,rulefile):
		self.rulefile = rulefile
		self._get_rule(rulefile)


	def _get_rule(self,rulefile):
		for line in open(rulefile):
			if re.match(r'###', line):
				continue

			p = re.compile('\s+')
			list = re.sub(p,"",line).split(":", 4)
			rule = {'type': list[0], 'in': list[1], 'relate': list[2], 'format': list[3]}
			gl.rulelist.append(rule)	


	def parse(self,val,pnum,bnum):

		if re.compile('^[\s]*\001$').match(val):
			return
		elif val == '\005\001':
			gl.type_status = ""
			gl.sub_status = 0
			#print "=================================="
			return
		elif gl.sub_status == 0 and gl.type_status != "" :
			gl.sub_status = 1

		for rule in gl.rulelist:
			regexp = r'' + rule['format'].decode('utf-8')
			p = re.compile(regexp)
			if p.match(val) and gl.sub_status == int(rule['in']):
				if gl.type_status == "":
					gl.type_status = rule['type']
				if (rule['relate'] and gl.type_status == rule['relate'] ) or (rule['relate'] == ""):
					gl.type_status = rule['type']
					break
		return val


class Subject_complex(object):


	def parse(self,val,pnum,bnum):

		#print "before : " + gl.main_type_status + " : " + gl.q_type + " : " + gl.type_status + " : " + val
		val = val.replace(b'\xc2\xa0',' ') #去除utf8特殊空格
		val = val.replace(b'\xe3\x80\x80',' ')
		val = val.replace('\004\004','') #去除多余下划线标记
		val = val.replace('\007\007','') #去除多余斜体标记
		val = val.replace('\016\016','') #去除多余着重点标记
		val = val.replace('\012\012','') #去除多余居中符
		val = val.replace('\013\013','') #去除多余居右符
		val = val.replace('\032\032','') #去除多余方框
		if gl.main_type_status == "":
			gl.main_type_status = "type"
			return
		elif re.compile('^[\s]*\001$').match(val) and (gl.main_type_status != "questions" or gl.type_status == "type" or gl.type_status == ""):
			if (gl.main_q_type=="文言文阅读题" or gl.main_q_type=="选择型阅读理解") and gl.main_type_status == "material":
				gl.main_type_status = "translation"
			return
		elif gl.main_type_status == "type":
			gl.main_type_status = "material"
		elif val == '\005\001':
			if gl.main_type_status == "material" or gl.main_type_status == "translation":
				gl.main_type_status = "questions"
			elif gl.type_status:
				gl.type_status = ""
				gl.q_type = ""
				gl.blank_cnt = 0
				gl.content["questions"].append(gl.question)
				gl.question = {'topic_type':{},'body':[],'options':[],'answer':[],'analysis':[]}
			return
		#elif gl.main_type_status == "questions" and (gl.type_status=="" or gl.type_status=="type"):
		elif gl.main_type_status == "questions" and gl.type_status=="":
			tid = 0
			if re.match(r'选择题'.decode('utf8'),val):
				gl.q_type = "选择题"
				tid = 1
			elif re.match(r'填空题'.decode('utf8'),val):
				gl.q_type = "填空题"
				tid = 2
			elif re.match(r'简答题'.decode('utf8'),val):
				gl.q_type = "简答题"
				tid = 4
			elif re.match(r'判断题'.decode('utf8'),val):
				gl.q_type = "判断题"
				tid = 3
			else:
				gl.excep = 16
				#print ""
			if tid:
				gl.question["topic_type"] = {"id":tid, "name":gl.q_type}
			else:
				gl.question["topic_type"] = {"id":tid, "name":"未定义"}
			gl.type_status = "type"
			return

		elif gl.type_status:
			if gl.q_type == "选择题":
				val = self._parse_blank(val,pnum,bnum)
			else:
				val = self._parse_panduan(val,pnum,bnum)

		if val:
			print "after : " + gl.main_type_status + " : " + gl.q_type + " : " + gl.type_status + " : " + val
			val = val.replace('\005','')
			val = val.replace("'","''")
			return val
		else:
			return


	def _parse_blank(self,val,pnum,bnum):

		#print "before:" + gl.type_status + " : " + val
		flg = 0 ###类型变化flg 用来增加空行的
		if gl.type_status == "":
			gl.type_status = "type"
			return
		elif gl.type_status == "" and gl.sub_status==1:
			gl.excep=5
			gl.type_status = "type"
			return
		elif re.match(r'^[\s　]*\001$'.decode('utf8'),val) or (val == '\005\001' and gl.type_status != "analysis" and gl.type_status != ""):
			gl.blank_num += 1
			return
		elif gl.type_status == "type":
			gl.sub_status=1
			gl.type_status = "body"
			gl.blank_num = 0
		elif gl.blank_num > 0 and gl.type_status != "analysis":
			if gl.type_status == "body":
				(val, tag) = self.option_ana(val)
				if tag == 1:
					gl.type_status = "options"
					#unit = {"type":"newline","value":"1"}
					#gl.question["body"].append(unit)
					flg = 1
			elif gl.type_status == "options":
				gl.type_status = "answer"
				flg = 1
				gl.option_stat = ""
			elif gl.type_status == "answer":
				gl.type_status = "analysis"
				flg = 1
			gl.blank_num = 0
		elif val == '\005\001' and gl.type_status == "analysis":
			gl.type_status = ""
			gl.blank_num = 0
			#print "=================================="
			return 
		elif gl.type_status == "options":
			(val, tag) = self.option_ana(val)

		if flg == 1:
			gl.type_change = 1
		else:
			gl.type_change = 0
		#print "after : " + gl.type_status + " : " + val
		return val


	def option_ana(self,val):

		p = re.match(r'([a-gA-G])[\.．、]*(.*)'.decode('utf8'), val)
		if p:
			gl.option_stat = p.group(1)
			return (p.group(2), 1)
		else:
			return (val, 0)


	def _parse_panduan(self,val,pnum,bnum):

		#print "before: " + gl.type_status + " : "+ val
		flg = 0 ###类型变化flg 用来增加空行的
		if gl.type_status == "":
			gl.type_status = "type"
			return
		elif gl.type_status == "" and gl.sub_status==1:
			gl.excep=5
			gl.type_status = "type"
			return
		elif re.compile('^[\s]*\001$').match(val) or (val == '\005\001' and gl.type_status != "analysis" and gl.type_status != ""):
			gl.blank_num += 1
			return
		elif gl.type_status == "type":
			gl.type_status = "body"
			gl.blank_num = 0
			gl.sub_status = 1
		elif gl.blank_num > 0 and gl.type_status != "analysis":
			if gl.type_status == "body":
				gl.type_status = "answer"
				flg = 1
			elif gl.type_status == "answer":
				gl.type_status = "analysis"
				flg = 1
			gl.blank_num = 0
		elif val == '\005\001' and gl.type_status == "analysis":
			gl.type_status = ""
			gl.blank_num = 0
			#print "=================================="
			return

		if flg == 1:
			gl.type_change = 1
		else:
			gl.type_change = 0
		#print "after : " + gl.type_status + " : "+ val
		return val
