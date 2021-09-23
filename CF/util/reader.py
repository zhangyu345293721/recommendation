# -*-coding:utf8-*-
"""
读取文件
author:zhangyu
"""
import os
from typing import Tuple, Dict


def get_user_click(rating_file: str) -> Dict:
    """
        获取用户点击链表
    Args:
        rating_file:点击率文件
    Return:
        字典
    """
    if not os.path.exists(rating_file):
        return {}, {}
    fp = open(rating_file)
    num = 0
    user_click = {}
    user_click_time = {}
    for line in fp:
        if num == 0:
            num += 1
            continue
        item = line.strip().split(',')
        if len(item) < 4:
            continue
        [user_id, item_id, rating, timestamp] = item
        if user_id + "_" + item_id not in user_click_time:
            user_click_time[user_id + "_" + item_id] = int(timestamp)
        if float(rating) < 3.0:
            continue
        if user_id not in user_click:
            user_click[user_id] = []
        user_click[user_id].append(item_id)
    fp.close()
    return user_click, user_click_time


def get_item_info(item_file: str) -> Tuple[Dict, Dict]:
    """
        通过文件获取点击率
    Args:
        item_file:输入文件
    Return:
        Tuple[Dict,Dict]
    """
    if not os.path.exists(item_file):
        return {}
    line_num = 0
    item_info = {}
    fp = open(item_file)
    for line in fp:
        if line_num == 0:
            line_num += 1
            continue
        item = line.strip().split(',')
        if len(item) < 3:
            continue
        if len(item) == 3:
            [item_id, title, genres] = item
        elif len(item) > 3:
            item_id = item[0]
            genres = item[-1]
            title = ",".join(item[1:-1])
        if item_id not in item_info:
            item_info[item_id] = [title, genres]
    fp.close()
    return item_info


if __name__ == "__main__":
    item_info = get_item_info("../data/movies.txt")
    print(item_info)
    d = get_user_click('../data/ratings.txt')
    print(d)
