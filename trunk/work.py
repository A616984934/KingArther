#!/usr/bin/env python
# This Python file uses the following encoding: utf-8

# @package AutoTest
# 功能：生产测试应用模块，定义通用功能函数为主程序提供相关功能接口.
#
# 作者：hchen
#
# 日期：2014-03-12
#
# 文件：work.py

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


## run提示信息写入日志
#
#将提示信息写入runlog的函数
def writerunlog(strw):
    """Write run log.
    参数传递:   strw(要写入的字符串)
    返回值:     NULL(执行异常时会返回OTHER_ERROR和ERROR_RT)
    """
    try:
        MODE = globalvar.MODE
        if MODE == 'AUTOTOOL':
            ID = globalvar.ID
            tcplib.SendRunlogMsg(ID, unrecode(strw))
            
        RUNLOGPATH = globalvar.RUN_LOG
        logpath = RUNLOGPATH
        runlog = open(logpath, 'a')
        print >> runlog, strw
        runlog.close()

    except KeyboardInterrupt:
        strw = recode('程序执行中断!')
        print strw
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序异常退出!work.writerunlog,异常信息%s' % err)
        print strw
        return ERROR_RT


##将cmd日志写到指定的文件之中
#
#这是为了方便查看某些测试项目的log,不必再在cmd.log内寻找
def writelogtofile(logpath, data):
    """
    传入参数:    logpath  要写日志的文件的绝对路径
                 data     写入的内容
    返回值       NULL(在异常情况下回返回ERROR_RT和OTHER_ERROR)
    """
    try:
        cmdlog = open(logpath, 'a')
        print >> cmdlog, data
        cmdlog.close()

    except KeyboardInterrupt:
        strw = recode('程序执行中断!')
        print strw
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序异常退出!work.writelogtofile,异常信息%s' % err)
        print strw
        return ERROR_RT



class Test_1():
    @pytest.fixtrue
    def login(self):
    retrun cookies
    def test1_(self login):

    def test2_(self):


## 将telnet通道的信息写到cmdlog日志之中
#
#将发送的命令以及返回结果写入cmdlog日志之中
#cmdlogpath为全局变量,为cmdlog文件的路径
def writecmdlog(data):
    """Write cmd log.
    参数传递:   data(写入的字符串)
    返回值:     NULL(执行异常时会返回OTHER_ERROR和ERROR_RT)
    """
    try:
        logpath = globalvar.CMD_LOG
        cmdlog = open(logpath, 'a')
        print >> cmdlog, data
        cmdlog.close()

        MODE = globalvar.MODE
        if MODE == 'AUTOTOOL':
            ID = globalvar.ID
            datalist = data.strip().split('\n')
            for key in datalist:
                tmp = key.strip().strip('\n')
                if len(tmp) == 0:
                    continue
                tcplib.SendCmdlogMsg(ID, tmp)

    except KeyboardInterrupt:
        strw = recode('程序执行中断!')
        print strw
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序异常退出!writecmdlog,异常信息%s' % err)
        print strw
        return ERROR_RT


##将文件夹打包
#
#打包的时候,根据flag在打包的名字后面加上PASS或者FAIL
def MakeZip(log_dir, flag):
    """To make log zip packege.
    传入参数:    logdir(文件夹)
                 flag(标志,当flag为False的时候,
                      在打包文件末尾加上FAIL)
    返回值:      zpath(打包的文件路径)
    """
    try:
        strw = recode('正在打包日志文件夹...')
        print strw
        writerunlog(strw)
        # GFILEZIP = globalvar.LOG_DIR

        # gfile = os.path.basename(GFILEZIP)
        # gfile = gfile.upper()

        # if not flag:
        #     gfile += '-FAIL'
        # else:
        #     gfile += '-PASS'
        # gfile += '.zip'
        if flag:
            result = 'PASS'
        else:
            result = 'Fail'
        time_str = globalvar.test_start_time_str
        import runconfig
        product = runconfig.product
        station = runconfig.station
        cfginfos = globalvar.CFG_INFOS
        getinfos = globalvar.getinfos
        ps = globalvar.PS
        gfile = '%s_%s_%s_%s-%s.zip' %(product, ps, station, time_str, result)

        gfile = gfile.upper()
        run_mode = globalvar.burnin_mode
        if run_mode == '1':
            gfile = gfile.replace('BURNIN', 'Data')
        elif run_mode == '2':
            gfile = gfile.replace('BURNIN', 'Reboot')
        elif run_mode == '3':
            gfile = gfile.replace('BURNIN', 'PowerCycle')
        elif run_mode == '4':
            gfile = gfile.replace('BURNIN', 'DL-CustImage')

        zpath = os.path.join(cur_file_dir(), gfile)
        if os.path.exists(zpath):
            os.remove(zpath)
        zfile = zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED)

        pathfile = []
        for root, dirs, l_file in os.walk(log_dir):
            for name in l_file:
                new_name = os.path.join(root, name)
                pathfile.append(new_name)

        if not pathfile:
            return False

        for tar in pathfile:
            zfile.write(tar, tar[len(log_dir):])

        try:
            wkdir = cur_file_dir()
            config_file = os.path.join(wkdir, 'config.ini')
            zfile.write(config_file, os.path.basename(config_file))
            changelog_file = os.path.join(wkdir, 'changenote.txt')
            zfile.write(changelog_file, os.path.basename(changelog_file))
        finally:
            zfile.close()

            strw = recode('已打包日志文件%s.' % os.path.basename(zpath))
            print strw
            print zpath
            writerunlog(strw)
            return zpath

    except KeyboardInterrupt:
        strw = recode('程序执行中断!')
        print strw
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序异常退出!,MakeZip,异常信息为%s' % err)
        print strw
        return ERROR_RT


##将指定的文件夹进行打包并上传到制定的FTP server
#
#ftpinfos为包含登录ftp信息的一个字典,其key分别为ftpaddr,port
#user,passwd,dir
def UploadLogDir(flag=False):
    """upload the specified dir to the specified FTP server
    参数传递:    ftpinfos   包含ftp server的ip port user password的一个字典
                 logdir     要上传的文件夹
                 flag       默认为False,打包的过程中会根据此flag来在打包文件的末尾加上
                            PASS或者FAIL的提示信息)
    返回值:      SUCCESS_RT 上传成功
                 ERROR_RT   上传失败
    """
    try:
        globalvar.Console_print_detect = 'stop'
        cfginfos = globalvar.CFG_INFOS
        ftpinfos = cfginfos['SETTING']
        ip = ftpinfos['ftp_ip']
        port = ftpinfos['ftp_port']
        user = ftpinfos['ftp_usr']
        passwd = ftpinfos['ftp_pwd']
        ftpdir = ftpinfos['ftp_addr']
        logdir = globalvar.LOG_DIR
        zpath = MakeZip(logdir, flag)
        if zpath == ERROR_RT or zpath == OTHER_ERROR:
            return ERROR_RT
        if not zpath:
            strw = recode('[%s]日志文件夹为空，不上传.' % os.path.basename(logdir))
            print strw
            return ERROR_RT

        strw = recode('正在上传日志文件[%s]...' % os.path.basename(zpath))
        print strw
        writerunlog(strw)

        ftp = FTP()
        ftp.connect(ip, port)
        ftp.login(user, passwd)

        ftp.cwd(ftpdir)

        f = open(zpath, 'rb')
        ftp.storbinary('STOR {0}'.format(os.path.basename(zpath)), f, 1024)
        f.close()
        ftp.close()

        os.remove(zpath)

        strw = recode('已上传日志文件[%s].' % os.path.basename(zpath))
        print strw

        return SUCCESS_RT

    except ftplib.error_perm:
        strw = recode('上传日志文件失败，请确保FTP SERVER端已存在%s文件夹，否则需要事先手动创建！' % dir)
        print strw
        writerunlog(strw)
        return ERROR_RT
    except socket.error:
        strw = recode('上传日志文件{0:s}失败，请确保网线连接正常，保持网络通畅！'.format(os.path.basename(zpath)))
        print strw
        writerunlog(strw)
        return ERROR_RT
    except KeyboardInterrupt:
        strw = recode('程序执行中断!')
        print strw
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序异常退出!UploadLogDir,异常信息%s' % err)
        print strw
        return ERROR_RT


## 获取当前文件所在文件夹路径.
#
# 通过sys.path[0]判断并返回当前文件所在文件夹路径.
def cur_file_dir():
    path = sys.path[0]
    if os.path.isdir(path):
        return path
    if os.path.isfile(path):
        return os.path.dirname(path)


## 创建日志文件夹.
#
# 日志文件夹的名称为PS序列号 + 检测类型（生产/出货/拷机） + 开始时间
def MakeLogDir():
    """
    传入参数:   ps      板卡的ps号
                logdir  log日志根目录的名称,默认为logdir
    工作方式:   根据ps来产生一定格式的日志文件供写入日志
    返回值:     SUCCESS_RT(创建成功)
    """
    try:
        # 从globalvar中获取相关参数
        STATION = globalvar.STATION
        log_dir = globalvar.TOP_LOG_FOLDER_NAME

        # 更新开始测试的时间
        globalvar.zipfile = time.strftime('%Y%m%d%H%M')
        globalvar.test_start_time_str = time.strftime('%Y%m%d%H%M')
        # make logdir.
        log = os.path.join(cur_file_dir(), log_dir)
        path = os.path.join(log, STATION)
        if os.path.exists(log):
            shutil.rmtree(log)
        if not os.path.exists(log):
            os.mkdir(log)

        if log_dir == 'logdir':
            if os.path.exists(path):
                shutil.rmtree(path)
            os.mkdir(path)
        else:
            path = log

        # 传递相关参数给globalvar
        runlogpath = os.path.join(path, 'run.log')
        cmdlogpath = os.path.join(path, 'cmd.log')

        RUNLOGPATH = runlogpath
        CMDLOGPATH = cmdlogpath

        globalvar.RUN_LOG = runlogpath
        globalvar.LOG_DIR = path
        globalvar.CMD_LOG = cmdlogpath

        writerunlog(RUNLOGPATH)
        writecmdlog(CMDLOGPATH)

        return SUCCESS_RT

    except KeyboardInterrupt:
        strw = recode('程序执行中断!')
        print strw
        return ERROR_RT
    except Exception, err:
        strw = recode('程序异常退出!,MakeLogDir,异常信息为%s' % err)
        print strw
        return ERROR_RT


##将字符串中的特殊字符前面加上'\'
#
#将此字符串作为正则表达式使用时候,防止
#这些字符与正则表达式的特殊符号冲突,
#需要将这些特殊符号进行转义
def StrToExp(s):
    """
    参数传递:    string(字符串)
    工作方式:    把字符串中的含有正则表达式特殊字符的替换为前面加上'\'
    返回值:      expression(正则表达式)
    """
    char_list = ['\\', '.', '[', ']', '*', '+', '?', '-', '^', '$', ')', '(', '!', '=', '<']
    for char in char_list:
        tmp = '\\' + char
        if s.find(char) != -1:
            s = s.replace(char, tmp)
    return s


##在指定文件中每行中匹配特定的字符串
#
#用正则表达式匹配指定文件的每一行,若
#匹配成功则返回匹配到的字符串
def search_logfile(pattern, logfile):
    """
    参数传递:   pattern 正则表达式
                logfle  文件
    工作方式:   在指定文件中每行中匹配特定的字符串
    返回值:     tmpstr 匹配到的字符串,若没有匹配到则返回空
    """
    try:
        tmpstr = ''
        f = open(os.path.normcase(logfile))
        p = pattern
        line = f.readline()
        while line:
            m = p.search(line)
            if m:
                tmpstr = m.group()
                break
            line = f.readline()
        f.close()
        return tmpstr

    except KeyboardInterrupt:
        strW = '程序执行中断!'
        print strW
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序异常退出!,search_logfile,异常信息为%s' % err)
        print strw
        return ERROR_RT


##把含有,的数字字符串转换为数字
#
#举例把23,123,0a12转换为数字23123012
def translate_str_to_int(number):
    """
    参数传递:   number  含有,的数字字符串
    工作方式:   把含有,的数字字符串转换为数字
    返回值:     int格式的数字
    """
    try:
        return int(filter(str.isdigit, str(number)))
    except KeyboardInterrupt:
        strW = '程序执行中断!'
        print strW
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序异常退出!,translate_number_to_int,异常信息为%s' % err)
        print strw
        return ERROR_RT


#上传板卡内的log文件
def upload_diag_log(child, SN, Mark):
    strW = recode('开始上传diag的log...')
    print strW
    writerunlog(strW)
    try:
        cfginfos = globalvar.CFG_INFOS
        cfg_setting = cfginfos['SETTING']
        ftpIP = cfg_setting['ftp_ip']
        logFtpUser = cfg_setting['ftp_usr']
        logFtpPassed = cfg_setting['ftp_pwd']
        DIR = cfg_setting['dir']
        ftpPath = cfg_setting['ftp_addr']

        curt_Time = time.strftime("%Y%m%d%H%M")
        t = 0
        cmd = 'sh /tmp/ftp_upload.sh %s %s %s %s %s %s %s %s &' % (
            ftpIP, logFtpUser, logFtpPassed, DIR, SN, Mark, curt_Time, ftpPath)
        child.write(cmd + ENTER)
        time.sleep(0.5)
        (i, match, data) = child.expect(['Upload End'], timeout=30)
        writecmdlog(data)
        while i == -1:
            (i, match, data) = child.expect(['Upload End'], timeout=30)
            writecmdlog(data)
            t += 1
            if t > 10:
                strW = recode('未能成功上传diag的log,请手动上传')
                print strW
                writerunlog(strW)
                break
            else:
                continue
        if i == 0:
            strW = recode('成功开始上传diag的log')
            print strW
            writerunlog(strW)
        return SUCCESS_RT
    except KeyboardInterrupt:
        strW = '程序执行中断!'
        print strW
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序异常退出!,upload_diag_log,异常信息为%s' % err)
        print strw
        return ERROR_RT


def delay_time(workmode):
    """
    参数传递:   number  含有,的数字字符串
    工作方式:   把含有,的数字字符串转换为数字
    返回值:     int格式的数字
    """
    try:
        """
        此功能模块还需要详细设计
        """
        cfginfos = globalvar.CFG_INFOS
        kw = 'bcm_time'
        BurnIn_Time = cfginfos['BURNINTIME'][kw]
        TimeDelay = float(BurnIn_Time) * 3600 # 将小时转化成秒
        tt = str(float(BurnIn_Time))
        strW = recode('已经开始拷机，%s拷机时间为【%s】小时'%(workmode,tt))
        writerunlog(strW)
        #设置拷机倒计时
        a = int(TimeDelay)/600
        a = int(a)
        for i in range(a):
            j = a-i
            Time = j*10
            strW = recode('已经开始【%s】拷机，还要拷机【%d】分钟'%(workmode, Time))
            print strW
            writerunlog(strW)
            time.sleep(600)
        return SUCCESS_RT
    except KeyboardInterrupt:
        strW = '程序执行到[work.delay_time]被手动终止'
        print recode(strW)
        return OTHER_ERROR
    except Exception,err:
        strW = '程序执行到[work.delay_time]异常退出!异常信息为%s'%err
        print recode(strW)
        return ERROR_RT


if __name__ == '__main__':
    logdir = r'D:\PyWork\autoAC2768_NewModule\logdir\Prd_201404101803'
    print '---------------------'
    print os.getcwd()
    print '---------------------'
    print logdir
    MakeZip(logdir, True)