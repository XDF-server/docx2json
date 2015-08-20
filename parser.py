#!/usr/bin/env python
# encoding: utf-8
import gl
from lxml import etree

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
        for paragraph_node in self.doc_root.findall('.//' + self._get_doc_path('w', 'p')):
            self.paragraph_num += 1
            self.align = 0
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
            self.last_text = text
            self.parse_num += 1
            if self.style == 4:
                self.style = 0
                text = '\004' + text + '\004'

            if self.style == 16:
                self.style = 0
                text = '\016' + text + '\016'

            if self.vertAlign == 2:
                self.vertAlign = 0
                text = '\002' + text + '\002'
            elif self.vertAlign == 3:
                self.vertAlign = 0
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
            path = self._get_doc_path('r', 'id')
            picid = node.get(path)
            self.parse_num += 1
            return '\006' + self.pic_rel_map[picid] + '\006'
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
            return '\006' + self.pic_rel_map[picid] + '\006'
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
            下划线
        '''
        if node.tag == self._get_doc_path('w', 'u'):
            path = self._get_doc_path('w', 'val')
            style_type = node.get(path)
            if 'single' == style_type:
                self.style = 4
        '''
            下标点
        '''
        if node.tag == self._get_doc_path('w', 'em'):
            path = self._get_doc_path('w', 'val')
            style_type = node.get(path)
            if 'dot' == style_type or 'underDot' == style_type:
                self.style = 16
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
            特殊字体结束判断
        '''
        if node.tag == self._get_doc_path('w', 'r'):
            if self.style != 0:
                self.style = 0
            

    
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
