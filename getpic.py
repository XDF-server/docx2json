#!/usr/local/bin/python2.7

import re
def extract_image(filename):
	'''
    extract images from .doc file, may be useful in other unzip files also
    gif:gif v87
        start tag : GIF87a
        end tag   : x3B
        output ext: gif
        re string : (GIF87a.+?\x3B)
    gif:gif v89
        start tag : GIF89a
        end tag   : x3B
        output ext: gif
        re string : (GIF89a.+?\x3B)
    png:
        start tag : \x89\x50\x4E\x47\x0D\x0A\x1A\x0A
        end tag   : \x00\x00\x00\x00\x49\x45\x4E\x44\xAE\x42\x60\x82
        output ext: png
        re string : (\x89\x50\x4E\x47\x0D\x0A\x1A\x0A.+?\x00\x00\x00\x00\x49\x45\x4E\x44\xAE\x42\x60\x82)
    jpg:
        start tag : \xFF\xD8
        end tag   : \xFF\xD9
        output ext: jpg
        re string : (\xFF\xD8.+?\xFF\xD8.+?\xFF\xD9.+?\xFF\xD9)   #jpg file has a content start with \xff\xd8 and end with \xff\xd9, so we should match 2 times
	'''
	file_format = {
		'gifv87':{'start':'GIF87a', 'end':'\x3B', 'ext':'gif','regstr':'(GIF87a.+?\x3B)'},
		'gifv89':{'start':'GIF89a', 'end':'\x3B', 'ext':'gif','regstr':'(GIF89a.+?\x3B)'},
		'png':{'start':'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A', 'end':'\x00\x00\x00\x00\x49\x45\x4E\x44\xAE\x42\x60\x82', 'ext':'png','regstr':'(\x89\x50\x4E\x47\x0D\x0A\x1A\x0A.+?\x00\x00\x00\x00\x49\x45\x4E\x44\xAE\x42\x60\x82)'},
		'jpg':{'start':'\xFF\xD8', 'end':'\xFF\xD9', 'ext':'jpg','regstr':'(\xFF\xD8.+?\xFF\xD8.+?\xFF\xD9.+?\xFF\xD9)'},
	}

	with open(filename, 'rb') as f:
		data = f.read()
		for x in file_format.keys():
			reg = file_format[x]['regstr'] #use re str
			p = re.compile(reg, re.S)
			rs = p.findall(data)
			for i in range(len(rs)):
				print "OK"
				with open('./file' + str(i) + '.' + file_format[x]['ext'], 'wb') as w:
					w.write(rs[i])

if __name__ == '__main__':
	filename = r'/home/wzj/docx/qd_hKEtYl2075.docx'
	extract_image(filename)
