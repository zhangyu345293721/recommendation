# -*-coding:utf8-*-
"""
特征选择和数据选择
author:zhangyu
email:zhangyuyu417@gmail.com

"""
import pandas as pd
import numpy as np
import operator
import sys


def get_input(input_train_file, input_test_file):
    """
    Args:
        input_train_file:输入训练文件
        input_test_file:输入测试文件
    Return:
         pd.DataFrame train_data
         pd.DataFrame test_data
    """
    dtype_dict = {"age": np.int32,
                  "education-num": np.int32,
                  "capital - gain": np.int32,
                  "capital - loss": np.int32,
                  "hours - per - week": np.int32}
    use_list = range(15)
    use_list.remove(2)
    train_data_df = pd.read_csv(input_train_file, sep=",", header=0, dtype=dtype_dict, na_values="?", usecols=use_list)
    train_data_df = train_data_df.dropna(axis=0, how="any")
    test_data_df = pd.read_csv(input_test_file, sep=",", header=0, dtype=dtype_dict, na_values="?", usecols=use_list)
    test_data_df = test_data_df.dropna(axis=0, how="any")
    return train_data_df, test_data_df


def label_trans(x):
    """
    Args:
        x: 每个元素
    """
    if x == "<=50K":
        return "0"
    if x == ">50K":
        return "1"
    return "0"


def process_label_feature(lable_feature_str, df_in):
    """
    Args:
        lable_feature_str:标致特征字符串
        df_in:df输入
    """
    df_in.loc[:, lable_feature_str] = df_in.loc[:, lable_feature_str].apply(label_trans)


def dict_trans(dict_in):
    """
    Args:
        dict_in: key 字符串, value int
    Return:
        dict:字典
    """
    output_dict = {}
    index = 0
    for zuhe in sorted(dict_in.iteritems(), key=operator.itemgetter(1), reverse=True):
        output_dict[zuhe[0]] = index
        index += 1
    return output_dict


def dis_to_feature(x, feature_dict):
    """
    Args:
        x: 元素
        feature_dict: 位置字典
    Return:
        字符串
    """
    output_list = [0] * len(feature_dict)
    if x not in feature_dict:
        return ",".join([str(ele) for ele in output_list])
    else:
        index = feature_dict[x]
        output_list[index] = 1
    return ",".join([str(ele) for ele in output_list])


def process_dis_feature(feature_str, df_train, df_test):
    """
    Args:
        feature_str: 特征字符串
        df_train: 训练数据df
        df_test:  测试数据df
    Return:
        特征输出
    """
    origin_dict = df_train.loc[:, feature_str].value_counts().to_dict()
    feature_dict = dict_trans(origin_dict)
    df_train.loc[:, feature_str] = df_train.loc[:, feature_str].apply(dis_to_feature, args=(feature_dict,))
    df_test.loc[:, feature_str] = df_test.loc[:, feature_str].apply(dis_to_feature, args=(feature_dict,))
    return len(feature_dict)


def list_trans(input_dict):
    """
    Args:
        input_dict:{'count': 30162.0, 'std': 13.134664776855985, 'min': 17.0, 'max': 90.0, '50%': 37.0,
                    '25%': 28.0, '75%': 47.0, 'mean': 38.437901995888865}
    Return:
        list
    """
    output_list = [0] * 5
    key_list = ["min", "25%", "50%", "75%", "max"]
    for index in range(len(key_list)):
        fix_key = key_list[index]
        if fix_key not in input_dict:
            print("error")
            sys.exit()
        else:
            output_list[index] = input_dict[fix_key]
    return output_list


def output_file(df_in, out_file):
    """
        写数据到输出文件
    """
    fw = open(out_file, "w+")
    for row_index in df_in.index:
        outline = ",".join([str(ele) for ele in df_in.loc[row_index].values])
        fw.write(outline + "\n")
    fw.close()


def ana_train_data(input_train_data, input_test_data, out_train_file, out_test_file, feature_num_file):
    """
    Args:
        input_train_data: 输入训练数据
        input_test_data: 输入测试数据
        out_train_file: 输出训练文件
        out_test_file: 输出测试文件
        feature_num_file:训练数据文件
    """
    train_data_df, test_data_df = get_input(input_train_data, input_test_data)
    label_feature_str = "label"
    dis_feature_list = ["workclass", "education", "marital-status", "occupation",
                        "relationship", "race", "sex", "native-country"]
    con_feature_list = ["age", "education-num", "capital-gain", "capital-loss", "hours-per-week"]
    process_label_feature(label_feature_str, train_data_df)
    process_label_feature(label_feature_str, test_data_df)
    dis_feature_num = 0
    con_feature_num = 0
    for dis_feature in dis_feature_list:
        tmp_feature_num = process_dis_feature(dis_feature, train_data_df, test_data_df)
        dis_feature_num += tmp_feature_num
    for con_feature in con_feature_list:
        con_feature_num += 1
    output_file(train_data_df, out_train_file)
    output_file(test_data_df, out_test_file)
    fw = open(feature_num_file, "w+")
    fw.write("feature_num=" + str(dis_feature_num + con_feature_num))


if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("usage: python xx.py origin_train origin_test train_file test_file feature_num_file")
        sys.exit()
    else:
        origin_train = sys.argv[1]
        origin_test = sys.argv[2]
        train_file = sys.argv[3]
        test_file = sys.argv[4]
        feature_num_file = sys.argv[5]
        ana_train_data(origin_train, origin_test, train_file, test_file, feature_num_file)
