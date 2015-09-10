#!/usr/local/python2.7/bin/python
# *-* coding:utf-8 *-*

import zipfile
import re
import os
from parser import Parser
from subject import * 
from dic2json import Dic2json
import gl
import json

class Docxml(object):
	
	def __init__(self,docxname, config_file, config_type):
		self.reset(docxname)
		self.config_file = config_file
		self.config_type = config_type

	def reset(self,docxname):
		self.docxname = docxname[0:docxname.find('.')]
		self.fd = open(docxname)
		self.zf = zipfile.ZipFile(self.fd)
		self._pic_unzip()

	def get_xml(self,xmlname):
		return self.zf.read(xmlname,'r')

	def parse(self):
		self.parser = Parser()
		document_xml = self.get_xml('word/document.xml')
		self.parser.set_document_xml(document_xml)
		pic_rel_xml = self.get_xml('word/_rels/document.xml.rels')
		self.parser.set_pic_rel_xml(pic_rel_xml)

	def subject(self,stype):
		#if self.config_type == "tag":
		#	subject = Subject(self.config_file)
		#elif stype == "选择题" or stype == "单项选择":
		#	subject = Subject_blank()
		#elif stype == "判断题" or stype == "简答题" or stype == "填空题" or stype == "解答题":
		#	subject = Subject_panduan()
		#elif stype == "综合题":
		#if stype == "综合题":
		subject = Subject_complex()

		doc_line = ''
		dic2json = Dic2json()

		print "###gl.excep" + str(gl.excep)
		for node,val,pnum,bnum in self.parser.iterater():
			doc_line += val
			if '\001' == val:
				json_unit = subject.parse(doc_line,pnum,bnum)
				doc_line = ''
				if json_unit :
					dic2json.parse( json_unit[0:-1], self.docxname )


	def _pic_unzip(self):
		namelist = self.zf.namelist()
		try:
			os.mkdir(self.docxname)
		except OSError, why:
			print "Warning: %s " % str(why)
			
		for name in namelist:
			if re.match(r'word/media/*',name):
				self.zf.extract(name,self.docxname)
			elif re.match(r'media/*',name):
				self.zf.extract(name,self.docxname)
			#elif re.match(r'word/*',name):
			#	self.zf.extract(name,self.docxname)

	def __del__(self):
		self.fd.close()
				

#file_o='/home/work/wzj/docx/qd_hRpvpK4384.docx' ###选择型阅读理解
#file_o='/home/work/wzj/docx/qd_hRtBso8550.docx' ###选择型阅读理解
#file_o='/home/work/wzj/docx/qd_hQ4Xi97460.docx' ###综合题
#file_o='/home/work/wzj/docx/qd_hSxVNm9081.docx' ###分析说明题
#file_o='/home/work/wzj/docx/qd_hQBU0t2728.docx' ###探究题
#file_o='/home/work/wzj/docx/qd_hPXjeK7573.docx' ###组合选择题
file_o='/home/work/wzj/docx/qd_hRAWN96891.docx' ###现代文阅读题
#file_o='/home/work/wzj/docx/qd_hM0Uyl7896.docx' ###实验题
#file_o='/home/work/wzj/docx/qd_ikm0SM7518.ori.docx' ###err6
#file_o='/home/work/wzj/docx/qd_xPz8W4k08M.docx'  ###err8
docx = Docxml(file_o, '','')
docx.parse()
docx.subject(gl.main_q_type)
if gl.question["topic_type"].has_key("id") and gl.question["topic_type"]["id"]:
	gl.content["questions"].append(gl.question)
print json.dumps(gl.content, ensure_ascii=0)
print gl.excep
