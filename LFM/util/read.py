"""
工具类
author:zhangyu
email:zhangyuyu417@gmail.com
description:处理统计数据
"""

import os
from typing import List, Dict
import json


def get_item_info(input_file: str) -> Dict:
    """
        获取商品信息
    Args:
        input_file:输入文件
    Return:
       商品信息字典
    """
    if not os.path.exists(input_file):
        return {}
    item_info = {}
    line_num = 0
    fp = open(input_file)
    for line in fp:
        if line_num == 0:
            line_num += 1
            continue
        item = line.strip().split(',')
        if len(item) < 3:
            continue
        elif len(item) == 3:
            item_id, title, genre = item[0], item[1], item[2]
        elif len(item) > 3:
            item_id = item[0]
            genre = item[-1]
            title = ",".join(item[1:-1])
        item_info[item_id] = [title, genre]
    fp.close()
    return item_info


def get_ave_score(input_file: str) -> Dict:
    """
        获取点击率分数
    Args:
        input_file:输入文件
    Return:
        商品id和点击次数Dict
    """
    if not os.path.exists(input_file):
        return {}
    line_num = 0
    record_dict = {}
    score_dict = {}
    fp = open(input_file)
    for line in fp:
        if line_num == 0:
            line_num += 1
            continue
        item = line.strip().split(',')
        if len(item) < 4:
            continue
        user_id, item_id, rating = item[0], item[1], float(item[2])
        if item_id not in record_dict:
            record_dict[item_id] = [0, 0]
        record_dict[item_id][0] += 1
        record_dict[item_id][1] += rating
    fp.close()
    for item_id in record_dict:
        score_dict[item_id] = round(record_dict[item_id][1] / record_dict[item_id][0], 3)
    return score_dict


def get_train_data(input_file: str) -> List[int]:
    """
        训练LFM模型
    Args:
        input_file:输入文件
    Return:
        链表
    """
    if not os.path.exists(input_file):
        return []
    score_dict = get_ave_score(input_file)
    neg_dict = {}
    pos_dict = {}
    train_data = []
    line_num = 0
    score_thr = 4.0
    fp = open(input_file)
    for line in fp:
        if line_num == 0:
            line_num += 1
            continue
        item = line.strip().split(',')
        if len(item) < 4:
            continue
        user_id, item_id, rating = item[0], item[1], float(item[2])
        if user_id not in pos_dict:
            pos_dict[user_id] = []
        if user_id not in neg_dict:
            neg_dict[user_id] = []
        if rating >= score_thr:
            pos_dict[user_id].append((item_id, 1))
        else:
            score = score_dict.get(item_id, 0)
            neg_dict[user_id].append((item_id, score))
    fp.close()
    for user_id in pos_dict:
        data_num = min(len(pos_dict[user_id]), len(neg_dict.get(user_id, [])))
        if data_num > 0:
            train_data += [(user_id, zuhe[0], zuhe[1]) for zuhe in pos_dict[user_id]][:data_num]
        else:
            continue
        sorted_neg_list = sorted(neg_dict[user_id], key=lambda element: element[1], reverse=True)[:data_num]
        train_data += [(user_id, zuhe[0], 0) for zuhe in sorted_neg_list]
    return train_data


if __name__ == '__main__':
    user_file_path = "../data/ratings.txt"
    item_file_path = "../data/movies.txt"
    item_info = get_item_info(item_file_path)
    score_info = get_train_data(user_file_path)
    # print(item_info)
    # print(score_info)
    # s = json.dumps(score_info)
    # with open('user_item.txt', 'w') as f:
    #     f.write(s)
    # with open('user_item.txt', 'r') as f:
    #     line = f.readline()
    #     o = json.loads(line)
    # print(o)
