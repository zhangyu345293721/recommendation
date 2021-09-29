"""
author:zhangyu
email:zhangyuyu417@gmail.com
description:训练LFM模型
"""
from typing import List, Tuple, Dict

import numpy as np
import sys

sys.path.append("../util")
import LFM.util.read as read
import operator
import time

user_file_path = "../data/ratings.txt"
item_file_path = "../data/movies.txt"


def lfm_train(train_data: List[List[object]], F: int, alpha: float, beta: float, step: int) -> Tuple[Dict, Dict]:
    """
    Args:
        train_data: 训练LFM模型的数据
        F: 用户向量长, 物品向量长
        alpha:规律因子
        beta: 学习率
        step: 迭代数
    Return:
        dict: key item_id, value:np.ndarray
        dict: key user_id, value:np.ndarray
    """
    user_vec = {}
    item_vec = {}
    for step_index in range(step):
        for data_instance in train_data:
            user_id, item_id, label = data_instance
            if user_id not in user_vec:
                user_vec[user_id] = init_model(F)
            if item_id not in item_vec:
                item_vec[item_id] = init_model(F)
            delta = label - model_predict(user_vec[user_id], item_vec[item_id])
            for index in range(F):
                user_vec[user_id][index] += beta * (delta * item_vec[item_id][index] - alpha * user_vec[user_id][index])
                item_vec[item_id][index] += beta * (delta * user_vec[user_id][index] - alpha * item_vec[item_id][index])
        beta = beta * 0.9
    return user_vec, item_vec


def init_model(vector_len: int) -> np.ndarray:
    """
    Args:
        vector_len: 向量长度
    Return:
         ndarray
    """
    return np.random.randn(vector_len)


def model_predict(user_vector: Dict, item_vector: Dict) -> float:
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


def model_train_process() -> List[List[str]]:
    """
        latent factor model模型
    """
    train_data = read.get_train_data(user_file_path)
    user_vec, item_vec = lfm_train(train_data, 50, 0.01, 0.1, 50)
    res = {}
    for user_id in user_vec:
        recom_result = give_recom_result(user_vec, item_vec, user_id)
        temp_res = ana_recom_result(train_data, user_id, recom_result)
        res[user_id] = temp_res
    return res


def give_recom_result(user_vec: List[str], item_vec: List[str], user_id: str) -> List[Tuple]:
    """
        用LFM模型获取固定结果
    Args:
        user_vec: LFM模型结果
        item_vec: LFM模型结果
        user_id: 固定用户id
    Return:
        list:[(item_id, score), (item_id1, score1)]
    """
    fix_num = 10
    if user_id not in user_vec:
        return []
    record = {}
    recom_list = []
    user_vector = user_vec[user_id]
    for item_id in item_vec:
        item_vector = item_vec[item_id]
        res = np.dot(user_vector, item_vector) / (np.linalg.norm(user_vector) * np.linalg.norm(item_vector))
        record[item_id] = res
    for item in sorted(record.items(), key=operator.itemgetter(1), reverse=True)[:fix_num]:
        item_id = item[0]
        score = round(item[1], 3)
        recom_list.append((item_id, score))
    return recom_list


def ana_recom_result(train_data: List[List[object]], user_id: str, recom_list: List[List[str]]) -> List[List[str]]:
    """
        测试结果
    Args:
        train_data: 测试模型
        user_id:固定用户id
        recom_list: 模型推荐结果
    Return:
        结果List
    """
    result = []
    item_info = read.get_item_info(item_file_path)
    # for data_instance in train_data:
    #     tmp_user_id, item_id, label = data_instance
    #     if tmp_user_id == user_id and label == 1:
    #         pass
    #         # print(item_info[item_id])
    #         # result.append(item_info[item_id])
    # print("recom result")
    for recom in recom_list:
        item_id = recom[0]
        result.append(item_info[item_id][0])
    return result


if __name__ == "__main__":
    # print(type(np.random.randn(10)))
    start_time = time.time()
    res = model_train_process()
    for r in res:
        print(r, res[r][-3:])
    end_time = time.time()
    print(f"程序总运行时间: {end_time - start_time} s")
