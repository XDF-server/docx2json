#! *-* coding:utf-8 *-*

import glob
import sys

###题号
oldid = 0

###规则字典
rulelist = []

###习题json字串
question={'topic_type':{},'body':[],'options':[],'answer':[],'analysis':[]}
content={'material':[],'translation':[],'questions':[]}

###0:题目生成完毕 1:题目生成中
sub_status = 0

###正在生成何种类型的数据
type_status = ""
main_type_status = ""
###类型变更flg
type_change = ""
###答案选项
option_stat = ""

###空行数
blank_num = 0
###空格数
blank_cnt = 0

###题型
#q_type="单项选择"
#q_type="选择题"
#q_type="简答题"
#q_type="解答题"
#q_type="填空题"
#q_type="判断题"

q_type=""
#main_q_type="综合题"
#main_q_type="组合选择题"
#main_q_type="组合填空题"
#main_q_type="组合简答题"
#main_q_type="探究题"
#main_q_type="文言文阅读题"
main_q_type="现代文阅读题"
#main_q_type="选择型阅读理解"


#main_q_type="分析说明题"

#分析说明题	qd_hSxVNm9081.docx 需要新定义子题类型
#实验题	9005

###异常flg 不入库
###1:emf
###2:table
###3:序号 numPr
###4:word公式
###5:复合题
###6:textbox
###7:file open ng
###8:mc:AlternateContent
###9:UnicodeDecodeError
####10:多空格
###11:text NoneType
###12:图片异常
###13:TypeChange.wmf2svg NG
###14:判断题非常规
###15:题目不完整
###16:子题类型非基础题
excep=0

###角标集
vertAlignlist = glob.glob("/home/work/wzj/tmpfile_f/vertAlign/*.png")
vertAlignSet = set(vertAlignlist)
