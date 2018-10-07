# -*- coding: utf-8 -*-
"""
******* 文档说明 ******
日志设置 文件

# 当前项目: NewWordDiscovery
# 创建时间: 2018/10/5 17:00
# 开发作者: Vincent
# 创建平台: PyCharm Community Edition    python 3.5
# 版    本: V1.0
"""
import logging
import os


# 日志文件设置，可将日志文件分别打印到前端及日志中
def logger_set(path, f_level='DEBUG', s_level='DEBUG', name='main'):
    """
    :param path:   日志保存路径
    :param s_level:   控制台输出的日志级别默认为 DEBUG   # DEBUG，INFO，WARNING，ERROR，CRITICAL
    :param f_level:   日志文件输出的日志级别默认为 DEBUG   # DEBUG，INFO，WARNING，ERROR，CRITICAL
    :param name:   日志名称，默认为 'main'
    """
    # 创建一个logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # 输入为文件名时，默认其存放路径为 log 文件夹下。 输入为文件绝对路径时保存到路径文件上【方便与其它代码合并日志】
    if not os.path.isfile(path):
        #  当前文件路径 的上层路径， 'NLP' 所在目录   'C:\Users\Vincent\Desktop\NLP_Project'
        cwd = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))
        path = os.path.join(cwd, 'log', path)

    # 创建一个handler，用于写入日志文件 【默认为 DEBUG 级别】
    fh = logging.FileHandler(path)
    if f_level == 'INFO':
        fh.setLevel(logging.INFO)  # DEBUG，INFO，WARNING，ERROR，CRITICAL
    elif f_level == 'WARNING':
        fh.setLevel(logging.WARNING)  # DEBUG，INFO，WARNING，ERROR，CRITICAL
    elif f_level == 'ERROR':
        fh.setLevel(logging.ERROR)  # DEBUG，INFO，WARNING，ERROR，CRITICAL
    elif f_level == 'CRITICAL':
        fh.setLevel(logging.CRITICAL)  # DEBUG，INFO，WARNING，ERROR，CRITICAL
    else:
        fh.setLevel(logging.DEBUG)  # DEBUG，INFO，WARNING，ERROR，CRITICAL

    # 创建一个handler，用于输出到控制台 【Level 可由用户设置，默认为 DEBUG 级别】
    sh = logging.StreamHandler()

    if s_level == 'INFO':
        sh.setLevel(logging.INFO)  # DEBUG，INFO，WARNING，ERROR，CRITICAL
    elif s_level == 'WARNING':
        sh.setLevel(logging.WARNING)  # DEBUG，INFO，WARNING，ERROR，CRITICAL
    elif s_level == 'ERROR':
        sh.setLevel(logging.ERROR)  # DEBUG，INFO，WARNING，ERROR，CRITICAL
    elif s_level == 'CRITICAL':
        sh.setLevel(logging.CRITICAL)  # DEBUG，INFO，WARNING，ERROR，CRITICAL
    else:
        sh.setLevel(logging.DEBUG)  # DEBUG，INFO，WARNING，ERROR，CRITICAL

    # 定义handler的输出格式
    formatter = '%(asctime)s %(name)s %(filename)s %(funcName)s %(lineno)4d %(levelname)-8s:  %(message)s'
    fh.setFormatter(logging.Formatter(formatter))

    formatter = '%(asctime)s %(levelname)-8s: %(message)s'
    sh.setFormatter(logging.Formatter(formatter))

    # 给logger添加handler
    logger.addHandler(fh)
    logger.addHandler(sh)


if __name__ == '__main__':
    # 当前文件路径 的上层路径， 'Code' 所在目录
    CWD = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))
    print('Current Path: %s' % CWD)
    # log_path_test = os.path.join(cwd, 'temp', 'test__%s.log' % os.path.basename(__file__))

    # 日志创建设置
    logger_set(path=os.path.join(CWD, '_test.log'), f_level='DEBUG', name="main")

    my_logger = logging.getLogger('main')
    my_logger.debug('this is debug info')
    my_logger.info('this is information')
    my_logger.warning('this is warning message')
    my_logger.error('this is error message')
    my_logger.fatal('this is fatal message, it is same as my_logger.critical')
    my_logger.critical('this is critical message')

    # 清空 my_logger 中的日志 handlers
    my_logger.handlers = []
    my_logger.debug('Clear Handlers!!!!!!!!!!!!!')  # 清空后，日志不再记录

    # 日志创建设置，创建另一个名称为 test 的logger, 若日志保存名称相同时，直接添加在同一文件中；若名称不同，另创建文件
    logger_set(path='_test.log', f_level='WARNING', s_level='WARNING', name="test")
    my_logger = logging.getLogger('test')
    my_logger.debug('test    this is debug info')
    my_logger.info('test    this is information')
    my_logger.warning('test    this is warning message')
