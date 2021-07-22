# -*-coding:utf8-*-
"""
 训练wd模型
author:zhangyu
email:zhangyuyu417@gmail.com

"""
from __future__ import division
import tensorflow as tf
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


def get_feature_column():
    """
    Return:
        wide feature  的列, deep feature 的列
    """
    age = tf.feature_column.numeric_column("age")
    education_num = tf.feature_column.numeric_column("education-num")
    capital_gain = tf.feature_column.numeric_column("capital-gain")
    capital_loss = tf.feature_column.numeric_column("capital-loss")
    hour_per_work = tf.feature_column.numeric_column("hours-per-week")

    work_class = tf.feature_column.categorical_column_with_hash_bucket("workclass", hash_bucket_size=512)
    education = tf.feature_column.categorical_column_with_hash_bucket("education", hash_bucket_size=512)
    marital_status = tf.feature_column.categorical_column_with_hash_bucket("marital-status", hash_bucket_size=512)
    occupation = tf.feature_column.categorical_column_with_hash_bucket("occupation", hash_bucket_size=512)
    realationship = tf.feature_column.categorical_column_with_hash_bucket("relationship", hash_bucket_size=512)

    age_bucket = tf.feature_column.bucketized_column(age, boundaries=[18, 25, 30, 35, 40, 45, 50, 55, 60, 65])
    gain_bucket = tf.feature_column.bucketized_column(capital_gain, boundaries=[0, 1000, 2000, 3000, 10000])
    loss_bucket = tf.feature_column.bucketized_column(capital_loss, boundaries=[0, 1000, 2000, 3000, 5000])

    cross_columns = [
        tf.feature_column.crossed_column([age_bucket, gain_bucket], hash_bucket_size=36),
        tf.feature_column.crossed_column([gain_bucket, loss_bucket], hash_bucket_size=16)
    ]

    base_columns = [work_class, education, marital_status, occupation, realationship, age_bucket, gain_bucket,
                    loss_bucket, ]
    wide_columns = base_columns + cross_columns
    deep_columns = [
        age,
        education_num,
        capital_gain,
        capital_loss,
        hour_per_work,
        tf.feature_column.embedding_column(work_class, 9),
        tf.feature_column.embedding_column(education, 9),
        tf.feature_column.embedding_column(marital_status, 9),
        tf.feature_column.embedding_column(occupation, 9),
        tf.feature_column.embedding_column(realationship, 9),
    ]
    return wide_columns, deep_columns


def build_model_estimator(wide_column, deep_column, model_folder):
    """
    Args:
        wide_column: wide特征
        deep_column:deep特征
        model_folder: 原始模型和输出文件
    Return:
        输出模型
    """
    model_es = tf.estimator.DNNLinearCombinedClassifier(
        model_dir=model_folder,
        linear_feature_columns=wide_column,
        linear_optimizer=tf.train.FtrlOptimizer(0.1, l2_regularization_strength=1.0),
        dnn_feature_columns=deep_column,
        dnn_optimizer=tf.train.ProximalAdagradOptimizer(learning_rate=0.1, l1_regularization_strength=0.001,
                                                        l2_regularization_strength=0.001),
        dnn_hidden_units=[128, 64, 32, 16]
    )
    feature_column = wide_column + deep_column
    feature_spec = tf.feature_column.make_parse_example_spec(feature_column)
    serving_input_fn = (tf.estimator.export.build_parsing_serving_input_receiver_fn(feature_spec))
    return model_es, serving_input_fn


def input_fn(data_file, re_time, shuffle, batch_num, predict):
    """
    Args:
        data_file:数据文件
        re_time:间隔重复时间长度
        shuffle: 是否打乱
        batch_num:批次号
        predict: 是否预测
    Return:
        特征
    """
    _CSV_COLUMN_DEFAULTS = [[0], [''], [0], [''], [0], [''], [''], [''], [''], [''],
                            [0], [0], [0], [''], ['']]

    _CSV_COLUMNS = [
        'age', 'workclass', 'fnlwgt', 'education', 'education-num',
        'marital-status', 'occupation', 'relationship', 'race', 'gender',
        'capital-gain', 'capital-loss', 'hours-per-week', 'native-country',
        'label'
    ]

    def parse_csv(value):
        columns = tf.decode_csv(value, record_defaults=_CSV_COLUMN_DEFAULTS)
        features = dict(zip(_CSV_COLUMNS, columns))
        labels = features.pop('label')
        classes = tf.equal(labels, '>50K')
        return features, classes

    def parse_csv_predict(value):
        columns = tf.decode_csv(value, record_defaults=_CSV_COLUMN_DEFAULTS)
        features = dict(zip(_CSV_COLUMNS, columns))
        labels = features.pop('label')
        return features

    data_set = tf.data.TextLineDataset(data_file).skip(1).filter(
        lambda line: tf.not_equal(tf.strings.regex_full_match(line, ".*\?.*"), True))
    if shuffle:
        data_set = data_set.shuffle(buffer_size=30000)
    if predict:
        data_set = data_set.map(parse_csv_predict, num_parallel_calls=5)
    else:
        data_set = data_set.map(parse_csv, num_parallel_calls=5)

    data_set = data_set.repeat(re_time)
    data_set = data_set.batch(batch_num)
    return data_set


def train_wd_model(model_es, train_file, test_file, model_export_folder, serving_input_fn):
    """
    Args:
        model_es: wd评估
        train_file:训练文件
        test_file:测试文件
        model_export_folder: 输出文件夹
        serving_input_fn: 模型文件输出
    """
    total_run = 6
    for index in range(total_run):
        model_es.train(input_fn=lambda: input_fn(train_file, 10, True, 100, False))
        print(model_es.evaluate(input_fn=lambda: input_fn(test_file, 1, False, 100, False)))
    model_es.export_savedmodel(model_export_folder, serving_input_fn)


def get_auc(predict_list, test_label):
    """
    Args:
        predict_list: 模型预测分数链表
        test_label:   测试标签
    auc = (sum(pos_index)-pos_num(pos_num + 1)/2)/pos_num*neg_num
    """
    total_list = []
    for index in range(len(predict_list)):
        predict_score = predict_list[index]
        label = test_label[index]
        total_list.append((label, predict_score))
    sorted_total_list = sorted(total_list, key=lambda ele: ele[1])
    neg_num = 0
    pos_num = 0
    count = 1
    total_pos_index = 0
    for zuhe in sorted_total_list:
        label, predict_score = zuhe
        if label == 0:
            neg_num += 1
        else:
            pos_num += 1
            total_pos_index += count
        count += 1
    auc_score = (total_pos_index - (pos_num) * (pos_num + 1) / 2) / (pos_num * neg_num)
    print("auc:%.5f" % (auc_score))


def get_test_label(test_file):
    """
        获取测试文件
    """
    if not os.path.exists(test_file):
        return []
    fp = open(test_file)
    linenum = 0
    test_label_list = []
    for line in fp:
        if linenum == 0:
            linenum += 1
            continue
        if "?" in line.strip():
            continue
        item = line.strip().split(",")
        label_str = item[-1]
        if label_str == ">50K":
            test_label_list.append(1)
        elif label_str == "<=50K":
            test_label_list.append(0)
        else:
            print
            label_str
            print
            "error"
    fp.close()
    return test_label_list


def test_model_performance(model_es, test_file):
    """
        通过测试文件检验模型准确率
    """
    test_label = get_test_label(test_file)
    result = model_es.predict(input_fn=lambda: input_fn(test_file, 1, False, 100, True))
    predict_list = []
    for one_res in result:
        if "probabilities" in one_res:
            predict_list.append(one_res["probabilities"][1])
    get_auc(predict_list, test_label)


def run_main(train_file, test_file, model_folder, model_export_folder):
    """
    Args:
        train_file: 训练文件
        test_file: 测试文件
        model_folder: 模型文件
        model_export_folder: 模型输出文件
    """
    wide_column, deep_column = get_feature_column()
    model_es, serving_input_fn = build_model_estimator(wide_column, deep_column, model_folder)
    train_wd_model(model_es, train_file, test_file, model_export_folder, serving_input_fn)
    test_model_performance(model_es, test_file)


if __name__ == "__main__":
    run_main("../data/train.txt", "../data/test.txt", "../data/wd", "../data/wd_export")
