#!/usr/bin/env python
# This Python file uses the following encoding: utf-8

# @package AutoPA6821_PreTest
# 功能：NewTAP生产测试应用模块，定义通用功能函数为主程序提供相关功能接口.
#
# 作者：hchen.
#
# 日期：2014-03-12.
#
# 文件：connection.py.

# import system modules
import os
import re
import time
import telnetlib
import socket
import sys

# import our modules
import work  # 写日志，以及上传到ftp的相关函数
import connection  # 登陆板卡的一些函数，以及在板卡上切换工作路径的函数
import globalvar  # 一些全局变量
import command  # 一些常用的命令
from work import recode  # 从work那边获取recode
import special

# 获取相关的全局变量
#
# 将本地的全局变量都指向到globalvar中全局变量
ENCODE_TYPE = globalvar.ENCODE_TYPE  # 文件默认的系统编码
ERROR_RT = globalvar.ERROR_RT  # 错误返回值
SUCCESS_RT = globalvar.SUCCESS_RT  # 成功返回值
OTHER_ERROR = globalvar.OTHER_ERROR  # 其他错误返回值
DEBUGMODE = globalvar.DEBUGMODE  # debug模式开关
ENTER = globalvar.ENTER  # 回车符重定义


##telnet指定的ip和port
#
#默认的telnet port为23
def TelnetServer(ip, port='23'):
    """telnet the specified ip and port
    Input: ip, default port which is for telnet port
    return: tn(telnet success,the tn is the connection channel)
            OTHER_ERROR(KeyboardInterrupt)
            ERROR_RT(sth abnormal happen)
    """
    try:
        strw = recode('已经开始扫描串口输出，请给设备上电...')
        print strw
        work.writerunlog(strw)
        print ip, port
        tn = telnetlib.Telnet(ip, port)
        strw = recode('已经成功登陆设备')
        print strw
        return tn

    except socket.error:
        strw = recode('连接到设备失败！')
        print strw
        work.writerunlog(strw)
        return ERROR_RT
    except EOFError:
        strw = recode('登陆设备失败，请确保网线连接正常，保持网络通畅！')
        print strw
        work.writerunlog(strw)
        return ERROR_RT
    except KeyboardInterrupt:
        strw = recode('程序执行中断!')
        print strw
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序异常退出!TelnetServer,异常信息%s' % err)
        print strw
        return ERROR_RT


##telnet指定的ip和port
#
#默认的telnet port为23
def TelnetBoard(ip, port='23'):
    '''telnet the spicified ip and port
    imput: ip, default port which is for telnet port
    return: tn(telnet success,the tn is the connection channel)
            OTHER_ERROR(KeyboardInterrupt)
            ERROR_RT(sth abnormal happen)
    '''
    try:
        tn = telnetlib.Telnet(ip, port)
        tn.expect(['login:'], timeout=5)
        tn.write('root' + ENTER)
        pattern = 'Password:'
        p = re.compile(pattern, re.IGNORECASE | re.DOTALL)
        (index, match, data) = tn.expect([p], timeout=5)
        if index == -1:
            strw = recode('通过网络telnet到板卡失败,等待Password:失败')
            print strw
            work.writerunlog(strw)
            return ERROR_RT
        tn.write('embed220' + ENTER)
        pattern = '#'
        p = re.compile(pattern, re.IGNORECASE | re.DOTALL)
        (index, match, data) = tn.expect([p], timeout=5)
        if index == -1:
            strw = recode('通过网络telnet到板卡失败，等待#失败')
            print strw
            work.writerunlog(strw)
            return ERROR_RT
        strw = recode('以telnet方式登录板卡成功')
        print strw
        #work.writerunlog(strw)
        return tn
    except socket.error:
        strw = recode('连接到设备失败！')
        print strw
        work.writerunlog(strw)
        return ERROR_RT
    except EOFError:
        strw = recode('登陆设备失败，请确保网线连接正常，保持网络通畅！')
        print strw
        work.writerunlog(strw)
        return ERROR_RT
    except KeyboardInterrupt:
        strw = recode('程序执行中断!')
        print strw
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序异常退出!TelnetBoard,异常信息%s' % err)
        print strw
        return ERROR_RT


# reset board and goto Uboot
def ResetToUboot():
    """
    Reset Board and Goto Uboot
    """
    tn = globalvar.TN
    tn.write('reset' + ENTER)
    tn.write('reboot' + ENTER)

    #record console output and goto Uboot shell
    rt = connection.GoToUboot(tn)
    if rt == ERROR_RT or rt == OTHER_ERROR:
        strW = recode('FAIL-板卡进入Uboot界面失败')
        print strW
        work.writerunlog(strW)
        return
    else:
        return SUCCESS_RT


def ExitLcsh():
    """
    传入参数:   telnet通道
    返回值:     SUCCESS_RT(成功)
                ERROR_RT(失败)
    """
    try:
        import sys
        f_name = sys._getframe().f_code.co_name
        tn = globalvar.TN

        cmd = 'exit'
        pattern = 'Switch#'
        tn.write(cmd + ENTER)
        p = re.compile(pattern, re.DOTALL | re.IGNORECASE)
        (index, match, data) = tn.expect([p], timeout=10)
        work.writecmdlog(data)
        if index == -1:
            strw = recode('%s FAIL' % f_name)
            print strw
            work.writerunlog(strw)
            return ERROR_RT

        return SUCCESS_RT

    except KeyboardInterrupt:
        strw = recode('程序执行中断!')
        print strw
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序异常退出!%s,异常信息%s' % (f_name, err))
        print strw
        return ERROR_RT


def GotoLcsh():
    try:
        import sys
        f_name = sys._getframe().f_code.co_name
        tn = globalvar.TN

        cmd = 'lcsh'
        pattern = 'Password:'
        p = re.compile(pattern, re.DOTALL | re.IGNORECASE)
        tn.write(cmd + ENTER)
        (index, match, data) = tn.expect([p], timeout=10)
        work.writecmdlog(data)
        if index == -1:
            strw = recode('%s FAIL' % f_name)
            print strw
            work.writerunlog(strw)
            return ERROR_RT

        cmd = '!@#'
        pattern = 'lcsh#'
        p = re.compile(pattern, re.DOTALL | re.IGNORECASE)
        tn.write(cmd + ENTER)
        (index, match, data) = tn.expect([p], timeout=10)
        work.writecmdlog(data)
        if index == -1:
            strw = recode('%s FAIL' % f_name)
            print strw
            work.writerunlog(strw)
            return ERROR_RT

        return SUCCESS_RT

    except KeyboardInterrupt:
        strw = recode('程序执行中断!')
        print strw
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序异常退出!%s,异常信息%s' % (f_name, err))
        print strw
        return ERROR_RT


def ExitConfigTerminal():
    tn = globalvar.TN
    cmd = 'exit'
    tn.write(cmd + ENTER)
    tn.expect(['#'], timeout=5)


def GotoConfigTerminal():
    try:
        import sys
        f_name = sys._getframe().f_code.co_name
        tn = globalvar.TN

        cmd = 'configure terminal'
        pattern = re.escape('Switch(config)#')
        p = re.compile(pattern, re.DOTALL | re.IGNORECASE)
        tn.write(cmd + ENTER)
        (index, match, data) = tn.expect([p], timeout=10)
        work.writecmdlog(data)
        if index == -1:
            strw = recode('%s FAIL' % f_name)
            print strw
            work.writerunlog(strw)
            return ERROR_RT

        return SUCCESS_RT

    except KeyboardInterrupt:
        strw = recode('程序执行中断!')
        print strw
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序异常退出!%s,异常信息%s' % (f_name, err))
        print strw
        return ERROR_RT


##exit from the BCM
#
#退出BCM界面
def ExitCtcCli():
    """
    传入参数:   telnet通道
    返回值:     SUCCESS_RT(成功)
                ERROR_RT(失败)
    """
    try:
        tn = globalvar.TN
        cmd = 'exit'
        tn.write(cmd + ENTER)
        tn.expect(['#'], timeout=5)

        cmd = 'exit'
        tn.write(cmd + ENTER)
        tn.expect(['#'], timeout=5)

        return SUCCESS_RT

    except KeyboardInterrupt:
        strw = recode('程序执行中断!')
        print strw
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序异常退出!ExitCtcCli,异常信息%s' % err)
        print strw
        return ERROR_RT


##goto the BCM mode
#
#一般而言进入BCM的命令是一样的,所以把进入BCM的命令写入函数内
def GotoCtcCli():
    """
    传入参数:   telnet通道
    返回值:     SUCCESS_RT(成功)
                ERROR_RT(失败)
    """
    try:
        import sys
        f_name = sys._getframe().f_code.co_name
        tn = globalvar.TN

        cmd = 'vtysh'
        pattern = ':'
        p = re.compile(pattern, re.DOTALL | re.IGNORECASE)
        tn.write(cmd + ENTER)
        (index, match, data) = tn.expect([p], timeout=10)
        work.writecmdlog(data)
        if index == -1:
            strw = recode('板卡进入CtcCli失败')
            print strw
            work.writerunlog(strw)
            return ERROR_RT

        time.sleep(2)

        cmd = '!@#'
        pattern = 'CTC_CLI\(ctc-sdk\)'
        p = re.compile(pattern, re.DOTALL | re.IGNORECASE)
        tn.write(cmd + ENTER)
        (index, match, data) = tn.expect([p], timeout=10)
        work.writecmdlog(data)
        if index == -1:
            strw = recode('板卡进入CtcCli失败')
            print strw
            work.writerunlog(strw)
            return ERROR_RT

        return SUCCESS_RT

    except KeyboardInterrupt:
        strw = recode('程序执行中断!')
        print strw
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序异常退出!%s,异常信息%s' % (f_name, err))
        print strw
        return ERROR_RT


##控制powercycle
#
#控制powercycle设备做上下电动作
def work_NPS(NPS_IP, NPS_PORT, NPS_WORK):
    """
    参数传递：        NPS_IP:              powercycle设备IP地址
          NPS_PORT:            所需要控制的端口
          NPS_WORK:            需要切换到的工作状态
    工作方式：       控制powercycle设备进行上下电动作
    返回参数：       返回执行的结果， SUCCESS_RT or ERROR_RT
    """
    try:
        #对NPS Port进行处理，以便能够适应多
        ports = NPS_PORT
        if type(ports) == str:
            if ports.find('-') != -1:
                a = ports.count('-')
                ports = ports.replace('-', ',', a)
        NPS_PORT = ports

        #连接到NPS
        strW = recode('准备开始连接到NPS')
        work.writerunlog(strW)
        rt = 0
        rt_times = 20
        while rt < rt_times:
            port = 23
            nps_child = telnetlib.Telnet(NPS_IP, port)
            time.sleep(10)
            nps_child.write('\r' + ENTER)
            (index, match, data) = nps_child.expect(['>'])
            if index == -1:
                nps_child.write('\r' + ENTER)
                time.sleep(0.5)
                (j, match, data) = nps_child.expect(['>'])
                if j == -1:
                    strW = recode('NPS设备连接失败，2分钟后将会重新开始连接。(Crtl+C中止程序)')
                    print strW
                    work.writerunlog(strW)
                    time.sleep(120)
                    nps_child.close()
                    nps_child = None
                    rt += 1
                    continue
            break

        time.sleep(5)
        #开始发送命令
        strW = recode('准备开始做上下电动作')
        work.writerunlog(strW)
        eee = '/%s %s\s*.+>' % (NPS_WORK, NPS_PORT)
        eee = re.compile(eee, re.DOTALL | re.IGNORECASE)
        ppp = [eee]
        cmd = '/%s %s' % (NPS_WORK, NPS_PORT)
        timeout = 20
        rt = command.CmdExpectNPS(nps_child, cmd, ppp, timeout)
        if rt == -1 or rt == ERROR_RT:
            strW = recode('控制NPS【%s】的端口[%s]到【%s】模式失败，请检查！将会重试一次' %
                          (NPS_IP, NPS_PORT, NPS_WORK))
            work.writerunlog(strW)
            timeout = 20
            rt = command.CmdExpectNPS(nps_child, cmd, ppp, timeout)
            if rt == -1 or rt == ERROR_RT:
                strW = recode('控制NPS【%s】的端口[%s]到【%s】模式失败，请检查！' %
                              (NPS_IP, NPS_PORT, NPS_WORK))
                work.writerunlog(strW)
                print strW
                return ERROR_RT

        time.sleep(5)
        exit_cmd = '/x'
        rtstr = 'Disconnected'
        rtstr = re.compile(rtstr, re.DOTALL | re.IGNORECASE)
        exits = [rtstr]
        rt = command.CmdExpectNPS(nps_child, exit_cmd, exits, timeout)
        if rt == -1 or rt == ERROR_RT:
            strW = recode('退出NPS失败，请检查！将会重试一次')
            work.writerunlog(strW)
            timeout = 20
            rt = command.CmdExpect(nps_child, exit_cmd, exits, timeout)
            if rt == -1 or rt == ERROR_RT:
                strW = recode('退出NPS失败，请检查！')
                work.writerunlog(strW)
                print strW
                nps_child.close()
                return SUCCESS_RT
        #关闭连接
        nps_child.close()
        return SUCCESS_RT
    except socket.error:
        strw = recode('连接到设备失败！')
        print strw
        work.writerunlog(strw)
        return ERROR_RT
    except EOFError:
        strw = recode('登陆设备失败，请确保网线连接正常，保持网络通畅！')
        print strw
        work.writerunlog(strw)
        return ERROR_RT
    except KeyboardInterrupt:
        strW = '程序执行到[connection.work_NPS]被手动终止'
        print recode(strW)
        return OTHER_ERROR
    except Exception, err:
        strW = '程序执行到[connection.work_NPS]异常退出!异常信息为%s' % err
        print recode(strW)
        return ERROR_RT


def LoginLinux(tn, times=5):
    '''login the linux kernel'''
    if times == 0:
        strw = recode('登陆linux失败')
        print strw
        work.writerunlog(strw)
        return ERROR_RT
    tn.write(ENTER)
    tn.expect(['login:'], timeout=5)

    tn.read_very_eager()
    tn.write('root' + ENTER)
    tn.expect([':'], timeout=5)
    tn.write('embed220' + ENTER)
    (index, match, data) = tn.expect(['#'], timeout=5)
    if index == -1:
        times = times - 1
        LoginLinux(tn, times)
    else:
        time.sleep(5)
        return SUCCESS_RT


def ListenAndGotoUboot():
    '''Detect the console info and login the Uboot shell'''
    import sys
    f_name = sys._getframe().f_code.co_name
    logpath = os.path.join(globalvar.LOG_DIR, '%s.log' % f_name)
    tn = globalvar.TN

    strw = recode('正在等待板卡进入Uboot...')
    print strw
    work.writerunlog(strw)
    while True:
        pattern = 'ctrl-p'
        p = re.compile(pattern, re.DOTALL | re.IGNORECASE)
        (index, match, data) = tn.expect([p], timeout=300)
        print data

        work.writecmdlog(data)
        work.writelogtofile(logpath, data)
        if index == -1:
            strw = recode('板卡进入PMON失败1')
            print strw
            work.writerunlog(strw)
            return ERROR_RT
        # TODO 检查 mtd1, 不是则 reboot
        if 'mtd1' in data.split('/dev/fs/')[-1]:
            tn.write(chr(16))
            tn.write(chr(16))
            time.sleep(1)
            tn.write('reboot' + ENTER)
        else:
            break

    if globalvar.BOARD_TYPE == 'YES':
        tn.write(chr(16))
        tn.write(chr(16))
        (index, match, data) = tn.expect(['PMON>'], timeout=20)
        work.writecmdlog(data)
        work.writelogtofile(logpath, data)
        if index == -1:
            strw = recode('板卡进入PMON失败2')
            print strw
            work.writerunlog(strw)
            return ERROR_RT

    strw = recode('板卡已经进入PMON')
    print strw
    work.writerunlog(strw)

    return SUCCESS_RT


def ListenAndGotoPowerInput():
    '''detect the power on please enter product series: prompt'''
    import sys
    f_name = sys._getframe().f_code.co_name
    logpath = os.path.join(globalvar.LOG_DIR, '%s.log' % f_name)
    tn = globalvar.TN

    strw = recode('正在等待板卡进入please enter product series:...')
    print strw
    work.writerunlog(strw)

    for i in range(200):
        tn.read_very_eager()
        tn.write('\002')
        pattern = 'product series:'
        (index, match, data) = tn.expect([pattern], timeout=0.5)
        if index != -1:
            return SUCCESS_RT

    strw = recode('进入please enter product series:失败')
    print strw
    work.writerunlog(strw)
    return ERROR_RT


def ListenAndGotoLinux():
    '''Detect the console info and login the kernel shell'''
    import sys
    tt = globalvar.tt
    f_name = sys._getframe().f_code.co_name
    logpath = os.path.join(globalvar.LOG_DIR, '%s.log' % f_name)
    tn = globalvar.TN
    tn.read_very_eager()

    strw = recode('正在等待板卡进入linux kernel...')
    print strw
    work.writerunlog(strw)

    # tn.write(ENTER)

    # pattern1 = 'The system is going down NOW!'
    pattern = 'Press RETURN to get started'
    # pattern = pattern1 + '.+' + pattern2 + '$'
    p = re.compile(pattern, re.DOTALL | re.IGNORECASE)
    (index, match, data) = tn.expect([p], timeout=300)
    print data
    work.writecmdlog(data)
    work.writelogtofile(logpath, data)
    if index == -1:
        strw = recode('板卡进入linux kernel失败')
        print strw
        work.writerunlog(strw)
        return ERROR_RT

    # if not globalvar.BOARD_TYPE == 'YES':
    #     if 'setting system clock' not in data:
    #         strw = recode('检查 RTC 失败')
    #         print strw
    #         work.writerunlog(strw)
    #         return ERROR_RT

    tn.write(ENTER)
    time.sleep(10)

    tn.write(ENTER)
    (index, match, data) = tn.expect(['Switch'], timeout=500)
    work.writecmdlog(data)
    work.writelogtofile(logpath, data)
    if index == -1:
        strw = recode('板卡登陆linux失败')
        print strw
        work.writerunlog(strw)
        return ERROR_RT

    pattern = 'Password'
    p = re.compile(re.escape(pattern), re.DOTALL | re.IGNORECASE)
    tn.write('enable' + ENTER)
    (index, match, data) = tn.expect([p], timeout=5)
    work.writecmdlog(data)
    work.writelogtofile(logpath, data)
    if index == -1:
        strw = recode('板卡登陆linux失败')
        print strw
        work.writerunlog(strw)
        return ERROR_RT

    pattern = 'Switch#'
    p = re.compile(re.escape(pattern), re.DOTALL | re.IGNORECASE)
    tn.write('admin' + ENTER)
    (index, match, data) = tn.expect([p], timeout=5)
    work.writecmdlog(data)
    work.writelogtofile(logpath, data)
    if index == -1:
        strw = recode('板卡登陆linux失败')
        print strw
        work.writerunlog(strw)
        return ERROR_RT

    if special.checkportmac() == ERROR_RT:
        return ERROR_RT


    strw = recode('板卡已经进入linux kernel')
    print strw
    work.writerunlog(strw)
    time.sleep(5)
    return SUCCESS_RT


def lowtemp_gotolinuxcheckport():
    '''Detect the console info and login the kernel shell'''
    try:
        import sys

        f_name = sys._getframe().f_code.co_name
        logpath = os.path.join(globalvar.LOG_DIR, '%s.log' % f_name)
        tn = globalvar.TN
        tn.read_very_eager()
        data_log = ''
        dirValue = globalvar.LOG_DIR
        logfile = os.path.join(dirValue, '%s.log') % f_name
        flag = 'PASS'

        strw = recode('正在等待板卡进入linux kernel...')
        print strw
        work.writerunlog(strw)

        # tn.write(ENTER)

        # pattern1 = 'The system is going down NOW!'
        pattern = 'Press RETURN to get started'
        # pattern = pattern1 + '.+' + pattern2 + '$'
        p = re.compile(pattern, re.DOTALL | re.IGNORECASE)
        (index, match, data) = tn.expect([p], timeout=300)
        print data
        work.writecmdlog(data)
        work.writelogtofile(logpath, data)
        if index == -1:
            strw = recode('板卡进入linux kernel失败')
            print strw
            work.writerunlog(strw)
            return ERROR_RT

        # if not globalvar.BOARD_TYPE == 'YES':
        #     if 'setting system clock' not in data:
        #         strw = recode('检查 RTC 失败')
        #         print strw
        #         work.writerunlog(strw)
        #         return ERROR_RT

        tn.write(ENTER)
        time.sleep(10)

        tn.write(ENTER)
        (index, match, data) = tn.expect(['Switch'], timeout=500)
        work.writecmdlog(data)
        work.writelogtofile(logpath, data)
        if index == -1:
            strw = recode('板卡登陆linux失败')
            print strw
            work.writerunlog(strw)
            return ERROR_RT

        pattern = 'Password'
        p = re.compile(re.escape(pattern), re.DOTALL | re.IGNORECASE)
        tn.write('enable' + ENTER)
        (index, match, data) = tn.expect([p], timeout=5)
        work.writecmdlog(data)
        work.writelogtofile(logpath, data)
        if index == -1:
            strw = recode('板卡登陆linux失败')
            print strw
            work.writerunlog(strw)
            return ERROR_RT

        pattern = 'Switch#'
        p = re.compile(re.escape(pattern), re.DOTALL | re.IGNORECASE)
        tn.write('admin' + ENTER)
        (index, match, data) = tn.expect([p], timeout=5)
        work.writecmdlog(data)
        work.writelogtofile(logpath, data)
        if index == -1:
            strw = recode('板卡登陆linux失败')
            print strw
            work.writerunlog(strw)
            return ERROR_RT

        cmd = 'ctc_shell'
        tn.write(cmd + ENTER)
        pattern = 'CTC_CLI\(ctc\-sdk\)#\s*'
        pattern = re.compile(pattern, re.IGNORECASE | re.DOTALL)
        (index, match, data) = tn.expect([pattern], timeout=10)
        data_log = data_log + data
        work.writecmdlog(data)
        work.writelogtofile(logfile, data)

        if index == -1:
            strw = recode('进入CTC_CLI失败')
            print strw
            work.writerunlog(strw)
            flag = 'FAIL'

        cmd = 'show port mac-link'
        for i in cmd:
            time.sleep(0.2)
            tn.write(i)
        tn.write(ENTER)
        pattern = 'CTC_CLI\(ctc\-sdk\)#'
        pattern = re.compile(pattern, re.IGNORECASE | re.DOTALL)
        (index, match, data) = tn.expect([pattern], timeout=10)
        data_log = data_log + data
        work.writecmdlog(data)
        work.writelogtofile(logfile, data)
        if index == -1:
            strw = recode('show port mac-link失败')
            print strw
            work.writerunlog(strw)
            flag = 'FAIL'

        pattern = 'down'
        p = re.compile(pattern, re.IGNORECASE | re.DOTALL)
        if p.search(data) != None:
            strw = recode('抓取到port有down状态...')
            print strw
            work.writerunlog(strw)
            flag = 'FAIL'

        if flag == "PASS":
            return SUCCESS_RT
        else:
            return ERROR_RT

    except KeyboardInterrupt:
        strw = recode('程序执行到[connection.%s]被手动终止'%f_name)
        print strw
        return OTHER_ERROR
    except Exception,err:
        strw = recode('程序执行到[connection.%s]异常退出!异常信息为%s'%(f_name,err))
        print strw
        return ERROR_RT

def ResetAndGotoLinux():

    '''reset and goto linux'''
    import sys
    f_name = sys._getframe().f_code.co_name
    logpath = os.path.join(globalvar.LOG_DIR, '%s.log' % f_name)
    tn = globalvar.TN

    tn.write('reset' + ENTER)

    return ListenAndGotoLinux()


def RebootAndGotoLinux():
    '''reset and goto linux'''
    import sys
    f_name = sys._getframe().f_code.co_name
    logpath = os.path.join(globalvar.LOG_DIR, '%s.log' % f_name)
    tn = globalvar.TN

    cmd = 'reboot'
    tn.write(cmd + ENTER)
    tn.expect(['\]'], timeout=5)
    tn.write('y' + ENTER)
    tn.write(ENTER)
    tn.expect(['waiting'],timeout=10)
    # tn.expect(['\]'], timeout=5)
    # tn.write('y' + ENTER)
    # tn.expect(['\]'], timeout=5)

    return ListenAndGotoLinux()


def BootAndGotoLinux():
    '''reset and goto linux'''
    import sys
    f_name = sys._getframe().f_code.co_name
    logpath = os.path.join(globalvar.LOG_DIR, '%s.log' % f_name)
    tn = globalvar.TN
    cfginfos = globalvar.CFG_INFOS
    gatewayip = cfginfos['IPINFO']['gateway_ip']
    tftp_dir = cfginfos['DL_FILE_VER']['tftp_dir']
    linux_file = cfginfos['DL_FILE_VER']['linux_file']
    networkip = cfginfos['IPINFO']['network_ip']
    print 'BootAndGotoLinux的BOARD_TYPE为 '+ globalvar.BOARD_TYPE
    if globalvar.BOARD_TYPE == 'YES':
        cmd0 = 'cpldwrite 0x1c 0x1'
        cmd1 = 'ifaddr eth0 %s:%s::%s' % (globalvar.IP, networkip, gatewayip)
        cmd2 = 'load %s%s' % (tftp_dir, linux_file)
        cmd_list = [cmd0, cmd1, cmd2]
        for cmd in cmd_list:
            print '运行命令：'+cmd
            p = cmd + '.+' + 'PMON'
            pattern = [re.compile(p, re.IGNORECASE | re.DOTALL)]
            tn.read_very_eager()
            time.sleep(0.5)
            for i in cmd:
                tn.write(i)
                time.sleep(0.1)
            tn.write(ENTER)
            (index, match, data) = tn.expect(pattern, timeout=400)
            #work.writecmdlog(data)
            work.writelogtofile(logpath, data)
            if index == -1:
                strw = recode('命令%s执行失败' % cmd)
                print strw
                work.writerunlog(strw)
                return ERROR_RT

        cmd3 = 'g rdinit=/sbin/init console=ttyS0,115200 bootimage=image bootpart=al0'

        tn.write(cmd3 + ENTER)
        # TODO 检查 clock
        p = cmd3 + '.+' + 'Waiting the system initialize'
        pattern = [re.compile(p, re.IGNORECASE | re.DOTALL)]
        tn.read_very_eager()
        time.sleep(0.5)
        (index, match, data) = tn.expect(pattern, timeout=400)
        work.writelogtofile(logpath, data)
        if index == -1:
            strw = recode('检查 RTC 失败1')
            print strw
            work.writerunlog(strw)
            return ERROR_RT
        elif 'setting system clock' not in data:
            strw = recode('检查 RTC 失败2')
            print strw
            work.writerunlog(strw)
            return ERROR_RT

    return SUCCESS_RT


def Gotoshell():
    tn = globalvar.TN
    dirValue = globalvar.LOG_DIR
    f_name = sys._getframe().f_code.co_name
    logfile = os.path.join(dirValue, '%s.log') % f_name
    pattern = 'Password'
    p = re.compile(re.escape(pattern), re.DOTALL | re.IGNORECASE)
    tn.write('start shell' + ENTER)
    time.sleep(1)
    (index, match, data) = tn.expect([p], timeout=30)
    #work.writecmdlog(data)
    work.writelogtofile(logfile, data)
    if index == -1:
        strw = recode('板卡登陆shell失败1')
        print strw
        work.writerunlog(strw)

    pattern = 'root'
    p = re.compile(re.escape(pattern), re.DOTALL | re.IGNORECASE)
    tn.write('!@#' + ENTER)
    (index, match, data) = tn.expect([p], timeout=30)
    #work.writecmdlog(data)
    work.writelogtofile(logfile, data)
    if index == -1:
        strw = recode('板卡登陆shell失败2')
        print strw
        work.writerunlog(strw)

    return SUCCESS_RT
