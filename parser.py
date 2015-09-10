#!/usr/bin/env python
# encoding: utf-8
import gl
import re
from lxml import etree
import json

class Parser(object):
    
    def __init__(self):
        self.reset()

    
    def reset(self):
        self.doc_root = None
        self.pic_rel_root = None
        self.doc_nsmap = { }
        self.pic_rel_map = { }
        self.last_text = None
        self.parse_num = 0
        self.paragraph_num = 0
        self.vertAlign = 0
        self.style = 0
        self.align = 0
        self.picflg = 0
        self.w = 0
        self.h = 0
        self.x = 0.0
        self.xl = 0.0
        self.y = 0.0
        self.yl =0.0

    
    def set_document_xml(self, document_xml):
        self.doc_root = etree.fromstring(document_xml)
        self.doc_nsmap = self.doc_root.nsmap

    
    def set_pic_rel_xml(self, pic_rel_xml):
        self.pic_rel_root = etree.fromstring(pic_rel_xml)
        self.pic_ns = self.pic_rel_root.nsmap[None]
        self._pic_relation()

    
    def iterater(self):
        '''
            按word显示的行解析word文档
        '''
        if self.doc_root.findall('.//' + self._get_doc_path('w', 'tbl')):
            gl.excep=2
        for paragraph_node in self.doc_root.findall('.//' + self._get_doc_path('w', 'p')):
            self.paragraph_num += 1
            self.align = 0
            self.style = 0
            for doc_node in paragraph_node.iter(tag = etree.Element):
                self.doc_nsmap = doc_node.nsmap
                val = self._adapter(doc_node)
                #print etree.tostring(doc_node, pretty_print=True, encoding="UTF-8")
                if val is not None:
                    yield (doc_node, val, self.paragraph_num, self.parse_num)
                    continue
            yield (paragraph_node, '\001', self.paragraph_num, self.parse_num)
            self.parse_num = 0
        

    
    def get_last_text(self):
        return self.last_text

    
    def _adapter(self, node):
        '''
            文字
        '''
        if node.tag == self._get_doc_path('w', 't'):
            text = node.text
            if text is None:
                gl.excep = 11
                return ""
            self.last_text = text
            self.parse_num += 1
            if self.style == 2:
                self.style = 0
                text = '\007' + text + '\007'

            if self.style == 4:
                self.style = 0
                text = '\004' + text + '\004'

            if self.style == 16:
                self.style = 0
                text = '\016' + text + '\016'

            if self.style == 32:
                self.style = 0
                text = '\032' + text + '\032'

            if self.style == 64:
                self.style = 0
                text = '\014' + text + '\014'

            if self.vertAlign == 2:
                self.vertAlign = 0
	        text = text.replace('\007','\010')
                text = '\002' + text + '\002'
            elif self.vertAlign == 3:
                self.vertAlign = 0
	        text = text.replace('\007','\010')
                text = '\003' + text + '\003'

            if self.align == 3:
                text = '\013' + text + '\013'
            elif self.align == 2:
                text = '\012' + text + '\012'

            return text

        '''
            图片
        '''
        if node.tag == self._get_doc_path('v', 'imagedata'):
            cropleft = 0
            cropright = 0
            croptop = 0
            cropbottom = 0
            if node.attrib.has_key('cropleft'):
                if re.search(r'f',node.attrib['cropleft']):
                    cropleft = float(filter(str.isdigit,node.attrib['cropleft']))/65536
                elif re.search(r'%',node.attrib['cropleft']):
                    cropleft = float(filter(str.isdigit,node.attrib['cropleft']))/100
                else:
                    cropleft = float(node.attrib['cropleft'])
                self.xl = cropleft
            if node.attrib.has_key('cropright'):
                if re.search(r'f',node.attrib['cropright']):
                    cropright = float(filter(str.isdigit,node.attrib['cropright']))/65536
                elif re.search(r'%',node.attrib['cropright']):
                    cropright = float(filter(str.isdigit,node.attrib['cropright']))/100
                else:
                    cropright = float(node.attrib['cropright'])
                self.x = 1 - cropright - cropleft
            if node.attrib.has_key('croptop'):
                if re.search(r'f',node.attrib['croptop']):
                    croptop = float(filter(str.isdigit,node.attrib['croptop']))/65536
                elif re.search(r'%',node.attrib['croptop']):
                    croptop = float(filter(str.isdigit,node.attrib['croptop']))/100
                else:
                    croptop = float(node.attrib['croptop'])
                self.yl = croptop
            if node.attrib.has_key('cropbottom'):
                if re.search(r'f',node.attrib['cropbottom']):
                    cropbottom = float(filter(str.isdigit,node.attrib['cropbottom']))/65536
                elif re.search(r'%',node.attrib['cropbottom']):
                    cropbottom = float(filter(str.isdigit,node.attrib['cropbottom']))/100
                else:
                    cropbottom = float(node.attrib['cropbottom'])
                self.y = 1 - cropbottom - croptop
            path = self._get_doc_path('r', 'id')
            picid = node.get(path)
            self.parse_num += 1
            #print "#####imagedata#######"
            str_pos = 'x:' + str(self.x) + ';xl:' + str(self.xl) + ';y:' + str(self.y) + ';yl:' + str(self.yl)
            if self.picflg:
                if picid is None:
                    gl.excep = 12
                    return ''
                else:
                    return ' ' + str_pos + ' ' + self.pic_rel_map[picid] + '\006'
            else:
                return ""
        '''
            imagedata 图片大小
        '''
        if node.tag == self._get_doc_path('v', 'shape') and gl.excep!=6:
            print "####006image" + str(gl.excep)
            if node.attrib.has_key('style'):
                print node.attrib['style']
                w=0
                y=0
                p=re.search(r'width:([0-9.]+)(pt|px|in|;)',node.attrib['style'])
                if p.group(1):
                    if p.group(2) == "in":
                        w=int(round(float(p.group(1)) * 72))
                    else:
                        w=int(round(float(p.group(1))))
                p=re.search(r'height:([0-9.]+)(pt|px|in|;|$)',node.attrib['style'])
                if p.group(1):
                    if p.group(2) == "in":
                        h=int(round(float(p.group(1)) * 72 ))
                    else:
                        h=int(round(float(p.group(1))))
                self.picflg=1
                return '\006image ' + str(w) + ' ' + str(h)
        '''
            题目分割
        '''
        if node.tag == self._get_doc_path('w', 'bottom'):
            self.paragraph_num = 0
            self.parse_num = 0
            return '\005'
        '''
            公式图片
        '''
        if node.tag == self._get_doc_path('a', 'blip'):
            path = self._get_doc_path('r', 'embed')
            picid = node.get(path)
            self.parse_num += 1
            self.picflg=1
            if picid is None:
                gl.excep = 12
                return ''
            else:
                return '\006embed ' + self.pic_rel_map[picid] + ' '
        '''
            embed 图片偏移
        '''
        if node.tag == self._get_doc_path('a', 'srcRect'):
            cropleft = 0
            cropright = 0
            croptop = 0
            cropbottom = 0
            if node.attrib.has_key('l'):
                cropleft = float(node.attrib['l'])/100000
                self.xl = cropleft
            if node.attrib.has_key('r'):
                cropright = float(node.attrib['r'])/100000
                self.x = 1 - cropright - cropleft
            if node.attrib.has_key('t'):
                croptop = float(node.attrib['t'])/100000
                self.yl = croptop
            if node.attrib.has_key('b'):
                cropbottom = float(node.attrib['b'])/100000
                self.y = 1 - cropbottom - croptop
        '''
            embed 图片大小
        '''
        if node.tag == self._get_doc_path('a', 'ext'):
            if node.attrib.has_key('cx'):
                #print "#################"
                w = int(node.attrib['cx'])/12700
                h = int(node.attrib['cy'])/12700
                str_pos = 'x:' + str(self.x) + ';xl:' + str(self.xl) + ';y:' + str(self.y) + ';yl:' + str(self.yl)
                if self.picflg:
                    return str_pos + ' ' + str(w) + ' ' + str(h) + '\006'
                else:
                    return ""
        '''
            角标
        '''
        if node.tag == self._get_doc_path('w', 'vertAlign'):
            path = self._get_doc_path('w', 'val')
            align_type = node.get(path)
            self.parse_num += 1
            if 'subscript' == align_type:
                self.vertAlign = 2
            if 'superscript' == align_type:
                self.vertAlign = 3
        '''
            斜体
        '''
        if node.tag == self._get_doc_path('w', 'i'):
            if self.style == 64:
                self.style = 66
            else:
                self.style = 2
        '''
            下划线
        '''
        if node.tag == self._get_doc_path('w', 'u'):
            path = self._get_doc_path('w', 'val')
            style_type = node.get(path)
            if 'single' == style_type:
		if self.style == 64:
                    self.style = 68
                else:
                    self.style = 4
        '''
            下标点
        '''
        if node.tag == self._get_doc_path('w', 'em'):
            path = self._get_doc_path('w', 'val')
            style_type = node.get(path)
            if 'dot' == style_type or 'underDot' == style_type:
		if self.style == 64:
                    self.style = 80
                else:
                    self.style = 16
        '''
            方框
        '''
        if node.tag == self._get_doc_path('w', 'bdr'):
            path = self._get_doc_path('w', 'val')
            style_type = node.get(path)
            if 'single' == style_type:
                self.style = 32
        '''
            缩进
        '''
        if node.tag == self._get_doc_path('w', 'ind'):
            self.style = 64
        '''
            行位置:居左 1 居中 2 居右 3
        '''
        if node.tag == self._get_doc_path('w', 'jc'):
            path = self._get_doc_path('w', 'val')
            style_type = node.get(path)
            if 'right' == style_type:
                self.align = 3
            elif 'center' == style_type:
                self.align = 2
        '''
            特殊字体初始化
        '''
        if node.tag == self._get_doc_path('w', 'r'):
            if self.style > 64:
                self.style = 64
            elif self.style != 64:
                self.style = 0
            self.vertAlign = 0
            self.w = 0
            self.h = 0
            self.x = 0.0
            self.xl = 0.0
            self.y = 0.0
            self.yl =0.0
            self.picflg =0
        if node.tag == self._get_doc_path('w', 'numPr'):
            gl.excep=3
        if node.tag == self._get_doc_path('w', 'fldChar'):
            gl.excep=4
        if node.tag == self._get_doc_path('v', 'textbox'):
            gl.excep=6
        if node.tag == self._get_doc_path('mc', 'AlternateContent'):
            gl.excep=8

    
    def _pic_relation(self):
        for pic_rel_node in self.pic_rel_root.iter(tag = etree.Element):
            if pic_rel_node.tag == self._get_pic_path('Relationship'):
                self.pic_rel_map[pic_rel_node.get('Id')] = pic_rel_node.get('Target')
                continue

    
    def _get_pic_path(self, tag):
        return '{%s}%s' % (self.pic_ns, tag)

    
    def _get_doc_path(self, namespace, tag):
        if self.doc_nsmap.has_key(namespace):
            return '{%s}%s' % (self.doc_nsmap[namespace], tag)
            

    
    def _pic_relation(self):
        for pic_rel_node in self.pic_rel_root.iter(tag = etree.Element):
            if pic_rel_node.tag == self._get_pic_path('Relationship'):
                self.pic_rel_map[pic_rel_node.get('Id')] = pic_rel_node.get('Target')
                continue

    
    def _get_pic_path(self, tag):
        return '{%s}%s' % (self.pic_ns, tag)

    
    def _get_doc_path(self, namespace, tag):
        if self.doc_nsmap.has_key(namespace):
            return '{%s}%s' % (self.doc_nsmap[namespace], tag)
