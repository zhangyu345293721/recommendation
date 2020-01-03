# -*-coding:utf8-*-
"""
    训练gdbt模型
    author:zhangyu
"""
import Tree.xgboost as xgb
import sys
sys.path.append("../")
import Tree.util.get_feature_num as GF
import numpy as np
from sklearn.linear_model import LogisticRegressionCV as LRCV
from scipy.sparse import coo_matrix


def get_train_data(train_file, feature_num_file):
    """
        获取训练数据和标签
    """
    total_feature_num = GF.get_feature_num(feature_num_file)
    train_label = np.genfromtxt(train_file, dtype=np.int32, delimiter=",", usecols= -1)
    feature_list = range(total_feature_num)
    train_feature = np.genfromtxt(train_file, dtype=np.int32, delimiter=",", usecols= feature_list)
    return train_feature, train_label


def train_tree_model_core(train_mat, tree_depth, tree_num, learning_rate):
    """
    Args:
        train_mat:训练数据和标签
        tree_depth:树的深度
        tree_num:树的数量
        learning_rate: 步频
    Return:
        Booster
    """
    para_dict = {"max_depth":tree_depth, "eta":learning_rate, "objective":"reg:linear","silent":1}
    bst = xgb.train(para_dict, train_mat, tree_num)
    return bst


def choose_parameter():
    """
    Return:
         链表
    """
    result_list = []
    tree_depth_list = [4, 5, 6]
    tree_num_list = [10, 50, 100]
    learning_rate_list = [0.3, 0.5, 0.7]
    for ele_tree_depth in tree_depth_list:
        for ele_tree_num in tree_num_list:
            for ele_learning_rate in learning_rate_list:
                result_list.append((ele_tree_depth, ele_tree_num, ele_learning_rate))
    return result_list


def grid_search(train_mat):
    """
    Args:
        train_mat: 训练数据和标签
    """
    para_list = choose_parameter()
    for ele in para_list:
        (tree_depth, tree_num, learning_rate) = ele
        para_dict = {"max_depth": tree_depth, "eta": learning_rate, "objective": "reg:linear", "silent": 1}
        res = xgb.cv(para_dict, train_mat, tree_num, nfold=5, metrics={'auc'})
        auc_score = res.loc[tree_num-1, ['test-auc-mean']].values[0]
        print ("tree_depth:%s,tree_num:%s, learning_rate:%s, auc:%f" \
              %(tree_depth, tree_num, learning_rate, auc_score))


def train_tree_model(train_file , feature_num_file, tree_model_file):
    """
    Args:
        train_file: 训练文件
        tree_model_file: 树模型文件
        feature_num_file:特征数量文件
    """
    train_feature, train_label = get_train_data(train_file, feature_num_file)
    train_mat = xgb.DMatrix(train_feature, train_label)
    tree_num = 10
    tree_depth = 4
    learning_rate = 0.3
    bst = train_tree_model_core(train_mat, tree_depth, tree_num, learning_rate)
    bst.save_model(tree_model_file)


def get_gbdt_and_lr_feature(tree_leaf, tree_num, tree_depth):
    """
    Args:
        tree_leaf:树叶子
        tree_num:树的数量
        tree_depth:total_tree_depth
    Return:
         Matrix
    """
    total_node_num = 2**(tree_depth + 1) - 1
    yezi_num = 2**tree_depth
    feiyezi_num = total_node_num - yezi_num
    total_col_num = yezi_num*tree_num
    total_row_num = len(tree_leaf)
    col = []
    row = []
    data = []
    base_row_index = 0
    for one_result in tree_leaf:
        base_col_index = 0
        for fix_index in one_result:
            yezi_index = fix_index - feiyezi_num
            yezi_index  = yezi_index if yezi_index >= 0 else 0
            col.append(base_col_index + yezi_index)
            row.append(base_row_index)
            data.append(1)
            base_col_index += yezi_num
        base_row_index += 1
    total_feature_list = coo_matrix((data, (row,col)), shape=(total_row_num, total_col_num))
    return total_feature_list


def get_mix_model_tree_info():
    """
        混合模型中树的信息
    """
    tree_depth = 4
    tree_num = 10
    step_size = 0.3
    result = (tree_depth, tree_num, step_size)
    return result


def train_tree_and_lr_model(train_file, feature_num_file, mix_tree_model_file, mix_lr_model_file):
    """
    Args:
        train_file:训练文件
        feature_num_file:特征数量文件
        mix_tree_model_file: 混合树模型文件
        mix_lr_model_file:混合模型文件
    """
    train_feature, train_label = get_train_data(train_file, feature_num_file)
    train_mat = xgb.DMatrix(train_feature, train_label)
    (tree_depth, tree_num, learning_rate) = get_mix_model_tree_info()
    bst = train_tree_model_core(train_mat, tree_depth, tree_num, learning_rate)
    bst.save_model(mix_tree_model_file)
    tree_leaf = bst.predict(train_mat, pred_leaf=True)
    total_feature_list = get_gbdt_and_lr_feature(tree_leaf, tree_num, tree_depth)
    lr_clf = LRCV(Cs=[1.0], penalty='l2', dual=False, tol=0.0001, max_iter=500, cv=5)\
        .fit(total_feature_list, train_label)
    scores = lr_clf.scores_.values()[0]
    print( "diffC:%s" % (','.join([str(ele) for ele in scores.mean(axis=0)])))
    print( "Accuracy:%f(+-%0.2f)" % (scores.mean(), scores.std() * 2))
    lr_clf = LRCV(Cs=[1.0], penalty='l2', dual=False, tol=0.0001, max_iter=500, scoring='roc_auc', cv=5).fit(
        total_feature_list, train_label)
    scores = lr_clf.scores_.values()[0]
    print ("diffC:%s" % (','.join([str(ele) for ele in scores.mean(axis=0)])))
    print ("AUC:%f,(+-%0.2f)" % (scores.mean(), scores.std() * 2))
    fw = open(mix_lr_model_file, "w+")
    coef = lr_clf.coef_[0]
    fw.write(','.join([str(ele) for ele in coef]))


if __name__ == "__main__":

    if len(sys.argv) == 4:
        train_file = sys.argv[1]
        feature_num_file = sys.argv[2]
        tree_model = sys.argv[3]
        train_tree_model(train_file, feature_num_file, tree_model)
    elif len(sys.argv) == 5:
        train_file = sys.argv[1]
        feature_num_file = sys.argv[2]
        tree_mix_model = sys.argv[3]
        lr_coef_mix_model = sys.argv[4]
        train_tree_and_lr_model(train_file,  feature_num_file, tree_mix_model, lr_coef_mix_model)
    else:
        print ("train gbdt model usage: python xx.py train_file feature_num_file tree_model")
        print ("train lr_gbdt model usage: python xx.py train_file feature_num_file tree_mix_model lr_coef_mix_model")
        sys.exit()
   
