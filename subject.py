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


	def __init__(self):
		self.end_flg = 0 ###结束符flg,用于应对 \005content\001 这种格式
		self.old_status = ""

	def parse(self,val,pnum,bnum):

		print "before " + str(self.end_flg) + " : " + gl.main_type_status + " : " + gl.q_type + " : " + gl.type_status + " : " + val
		val = val.replace(b'\xc2\xa0',' ') #去除utf8特殊空格
		val = val.replace(b'\xe3\x80\x80',' ')
		val = val.replace('\004\004','') #去除多余下划线标记
		val = val.replace('\007\007','') #去除多余斜体标记
		val = val.replace('\016\016','') #去除多余着重点标记
		val = val.replace('\012\012','') #去除多余居中符
		val = val.replace('\013\013','') #去除多余居右符
		val = val.replace('\032\032','') #去除多余方框

		p = re.match('^\005(.+\001)$',val)
		### 格式判断开始
		if gl.main_type_status == "":
			gl.main_type_status = "type"
			return
		elif re.match('^[\s]*\001$',val):
			if gl.main_type_status == "type":
				self.old_status = gl.main_type_status
				gl.main_type_status = "material"
				return
			elif gl.main_type_status == "material":
				self.old_status = gl.main_type_status
				gl.main_type_status = "translation"
				return
			elif gl.main_type_status != "questions":
				return
			elif gl.main_type_status == "questions" and gl.type_status=="":
				return
		elif val == '\005\001':
			if gl.main_type_status == "material" or gl.main_type_status == "translation":
				self.old_status = gl.main_type_status
				gl.main_type_status = "questions"
				return
			elif gl.type_status:
				if gl.type_status == "analysis":
					gl.type_status = ""
					gl.q_type = ""
					gl.blank_cnt = 0
					gl.blank_num = 0
					gl.content["questions"].append(gl.question)
					gl.question = {'topic_type':{},'body':[],'options':[],'answer':[],'analysis':[]}
					return
				else:
					val = "\001"
			elif gl.main_type_status == "questions" and gl.type_status == "":
				return
		elif p:
			val = p.group(1)
			if gl.main_type_status == "material" or gl.main_type_status == "translation" or gl.main_type_status == "type":
				self.end_flg = 1
			elif gl.main_type_status == "questions":
				if gl.type_status:
					if gl.type_status == "analysis":
						self.end_flg = 1
				else:
					gl.main_type_status = self.old_status
					self.end_flg = 1
		elif self.end_flg:
			tid = 0
			if re.match('选择题'.decode('utf8'),val) or re.match('\014选择题'.decode('utf8'),val):
				gl.q_type = "选择题"
				tid = 1
			elif re.match('填空题'.decode('utf8'),val) or re.match('\014填空题'.decode('utf8'),val):
				gl.q_type = "填空题"
				tid = 2
			elif re.match('判断题'.decode('utf8'),val) or re.match('\014判断题'.decode('utf8'),val):
				gl.q_type = "判断题"
				tid = 3
			elif re.match('简答题'.decode('utf8'),val) or re.match('\014简答题'.decode('utf8'),val):
				gl.q_type = "简答题"
				tid = 4
			elif re.match('论述题'.decode('utf8'),val) or re.match('\014论述题'.decode('utf8'),val):
				gl.q_type = "论述题"
				tid = 5
			if tid:
				gl.blank_cnt = 0
				gl.blank_num = 0
				if gl.question["topic_type"].has_key("id") and gl.question["topic_type"]["id"]:
					gl.content["questions"].append(gl.question)

				gl.question = {'topic_type':{},'body':[],'options':[],'answer':[],'analysis':[]}
				gl.question["topic_type"] = {"id":tid, "name":gl.q_type}
				gl.type_status = "type"
				gl.main_type_status = "questions"
				self.end_flg = 0
				self.old_status = ""
				return
			
		elif gl.type_status=="" and gl.main_type_status == "questions":
			tid = 0
			gl.question["topic_type"] = {"id":tid, "name":"未定义"}
			if re.match('选择题'.decode('utf8'),val) or re.match('\014选择题'.decode('utf8'),val):
				gl.q_type = "选择题"
				tid = 1
			elif re.match('填空题'.decode('utf8'),val) or re.match('\014填空题'.decode('utf8'),val):
				gl.q_type = "填空题"
				tid = 2
			elif re.match('判断题'.decode('utf8'),val) or re.match('\014判断题'.decode('utf8'),val):
				gl.q_type = "判断题"
				tid = 3
			elif re.match('简答题'.decode('utf8'),val) or re.match('\014简答题'.decode('utf8'),val):
				gl.q_type = "简答题"
				tid = 4
			elif re.match('论述题'.decode('utf8'),val) or re.match('\014论述题'.decode('utf8'),val):
				gl.q_type = "论述题"
				tid = 5
			else:
				print "####route16"
				gl.excep = "16" + val
				return
			if tid:
				gl.question["topic_type"] = {"id":tid, "name":gl.q_type}
				gl.type_status = "type"
				return

		if gl.main_type_status == "type":
			self.old_status = gl.main_type_status
			gl.main_type_status == "material"
				
		if gl.type_status:
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
		if gl.type_status == "":
			gl.type_status = "type"
			return
		elif gl.type_status == "" and gl.sub_status==1:
			gl.excep=5
			gl.type_status = "type"
			return
		elif re.match('^[\s]*\001$'.decode('utf8'),val):
			gl.blank_num += 1
			return
		elif gl.type_status == "type":
			if gl.main_q_type == "选择型完形填空":
				(val, tag) = self.option_ana(val)
				if tag == 1:
					gl.type_status = "options"
			else:
				gl.sub_status=1
				gl.type_status = "body"
				gl.blank_num = 0
		elif gl.blank_num > 0 and gl.type_status != "analysis":
			if gl.type_status == "body":
				(val, tag) = self.option_ana(val)
				if tag == 1:
					gl.type_status = "options"
			elif gl.type_status == "options":
				gl.type_status = "answer"
				gl.option_stat = ""
			elif gl.type_status == "answer":
				gl.type_status = "analysis"
			gl.blank_num = 0
		elif gl.type_status == "options":
			(val, tag) = self.option_ana(val)

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

		#print "before: " + gl.type_status + str(gl.blank_num) + " : "+ val
		if gl.type_status == "":
			gl.type_status = "type"
			return
		elif gl.type_status == "" and gl.sub_status==1:
			gl.excep=5
			gl.type_status = "type"
			return
		elif re.compile('^[\s]*\001$').match(val):
			gl.blank_num += 1
			return
		elif gl.type_status == "type":
			gl.type_status = "body"
			gl.blank_num = 0
			gl.sub_status = 1
		elif gl.blank_num > 0 and gl.type_status != "analysis":
			if gl.type_status == "body":
				gl.type_status = "answer"
			elif gl.type_status == "answer":
				gl.type_status = "analysis"
			gl.blank_num = 0

		#print "after : " + gl.type_status + " : "+ val
		return val
