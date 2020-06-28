#!/usr/bin/env python
# This Python file uses the following encoding: utf-8

# @package autotest
# 功能：NewTAP生产测试应用模块，定义通用功能函数为主程序提供相关功能接口.
#
# 作者：hchen
#
# 日期：2014-03-12
#
# 文件：special.py

# import system modules
import os
import re
import time
import sys

# import our modules
import work                 # 写日志，以及上传到ftp的相关函数
import connection           # 登陆板卡的一些函数，以及在板卡上切换工作路径的函数
import app                  # 通用的功能函数，比如：写FRU，获取序列号等
import globalvar            # 一些全局变量
from work import recode     # 从work那边获取recode
import command
import tcplib
import appconfig
from datetime import datetime
import runconfig

# 获取相关的全局变量
#
# 将本地的全局变量都指向到globalvar中全局变量
ENCODE_TYPE = globalvar.ENCODE_TYPE     # 文件默认的系统编码
ERROR_RT = globalvar.ERROR_RT           # 错误返回值
SUCCESS_RT = globalvar.SUCCESS_RT       # 成功返回值
OTHER_ERROR = globalvar.OTHER_ERROR     # 其他错误返回值
DEBUGMODE = globalvar.DEBUGMODE         # debug模式开关
ENTER = globalvar.ENTER                 # 回车符重定义
file_name = os.path.basename(__file__)[:-3]

def Downloadpmon():
    try:
        loginfos = globalvar.loginfos
        tn = globalvar.TN
        f_name = sys._getframe().f_code.co_name
        dirValue = globalvar.LOG_DIR
        logfile = os.path.join(dirValue, '%s.log')%f_name
        cfginfos = globalvar.CFG_INFOS
        gatewayip = cfginfos['IPINFO']['gateway_ip']
        tftp_dir = cfginfos['DL_FILE_VER']['tftp_dir']
        pmon_file = cfginfos['DL_FILE_VER']['pmon_file']
        networkip = cfginfos['IPINFO']['network_ip']
        data_log = ''
        flag = 'PASS'

        # strw = '请插上网线并拔下管理网口对应的光模块'
        # rt = app.wait_op_input(strw)
        # if rt == ERROR_RT:
        #     return ERROR_RT
        if globalvar.BOARD_TYPE == 'YES':
            app.SetIP()
            cmd0 = 'cpldwrite 0x1c 0x1'
            cmd1 = 'ifaddr eth0 %s:%s::%s'%(globalvar.IP,networkip,gatewayip)
            cmd2 = 'load -f 0xbfc00000 -r %s%s'%(tftp_dir,pmon_file)
            cmd_list = [cmd0,cmd1,cmd2]
            for i in range(0,3,1):
                cmd = cmd_list[i]
                p = cmd+'.+'+'PMON>'
                pattern = [re.compile(p, re.IGNORECASE | re.DOTALL)]
                tn.read_very_eager()
                time.sleep(0.5)
                for i in cmd:
                    tn.write(i)
                    time.sleep(0.1)
                tn.write(ENTER)
                time.sleep(0.5)
                (index, match, data) = tn.expect(pattern, timeout=60)
                data_log = data_log + data
                # print data
                work.writecmdlog(data)
                work.writelogtofile(logfile, data)
                if index == -1:
                    strw = recode('命令%s执行失败'%cmd)
                    print strw
                    work.writerunlog(strw)
                    flag = 'FAIL'
                    return ERROR_RT

                if i == 2 :
                    strmatch = 'No Errors found'
                    p = re.compile(strmatch,re.IGNORECASE | re.DOTALL)
                    if p.search(data):
                        strw = recode('PMON升级成功')
                        print strw
                        work.writerunlog(strw)
                    else:
                        strw = recode('PMON升级失败')
                        print strw
                        work.writerunlog(strw)
                        flag = 'FAIL'
                        return ERROR_RT

                    strmatch = 'Can\'t assign requested address'
                    p = re.compile(strmatch,re.IGNORECASE | re.DOTALL)
                    if p.search(data):
                        strw = recode('TFTP不存在')
                        print strw
                        work.writerunlog(strw)
                        flag = 'FAIL'
                        return ERROR_RT

        # tn.write('reboot'+ENTER)

        loginfos[f_name] = data_log
        globalvar.loginfos = loginfos

        if flag == "PASS":
            return SUCCESS_RT
        else:
            return ERROR_RT
    except KeyboardInterrupt:
        strw = recode('程序执行到[%s.%s]被手动终止'%(file_name,f_name))
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[%s.%s]异常退出!异常信息为%s' % (file_name,f_name,err))
        print strw
        work.writerunlog(strw)
        return ERROR_RT


def ClearFlash():
    try:
        loginfos = globalvar.loginfos
        tn = globalvar.TN
        f_name = sys._getframe().f_code.co_name
        dirValue = globalvar.LOG_DIR
        logfile = os.path.join(dirValue, '%s.log')%f_name
        data_log = ''
        flag = 'PASS'

        print '是否擦除'+ globalvar.BOARD_TYPE

        if globalvar.BOARD_TYPE == 'YES':
            cmd0 = 'cpldwrite 0x1c 0x1'
            cmd1 = 'mtd_erase /dev/mtd0'
            cmd2 = 'mtd_erase /dev/mtd1'
            cmd3 = 'mtd_erase /dev/mtd2'
            cmd4 = 'mtd_erase /dev/mtd3'
            cmd_list = [cmd0,cmd1,cmd2,cmd3,cmd4]
            for cmd in cmd_list:
                p = cmd+'.+'+'PMON'
                pattern = [re.compile(p, re.IGNORECASE | re.DOTALL)]
                tn.read_very_eager()
                time.sleep(0.5)
                for i in cmd:
                    tn.write(i)
                    time.sleep(0.1)
                tn.write(ENTER)
                time.sleep(0.5)
                (index, match, data) = tn.expect(pattern, timeout=60)
                data_log = data_log + data
                work.writelogtofile(logfile, data)
                if index == -1:
                    strw = recode('命令%s执行失败'%cmd)
                    print strw
                    work.writerunlog(strw)

        loginfos[f_name] = data_log
        globalvar.loginfos = loginfos

        if flag == "PASS":
            return SUCCESS_RT
        else:
            return ERROR_RT
    except KeyboardInterrupt:
        strw = recode('程序执行到[%s.%s]被手动终止'%(file_name,f_name))
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[%s.%s]异常退出!异常信息为%s' % (file_name,f_name,err))
        print strw
        work.writerunlog(strw)
        return ERROR_RT

def DownloadLinuxFile():
    try:
        loginfos = globalvar.loginfos
        tn = globalvar.TN
        f_name = sys._getframe().f_code.co_name
        dirValue = globalvar.LOG_DIR
        logfile = os.path.join(dirValue, '%s.log')%f_name
        cfginfos = globalvar.CFG_INFOS
        gatewayip = cfginfos['IPINFO']['gateway_ip']
        tftp_dir = cfginfos['DL_FILE_VER']['tftp_dir']
        linux_file = cfginfos['DL_FILE_VER']['linux_file']
        data_log = ''
        flag = 'PASS'

        
        if globalvar.BOARD_TYPE == 'YES':
            for i in range(1,1000,1):
                cmd = 'delete boot/*'
                pattern = 'no'
                pattern = re.compile(pattern, re.DOTALL | re.IGNORECASE)
                tn.write(cmd + ENTER)
                (index, match, data) = tn.expect([pattern], timeout=60)
                data_log = data_log + data
                work.writecmdlog(data)
                work.writelogtofile(logfile,data)
                if index == -1:
                    flag = 'FAIL'

                cmd = 'yes'
                pattern = '#'
                pattern = re.compile(pattern, re.DOTALL | re.IGNORECASE)
                tn.write(cmd + ENTER)
                (index, match, data) = tn.expect([pattern], timeout=60)
                data_log = data_log + data
                work.writecmdlog(data)
                work.writelogtofile(logfile,data)
                if index == -1:
                    flag = 'FAIL'

                cmd = 'copy mgmt-if %s%s   flash:/boot/%s'%(tftp_dir,linux_file,linux_file)
                pattern = 'md5 \w+ ok'
                pattern = re.compile(pattern, re.DOTALL | re.IGNORECASE)
                for i in cmd:
                    tn.write(i)
                    time.sleep(0.05)
                tn.write(ENTER)
                (index, match, data) = tn.expect([pattern], timeout=1500)
                data_log = data_log + data
                print data
                work.writecmdlog(data)
                work.writelogtofile(logfile,data)   
                if index == -1:
                    strw = recode('下载版本文件失败')
                    print strw
                    work.writerunlog(strw)
                    flag = 'FAIL'
                else:
                    break

        cmd = ' boot system flash:/boot/%s'%linux_file
        pattern = 'confirm'
        pattern = re.compile(pattern, re.DOTALL | re.IGNORECASE)
        tn.write(cmd + ENTER)
        (index, match, data) = tn.expect([pattern], timeout=60)
        data_log = data_log + data
        work.writecmdlog(data)
        work.writelogtofile(logfile,data)
        if index == -1:
            flag = 'FAIL'

        cmd = 'y'
        pattern = 'success'
        pattern = re.compile(pattern, re.DOTALL | re.IGNORECASE)
        tn.write(cmd + ENTER)
        (index, match, data) = tn.expect([pattern], timeout=60)
        data_log = data_log + data
        work.writecmdlog(data)
        work.writelogtofile(logfile,data)
        if index == -1:
            strw = recode('设置启动文件失败')
            print strw
            work.writerunlog(strw)
            flag = 'FAIL'
    
        loginfos[f_name] = data_log
        globalvar.loginfos = loginfos

        strw = recode('%s ...... %s'%(f_name, flag))
        print strw 
        work.writerunlog(strw)

        if flag == "PASS":
            return SUCCESS_RT
        else:
            return ERROR_RT
    except KeyboardInterrupt:
        strw = recode('程序执行到[%s.%s]被手动终止'%(file_name,f_name))
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[%s.%s]异常退出!异常信息为%s' % (file_name,f_name,err))
        print strw
        work.writerunlog(strw)
        return ERROR_RT   


def CopylinuxFile():
    try:
        loginfos = globalvar.loginfos
        tn = globalvar.TN
        f_name = sys._getframe().f_code.co_name
        dirValue = globalvar.LOG_DIR
        logfile = os.path.join(dirValue, '%s.log')%f_name
        cfginfos = globalvar.CFG_INFOS
        gatewayip = cfginfos['IPINFO']['gateway_ip']
        tftp_dir = cfginfos['DL_FILE_VER']['tftp_dir']
        linux_file = cfginfos['DL_FILE_VER']['linux_file']
        data_log = ''
        flag = 'PASS'

        connection.Gotoshell()
        cmd0 = 'mount'
        cmd1 = 'umount /dev/mtdblock0'
        cmd2 = 'mount -t yaffs2 /dev/mtdblock1 /mnt/flash/boot'
        cmd_list = [cmd0,cmd1,cmd2]
        for cmd in cmd_list:
            pattern, timeout = '$', 10
            data = command.CmdGet(tn, cmd, [pattern], timeout)
            data_log = data_log + data
            work.writelogtofile(logfile, data)
            if data == ERROR_RT: 
                flag = 'FAIL'

        tn.write('exit'+ENTER)

        
        if globalvar.BOARD_TYPE == 'YES':
            for i in range(1,1000,1):
                cmd = 'delete boot/*'
                pattern = 'no'
                pattern = re.compile(pattern, re.DOTALL | re.IGNORECASE)
                tn.write(cmd + ENTER)
                (index, match, data) = tn.expect([pattern], timeout=60)
                data_log = data_log + data
                work.writecmdlog(data)
                work.writelogtofile(logfile,data)
                if index == -1:
                    flag = 'FAIL'

                cmd = 'yes'
                pattern = '#'
                pattern = re.compile(pattern, re.DOTALL | re.IGNORECASE)
                tn.write(cmd + ENTER)
                (index, match, data) = tn.expect([pattern], timeout=60)
                data_log = data_log + data
                work.writecmdlog(data)
                work.writelogtofile(logfile,data)
                if index == -1:
                    flag = 'FAIL'

                cmd = 'copy mgmt-if %s%s   flash:/boot/%s'%(tftp_dir,linux_file,linux_file)
                pattern = 'md5 \w+ ok '
                pattern = re.compile(pattern, re.DOTALL | re.IGNORECASE)
                for i in cmd:
                    tn.write(i)
                    time.sleep(0.05)
                tn.write(ENTER)
                (index, match, data) = tn.expect([pattern], timeout=600)
                data_log = data_log + data
                work.writecmdlog(data)
                work.writelogtofile(logfile,data)
                if index == -1:
                    strw = recode('下载版本文件失败')
                    print strw
                    work.writerunlog(strw)
                    flag = 'FAIL'
                else:
                    break

        cmd = ' boot system flash:/boot/%s'%linux_file
        for i in cmd:
            tn.write(i)
            time.sleep(0.1)
        pattern = 'confirm'
        pattern = re.compile(pattern, re.DOTALL | re.IGNORECASE)
        tn.write(ENTER)
        (index, match, data) = tn.expect([pattern], timeout=60)
        data_log = data_log + data
        work.writecmdlog(data)
        work.writelogtofile(logfile,data)
        if index == -1:
            flag = 'FAIL'

        cmd = 'y'
        pattern = 'success'
        pattern = re.compile(pattern, re.DOTALL | re.IGNORECASE)
        tn.write(cmd + ENTER)
        (index, match, data) = tn.expect([pattern], timeout=60)
        data_log = data_log + data
        work.writecmdlog(data)
        work.writelogtofile(logfile,data)
        if index == -1:
            strw = recode('设置启动文件失败')
            print strw
            work.writerunlog(strw)
            flag = 'FAIL'

        connection.Gotoshell()
        tn.write('umount /dev/mtdblock1'+ENTER)
        cmd = 'reboot'
        #pattern = 'yes/no'
        #pattern = re.compile(pattern, re.DOTALL | re.IGNORECASE)
        #tn.write(cmd + ENTER)
        #(index, match, data) = tn.expect([pattern], timeout=60)
        #work.writecmdlog(data)
        #work.writelogtofile(logfile,data)
        #if index == -1:
        #    flag = 'FAIL'
#
        #cmd = 'no'
        #pattern = 'confirm'
        #pattern = re.compile(pattern, re.DOTALL | re.IGNORECASE)
        #tn.write(cmd + ENTER)
        #(index, match, data) = tn.expect([pattern], timeout=6000)
        #work.writecmdlog(data)
        #work.writelogtofile(logfile,data)
        #if index == -1:
        #    flag = 'FAIL'
#
        #cmd = 'y'
        for i in range(1,1000,1):
            pattern = 'ctrl-p'
            pattern = re.compile(pattern, re.DOTALL | re.IGNORECASE)
            tn.write(cmd + ENTER)
            (index, match, data) = tn.expect([pattern], timeout=6000)
            work.writecmdlog(data)
            work.writelogtofile(logfile,data)
            if index == -1:
                flag = 'FAIL'
    
            pattern = 'yaffs2@mtd0'
            pattern = re.compile(pattern, re.DOTALL | re.IGNORECASE)
            p = re.search(pattern, data)
            #print data
            if p :
                tn.write(chr(16))
                cmd = 'reboot'
                strw = recode('启动分区为mtd0')
                print strw 
                work.writerunlog(strw)
                
            else:
                strw = recode('启动分区为mtd1')
                print strw 
                work.writerunlog(strw)
                break
    
        loginfos[f_name] = data_log
        globalvar.loginfos = loginfos

        strw = recode('%s ...... %s'%(f_name, flag))
        print strw 
        work.writerunlog(strw)

        if flag == "PASS":
            return SUCCESS_RT
        else:
            return ERROR_RT
    except KeyboardInterrupt:
        strw = recode('程序执行到[%s.%s]被手动终止'%(file_name,f_name))
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[%s.%s]异常退出!异常信息为%s' % (file_name,f_name,err))
        print strw
        work.writerunlog(strw)
        return ERROR_RT 

def RestorePartition():
    try:
        loginfos = globalvar.loginfos
        tn = globalvar.TN
        f_name = sys._getframe().f_code.co_name
        dirValue = globalvar.LOG_DIR
        logfile = os.path.join(dirValue, '%s.log')%f_name
        cfginfos = globalvar.CFG_INFOS
        gatewayip = cfginfos['IPINFO']['gateway_ip']
        tftp_dir = cfginfos['DL_FILE_VER']['tftp_dir']
        linux_file = cfginfos['DL_FILE_VER']['linux_file']
        data_log = ''
        flag = 'PASS'

        connection.Gotoshell()
        pattern = 'mount'+'.+'+'root@Switch'
        pattern = re.compile(pattern, re.DOTALL | re.IGNORECASE)
        tn.write('mount'+ENTER)
        (index, match, data) = tn.expect([pattern], timeout=60)
        print data
        work.writecmdlog(data)
        work.writelogtofile(logfile,data)
        if (index == -1) or ('/dev/mtdblock1' not in data):
            flag = 'FAIL'
        cmd = 'reboot'
        for i in range(1,1000,1):
            pattern = 'ctrl-p'
            pattern = re.compile(pattern, re.DOTALL | re.IGNORECASE)
            tn.write(cmd + ENTER)
            (index, match, data) = tn.expect([pattern], timeout=300)
            #work.writecmdlog(data)
            work.writelogtofile(logfile,data)
            if index == -1:
                flag = 'FAIL'
    
            pattern = 'yaffs2@mtd1'
            pattern = re.compile(pattern, re.DOTALL | re.IGNORECASE)
            p = re.search(pattern, data)
            if p :
                tn.write(chr(16))
                cmd = 'reboot'
                strw = recode('启动分区为mtd1')
                print strw 
                work.writerunlog(strw)                
            else:
                strw = recode('启动分区为mtd0')
                print strw 
                work.writerunlog(strw)
                break
        # 检查 mtd0
        connection.ListenAndGotoLinux()
        connection.Gotoshell()
        pattern = 'mount'+'.+'+'root@Switch'
        pattern = re.compile(pattern, re.DOTALL | re.IGNORECASE)
        tn.write('mount'+ENTER)
        (index, match, data) = tn.expect([pattern], timeout=60)
        print data
        work.writecmdlog(data)
        work.writelogtofile(logfile,data)
        if index == -1 or '/dev/mtdblock0' not in data:
            flag = 'FAIL'

        strw = recode('%s ...... %s'%(f_name, flag))
        print strw 
        work.writerunlog(strw)

        pattern = 'Switch#'
        pattern = re.compile(pattern, re.DOTALL | re.IGNORECASE)
        tn.write('exit'+ENTER)
        (index, match, data) = tn.expect([pattern], timeout=60)
        work.writelogtofile(logfile,data)
        if index == -1:
            flag = 'FAIL'

        if flag == "PASS":
            return SUCCESS_RT
        else:
            return ERROR_RT
    except KeyboardInterrupt:
        strw = recode('程序执行到[%s.%s]被手动终止'%(file_name,f_name))
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[%s.%s]异常退出!异常信息为%s' % (file_name,f_name,err))
        print strw
        work.writerunlog(strw)
        return ERROR_RT 

def ConfigRtc():
    try:
        loginfos = globalvar.loginfos
        tn = globalvar.TN
        f_name = sys._getframe().f_code.co_name
        dirValue = globalvar.LOG_DIR
        logfile = os.path.join(dirValue, '%s.log')%f_name
        data_log = ''
        flag = 'PASS'

        connection.ListenAndGotoLinux()
        connection.Gotoshell()
        #100209062018
        time_now = time_now = time.strftime('%H%M%m%d%Y')
        dayOfWeek = datetime.now().weekday() + 1
        hour = time_now[0:2]
        minute = time_now[2:4]
        month = time_now[4:6]
        day = time_now[6:8]
        year = time_now[10:12]
        cmd0 = 'i2cset -y 0 0x32 0xf0 0x30'
        cmd1 = 'i2cset -y 0 0x32 0x60 0x%s'%year
        cmd2 = 'i2cset -y 0 0x32 0x50 0x%s'%month
        cmd3 = 'i2cset -y 0 0x32 0x40 0x%s'%day
        cmd4 = 'i2cset -y 0 0x32 0x30 0x0%s'%dayOfWeek
        cmd5 = 'i2cset -y 0 0x32 0x20 0x%s'%hour
        cmd6 = 'i2cset -y 0 0x32 0x10 0x%s'%minute
        cmd_list = [cmd0,cmd1,cmd2,cmd3,cmd4,cmd5,cmd6]
        for cmd in cmd_list:
            for i in cmd:
                tn.write(i)
                time.sleep(0.1)
            p = '$'
            pattern = [re.compile(p, re.IGNORECASE | re.DOTALL)]
            tn.read_very_eager()
            time.sleep(0.5)
            tn.write(ENTER)
            time.sleep(0.5)
            (index, match, data) = tn.expect(pattern, timeout=60)
            data_log = data_log + data
            work.writecmdlog(data)
            work.writelogtofile(logfile, data)
            if index == -1:
                strw = recode('命令%s执行失败'%cmd)
                print strw
                work.writerunlog(strw)

        tn.write('exit'+ENTER)
        
        loginfos[f_name] = data_log
        globalvar.loginfos = loginfos

        strw = recode('%s ...... %s'%(f_name, flag))
        print strw 
        work.writerunlog(strw)

        if flag == "PASS":
            return SUCCESS_RT
        else:
            return ERROR_RT
    except KeyboardInterrupt:
        strw = recode('程序执行到[%s.%s]被手动终止'%(file_name,f_name))
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[%s.%s]异常退出!异常信息为%s' % (file_name,f_name,err))
        print strw
        work.writerunlog(strw)
        return ERROR_RT

def CheckFan():
    try:
        loginfos = globalvar.loginfos
        tn = globalvar.TN
        f_name = sys._getframe().f_code.co_name
        dirValue = globalvar.LOG_DIR
        logfile = os.path.join(dirValue, '%s.log')%f_name
        data_log = ''
        flag = 'PASS'

        connection.Gotoshell()

        strw = '请注意观察风扇'
        rt = app.wait_op_input(strw)
        if rt == ERROR_RT:
            strw = recode('风扇测试失败')
            print strw
            work.writerunlog(strw)
            flag = 'FAIL'

        cmd = 'i2cset -y 0 0x4 0xe 0xf w'
        tn.write(cmd+ENTER)

        strw = '风扇是否全速转动一会儿'
        rt = app.wait_op_input(strw)
        if rt == ERROR_RT:
            strw = recode('风扇测试失败')
            print strw
            work.writerunlog(strw)
            flag = 'FAIL'

        tn.write('exit'+ENTER)
        
        loginfos[f_name] = data_log
        globalvar.loginfos = loginfos

        strw = recode('%s ...... %s'%(f_name, flag))
        print strw 
        work.writerunlog(strw)

        if flag == "PASS":
            return SUCCESS_RT
        else:
            return ERROR_RT
    except KeyboardInterrupt:
        strw = recode('程序执行到[%s.%s]被手动终止'%(file_name,f_name))
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[%s.%s]异常退出!异常信息为%s' % (file_name,f_name,err))
        print strw
        work.writerunlog(strw)
        return ERROR_RT

def DiagUSB():
    try:
        loginfos = globalvar.loginfos
        tn = globalvar.TN
        f_name = sys._getframe().f_code.co_name
        dirValue = globalvar.LOG_DIR
        logfile = os.path.join(dirValue, '%s.log')%f_name
        data_log = ''
        flag = 'PASS'

        connection.Gotoshell()

        cmd = 'mount /dev/sda1 /mnt'
        pattern = '$'
        tn.read_very_eager()
        time.sleep(0.5)
        tn.write(cmd + ENTER)
        time.sleep(0.5)
        (index, match, data) = tn.expect([pattern], timeout=60)
        data_log = data_log + data
        work.writecmdlog(data)
        work.writelogtofile(logfile, data)
        if index == -1:
            strw = recode('命令%s执行失败'%cmd)
            print strw
            work.writerunlog(strw)  
            flag = 'FAIL'  
        
        cmd = 'sh /mnt/diag_sdx.sh /dev/sda1'
        pattern = '$'
        pattern = re.compile(pattern, re.DOTALL | re.IGNORECASE)
        tn.read_very_eager()
        time.sleep(0.5)
        tn.write(cmd + ENTER)
        time.sleep(0.5)
        (index, match, data) = tn.expect([pattern], timeout=60)
        data_log = data_log + data
        work.writecmdlog(data)
        work.writelogtofile(logfile, data)
        if index == -1:
            strw = recode('命令%s执行失败'%cmd)
            print strw
            work.writerunlog(strw)  
            flag = 'FAIL'  

        pattern = 'ok'  
        pattern = re.compile(pattern, re.DOTALL | re.IGNORECASE)
        p = re.search(pattern,data)
        if p==ERROR_RT:
            strw = recode('USB测试失败')
            print strw
            work.writerunlog(strw)
            flag = 'FAIL'

        tn.write('exit'+ENTER)
        
        loginfos[f_name] = data_log
        globalvar.loginfos = loginfos

        strw = recode('%s ...... %s'%(f_name, flag))
        print strw 
        work.writerunlog(strw)

        if flag == "PASS":
            return SUCCESS_RT
        else:
            return ERROR_RT
    except KeyboardInterrupt:
        strw = recode('程序执行到[%s.%s]被手动终止'%(file_name,f_name))
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[%s.%s]异常退出!异常信息为%s' % (file_name,f_name,err))
        print strw
        work.writerunlog(strw)
        return ERROR_RT

def diag_sfp():
    try:
        loginfos = globalvar.loginfos
        tn = globalvar.TN
        f_name = sys._getframe().f_code.co_name
        dirValue = globalvar.LOG_DIR
        logfile = os.path.join(dirValue, '%s.log')%f_name
        data_log = ''
        flag = 'PASS'

        tn.write(ENTER)
        time.sleep(3)
        tn.write(ENTER)
        cmd = 'enable'
        for i in cmd:
            tn.write(i)
            time.sleep(0.05)
        tn.write(ENTER)
        cmd = 'admin'
        for i in cmd:
            tn.write(i)
            time.sleep(0.05)
        tn.write(ENTER)

        connection.Gotoshell()

        cmd = 'top'
        p = cmd+'.+'+'Switch'
        pattern = [re.compile(p, re.IGNORECASE | re.DOTALL)]
        tn.read_very_eager()
        time.sleep(0.5)
        tn.write(cmd + ENTER)
        time.sleep(3)
        tn.write('\003')
        (index, match, data) = tn.expect(pattern, timeout=60)
        data_log = data_log + data
        work.writecmdlog(data)
        work.writelogtofile(logfile, data)
        if index == -1:
            strw = recode('命令%s执行失败'%cmd)
            print strw
            work.writerunlog(strw)
            flag = 'FAIL'

        pattern = '1\d\d\d\s+\d\s.+fea'
        pattern = re.compile(pattern, re.IGNORECASE | re.DOTALL)
        p = re.search(pattern, data)
        if p:
            PID = p.group()[0:4]
            print p.group()
        else:
            strw = recode('PID号抓取失败')
            print strw
            work.writerunlog(strw)
            flag = 'FAIL'

        cmd = 'kill %s'%PID
        p = cmd+'.+'+'$'
        pattern = [re.compile(p, re.IGNORECASE | re.DOTALL)]
        tn.read_very_eager()
        time.sleep(0.5)
        tn.write(cmd + ENTER)
        time.sleep(0.5)
        (index, match, data) = tn.expect(pattern, timeout=60)
        data_log = data_log + data
        work.writecmdlog(data)
        work.writelogtofile(logfile, data)
        if index == -1:
            strw = recode('命令%s执行失败'%cmd)
            print strw
            work.writerunlog(strw)
            flag = 'FAIL'

        cmd_list = [
            'i2cset -y 0 0x4 0x15 0x1 w',
            'i2cset -y 0 0x4 0x15 0x2 w',
            'i2cset -y 0 0x4 0x15 0x3 w',
            'i2cset -y 0 0x4 0x15 0x4 w',
        ]
        for cmd in cmd_list:
            p = cmd+'.+'+'$'
            pattern = [re.compile(p, re.IGNORECASE | re.DOTALL)]
            tn.read_very_eager()
            time.sleep(0.5)
            tn.write(cmd + ENTER)
            time.sleep(0.5)
            (index, match, data) = tn.expect(pattern, timeout=60)
            data_log = data_log + data
            work.writecmdlog(data)
            work.writelogtofile(logfile, data)
            if index == -1:
                strw = recode('命令%s执行失败'%cmd)
                print strw
                work.writerunlog(strw)
                flag = 'FAIL'

            cmd_list = [
                'i2cget -y 0 0x51 0x60',
                'i2cget -y 0 0x51 0x61',
            ]
            for cmd in cmd_list:
                p = cmd+'.+'+'$'
                pattern = [re.compile(p, re.IGNORECASE | re.DOTALL)]
                tn.read_very_eager()
                time.sleep(0.5)
                tn.write(cmd + ENTER)
                time.sleep(0.5)
                (index, match, data) = tn.expect(pattern, timeout=60)
                data_log = data_log + data
                work.writecmdlog(data)
                work.writelogtofile(logfile, data)
                if index == -1:
                    strw = recode('命令%s执行失败'%cmd)
                    print strw
                    work.writerunlog(strw)
                    flag = 'FAIL'

                pattern = '0x\S\S'
                pattern = re.compile(p, re.IGNORECASE | re.DOTALL)
                p = re.search(pattern,data)
                if p:
                    strw = recode('光模块信息读取正常')
                    print strw
                    work.writerunlog(strw)
                else:
                    strw = recode('光模块信息读取异常')
                    print strw
                    work.writerunlog(strw)
                    flag = 'FAIL'
                    
        if globalvar.port_number == '56' or globalvar.port_number == '32':
            cmd_list = [
                'i2cset -y 0 0x71 0x01',
                'i2cset -y 0 0x71 0x02',
                'i2cset -y 0 0x71 0x04',
                'i2cset -y 0 0x71 0x08',
            ]
            for cmd in cmd_list:
                tn.write('i2cset -y 0 0x4 0x15 0x5 w'+ENTER)
                p = cmd+'.+'+'$'
                pattern = [re.compile(p, re.IGNORECASE | re.DOTALL)]
                tn.read_very_eager()
                time.sleep(0.5)
                tn.write(cmd + ENTER)
                time.sleep(0.5)
                (index, match, data) = tn.expect(pattern, timeout=60)
                data_log = data_log + data
                work.writecmdlog(data)
                work.writelogtofile(logfile, data)
                if index == -1:
                    strw = recode('命令%s执行失败'%cmd)
                    print strw
                    work.writerunlog(strw)
                    flag = 'FAIL'
            
                cmd_list = [
                    'i2cget -y 0 0x51 0x60',
                    'i2cget -y 0 0x51 0x61',
                ]
                for cmd in cmd_list:
                    p = cmd+'.+'+'$'
                    pattern = [re.compile(p, re.IGNORECASE | re.DOTALL)]
                    tn.read_very_eager()
                    time.sleep(0.5)
                    tn.write(cmd + ENTER)
                    time.sleep(0.5)
                    (index, match, data) = tn.expect(pattern, timeout=60)
                    data_log = data_log + data
                    work.writecmdlog(data)
                    work.writelogtofile(logfile, data)
                    if index == -1:
                        strw = recode('命令%s执行失败'%cmd)
                        print strw
                        work.writerunlog(strw)
                        flag = 'FAIL'
            
                    pattern = '0x\S\S'
                    pattern = re.compile(p, re.IGNORECASE | re.DOTALL)
                    p = re.search(pattern,data)
                    if p:
                        strw = recode('光模块信息读取正常')
                        print strw
                        work.writerunlog(strw)
                    else:
                        strw = recode('光模块信息读取异常')
                        print strw
                        work.writerunlog(strw)
                        flag = 'FAIL'

        tn.write('exit'+ENTER)

        loginfos[f_name] = data_log
        globalvar.loginfos = loginfos

        strw = recode('%s ...... %s'%(f_name, flag))
        print strw 
        work.writerunlog(strw)

        if flag == "PASS":
            return SUCCESS_RT
        else:
            return ERROR_RT
    except KeyboardInterrupt:
        strw = recode('程序执行到[%s.%s]被手动终止'%(file_name,f_name))
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[%s.%s]异常退出!异常信息为%s' % (file_name,f_name,err))
        print strw
        work.writerunlog(strw)
        return ERROR_RT

def StartPacketTestBurnIn():
    try:
        loginfos = globalvar.loginfos
        tn = globalvar.TN       
        f_name = sys._getframe().f_code.co_name
        dirValue = globalvar.LOG_DIR
        logfile = os.path.join(dirValue, '%s.log')%f_name
        cfginfos = globalvar.CFG_INFOS    # 从globalvar中获得CFG_INFOS
        test_time = cfginfos['BURNINTIME']['data_time']
        data_log = ''
        flag = 'PASS'

        cmd_list = [
        'cd flash/test/',
        'source env.sh',
        'sh load_all.sh',
        'cd test'
        ]
        for cmd in cmd_list:
            tn.write(cmd+ENTER)
            tn.expect(['root'],20)

        # CheckPacketTest()
        # CheckNetPortTest()

        # if globalvar.flag1 == 'PASS' and globalvar.flag2 == 'PASS':
        #     flag = 'PASS'
        #     print flag
        # else:
        #     flag = 'FAIL'
        #     print flag

        # if flag == 'PASS':
            # cmd = 'rm memtester.log'
            # tn.write(cmd+ENTER)
            # tn.expect(['root'],10)
        if globalvar.boardtype == "E580-VX6300":
            strw = recode('48口类型板卡发包')
            work.writerunlog(strw)

            cmd = 'sh start_packet_test_48.sh'
            tn.write(cmd+ENTER)
            tn.expect(['root'],300)
        elif globalvar.boardtype == "E580-VX6300A2":
            strw = recode('36口类型板卡发包')
            work.writerunlog(strw)

            cmd = 'sh start_packet_test.sh'
            tn.write(cmd + ENTER)
            tn.expect(['root'],300)
        else:
            strw = recode('板卡获取失败')
            print strw
            work.writerunlog(strw)
            flag = 'FAIL'


            # cmd = 'sh check_memtester.sh 400 %s > memtest.log &'%(int(float(test_time)*3000))
            # tn.write(cmd+ENTER)
            # tn.expect(['root'],10)
            # cmd = 'ip netns exec mgmt /bin/sh'
            # tn.write(cmd+ENTER)
            # tn.expect(['#'],10)
            # cmd = 't=%s'% (int(float(test_time)*30))
            # tn.write(cmd+ENTER)
            # tn.expect(['#'],10)
            # cmd = 'p_num=$((6100000*$t))'
            # tn.write(cmd+ENTER)
            # tn.expect(['#'],10)
            # cmd = 'sh tx_port_packet.sh 0 $p_num'
            # tn.write(cmd+ENTER)

        loginfos[f_name] = data_log
        globalvar.loginfos = loginfos

        strw = recode('%s ...... %s'%(f_name, flag))
        print strw 
        work.writerunlog(strw)

        if flag == "PASS":
            return SUCCESS_RT
        else:
            return ERROR_RT
    except KeyboardInterrupt:
        strw = recode('程序执行到[%s.%s]被手动终止'%(file_name,f_name))
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[%s.%s]异常退出!异常信息为%s' % (file_name,f_name,err))
        print strw
        work.writerunlog(strw)
        return ERROR_RT

def BurninWait():
    try:
        loginfos = globalvar.loginfos
        tn = globalvar.TN
        f_name = sys._getframe().f_code.co_name
        dirValue = globalvar.LOG_DIR
        logfile = os.path.join(dirValue, '%s.log')%f_name
        cfginfos = globalvar.CFG_INFOS    # 从globalvar中获得CFG_INFOS
        test_time = cfginfos['BURNINTIME']['data_time']
        flag = 'PASS'

        strw = recode('拷机开始，拷机时长为%s小时')%test_time
        print strw
        work.writerunlog(strw)

        num = int(float(test_time)*3600)
        time.sleep(num)

        if flag == "PASS":
            return SUCCESS_RT
        else:
            return ERROR_RT
    except KeyboardInterrupt:
        strw = recode('程序执行到[%s.%s]被手动终止'%(file_name,f_name))
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[%s.%s]异常退出!异常信息为%s' % (file_name,f_name,err))
        print strw
        work.writerunlog(strw)
        return ERROR_RT


def CheckPacketTest():
    try:
        loginfos = globalvar.loginfos
        tn = globalvar.TN
        f_name = sys._getframe().f_code.co_name
        dirValue = globalvar.LOG_DIR
        logfile = os.path.join(dirValue, '%s.log')%f_name
        cfginfos = globalvar.CFG_INFOS    # 从globalvar中获得CFG_INFOS
        data_log = ''
        flag = 'PASS'

        cmd = 'sh start_packet_test.sh'
        tn.write(cmd+ENTER)
        tn.expect(['root'],300)

        cmd = 'sh check_packet_test.sh'
        pattern = 'root'
        pattern = re.compile(pattern, re.IGNORECASE | re.DOTALL)
        tn.write(cmd + ENTER)
        (index, match, data) = tn.expect([pattern], timeout=60)
        print data
        data_log = data_log + data
        work.writecmdlog(data)
        work.writelogtofile(logfile, data)
        if index == -1:
            strw = recode('读取发包数量失败')
            print strw
            work.writerunlog(strw)
            flag = 'FAIL'

        pattern = 'FAIL'
        pattern = re.compile(pattern, re.IGNORECASE | re.DOTALL)
        p = re.search(pattern,data)
        if p :
            flag = 'FAIL'

        globalvar.flag1 = flag

        loginfos[f_name] = data_log
        globalvar.loginfos = loginfos

        strw = recode('%s ...... %s'%(f_name, flag))
        print strw 
        work.writerunlog(strw)

        if flag == "PASS":
            return SUCCESS_RT
        else:
            return ERROR_RT
    except KeyboardInterrupt:
        strw = recode('程序执行到[%s.%s]被手动终止'%(file_name,f_name))
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[%s.%s]异常退出!异常信息为%s' % (file_name,f_name,err))
        print strw
        work.writerunlog(strw)
        return ERROR_RT

def CheckPacketTestBurnIn():
    try:
        loginfos = globalvar.loginfos
        tn = globalvar.TN
        f_name = sys._getframe().f_code.co_name
        dirValue = globalvar.LOG_DIR
        logfile = os.path.join(dirValue, '%s.log')%f_name
        cfginfos = globalvar.CFG_INFOS    # 从globalvar中获得CFG_INFOS
        data_log = ''
        flag = 'PASS'

        # cmd = 'sh show_netport_counter.sh '
        # pattern = 'eth0.+?\w\w\w\w'
        # pattern = re.compile(pattern, re.IGNORECASE | re.DOTALL)
        # tn.write(cmd + ENTER)
        # (index, match, data) = tn.expect([pattern], timeout=6000)
        # print data
        # data_log = data_log + data
        # work.writecmdlog(data)
        # work.writelogtofile(logfile, data)
        # if index == -1:
        #     strw = recode('读取发包数量失败')
        #     print strw
        #     work.writerunlog(strw)
        #     flag = 'FAIL'
        #
        # pattern = 'FAIL'
        # pattern = re.compile(pattern, re.IGNORECASE | re.DOTALL)
        # p = re.search(pattern,data)
        # if p :
        #     flag = 'FAIL'
        #
        # cmd = 'exit'
        # tn.write(cmd+ENTER)
        # tn.expect(['root'],10)

        if globalvar.boardtype == "E580-VX6300":
            strw = recode('检查48口类型板卡发包情况')
            work.writerunlog(strw)

            cmd = 'sh check_packet_test_48.sh'
            pattern = cmd + '.+root'
            pattern = re.compile(pattern, re.IGNORECASE | re.DOTALL)
            tn.write(cmd + ENTER)
            (index, match, data) = tn.expect([pattern], timeout=300)
            print data
            data_log = data_log + data
            work.writecmdlog(data)
            work.writelogtofile(logfile, data)
            if index == -1:
                strw = recode('读取发包数量失败')
                print strw
                work.writerunlog(strw)
                flag = 'FAIL'

            pattern = 'FAIL'
            pattern = re.compile(pattern, re.IGNORECASE | re.DOTALL)
            p = re.search(pattern,data)
            if p :
                flag = 'FAIL'
        elif globalvar.boardtype == "E580-VX6300A2":
            strw = recode('检查36口类型板卡发包情况')
            work.writerunlog(strw)

            cmd = 'sh check_packet_test.sh'
            pattern = cmd + '.+root'
            pattern = re.compile(pattern, re.IGNORECASE | re.DOTALL)
            tn.write(cmd + ENTER)
            (index, match, data) = tn.expect([pattern], timeout=300)
            print data
            data_log = data_log + data
            work.writecmdlog(data)
            work.writelogtofile(logfile, data)
            if index == -1:
                strw = recode('读取发包数量失败')
                print strw
                work.writerunlog(strw)
                flag = 'FAIL'

            pattern = 'FAIL'
            pattern = re.compile(pattern, re.IGNORECASE | re.DOTALL)
            p = re.search(pattern, data)
            if p:
                flag = 'FAIL'

        else:
            strw = recode('板卡获取失败')
            print strw
            work.writerunlog(strw)
            flag = 'FAIL'

        # cmd = 'cat memtest.log | grep "PASS"'
        # pattern = 'memtester \w\w\w\w'
        # pattern = re.compile(pattern, re.IGNORECASE | re.DOTALL)
        # tn.write(cmd + ENTER)
        # (index, match, data) = tn.expect([pattern], timeout=60)
        # print data
        # data_log = data_log + data
        # work.writecmdlog(data)
        # work.writelogtofile(logfile, data)
        # if index == -1:
        #     strw = recode('读取发包数量失败')
        #     print strw
        #     work.writerunlog(strw)
        #     flag = 'FAIL'
        #
        # pattern = 'FAIL'
        # pattern = re.compile(pattern, re.IGNORECASE | re.DOTALL)
        # p = re.search(pattern,data)
        # if p :
        #     flag = 'FAIL'

        tn.write('exit' + ENTER)
        tn.expect(['Switch#'],timeout=10)

        loginfos[f_name] = data_log
        globalvar.loginfos = loginfos

        strw = recode('%s ...... %s'%(f_name, flag))
        print strw 
        work.writerunlog(strw)

        if flag == "PASS":
            return SUCCESS_RT
        else:
            return ERROR_RT
    except KeyboardInterrupt:
        strw = recode('程序执行到[%s.%s]被手动终止'%(file_name,f_name))
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[%s.%s]异常退出!异常信息为%s' % (file_name,f_name,err))
        print strw
        work.writerunlog(strw)
        return ERROR_RT


def checkportmac():
    try:
        tt = globalvar.tt
        err_count = globalvar.err_count
        loginfos = globalvar.loginfos
        tn = globalvar.TN
        f_name = sys._getframe().f_code.co_name
        dirValue = globalvar.LOG_DIR
        logfile = os.path.join(dirValue, '%s.log') % f_name
        cfginfos = globalvar.CFG_INFOS  # 从globalvar中获得CFG_INFOS
        data_log = ''
        flag = 'PASS'


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
        p = re.compile(pattern,re.IGNORECASE | re.DOTALL)
        if p.search(data) != None:
            strw = recode('抓取到port有down状态...')
            print strw
            work.writerunlog(strw)
            # flag = 'FAIL'
            strw1 = recode("第%s次重启时有抓到down状态" % str(tt+1))
            print strw1
            work.writerunlog(strw1)

            globalvar.err_count = err_count + 1
            strw2 = recode("目前down状态共有%s次" % globalvar.err_count )
            print strw2
            work.writerunlog(strw2)

        tn.write('exit' + ENTER)
        tn.expect(['CTC_CLI#'],timeout=10)

        tn.write('exit' + ENTER)
        tn.expect(['Switch#'],timeout=10)

        loginfos[f_name] = data_log
        globalvar.loginfos = loginfos

        strw = recode('%s ...... %s' % (f_name, flag))
        print strw
        work.writerunlog(strw)

        if flag == "PASS":
            return SUCCESS_RT
        else:
            return ERROR_RT

    except KeyboardInterrupt:
        strw = recode('程序执行到[%s.%s]被手动终止' % (file_name, f_name))
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[%s.%s]异常退出!异常信息为%s' % (file_name, f_name, err))
        print strw
        work.writerunlog(strw)
        return ERROR_RT

def sleep_time():
    try:
        cfginfos = globalvar.CFG_INFOS
        sleep_time = cfginfos['BURNINTIME']['sleep_time']
        loginfos = globalvar.loginfos
        tn = globalvar.TN
        f_name = sys._getframe().f_code.co_name
        dirValue = globalvar.LOG_DIR
        logfile = os.path.join(dirValue, '%s.log') % f_name
        cfginfos = globalvar.CFG_INFOS  # 从globalvar中获得CFG_INFOS
        data_log = ''
        flag = 'PASS'

        strw = recode('高温到低温静置时间为%s小时') % sleep_time
        print strw
        work.writerunlog(strw)

        num = int(float(sleep_time) * 3600)
        time.sleep(num)

        if flag == "PASS":
            return SUCCESS_RT
        else:
            return ERROR_RT

    except KeyboardInterrupt:
        strw = recode('程序执行到[%s.%s]被手动终止' % (file_name, f_name))
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[%s.%s]异常退出!异常信息为%s' % (file_name, f_name, err))
        print strw
        work.writerunlog(strw)
        return ERROR_RT

def lowtemp_sleep():
    try:
        cfginfos = globalvar.CFG_INFOS
        sleep_time = cfginfos['BURNINTIME']['lowtemp_time']
        power_port = cfginfos['NPSINFO']['nps_powerport']
        loginfos = globalvar.loginfos
        nps_tn = globalvar.NPS_TN
        print nps_tn
        f_name = sys._getframe().f_code.co_name
        dirValue = globalvar.LOG_DIR
        logfile = os.path.join(dirValue, '%s.log') % f_name
        cfginfos = globalvar.CFG_INFOS  # 从globalvar中获得CFG_INFOS
        data_log = ''
        flag = 'PASS'

        nps_tn.write(ENTER)
        nps_tn.write(ENTER)
        # cmd = '/off a*'

        offstr = '/off %s'%power_port
        onstr = '/on %s'%power_port

        nps_tn.write('/off %s\r\n\r\n'%power_port)
        # pattern = 'NPS>\s*'
        # pattern = re.compile(pattern,re.IGNORECASE | re.DOTALL)
        #
        # (index,match,data) = nps_tn.expect([pattern],timeout=10)
        data = nps_tn.read_very_eager()
        print data
        # if index == -1:
        #     strw = recode('NPS关机失败')
        #     print strw
        #     work.writerunlog(strw)
        #     flag = 'FAIL'

        flag_ = True
        count = 0
        while flag_:
            if offstr not in data:
                print data
                time.sleep(1)
                nps_tn.write('/off %s\r\n\r\n'%power_port)
                data = nps_tn.read_very_eager()
                print data
                count += 1
                if count == 20:
                    strw = recode('发送重启命令次数达到限制，关机失败')
                    print strw
                    work.writerunlog(strw)
                    return ERROR_RT
            else:
                flag_ = False

        strw = recode('低温静置时间为%s小时' % sleep_time)
        print strw
        work.writerunlog(strw)


        num = int(float(sleep_time) * 3600)
        time.sleep(num)

        nps_tn.write(ENTER)
        nps_tn.write(ENTER)
        # cmd = '/on a*'
        nps_tn.write('/on %s\r\n\r\n'%power_port)
        # pattern = 'NPS>'
        # pattern = re.compile(pattern, re.IGNORECASE | re.DOTALL)
        # (index, match, data) = nps_tn.expect([pattern], timeout=10)
        data = nps_tn.read_very_eager()
        print data
        # if index == -1:
        #     strw = recode('NPS开机失败')
        #     print strw
        #     work.writerunlog(strw)
        #     flag = 'FAIL'

        flag_ = True
        count = 0
        while flag_:
            if onstr not in data:
                print data
                time.sleep(2)
                nps_tn.write('/on %s\r\n\r\n'%power_port)
                data = nps_tn.read_very_eager()
                print data
                count += 1
                if count == 20:
                    strw = recode('发送重启命令次数达到限制,开机失败')
                    print strw
                    work.writerunlog(strw)
                    return ERROR_RT
            else:
                flag_ = False


        strw = recode('NPS已经开机')
        print strw
        work.writerunlog(strw)

        if flag == "PASS":
            return SUCCESS_RT
        else:
            return ERROR_RT

    except KeyboardInterrupt:
        strw = recode('程序执行到[%s.%s]被手动终止' % (file_name, f_name))
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[%s.%s]异常退出!异常信息为%s' % (file_name, f_name, err))
        print strw
        work.writerunlog(strw)
        return ERROR_RT

def CheckNetPortTest():
    try:
        loginfos = globalvar.loginfos
        tn = globalvar.TN
        f_name = sys._getframe().f_code.co_name
        dirValue = globalvar.LOG_DIR
        logfile = os.path.join(dirValue, '%s.log')%f_name
        cfginfos = globalvar.CFG_INFOS    # 从globalvar中获得CFG_INFOS
        data_log = ''
        flag = 'PASS'

        cmd = 'ip netns exec mgmt mgmt_phy eth0 22 1'
        tn.write(cmd+ENTER)
        tn.expect(['root'],10)
        cmd = 'ip netns exec mgmt /bin/sh'
        tn.write(cmd+ENTER)
        tn.expect(['#'],10)

        cmd = 'sh eth_counter.sh'
        tn.write(cmd+ENTER)
        tn.expect(['#'],10)

        cmd = 'sh tx_port_packet.sh 0 10000'
        tn.write(cmd+ENTER)
        tn.expect(['#'],300)

        cmd = 'sh show_netport_counter.sh '
        pattern = '#'
        pattern = re.compile(pattern, re.IGNORECASE | re.DOTALL)
        tn.write(cmd + ENTER)
        (index, match, data) = tn.expect([pattern], timeout=60)
        print data
        data_log = data_log + data
        #work.writecmdlog(data)
        work.writelogtofile(logfile, data)
        if index == -1:
            strw = recode('读取发包数量失败')
            print strw
            work.writerunlog(strw)
            flag = 'FAIL'

        pattern = 'FAIL'
        pattern = re.compile(pattern, re.IGNORECASE | re.DOTALL)
        p = re.search(pattern,data)
        if p :
            flag = 'FAIL'

        cmd = 'exit'
        tn.write(cmd+ENTER)
        tn.expect(['root'],10)

        globalvar.flag2 = flag

        loginfos[f_name] = data_log
        globalvar.loginfos = loginfos

        strw = recode('%s ...... %s'%(f_name, flag))
        print strw 
        work.writerunlog(strw)

        if flag == "PASS":
            return SUCCESS_RT
        else:
            return ERROR_RT
    except KeyboardInterrupt:
        strw = recode('程序执行到[%s.%s]被手动终止'%(file_name,f_name))
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[%s.%s]异常退出!异常信息为%s' % (file_name,f_name,err))
        print strw
        work.writerunlog(strw)
        return ERROR_RT

def SetOEMInformation():
    try:
        loginfos = globalvar.loginfos
        tn = globalvar.TN
        f_name = sys._getframe().f_code.co_name
        dirValue = globalvar.LOG_DIR
        logfile = os.path.join(dirValue, '%s.log')%f_name
        flag = 'PASS'
        data_log = ''

        pattern = 'Password'
        p = re.compile(re.escape(pattern), re.DOTALL | re.IGNORECASE)
        tn.write('internal-debug' + ENTER)
        time.sleep(1)
        (index,match,data) = tn.expect([p], timeout=5)
        work.writecmdlog(data)
        work.writelogtofile(logfile,data)
        if index == -1:
            strw = recode('板卡登陆debug失败1')
            print strw
            work.writerunlog(strw)

        pattern = '#'
        p = re.compile(re.escape(pattern), re.DOTALL | re.IGNORECASE)
        tn.write('!@#' + ENTER)
        (index,match,data) = tn.expect([p], timeout=5)
        work.writecmdlog(data)
        work.writelogtofile(logfile,data)
        if index == -1:
            strw = recode('板卡登陆debug失败2')
            print strw
            work.writerunlog(strw)

        # 写入 config.ini TODO
        cfginfos = globalvar.CFG_INFOS
        cmd = cfginfos['OEM']['cmd']
        # cmd = 'update oem information package ENOS product VX3100 boardtype VX3100A3 snmpoid 27975 chassistype PIZZA_BOX card1 NULL card2 NULL card3 NULL company 2016 Wanfang Electronic Co.,Ltd'
        if globalvar.BOARD_TYPE == 'YES':
            for i in cmd:
                tn.write(i)
                time.sleep(0.05)
            tn.write(ENTER)
        tn.write('exit'+ENTER)
        data_log = data_log + cmd

        loginfos[f_name] = data_log
        globalvar.loginfos = loginfos

        strw = recode('%s ...... %s'%(f_name, flag))
        print strw 
        work.writerunlog(strw)

        if flag == "PASS":
            return SUCCESS_RT
        else:
            return ERROR_RT
    except KeyboardInterrupt:
        strw = recode('程序执行到[%s.%s]被手动终止'%(file_name,f_name))
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[%s.%s]异常退出!异常信息为%s' % (file_name,f_name,err))
        print strw
        work.writerunlog(strw)
        return ERROR_RT

#检查温度和电压
def read_temp():
    """check temperature and voltage of the device"""
    try:
        dirValue = globalvar.LOG_DIR
        logfile = os.path.join(dirValue, 'check_temp_vol.log')
        tn = globalvar.TN
        loginfos = globalvar.loginfos
        f_name = sys._getframe().f_code.co_name
        data_log = ''
        flag = 'PASS'

        #读取温度电压结果
        cmd = 'sh read_tmp.sh '
        pattern = '\d\d'
        pattern = re.compile(pattern, re.IGNORECASE | re.DOTALL)
        tn.write(cmd + ENTER)
        (index, match, data) = tn.expect([pattern], timeout=60)
        data_log = data_log + data
        print data
        work.writecmdlog(data)
        work.writelogtofile(logfile, data)
        if index == -1:
            strW = recode('读取温度log失败')
            print strW
            work.writerunlog(strW)
            flag = 'FAIL'

        pattern = '\d\d'
        pattern = re.compile(pattern, re.IGNORECASE | re.DOTALL)
        p = re.search(pattern,data)
        if p:
            temp = p.group()
            if 20 <= int(temp) <=60:
                strW = recode('温度测试通过')
                print strW
            else:
                strW = recode('温度不在合理范围内')
                print strW
                work.writerunlog(strW)
                flag = 'FAIL'
        else:
            strW = recode('读取温度log失败')
            print strW
            work.writerunlog(strW)
            flag = 'FAIL'

        loginfos[f_name] = data_log 
        globalvar.loginfos = loginfos

        strw = recode('%s ...... %s'%(f_name, flag))
        print strw 
        work.writerunlog(strw)

        if flag == "PASS":
            return SUCCESS_RT
        else:
            return ERROR_RT 

    except KeyboardInterrupt:
        strw = recode('程序执行到[special.%s]被手动终止'%f_name)
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[special.%s]异常退出!异常信息为%s' % (f_name,err))
        print strw
        work.writerunlog(strw)
        return ERROR_RT

def diag_all_i2c():
    try:
        loginfos = globalvar.loginfos
        tn = globalvar.TN
        f_name = sys._getframe().f_code.co_name
        dirValue = globalvar.LOG_DIR
        logfile = os.path.join(dirValue, 'diag_all_i2c.log')
        data_log = ''
        flag = 'PASS'

        cmd = 'diag_all_i2c.sh'
        for i in cmd:
            tn.write(i)
            time.sleep(0.1)
        shellStr = cmd + '.+'+'root'
        shellStr = re.compile(shellStr, re.IGNORECASE | re.DOTALL)
        tn.write(ENTER)
        (index, match, data) = tn.expect([shellStr], timeout=120)
        data_log = data_log + data
        work.writecmdlog(data)
        work.writelogtofile(logfile, data)
        if index == -1:
            strw = recode('读取i2c信息失败')
            print strw
            work.writerunlog(strw)
            flag = 'FAIL'

        strmatch = 'FAIL'
        p = re.compile(strmatch,re.IGNORECASE | re.DOTALL)
        if p.search(data):
            strw = recode('i2c信息读取异常')
            print strw
            work.writerunlog(strw)
            flag = 'FAIL'

        loginfos[f_name] = data_log
        globalvar.loginfos = loginfos

        strw = recode('%s ...... %s'%(f_name, flag))
        print strw 
        work.writerunlog(strw)

        if flag == "PASS":
            return SUCCESS_RT
        else:
            return ERROR_RT
    except KeyboardInterrupt:
        strw = recode('程序执行到[special.%s]被手动终止'%f_name)
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[special.%s]异常退出!异常信息为%s' % (f_name,err))
        print strw
        work.writerunlog(strw)
        return ERROR_RT

def check_memtester():
    """check temperature and voltage of the device"""
    try:
        dirValue = globalvar.LOG_DIR
        logfile = os.path.join(dirValue, 'check_ddr.log')
        tn = globalvar.TN
        loginfos = globalvar.loginfos
        f_name = sys._getframe().f_code.co_name
        data_log = ''
        flag = 'PASS'

        cmd = 'sh check_memtester.sh 10 10'
        for i in cmd:
            tn.write(i)
            time.sleep(0.05)
        pattern = cmd + '.+'+'root'
        pattern = re.compile(pattern, re.IGNORECASE | re.DOTALL)
        tn.write(ENTER)
        (index, match, data) = tn.expect([pattern], timeout=60)
        #print data
        data_log = data_log + data
        work.writecmdlog(data)
        work.writelogtofile(logfile, data)
        if index == -1:
            strw = recode('读取内存失败')
            print strw
            work.writerunlog(strw)
            flag = 'FAIL'

        pattern = 'FAIL'
        pattern = re.compile(pattern, re.IGNORECASE | re.DOTALL)
        p = re.search(pattern,data)
        if p :
            flag = 'FAIL'

        loginfos[f_name] = data_log
        globalvar.loginfos = loginfos

        strw = recode('%s ...... %s'%(f_name, flag))
        print strw 
        work.writerunlog(strw)

        if flag == "PASS":
            return SUCCESS_RT
        else:
            return ERROR_RT

    except KeyboardInterrupt:
        strw = recode('程序执行到[special.%s]被手动终止'%f_name)
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = '程序执行到[special.%s]异常退出!异常信息为%s' % (f_name,err)
        print recode(strw)
        return ERROR_RT

def SelectDownloadPmon():
    """选择是否下载Pmon镜像"""
    try:
        loginfos = globalvar.loginfos
        f_name = sys._getframe().f_code.co_name

        if globalvar.BOARD_TYPE == 'YES':
            connection.ListenAndGotoUboot()
            Downloadpmon()
            connection.ListenAndGotoUboot()
            ClearFlash()
            connection.BootAndGotoLinux()
            return SUCCESS_RT
        elif globalvar.BOARD_TYPE == 'NO':
            strw = recode('此板卡跳过下载linux镜像等')
            print strw
            work.writerunlog(strw)
            return SUCCESS_RT
        else:
            strw = recode('config配置有问题')
            print strw
            work.writerunlog(strw)
            return ERROR_RT

    except KeyboardInterrupt:
        strw = recode('程序执行到[special.%s]被手动终止'%f_name)
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = '程序执行到[special.%s]异常退出!异常信息为%s' % (f_name,err)
        print recode(strw)
        return ERROR_RT

def SelectDownloadLinux():
    """选择是否下载Pmon镜像"""
    try:
        loginfos = globalvar.loginfos
        f_name = sys._getframe().f_code.co_name

        if globalvar.BOARD_TYPE == 'YES':
            DownloadLinuxFile()
            CopylinuxFile()
            connection.ListenAndGotoLinux()
            return SUCCESS_RT
        elif globalvar.BOARD_TYPE == 'NO':
            strw = recode('此板卡跳过下载linux镜像等')
            print strw
            work.writerunlog(strw)
            return SUCCESS_RT
        else:
            strw = recode('config配置有问题')
            print strw
            work.writerunlog(strw)
            return ERROR_RT

    except KeyboardInterrupt:
        strw = recode('程序执行到[special.%s]被手动终止'%f_name)
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = '程序执行到[special.%s]异常退出!异常信息为%s' % (f_name,err)
        print recode(strw)
        return ERROR_RT

