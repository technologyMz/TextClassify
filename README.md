# 文本分类
## 数据集 
新闻分类数据集  
包含{'体育': 0, '娱乐': 1, '家居': 2, '房产': 3, '教育': 4, '时尚': 5, '时政': 6, '游戏': 7, '科技': 8, '财经': 9}十个类别，其中train文件50000条，val5000条，test10000条。  

## Naive Bayes
对于文本分类，本人不习惯一上来就搭个网络试试，先来个传统文本分类算法：
```python  
print(classification_report(y_labels, y_pre))
              precision    recall  f1-score   support

          体育       1.00      0.99      0.99      1000
          娱乐       0.93      0.98      0.96      1000
          家居       0.93      0.74      0.83      1000
          房产       0.81      0.86      0.83      1000
          教育       0.97      0.91      0.94      1000
          时尚       0.95      0.97      0.96      1000
          时政       0.91      0.94      0.92      1000
          游戏       0.95      0.97      0.96      1000
          科技       0.93      0.95      0.94      1000
          财经       0.93      0.99      0.96      1000

    accuracy                           0.93     10000
   macro avg       0.93      0.93      0.93     10000
weighted avg       0.93      0.93      0.93     10000
```
## NNS
下面试试神经网络，一般遵循“窄而深”的原则搭建网络，这里举的例子均较为简单，简单提供思路使用，且无论前面的贝叶斯还是这里的神经网络，均未做停用词处理。可根据个人需求定制细节。
### CNN
测试集准确率95.16%  
![img](https://github.com/MachineWei/TextClassify/blob/master/images/textcnn.png)
### LSTM
测试集准确率84.92%  
![img](https://github.com/MachineWei/TextClassify/blob/master/images/textlstm.png)





