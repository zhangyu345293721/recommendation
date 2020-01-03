# -*-coding:utf8-*-
"""
    测试gdbt模型
    author:zhangyu
"""
from __future__ import division
import numpy as np
import Tree.xgboost as xgb
import Tree.train as TA
from scipy.sparse import csc_matrix
import math
import sys


def get_test_data(test_file, feature_num_file):
    """
    Args:
        test_file:测试文件
        feature_num_file: 特征数量文件
    Return:
         数组
    """
    total_feature_num = 103
    test_label = np.genfromtxt(test_file, dtype=np.float32, delimiter=",", usecols=-1)
    feature_list = range(total_feature_num)
    test_feature = np.genfromtxt(test_file, dtype=np.float32, delimiter=",", usecols=feature_list)
    return test_feature, test_label


def predict_by_tree(test_feature, tree_model):
    """
        通过gbdt模型预测
    """
    predict_list = tree_model.predict(xgb.DMatrix(test_feature))
    return predict_list


def predict_by_lr_gbdt(test_feature, mix_tree_model, mix_lr_coef, tree_info):
    """
        通过混合模型预测
    """
    tree_leaf = mix_tree_model.predict(xgb.DMatrix(test_feature), pred_leaf=True)
    (tree_depth, tree_num, step_size) = tree_info
    total_feature_list = TA.get_gbdt_and_lr_feature(tree_leaf, tree_depth=tree_depth, tree_num=tree_num)
    result_list = np.dot(csc_matrix(mix_lr_coef), total_feature_list.tocsc().T).toarray()[0]
    sigmoid_ufunc = np.frompyfunc(sigmoid, 1, 1)
    return sigmoid_ufunc(result_list)


def sigmoid(x):
    """
        sigmoid方法
    """
    return 1 / (1 + math.exp(-x))


def get_auc(predict_list, test_label):
    """
    Args:
        predict_list: 预测分数链表
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


def get_accuary(predict_list, test_label):
    """
    Args:
        predict_list:预测链表
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
    accuary_score = right_num / total_num
    print("accuary:%.5f" % (accuary_score))


def run_check_core(test_feature, test_label, model, score_func):
    """
    Args:
        test_feature:测试特征
        test_label:测试模型
        model: tree model
        score_func: 使用不同的模型测试
    """
    predict_list = score_func(test_feature, model)
    get_auc(predict_list, test_label)
    get_accuary(predict_list, test_label)


def run_check(test_file, tree_model_file, feature_num_file):
    """
    Args:
        test_file:测试文件
        tree_model_file:gbdt模型
        feature_num_file:特征数量文件
    """
    test_feature, test_label = get_test_data(test_file, feature_num_file)
    tree_model = xgb.Booster(model_file=tree_model_file)
    run_check_core(test_feature, test_label, tree_model, predict_by_tree)


def run_check_lr_gbdt_core(test_feature, test_label, mix_tree_model, mix_lr_coef, tree_info, score_func):
    """
        通过混合模型测试
    Args:
        test_feature:测试特征
        test_label:测试标签
        mix_tree_model:混合数模型
        mix_lr_coef:混合lr
        tree_info:树信息
        score_func:不同分数方法
    """
    predict_list = score_func(test_feature, mix_tree_model, mix_lr_coef, tree_info)
    get_auc(predict_list, test_label)
    get_accuary(predict_list, test_label)


def run_check_lr_gbdt(test_file, tree_mix_model_file, lr_coef_mix_model_file, feature_num_file):
    """
    Args:
        test_file:测试文件
        tree_mix_model_file: 树混合模型文件
        lr_coef_mix_model_file:混合模型文件
        feature_num_file:特征数量文件
    """
    test_feature, test_label = get_test_data(test_file, feature_num_file)
    mix_tree_model = xgb.Booster(model_file=tree_mix_model_file)
    mix_lr_coef = np.genfromtxt(lr_coef_mix_model_file, dtype=np.float32, delimiter=",")
    tree_info = TA.get_mix_model_tree_info()
    run_check_lr_gbdt_core(test_feature, test_label, mix_tree_model, \
                           mix_lr_coef, tree_info, predict_by_lr_gbdt)


if __name__ == "__main__":
    if len(sys.argv) == 4:
        test_file = sys.argv[1]
        tree_model = sys.argv[2]
        feature_num_file = sys.argv[3]
        run_check(test_file, tree_model, feature_num_file)
    elif len(sys.argv) == 5:
        test_file = sys.argv[1]
        tree_mix_model = sys.argv[2]
        lr_coef_mix_model = sys.argv[3]
        feature_num_file = sys.argv[4]
        run_check_lr_gbdt(test_file, tree_mix_model, lr_coef_mix_model, feature_num_file)
    else:
        print("check gbdt model usage: python xx.py test_file  tree_model feature_num_file")
        print("check lr_gbdt model usage: python xx.py test_file tree_mix_model lr_coef_mix_model feature_num_file")
        sys.exit()
