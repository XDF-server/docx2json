# *_* coding:utf-8 *-*

from docx import * 
from parser import *
import time
import zipfile

parser = Parser('/home/zhangchunyang/docx/qd_hHyrlb9887.docx')
for node,msg in parser.iterater():
	print msg
	time.sleep(0.1)
	#if msg == 'BOM':
'''zf = zipfile.ZipFile('qd_hHyrlb9887.docx') 
zf.namelist()
zf.extractall('.',['word/media/'])'''
