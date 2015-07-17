# *-* coding:utf-8 *-*

from  lxml import etree
from docx import *

class Parser(object):

	def __init__(self,docxname):
		self.docx = Docx()
		self.reset(docxname)

	def reset(self,docxname):
		self.docx.open(docxname)
		document_xml = self.docx.get_xml('word/document.xml')
		self.doc_root =  etree.fromstring(document_xml)
		self.nsmap = self.doc_root.nsmap
		pic_rel_xml = self.docx.get_xml('word/_rels/document.xml.rels')
		self.pic_rel_root = etree.fromstring(pic_rel_xml)
		self.pic_ns = self.pic_rel_root.nsmap[None]
		self.pic_rel_map =  {}
		self._pic_relation()
		self.last_text = None
	
	def iterater(self):
		'''
			按word显示的行解析word文档
		'''
		for paragraph_node in self.doc_root.findall('.//' + self._get_doc_path('w','p')):

			for doc_node in paragraph_node.iter(tag = etree.Element):

				self.nsmap = doc_node.nsmap		
					
				val = self._adapter(doc_node)		

				if val is not None:
					yield(doc_node,val)
				
			yield(paragraph_node,'P')

	def get_last_text(self):
		return self.last_text
				
	def _adapter(self,node):
		'''
			文字
		'''
		if node.tag == self._get_doc_path('w','t'):		
			text = node.text
			self.last_text = text
			return text
		'''
			图片
		'''
		if node.tag == self._get_doc_path('v','imagedata'):
			path = self._get_doc_path('r','id')
			picid = node.get(path)
			return self.docx.docxname + '/word/' + self.pic_rel_map[picid]
		'''
			题目分割
		'''
		if node.tag == self._get_doc_path('w','bottom'):
			return 'BOM'
		
		'''
			公式图片
		'''
		if node.tag == self._get_doc_path('a','blip'):
			path = self._get_doc_path('r','embed')
			picid = node.get(path)
			return self.docx.docxname + '/word/' + self.pic_rel_map[picid]
		'''
			角标
		'''
		if node.tag == self._get_doc_path('w','vertAlign'):
			path = self._get_doc_path('w','val')
			align_type = node.get(path)
			
			if 'subscript' == align_type:
				return 'SUB'
			if 'superscript' == align_type:
				return 'SUP'

		return None
			
				

	def _pic_relation(self):
		for pic_rel_node in self.pic_rel_root.iter(tag = etree.Element):
			if pic_rel_node.tag == self._get_pic_path('Relationship'):				
				self.pic_rel_map[pic_rel_node.get('Id')] = pic_rel_node.get('Target')

	def _get_pic_path(self,tag):
		return '{%s}%s' % (self.pic_ns,tag)

	def _get_doc_path(self,namespace,tag):
		if self.nsmap.has_key(namespace):
			return '{%s}%s' % (self.nsmap[namespace],tag)
	

	
		
		
		
