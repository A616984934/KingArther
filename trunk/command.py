#!/usr/bin/env python
# This Python file uses the following encoding: utf-8

# @package command
# 功能：生产命令交互模块，定义命令交互接口模块
#
# 作者：Ma.chunqiang
#
# 日期：2016-07-25
#
# 文件：command.py

# import system modules
import re

# import our modules
import work                 # 写日志，以及上传到ftp的相关函数
import globalvar            # 一些全局变量
from work import recode     # 从work那边获取recode

# 获取相关的全局变量
#
# 将本地的全局变量都指向到globalvar中全局变量
ENCODE_TYPE = globalvar.ENCODE_TYPE     # 文件默认的系统编码
ERROR_RT = globalvar.ERROR_RT           # 错误返回值
SUCCESS_RT = globalvar.SUCCESS_RT       # 成功返回值
OTHER_ERROR = globalvar.OTHER_ERROR     # 其他错误返回值
DEBUGMODE = globalvar.DEBUGMODE         # debug模式开关
ENTER = globalvar.ENTER                 # 回车符重定义

## 向telnet通道中发送指令
#
#发送指令后,侦测通道的返回信息,如果在timeout时间内侦测到返回结果与
#规定的正则表达式匹配则指令发送完毕,反之,如果没有侦测到则认为命令
#发送失败
def CmdExpect(tn, cmd, plist, timeout=5):
    """
    参数传递:   tn      telent连接通道
                cmd     写入通道的命令
                p       匹配telnet通道返回结果的正则表达式列表
                timeout 等待匹配结果的时间
    返回值:     ERROR_RT失败
                index   返回匹配正则表达式列表的索引
    """
    try:
        if not isinstance(plist, list):
            strw = recode('传入参数plist不为列表,请检查')
            print strw
            return ERROR_RT
        tn.read_very_eager()
        tn.write(cmd + ENTER)
        (index, match, data) = tn.expect(plist, timeout=timeout)
        #write data to cmd log
        work.writecmdlog(cmd)
        work.writecmdlog(data)
        if index == -1:
            strw = recode('命令%s返回值错误' % cmd)
            print strw
            #write strw to run log
            work.writerunlog(strw)
            return ERROR_RT

        return index

    except KeyboardInterrupt:
        strw = recode('程序执行中断!')
        print strw
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序异常退出!CmdSend,异常信息%s' % err)
        print strw
        return ERROR_RT


##向telent通道发送指令并且返回结果
#
#发送命令之后侦测通道的返回值是否与规定的正则表达式匹配,
#如果匹配则返回匹配的结果
def CmdGet(tn, cmd, plist, timeout=5):
    """send command to the telnet tn channel
    input:  tn(telnet connection channel)
            cmd(the command to be written to the connection channel)
            plist(the regular expression list which is for detecting)
            timeout(default value is 5s)
    return: ERROR_RT(send command fail)
            data(the return info from the telnet channel)
    """
    try:
        import time

        if not isinstance(plist, list):
            strw = recode('传入参数plist不为列表,请检查')
            print strw
            return ERROR_RT
        tn.read_very_eager()
        for char in cmd:
            tn.write(char)
            time.sleep(0.01)

        tn.write(ENTER)
        (index, match, data) = tn.expect(plist, timeout=timeout)
        #write data to cmd log
        work.writecmdlog(cmd)
        work.writecmdlog(data)
        if index == -1:
            strw = recode('命令%s的返回值错误' % cmd)
            print strw
            #write strw to run log
            work.writerunlog(strw)
            return ERROR_RT

        return data
    except KeyboardInterrupt:
        strw = recode('程序执行中断!')
        print strw
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[command.CmdExpect]异常退出,异常信息%s' % err)
        print strw
        return ERROR_RT
        
def ExecuteCommand(tn,cmd_dict):
    '''Execute Command and check its return value'''
    cmd      = cmd_dict['cmd']
    prompt   = cmd_dict['prompt']
    waittime = int(cmd_dict['waittime'])
    strmatch = cmd_dict['strmatch']

    pattern = re.escape(cmd[0:4])+'.+'+prompt
    prompt_match = re.compile(pattern,re.IGNORECASE | re.DOTALL)
    rt = CmdGet(tn,cmd,[prompt_match],int(waittime))
    if rt == ERROR_RT:return ERROR_RT
    p = re.compile(strmatch,re.IGNORECASE | re.DOTALL)
    if p.search(rt) == None:
        strw = recode('command %s 执行失败!' %cmd)
        print strw
        work.writerunlog(strw)
        return ERROR_RT

    return SUCCESS_RT


##向telent通道发送指令并且返回结果
#
#发送命令之后不管是否匹配,均返回匹配的结果
#返回的结果都是一个数组的格式
def CmdReturn(tn, cmd, plist, timeout=5):
    """send command to the telnet tn channel
    input:  tn          telnet连接通道
            cmd         输入的命令
            plist       与返回结果相匹配的正则表达式列表
            timeout     等待匹配结果的时间
    return: (index, data)   index为匹配的正则表达式列表的索引
    """
    try:
        if not isinstance(plist, list):
            strw = recode('传入参数plist不为列表,请检查')
            print strw
            return ERROR_RT, ERROR_RT
        tn.read_very_eager()
        tn.write(cmd + ENTER)
        (index, match, data) = tn.expect(plist, timeout=timeout)
        #write data to cmd log
        work.writecmdlog(cmd)
        work.writecmdlog(data)
        if index == -1:
            strw = recode('命令%s的返回值不在plist列表中' % cmd)
            print strw
            #write strw to run log
            work.writerunlog(strw)
            return index, data

        return index, data
    except KeyboardInterrupt:
        strw = recode('程序执行中断!')
        print strw
        return OTHER_ERROR, OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[cmd.CmdExpect]异常退出,异常信息%s' % err)
        print strw
        return ERROR_RT, ERROR_RT


##连续发送多条命令
#
#主要用在配置vlan规则,uboot环境变量设置等
#这些命令已经在config.ini中得到统一,一系列的命令仅仅放到
#一个section下面,且option已经提前定义好
def CmdMultiSend(tn, section, plist, timeout=5):
    """send a serial of command to the telnet channel
    传入参数:    section(config中的section名字)
                 plist(返回值匹配的正则表达式列表)
    返回:        SUCCESS_RT(命令执行成功)
                 ERROR_RT(命令执行失败)
    """
    try:
        cfginfos = globalvar.CFG_INFOS
        num = cfginfos[section]['number']
        for i in range(1, int(num) + 1):
            idd = 'cmd' + str(i)
            cmd = cfginfos[section][idd]
            #print cmd
            rt = CmdGet(tn, cmd, plist, timeout=timeout)
            if rt == ERROR_RT:
                return ERROR_RT

            if cmd.find('wget') or cmd.find('tftp'):
                p_list = []
                p1 = re.compile('File\s*not\s*found', re.IGNORECASE)
                p2 = re.compile('no\s*such\s*file\s*or\s*directory', re.IGNORECASE)
                p_list.append(p1)
                p_list.append(p2)
                for p in p_list:
                    s = p.search(rt)
                    if s:
                        strw = recode('命令%s返回结果有误' % cmd)
                        print strw
                        return ERROR_RT

        return SUCCESS_RT
    except KeyboardInterrupt:
        strw = recode('程序执行中断!')
        print strw
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[command.CmdMultiSend]异常退出,异常信息%s' % err)
        print strw
        return ERROR_RT


def CmdExpectNPS(tn, cmd, plist, timeout=5):
    """
    参数传递:   tn      telent连接通道
                cmd     写入通道的命令
                p       匹配telnet通道返回结果的正则表达式列表
                timeout 等待匹配结果的时间
    返回值:     ERROR_RT失败
                index   返回匹配正则表达式列表的索引
    """
    try:
        NPS_ENTER = '\r'
        if not isinstance(plist, list):
            strw = recode('传入参数plist不为列表,请检查')
            print strw
            return ERROR_RT
        tn.read_very_eager()
        tn.write(cmd + NPS_ENTER)
        (index, match, data) = tn.expect(plist,timeout=timeout)
        work.writecmdlog(cmd)
        work.writecmdlog(data)
        if index == -1:
            strw = recode('命令%s返回值错误' %cmd)
            work.writerunlog(strw)
            return ERROR_RT

        return index

    except KeyboardInterrupt:
        strw = recode('程序执行中断!')
        print strw
        return OTHER_ERROR
    except Exception,err:
        strw = recode('程序异常退出!CmdSend,异常信息%s'%err)
        print strw
        return ERROR_RT
