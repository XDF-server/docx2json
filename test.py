#!/usr/local/python2.7/bin/python
# *_* coding:utf-8 *-*

import re
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )
import glob
import string
import hashlib


print "001 \001"
print "002 \002"
print "003 \003"
print "004 \004"
print "005 \005"
print "006 \006"
exit()
i = 0
i = ~i
print i
if i:
	print "OK1"
i = ~i
print i
if i:
	print "OK2"
exit()

word = wc.Dispatch('Word.Application') 
doc = word.Documents.Open('/home/work/wzj/docx/qd_hMrePG4435.docx') 
doc.SaveAs('tdir/math.html', 8 ) 
doc.Close() 
word.Quit()
exit()

filep="/home/work/wzj/docx/qd_hMrePG4435/media/image2.bin"
#filep="/home/work/wzj/docx/qd_hMrePG4435/word/embeddings/embeddedObject2.bin"
files=open(filep,'r')
row=files.readlines()
print row
for i in row:
	print i
	break
files.close()

exit()

from PIL import Image,ImageFont,ImageDraw

img=Image.open("/home/work/wzj/docx/qd_hMrePG4435/media/image.bin")
img.save('image.gif')

exit()
test="Ca\0032\003HoHoo\0022+\002\003-\003Bac\002甲\002"
test=test.decode('utf8')
#for i in test:
#	print i
test_l = re.split(r'\002|\003',test)
ns = int(len(test_l)/2)
#print ns
n = len("".join(test_l))
w = 10 * n - 4 * ns
h = 20
#bgcolor=(255,255,255,0) #背景颜色
bgcolor=(0,0,0,0) #背景颜色
fontcolor = (0,0,0) #字体颜色
font_n = ImageFont.truetype("/usr/share/fonts/simsun/simsun.ttf",20) #加载字体
font_s = ImageFont.truetype("/usr/share/fonts/simsun/simsun.ttf",10) #加载字体
img = Image.new("RGBA", (w,h), bgcolor) # 创建图形 生成背景图片
draw = ImageDraw.Draw(img) # 创建画笔 产生draw对象，draw是一些算法的集合
text = ""
sta = 0
sub_flg = 0
up_flg = 0
for i in test:
	if i == '\002':
		if sub_flg==0:
			sub_flg=1
			if text:
				draw.text((sta,0),text,font=font_n,fill=fontcolor)
				sta += len(text) * 10 + 2
				text = ""
		else:
			if text:
				draw.text((sta,10),text,font=font_s,fill=fontcolor)
				sta += len(text) * 5 + 2
				text = ""
			sub_flg=0
	elif i == '\003':
		if up_flg==0:
			up_flg=1
			if text:
				draw.text((sta,0),text,font=font_n,fill=fontcolor)
				sta += len(text) * 10 + 2
				text = ""
		else:
			if text:
				draw.text((sta,0),text,font=font_s,fill=fontcolor)
				sta += len(text) * 5 + 2
				text = ""
			up_flg=0
	else:
		text += i

del draw
#transparency = img.info['transparency'] 
#img.save('test.gif',transparency=transparency) #保存原始版本
img.convert('RGBA')
img.save('test.gif') #保存原始版本

exit()
#draw.text((0,0),test,font=font,fill=fontcolor) #画字体,(0,0)是起始位置
#del draw #释放draw
#img.convert('RGB')
#img.save('test.gif') #保存原始版本

toImage = Image.new('RGB', (100, 10),bgcolor)
for i in range(cnt):
	fname = "test" + str(i) + ".gif"
	fromImage = Image.open(fname)
	toImage.paste(fromImage,( fromImage.size[0], 10))

toImage.save('test.gif')
del toImage
exit()

import random
# 随机字母:
def rndChar():
	return chr(random.randint(65, 90))

# 随机颜色1:
def rndColor():
	return (random.randint(64, 255), random.randint(64, 255), random.randint(64, 255))

# 随机颜色2:
def rndColor2():
	return (random.randint(32, 127), random.randint(32, 127), random.randint(32, 127))

# 240 x 60:
width = 60 * 4
height = 60
image = Image.new('RGB', (width, height), (255, 255, 255))
# 创建Font对象:
font = ImageFont.truetype('/usr/share/fonts/simsun/simsun.ttf', 36)
# 创建Draw对象:
draw = ImageDraw.Draw(image)
# 填充每个像素:
for x in range(width):
	for y in range(height):
		draw.point((x, y), fill=rndColor())

for t in range(4):
	draw.text((60 * t + 10, 10), rndChar(), font=font, fill=rndColor2())

image.save('code.gif');

exit()


test="Ca\0022\002Ho\0032+\003"
w=300 #图片宽度
h=100 #图片高度
bgcolor=(255,255,255) #背景颜色
img = Image.new("RGB", (w,h), bgcolor) # 创建图形 生成背景图片
font = ImageFont.truetype("/usr/share/fonts/simsun/simsun.ttf",5) #加载字体
fontcolor = (0,0,0) #字体颜色
draw = ImageDraw.Draw(img) # 创建画笔 产生draw对象，draw是一些算法的集合
draw.text((0,0),test,font=font,fill=fontcolor) #画字体,(0,0)是起始位置
del draw #释放draw
img.convert('RGB')
img.save('test.jpg') #保存原始版本

exit()
try:
	img.save('test.jpg') #保存原始版本
except IOError:
	PIL.ImageFile.MAXBLOCK = img.size[0] * img.size[1]
	img.save('test.jpg') #保存原始版本
	

exit()

val="a．sda.asdf".decode('utf8')
p=re.match(r'([a-zA-Z])[\.．](.*)'.decode('utf8'), val)
if p:
	print p.group(1)
	print p.group(2)
else:
	print val
exit()

str="过滤后的食盐水仍含abc有可溶性的"
#str=""
str+="CaCl"
str+='\002'
str+="2\002、MgCl"
str+='\003'
str+="2\003、Na"
str+='\002'
str+="2\002SO"
str+='\002'
str+="4\002等杂质"

p=re.findall(r'(\S*?)([a-zA-Z0-9+\-\(\)（）\002\003]+|$)'.decode('utf8'), str)

print str

text = ""
for group in p:
	if re.search(r'[\002\003]',group[1]):
		text += group[0]
		print "text:" + text
		print "pic:" + group[1]
		text = ""
	else:
		text += group[0] + group[1]

if text:
	print "text:" + text


exit()

import time
import MySQLdb
import demjson
import sys

import docx 


from PIL import Image

str="asdfasfdafs"
list=str.split(':')
for i in range(1,len(list),2):
	print i
exit()


img=Image.open('/home/wzj/docx/qd_hKEtYl2075/media/image.bin')
print img.size

exit()
print docx.__file__

exit()
val=0

if val == 0:
	print "OK1"

print sys.path
exit()
class Vector:
   def __init__(self, a, b):
      self.a = a
      self.b = b

   def __str__(self):
      return 'Vector (%d, %d)' % (self.a, self.b)
   
   def __add__(self,other):
      return Vector(self.a + other.a, self.b + other.b)

v1 = Vector(2,10)
v2 = Vector(5,-2)
print v1 + v2

exit()
class Point:
	def __init( self, x=0, y=0):
		self.x = x
		self.y = y
	def __del__(self):
		class_name = self.__class__.__name__
		print class_name, "destroyed"

pt1 = Point()
pt2 = pt1
pt3 = pt1
print id(pt1), id(pt2), id(pt3) # 打印对象的id
del pt1
print "1"
print "2"
print "3"

exit()
class Employee:
	'所有员工的基类'
	empCount = 0

	def __init__(self, name, salary):
		self.name = name
		self.salary = salary
		Employee.empCount += 1
   
	def displayCount(self):
		print "Total Employee %d" % Employee.empCount

	def displayEmployee(self):
		print "Name : ", self.name,  ", Salary: ", self.salary

"创建 Employee 类的第一个对象"
emp1 = Employee("Zara", 2000)
emp2 = Employee("Manni", 5000)

setattr(emp1, 'age', 8)
setattr(emp2, 'age', 9)

emp1.displayEmployee()
emp2.displayEmployee()
print "Total Employee %d" % Employee.empCount
print "age: %d" % emp1.age
print "age: %d" % emp2.age

exit()
localtime=time.localtime(time.time())
print localtime
print localtime[0]

def fun(arg33,*value):
	"测试"
#	print arg33
	for v in value:
		print v

fun(10)
fun(22,11,12)

exit()

