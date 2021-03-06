# -*- coding: utf-8 -*-
'''
SimpleCnn新闻文本分类
'''

from data import TextData
from public import SimpleCNNConfig, plt_model
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical, plot_model
from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout
from keras.layers import Embedding, Conv1D, GlobalMaxPooling1D
from keras.optimizers import Adam

# 读入训练数据
td = TextData()
(x_data, y_data, z_data), (x_labels, y_labels, z_labels) = td.load_idata()
word2id = td.word2id
cat2id = td.cat2id
num_classes=len(set(x_labels))
vocab_size = len(word2id)

# 将每条文本固定为相同长度
x_data = pad_sequences(x_data, SimpleCNNConfig.seq_length)   
x_labels = to_categorical(x_labels, num_classes=num_classes)

y_data = pad_sequences(y_data, SimpleCNNConfig.seq_length)   
y_labels = to_categorical(y_labels, num_classes=num_classes)


def simple_cnn(CNNConfig):
    # 构建模型
    model = Sequential()
    model.add(Embedding(vocab_size, CNNConfig.embedding_dims,
                        input_length=CNNConfig.seq_length))
    
    model.add(Conv1D(CNNConfig.filters, CNNConfig.kernel_size, padding='valid',
                     activation='relu', strides=1))
    model.add(GlobalMaxPooling1D())
    
    model.add(Dense(CNNConfig.hidden_dims, activation='relu'))
    model.add(Dropout(CNNConfig.dropout))
    
    model.add(Dense(num_classes, activation='softmax'))
    
    adam = Adam(lr=CNNConfig.learn_rate)
    model.compile(loss='categorical_crossentropy',
                  optimizer=adam, metrics=['accuracy'])
    
    model.summary()
    
    plot_model(model, to_file='./models/simple_cnn/simple_cnn.png', show_shapes=True, show_layer_names=False)
    
    return model


model = simple_cnn(SimpleCNNConfig)
# 训练模型
history = model.fit(x_data, x_labels,
          batch_size=SimpleCNNConfig.batch_size, epochs=SimpleCNNConfig.epochs,
          validation_data=(y_data, y_labels))

# 模型评估
test_loss, test_acc = model.evaluate(z_data, z_labels)

# 模型预测
y_pred = model.predict_classes(y_data)

# 结果绘图至本地
plt_model(history,  y_labels, y_pred, plot_img_path='./models/simple_cnn')


## 模型保存
#save_path = './models/simple_cnn/simple_cnn.h5'
#model.save(save_path)
## 模型加载
#model = load_model(save_path)


