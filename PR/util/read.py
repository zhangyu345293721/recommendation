# -*-coding:utf8-*-
"""
从用户数据中得到图
author:zhangyu
email:zhangyuyu417@gmail.com

"""

import os


def get_graph_from_data(input_file: str):
    """
    Args:
        input_file:输入文件
    Return:
         字典
    """
    if not os.path.exists(input_file):
        return {}
    graph = {}
    line_num = 0
    score_thr = 4.0
    fp = open(input_file)
    for line in fp:
        if line_num == 0:
            line_num += 1
            continue
        item = line.strip().split(",")
        if len(item) < 3:
            continue
        user_id, item_id, rating = item[0], "item_" + item[1], item[2]
        if float(rating) < score_thr:
            continue
        if user_id not in graph:
            graph[user_id] = {}
        graph[user_id][item_id] = 1
        if item_id not in graph:
            graph[item_id] = {}
        graph[item_id][user_id] = 1
    fp.close()
    return graph


def get_item_info(input_file):
    """
        获取物品的信息
    Args:
        input_file:输入文件
    Return:
        字典
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
