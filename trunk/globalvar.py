#!/usr/bin/env python
# This Python file uses the following encoding: utf-8

# @package globalvar
# 功能：SF4800全局变量模块，定义全局变量，另外还可作为不同模块之间进行信息传递的管道
#
# 作者：Ma.chunqiang.
#
# 日期：2016-07-25.
#
# 文件：globalvar.py.

# import public module
import sys

# debug模式开关
DEBUGMODE = '0'

#调试模式,当调试模式开启的时候,可以迅速跳过一些无关的步骤,直接步入要害（比如可以跳过扫条码等一系列纷繁复杂的操作）
#另外在调试模式下还支持即使某个测试项目测试失败，依旧可以向下测试
#debug_mode = False
debug_mode = False

# 获取当前系统.
ENCODE_TYPE = sys.getfilesystemencoding()

## 站别名称
STATION = ''  # 站别名称

## 返回值定义.
ERROR_RT = '11'  # 错误返回值信息
SUCCESS_RT = '22'  # 成功返回值信息
OTHER_ERROR = '33'  # 警告返回值定义

## 程序配置文件名称.
CONFIG = 'config.ini'  # config文件的名称
CFG_INFOS = {}  # 用来存储config文件的内容

## 回车符重定义
ENTER = '\n'  # 重定义回车符的含义，当前为windows风格

MODE = ''  # 预定义的启动模式，default为CMD模式启动
ID = ''  # 预定义的通道ID

##初始化log保存路径、保存名称等变量的赋值
LOG_DIR = ''  # 详细日志保存路径
RUN_LOG = ''  # 脚本过程日志
CMD_LOG = ''  # 串口输入日志
TOP_LOG_FOLDER_NAME = ''  # top log文件夹名称

## 串口记录启动或停止的标志
Console_print_detect = ''

## 记录开始测试的时间
test_start_time_str = ''

## 记录获取的SN相关信息以及从CONFIG文件中获取的相关记录
getinfos = dict()  # 用了保存获取到的SN相关信息
getinfos2 = dict()  # 用来保存QC的时候获取的子卡sn信息
pninfo = dict()  # 用来保存从config文件中获取的产品相关信息

# # TODO
# getinfos['ps'] = 'Q07H4340001'
# getinfos['mac'] = '00:25:5d:c4:83:50'
# pninfo['PN'] = 'VX3100-101'

## 拷机模式
burnin_mode = 'A'

## telnet端口
TN = ''  # 用了记录连接的通道
telnet = ''
tn = ''
tn1 = ''
NPS_TN = ''

# 设置配置IP的wkdir
setIPworkdir = 'SHELL'

# 是否要进行管理网口等检查设置
MGMT = 'Y'

## PS以及BS前3码定义
ES6200prd_snlist = ['P/N', 'B/N', 'P/S', 'B/S', 'MAC']
PS = ' '
#Hw Info
#此类信息会根据实际情况，在程序运行得时候被修改
port_number = ''
BOARD_TYPE = '48X2Q4Z'

#配置的IP地址，临时保存作为后用
IP = ''

flag1 = ''
flag2 = ''

#数据库相关信息
DATABASE_INFOS = {}
#测试过程中的log记录
loginfos = {}
#测试记录的结果
flag = {}

test_start_time = ''
datetime_start_time = ''
test_end_time = ''
datetime_end_time = ''
duration = ''

PS = ''
MAC = ''
boardtype = ''
tt = 0
err_count = 0
