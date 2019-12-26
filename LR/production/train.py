# -*-coding:utf8-*-
"""
author:zhangyu
train lr model
"""
import sys

sys.path.append("../")
from sklearn.linear_model import LogisticRegressionCV as lrcv
from sklearn.externals import joblib
import LR.util.get_feature_num as gf
import numpy as np


def train_lr_model(train_file, model_coef, model_file, feature_num_file):
    """
    Args:
        train_file: process file for lr train
        model_coef: w1 w2...
        model_file:model pkl
        feature_num_file: file to record num of feature
    """
    total_feature_num = gf.get_feature_num(feature_num_file)
    train_label = np.genfromtxt(train_file, dtype=np.int32, delimiter=",", usecols=-1)
    feature_list = range(total_feature_num)
    train_feature = np.genfromtxt(train_file, dtype=np.int32, delimiter=",", usecols=feature_list)
    lr_cf = lrcv(Cs=[1], penalty="l2", tol=0.0001, max_iter=500, cv=5).fit(train_feature, train_label)
    scores = lr_cf.scores_.values()[0]
    print
    "diff:%s" % (",".join([str(ele) for ele in scores.mean(axis=0)]))
    print
    "Accuracy:%s (+-%0.2f)" % (scores.mean(), scores.std() * 2)
    lr_cf = lrcv(Cs=[1], penalty="l2", tol=0.0001, max_iter=500, cv=5, scoring="roc_auc").fit(train_feature,
                                                                                              train_label)
    scores = lr_cf.scores_.values()[0]
    print
    "diff:%s" % (",".join([str(ele) for ele in scores.mean(axis=0)]))
    print
    "AUC:%s (+-%0.2f)" % (scores.mean(), scores.std() * 2)
    coef = lr_cf.coef_[0]
    fw = open(model_coef, "w+")
    fw.write(",".join(str(ele) for ele in coef))
    fw.close()
    joblib.dump(lr_cf, model_file)


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print
        "usage: python xx.py train_file coef_file model_file featuren_num_file"
        sys.exit()
    else:
        train_file = sys.argv[1]
        coef_file = sys.argv[2]
        model_file = sys.argv[3]
        feature_num_file = sys.argv[4]
        train_lr_model(train_file, coef_file, model_file, feature_num_file)

        # train_lr_model("../data/train_file", "../data/lr_coef", "../data/lr_model_file", "../data/feature_num")
