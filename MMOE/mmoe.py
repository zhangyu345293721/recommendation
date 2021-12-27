# -*- coding:utf-8 -*-
'''
author:zhangyu
date:2021/9/27
'''

import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Input
from keras import backend as K

# 模拟数据
# 1. expert_kernels (input_features * hidden_units * num_experts = 4 * 2 * 3)

# input_features = 4
# hidden_units = 2
# num_experts = 3

expert_kernels = tf.constant([
    [[1., 1., 1.], [2., 2., 1.]], \
    [[0.1, 0.5, 1.], [0.4, 0.1, 1.]], \
    [[1., 1., 1.], [2., 2., 1.]], \
    [[0., 1., 6.], [0., 2., 0.]]
], dtype=tf.float64)

print("expert_kernels: \n", expert_kernels)

# 2. gate_kernels (input_features * num_experts * num_tasks = 4 * 3 * 2)

# input_features = 4
# num_experts = 3
# num_tasks = 2

gate_kernels = [tf.constant([[0.1, 0.5, 1.], [0.4, 0.1, 1.], [1., 1., 1.], [2., 2., 1.]], dtype=tf.float64), \
                tf.constant([[1., 2., 1.], [4., 0.2, 1.5], [2., 1., 0.], [5., 2., 1.]], dtype=tf.float64)]

print("\n" * 3)
print("gate_kernels: \n", gate_kernels)
print("\n" * 3)

# 3. input samples (samples * input_features = 2 * 4)

# samples = 2
# input_features = 4
inputs = tf.constant([[1., 2., 1., 0.], [4., 0.2, 1., 1.]], dtype=tf.float64)

print("inputs: \n", inputs)

# 2. expert_outputs
# result 1: expert_outputs = input * expert_kernels (samples * hidden_units * num_experts = 2 * 2 * 3)
# f_{i}(x) = activation(W_{i} * x + b)

# samples = 2
# hidden_units = 2
# num_experts = 3

expert_outputs = tf.tensordot(a=inputs, b=expert_kernels, axes=1)
print("expert_outputs: \n", expert_outputs)
print("\n" * 3)

# 3. gate_outputs
# result 2: gate_outputs = input * gate_kernels (num_tasks * samples * num_experts = 2 * 2 * 3)
# g^{k}(x) = activation(W_{g,k} * x + b)

# num_tasks = 2

# samples: 2
# num_experts = 3

gate_outputs = []

for index, gate_kernel in enumerate(gate_kernels):
    gate_output = K.dot(x=inputs, y=gate_kernel)
    gate_outputs.append(gate_output)

gate_outputs = tf.nn.softmax(gate_outputs)
print("gate_outputs: \n", gate_outputs)

# 4. final_result
# result 3: final_outputs = gate_outputs * expert_outputs (num_tasks * samples * hidden_units = 2 * 2 * 2)
# 每个 task 的权重值 (gate_output) 分别作用于 expert_outputs，根据 hidden_units 维度进行加和
# f^{k}(x) = sum_{i=1}^{n} (g^{k}_{i}(x) * f_{i}(x))

final_outputs = []
hidden_units = 2

for gate_output in gate_outputs:
    expanded_gate_output = K.expand_dims(gate_output, axis=1)
    # print("expanded_gate_output", expanded_gate_output)
    # print("\n"*2)

    weighted_expert_output = expert_outputs * K.repeat_elements(expanded_gate_output, hidden_units, axis=1)
    # print("weighted_expert_output: ", weighted_expert_output)
    # print("\n"*3)

    final_outputs.append(K.sum(weighted_expert_output, axis=2))

print("final_outputs: \n", final_outputs)
