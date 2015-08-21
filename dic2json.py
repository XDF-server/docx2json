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
		self.flg_list = [] ###文本字体样式flg
		self.style = 0 ###文本字体样式
		self.cnt = 1 
	
	def parse(self,val,docname):
		#print gl.option_stat + "  " + gl.type_status + ":" + val
		if gl.type_change and gl.type_status != "options":
			unit = {"type":"newline","value":"1"}
			self._data_push(unit)
		self._analysis(val,docname)
		unit = {"type":"newline","value":"1"}
		self._data_push(unit)

	def _data_push(self,val):

		#print json.dumps(val, ensure_ascii=0)
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
			if self.option_result:
				gl.question["options"].append(self.option_result)
				self.option_result = []
				self.option_flg = ""

			gl.question[gl.type_status].append(val)


	def _analysis(self,val,docname):

		list = val.split('\006')
		for i in range(0,len(list)):
		#for i in range(1,len(list),2):
			if i%2 == 1:
				self._picinfo(list[i],docname)
			else:
				self._aligninfo(list[i],docname)


	def _aligninfo(self,val,docname):

		sub_flg = 0
		up_flg = 0
		align = 0
		text = ""
		acc_list = {'\001':1, '\002':2, '\004':4, '\008':8, '\016':16} 
		#print val
		for i in val:
			if i == '\004' or i == '\016':
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

		cmd = "mkdir -p /home/work/wzj/tmpfile/vertAlign/"
		retn=call(cmd,shell=True)
		pic_type = 0
		for i in val.decode('utf8'):
			pic = "/home/work/wzj/tmpfile/vertAlign/"
			url = "http://10.60.0.159/vertAlign/"
			if atype == 2:
				pic += "sub_" + i.encode('utf8') + ".gif"
				url += "sub_" + i.encode('utf8') + ".gif"
			elif atype == 3:
				pic += "up_" + i.encode('utf8') + ".gif"
				url += "up_" + i.encode('utf8') + ".gif"


			if pic in gl.vertAlignSet:

				###在角标集中存在
				try:
					img = Image.open(pic)
				except:
					print "_create_pic : openfileNG  pic: " + pic

				(width, height) = img.size
				unit = {"type" : "image", "value":url, "width":width, "height":height, "image_type":pic_type }
				self._data_push(unit)
			else:
				###在角标集中不存在
				w = 5
				if (unicodedata.east_asian_width(i) in ('F','W','A')):
					w = 10
				h = 20

				bgcolor=(255,255,255,0) #背景颜色,透明度
				fontcolor = (0,0,0) #字体颜色
				font = ImageFont.truetype("/usr/share/fonts/simsun/simsun.ttf",10)
				img = Image.new("RGBA", (w,h), bgcolor) # 创建图形 生成背景图片
				draw = ImageDraw.Draw(img) # 创建画笔
		
				if atype == 2:
					draw.text((0,10),val,font=font,fill=fontcolor)
				elif atype == 3:
					draw.text((0,0),val,font=font,fill=fontcolor)

				del draw

				img.save(pic) #保存原始版本
				gl.vertAlignSet.add(pic)
				unit = {"type" : "image", "value":url, "width":w, "height":h, "image_type":pic_type }
				self._data_push(unit)

		return ""


	def _picinfo(self,val,docname):

		###源文件位置
		file_s = docname + "/word/" + val
		if os.path.isfile(file_s) is False:
			file_s = docname + val
		###url用目录
		dir_b = docname.split('/')[-1] + "/" + "/".join(val.split('/')[0:-1])
		###实际目录
		dir_o = '/home/work/wzj/tmpfile/' + dir_b

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
			cmd = "/usr/local/bin/svgexport " + file_o_s + " " + file_o
			retn=call(cmd,shell=True)
			img = Image.open(file_o)
			(width, height) = img.size
			fname = ".".join(fnamelist[0:-1]) + ".png"
		elif re.search(r'wmf',result):
			###图片后缀 svg
			fname = ".".join(fnamelist[0:-1]) + ".svg"
			file_o_s = dir_o + '/' + fname
			TypeChange.wmf2svg(file_s, file_o_s)
			#pic_type = 3
			print "wmf svgexport"
			cmd = "/usr/local/bin/svgexport " + file_o_s + " " + file_o
			retn=call(cmd,shell=True)
			#img = Image.open(file_s)
			img = Image.open(file_o)
			(width, height) = img.size
			fname = ".".join(fnamelist[0:-1]) + ".png"
		else:
			cmd = "/usr/bin/convert -transparent white " + file_s + " " + file_o
			print cmd
			retn=call(cmd,shell=True)

			img = Image.open(file_s)
			(width, height) = img.size
			
		url = "http://10.60.0.159/" + dir_b + "/" + fname
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
		dir_o = '/home/work/wzj/tmpfile/' + dir_b

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
			
		url = "http://10.60.0.159/" + dir_b + "/" + fname
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
		dir_o = '/home/work/wzj/tmpfile/' + dir_b

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
			
		url = "http://10.60.0.159/" + dir_b + "/" + fname
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
		dir_o = '/home/work/wzj/tmpfile/' + dir_b

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

		url = "http://10.60.0.159/" + dir_b + "/" + fname
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
		dir_o = '/home/work/wzj/tmpfile/' + dir_b

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

		url = "http://10.60.0.159/" + dir_b + "/" + fname
		unit = {"type" : "image", "value":url, "width":width, "height":height, "image_type":pic_type }
		self._data_push(unit)
		return
		
