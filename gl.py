#! *-* coding:utf-8 *-*

import glob
import sys

###规则字典
rulelist = []

###习题json字串
question={'tag':'','body':[],'options':[],'answer':[],'analysis':[]}

###0:题目生成完毕 1:题目生成中
sub_status = 0

###正在生成何种类型的数据
type_status = ""
###类型变更flg
type_change = ""
###答案选项
option_stat = ""

###空行数
blank_num = 0

vertAlignlist = glob.glob("/home/work/wzj/tmpfile/vertAlign/*.gif")
vertAlignSet = set(vertAlignlist)
