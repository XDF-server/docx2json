#!/usr/local/python2.7/bin/python
# *-* coding:utf-8 *-* 

import os

class TypeChange(object):

	@staticmethod
	def wmf2svg(src_path,des_path):
		
		command = "java -jar wmf2svg.jar %s %s" % (src_path,des_path)
		os.system(command)


TypeChange.wmf2svg("/home/work/wzj/docx/qd_hMreOp5191/media/image2.bin","./image.svg")
