#!/usr/bin/env python
# This Python file uses the following encoding: utf-8

# @package AutoPA6821_PreTest
# 功能：NewTAP生产测试应用模块，定义通用功能函数为主程序提供相关功能接口.
#
# 作者：hchen.
#
# 日期：2012-11-05.
#
# 文件：tcplib.py.

# import system module
import re
import time
import socket

# import our modules
import globalvar            # 一些全局变量

# 获取相关的全局变量
#
# 将本地的全局变量都指向到globalvar中全局变量
ENCODE_TYPE = globalvar.ENCODE_TYPE     # 文件默认的系统编码
ERROR_RT = globalvar.ERROR_RT           # 错误返回值
SUCCESS_RT = globalvar.SUCCESS_RT       # 成功返回值

## TCP通讯端口号.
#
# TCP通讯端口号，此端口号需与AutoTool的通讯端口号相对应.
PORT = 33891

## 消息模式.
MSGPATTERN = 'BEG\#\[\w+\s*\*\+\*\s*(.*)\]\#END'
## ID消息.
IDMSG = 'ID'             # BEG#[ID *+* CSn-COMn]#END
## 交互消息.
EXCHANGEMSG = 'EXCHANGE'       # BEG#[EXCHANGE *+* message]#END
## 运行日志消息.
RUNLOGMSG = 'RUNLOG'         # BEG#[RUNLOG*+* message]#END
## 交互日志消息.
CMDLOGMSG = 'CMDLOG'         # BEG#[CMDLOG *+* message]#END
## 拷机消息.
BURNINMSG = 'BURNIN'
## 状态消息.
STATUSMSG = 'STATUS'
## 输入消息.
INPUTMSG = 'INPUT'
## powercycle消息
PCYCLEMSG = 'PCYCLE'         # #BEG#[PCYCLE *+* message]#END
PCYCLEMSG_UP = 'PCYCLE_UP'      # powercycle上电
PCYCLEMSG_DOWN = 'PCYCLE_DOWN'    # powercycle下电
PCYCLEMSG_DONE = 'PCYCLE_DONE'    # powercycle上下电结束
## 应答消息.
RESPONSE = 'BEG#OK#END'
## 通信结束消息.
OVER = 'BEG#OVER#END'


## 重新编码字符.
#
# 将字符串strw从utf-8编码转换成ENCODE_TYPE编码.
def recode(strw):
    return strw.decode('UTF-8').encode(ENCODE_TYPE)


## 封装ID消息.
#
# 将ID消息封装成BEG#[ID *+* id]#END样式.
def idmsg(id):
    tmp = 'BEG#[ID *+* %s]#END' % recode(id.strip())
    return tmp


## 封装交互消息.
#
# 将交互消息封装成BEG#[EXCHANGE *+* exchange]#END样式.
def exchangemsg(msg):
    tmp = 'BEG#[EXCHANGE *+* %s]#END' % recode(msg)
    return tmp


## 封装拷机消息.
#
# 将拷机消息封装成BEG#[BURNIN *+* burnin]#END样式.
def burninmsg(msg):
    tmp = 'BEG#[BURNIN *+* %s]#END' % recode(msg)
    return tmp


## 封装输入消息.
#
# 将输入消息封装成BEG#[INPUT *+* input]#END样式.
def inputmsg(msg):
    tmp = 'BEG#[INPUT *+* %s]#END' % recode(msg)
    return tmp


## 封装状态消息.
#
# 将状态消息封装成BEG#[STATUS *+* status]#END样式.
def statusmsg(msg):
    tmp = 'BEG#[STATUS *+* %s]#END' % recode(msg)
    return tmp


## 封运行日志消息.
#
# 将运行日志消息封装成BEG#[RUNLOG *+* runlog]#END样式.
def runlogmsg(msg):
    tmp = 'BEG#[RUNLOG *+* %s]#END' % recode(msg)
    return tmp


## 封交互日志态消息.
#
# 将交互日志消息封装成BEG#[CMDLOG *+* cmdlog]#END样式.
def cmdlogmsg(msg):
    tmp = 'BEG#[CMDLOG *+* %s]#END' % recode(msg)
    return tmp


## 封PowerCycle消息.
#
# 将PowerCycle消息封装成BEG#[PCYCLE *+* msg]#END样式.
def pcyclemsg(msg, port):
    tmp = 'BEG#[PCYCLE *+* %s *+* %s]#END' % (recode(msg), port)
    return tmp


## 解封装消息.
#
# 将消息从已封装的形式剥离出来.
def getmsg(msg):
    tmp = msg[msg.find('BEG#') + 4:msg.find('#END')]
    return tmp


## 连接到AutoTool.
#
# 以socket方式与AutoTool建立TCP连接.
def ConectToServer():
    for n in range(0, 5):
        try:
            ip = socket.gethostbyname(socket.gethostname())
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, PORT))
            return sock
        except socket.error:
            time.sleep(1)
    return ERROR_RT


## 发送交互消息.
def SendExChangeMsg(id, msg):
    pattern = 'CS\d+\-COM\d+'
    p = re.compile(pattern)
    m = p.match(id)
    if not m:
        return ERROR_RT

    sock = ConectToServer()
    if sock == ERROR_RT:
        strw = recode('发送EXCHANG消息：连接到服务器失败！')
        print strw
        return ERROR_RT
    sock.send(idmsg(id))
    r = sock.recv(2048)
    if r != RESPONSE:
        strw = recode('发送EXCHANG消息：发送ID消息失败！')
        print strw
        sock.close()
        return ERROR_RT

    sock.send(exchangemsg(msg))
    r = sock.recv(2048)
    if r == OVER:
        strw = recode('发送EXCHANGE消息：接收消息失败！')
        print strw
        sock.close()
        return ERROR_RT
    else:
        sock.send(OVER)
        sock.close()
        return getmsg(r)


## 发送拷机消息.
def SendBurnInMsg(id, msg):
    pattern = 'CS\d+\-COM\d+'
    p = re.compile(pattern)
    m = p.match(id)
    if not m:
        return ERROR_RT

    sock = ConectToServer()
    if sock == ERROR_RT:
        strw = recode('发送BURNIN消息：连接到服务器失败！')
        print strw
        return ERROR_RT
    sock.send(idmsg(id))
    r = sock.recv(1024)
    if r != RESPONSE:
        strw = recode('发送BURNIN消息：发送ID消息失败！')
        print strw
        sock.close()
        return ERROR_RT

    sock.send(burninmsg(msg))
    r = sock.recv(1024)
    if r == OVER:
        strw = recode('发送BURNIN消息：接收消息失败！')
        print strw
        sock.close()
        return ERROR_RT
    else:
        sock.send(OVER)
        sock.close()
        return getmsg(r)


## 发送输入消息.
def SendInputMsg(id, msg):
    pattern = 'CS\d+\-COM\d+'
    p = re.compile(pattern)
    m = p.match(id)
    if not m:
        return ERROR_RT

    sock = ConectToServer()
    if sock == ERROR_RT:
        strw = recode('发送INPUT消息：连接到服务器失败！')
        print strw
        return ERROR_RT
    sock.send(idmsg(id))
    r = sock.recv(2048)
    if r != RESPONSE:
        strw = recode('发送INPUT消息：发送ID消息失败！')
        print strw
        sock.close()
        return ERROR_RT

    sock.send(inputmsg(msg))
    r = sock.recv(2048)
    if r == OVER:
        strw = recode('发送INPUT消息：接收消息失败！')
        print strw
        sock.close()
        return ERROR_RT
    else:
        sock.send(OVER)
        sock.close()
        return getmsg(r)


## 发送状态消息.
def SendStatusMsg(id, msg):
    pattern = 'CS\d+\-COM\d+'
    p = re.compile(pattern)
    m = p.match(id)
    if not m:
        return ERROR_RT

    sock = ConectToServer()
    if sock == ERROR_RT:
        strw = recode('发送STATUS消息连接到服务器失败！')
        print strw
        return ERROR_RT
    sock.send(idmsg(id))
    r = sock.recv(2048)
    if r != RESPONSE:
        strw = recode('发送STATUS消息：发送ID消息失败！')
        print strw
        sock.close()
        return ERROR_RT

    sock.send(statusmsg(msg))
    r = sock.recv(2048)
    if r != RESPONSE:
        strw = recode('发送STATUS消息：接收返回信息失败！')
        print strw
        sock.close()
        return ERROR_RT
    else:
        sock.send(OVER)
        sock.close()
        return SUCCESS_RT


## 发送运行日志消息.
def SendRunlogMsg(id, msg):
    pattern = 'CS\d+\-COM\d+'
    p = re.compile(pattern)
    m = p.match(id)
    if not m:
        return ERROR_RT

    sock = ConectToServer()
    if sock == ERROR_RT:
        strw = recode('发送RUNLOG消息连接到服务器失败！')
        print strw
        return ERROR_RT
    sock.send(idmsg(id))
    r = sock.recv(2048)
    if r != RESPONSE:
        strw = recode('发送RUNLOG消息：发送ID消息失败！')
        print strw
        sock.close()
        return ERROR_RT

    sock.send(runlogmsg(msg))
    r = sock.recv(2048)
    if r != RESPONSE:
        strw = recode('发送RUNLOG消息：接收返回信息失败！')
        print strw
        sock.close()
        return ERROR_RT
    else:
        sock.send(OVER)
        sock.close()
        return SUCCESS_RT


## 发交互日志消息.
def SendCmdlogMsg(id, msg):
    pattern = 'CS\d+\-COM\d+'
    p = re.compile(pattern)
    m = p.match(id)
    if not m:
        return ERROR_RT

    sock = ConectToServer()
    if sock == ERROR_RT:
        strw = recode('发送CMDLOG消息连接到服务器失败！')
        print strw
        return ERROR_RT
    sock.send(idmsg(id))
    r = sock.recv(2048)
    if r != RESPONSE:
        strw = recode('发送CMDLOG消息：发送ID消息失败！')
        print strw
        sock.close()
        return ERROR_RT

    sock.send(cmdlogmsg(msg))
    r = sock.recv(2048)
    if r != RESPONSE:
        strw = recode('发送CMDLOG消息：接收返回信息失败！')
        print strw
        sock.close()
        return ERROR_RT
    else:
        sock.send(OVER)
        sock.close()
        return SUCCESS_RT


## 发POWERCYCLE上电消息.
def SendPCycleUpMsg(id, port):
    pattern = 'CS\d+\-COM\d+'
    p = re.compile(pattern)
    m = p.match(id)
    if not m:
        return ERROR_RT

    sock = ConectToServer()
    if sock == ERROR_RT:
        strw = recode('发送PCYCLE上电消息连接到服务器失败！')
        print strw
        return ERROR_RT
    sock.send(idmsg(id))
    r = sock.recv(2048)
    if r != RESPONSE:
        strw = recode('发送PCYCLE上电消息：发送ID消息失败！')
        print strw
        sock.close()
        return ERROR_RT

    sock.send(pcyclemsg(PCYCLEMSG_UP, port))
    r = sock.recv(2048)
    if r != RESPONSE:
        strw = recode('发送PCYCLE上电消息：接收返回信息失败！')
        print strw
        sock.close()
        return ERROR_RT
    else:
        sock.send(OVER)
        sock.close()
        return SUCCESS_RT


## 发POWERCYCLE下电消息.
def SendPCycleDownMsg(id, port):
    pattern = 'CS\d+\-COM\d+'
    p = re.compile(pattern)
    m = p.match(id)
    if not m:
        return ERROR_RT

    sock = ConectToServer()
    if sock == ERROR_RT:
        strw = recode('发送PCYCLE下电消息连接到服务器失败！')
        print strw
        return ERROR_RT
    sock.send(idmsg(id))
    r = sock.recv(2048)
    if r != RESPONSE:
        strw = recode('发送PCYCLE下电消息：发送ID消息失败！')
        print strw
        sock.close()
        return ERROR_RT

    sock.send(pcyclemsg(PCYCLEMSG_DOWN, port))
    r = sock.recv(2048)
    if r != RESPONSE:
        strw = recode('发送PCYCLE下电消息：接收返回信息失败！')
        print strw
        sock.close()
        return ERROR_RT
    else:
        sock.send(OVER)
        sock.close()
        return SUCCESS_RT


## 发POWERCYCLE上下电结束消息.
def SendPCycleDoneMsg(id, port, msg):
    pattern = 'CS\d+\-PCYCLE'
    p = re.compile(pattern)
    m = p.match(id)
    if not m:
        return ERROR_RT

    sock = ConectToServer()
    if sock == ERROR_RT:
        strw = recode('发送PCYCLE下电消息连接到服务器失败！')
        print strw
        return ERROR_RT
    sock.send(idmsg(id))
    r = sock.recv(2048)
    if r != RESPONSE:
        strw = recode('发送PCYCLE下电消息：发送ID消息失败！')
        print strw
        sock.close()
        return ERROR_RT

    sock.send(pcyclemsg(msg, port))
    r = sock.recv(2048)
    if r != RESPONSE:
        strw = recode('发送PCYCLE下电消息：接收返回信息失败！')
        print strw
        sock.close()
        return ERROR_RT
    else:
        sock.send(OVER)
        sock.close()
        return SUCCESS_RT
