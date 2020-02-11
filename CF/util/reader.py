# -*-coding:utf8-*-
"""
读取文件
author:zhangyu
"""
import os

def get_user_click(rating_file) -> dict:
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
        [userid, itemid, rating, timestamp] = item
        if userid + "_" + itemid not in user_click_time:
            user_click_time[userid + "_" + itemid] = int(timestamp)
        if float(rating) < 3.0:
            continue
        if userid not in user_click:
            user_click[userid] = []
        user_click[userid].append(itemid)
    fp.close()
    return user_click, user_click_time


def get_item_info(item_file) -> dict:
    """
        通过文件获取点击率
    Args:
        item_file:输入文件
    Return:
        字典
    """
    if not os.path.exists(item_file):
        return {}
    num = 0
    item_info = {}
    fp = open(item_file)
    for line in fp:
        if num == 0:
            num += 1
            continue
        item = line.strip().split(',')
        if len(item) < 3:
            continue
        if len(item) == 3:
            [itemid, title, genres] = item
        elif len(item) > 3:
            itemid = item[0]
            genres = item[-1]
            title = ",".join(item[1:-1])
        if itemid not in item_info:
            item_info[itemid] = [title, genres]
    fp.close()
    return item_info


if __name__ == "__main__":
    item_info = get_item_info("../data/movies.txt")
    print(item_info["11"])
