"""
author:zhangyu
排序方法
"""

from __future__ import division
import os
import operator
from typing import Dict, Tuple


def get_ave_score(input_file: str) -> Dict:
    """
    Args:
        input_file: 用户点击率文件
    Return:
        dict
    """
    if not os.path.exists(input_file):
        return {}
    line_num = 0
    record = {}
    ave_score = {}
    fp = open(input_file)
    for line in fp:
        if line_num == 0:
            line_num += 1
            continue
        item = line.strip().split(",")
        if len(item) < 4:
            continue
        user_id, item_id, rating = item[0], item[1], float(item[2])
        if item_id not in record:
            record[item_id] = [0, 0]
        record[item_id][0] += rating
        record[item_id][1] += 1
    fp.close()
    for item_id in record:
        ave_score[item_id] = round(record[item_id][0] / record[item_id][1], 3)
    return ave_score


def get_item_cate(ave_score: Dict, input_file: str) -> Tuple[Dict, Dict]:
    """
    Args:
        ave_score: 平均分数
        input_file: 输入文件
    Return:
        dict: key item_id value a dict, key: cate value:ratio
        dict: key cate value [item_id1, item_id2, item_id3]
    """

    if not os.path.exists(input_file):
        return {}, {}
    line_num = 0
    top_k = 100
    item_cate = {}
    record = {}
    cate_item_sort = {}
    fp = open(input_file)
    for line in fp:
        if line_num == 0:
            line_num += 1
            continue
        item = line.strip().split(',')
        if len(item) < 3:
            continue
        item_id = item[0]
        cate_str = item[-1]
        cate_list = cate_str.strip().split("|")
        ratio = round(1 / len(cate_list), 3)
        if item_id not in item_cate:
            item_cate[item_id] = {}
        for fix_cate in cate_list:
            item_cate[item_id][fix_cate] = ratio
    fp.close()
    for item_id in item_cate:
        for cate in item_cate[item_id]:
            if cate not in record:
                record[cate] = {}
            item_id_rating_score = ave_score.get(item_id, 0)
            record[cate][item_id] = item_id_rating_score
    for cate in record:
        if cate not in cate_item_sort:
            cate_item_sort[cate] = []
        for r in sorted(record[cate].items(), key=operator.itemgetter(1), reverse=True)[:top_k]:
            cate_item_sort[cate].append(r[0])
    return item_cate, cate_item_sort


def get_latest_timestamp(input_file: str) -> int:
    """
    Args:
        input_file:用户点击率文件
    """
    if not os.path.exists(input_file):
        return
    line_num = 0
    latest = 0
    fp = open(input_file)
    for line in fp:
        if line_num == 0:
            line_num += 1
            continue
        item = line.strip().split(",")
        if len(item) < 4:
            continue
        timestamp = int(item[3])
        if timestamp > latest:
            latest = timestamp
    fp.close()
    print(latest)
