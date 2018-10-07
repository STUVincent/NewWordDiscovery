# -*- coding: utf-8 -*-
"""
******* 文档说明 ******
通过 SlideCutWord 脚本 提取的词出现次数统计数据 计算 n_gram 下各个新词的 凝固度、自由度

并通过 p_min（最小概率或频数）、co_min（凝固度）、h_max（自由度） 的设置阈值 找出训练样本中可能性最大的用户词典

# 当前项目: NewWordDiscovery
# 创建时间: 2018/10/5 16:57
# 开发作者: Vincent
# 创建平台: PyCharm Community Edition    python 3.5
# 版    本: V1.0
"""
import os
import pickle
import time
from math import log
import logging
from multiprocessing import Process, Queue, cpu_count
from .LOG import logger_set  # 日志设置文件

logger = logging.getLogger('NLP')


# 以信息熵的方式 计算自由度 sum(-pi*log(pi))
def get_freedom(word_count):
    """
    :param word_count: # 每个词组出现的次数 【1，2，4，6，2】
    :return:  词组次数列表 熵值， 即代表词的自由度
    """
    word_count_sum = sum(word_count)  # 词数量
    entropy = 0
    for word_x in word_count:
        p = word_x / word_count_sum
        entropy = entropy - p * log(p, 2)
    return entropy


# 搜索 3 个字以上词
def search_n_word(process_i, queue_data, n_gram, args, p_min=0.00001, co_min=100, h_min=2):
    """
    :param process_i:
    :param queue_data:
    :param n_gram:
    :param args:  参数字典
    :param p_min:    词出现的最小概率 （p_min = 3 整数则为频数， p_min = 0.00001 浮点数则为概率）
    :param co_min:   最小凝固度，只有超过最小凝固度才继续判断自由度并进入下一步搜索
    :param h_min:    最大自由度，若小于最大自由度，则认为词组不完整，为大词组中的一小部分
    :return:
    """
    # 日志创建设置
    logger_set(path=args.path_log, s_level=args.level_s, f_level=args.level_f,
               name="process%d_%d_ngram" % (process_i, n_gram))

    logger_i = logging.getLogger("process%d_%d_ngram" % (process_i, n_gram))

    # 多进程临时文件夹
    temp_path = os.path.join(args.CWD, 'temp')
    with open(os.path.join(temp_path, 'WordCount_%s_001.tmp' % args.file_name), 'rb') as f_read_tmp:
        # 读取 文本行数 及 各词组词频数
        word_1_count = pickle.load(f_read_tmp)

    with open(os.path.join(temp_path, 'WordCount_%s_%03d.tmp' % (args.file_name, n_gram-1)), 'rb') as f_read_tmp:
        # 读取 文本行数 及 各词组词频数
        word_1n_count = pickle.load(f_read_tmp)

    with open(os.path.join(temp_path, 'WordCount_%s_%03d.tmp' % (args.file_name, n_gram)), 'rb') as f_read_tmp:
        # 读取 文本行数 及 各词组词频数
        word_n_count = pickle.load(f_read_tmp)

    with open(os.path.join(temp_path, 'WordCount_%s_%03d.tmp' % (args.file_name, n_gram+1)), 'rb') as f_read_tmp:
        # 读取 文本行数 及 各词组词频数
        word_n1_count = pickle.load(f_read_tmp)

    # 所有文本字符总长度
    word_count_sum = sum(word_1_count.values())

    # 若设置为概率，则将其转换成数值
    if isinstance(p_min, float):  # 若输入为浮点型数据【0，1】 则认为其为最小概率
        p_min = p_min * word_count_sum

    values_list = sorted(list(word_n_count.values()), reverse=True)

    word_no = 0  # 符合频数要求的词数量
    for word_no, x in enumerate(values_list):
        if x < p_min:
            break
    # 满足频数要求的词 及对应出现次数列表
    word_count_list = word_n_count.most_common(word_no + 1)

    logger_i.info('{:d} n_gram  满足最低概率词数量： {:d} '.format(n_gram, word_no + 1))

    # 若满足最低概率词的数量 超过 Top_n 值的一半，则 Top_n 可能设置过低，将导致部分低频词无法找到
    if word_no + 1 > args.top_n*0.5:
        logger_i.warning('参数 top_n {} 可能设置太小！'.format(args.top_n))

    # 搜索结果列表
    search_result = []
    # 判断每个符合频数要求的词 凝固度、 自由度 是否满足要求
    for i, (word_i, word_i_count) in enumerate(word_count_list):
        print('\r%2d: %-8d  ' % (process_i, i), end='')
        # 凝聚度
        co_f = word_count_sum * word_i_count / ((word_1_count[word_i[0]]+1) * (word_1n_count[word_i[1:]]+1))
        co_b = word_count_sum * word_i_count / ((word_1n_count[word_i[:-1]]+1) * (word_1_count[word_i[-1]]+1))
        # 满足凝聚度要求的 继续计算其左右自由度
        co = min(co_f, co_b)  # TODO  min | max | avg ??????????
        if co > co_min:
            front_word_num = []
            back_word_num = []

            # result_count_3 越大，数据越稀疏时，此方法效率越高
            for word_n1_i in word_n1_count:
                if word_n1_i[1:] == word_i:
                    front_word_num.append(word_n1_count[word_n1_i])
                if word_n1_i[:-1] == word_i:
                    back_word_num.append(word_n1_count[word_n1_i])

            front_freedom = get_freedom(front_word_num)
            back_freedom = get_freedom(back_word_num)

            # 输出满足自由度要求的词组
            if min(front_freedom, back_freedom) > h_min:
                search_result.append([word_i, n_gram, word_i_count, co, front_freedom, back_freedom])
                logger_i.debug('{},{},{},{:.1f},{:.3f},{:.3f}'.format
                               (word_i, n_gram, word_i_count, co, front_freedom, back_freedom))

    # 将词搜索结果 保存到临时文件中
    with open(os.path.join(temp_path, 'NewWordResult_%s_%d_ngram.tmp' % (args.file_name, n_gram)), 'wb') as f:
        pickle.dump(search_result, f)

    queue_data.put({process_i: 'OVER'})
    logger_i.info('Process_i {:d}  Finish!    '.format(process_i))


# 搜索 2 个字组成词
def search_2_word(process_i, queue_data, args, p_min=0.00001, co_min=100, h_min=2):
    """
    :param process_i:
    :param queue_data:
    :param args:    参数字典
    :param p_min:    词出现的最小概率 （p_min = 3 整数则为频数， p_min = 0.00001 浮点数则为概率）
    :param co_min:   最小凝固度，只有超过最小凝固度才继续判断自由度并进入下一步搜索
    :param h_min:    最大自由度，若小于最大自由度，则认为词组不完整，为大词组中的一小部分
    :return:
    """
    # 日志创建设置
    logger_set(path=args.path_log, s_level=args.level_s, f_level=args.level_f,
               name="process%d_%d_ngram" % (process_i, 2))
    logger_i = logging.getLogger("process%d_%d_ngram" % (process_i, 2))

    # 多进程临时文件夹
    temp_path = os.path.join(args.CWD, 'temp')
    with open(os.path.join(temp_path, 'WordCount_%s_001.tmp' % args.file_name), 'rb') as f_read_tmp:
        # 读取 文本行数 及 各词组词频数
        word_1_count = pickle.load(f_read_tmp)

    with open(os.path.join(temp_path, 'WordCount_%s_002.tmp' % args.file_name), 'rb') as f_read_tmp:
        # 读取 文本行数 及 各词组词频数
        word_2_count = pickle.load(f_read_tmp)

    with open(os.path.join(temp_path, 'WordCount_%s_003.tmp' % args.file_name), 'rb') as f_read_tmp:
        # 读取 文本行数 及 各词组词频数
        word_n1_count = pickle.load(f_read_tmp)

    # 所有文本字符总长度
    word_count_sum = sum(word_1_count.values())

    # 若设置为概率，则将其转换成数值
    if isinstance(p_min, float):  # 若输入为浮点型数据【0，1】 则认为其为最小概率
        p_min = p_min * word_count_sum

    values_list = sorted(list(word_2_count.values()), reverse=True)

    word_no = 0  # 符合频数要求的词数量
    for word_no, x in enumerate(values_list):
        if x < p_min:
            break
    # 满足频数要求的词 及对应出现次数列表
    word_count_list = word_2_count.most_common(word_no + 1)

    logger_i.info('文本字符串总长度： {:d} '.format(word_count_sum))
    logger_i.info('{:d} n_gram  满足最低概率词数量： {:d} '.format(2, word_no + 1))

    # 若满足最低概率词的数量 超过 Top_n 值的一半，则 Top_n 可能设置过低，将导致部分低频词无法找到
    if word_no + 1 > args.top_n*0.5:
        logger_i.warning('参数 top_n {} 可能设置太小！'.format(args.top_n))

    # 搜索结果列表
    search_result = []
    # 判断每个符合频数要求的词 凝固度、 自由度 是否满足要求
    for i, (word_i, word_i_count) in enumerate(word_count_list):
        print('\r%2d: %-8d  ' % (process_i, i), end='')
        # 凝聚度
        co = word_count_sum * word_i_count / (word_1_count[word_i[0]] * word_1_count[word_i[1]])
        # 满足凝聚度要求的 继续计算其左右自由度
        if co > co_min:
            front_word_num = []
            back_word_num = []

            # result_count_3 越大，数据越稀疏时，此方法效率越高
            for word_n1_i in word_n1_count:
                if word_n1_i[1:] == word_i:
                    front_word_num.append(word_n1_count[word_n1_i])
                if word_n1_i[:-1] == word_i:
                    back_word_num.append(word_n1_count[word_n1_i])

            front_freedom = get_freedom(front_word_num)
            back_freedom = get_freedom(back_word_num)

            # 输出满足自由度要求的词组
            if min(front_freedom, back_freedom) > h_min:
                search_result.append([word_i, 2, word_i_count, co, front_freedom, back_freedom])
                logger_i.debug('{},{},{},{:.1f},{:.3f},{:.3f}'.format
                               (word_i, 2, word_i_count, co, front_freedom, back_freedom))

    # 将词搜索结果 保存到临时文件中
    with open(os.path.join(temp_path, 'NewWordResult_%s_%d_ngram.tmp' % (args.file_name, 2)), 'wb') as f:
        pickle.dump(search_result, f)

    queue_data.put({process_i: 'OVER'})
    logger_i.info('Process_i {:d}  Finish!    '.format(process_i))


def search_word(n_gram, process_i, queue_data, args, parameter):
    if n_gram == 2:
        search_2_word(process_i, queue_data, args, parameter[0], parameter[1], parameter[2])
    elif n_gram > 2:
        search_n_word(process_i, queue_data, n_gram, args, parameter[0], parameter[1], parameter[2])


# 读取多进程队列 中的数据
def read_queue_data(queue_data):
    result = {}
    # 循环读取队列中数据，直到读取结束
    while queue_data.qsize() > 0:
        value = queue_data.get(True)
        result[list(value.keys())[0]] = list(value.values())[0]
    return result


# 主程序
def word_discover(args, parameter, process_no=None):
    """
    :param args:  参数字典
    :param parameter:   搜索词的参数  n_gram: [p_min=0.00001, co_min=100, h_min=2]
    :param process_no:   进程数量，默认为 None， 即 CPU核数
    :return:
    """
    if process_no is None:
        process_no = cpu_count()

    for p_i in parameter:
        logger.info('{} n_gram  词出现最小概率 p_min:{}  最小凝聚度 co_min:{}  最小自由度 h_min:{}  '.
                    format(p_i, parameter[p_i][0], parameter[p_i][1], parameter[p_i][2]))

    logger.info('- ' * 30)
    logger.info(' {:d} 进程 n_gram 新词发现程序开始。。。。'.format(process_no))

    # 父进程创建Queue，并传给各个子进程：
    queue_data = Queue(len(parameter))  # 用于数据 传输   每次抽样为一个进程
    # 进程输出数据
    queue_data_out = {}
    # 创建进程列表
    process_list = {}

    # 进行多进程处理 每次最大同时运行的进行数为 设定的 process_no
    for process_i, n_gram_i in enumerate(parameter):
        logger.info('进程 {:d}/{:d} 进入处理池。。。'.format(process_i + 1, len(parameter)))

        # 创建进程
        process_list[process_i] = Process(target=search_word, args=(n_gram_i, process_i, queue_data, args,
                                                                    parameter[n_gram_i]))
        # 启动进程
        process_list[process_i].start()

        # 循环判断进行中的进程数量，完成一个进程后再加入另一个新进程
        while True:
            # 判断进行中的进程数量
            process_alive_no = 0
            for process_x in process_list.keys():
                if process_list[process_x].is_alive():
                    process_alive_no = process_alive_no + 1

            # 当少于指定进程数时，跳出循环，加入下一个进程
            if process_alive_no < process_no:
                break
            else:  # 等待 1 秒
                time.sleep(1)

        # 读取队列中数据 并更新输出结果字典
        queue_data_out.update(read_queue_data(queue_data))

    # 判断进程是否结束，等待所有进程结束
    for process_i in process_list.keys():
        # 进程未结束
        if process_list[process_i].is_alive():
            logger.info('进程 {:d} 等待结束中。。。   '.format(process_i + 1))

            process_list[process_i].join(10000)  # 等待进程结束，最长等待 10000 秒
            #            process_list[process_i].terminate()  ## 强行关闭进程

    time.sleep(2)  # 延迟 1 秒，缓冲时延

    # 读取队列中数据 并更新输出结果字典
    queue_data_out.update(read_queue_data(queue_data))

    # 判断 输出的数据是否与抽样次数一样
    if (len(parameter)) != len(queue_data_out):
        logger.warning('进程信息： {} '.format(queue_data_out))
        logger.warning('警告 ！！！  {} 个进程尚未结束。。。。'.format(len(parameter) - len(queue_data_out)))

    logger.info('进程信息： {} '.format(queue_data_out))
    logger.info('- ' * 30)
