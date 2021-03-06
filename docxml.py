#!/usr/local/python2.7/bin/python
# *-* coding:utf-8 *-*

import zipfile
import re
import os
from parser import Parser
from subject import * 
from dic2json import Dic2json
import gl

class Docxml(object):
	
	def __init__(self,docxname, config_file, config_type):
		self.reset(docxname)
		self.config_file = config_file
		self.config_type = config_type

	def reset(self,docxname):
		self.docxname = docxname[0:docxname.find('.')]
		self.fd = open(docxname)
		try:
			self.zf = zipfile.ZipFile(self.fd)
			self._pic_unzip()
		except:
			gl.excep=7

	def get_xml(self,xmlname):
		return self.zf.read(xmlname,'r')

	def parse(self):
		self.parser = Parser()
		document_xml = self.get_xml('word/document.xml')
		self.parser.set_document_xml(document_xml)
		pic_rel_xml = self.get_xml('word/_rels/document.xml.rels')
		self.parser.set_pic_rel_xml(pic_rel_xml)

	def subject(self,stype):
		if self.config_type == "tag":
			subject = Subject(self.config_file)
		elif stype == "选择题" or stype == "单项选择":
			subject = Subject_blank()
		elif stype == "写作题" or stype=="书面表达":
			subject = Subject_xiezuo()
		else:
			subject = Subject_panduan()
		
		doc_line = ''
		dic2json = Dic2json()

		for node,val,pnum,bnum in self.parser.iterater():

			if gl.excep:
				break

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

	def __del__(self):
		self.fd.close()
				

#file_o='/home/work/wzj/docx/qd_jOPKLM3114.ori.docx'
#file_o='/home/work/wzj/docx/gonshi.docx'
#docx = Docxml(file_o, '','')
#docx.parse()
#docx.subject()
