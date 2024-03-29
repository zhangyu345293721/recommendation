# -*-coding:utf8-*-
"""
author:zhangyu
用线性模型检查文件，在测试中
email:zhangyuyu417@gmail.com

"""
from __future__ import division
import numpy as np
from sklearn.externals import joblib
import math
import sys

sys.path.append("../")
import LR.util.get_feature_num as gf


def get_test_data(test_file: str, feature_num_file: str):
    """
    Args:
        test_file:测试文件
        feature_num_file: 特征文件数量
    Return:
         二维数组
    """
    total_feature_num = gf.get_feature_num(feature_num_file)
    test_label = np.genfromtxt(test_file, dtype=np.float32, delimiter=",", usecols=-1)
    feature_list = range(total_feature_num)
    test_feature = np.genfromtxt(test_file, dtype=np.float32, delimiter=",", usecols=feature_list)
    return test_feature, test_label


def predict_by_lr_model(test_feature, lr_model):
    """
        通过逻辑回归模型
    """
    result_list = []
    prob_list = lr_model.predict_proba(test_feature)
    for index in range(len(prob_list)):
        result_list.append(prob_list[index][1])
    return result_list


def predict_by_lr_coef(test_feature, lr_coef):
    """
        通过模型预测
    """
    sigmoid_func = np.frompyfunc(sigmoid, 1, 1)
    return sigmoid_func(np.dot(test_feature, lr_coef))


def sigmoid(x):
    """
        通过sigmod函数
    """
    return 1 / (1 + math.exp(-x))


def get_auc(predict_list, test_label):
    """
    Args:
        predict_list: 预测链表
        test_label: 测试标签
        auc = (sum(pos_index)-pos_num(pos_num + 1)/2)/pos_num*neg_num
    """
    total_list = []
    for index in range(len(predict_list)):
        predict_score = predict_list[index]
        label = test_label[index]
        total_list.append((label, predict_score))
    sorted_total_list = sorted(total_list, key=lambda ele: ele[1])
    neg_num = 0
    pos_num = 0
    count = 1
    total_pos_index = 0
    for zuhe in sorted_total_list:
        label, predict_score = zuhe
        if label == 0:
            neg_num += 1
        else:
            pos_num += 1
            total_pos_index += count
        count += 1
    auc_score = (total_pos_index - (pos_num) * (pos_num + 1) / 2) / (pos_num * neg_num)
    print("auc:%.5f" % (auc_score))


def get_accuracy(predict_list, test_label):
    """
    Args:
        predict_list: 测试链表
        test_label: 测试标签
    """
    score_thr = 0.5
    right_num = 0
    for index in range(len(predict_list)):
        predict_score = predict_list[index]
        if predict_score >= score_thr:
            predict_label = 1
        else:
            predict_label = 0
        if predict_label == test_label[index]:
            right_num += 1
    total_num = len(predict_list)
    accuracy_score = right_num / total_num
    print("accuracy_score:%.5f" % (accuracy_score))


def run_check_core(test_feature, test_label, model, score_func):
    """
    Args:
        test_feature:测试特征
        test_label:测试标签
        model: lr_coef, lr_model
        score_func:分数方法
    """
    predict_list = score_func(test_feature, model)
    get_auc(predict_list, test_label)
    get_accuracy(predict_list, test_label)


def run_check(test_file, lr_coef_file, lr_model_file, feature_num_file):
    """
    Args:
        test_file: 测试文件
        lr_coef_file: w1,w2
        lr_model_file: 输出文件
        feature_num_file: 特征数量文件
    """
    test_feature, test_label = get_test_data(test_file, feature_num_file)
    lr_coef = np.genfromtxt(lr_coef_file, dtype=np.float32, delimiter=",")
    lr_model = joblib.load(lr_model_file)
    run_check_core(test_feature, test_label, lr_model, predict_by_lr_model)
    run_check_core(test_feature, test_label, lr_coef, predict_by_lr_coef)


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("usage: python xx.py test_file coef_file model_file feature_num_file")
        sys.exit()
    else:
        test_file = sys.argv[1]
        coef_file = sys.argv[2]
        model_file = sys.argv[3]
        feature_num_file = sys.argv[4]
        run_check(test_file, coef_file, model_file, feature_num_file)
