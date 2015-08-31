#! *-* coding:utf-8 *-*

import gl
import re
import os
#import shutil
from subprocess import call
import subprocess
from PIL import Image,ImageFont,ImageDraw
import glob
import json
import unicodedata
from glue_java import *

class Dic2json(object):

	def __init__(self):
		self.option_result = []
		self.option_flg = ""
		self.blank_flg = 0
		self.blank_cnt = 0
		self.flg_list = [] ###文本字体样式flg
		self.style = 0 ###文本字体样式
		self.cnt = 1 
	
	def parse(self,val,docname):
		#print gl.option_stat + "  " + gl.type_status + ":" + val + " " + gl.q_type_l
		#if gl.type_change and gl.type_status != "options":
		#	unit = {"type":"newline","value":"1"}
		#	self._data_push(unit)
		self._analysis(val,docname)
		print gl.type_status + gl.q_type_l
		if gl.q_type_l!="选择题":
			unit = {"type":"newline","value":"1"}
			self._data_push(unit)
		elif gl.type_status != "answer":
			unit = {"type":"newline","value":"1"}
			self._data_push(unit)

	def _data_push(self,val):

		val_o = val
		if gl.type_status == "options" :
			if self.option_flg != gl.option_stat:
				self.option_flg =  gl.option_stat
				if self.option_result:
					gl.question["options"].append(self.option_result)
					self.option_result = []
				self.option_result.append({ "type" : "option", "value" : gl.option_stat })
			if val:
				self.option_result.append(val)

		else:
			###初始化options相关变量
			if self.option_result:
				gl.question["options"].append(self.option_result)
				self.option_result = []
				self.option_flg = ""

			if gl.q_type=="填空题" and gl.type_status=="body" and val_o['type']=='text':
				if val['style']==4 and re.match('^[ 　]+$'.decode('utf8'),val_o['value']):
					if self.blank_flg==0:
						self.blank_flg = 1
						self.blank_cnt += 1
						val={ "type" : "blank", "value" : self.blank_cnt }
						gl.question[gl.type_status].append(val)
				elif re.search('_',val_o['value']):
					#print "###route"
					vlist = val_o['value'].split('_')
					for v in vlist:
						if v:
							val = {"type" : "text", "value":v, "size":"", "font":"", "style":val_o['style'], "align":val_o['align']} 
							gl.question[gl.type_status].append(val)
							self.blank_flg = 0
						elif self.blank_flg==0:
							self.blank_flg = 1
							self.blank_cnt += 1
							val={ "type" : "blank", "value" : self.blank_cnt }
							gl.question[gl.type_status].append(val)
				else:
					gl.question[gl.type_status].append(val)
					self.blank_flg = 0
			elif gl.q_type_l=="选择题" and gl.type_status == "answer":
				print "选择题"
				print val_o['value']
				for i in val_o['value']:
					gl.question[gl.type_status].append(i)
			else:
				gl.question[gl.type_status].append(val)
				self.blank_flg = 0


	def _analysis(self,val,docname):

		vlist = val.split('\006')
		for i in range(0,len(vlist)):
		#for i in range(1,len(vlist),2):
			if i%2 == 1:
				if gl.excep == 0:
					self._picinfo(vlist[i],docname)
			else:
				self._aligninfo(vlist[i],docname)


	def _aligninfo(self,val,docname):

		sub_flg = 0
		up_flg = 0
		align = 0
		text = ""
		acc_list = {'\001':1, '\007':2, '\004':4, '\008':8, '\016':16, '\032':32} 
		#print val
		for i in val:
			if i == '\004' or i == '\016' or i == '\032' or i == '\007':
				if self.flg_list.count(i)==0:
					self.flg_list.append(i)
					if text != "":
						unit = {"type" : "text", "value":text, "size":"", "font":"", "style":self.style, "align":align }
						self._data_push(unit)
						text = ""
					self.style += acc_list[i]  
				else:
					self.flg_list.remove(i)
					if text != "":
						unit = {"type" : "text", "value":text, "size":"", "font":"", "style":self.style, "align":align }
						self._data_push(unit)
						text = ""
					self.style -= acc_list[i]  
			elif i == '\012' or i == '\013':
				if text != "":
					unit = {"type" : "text", "value":text, "size":"", "font":"", "style":self.style, "align":align }
					self._data_push(unit)
				text = ""
				if align :
					align = 0
				else:
					if i == '\012':
						align = 2
					else:
						align = 3
					
			elif i == '\002':
				if sub_flg == 0:
					sub_flg = 1
					if text != "":
						#print "txt:" + text
						unit = {"type" : "text", "value":text, "size":"", "font":"", "style":self.style, "align":align }
						self._data_push(unit)
				else:
					#print "sub:" + text
					sub_flg = 0
					new_pic_info = self._create_pic(text,2)

				text = ""

			elif i == '\003':
				if up_flg == 0:
					up_flg = 1
					if text != "":
						#print "txt:" + text
						unit = {"type" : "text", "value":text, "size":"", "font":"", "style":self.style, "align":align }
						self._data_push(unit)
				else:
					#print "up:" + text
					up_flg = 0
					new_pic_info = self._create_pic(text,3)

				text = ""

			else:
				text += i

		if text != "":
			unit = {"type" : "text", "value":text, "size":"", "font":"", "style":self.style, "align":align }
			self._data_push(unit)


	def _create_pic(self,val,atype):

		#print "###create vertAlign start"
		cmd = "mkdir -p /home/work/wzj/tmpfile_f/vertAlign/"
		retn=call(cmd,shell=True)
		ttf_type = 0
		for i in val.decode('utf8'):
			print "####_create_pic: " + i
			if i=='\010':
				ttf_type = ~ttf_type
				continue
			if i==" " or i=="":
				continue
			
			pic = "/home/work/wzj/tmpfile_f/vertAlign/"
			#url = "http://10.60.0.159/vertAlign/"
			url = "/vertAlign/"
			#end=".gif"
			end=".png"
			pos = ""
			sflg=0
			sstr=""
			if i == '(':
				sflg=1
				sstr="xa"
				print "###sflg:1"
			elif i == ')':
				sflg=2
				sstr="xb"
				print "###sflg:2"
			elif i == '*':
				sflg=3
				sstr="xy"
				print "###sflg:3"
			elif i == '|':
				sflg=4
				sstr="xz"
				print "###sflg:4"
			elif i == r"/":
				sflg=5
				sstr="xc"
				print "###sflg:5"
			elif i == r";":
				sflg=6
				sstr="xd"
				print "###sflg:6"

			if atype == 2:
				if sflg:
					pic += "sub_" + sstr + end
				else:
					pic += "sub_" + i.encode('utf8') + end

				if sflg:
					url += "sub_" + sstr + end
				else:
					url += "sub_" + i.encode('utf8') + end
				pos = "south"
			elif atype == 3:
				if sflg:
					pic += "up_" + sstr + end
				else:
					pic += "up_" + i.encode('utf8') + end

				if sflg:
					url += "up_" + sstr + end
				else:
					url += "up_" + i.encode('utf8') + end
				pos = "north"

			font_file = ""
			if ttf_type:
				font_file = "/usr/share/fonts/times/timesi.ttf"
			else:
				font_file = "/usr/share/fonts/simsun/simsun.ttf"


			print pic
			if pic in gl.vertAlignSet:

				###在角标集中存在
				try:
					img = Image.open(pic)
				except:
					print "_create_pic : openfileNG  pic: " + pic
					print "_create_pic : openfileNG  i: " + i

				(width, height) = img.size
				unit = {"type" : "image", "value":url, "width":width, "height":height, "image_type":1 }
				self._data_push(unit)
			else:
				###在角标集中不存在
				w = 7
				if (unicodedata.east_asian_width(i) in ('F','W','A')):
					w = 10
				h = 20

				cmd = "/usr/bin/convert -transparent white -size " + str(w) + "x" + str(h) + " -gravity " + pos + " -pointsize 10 -font " + font_file + " label:'" + i + "' " + pic

                        	print cmd
                        	retn=call(cmd,shell=True)

				gl.vertAlignSet.add(pic)
				unit = {"type" : "image", "value":url, "width":w, "height":h, "image_type":1 }
				self._data_push(unit)

		return ""


	def _picinfo(self,val,docname):

		###源文件位置
		print "#####val: " + val
		vlist = val.split(' ')
		width_o = 0
		height_o = 0
		x = 0.0
		xl = 0.0
		y = 0.0
		yl = 0.0
		if vlist[0] == "embed":
			val = vlist[1]
			p=re.match(r'x:([e0-9.-]+);xl:([e0-9.-]+);y:([e0-9.-]+);yl:([e0-9.-]+)$',vlist[2])
                        x = float(p.group(1))
                        xl = float(p.group(2))
                        y = float(p.group(3))
                        yl = float(p.group(4))
			width_o = float(vlist[3])
			height_o = float(vlist[4])
		elif vlist[0] == "image":
			width_o = float(vlist[1])
			height_o = float(vlist[2])
			p=re.match(r'x:([e0-9.-]+);xl:([e0-9.-]+);y:([e0-9.-]+);yl:([e0-9.-]+)$',vlist[3])
                        x = float(p.group(1))
                        xl = float(p.group(2))
                        y = float(p.group(3))
                        yl = float(p.group(4))
			val = vlist[4]
		else:
			print gl.excep

		file_s = docname + "/word/" + val
		#print "file_s: " + file_s

		if os.path.isfile(file_s) is False:
			file_s = docname + val
		###url用目录
		dir_b = docname.split('/')[-1] + "/" + "/".join(val.split('/')[0:-1])
		###实际目录
		dir_o = '/home/work/wzj/tmpfile_f/' + dir_b

		###创建新文件目录
		try:
			cmd = "mkdir -p " + dir_o
			retn=call(cmd,shell=True)
		except: 
			print "mkdir err"


		pic_type = 1
		width = 0
		height = 0
		fname = val.split('/')[-1]
		fnamelist = fname.split('.')
		###图片后缀 png
		fname = ".".join(fnamelist[0:-1]) + ".png"
		file_o = dir_o + '/' + fname

		###查看图片类型
		cmd = "/usr/bin/file " + file_s
		p = []
		p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		result = p.stdout.readlines()[0]
		#print result
		if re.search(r'EMF',result):
			cmd = "echo " + str(gl.oldid) + file_s + ">>pic_need_change"
			retn=call(cmd,shell=True)
			#fname = ".".join(fnamelist[0:-1]) + ".svg"
			#file_o_s = dir_o + '/' + fname
			#cmd = "/usr/local/bin/svgexport " + file_o_s + " " + file_o
			#retn=call(cmd,shell=True)
			#img = Image.open(file_o)
			#(width, height) = img.size
			#fname = ".".join(fnamelist[0:-1]) + ".png"
			gl.excep=1
		elif re.search(r'wmf',result):
			###图片后缀 svg
			fname = ".".join(fnamelist[0:-1]) + ".svg"
			file_o_s = dir_o + '/' + fname
			TypeChange.wmf2svg(file_s, file_o_s)
			#pic_type = 3
			#print "wmf svgexport"
			cmd = "/usr/local/bin/svgexport " + file_o_s + " " + file_o
			retn=call(cmd,shell=True)
			#img = Image.open(file_s)
			img = Image.open(file_o)
			(width, height) = img.size
			fname = ".".join(fnamelist[0:-1]) + ".png"
		else:
			cmd = "/usr/bin/convert -transparent white " + file_s + " " + file_o
			#print cmd
			retn=call(cmd,shell=True)

			img = Image.open(file_s)
			(width, height) = img.size
			
		if x or xl or y or yl:
			#print "change:" + str(width) + "x" + str(height)
			#print x
			#print xl
			#print y
			#print yl
			width_x = 0
			width_l = 0
			height_y = 0
			height_l = 0
			if x:
				width_x = int(width * float(x))
			if xl:
				width_l = int(width * float(xl))
			if y:
				height_y = int(height * float(y))
			if yl:
				height_l = int(height * float(yl))
			file_s = file_o
			fname = ".".join(fnamelist[0:-1]) + "_co.png"
			file_o = dir_o + '/' + fname
			width = width_x
			height = height_y
			cmd = "/usr/bin/convert -crop " + str(width) + "x" + str(height) + "+" + str(width_l) + "+" + str(height_l) + " " + file_s + " " + file_o
			#print cmd
			retn=call(cmd,shell=True)

		if height_o and height/height_o/1.35 > 1.5 and width_o and width/width_o/1.35 > 1.5:
			#print "real:" + str(width_o) + "x" + str(height_o)
			#print "change:" + str(width) + "x" + str(height)
		        width = int(int(width_o) * 1.35 )	
		        height = int(int(height_o) * 1.35 )	
			file_s = file_o
			fname = ".".join(fnamelist[0:-1]) + "_cv.png"
			file_o = dir_o + '/' + fname
			cmd = "/usr/bin/convert -resize " +str(width) + "x" + str(height) + " " + file_s + " " + file_o
			#print cmd
			retn=call(cmd,shell=True)

		#url = "http://10.60.0.159/" + dir_b + "/" + fname
		url = "/" + dir_b + "/" + fname
		unit = {"type" : "image", "value":url, "width":width, "height":height, "image_type":pic_type }
		self._data_push(unit)

		return


	def _picinfo_convert(self,val,docname):

		###源文件位置
		file_s = docname + "/word/" + val
		if os.path.isfile(file_s) is False:
			file_s = docname + val
		###url用目录
		dir_b = docname.split('/')[-1] + "/" + "/".join(val.split('/')[0:-1])
		###实际目录
		dir_o = '/home/work/wzj/tmpfile_f/' + dir_b

		###创建新文件目录
		try:
			cmd = "mkdir -p " + dir_o
			retn=call(cmd,shell=True)
		except: 
			print "mkdir err"


		pic_type = 1
		width = 0
		height = 0
		fname = val.split('/')[-1]
		fnamelist = fname.split('.')
		###图片后缀 png
		fname = ".".join(fnamelist[0:-1]) + ".png"
		file_o = dir_o + '/' + fname

		###查看图片类型
		cmd = "/usr/bin/file " + file_s
		p = []
		p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		result = p.stdout.readlines()[0]
		print result
		if re.search(r'EMF',result):
			#cmd = "echo " + file_s + ">>pic_need_change"
			#retn=call(cmd,shell=True)
			fname = ".".join(fnamelist[0:-1]) + ".svg"
			file_o_s = dir_o + '/' + fname
			img = Image.open(file_o_s)
			(width, height) = img.size
			cmd = "cp -f " + file_o_s + " " + file_o
		elif re.search(r'wmf',result):
			###图片后缀 svg
			fname = ".".join(fnamelist[0:-1]) + ".svg"
			file_o = dir_o + '/' + fname
			TypeChange.wmf2svg(file_s, file_o)
			pic_type = 3
			img = Image.open(file_s)
			(width, height) = img.size
		else:
			cmd = "/usr/bin/convert -transparent white " + file_s + " " + file_o
			print cmd
			retn=call(cmd,shell=True)

			img = Image.open(file_s)
			(width, height) = img.size
			
		#url = "http://10.60.0.159/" + dir_b + "/" + fname
		url = "/" + dir_b + "/" + fname
		unit = {"type" : "image", "value":url, "width":width, "height":height, "image_type":pic_type }
		self._data_push(unit)

		return


	def _picinfo_sizechange(self,val,docname):

		###源文件位置
		file_s = docname + "/word/" + val
		if os.path.isfile(file_s) is False:
			file_s = docname + val
		###url用目录
		dir_b = docname.split('/')[-1] + "/" + "/".join(val.split('/')[0:-1])
		###实际目录
		dir_o = '/home/work/wzj/tmpfile_f/' + dir_b

		###创建新文件目录
		try:
			cmd = "mkdir -p " + dir_o
			retn=call(cmd,shell=True)
		except: 
			print "mkdir err"


		pic_type = 1
		width = 0
		height = 0
		fname = val.split('/')[-1]
		fnamelist = fname.split('.')
		###图片后缀 png
		fname = ".".join(fnamelist[0:-1]) + ".png"
		file_o = dir_o + '/' + fname

		###查看图片类型
		cmd = "/usr/bin/file " + file_s
		p = []
		p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		result = p.stdout.readlines()[0]
		print result
		if re.search(r'EMF',result):
			cmd = "echo " + file_s + ">>pic_need_change"
			retn=call(cmd,shell=True)
		else:
			try: 
				img = Image.open(file_s)
				(width, height) = img.size
				cmd = "/usr/bin/convert -transparent white -adaptive-resize " + str(width) + "x" + str(height) + " " + file_s + " " + file_o
				print cmd
				retn=call(cmd,shell=True)
			except:
				cmd = "/usr/bin/convert -transparent white " + file_s + " " + file_o
				print cmd
				retn=call(cmd,shell=True)
				img = Image.open(file_o)
				(width, height) = img.size
			
		#url = "http://10.60.0.159/" + dir_b + "/" + fname
		url = "/" + dir_b + "/" + fname
		unit = {"type" : "image", "value":url, "width":width, "height":height, "image_type":pic_type }
		self._data_push(unit)

		return


	def _picinfo_bk2(self,val,docname):

		###源文件位置
		file_s = docname + "/word/" + val
		if os.path.isfile(file_s) is False:
			file_s = docname + val
		###url用目录
		dir_b = docname.split('/')[-1] + "/" + "/".join(val.split('/')[0:-1])
		###实际目录
		dir_o = '/home/work/wzj/tmpfile_f/' + dir_b

		###创建新文件目录
		try:
			cmd = "mkdir -p " + dir_o
			retn=call(cmd,shell=True)
		except: 
			print "mkdir err"
		

		img = Image.open(file_s)
		(width, height) = img.size

		url = ""
		file_o=""
		pic_type = 0
		fname = val.split('/')[-1]
		fnamelist = fname.split('.')
		print fnamelist
		if fnamelist[-1] == "bin":
			
			###查看图片类型
			cmd = "/usr/bin/file " + file_s
			p = []
			p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			result = p.stdout.readlines()[0]
			print result
			if re.search(r'wmf',result,re.I):
				###图片后缀 png
				fname = ".".join(fnamelist[0:-1]) + ".svg"
				file_o = dir_o + '/' + fname
				TypeChange.wmf2svg(file_s, file_o)
				pic_type = 3
			elif re.search(r'PNG',result,re.I):
				###图片后缀 png
				fname = ".".join(fnamelist[0:-1]) + ".png"
				file_o = dir_o + '/' + fname
				cmd = "cp -f " + file_s + " " +file_o
				retn=call(cmd,shell=True)
				pic_type = 1
			elif re.search(r'JPEG',result,re.I):
				###图片后缀 jpg
				fname = ".".join(fnamelist[0:-1]) + ".jpg"
				file_o = dir_o + '/' + fname
				cmd = "cp -f " + file_s + " " +file_o
				retn=call(cmd,shell=True)
				pic_type = 2
			else:
				print "######pic formart######" + result
				return

		else:
			file_o = dir_o + '/' + fname
			cmd = "cp -f " + file_s + " " +file_o
			retn=call(cmd,shell=True)
			#shutil.copy(file_s,file_o)

		#url = "http://10.60.0.159/" + dir_b + "/" + fname
		url = "/" + dir_b + "/" + fname
		unit = {"type" : "image", "value":url, "width":width, "height":height, "image_type":pic_type }
		self._data_push(unit)
		return
		

	def _picinfo_bak(self,val,docname):

		###源文件位置
		file_s = docname + "/word/" + val
		if os.path.isfile(file_s) is False:
			file_s = docname + val
		###url用目录
		dir_b = docname.split('/')[-1] + "/" + "/".join(val.split('/')[0:-1])
		###实际目录
		dir_o = '/home/work/wzj/tmpfile_f/' + dir_b

		###创建新文件目录
		try:
			cmd = "mkdir -p " + dir_o
			retn=call(cmd,shell=True)
		except: 
			print "mkdir err"
		

		url = ""
		file_o=""
		pic_type=0
		fname = val.split('/')[-1]
		fnamelist = fname.split('.')
		###查看图片类型
		cmd = "/usr/bin/file " + file_s
		p = []
		p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		result = p.stdout.readlines()[0]
		if fnamelist[-1] == "bin":
			
			if re.search(r'wmf|PNG',result,re.I):
				###图片后缀 png
				fname = ".".join(fnamelist[0:-1]) + ".png"
			elif re.search(r'JPEG',result,re.I):
				###图片后缀 jpg
				fname = ".".join(fnamelist[0:-1]) + ".jpg"
			else:
				print "######pic formart######" + result
				return

			file_o = dir_o + '/' + fname
			cmd = "/usr/bin/convert  " + file_s + " " + file_o
			retn=call(cmd,shell=True)
		else:
			file_o = dir_o + '/' + fname
			cmd = "cp -f " + file_s + " " +file_o
			retn=call(cmd,shell=True)
			#shutil.copy(file_s,file_o)

		img = Image.open(file_o)

		(width, height) = img.size

		#url = "http://10.60.0.159/" + dir_b + "/" + fname
		url = "/" + dir_b + "/" + fname
		unit = {"type" : "image", "value":url, "width":width, "height":height, "image_type":pic_type }
		self._data_push(unit)
		return
		
