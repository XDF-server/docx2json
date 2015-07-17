# *-* coding:utf-8 *-*

import urllib2
from qiniu import Auth
from qiniu import BucketManager

access_key = '3U3R4V_FY_xWfoMYPANcyP5VZ2jhsj7p1ymYlMCT'
secret_key = '40ajDfBPH-l7KaDbk0xmyffxV1dX4aS6UKYZGnaY'
bucket_prex = 'fs-'

q = Auth(access_key,secret_key)
bucket = BucketManager(q)

class Qiniu(object):

	@staticmethod	
	def download_pub_file(bucket_name,key,path='.'):
		base_url = 'http://%s.okjiaoyu.cn/%s' % (bucket_name,key)
		request = urllib2.Request(base_url)
		response = urllib2.urlopen(request)
		pic = response.read()

		with open(path + '/' + key,'wb') as fd:
			fd.write(pic)

		return response.code

	@staticmethod
	def download_pri_file(bucket_name,key):
		base_url = 'http://%s.okjiaoyu.cn/%s' % (bucket_name,key)
		private_url = q.private_download_url(base_url,expires = 3600)
		request = urllib2.Request(base_url)
		response = urllib2.urlopen(request)
		pic = response.read()

		with open(path + '/' + key,'wb') as fd:
			fd.write(pic)

		return response.code

	@staticmethod
	def get_file_info(bucket_name,key):
		bucket_name = bucket_prex + bucket_name
		ret, info = bucket.stat(bucket_name, key)
		return info 

	@staticmethod 
	def copy_file(frm_bucket_name,frm_key,to_bucket_name,to_key):
		frm_bucket_name = bucket_prex + frm_bucket_name
		to_bucket_name = bucket_prex + to_bucket_name
		ret, info = bucket.copy(frm_bucket_name, frm_key, to_bucket_name, to_key)
		return ret

	@staticmethod 
	def move_file(frm_bucket_name,frm_key,to_bucket_name,to_key):
		frm_bucket_name = bucket_prex + frm_bucket_name
		to_bucket_name = bucket_prex + to_bucket_name
		ret, info = bucket.move(frm_bucket_name, frm_key, to_bucket_name, to_key2)
		return ret

	@staticmethod
	def del_file(bucket_name,key):
		bucket_name = bucket_prex + bucket_name
		ret, info = bucket.delete(bucket_name, key)
		return ret
		

if __name__ == '__main__':
	print Qiniu.get_file_info('ap','ap_i82pBv7651.0x0.png')
	
	
