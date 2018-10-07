# -*- coding: utf-8 -*-
"""
******* 文档说明 ******
读取多进程提取的新词，提取并转换成CSV保存在 result 文件夹下

# 当前项目: NewWordDiscovery
# 创建时间: 2018/10/5 16:51 
# 开发作者: Vincent
# 创建平台: PyCharm Community Edition    python 3.5
# 版    本: V1.0
"""
import os
import pickle
import logging

logger = logging.getLogger('NLP')


def get_new_word(args):
    # 读取文件夹下所有文件名称
    file_list = os.listdir(os.path.join(args.CWD, 'temp'))
    # 提取新词发现对应的文件
    file_list = [file_i for file_i in file_list if 'NewWordResult_%s' % args.file_name in file_i]

    # 合并各个进程的搜索结果
    result_count = []
    for file_i in sorted(file_list, reverse=False):
        with open(os.path.join(args.CWD, 'temp', file_i), 'rb') as f_read_tmp:
            # 读取 文本行数 及 各词组词频数
            result_count_i = pickle.load(f_read_tmp)
            # 合并 搜索结果
            result_count.extend(result_count_i)
        logger.info("NewWordResult File:  {}  WordNum: {}".format(file_i, len(result_count_i)))

    # 保存到 CSV 文件 中
    csv_path = os.path.join(args.CWD, 'result',
                            'NewWordDiscovery_%s_%s.csv' % (args.file_name, args.Call_Time))
    with open(csv_path, 'w') as f_csv:
        # 打印标题
        print('词组,字数,频数,凝聚度,左自由度,右自由度,,词组,频数,凝聚度,左自由度,右自由度,词组,频数,凝聚度,左自由度,右自由度', file=f_csv)

        for j, new_word_i in enumerate(result_count):
            # 只提取不含空格的词组
            if ' ' not in new_word_i[0]:
                print_str = '%s,%d,%d,%.1f,%.3f,%.3f,' % (tuple(new_word_i))

                # 查看是否还有包含词， 如“4G套餐” 中包含“4G”和“套餐”
                similar_word = [r_i for r_i in result_count[:j] if r_i[0] in new_word_i[0]]

                for s_word_i in similar_word:
                    print_str = '%s,%s,%d,%.1f,%.3f,%.3f' % (print_str, s_word_i[0], s_word_i[2], s_word_i[3],
                                                             s_word_i[4], s_word_i[5])

                print(print_str, file=f_csv)

    logger.info("NewWordDiscovery path:  {}  ".format(csv_path))
    return csv_path
