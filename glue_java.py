# *-* coding:utf-8 *-* 

import os

class JAVA(object):

	@staticmethod
	def wmf2svg(src_path,des_path):
		
		command = "java -jar wmf2svg.jar %s %s" % (src_path,des_path)
		os.system(command)


JAVA.wmf2svg("../test/image5.wmf","./image.svg")
