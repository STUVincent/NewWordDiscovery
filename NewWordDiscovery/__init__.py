# -*- coding: utf-8 -*-
"""
******* 文档说明 ******
新词发现, 通过计算每个字间共同出现的概率，及其自由度判断其是否为新词
核心思想：
        凝固度  p_xy / (p_x * p_y)
            若词X 词Y 一起出现的概率除以其各出现概率，值越大，说明词X 词Y 经常出现在一起的概率越高
        自由度  sum(-pi*log(pi))
            若词X 词Y 两侧出现的词越多越杂，即其两侧取词的自由度越高，词X 词Y 越独立，
            若有一侧自由度很低，则说明 词X 词Y 不是单独出现，可能为 XYZ 词中一部分

通过设定最低概率、最低凝固度、自由度 来限制搜索到的词典数量
p_min（最小概率或频数）、co_min（凝固度） 越小，h_max（自由度） 越大查找到的词典数量越多，相对准确率也下降

参考资料： http://www.cnblogs.com/bigdatafly/p/5014597.html

若使用新的文本数据，请对应修改 get_corpus.py  下 get_word（） 函数中文本读取代码，返回文本数据迭代器

主要参数：
   --file_name  训练文件名称

    --level_s  CMD界面窗口显示日志级别. 【默认为INFO】
    --level_f  日志文件记录级别. 【默认为INFO】

    --batch_len  批次计算的文本字符串长度 。【 字符串长度减少可降低占用内存，默认1000000个字符就进入统计计算】
    --top_n  保存 top_n 个词组 参数设置越大，结果准确度越高，内存也增加, 在硬件配置允许的条件下应尽量调高 【默认 1000000】

    【常用设置 重要参数】
    --n_gram  提取的新词长度  默认为5。 即超过5个字符的新词不再处理
    --p_min  词出现的最小概率 （p_min = 3 整数则为频数， p_min = 0.00001 浮点数则为概率） 【dytpe: int, default 0.00001 】
    --co_min  最小凝固度，只有超过最小凝固度才继续判断自由度并进入下一步搜索  【dytpe: int, default 100】
    --h_min   最大自由度，若小于最大自由度，则认为词组不完整，为大词组中的一小部分 【dytpe: int, default 1.2】

# 当前项目: NewWordDiscovery
# 创建时间: 2018/10/5 16:50
# 开发作者: Vincent
# 创建平台: PyCharm Community Edition    python 3.5
# 版    本: V1.0
"""
import os
from .Main import new_word_discover  # 新词发现 主程序

#  当前文件路径 的上层路径
CWD = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))

#  当前子项目名称 NewWordDiscover
project_name = os.path.basename(os.path.abspath(os.path.dirname(__file__)))

# ############################ 创建文件夹 ##############################################
# 判断是否存在临时文件夹 ，若无则重新创建
if not os.path.isdir(os.path.join(CWD, 'temp')):
    os.mkdir(os.path.join(CWD, 'temp'))

# 判断是否存在结果文件夹 ，若无则重新创建
if not os.path.isdir(os.path.join(CWD, 'result')):
    os.mkdir(os.path.join(CWD, 'result'))

# 判断是否存在日志文件夹 ，若无则重新创建
if not os.path.isdir(os.path.join(CWD, 'log')):
    os.mkdir(os.path.join(CWD, 'log'))
