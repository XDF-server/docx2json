# *-* coding:utf-8 *-*

import zipfile
import re
import os

class Docx(object):
	
	def __init__(self):
		self.reset()

	def reset(self):
		self.zf = None	
		self.fd = None
		self.docxname = None
	
	def open(self,docxname):
		self.docxname = docxname[0:docxname.find('.')]
		self.fd = open(docxname)
		self.zf = zipfile.ZipFile(self.fd)
		self._pic_unzip()

	def get_xml(self,xmlname):
		return self.zf.read(xmlname,'r')

	def _pic_unzip(self):
		namelist = self.zf.namelist()

		os.mkdir(self.docxname)
			
		for name in namelist:
			if re.match(r'word/media/*',name):
				self.zf.extract(name,self.docxname)

	def __del__(self):
		self.fd.close()
				

if __name__ == '__main__':
	docx = Docx()
	docx.open('test.docx')
	print docx.get_xml('word/document.xml')
