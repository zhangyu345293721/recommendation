# -*-coding:utf8-*-
"""
author:zhangyu
"""

import os
import numpy as np
import operator
import sys


def load_item_vec(input_file):
    """
    Args:
        input_file: 词向量文件
    Return:
        dict key:itemid value:np.array([num1, num2....])
    """
    if not os.path.exists(input_file):
        return {}
    linenum = 0
    item_vec = {}
    fp = open(input_file)
    for line in fp:
        if linenum == 0:
            linenum += 1
            continue
        item = line.strip().split()
        if len(item) < 129:
            continue
        itemid = item[0]
        if itemid == "</s>":
            continue
        item_vec[itemid] = np.array([float(ele) for ele in item[1:]])
    fp.close()
    return item_vec


def cal_item_sim(item_vec, itemid, output_file):
    """
    Args
        item_vec:词嵌入向量
        itemid:固定的标致
        output_file: 输出文件
    """
    if itemid not in item_vec:
        return
    score = {}
    topk = 10
    fix_item_vec = item_vec[itemid]
    for tmp_itemid in item_vec:
        if tmp_itemid == itemid:
            continue
        tmp_itemvec = item_vec[tmp_itemid]
        fenmu = np.linalg.norm(fix_item_vec) * np.linalg.norm(tmp_itemvec)
        if fenmu == 0:
            score[tmp_itemid] = 0
        else:
            score[tmp_itemid] = round(np.dot(fix_item_vec, tmp_itemvec) / fenmu, 3)
    fw = open(output_file, "w+")
    out_str = itemid + "\t"
    tmp_list = []
    for zuhe in sorted(score.iteritems(), key=operator.itemgetter(1), reverse=True)[:topk]:
        tmp_list.append(zuhe[0] + "_" + str(zuhe[1]))
    out_str += ";".join(tmp_list)
    fw.write(out_str + "\n")
    fw.close()


def run_main(input_file, output_file):
    item_vec = load_item_vec(input_file)
    cal_item_sim(item_vec, "27", output_file)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: python xx.py inputfile outputfile")
        sys.exit()
    else:
        inputfile = sys.argv[1]
        outputfile = sys.argv[2]
        run_main(inputfile, outputfile)
        # run_main("../data/item_vec.txt", "../data/sim_result.txt")
