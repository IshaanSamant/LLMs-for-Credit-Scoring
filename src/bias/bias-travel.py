import pandas as pd
import numpy as np
import sklearn as sk
from aif360.metrics import BinaryLabelDatasetMetric, ClassificationMetric
from aif360.datasets import BinaryLabelDataset
from aif360.explainers import MetricTextExplainer
import random
import json
from process import predo_tra, preres_tra

'''data preprocess'''

# 每个数据的变量名
mean_list = ['target','Agency','Agency Type','Distribution Channel','Product Name',
             'Duration','Destination','Net Sales','Commission','Age']
feature_size = 10

# 原数据处理
# data中所有数据需要修改成数值格式
# todo age 和gender需要进一步划分成二分类？

train_data = pd.read_csv('./bias_data/TraIn_train.csv', sep=',', names=[i for i in range(feature_size)])
train_data = predo_tra(train_data)
train = pd.DataFrame(train_data)
train.columns = mean_list

test_data = pd.read_csv('./bias_data/TraIn_test.csv', sep=',', names=[i for i in range(feature_size)])
test_data = predo_tra(test_data)
test = pd.DataFrame(test_data)
test.columns = mean_list # 表格重新写表头

# method结果读取
# todo 标签需要转换适配各个数据集
res = preres_tra(test.values.tolist(),'our/flare_trin_desc_write_out_info.json')
res = pd.DataFrame(res)
res.columns = mean_list

'''data bias test'''
# 测试数据本身偏见性
# favorable_label 为好的数值，即无风险的代表数字
# unfavorable_label 为坏的数值
# df 为数据
# label_names 作为目标的变量名
# protected_attribute_names 需要保护的变量名，含偏见的变量名
test_data = BinaryLabelDataset(favorable_label=0, unfavorable_label=1, df=test, label_names=['target'], protected_attribute_names=['Age'])

# unprivileged_groups 弱势群体，例如{gender：1}表示弱势群体是女性，list[]内可以叠加，也可以多次使用分开算
# privileged_groups 优势群体，例如{gender：2}表示优势群体是男性，
metric = BinaryLabelDatasetMetric(test_data, unprivileged_groups=[{'Age':1}], privileged_groups=[{'Age':0}])
text_res = MetricTextExplainer(metric)

print('DI:', text_res.disparate_impact())

# unprivileged_groups 弱势群体，例如{gender：1}表示弱势群体是女性，list[]内可以叠加，也可以多次使用分开算
# privileged_groups 优势群体，例如{gender：2}表示优势群体是男性，
train_data = BinaryLabelDataset(favorable_label=0, unfavorable_label=1, df=train, label_names=['target'], protected_attribute_names=['Age'])

metric = BinaryLabelDatasetMetric(train_data, unprivileged_groups=[{'Age':1}], privileged_groups=[{'Age':0}])
text_res = MetricTextExplainer(metric)

print('DI:', text_res.disparate_impact())


'''method bias test'''
# 测试模型偏见性
# favorable_label 为好的数值，即无风险的代表数字
# unfavorable_label 为坏的数值
# df 为method输出的数据
# label_names 作为目标的变量名
# protected_attribute_names 需要保护的变量名，含偏见的变量名
res_data = BinaryLabelDataset(favorable_label=0, unfavorable_label=1, df=res, label_names=['target'], protected_attribute_names=['Age'])

metric = ClassificationMetric(test_data, res_data, unprivileged_groups=[{'Age':1}], privileged_groups=[{'Age':0}])
text_res = MetricTextExplainer(metric)

print('EOD:', text_res.equal_opportunity_difference())
print('ERR:', text_res.average_odds_difference())


print('down')