#-*-coding:utf8-*-
"""
author:zhangyu
"""

from __future__ import division
from scipy.sparse import coo_matrix
import numpy as np
import PR.read as read
import sys

def graph_to_m(graph):
    """
    Args:
        graph:用户商品图
    Return:
       coo_matrix
       list
       dict
    """
    vertex = graph.keys()
    address_dict = {}
    total_len = len(vertex)
    for index in range(len(vertex)):
        address_dict[vertex[index]] = index
    row = []
    col = []
    data = []
    for element_i in graph:
        weight = round(1/len(graph[element_i]), 3)
        row_index = address_dict[element_i]
        for element_j in graph[element_i]:
            col_index = address_dict[element_j]
            row.append(row_index)
            col.append(col_index)
            data.append(weight)
    row = np.array(row)
    col = np.array(col)
    data = np.array(data)
    m = coo_matrix((data, (row, col)), shape=(total_len, total_len))
    return m, vertex, address_dict


def mat_all_point(m_mat, vertex, alpha):
    """
    get E-alpha*m_mat.T
    Args:
        m_mat:  m_mat
        vertex: 总共用户点
        alpha:  随机图像
    Return:
        a sparse
    """
    total_len = len(vertex)
    row = []
    col = []
    data = []
    for index in range(total_len):
        row.append(index)
        col.append(index)
        data.append(1)
    row = np.array(row)
    col = np.array(col)
    data = np.array(data)
    eye_t = coo_matrix((data, (row, col)), shape=(total_len, total_len))
    return eye_t.tocsr() - alpha*m_mat.tocsr().transpose()

if __name__ == "__main__":
    graph = read.get_graph_from_data("../data/log.txt")
    m, vertex, address_dict = graph_to_m(graph)
    mat_all_point(m, vertex, 0.8)
