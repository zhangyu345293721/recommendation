"""
author:zhangyu
排序方法
"""

from __future__ import division
import os
import operator


def get_ave_score(input_file):
    """
    Args:
        input_file: 用户点击率文件
    Return:
        dict
    """
    if not os.path.exists(input_file):
        return {}
    linenum = 0
    record = {}
    ave_score = {}
    fp = open(input_file)
    for line in fp:
        if linenum == 0:
            linenum += 1
            continue
        item = line.strip().split(",")
        if len(item) < 4:
            continue
        userid, itemid, rating = item[0], item[1], float(item[2])
        if itemid not in record:
            record[itemid] = [0, 0]
        record[itemid][0] += rating
        record[itemid][1] += 1
    fp.close()
    for itemid in record:
        ave_score[itemid] = round(record[itemid][0] / record[itemid][1], 3)
    return ave_score


def get_item_cate(ave_score, input_file):
    """
    Args:
        ave_score: 平均分数
        input_file: 输入文件
    Return:
        dict: key itemid value a dict, key: cate value:ratio
        dict: key cate value [itemid1, itemid2, itemid3]
    """

    if not os.path.exists(input_file):
        return {}, {}
    linenum = 0
    topk = 100
    item_cate = {}
    record = {}
    cate_item_sort = {}
    fp = open(input_file)
    for line in fp:
        if linenum == 0:
            linenum += 1
            continue
        item = line.strip().split(',')
        if len(item) < 3:
            continue
        itemid = item[0]
        cate_str = item[-1]
        cate_list = cate_str.strip().split("|")
        ratio = round(1 / len(cate_list), 3)
        if itemid not in item_cate:
            item_cate[itemid] = {}
        for fix_cate in cate_list:
            item_cate[itemid][fix_cate] = ratio
    fp.close()
    for itemid in item_cate:
        for cate in item_cate[itemid]:
            if cate not in record:
                record[cate] = {}
            itemid_rating_score = ave_score.get(itemid, 0)
            record[cate][itemid] = itemid_rating_score
    for cate in record:
        if cate not in cate_item_sort:
            cate_item_sort[cate] = []
        for zuhe in sorted(record[cate].iteritems(), key=operator.itemgetter(1), reverse=True)[:topk]:
            cate_item_sort[cate].append(zuhe[0])
    return item_cate, cate_item_sort


def get_latest_timestamp(input_file):
    """
    Args:
        input_file:用户点击率文件
    """
    if not os.path.exists(input_file):
        return
    linenum = 0
    latest = 0
    fp = open(input_file)
    for line in fp:
        if linenum == 0:
            linenum += 1
            continue
        item = line.strip().split(",")
        if len(item) < 4:
            continue
        timestamp = int(item[3])
        if timestamp > latest:
            latest = timestamp
    fp.close()
    print(latest)
