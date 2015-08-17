#! *-* coding:utf-8 *-*

import gl
import re
import os
import shutil
from subprocess import call
from PIL import Image,ImageFont,ImageDraw
import glob
import json

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
		text = ""
		acc_list = {'\001':1, '\002':2, '\004':4, '\008':8, '\016':16} 
		#print val
		for i in val:
			if i == '\004' or i == '\016':
				if self.flg_list.count(i)==0:
					self.flg_list.append(i)
					if text != "":
						unit = {"type" : "text", "value":text, "size":"", "font":"", "style":self.style }
						self._data_push(unit)
						text = ""
					self.style += acc_list[i]  
				else:
					self.flg_list.remove(i)
					if text != "":
						unit = {"type" : "text", "value":text, "size":"", "font":"", "style":self.style }
						self._data_push(unit)
						text = ""
					self.style -= acc_list[i]  
			elif i == '\002':
				if sub_flg == 0:
					sub_flg = 1
					if text != "":
						#print "txt:" + text
						unit = {"type" : "text", "value":text, "size":"", "font":"", "style":self.style }
						self._data_push(unit)
				else:
					#print "sub:" + text
					sub_flg = 0
					new_pic_info = self._create_pic(text,2)
					unit = {"type" : "image", "value":new_pic_info['url'], "width":new_pic_info['w'], "height":new_pic_info['h'] }
					self._data_push(unit)

				text = ""

			elif i == '\003':
				if up_flg == 0:
					up_flg = 1
					if text != "":
						#print "txt:" + text
						unit = {"type" : "text", "value":text, "size":"", "font":"", "style":self.style }
						self._data_push(unit)
				else:
					#print "up:" + text
					up_flg = 0
					new_pic_info = self._create_pic(text,3)
					unit = {"type" : "image", "value":new_pic_info['url'], "width":new_pic_info['w'], "height":new_pic_info['h'] }
					self._data_push(unit)

				text = ""

			else:
				text += i

		if text != "":
			unit = {"type" : "text", "value":text, "size":"", "font":"", "style":self.style }
			self._data_push(unit)

	def _picinfo(self,val,docname):

		file = docname + "/word/" + val
		if os.path.isfile(file) is False:
			file = docname + val
		dir_b = docname.split('/')[-1] + "/" + "/".join(val.split('/')[0:-1])
		fname = val.split('/')[-1]
		fnamelist = fname.split('.')
		if fnamelist[-1] == "bin":
			fname = ".".join(fnamelist[0:-1]) + ".png"
		dir_o = '/home/work/wzj/tmpfile/' + dir_b
		file_o = dir_o + '/' + fname
		url = "http://10.60.0.159/" + dir_b + "/" + fname
		
		img = Image.open(file)

		(width, height) = img.size

		try:
			cmd = "mkdir -p " + dir_o
			retn=call(cmd,shell=True)
		except: 
			print "mkdir err"

		if os.path.isfile(file_o):
			os.system('rm -f ' + file_o)

		shutil.copy(file,file_o)
		unit = {"type" : "image", "value":url, "width":width, "height":height }
		self._data_push(unit)
		return
		

	def _create_pic(self,val,atype):

		pic = "/home/work/wzj/tmpfile/vertAlign/"
		url = "http://10.60.0.159/vertAlign/"
		cmd = "mkdir -p /home/work/wzj/tmpfile/vertAlign/"
		retn=call(cmd,shell=True)
		if atype == 2:
			pic += "sub_" + val.encode('utf8') + ".gif"
			url += "sub_" + val.encode('utf8') + ".gif"
		elif atype == 3:
			pic += "up_" + val.encode('utf8') + ".gif"
			url += "up_" + val.encode('utf8') + ".gif"


		if pic in gl.vertAlignSet:
		
			try:
				img = Image.open(pic)
			except:
				print "_create_pic : openfileNG  pic: " + pic

			(width, height) = img.size
			return {'url':url, 'w':width, 'h':height}

		w = 10 * len(val)
		len1 = len(val)
		len2 = len(val.encode('utf8'))
		if len2 / len1 == 3:
			w = 15 * len1
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
		return {'url':url, 'w':w, 'h':h}
