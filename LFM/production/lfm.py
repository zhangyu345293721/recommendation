# -*-coding:utf8-*-
"""
author:zhangyu
训练LFM模型
email:zhangyuyu417@gmail.com
"""

import numpy as np
import sys

sys.path.append("../util")
import LFM.util.read as read
import operator


def lfm_train(train_data, F, alpha, beta, step):
    """
    Args:
        train_data: 训练LFM模型的数据
        F: 用户向量长, 物品向量长
        alpha:规律因子
        beta: 学习率
        step: 迭代数
    Return:
        dict: key itemid, value:np.ndarray
        dict: key userid, value:np.ndarray
    """
    user_vec = {}
    item_vec = {}
    for step_index in range(step):
        for data_instance in train_data:
            userid, itemid, label = data_instance
            if userid not in user_vec:
                user_vec[userid] = init_model(F)
            if itemid not in item_vec:
                item_vec[itemid] = init_model(F)
            delta = label - model_predict(user_vec[userid], item_vec[itemid])  # 视频讲解中此处代码有误，应该每个样本都更新
            for index in range(F):
                user_vec[userid][index] += beta * (delta * item_vec[itemid][index] - alpha * user_vec[userid][index])
                item_vec[itemid][index] += beta * (delta * user_vec[userid][index] - alpha * item_vec[itemid][index])
        beta = beta * 0.9
    return user_vec, item_vec


def init_model(vector_len):
    """
    Args:
        vector_len: 向量长度
    Return:
         ndarray
    """
    return np.random.randn(vector_len)


def model_predict(user_vector, item_vector):
    """
    user_vector and item_vector distance
    Args:
        user_vector: 用户向量
        item_vector: 物品向量
    Return:
         num
    """
    res = np.dot(user_vector, item_vector) / (np.linalg.norm(user_vector) * np.linalg.norm(item_vector))
    return res


def model_train_process():
    """
        测试lfm模型
    """
    train_data = read.get_train_data("../data/ratings.txt")
    user_vec, item_vec = lfm_train(train_data, 50, 0.01, 0.1, 50)
    for userid in user_vec:
        recom_result = give_recom_result(user_vec, item_vec, userid)
        # ana_recom_result(train_data, userid, recom_result)


def give_recom_result(user_vec, item_vec, userid):
    """
        用LFM模型获取固定结果
    Args:
        user_vec: LFM模型结果
        item_vec: LFM模型结果
        userid: 固定用户id
    Return:
        list:[(itemid, score), (itemid1, score1)]
    """
    fix_num = 10
    if userid not in user_vec:
        return []
    record = {}
    recom_list = []
    user_vector = user_vec[userid]
    for itemid in item_vec:
        item_vector = item_vec[itemid]
        res = np.dot(user_vector, item_vector) / (np.linalg.norm(user_vector) * np.linalg.norm(item_vector))
        record[itemid] = res
    for zuhe in sorted(record.iteritems(), key=operator.itemgetter(1), reverse=True)[:fix_num]:
        itemid = zuhe[0]
        score = round(zuhe[1], 3)
        recom_list.append((itemid, score))
    return recom_list


def ana_recom_result(train_data, userid, recom_list):
    """
        测试结果
    Args:
        train_data: 测试模型
        userid:固定用户id
        recom_list: 模型推荐结果
    """
    item_info = read.get_item_info("../data/movies.txt")
    for data_instance in train_data:
        tmp_userid, itemid, label = data_instance
        if tmp_userid == userid and label == 1:
            print(item_info[itemid])
    print("recom result")
    for zuhe in recom_list:
        print(item_info[zuhe[0]])


if __name__ == "__main__":
    model_train_process()
