# -*-coding:utf8-*-
"""
基于用户的协同过滤算法
author:zhangyu
email:zhangyuyu417@gmail.com
"""
from __future__ import division
import sys
from typing import Dict

sys.path.append("../util")
import CF.util.reader as reader
import math
import operator


def transfer_user_click(user_click: Dict) -> Dict:
    """
        获取用户点击的商品
    Args:
        user_click: key user_id, value:[item_id1, item_id2]
    Return:
        dict, key item_id value:[user_id1, user_id2]
    """
    item_click_by_user = {}
    for user in user_click:
        item_list = user_click[user]
        for item_id in item_list:
            item_click_by_user.setdefault(item_id, [])
            item_click_by_user[item_id].append(user)
    return item_click_by_user


def base_contribution_score():
    """
       基于用户来打分
    """
    return 1


def update_contribution_score(item_user_click_count: int) -> float:
    """
            更新分数
    Args:
            item_user_click_count: 多少用户点击了这个商品
    Return:
            返回分数
    """
    return 1 / math.log10(1 + item_user_click_count)


def update_two_contribution_score(click_time_one: int, click_time_two: int) -> float:
    """
        更新分数2
    Args:
         click_time_one:点击时间1
         click_time_two:点击时间2
    Return:
        分数
    """
    delta_time = abs(click_time_two - click_time_one)
    norm_num = 60 * 60 * 24
    delta_time = delta_time / norm_num
    return 1 / (1 + delta_time)


def cal_user_sim(item_click_by_user: Dict, user_click_time: Dict) -> Dict:
    """
        获取具体信息
    Args:
        item_click_by_user: 点击字典
    Return:
        字典
    """
    co_appear = {}
    user_click_count = {}
    for item_id, user_list in item_click_by_user.items():
        for index_i in range(0, len(user_list)):
            user_i = user_list[index_i]
            user_click_count.setdefault(user_i, 0)
            user_click_count[user_i] += 1
            if user_i + "_" + item_id not in user_click_time:
                click_time_one = 0
            else:
                click_time_one = user_click_time[user_i + "_" + item_id]
            for index_j in range(index_i + 1, len(user_list)):
                user_j = user_list[index_j]
                if user_j + "_" + item_id not in user_click_time:
                    click_time_two = 0
                else:
                    click_time_two = user_click_time[user_j + "_" + item_id]
                co_appear.setdefault(user_i, {})
                co_appear[user_i].setdefault(user_j, 0)
                co_appear[user_i][user_j] += update_two_contribution_score(click_time_one, click_time_two)
                co_appear.setdefault(user_j, {})
                co_appear[user_j].setdefault(user_i, 0)
                co_appear[user_j][user_i] += update_two_contribution_score(click_time_one, click_time_two)

    user_sim_info = {}
    user_sim_info_sorted = {}
    for user_i, relate_user in co_appear.items():
        user_sim_info.setdefault(user_i, {})
        for user_j, cotime in relate_user.items():
            user_sim_info[user_i].setdefault(user_j, 0)
            user_sim_info[user_i][user_j] = cotime / math.sqrt(user_click_count[user_i] * user_click_count[user_j])
    for user in user_sim_info:
        user_sim_info_sorted[user] = sorted(user_sim_info[user].items(), key=operator.itemgetter(1), reverse=True)
    return user_sim_info_sorted


def cal_recom_result(user_click: Dict, user_sim: Dict) -> Dict:
    """
         基于用户推荐结果
    Args:
        user_click: 用户点击字典
        user_sim: 点击字典和分数
    Return:
         字典：商品id
    """
    recom_result = {}
    top_k_user = 3
    item_num = 5
    for user, item_list in user_click.items():
        tmp_dict = {}
        for item_id in item_list:
            tmp_dict.setdefault(item_id, 1)
        recom_result.setdefault(user, {})
        for user in user_sim[user][:top_k_user]:
            user_id_j, sim_score = user
            if user_id_j not in user_click:
                continue
            for item_id_j in user_click[user_id_j][:item_num]:
                recom_result[user].setdefault(item_id_j, sim_score)
    return recom_result


def debug_user_sim(user_sim: Dict) -> None:
    """
        打印用户结果
    Args:
        user_sim: 用户id和分数
    """
    top_k = 5
    fix_user = "1"
    if fix_user not in user_sim:
        print("invalid user")
        return
    for user in user_sim[fix_user][:top_k]:
        user_id, score = user
        print(fix_user + "\tsim_user" + user_id + "\t" + str(score))


def debug_recom_result(item_info: Dict, recom_result: Dict) -> None:
    """
        测试用户结果
    Args:
        item_info: 商品信息
        recom_result: 推荐结果
    """
    fix_user = "1"
    if fix_user not in recom_result:
        print("invalid user for recoming result")
        return
    for item_id in recom_result["1"]:
        if item_id not in item_info:
            continue
        recom_score = recom_result["1"][item_id]
        print("recom_result:" + ",".join(item_info[item_id]) + "\t" + str(recom_score))


def main_flow() -> Dict:
    """
        主方法
    """
    user_click, user_click_time = reader.get_user_click("../data/ratings.txt")
    item_info = reader.get_item_info("../data/movies.txt")
    item_click_by_user = transfer_user_click(user_click)
    user_sim = cal_user_sim(item_click_by_user, user_click_time)
    debug_user_sim(user_sim)


if __name__ == "__main__":
    main_flow()
