# -*- coding: utf-8 -*-
"""
******* 文档说明 ******
# 当前项目: NewWordDiscovery
# 创建时间: 2018/10/5 16:55 
# 开发作者: Vincent
# 创建平台: PyCharm Community Edition    python 3.5
# 版    本: V1.0
"""
import os
import time
import logging
from .SlideCutWord import multi_count_word  # 多进程切词计数
from .WordDiscovery import word_discover  # 新词发现程序
from .GetNewWord import get_new_word  # 提取各个进程找到的新词
from .LOG import logger_set  # 调用日志设置文件


# 新词发现程序中使用的 变量存储类
class Arguments:
    #  当前文件路径 的上层路径
    CWD = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))

    # 调用当前文件时的系统日期时间
    Call_Time = time.strftime('%Y%m%d%H%M%S', time.localtime())  # 初始化时间， 导入此文件时间，实例化时不变

    def __init__(self):
        self.start_time = time.time()  # 实例化时间

    # 打印当前存储类中的所有参数 取值
    def __repr__(self):
        arg_values = '\n'.join(['     {}: {}'.format(x, self.__getattribute__(x)) for x in dir(self) if x[0] != '_'])
        return 'Arguments Values:  \n{}'.format(arg_values)


# 新词发现调用程序
def new_word_discover(file, f_data_col=None, f_txt_sep=None, f_encoding='utf8',
                      n_gram=5, batch_len=100000, top_n=100000, p_min=0.0001, co_min=100, h_min=1.2,
                      level_s='INFO', level_f='DEBUG', log_path=None, process_no=None):
    """
    :param file:       待切词的文件 【绝对路径或文件名，若为文件名则默认存储路径为 .\\NLP\\Data】
    :param f_data_col: 提取数据的列序号 默认为None 【整数 从 0 开始】
    :param f_txt_sep:  txt 文件的切分字符  默认为None 【 csv 文件忽然此参数】
    :param f_encoding: 默认为utf8  utf8 | gbk
    :param n_gram:     提取的新词长度  默认为5。 即超过5个字符的新词不再处理
    :param batch_len:  批次计算的文本字符串长度 。【 字符串长度减少可降低占用内存，默认100000个字符就进入统计计算】
    :param top_n:      保存 top_n 个词组 参数设置越大，结果准确度越高，内存也增加, 在硬件配置允许的条件下应尽量调高 【默认 1000000】
    :param p_min:      词出现的最小概率 （p_min = 3 整数则为频数， p_min = 0.0001 浮点数则为概率）【默认 0.0001】
    :param co_min:     最小凝固度，只有超过最小凝固度才继续判断自由度并进入下一步搜索  【dytpe: int, default 100】
    :param h_min:      最大自由度，若小于最大自由度，则认为词组不完整，为大词组中的一小部分  【dytpe: int, default 1.2】
    :param level_s:    界面显示日志级别.  ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']  默认 INFO
    :param level_f:    日志文件记录级别.  ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']  默认 INFO
    :param log_path:   日志存储路径，默认为 None，默认存储到 .\\NLP\\log\\NLP_[当前时间].log
    :param process_no: 多进程处理的进程数，int 类型，默认为None 即 CPU 核数
    :return:
    """
    # ##################################### 参数设置 #############################################
    # 变量存储类
    args = Arguments()

    # 用户输入参数存储到类中
    args.f_data_col = f_data_col
    args.f_txt_sep = f_txt_sep
    args.f_encoding = f_encoding
    args.n_gram = n_gram
    args.batch_len = batch_len
    args.top_n = top_n
    args.p_min = p_min
    args.co_min = co_min
    args.h_min = h_min
    args.level_s = level_s
    args.level_f = level_f
    args.path_corpus = file  # 语料路径或语料名称
    args.file_name = os.path.basename(args.path_corpus)  # 语料名称

    # 设置日志名称或路径，加入到存储类中
    if log_path is None:    # 无用户输入路径，则默认存储到 .\NLP\log\NLP_20180627142417.log 中
        args.path_log = '%s_NewWordDiscover_%s.log' % ('NLP', args.Call_Time)
    else:  # 用户指定输入路径
        args.path_log = log_path

    # 若未创建日志，则创建日志 handler
    if len(logging.getLogger('NLP').handlers) == 0:
        logger_set(path=args.path_log, f_level=level_f, s_level=level_s, name='NLP')

    # ################################################################################################
    # 读取日志模块handler
    logger = logging.getLogger('NLP')

    logger.info('NewWordDiscover Setting {}'.format(args))
    logger.info('NewWordDiscover Starting......')

    # 滑动取词，并统计， 结果以 pickle 文件 临时存储到 temp 文件夹中
    multi_count_word(args, process_no=process_no)

    # 搜索词的参数  n_gram: [p_min=0.00001, co_min=100, h_min=2]
    search_word_parameter = dict()
    for n_gram_i in range(2, args.n_gram + 1):
        search_word_parameter[n_gram_i] = [args.p_min, args.co_min, args.h_min]  # [p_min=0.00001, co_min=100, h_min=2]
    # # 搜索词的参数  n_gram: [p_min=0.00001, co_min=100, h_min=2] 【手动设置各 n_gram 参数】
    #     search_word_par = {
    #         5: [0.0001, 100, 2],
    #         3: [0.0001, 100, 2],
    #         4: [0.0001, 100, 2],
    #         2: [0.0001, 100, 2]
    #     }

    # 新词搜索主程序
    word_discover(args, search_word_parameter, process_no=process_no)

    # 提取各个进程找到的新词
    result_csv = get_new_word(args)

    # 结束。 计算用时
    logger.info('NewWordDiscover Finish！ UsedTime {:.1f} Sec.\n'.format(time.time() - args.start_time))
    # TODO 结束当前新词发现程序， 清空logger的handlers  【是否有更好的结束方式？？？】
    logger.handlers = []

    return result_csv
