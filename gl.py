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

###题型
#q_type = "填空题"
#q_type="单项选择"
#q_type="选择题"
#q_type="判断题"
q_type="简答题"
#q_type="解答题"

q_type_l=q_type
if q_type=="选择题" or q_type=="单项选择":
    q_type_l="选择题"
elif q_type=="简答题" or q_type=="解答题":
    q_type_l="简答题"


###异常flg 不入库
###1:emf
###2:table
###3:序号 numPr
###4:word公式
###5:复合题
excep=0

###角标集
vertAlignlist = glob.glob("/home/work/wzj/tmpfile/vertAlign/*.png")
#vertAlignlist = glob.glob("/home/work/wzj/tmpfile/vertAlign/*.gif")
vertAlignSet = set(vertAlignlist)
