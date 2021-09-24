"""
author:zhangyu
description:获取线上和线下的推荐
"""

from __future__ import division
import os
import operator
import sys
from typing import Dict

from ContentBased.util import read

sys.path.append("../")


def get_up(item_cate, input_file: str) -> Dict:
    """
    Args:
        item_cate: 物品实例
        input_file: 用户点击率文件
    Return:
        dict
    """
    if not os.path.exists(input_file):
        return {}
    record = {}
    up = {}
    line_num = 0
    score_thr = 4.0
    top_k = 2
    fp = open(input_file)
    for line in fp:
        if line_num == 0:
            line_num += 1
            continue
        item = line.strip().split(',')
        if len(item) < 4:
            continue
        user_id, item_id, rating, timestamp = item[0], item[1], float(item[2]), int(item[3])
        if rating < score_thr:
            continue
        if item_id not in item_cate:
            continue
        time_score = get_time_score(timestamp)
        if user_id not in record:
            record[user_id] = {}
        for fix_cate in item_cate[item_id]:
            if fix_cate not in record[user_id]:
                record[user_id][fix_cate] = 0
            record[user_id][fix_cate] += rating * time_score * item_cate[item_id][fix_cate]
    fp.close()
    for user_id in record:
        if user_id not in up:
            up[user_id] = []
        total_score = 0
        for r in sorted(record[user_id].items(), key=operator.itemgetter(1), reverse=True)[:top_k]:
            up[user_id].append((r[0], r[1]))
            total_score += r[1]
        for index in range(len(up[user_id])):
            up[user_id][index] = (up[user_id][index][0], round(up[user_id][index][1] / total_score, 3))
    return up


def get_time_score(timestamp: int) -> float:
    """
    Args:
        timestamp: 时间戳
    Return:
        分数
    """
    fix_time_stamp = 1476086345
    total_sec = 24 * 60 * 60
    delta = (fix_time_stamp - timestamp) / total_sec / 100
    return round(1 / (1 + delta), 3)


def recom(cate_item_sort, up, user_id, top_k=10):
    """
    Args:
        cate_item_sort: item进行排序
        up:用户特征
        user_id:用户id
        top_k: top_K
    Return:
         dict
    """
    if user_id not in up:
        return {}
    recom_result = {}
    if user_id not in recom_result:
        recom_result[user_id] = []
    for zuhe in up[user_id]:
        cate = zuhe[0]
        ratio = zuhe[1]
        num = int(top_k * ratio) + 1
        if cate not in cate_item_sort:
            continue
        recom_list = cate_item_sort[cate][:num]
        recom_result[user_id] += recom_list
    return recom_result


def run_main():
    ave_score = read.get_ave_score("../data/ratings.txt")
    item_cate, cate_item_sort = read.get_item_cate(ave_score, "../data/movies.txt")
    up = get_up(item_cate, "../data/ratings.txt")
    recom(cate_item_sort, up, "1")


if __name__ == "__main__":
    run_main()
