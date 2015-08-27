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



class Subject_blank(object):
	

	def parse(self,val,pnum,bnum):

		print "before:" + gl.type_status + " : " + val
		flg = 0 ###类型变化flg 用来增加空行的
		val = val.replace(b'\xc2\xa0',' ')
		val = val.replace(b'\xe3\x80\x80',' ')
		val = val.replace('\004\004','')
		val = val.replace('\007\007','') #去除多余斜体标记
		val = val.replace('\016\016','')
		val = val.replace('\012\012','') #去除多余居中符
		val = val.replace('\013\013','') #去除多余居右符
		val = val.replace('\032\032','')
		#print "###" + val +"###" + str(gl.blank_num)
		if gl.type_status == "":
			gl.type_status = "type"
			return
		elif re.match(r'^[\s　]*\001$',val) or (val == '\005\001' and gl.type_status != "analysis" and gl.type_status != ""):
			gl.blank_num += 1
			return
		elif gl.type_status == "type":
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
		print "after : " + gl.type_status + " : " + val
		val = val.replace('\005','')
		val = val.replace("'","''")
		return val


	def option_ana(self,val):

		p = re.match(r'([a-gA-G])[\.．、]*(.*)'.decode('utf8'), val)
		if p:
			gl.option_stat = p.group(1)
			return (p.group(2), 1)
		else:
			return (val, 0)


class Subject_panduan(object):
	

	def parse(self,val,pnum,bnum):

		print "before: " + gl.type_status + " : "+ val
		flg = 0 ###类型变化flg 用来增加空行的
		val = val.replace(b'\xc2\xa0',' ') #去除utf8特殊空格
		val = val.replace('\004\004','') #去除多余下划线标记
		val = val.replace('\007\007','') #去除多余斜体标记
		val = val.replace('\016\016','') #去除多余着重点标记
		val = val.replace('\012\012','') #去除多余居中符
		val = val.replace('\013\013','') #去除多余居右符
		val = val.replace('\032\032','') #去除多余方框
		if gl.type_status == "":
			gl.type_status = "type"
			return
		elif re.compile('^[\s]*\001$').match(val) or (val == '\005\001' and gl.type_status != "analysis" and gl.type_status != ""):
			gl.blank_num += 1
			return
		elif gl.type_status == "type":
			gl.type_status = "body"
			gl.blank_num = 0
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
		print "after : " + gl.type_status + " : "+ val
		val = val.replace('\005','')
		val = val.replace("'","''")
		return val
