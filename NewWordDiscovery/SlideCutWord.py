# -*- coding: utf-8 -*-
"""
******* 文档说明 ******
多进程滑动切词
【步长为1，指定窗口数下滑动提取文本， 统计各文本频数】
1、 文本保存方式若与样本不同，可修改 get_corpus.py  下 get_word（） 函数中文本读取代码，返回文本数据迭代器
2、 word_windows_list   文本窗口大小列表。 可根据需要设置不同长度，程序中每个长度独立进入一个进程中处理
3、 batch  每批次进行统计的文本行数， 数值调小可降低内存占用，相反运行时间将相对较长
4、 top_n  保存频数前 top_n 的文本

结果保存在 temp 文件夹中 如 WordCount_temp_024.tmp  数值代表窗口大小 【pickle 文件，可直接读取 result_count】

# 当前项目: NewWordDiscovery
# 创建时间: 2018/10/5 16:55
# 开发作者: Vincent
# 创建平台: PyCharm Community Edition    python 3.5
# 版    本: V1.0
"""
import os
from collections import Counter, deque
from multiprocessing import Process, Queue, cpu_count
import pickle
import time
import logging
from .LOG import logger_set  # 日志设置文件
from .get_corpus import get_corpus  # 文本读取文件

logger = logging.getLogger('NLP')


# 计算指定窗口长度 词组 出现的频数，返回TopN个词组 及 频数
def count_word(process_i, queue_data, windows, args):
    """
    :param process_i:  进程序号
    :param queue_data:  数据传输
    :param windows:  n_gram 窗口大小
    :param args:  参数字典
    :return:
    """
    # 日志创建设置
    logger_set(path=args.path_log, s_level=args.level_s, f_level=args.level_f, name="process_%d" % process_i)
    logger_i = logging.getLogger("process_%d" % process_i)

    # 创建队列 存放切词词组
    result_deque = deque()
    result_count = Counter(result_deque)

    # 读取文本，迭代器
    corpus_iterator = get_corpus(args.path_corpus, data_col=args.f_data_col, txt_sep=args.f_txt_sep,
                                 encoding=args.f_encoding)

    line_i = 0   # 文本读取行序号
    corpus = ''   # 文本合并
    # 循环计算文档中词组出现次数
    for line_i, corpus_i in enumerate(corpus_iterator):
        corpus = corpus + corpus_i
        # corpus = '%s %s' % (corpus, corpus_i)

        # 为节省内存，每读取一定数据后进入统计，清空原数据。
        if len(corpus) > args.batch_len:  # 判断大于指定字符数量开始滑动取词
            # 将当前会话文本 按设置窗口滑动取值，小于窗口值的忽略
            for i in range(len(corpus)-windows + 1):
                result_deque.append(corpus[i:(i+windows)])

            print('\r%3d WordWindows:%2d  line: %d      ' % (process_i, windows, line_i), end='')
            logger_i.debug('%3d WordWindows:%2d    Corpus line: %d' % (process_i, windows, line_i))
            # 更新各个词组出现次数
            result_count.update(Counter(result_deque))
            result_deque.clear()  # 清空队列
            corpus = ''  # 文本清空

            # 只保存前 top_n 个词组 减少内存
            result_count = Counter(dict(result_count.most_common(args.top_n)))

    # ####### 继续处理剩余的文本
    # 将当前会话文本 按设置窗口滑动取值，小于窗口值的忽略
    for i in range(len(corpus) - windows + 1):
        result_deque.append(corpus[i:(i + windows)])

    print('\r%3d WordWindows:%2d  line: %d      ' % (process_i, windows, line_i), end='')
    logger_i.debug('%3d WordWindows:%2d    Corpus line: %d' % (process_i, windows, line_i))

    # 更新各个词组出现次数
    result_count.update(Counter(result_deque))

    # 只保存前 top_n 个词组 减少内存
    result_count = Counter(dict(result_count.most_common(args.top_n)))

    # 返回 出现最大的前N个词组及对应数量
    with open(os.path.join(args.CWD, 'temp',
                           'WordCount_%s_%03d.tmp' % (os.path.basename(args.path_corpus), windows)), 'wb') as f:
        pickle.dump(result_count, f)

    queue_data.put({process_i: 'OVER'})
    logger_i.info('Process_i  %d  Finish!    ' % process_i)


# 读取多进程队列 中的数据
def read_queue_data(queue_data):
    result = {}
    # 循环读取队列中数据，直到读取结束
    while queue_data.qsize() > 0:
        value = queue_data.get(True)
        result[list(value.keys())[0]] = list(value.values())[0]
    return result


# 多进程 词组统计程序
def multi_count_word(args, process_no=None):
    """
    :param args:  参数字典
    :param process_no:   进程数量，默认为 None， 即 CPU核数
    :return:
    """
    if process_no is None:
        process_no = cpu_count()

    logger.info('- ' * 30)
    logger.info(' {:d} 进程 n_gram 词组统计程序开始。。。。'.format(process_no))

    # 词组长度 n_gram 窗口列表， 【1，2，3 。。。】
    word_windows_list = range(1, args.n_gram + 2)
    # 父进程创建Queue，并传给各个子进程：
    queue_data = Queue(len(word_windows_list))  # 用于数据 传输   每次抽样为一个进程
    # 进程输出数据
    queue_data_out = {}
    # 创建进程列表
    process_list = {}

    # 进行多进程处理 每次最大同时运行的进行数为 设定的 process_no
    for process_i, Line_set_i in enumerate(word_windows_list):
        logger.info('进程 {:d}/{:d} 进入处理池。。。'.format(process_i + 1, len(word_windows_list)))

        # 创建进程
        process_list[process_i] = Process(target=count_word, args=(process_i + 1, queue_data,
                                                                   word_windows_list[process_i], args))
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

    time.sleep(1)  # 延迟 1 秒，缓冲时延

    # 读取队列中数据 并更新输出结果字典
    queue_data_out.update(read_queue_data(queue_data))

    # 判断 输出的数据是否与抽样次数一样
    if len(word_windows_list) != len(queue_data_out):
        logger.warning('进程信息： {} '.format(queue_data_out))
        logger.warning('警告 ！！！  {} 个进程尚未结束。。。。'.format(len(word_windows_list) - len(queue_data_out)))

    logger.info('进程信息： {} '.format(queue_data_out))
    logger.info('- ' * 30)
