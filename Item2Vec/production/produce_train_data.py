#-*-coding:utf8-*-
"""
author:david
date:2018***
produce train data for item2vec
"""

import os
import sys


def produce_train_data(input_file, out_file):
    """
    Args:
        input_file:user behavior file
        out_file: output file
    """
    if not os.path.exists(input_file):
        return
    record = {}
    linenum = 0
    score_thr = 4.0
    fp = open(input_file)
    for line in fp:
        if linenum==0:
            linenum += 1
            continue
        item = line.strip().split(',')
        if len(item) < 4:
            continue
        userid, itemid, rating = item[0], item[1], float(item[2])
        if rating < score_thr:
            continue
        if userid not in record:
            record[userid] = []
        record[userid].append(itemid)
    fp.close()
    fw = open(out_file, 'w+')
    for userid in record:
        fw.write(" ".join(record[userid]) + "\n")
    fw.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "usage: python xx.py inputfile outputfile"
        sys.exit()
    else:
        inputfile = sys.argv[1]
        outputfile = sys.argv[2]
        produce_train_data(inputfile, outputfile)
        #produce_train_data("../data/ratings.txt", "../data/train_data.txt")
