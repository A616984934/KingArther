#!/usr/bin/env python
# This Python file uses the following encoding: utf-8

# @package AutoTest
# 功能：定义一些相对纯粹的函数或者类，供其它各个模块来使用
#
# 作者：MaChunqiang
#
# 日期：2017-4-13
#
# 文件：common.py

# import system modules
import os
import sys
import time
import socket
import zipfile
import ftplib
from ftplib import FTP
import shutil

# import our modules
import tcplib               # 与autotool通信的函数
import globalvar            # 一些全局变量

# 获取相关的全局变量
#
# 将本地的全局变量都指向到globalvar中全局变量
ENCODE_TYPE = globalvar.ENCODE_TYPE     # 文件默认的系统编码
ERROR_RT = globalvar.ERROR_RT           # 错误返回值
SUCCESS_RT = globalvar.SUCCESS_RT       # 成功返回值
OTHER_ERROR = globalvar.OTHER_ERROR     # 其他错误返回值
DEBUGMODE = globalvar.DEBUGMODE         # debug模式开关
ENTER = globalvar.ENTER                 # 回车符重定义


# 将字符串strw从utf-8编码转换成ENCODE_TYPE编码.
def recode(strw):
    return strw.decode('UTF-8').encode(ENCODE_TYPE)


# 将字符串strw从ENCODE_TYPE编码转换成utf-8编码.
def unrecode(strw):
    return strw.decode(ENCODE_TYPE).encode('UTF-8')


# 获得当前路径
def cur_file_dir():
    path = sys.path[0]
    if os.path.isdir(path):
        return path
    if os.path.isfile(path):
        return os.path.dirname(path)




if __name__ == '__main__':
    logdir = r'D:\PyWork\autoAC2768_NewModule\logdir\Prd_201404101803'
    print '---------------------'
    print os.getcwd()
    print '---------------------'
    print logdir
    MakeZip(logdir, True)