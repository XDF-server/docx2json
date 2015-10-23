#! *-* coding:utf-8 *-*

import glob
import sys

###题号
oldid = 0

###规则字典
rulelist = []

###习题json字串
question={'tag':'','body':[],'options':[],'answer':[],'analysis':[]}
answer_sub={'index':0,'group':[]}

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

###填空题空数
b_num = 0

###题型
#q_type="选择题" ###结构1
#q_type="多选题" ###结构1
#q_type="单项选择" ###结构1
#q_type="不定项选择题" ###结构1
#q_type="判断题" ###结构2
#q_type="简答题" ###结构3
#q_type="解答题" ###结构3
#q_type="计算题" ###结构3
#q_type="论述题" ###结构3
#q_type="翻译题" ###结构3
#q_type="材料题" ###结构3
#q_type="论证题" ###结构3
#q_type="论述题" ###结构3
#q_type="辨析题" ###结构3
#q_type="信息综合题" ###结构3
q_type="填空题" ###结构4
#q_type="词汇运用" ###结构4
#q_type="句型转换" ###结构4
#q_type="填空型完形填空" ###结构4
#q_type="填空型阅读理解" ###结构4
#q_type="写作题" ###结构11
#q_type="书面表达" ###结构11

if q_type=="写作题" or q_type=="书面表达":
	question.clear()
	question={'tag':'','interpret':[],'model_essay':[],'answer':[],'analysis':[]}

q_type_l=q_type
if q_type=="选择题" or q_type=="单项选择" or q_type=="多选题" or q_type=="不定项选择题":
    q_type_l="选择题"
elif q_type=="简答题" or q_type=="解答题":
    q_type_l="简答题"


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
###10:多空格
###11:text NoneType
###12:图片异常
###13:TypeChange.wmf2svg NG
###14:判断题非常规
###15:题目不完整
###16:子题类型非基础题
###17:题目格式异常
###18:<m:oMath>
###19:<w:sym>
###20html也无法解析的东西,符号:-
###21运营提出有问题的填空题
###22空与答案数不一致
excep=0

###角标集
vertAlignlist = glob.glob("/home/work/wzj/tmpfile_f/vertAlign/*.png")
#vertAlignlist = glob.glob("/home/work/wzj/tmpfile/vertAlign/*.png")
#vertAlignlist = glob.glob("/home/work/wzj/tmpfile/vertAlign/*.gif")
vertAlignSet = set(vertAlignlist)
