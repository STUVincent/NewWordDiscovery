# -*- coding: utf-8 -*-
"""
******* 文档说明 ******
获取语料程序，以迭代器方式返回， 若更换语料数据，请对应修改本脚本中的代码

# 当前项目: NewWordDiscovery
# 创建时间: 2018/10/5 16:59
# 开发作者: Vincent
# 创建平台: PyCharm Community Edition    python 3.5
# 版    本: V1.0
"""
import re
import csv
import os


# 文本数据读取 迭代器 【更换训练文本数据时，请对应修改此函数代码】
def get_corpus(file, data_col=None, txt_sep=None, encoding='utf8', clean=True):
    """
    :param file:         文件路径
    :param data_col:     提取文本的列序号 【从 0 开始】
    :param txt_sep:     非csv文件的切分字符
    :param encoding:    默认'utf8'
    :param clean:    正则清洗，只提取汉字、数字、字母   默认 True 【新词发现时必须为True模式】
    :return:   会话文本，迭代器
    """
    # 输入文件名时，默认其存放路径为 .\NLP\Data'
    if not os.path.isfile(file):
        #  当前文件路径 的上层路径， 'NLP' 所在目录   'C:\Users\Vincent\Desktop\NLP'
        cwd = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))
        file = os.path.join(cwd, 'Data', file)

    # 正则清洗，只提取汉字、数字、字母
    if clean:
        # 正则表达式转换，只提取汉字、数字、字母
        re_clean = re.compile('[^\u4e00-\u9fa5 a-zA-Z0-9]')
        # 将多个空格 替换成一个空格
        re_sub = re.compile(' +')

        # 读取 CSV 文件数据
        if file[-3:] == 'csv':
            for line_data in csv.reader(open(file, encoding=encoding, errors='ignore')):
                corpus = line_data[data_col]  # csv 文件第 data_col 列为文本数据

                # 若文本长度大于0， 则通过迭代器输出
                if len(corpus) > 0:
                    # 正则清洗
                    corpus = re.sub(re_clean, ' ', corpus)
                    corpus = re.sub(re_sub, ' ', corpus)
                    yield corpus

        # 读取 其它 文件数据
        else:
            for line_data in open(file, encoding=encoding, errors='ignore'):
                corpus = line_data.split(txt_sep)[data_col]  # txt 文件第 data_col 列为文本数据
                # 若文本长度大于0， 则通过迭代器输出
                if len(corpus) > 0:
                    # 正则清洗
                    corpus = re.sub(re_clean, ' ', corpus)
                    corpus = re.sub(re_sub, ' ', corpus)
                    yield corpus

    # 提取原文、标签
    else:
        # 读取 CSV 文件数据
        if file[-3:] == 'csv':
            for line_data in csv.reader(open(file, encoding=encoding, errors='ignore')):
                corpus = line_data[data_col]  # csv 文件第 data_col 列为文本数据
                yield corpus

        # 读取 其它 文件数据
        else:
            for line_data in open(file, encoding=encoding, errors='ignore'):
                line_data = line_data.split(txt_sep)  # txt 文件以txt_sep为分隔符
                corpus = line_data[data_col]  # csv 文件第 data_col 列为文本数据
                yield corpus

# 文件打开配置调试
if __name__ == '__main__':
    corpus_data = get_corpus(r'C:\Users\Vincent\Desktop\NewWordDiscovery\Data\java.txt', data_col=0, txt_sep='\n',
                             encoding='utf-8', clean=True)

    for i, corpus_i in enumerate(corpus_data):
        print(i, corpus_i[:30])
        if i > 100:
            break
