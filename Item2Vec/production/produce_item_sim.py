# -*-coding:utf8-*-
"""
author:zhangyu
email:zhangyuyu417@gmail.com
"""

import os
import numpy as np
import operator
import sys


def load_item_vec(input_file: str):
    """
    Args:
        input_file: 词向量文件
    Return:
        dict key:item_id value:np.array([num1, num2....])
    """
    if not os.path.exists(input_file):
        return {}
    line_num = 0
    item_vec = {}
    fp = open(input_file)
    for line in fp:
        if line_num == 0:
            line_num += 1
            continue
        item = line.strip().split()
        if len(item) < 129:
            continue
        item_id = item[0]
        if item_id == "</s>":
            continue
        item_vec[item_id] = np.array([float(ele) for ele in item[1:]])
    fp.close()
    return item_vec


def cal_item_sim(item_vec, item_id: str, output_file: str):
    """
    Args
        item_vec:词嵌入向量
        item_id:固定的标致
        output_file: 输出文件
    """
    if item_id not in item_vec:
        return
    score = {}
    top_k = 10
    fix_item_vec = item_vec[item_id]
    for tmp_item_id in item_vec:
        if tmp_item_id == item_id:
            continue
        tmp_item_vec = item_vec[tmp_item_id]
        fenmu = np.linalg.norm(fix_item_vec) * np.linalg.norm(tmp_item_vec)
        if fenmu == 0:
            score[tmp_item_id] = 0
        else:
            score[tmp_item_id] = round(np.dot(fix_item_vec, tmp_item_vec) / fenmu, 3)
    fw = open(output_file, "w+")
    out_str = item_id + "\t"
    tmp_list = []
    for s in sorted(score.items(), key=operator.itemgetter(1), reverse=True)[:top_k]:
        tmp_list.append(s[0] + "_" + str(s[1]))
    out_str += ";".join(tmp_list)
    fw.write(out_str + "\n")
    fw.close()


def run_main(input_file: str, output_file: str) -> None:
    '''
        文件内容
    Args:
        input_file: 输入文件
        output_file: 输出文件

    Returns:
        None
    '''
    item_vec = load_item_vec(input_file)
    cal_item_sim(item_vec, "27", output_file)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: python xx.py inputfile outputfile")
        sys.exit()
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        run_main(input_file, output_file)
