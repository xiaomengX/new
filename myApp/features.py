import numpy as np
from sklearn import preprocessing
import python_speech_features as mfcc
from scipy.io.wavfile import read
#计算并返回给定特征向量矩阵的增量
def calculate_delta(array):
    rows,cols=array.shape
    deltas=np.zeros((rows,20))
    N=2
    for i in range(rows):
        index = []
        j = 1
        while j <= N:
            if i - j < 0:
                first = 0
            else:
                first = i - j
            if i + j > rows - 1:
                second = rows - 1
            else:
                second = i + j
            index.append((second, first))
            j += 1
        deltas[i] = (array[index[0][0]] - array[index[0][1]] + (2 * (array[index[1][0]] - array[index[1][1]]))) / 10
    # print(deltas)
    return deltas


def extract_features(audio, rate):
  #从音频中提取20个dim mfcc特征，执行CMS并结合delta使其成为40个dim特征向量
    mfcc_feat = mfcc.mfcc(audio, rate, 0.025, 0.01, 20, appendEnergy=True)

    mfcc_feat = preprocessing.scale(mfcc_feat)
    delta = calculate_delta(mfcc_feat)


    combined = np.hstack((mfcc_feat, delta))
    # print(delta)
    return combined