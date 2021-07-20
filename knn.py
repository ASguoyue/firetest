import math
import operator
import os
from PIL import Image
import numpy as np
##111

def binaryzation(data):
    row = data.shape[1]
    col = data.shape[2]
    ret = np.empty(row * col)
    for i in range(row):
        for j in range(col):
            ret[i * col + j] = 0
            if data[0][i][j] > 127:
                ret[i * col + j] = 1
    return ret


def load_data(data_path, split):
    files = os.listdir(data_path)
    file_num = len(files)
    idx = np.random.permutation(file_num)
    selected_file_num = 42000
    selected_files = []
    for i in range(selected_file_num):
        selected_files.append(files[idx[i]])

    img_mat = np.empty((selected_file_num, 1, 28, 28), dtype="float32")

    data = np.empty((selected_file_num, 28 * 28), dtype="float32")
    label = np.empty(selected_file_num, dtype="uint8")

    print("loading data...")
    for i in range(selected_file_num):
        print(i, "/", selected_file_num, "\r", )
        file_name = selected_files[i]
        file_path = os.path.join(data_path, file_name)
        img_mat[i] = Image.open(file_path)
        data[i] = binaryzation(img_mat[i])
        label[i] = int(file_name.split('.')[0])
    print("")

    div_line = int(split * selected_file_num)
    idx = np.random.permutation(selected_file_num)
    train_idx, test_idx = idx[:div_line], idx[div_line:]
    train_data, test_data = data[train_idx], data[test_idx]
    train_label, test_label = label[train_idx], label[test_idx]

    return train_data, train_label, test_data, test_label


# 计算欧式距离
def calculate_euclidean_distance(data1, data2, length):
    return np.linalg.norm(data1-data2, ord=None, axis=None, keepdims=False)


# 从训练集选出离测试集中一个实例最近的数据
def get_neighbors(k, test):
    distance = []
    length = len(test)
    for i in range(len(train_data)):
        dist = calculate_euclidean_distance(test, train_data[i], length)
        distance.append((train_label[i], dist))
    distance.sort(key=operator.itemgetter(1))
    neighbors = []
    for i in range(k):
        neighbors.append(distance[i][0])
    return neighbors


# 统计类别个数
def get_response(neighbors):
    class_vote = {}
    for i in range(len(neighbors)):
        response = neighbors[i]
        if response not in class_vote:
            class_vote[response] = 1
        else:
            class_vote[response] += 1
    softed_vote = sorted(class_vote.items(), key=operator.itemgetter(1), reverse=True)
    return softed_vote[0][0]


if __name__ == '__main__':

    train_data, train_label, test_data, test_label = load_data("mnist_data", 0.95)

    k = 10
    test_result = []
    for data in test_data:
        neighbors = get_neighbors(k, data)
        test_result.append(get_response(neighbors))
    print(test_result)

    a = np.asarray(test_result)
    arr = test_label-a
    arrnum = 0
    for i in arr:
        if i != 0:
            arrnum += 1

    print(1-arrnum/len(test_label))