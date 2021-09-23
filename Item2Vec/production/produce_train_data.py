"""
从数据中训练Item2Vec
author:zhangyu
email:zhangyuyu417@gmail.com
"""

import os
import sys


def produce_train_data(input_file: str, out_file: str):
    """
    Args:
        input_file:用户行为文件
        out_file: 输出文件
    """
    if not os.path.exists(input_file):
        return
    record = {}
    line_num = 0
    score_thr = 4.0
    fp = open(input_file)
    for line in fp:
        if line_num == 0:
            line_num += 1
            continue
        item = line.strip().split(',')
        if len(item) < 4:
            continue
        user_id, item_id, rating = item[0], item[1], float(item[2])
        if rating < score_thr:
            continue
        if user_id not in record:
            record[user_id] = []
        record[user_id].append(item_id)
    fp.close()
    fw = open(out_file, 'w+')
    for user_id in record:
        fw.write(" ".join(record[user_id]) + "\n")
    fw.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: python xx.py inputfile outputfile")
        sys.exit()
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        produce_train_data(input_file, output_file)
