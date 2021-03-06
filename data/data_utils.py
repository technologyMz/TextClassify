# -*- coding: utf-8 -*-

import re
import jieba
import random
import numpy as np
from collections import Counter

class DataPath:
    raw_train = './data/raw_data/cnews.train.txt'
    raw_test = './data/raw_data/cnews.test.txt'
    raw_val = './data/raw_data/cnews.val.txt'

    train_dir = './data/segment_data/train.txt'
    test_dir = './data/segment_data/test.txt'
    val_dir = './data/segment_data/val.txt'
    vocab_dir = './data/segment_data/vocab.txt'
    stop_words = './data/segment_data/stop_words.txt'


class TextData:
    
    re_han = re.compile("([\u4E00-\u9FD5]+)")
    
    def __init__(self, cut=False, sampling_rate=1):
        """
        :param cut: 是否需要进行分词（等于True时覆盖sampling_rate）
        :param sampling_rate: sampling_rate: 只选取部分数据进行训练、测试、验证（数据量较大时）
        """
        self.cut = cut
        self.sampling_rate = sampling_rate
        self.stop_words = self.open_file(DataPath.stop_words).read().strip().split('\n')
        if self.cut:
            self.local_data()
        self.word2id, self.cat2id = self.build_vocab(DataPath.train_dir, DataPath.vocab_dir)
    
    def open_file(self, file, mode='r'):
        return open(file, mode, encoding='utf-8', errors='ignore')

    def cut_words(self, sentence : str) -> list:
        """载入分词工具"""
        return jieba.lcut(sentence)

    def remove_stopwords(self, words):
        """删除停用词"""
        return [word for word in words if word not in self.stop_words]

    def text_preprogress(self, content):
        """文本预处理"""
        sentences = self.re_han.findall(content)
        ch_words = [' '.join(self.remove_stopwords(self.cut_words(sentence))) for sentence in sentences]
        return ' '.join(ch_words)

    def to_local(self, input_file, out_file, input_separator='\t'):
        """文本预处理，并写入本地"""
        with self.open_file(input_file) as in_f, self.open_file(out_file,'w') as out_f:
            for line in in_f:
                if random.random() <= self.sampling_rate:
                    label, content = line.strip().split(input_separator)
                    if content:
                        words = self.text_preprogress(content)
                        out_f.write(label + '\t' + words+'\n')

    def read_file(self, input_file, input_separator='\t'):
        """读取处理后的本地数据"""
        contents, labels = [], []
        with self.open_file(input_file) as in_f:
            for line in in_f:
                try:
                    label, content = line.strip().split(input_separator)
                    if content:
                        contents.append(content)
                        labels.append(label)
                except:
                    pass
        return contents, labels

    def build_vocab(self, train_segment_dir, vocab_dir, vocab_size=5000):
        """根据训练集构建词汇表并存储"""
        contents, labels = self.read_file(train_segment_dir)
        labels = sorted(list(set(labels)))
        all_data = []
        for content in contents:
            all_data.extend([c.strip() for c in content.split(' ') if c.strip()!=''])
    
        counter = Counter(all_data)
        count_pairs = counter.most_common(vocab_size - 1)
        words, s = list(zip(*count_pairs))
        # 添加一个 <PAD> 来将所有文本pad为同一长度
        words = ['<PAD>'] + list(words)
        self.open_file(vocab_dir, mode='w').write('\n'.join(words) + '\n')
        return dict(zip(words, range(len(words)))), dict(zip(labels, range(len(set(labels)))))

    def batch_iter(self, x, y, batch_size=64):
        """生成批次数据"""
        data_len = len(x)
        num_batch = int((data_len - 1) / batch_size) + 1
    
        indices = np.random.permutation(np.arange(data_len))
        x_shuffle = x[indices]
        y_shuffle = y[indices]
    
        for i in range(num_batch):
            start_id = i * batch_size
            end_id = min((i + 1) * batch_size, data_len)
            yield x_shuffle[start_id:end_id], y_shuffle[start_id:end_id]

    def local_data(self):
        """训练集、测试集、验证集均分词并写入本地"""
        print('将分词结果写入本地ing')
        self.to_local(DataPath.raw_train, DataPath.train_dir)
        self.to_local(DataPath.raw_test, DataPath.test_dir)
        self.to_local(DataPath.raw_val, DataPath.val_dir)
        print('Done！')

    def load_data(self):
        """读取文件（已分词）"""
        print('读取已分词文本ing')
        train_data, train_labels=self.read_file(DataPath.train_dir)
        test_data, test_labels=self.read_file(DataPath.test_dir)
        val_data, val_labels=self.read_file(DataPath.val_dir)
        return (train_data, test_data, val_data), (train_labels, test_labels, val_labels)

    def to_id(self, _data, _labels):
        _data = [[self.word2id.get(word, 0) for word in sen.split(' ')] for sen in _data] 
        _labels = [self.cat2id.get(label) for label in _labels]
        return _data, _labels

    def load_idata(self):
        """将（已分词）文件转换为id表示"""
        (train_data, test_data, val_data), (train_labels, test_labels, val_labels) = self.load_data()
        print('载入id数据ing')
        x_data, x_labels = self.to_id(train_data, train_labels)
        y_data, y_labels = self.to_id(test_data, test_labels)
        z_data, z_labels = self.to_id(val_data, val_labels)
        return (x_data, y_data, z_data), (x_labels, y_labels, z_labels)


# 载入词向量模型
def create_embedding_matrix(filepath, word_index, embedding_dim):
    vocab_size = len(word_index)
    embedding_matrix = np.zeros((vocab_size, embedding_dim))

    with open(filepath, encoding='utf-8') as f:
        for line in f:
            word, *vector = line.split()
            if word in word_index:
                idx = word_index[word]
                embedding_matrix[idx] = np.array(vector, dtype=np.float32)[:embedding_dim]
    return embedding_matrix


#让每条文本的长度相同，用0填充
def seq_padding(X, padding=0):
    L = [len(x) for x in X]
    ML = max(L)
    return np.array([
        np.concatenate([x, [padding] * (ML - len(x))]) if len(x) < ML else x for x in X
    ])
 
#data_generator只是一种为了节约内存的数据方式
class data_generator:
    def __init__(self, data, seq_length, batch_size, tokenizer, shuffle=True):
        self.data = data
        self.seq_length = seq_length
        self.batch_size = batch_size
        self.tokenizer = tokenizer
        self.shuffle = shuffle
        self.steps = len(self.data) // self.batch_size
        if len(self.data) % self.batch_size != 0:
            self.steps += 1
 
    def __len__(self):
        return self.steps
 
    def __iter__(self):
        while True:
            idxs = list(range(len(self.data)))
 
            if self.shuffle:
                np.random.shuffle(idxs)
 
            X1, X2, Y = [], [], []
            for i in idxs:
                d = self.data[i]
                text = d[0][:self.seq_length]
                x1, x2 = self.tokenizer.encode(first=text)
                y = d[1]
                X1.append(x1)
                X2.append(x2)
                Y.append([y])
                if len(X1) == self.batch_size or i == idxs[-1]:
                    X1 = seq_padding(X1)
                    X2 = seq_padding(X2)
                    Y = seq_padding(Y)
                    yield [X1, X2], Y[:, 0, :]
                    [X1, X2, Y] = [], [], []
    