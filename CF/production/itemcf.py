# -*-coding:utf8-*-
"""
基于商品的协同过滤算法
@author:zhangyu
email:zhangyuyu417@gmail.com
"""
from __future__ import division
import sys

sys.path.append("../util")
import CF.util.reader as reader
import math
import operator


def base_contribute_score() -> int:
    """
       商品的分数通过用户输入
    """
    return 1


def update_one_contribute_score(user_total_click_num) -> float:
    """
        通过用户来更新分数
    """
    return 1 / math.log10(1 + user_total_click_num)


def update_two_contribute_score(click_time_one: int, click_time_two: int) -> float:
    """
        通过用户来更新两个分数
    """
    delata_time = abs(click_time_one - click_time_two)
    total_sec = 60 * 60 * 24
    delata_time = delata_time / total_sec
    return 1 / (1 + delata_time)


def cal_item_sim(user_click, user_click_time):
    """
        用户点击
    Args:
        user_click:用户点击字典
    Return:
        结果字典
    """
    co_appear = {}
    item_user_click_time = {}
    for user, itemlist in user_click.items():
        for index_i in range(0, len(itemlist)):
            itemid_i = itemlist[index_i]
            item_user_click_time.setdefault(itemid_i, 0)
            item_user_click_time[itemid_i] += 1
            for index_j in range(index_i + 1, len(itemlist)):
                itemid_j = itemlist[index_j]
                if user + "_" + itemid_i not in user_click_time:
                    click_time_one = 0
                else:
                    click_time_one = user_click_time[user + "_" + itemid_i]
                if user + "_" + itemid_j not in user_click_time:
                    click_time_two = 0
                else:
                    click_time_two = user_click_time[user + "_" + itemid_j]
                co_appear.setdefault(itemid_i, {})
                co_appear[itemid_i].setdefault(itemid_j, 0)
                co_appear[itemid_i][itemid_j] += update_two_contribute_score(click_time_one, click_time_two)

                co_appear.setdefault(itemid_j, {})
                co_appear[itemid_j].setdefault(itemid_i, 0)
                co_appear[itemid_j][itemid_i] += update_two_contribute_score(click_time_one, click_time_two)
    item_sim_score = {}
    item_sim_score_sorted = {}
    for itemid_i, relate_item in co_appear.items():
        for itemid_j, co_time in relate_item.items():
            sim_score = co_time / math.sqrt(item_user_click_time[itemid_i] * item_user_click_time[itemid_j])
            item_sim_score.setdefault(itemid_i, {})
            item_sim_score[itemid_i].setdefault(itemid_j, 0)
            item_sim_score[itemid_i][itemid_j] = sim_score
    for itemid in item_sim_score:
        item_sim_score_sorted[itemid] = sorted(item_sim_score[itemid].iteritems(), key= \
            operator.itemgetter(1), reverse=True)
    return item_sim_score_sorted


def cal_recom_result(sim_info, user_click):
    """
        通过商品推荐
    Args:
        sim_info: 字典
        user_click: 用户点击字典
    Return:
        dict, key:userid value dict, value_key itemid , value_value recom_score
    """
    recent_click_num = 3
    topk = 5
    recom_info = {}
    for user in user_click:
        click_list = user_click[user]
        recom_info.setdefault(user, {})
        for itemid in click_list[:recent_click_num]:
            if itemid not in sim_info:
                continue
            for itemsimzuhe in sim_info[itemid][:topk]:
                itemsimid = itemsimzuhe[0]
                itemsimscore = itemsimzuhe[1]
                recom_info[user][itemsimid] = itemsimscore
    return recom_info


def debug_itemsim(item_info, sim_info):
    """
        展示详细信息
    Args:
        item_info: 商品详情字段
        sim_info:  详细信息
    """
    fixed_itemid = "1";
    if fixed_itemid not in item_info:
        print("invalid itemid")
        return
    [title_fix, genres_fix] = item_info[fixed_itemid]
    for zuhe in sim_info[fixed_itemid][:5]:
        itemid_sim = zuhe[0]
        sim_score = zuhe[1]
        if itemid_sim not in item_info:
            continue
        [title, genres] = item_info[itemid_sim]
        print
        title_fix + "\t" + genres_fix + "\tsim:" + title + "\t" + genres + "\t" + str(sim_score)


def debug_recomresult(recom_result, item_info):
    """
        测试推荐结果
    Args:
        recom_result: 推荐结果字典
        item_info: 商品字典

    """
    user_id = "1"
    if user_id not in recom_result:
        print("invalid result")
        return
    for zuhe in sorted(recom_result[user_id].iteritems(), key=operator.itemgetter(1), reverse=True):
        itemid, score = zuhe
        if itemid not in item_info:
            continue
        print(",".join(item_info[itemid]) + "\t" + str(score))


def main_flow():
    """
       基于商品推荐的主函数
    """
    user_click, user_click_time = reader.get_user_click("../data/ratings.txt")
    item_info = reader.get_item_info("../data/movies.txt")
    sim_info = cal_item_sim(user_click, user_click_time)
    debug_itemsim(item_info, sim_info)


if __name__ == "__main__":
    main_flow()
