#!/usr/bin/env python
# This Python file uses the following encoding: utf-8

# @package autotest
# 功能：为自动化生产脚本定义通用的模块.
#
# 作者：hchen.
#
# 日期：2014-03-12.
#
# 文件：app.py.
# import system modules
import os
import re
import time
import sys

# import our modules
import work                 # 写日志，以及上传到ftp的相关函数
import tcplib               # 与autotool通信的函数
import globalvar            # 一些全局变量
import command              # 一些常用的命令
import connection
import runconfig
from work import recode     # 从work那边获取recode
import special
import appconfig

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

## show fail
def show_fail_info(strw):
    tn = globalvar.TN
    tn.write('quit' + ENTER)
    # 用来传递给串口记录程序结束使用
    globalvar.Console_print_detect = 'stop'
    mode = globalvar.MODE
    strw = recode(strw)
    print strw
    work.writerunlog(strw)
    work.UploadLogDir()
    if mode == 'AUTOTOOL':
        id = globalvar.ID
        tcplib.SendStatusMsg(id, strw)
    return

## 获取产品序列号
#
# 获取产品序列号，以便后续能够进行FRU升级以及创建相关的log
def get_ps(board_name):
    """
    @return ps: 产品序列号
    """
    global ps
    cfginfos = globalvar.CFG_INFOS
    ps3bit = cfginfos['INPUTINFO']['ps3bit']
    ps3bits = ps3bit.split(',')
    try:
        strw = '请输入%s产品序列号(P/S):' % board_name
        while True:
            strw = recode(strw)
            ps = raw_input(strw)
            if len(ps) != 11:
                strw = 'PS条码输入错误[长度不为11位]！请重新输入%s产品序列号(P/S):' % board_name
                continue
            elif ps[:3] not in ps3bits:
                strw = 'PS条码输入错误[前3码不在%s中]！请重新输入%s产品序列号(P/S):' % (ps3bit, board_name)
                continue
            elif ps[3].isalpha() is False:
                strw = 'PS条码输入错误[第4码不为字母]！请重新输入%s产品序列号(P/S):' % board_name
                continue
            else:
                break

        # 返回获取到的PS
        return ps
    except KeyboardInterrupt:
        strw = recode('程序执行到[app.get_ps]被手动终止')
        print strw
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[app.get_ps]异常退出!异常信息为%s' % err)
        print strw
        return ERROR_RT


## 获取板卡序列号
#
# 获取板卡序列号，以便后续能够进行FRU升级以及创建相关的log
def get_bs(board_name):
    """
    @return bs: 获取到的板卡序列号
    """
    global bs
    cfginfos = globalvar.CFG_INFOS
    bs3bit = cfginfos['INPUTINFO']['bs3bit']
    bs3bits = bs3bit.split(',')
    try:
        strw = '请输入%s板卡序列号(B/S):' % board_name
        while True:
            strw = recode(strw)
            bs = raw_input(strw)
            if len(bs) != 11:
                strw = 'BS条码输入错误[长度不为11位]！请重新输入%s产品序列号(B/S):' % board_name
                continue
            elif bs[:3] not in bs3bits:
                strw = 'BS条码输入错误[前3码不在%s中]！请重新输入%s板卡序列号(B/S):' % (bs3bit, board_name)
                continue
            elif bs[3].isalpha() is False:
                strw = 'BS条码输入错误[第4码不为字母]！请重新输入%s板卡序列号(B/S):' % board_name
                continue
            else:
                break

        #返回获取到的BS
        return bs
    except KeyboardInterrupt:
        strw = recode('程序执行到[app.get_bs]被手动终止')
        print strw
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[app.get_bs]异常退出!异常信息为%s' % err)
        print strw
        return ERROR_RT


## 获取板卡序列号
#
# 获取板卡序列号，以便后续能够进行FRU升级以及创建相关的log
def get_pmbs(boardid='0'):
    """
    @param boardid: 左路or右路
    @return pmbs: 获得的扣板序列号
    """
    global BS
    cfginfos = globalvar.CFG_INFOS
    bs3bit = cfginfos['INPUTINFO']['pmbs3bit']
    if boardid == '0':
        boardname = '扣板'
    elif boardid == '1':
        boardname = '左路扣板'
    else:
        boardname = '右路扣板'
    try:
        strw = '请输入%s板卡序列号(P/S):' % boardname
        while True:
            strw = recode(strw)
            BS = raw_input(strw)
            if len(BS) != 11:
                strw = 'PS条码输入错误[长度不为11位]！请重新输入%s板卡序列号(P/S):' % boardname
                continue
            elif BS[:3] != bs3bit:
                strw = 'PS条码输入错误[前3码不为%s]！请重新输入%s板卡序列号(P/S):' % (bs3bit, boardname)
                continue
            elif BS[3].isalpha() is False:
                strw = 'PS条码输入错误[第4码不为字母]！请重新输入%s板卡序列号(P/S):' % boardname
                continue
            else:
                break

        #返回获取到的BS
        return BS
    except KeyboardInterrupt:
        strw = recode('程序执行到[app.get_pmbs]被手动终止')
        print strw
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[app.get_pmbs]异常退出!异常信息为%s' % err)
        print strw
        return ERROR_RT


## 用来解析globalvar中的PNs
#
# 用来解析globalvar中的PNs
def GetPNinfos(pns):
    """
    get pn infos
    """
    try:
        pninfos = {}
        pninfo_lens = int(pns['pninfo_lens'])
        print pninfo_lens
        for key in pns.keys():
            if key == 'pninfo_lens':
                continue
            tmp = pns[key]
            tmplist = tmp.split('*+*')  # PNs中的分隔符为[*+*]
            if len(tmplist) != pninfo_lens:
                strw = recode('PNs中所包含的信息数量不对，请检查！')
                print strw
                work.writerunlog(strw)
                return ERROR_RT
            else:
                keywd = tmplist[0].strip()
                pninfos[keywd] = {}
                t = tmplist[1].strip()
                pninfos[keywd]['PN'] = t
                t = tmplist[2].strip()
                pninfos[keywd]['BN'] = t
                t = tmplist[3].strip()
                pninfos[keywd]['_minor_board_type'] = t
                t = tmplist[4].strip()
                pninfos[keywd]['_major_board_type'] = t
                t = tmplist[5].strip()
                pninfos[keywd]['product_version'] = t
                t = tmplist[6].strip()
                pninfos[keywd]['_board_version'] = t

        return pninfos
    except KeyboardInterrupt:
        strw = recode('程序执行到[app.GetPNinfos]被手动终止')
        print strw
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[app.GetPNinfos]异常退出!异常信息为%s' % err)
        print strw
        return ERROR_RT


## 用来解析globalvar中的BNs
#
# 用来解析globalvar中的BNs
def GetBNinfos(BNs):
    """
    get bn infos
    """
    try:
        bninfos = {}
        for key in BNs.keys():
            tmp = BNs[key]
            tmplist = tmp.split('*+*')  # PNs中的分隔符为[*+*]
            if len(tmplist) != 2:   # 元素列表个数，如果不是这个，说明BNs中格式与默认的不一致，则需要修改本函数
                strw = recode('PNs中所包含的信息数量不对，请检查！')
                print strw
                work.writerunlog(strw)
                return ERROR_RT
            else:
                keywd = tmplist[0].strip()
                bninfos[keywd] = {}
                t = tmplist[1].strip()
                bninfos[keywd]['BN'] = t

        return bninfos
    except KeyboardInterrupt:
        strw = '程序执行到[app.GetBNinfos]被手动终止'
        print recode(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = '程序执行到[app.GetBNinfos]异常退出!异常信息为%s' % err
        print recode(strw)
        return ERROR_RT


## 获取产品市场型号
#
# 获取产品市场型号， cmd模式下使用
def GetPN(board_name):
    """
    get pn
    """
    cfginfos = globalvar.CFG_INFOS
    PNs = cfginfos['PNINFO']
    try:
        global pninfo, pn
        pninfos = GetPNinfos(PNs)
        if pninfos == ERROR_RT:
            return ERROR_RT
        strw = '请输入%s产品市场型号(P/N):' % board_name
        while True:
            strw = recode(strw)
            PN = raw_input(strw)
            if PN not in pninfos.keys():
                strw = 'PN条码输入错误[%s不在globalvar变量定义]！请重新输入%s产品市场型号(P/N):' % (PN, board_name)
                continue
            else:
                pninfo = pninfos[PN]
                pn = pninfo['PN']
                break

        #返回获取到的信息
        return pn, pninfo

    except KeyboardInterrupt:
        strw = recode('程序执行到[app.GetPN]被手动终止')
        print strw
        return OTHER_ERROR, OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[app.GetPN]异常退出!异常信息为%s' % err)
        print strw
        return ERROR_RT, ERROR_RT


##获取板卡型号
#
#获取板卡型号，在CMD模式下使用
def GetBN(pn_info):
    """
    get bn
    """
    cfginfos = globalvar.CFG_INFOS
    BNs = cfginfos['BNINFO']

    try:
        bn = ''
        bn_from_var = pn_info['BN']
        bninfos = GetBNinfos(BNs)    # 此处函数需要添加
        strw = '请输入板卡型号(B/N):'
        while True:
            strw = recode(strw)
            BN = raw_input(strw)
            if BN not in bninfos.keys():
                strw = 'BN条码输入错误[%s不在globalvar变量定义]！请重新输入板卡型号(B/N):' % BN
                continue
            else:
                bn = bninfos[BN]['BN']
                if bn != bn_from_var:
                    strw = 'BN条码输入错误[{%s}与PN带出来的{%s}不匹配]!请重新输入板卡型号(B/N):' % (bn, bn_from_var)
                    continue
                break

        #返回获取到的信息
        return bn

    except KeyboardInterrupt:
        strw = recode('程序执行到[app.GetBN]被手动终止')
        print strw
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[app.GetBN]异常退出!异常信息为%s' % err)
        print strw
        return ERROR_RT


## 获取MAC地址
#
# 获取MAC地址，在CMD模式下使用
def GetMAC(boardid='0'):
    """
    get mac
    """
    if boardid == '0':
        boardname = 'CPU'
    elif boardid == '1':
        boardname = '左路扣板'
    else:
        boardname = '右路扣板'
    try:
        mac = ''
        cfginfos = globalvar.CFG_INFOS
        mac6bit = cfginfos['INPUTINFO']['mac6bit']
        strw = recode('请输入%s MAC地址:' % boardname)
        while True:
            mac = raw_input(strw)
            if len(mac) != 12:
                strw = recode('MAC地址输入错误[长度不为12位]!请重新输入%sMAC地址:' % boardname)
                continue
            elif mac[:6] != mac6bit:
                strw = recode('MAC地址输入错误[不是以000906开头]!请重新输入%sMAC地址:' % boardname)
                continue
            else:
                break
            #返回获取到的MAC
        mac = MACFormat(mac)
        return mac

    except KeyboardInterrupt:
        strw = recode('程序执行到[app.GetMAC]被手动终止')
        print strw
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[app.GetMAC]异常退出!异常信息为%s' % err)
        print strw
        return ERROR_RT


def MACFormat(MAC):
    """convert the MAC to the format XX:XX:XX:XX:XX:XX"""
    return ':'.join(MAC[i:i + 2] for i in range(0, 11, 2))


##选择脚本启动模式
#
#选择脚本启动模式
def select_burnin_mode():
    """
    参数传递：       MODE:    由globalvar中传入
    工作方式：       当工作模式在CMD模式下的时候，要求作业员手动选择启动模式，在AUTOTOOL模式下面会自动开始顺序拷机。
    返回参数：       返回选择的工作模式
    """
    try:
        MODE = globalvar.MODE
        if MODE == 'AUTOTOOL':
            cfginfos = globalvar.CFG_INFOS
            workmode = cfginfos['BURNIN_CONTROL']['work_mode']
            rt = workmode.upper()
        else:
            strw = recode('请选择启动模式[A-顺序拷机; B-单步拷机; C-停止拷机; D-跳出程序]：')
            while True:
                rt = raw_input(strw)
                rt = rt.upper()
                if rt != 'A' and rt != 'B' and rt != 'C' and rt != 'D':
                    strw = recode('输入错误，请重新选择启动模式[A-顺序拷机; B-单步拷机; C-停止拷机; D-跳出程序]：')
                    continue
                else:
                    break
            if rt == 'B':
                strw = recode('请选择拷机项目[1-数据拷机;  2-Reboot重启拷机;  3-PowerCycle重启拷机;  4-烧录出货镜像]:')
                while True:
                    rt = raw_input(strw)
                    rt = rt.upper()
                    if rt != '1' and rt != '2' and rt != '3' and rt != '4':
                        strw = recode('输入错误,请重新选择拷机项目[1-数据拷机;  2-Reboot重启拷机;  3-PowerCycle重启拷机;  4-烧录出货镜像]:')
                        continue
                    else:
                        break
        return rt
    except KeyboardInterrupt:
        strw = '程序执行到[app.select_burnin_mode]被手动终止'
        print recode(strw)
        return OTHER_ERROR
#    except Exception, err:
#        strw = '程序执行到[app.select_burnin_mode]异常退出!异常信息为%s' % err
#        print recode(strw)
#        return ERROR_RT


## 获取板卡相关信息
#
# 获取板卡相关信息，在autotool模式下使用
def autotoolGetInputInfos(ID, snlist):
    """
    autotool mode get serial number infos
    """
    try:
        rtinfos = {}
        while True:
            value = ''
            for n in range(0, len(snlist)):
                value = value + snlist[n].strip() + '*'
            value = value.strip('*').strip()
            rt = tcplib.SendInputMsg(ID, value)
            if rt == ERROR_RT:
                return ERROR_RT, ERROR_RT
            rtlist = rt.split('*')
            getinfos = {}
            for key in rtlist:
                key = key.strip()
                kvalue = key[key.find('[') + 1:key.find(']')].strip()
                key = key[0:key.find('[')].strip()
                if key.find('/') is not False:
                    a = key.count('/')
                    key = key.replace('/', '', a)
                key = key.lower()
                getinfos[key] = kvalue

            cfginfos = globalvar.CFG_INFOS
            flag = True
            for key in getinfos.keys():
                if key == 'ps':
                    PS3bit = cfginfos['INPUTINFO']['ps3bit']
                    PS3bits = PS3bit.split(',')
                    PS = getinfos['ps']
                    if len(PS) != 11:
                        strw = 'PS条码输入错误[长度不为11位]！'
                        print recode(strw)
                        work.writerunlog(recode(strw))
                        flag = False
                        continue
                    elif PS[3].isalpha() is False:
                        strw = 'PS条码输入错误[第4码不为字母]！'
                        print recode(strw)
                        work.writerunlog(recode(strw))
                        flag = False
                        continue
                    elif PS[:3] not in PS3bits:
                        strw = 'PS条码输入错误[前3码不在%s中]！' % PS3bit
                        print recode(strw)
                        work.writerunlog(recode(strw))
                        flag = False
                        continue
                    else:
                        rtinfos['ps'] = getinfos['ps']
                        snlist.remove('P/S')
                elif key == 'bs':
                    BS3bit = cfginfos['INPUTINFO']['bs3bit']
                    BS3bits = BS3bit.split(',')
                    BS = getinfos['bs']
                    if len(BS) != 11:
                        strw = 'BS条码输入错误[长度不为11位]！'
                        print recode(strw)
                        work.writerunlog(recode(strw))
                        flag = False
                        continue
                    elif BS[:3] not in BS3bits:
                        strw = 'BS条码输入错误[前3码不在%s中]！' % BS3bit
                        print recode(strw)
                        work.writerunlog(recode(strw))
                        flag = False
                        continue
                    elif BS[3].isalpha() is False:
                        strw = 'BS条码输入错误[第4码不为字母]！'
                        print recode(strw)
                        work.writerunlog(recode(strw))
                        flag = False
                        continue
                    else:
                        rtinfos['bs'] = getinfos['bs']
                        snlist.remove('B/S')
                elif key == 'pn':
                    print key
                    PNs = cfginfos['PNINFO']
                    pninfos = GetPNinfos(PNs)
                    if pninfos == ERROR_RT:
                        return ERROR_RT, ERROR_RT
                    PN = getinfos['pn']
                    if PN not in pninfos.keys():
                        strw = 'PN条码输入错误[%s]不在config中定义]！' % PN
                        print strw
                        work.writerunlog(recode(strw))
                        flag = False
                        continue
                    else:
                        pninfo = pninfos[PN]
                        rtinfos['pn'] = pninfo["PN"]
                        snlist.remove('P/N')
                        globalvar.pninfo = pninfo
                elif key == 'bn':
                    BNs = cfginfos['BNINFO']
                    bninfos = GetBNinfos(BNs)
                    if bninfos == ERROR_RT:
                        return ERROR_RT, ERROR_RT
                    BN = getinfos['bn']
                    if BN not in bninfos.keys():
                        strw = 'BN条码输入错误[%s]不在config中定义]！' % BN
                        print strw
                        work.writerunlog(recode(strw))
                        flag = False
                        continue
                    else:
                        rtinfos['bn'] = bninfos[BN]["BN"]
                        snlist.remove('B/N')
                elif key == 'mac':
                    print key
                    MAC = getinfos['mac']
                    mac6bit = cfginfos['INPUTINFO']['mac6bit']
                    print mac6bit
                    if MAC[:6] != mac6bit:
                        strw = recode('MAC地址输入错误[不是以%s开头]!' % mac6bit)
                        print strw
                        work.writerunlog(strw)
                        flag = False
                        continue
                    elif len(MAC) != 12:
                        strw = recode('MAC地址输入错误[长度不为12位]!')
                        print strw
                        work.writerunlog(strw)
                        flag = False
                        continue
                    else:
                        MAC = MACFormat(MAC)
                        rtinfos['mac'] = MAC
                        snlist.remove('MAC')

            if len(snlist) != 0:
                flag = False
            if flag is False:
                continue
            else:
                if 'bn' in rtinfos.keys():
                    print recode('检查PN和BN一致性')
                    if rtinfos['bn'] != pninfo['BN']:
                        strw = recode('由PN带出的[%s]与实际输入的[%s]不符合，请检查' % (pninfo['BN'], rtinfos['bn']))
                        print strw
                        work.writerunlog(strw)
                        return ERROR_RT, ERROR_RT
                    else:
                        return rtinfos, pninfo
                else:
                    return rtinfos, pninfo
                    #return rtinfos

    except KeyboardInterrupt:
        strw = recode('程序执行到[app.autotoolGetInputInfos]被手动终止')
        print strw
        return OTHER_ERROR
#    except Exception, err:
#        strw = recode('程序执行到[app.autotoolGetInputInfos]异常退出!异常信息为%s' % err)
#        print strw
#        return ERROR_RT


#获取产品信息
#
#获取产品FRU相关信息
def get_fru_info():
    """
    参数传递：       childInfos:    内含与设备连接的相关信息
    工作方式：       当工作模式在CMD模式下的时候，要求作业员手动选择启动模式，在AUTOTOOL模式下面会自动开始顺序拷机。
    返回参数：       返回选择的工作模式
    """
    tn = globalvar.TN
    f_name = sys._getframe().f_code.co_name
    getinfos = globalvar.getinfos
    flag = 'PASS'


    strw = recode('正在获取产品序列号和市场型号...')
    print strw
    work.writerunlog(strw)

    try:
        time.sleep(2)
        tn.write(ENTER)
        tn.write(ENTER)
        tn.write(ENTER)
        tn.write(ENTER)
        (index,match,data) = tn.expect(['Switch'],timeout=500)
        if index == -1:
            strw = recode('板卡登陆linux失败')
            print strw
            work.writerunlog(strw)
            return ERROR_RT

        pattern = 'Password'
        p = re.compile(re.escape(pattern), re.DOTALL | re.IGNORECASE)
        tn.write('enable' + ENTER)
        (index,match,data) = tn.expect([p], timeout=5)
        if index == -1:
            strw = recode('板卡登陆linux失败')
            print strw
            work.writerunlog(strw)
            return ERROR_RT

        pattern = 'Switch#'
        p = re.compile(re.escape(pattern), re.DOTALL | re.IGNORECASE)
        tn.write('admin' + ENTER)
        (index,match,data) = tn.expect([p], timeout=5)
        if index == -1:
            strw = recode('板卡登陆linux失败')
            print strw
            work.writerunlog(strw)
            return ERROR_RT

        strw = recode('板卡已经进入linux kernel')
        print strw
        work.writerunlog(strw)

        # cmd_list = ['configure terminal',
        #     'no errdisable detect reason fdb-loop',
        #     'no errdisable detect reason link-flap',
        #     'no errdisable fdb-loop ',
        #     'exit',
        # ]
        # for cmd in cmd_list:
        #     for i in cmd:
        #         tn.write(i)
        #         time.sleep(0.05)
        #     tn.write(ENTER)


        connection.Gotoshell()
        cmd = 'onie-syseeprom '
        for i in cmd:
            tn.write(i)
            time.sleep(0.05)
        rtstr = re.escape(cmd) + '.+' + 'root'
        rtstr = re.compile(rtstr, re.IGNORECASE | re.DOTALL)
        tn.write(ENTER)
        (index, match, data) = tn.expect([rtstr], timeout=30)
        if index == -1:
            strw = recode('获取FRU信息失败')
            print strw
            work.writerunlog(strw)
            return ERROR_RT
        else:
            pattern = 'Product Name         0x21  \d\d \S+'
            pattern = re.compile(pattern, re.IGNORECASE | re.DOTALL)
            p = re.search(pattern,data)
            if p:
                pn = p.group()[30:]
                globalvar.boardtype = pn
                print pn
            else:
                strw = recode('板卡类型抓取失败')
                print strw 
                work.writerunlog(strw)
                flag = 'FAIL'

        strw = recode('%s ...... %s'%(f_name, flag))
        print strw 
        work.writerunlog(strw)

        if flag == "PASS":
            return SUCCESS_RT
        else:
            return ERROR_RT

    except KeyboardInterrupt:
        strw = '程序执行到[app.get_fru_info]被手动终止'
        print recode(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = '程序执行到[app.get_fru_info]异常退出!异常信息为%s' % err
        print recode(strw)
        return ERROR_RT

def set_iophy():
    try:
        loginfos = globalvar.loginfos
        tn = globalvar.TN
        dirValue = globalvar.LOG_DIR
        f_name = sys._getframe().f_code.co_name
        logfile = os.path.join(dirValue, '%s.log') % f_name
        data_log = ''
        flag = 'PASS'

        cmdlist = [
            'lcsh',
            'write gephy 1 22 0',
            'write gephy 1 9 0x1e00',
            'write gephy 1 0 0x9140',
            'write gephy 1 22 6',
            'write gephy 1 18 0x8',
            'write gephy 1 22 0',
            'write gephy 2 22 0',
            'write gephy 2 9 0x1e00',
            'write gephy 2 0 0x9140',
            'write gephy 2 22 6',
            'write gephy 2 18 0x8',
            'write gephy 2 22 0',
            'write gephy 3 22 0',
            'write gephy 3 9 0x1e00',
            'write gephy 3 22 6',
            'write gephy 3 18 0x8',
            'write gephy 3 22 0'
                   ]

        for cmd in cmdlist:
            for c in cmd:
                time.sleep(0.1)
                tn.write(c)
            tn.write(ENTER)
            (index,match,data) = tn.expect(['lcsh#'],timeout=10)
            data_log = data_log + data
            work.writecmdlog(data)
            work.writelogtofile(logfile, data)
            if index == -1:
                strw = recode('前3个电口（IO上3个口）phy层打环失败')
                print strw
                work.writerunlog(strw)
                flag = 'FAIL'

        loginfos[f_name] = data_log
        globalvar.loginfos = loginfos

        tn.write('exit' + ENTER)
        tn.write('exit' + ENTER)
        tn.expect(['Switch#'],timeout=10)
        tn.write('exit' + ENTER)

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



def get_board_type_burnin():
    '''get board type'''
    # check the board_type

    board_type = globalvar.BOARD_TYPE
    if board_type not in ['48X6Q','48X4Q4T']:
        strw = recode('获取设备型号不在【48X6Q,48X4Q4T】中')
        print strw
        work.writerunlog(strw)
        return ERROR_RT            

    # set the value in the globalvar based on the board_type
    if board_type == '48X6Q':
        optical_module_num = 54
        for idx in xrange(55, 58+1):
            del globalvar.port_mapping[idx]
    elif board_type == '48X4Q4T':
        optical_module_num = 52
        for idx in xrange(53, 54+1):
            del globalvar.port_mapping[idx]

    port_mapping = globalvar.port_mapping
    port_list = [port_mapping[key] for key in port_mapping.keys()]
    new_port_list = [(port_list[::2][index],port_list[1::2][index]) for index in range(0, len(port_list)/2 )]

    print port_list
    globalvar.port_list, globalvar.new_port_list = port_list, new_port_list

    return SUCCESS_RT


def get_board_type():
    """
    参数传递：       pn: 传递进来的pn
    工作方式：       根据传递进来的pn在globalvar中查找对应的硬件类型,并会将该结果更新到globalvar中去
    返回参数：       返回执行的结果， SUCCESS_RT or ERROR_RT
    """
    try:
        pninfo = globalvar.pninfo
        getinfos = globalvar.getinfos
        part_number = pninfo['PN']
        strw = recode('正在获取并更新板卡类型....')
        print strw
        work.writerunlog(strw)

        pn_new = part_number[:]
        hwinfos = {}
        cfginfos = globalvar.CFG_INFOS
        hws = cfginfos['HWINFO']
        for key in hws.keys():
            tmp = hws[key]
            tmplist = tmp.split('*+*')  # PNs中的分隔符为[*+*]
            if len(tmplist) != 2:   # 元素列表个数，如果不是这个，说明PNs中格式与默认的不一致，则需要修改本函数
                strw = recode('HWs中所包含的信息数量不对，请检查！')
                print strw
                return ERROR_RT
            else:
                keywd = tmplist[0].strip()
                hwinfos[keywd] = {}
                t = tmplist[1].strip()
                hwinfos[keywd]['board_type'] = t
                #t = tmplist[2].strip()
                #hwinfos[keywd]['port_number'] = t
        print hwinfos.keys()
        print pn_new
        globalvar.PS = getinfos['ps']
        #此为判断此种型号的板卡，自动化是否支持（有可能是由于没有在HWINFO中配置导致出现此种打印）
        if pn_new not in hwinfos.keys():
            strw = recode('该版本不支持此类型【%s】板卡' % part_number)
            print strw
            work.writerunlog(strw)
            return ERROR_RT
        else:
            hwinfo = hwinfos[pn_new]
            globalvar.BOARD_TYPE = hwinfo['board_type']
            #globalvar.port_number = hwinfo['port_number']

        #strw = recode('板卡类型为%s'%hwinfo['board_type'])
        #print strw 
        #work.writerunlog(strw)


        return SUCCESS_RT
    except KeyboardInterrupt:
        strw = recode('程序执行到[app.get_board_type]被手动终止')
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
#    except Exception, err:
#        strw = recode('程序执行到[app.get_board_type]异常退出!异常信息为%s' % err)
#        print strw
#        work.writerunlog(strw)
#        return ERROR_RT




# Enter IPMI and check ATCA led
def Enter_IPMI_check_led():
    """check the IPMI version"""
    try:
        tn = globalvar.TN
        flag = True
        logpath = os.path.join(globalvar.LOG_DIR, 'IPMICheck.log')
        cfginfos = globalvar.CFG_INFOS
        version = cfginfos['IPMI_ver']['ipmi_ver']
        pattern = 'App\s*code\s*version\s*:\s*\d\.\d+.+interrupt'
        p = re.compile(pattern, re.DOTALL | re.IGNORECASE)
        (index, match, data) = tn.expect([p], timeout=60)
        work.writelogtofile(logfile, data)
        if index == -1:
            strw = recode('没有侦测到IPMI版本信息')
            print strw
            work.writerunlog(strw)
            return ERROR_RT

        ipmi_version = data

        cmd = '\003'
        pattern = 'IPMI>'
        p = re.compile(pattern, re.DOTALL | re.IGNORECASE)
        tn.write(cmd + ENTER)
        (index, match, data) = tn.expect([p], timeout=10)
        if index == -1:
            strw = recode('进入IPMI>界面失败')
            print strw
            work.writerunlog(strw)
            return ERROR_RT

        #检查IPMI版本信息
        if ipmi_version.find(version) != -1:
            strw = recode('IPMI版本正确')
            print strw
            work.writerunlog(strw)
        else:
            strw = recode('IPMI版本错误')
            print strw
            work.writerunlog(strw)
            flag = False

        #检查OOS、Status、H/S指示灯
        p = ['IPMI>', 'DEBUG>']
        cmd = 'lb -a 0x70 -m w 0x55'
        wait_time = 10
        tn.write(cmd)
        time.sleep(1)
        tn.write(ENTER)
        (index, match, data) = tn.expect(p, timeout=wait_time)
        work.writecmdlog(data)
        if index == -1:
            strw = recode('命令%s执行失败' % cmd)
            print strw
            work.writerunlog(strw)
            return ERROR_RT

        mode = globalvar.MODE
        id = globalvar.ID
        if mode == 'AUTOTOOL':
            while True:
                rt = tcplib.SendExChangeMsg(id, '请确认面板的LED灯是否正常?')
                work.writerunlog(recode('请确认面板的LED灯是否正常?'))
                if rt.upper() != 'YES':
                    strw = recode('面板LED灯不正常')
                    print strw
                    work.writerunlog(strw)
                    flag = False
                    break
                else:
                    strw = recode('面板LED灯正常')
                    print strw
                    work.writerunlog(strw)
                    break
        if mode == 'CMD':
            strw = recode('请确认面板的LED灯是否正常[Y]:')
            while True:
                rt = raw_input(strw)
                rt = rt.upper()
                if rt == 'Y':
                    strw = recode('面板LED灯正常')
                    print strw
                    work.writerunlog(strw)
                    break
                elif rt == 'N':
                    strw = recode('面板LED灯不正常')
                    print strw
                    work.writerunlog(strw)
                    flag = False
                    break
                else:
                    strw = recode('输入有误,请确认面板的LED灯是否正常[Y-正常 ； N-不正常]:')
                    continue

        if flag is False:
            return ERROR_RT
        else:
            return SUCCESS_RT

    except KeyboardInterrupt:
        strw = recode('程序执行中断!')
        print strw
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序异常退出!app.Enter_IPMI_check_led,异常信息%s' % err)
        print strw
        return ERROR_RT


# check ipmi app version
def check_ipmi_version():
    try:
        #检查IPMI版本信息
        cfginfos = globalvar.CFG_INFOS
        ipmi_version = cfginfos['IPMI_ver']['ipmi_ver']
        dirValue = globalvar.LOG_DIR
        bootFile = os.path.join(dirValue, 'IPMICheck.log')
        f = open(bootFile, 'r')
        p = re.compile(r'App\s*code\s*version:\s*')
        rt = f.readline()
        app_ver = None
        while rt:
            m = p.search(rt)
            if m:
                rt = rt.strip()
                tmp = re.findall(r'App\s*code\s*version:\s*(\d+\.\d+)', rt)
                if len(tmp) == 0:
                    strw = recode('获取IPMI版本失败，请检查')
                    print strw
                    work.writerunlog(strw)
                    return ERROR_RT
                else:
                    app_ver = tmp[0]
                strw = recode('成功读取IPMI版本...')
                work.writerunlog(strw)
            if app_ver is not None:
                break
            rt = f.readline()
        f.close()

        flag = True
        #Compare Uboot version info
        if app_ver == ipmi_version:
            strw = recode('IPMI版本正确.')
            print strw
            work.writerunlog(strw)
        else:
            strw = recode('IPMI版本不正确，当前版本：%s,正确版本应为：%s' % (app_ver, ipmi_version))
            work.writerunlog(strw)
            print strw
            flag = False

        if not flag:
            return ERROR_RT
        return SUCCESS_RT

    except KeyboardInterrupt:
        strw = recode('程序执行到[app.check_ipmi_version]被手动终止')
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[app.check_ipmi_version]异常退出!异常信息为%s' % err)
        print strw
        work.writerunlog(strw)
        return ERROR_RT


##设置板卡Uboot环境变量
#
#设置板卡环境变量
def SetUbootEnv():
    """
    参数传递：       tn:         与板卡交互的通道
                    ps:        由main函数传递过来的产品序列号
                    mark:        是否做其他事情的标记
    工作方式：       根据config来设置环境变量，如果需要做diag mem则继续做diag mem的动作
    返回参数：       返回执行的结果， SUCCESS_RT or ERROR_RT
    """
    strw = recode('正在配置Uboot启动脚本...')
    print strw
    work.writerunlog(strw)

    try:
        #获取已经抓取好的config文件信息
        cfginfos = globalvar.CFG_INFOS
        getinfos = globalvar.getinfos
        tn = globalvar.TN

        #根据ps来计算出将要设置的IP地址
        ps = filter(str.isdigit, getinfos['ps'])
        tmp = int(ps) % 255
        _ps = str(tmp)
        ps_wk = _ps[5:7]   # 获取ps中代表周别的两位
        ps_icr = _ps[-4:]  # 获取后4位流水号
        a = int(ps_icr) / 255  # 将后4位流水号除以255
        a3 = int(a) % 3     # 把后4位除以255的商对3取余
        b = int(ps_icr) % 255   # 对后4位流水号进行255取余
        if b == 0 or b == 1:
            b = '86'

        ipend = str(b)

        uboot = 'Bootrom:>'
        uboot = re.compile(uboot, re.IGNORECASE | re.DOTALL)
        plist = [uboot]

        section = 'EnvCmd'
        savecmd = 'saveenv'

        num = int(cfginfos[section]['number'])
        for n in range(1, num + 1):
            kw = 'envcmd' + '%s' % n
            envcmd = cfginfos[section][kw]
            if envcmd.find('ipaddr') != -1:
                envcmd += ipend
            cmd = 'setenv' + ' ' + envcmd
            rt = command.CmdExpect(tn, cmd, plist)
            if rt == -1 or rt == ERROR_RT:
                strw = recode('执行命令[%s]超时' % cmd)
                print strw
                work.writerunlog(strw)
                tn.close()
                return ERROR_RT
            else:
                strw = recode('已设置%s' % cmd)
                work.writerunlog(strw)
                time.sleep(0.5)

        #保存设置好的环境变量
        rt = command.CmdExpect(tn, savecmd, plist)
        if rt == -1 or rt == ERROR_RT:
            strw = recode('执行命令[%s]超时' % savecmd)
            print strw
            work.writerunlog(strw)
            tn.close()
            return ERROR_RT

        return SUCCESS_RT
    except KeyboardInterrupt:
        strw = recode('程序执行到[app.SetUbootEnv]被手动终止')
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
#    except Exception, err:
#        strw = recode('程序执行到[app.SetUbootEnv]异常退出!异常信息为%s' % err)
#        print strw
#        work.writerunlog(strw)
#        return ERROR_RT

def get_firmware_data():
    '''get firmware data'''
    tn = globalvar.TN
    cmd = 'cd /tmp/test/'
    tn.write(cmd + ENTER)
    tn.expect(['#'], timeout=5)
    tn.read_very_eager()
    time.sleep(2)

    cmd = 'bash show_all_version.sh'
    prompt = '#'
    pattern = re.escape(cmd)+'.+'+prompt
    prompt_match = re.compile(pattern,re.IGNORECASE | re.DOTALL)
    wait_time = 20
    data =  command.CmdGet(tn,cmd,[prompt_match],int(wait_time))

    return data

def parse_firmware_data(data):
    '''parse the firmware data and return a dict

    Args:
        data: all the version showed data
            example
                /tmp/test/prd # bash show_all_version.sh
                current boot version is 2.1
                current ipmc version is 1.8
                current fpga version is 0.6
                Uboot_Octeon_cpf6100_Prog_V1.1.9-p8
                vmlinux.64_Octeon2_Prog_V1.1.13-p8

    Returns:
        dict: contains the version
            example
            {
            'boot':'2.1',
            'ipmc':'1.8',
            'fpga':'0.6',
            'uboot':'Uboot_Octeon_cpf6100_Prog_V1.1.9-p8',
            'kernel':'vmlinux.64_Octeon2_Prog_V1.1.13-p8'
            }
        error_rt: return error if re search fail
    '''
    firmware_dict = {}
    firmware_list = ['boot', 'ipmc', 'fpga']
    for firmware in firmware_list:
        pattern = firmware + '.+?(\d\.\d+)'
        p = re.search(pattern,data)
        if p == None:
            return ERROR_RT
        else:
            firmware_dict[firmware] = p.group(1)
    print firmware_dict
    return firmware_dict

def compare_firmware_version(firmware_dict, spec_firmware_dict):
    '''compare firmware version'''
    firmware_list = ['boot', 'ipmc', 'fpga']
    for firmware in firmware_list:
        if firmware_dict[firmware] != spec_firmware_dict[firmware]:
            strw = recode('版本%s比较失败' %firmware)
            print strw
            work.writerunlog(strw)
            return ERROR_RT
    return SUCCESS_RT

def check_firmware():
    '''check the firmware version, such as ipmc_boot,ipmc,fpga.etc '''
    cfginfos = globalvar.CFG_INFOS
    spec_firmware_dict = cfginfos['Firmware_version']
    data = get_firmware_data()
    if data == ERROR_RT:return ERROR_RT
    firmware_dict = parse_firmware_data(data)
    return compare_firmware_version(firmware_dict, spec_firmware_dict)


def ParseRegData(data):
    pattern = '\s+(0x\S\S\S\S)'
    p = re.search(pattern, data)
    if p == None:
        return ERROR_RT
    return p.group(1)

def GetCpldVersion():
    '''get cpld version'''
    f_name = sys._getframe().f_code.co_name
    logpath = os.path.join(globalvar.LOG_DIR, '%s.log'%f_name)
    tn = globalvar.TN

    ver_all = 'cpld_'
    reg_list = ['0x50', '0x51', '0x52', '0x53', '0x54', '0x55']
    for reg in reg_list:
        cmd = 'i2cget -y 0 0x4 %s w' %reg
        prompt = '0x\S\S\S\S'
        pattern = re.escape(cmd)+'.+'+prompt
        prompt_match = re.compile(pattern, re.IGNORECASE | re.DOTALL)
        wait_time = 10
        data = command.CmdGet(tn, cmd, [prompt_match],int(wait_time))
        print data
        if data == ERROR_RT: return ERROR_RT
            
        value = ParseRegData(data)
        print value
        if value == ERROR_RT : return  ERROR_RT

        if reg != '0x55':
            ver_all = ver_all  + value[2:] + '_'
        else:
            ver_all = ver_all  + value[2:]

    return ver_all


def check_version():
    try:
        loginfos = globalvar.loginfos
        tn = globalvar.TN
        f_name = sys._getframe().f_code.co_name
        dirValue = globalvar.LOG_DIR
        logfile = os.path.join(dirValue, '%s.log')%f_name

        cfginfos = globalvar.CFG_INFOS
        version = cfginfos['Firmware_version']['cpld_version']
        sdram = cfginfos['Firmware_version']['sdram']
        flash = cfginfos['Firmware_version']['flash']
        pmon = cfginfos['Firmware_version']['pmon']
        data_log = ''
        flag = 'PASS'
        bootFile = os.path.join(dirValue, 'ConsoleCatchlog_tn1.log')
        f = open(bootFile, 'r')
        rt = f.readlines()
        rt = str(rt)
        print rt

        cmd = 'show version'
        pattern = cmd + '.+' + 'System serial number'
        pattern = re.compile(pattern, re.IGNORECASE | re.DOTALL)
        wait_time = 10
        tn.read_very_eager()
        data = command.CmdGet(tn, cmd, [pattern],int(wait_time))
        print data

        pattern = 'SDRAM size             : %sM'%sdram
        pattern = re.compile(pattern, re.IGNORECASE | re.DOTALL)
        p = re.search(pattern,data)
        if p:
            strw = recode('SDRAM check success')
            print strw
            work.writerunlog(strw)
        else:
            strw = recode('SDRAM check fail')
            print strw
            work.writerunlog(strw)
            flag = 'FAIL'

        pattern = 'Flash size             : %sM'%flash
        pattern = re.compile(pattern, re.IGNORECASE | re.DOTALL)
        p = re.search(pattern,data)
        if p:
            strw = recode('FLASH check success')
            print strw
            work.writerunlog(strw)
        else:
            strw = recode('FLASH check fail')
            print strw
            work.writerunlog(strw)
            flag = 'FAIL'

        cmd_list = [
            'configure terminal',
            'no errdisable detect reason fdb-loop',
            'no errdisable detect reason link-flap',
            'no errdisable fdb-loop ',
            'exit'
        ]        
        for cmd in cmd_list:
            for i in cmd:
                tn.write(i)
                time.sleep(0.05)
            tn.write(ENTER)

        connection.Gotoshell()
        cmd = 'cd test'
        tn.write(cmd+ENTER)
        (index, match, data) = tn.expect(['root'],10)
        if "can't" in data:
            strw = recode('cd test error')
            print strw
            work.writerunlog(strw)
            flag = 'FAIL'
        if globalvar.BOARD_TYPE == 'YES':
            cmd = 'unzip -q VX3100_diag_tools_*.zip'
            tn.write(cmd+ENTER)
            tn.expect(['root'],60)
        cmd = '. env.sh '
        tn.write(cmd+ENTER)
        tn.expect(['root'],10)
        cmd = 'sh load_all.sh'
        tn.write(cmd+ENTER)
        tn.expect(['root'],10)
        cmd = 'cd test'
        tn.write(cmd+ENTER)
        (index, match, data) = tn.expect(['root'],10)
        if "can't" in data:
            strw = recode('cd test error')
            print strw
            work.writerunlog(strw)
            flag = 'FAIL'

        cmd = 'sh show_cyclone_version.sh'
        pattern = version
        pattern = re.compile(pattern, re.IGNORECASE | re.DOTALL)
        wait_time = 10
        data = command.CmdGet(tn, cmd, [pattern],int(wait_time))
        print data

        pattern = version
        pattern = re.compile(pattern, re.IGNORECASE | re.DOTALL)
        p = re.search(pattern,data)
        if p:
            strw = recode('CPLD check success')
            print strw
            work.writerunlog(strw)
        else:
            strw = recode('CPLD check fail')
            print strw
            work.writerunlog(strw)
            flag = 'FAIL'

        pattern = str('PMON Version: V%s')%pmon
        p = re.compile(pattern, re.IGNORECASE | re.DOTALL)
        m = p.search(rt)
        if m:
            strw = recode('PMON版本正确.')
            print strw
            work.writerunlog(strw)
        else:
            strw = recode('PMON版本错误.')
            print strw
            work.writerunlog(strw)
            flag = 'FAIL'

        data_log = data_log + rt

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


def CheckUbootVersion():
    f_name = sys._getframe().f_code.co_name
    logpath = os.path.join(globalvar.LOG_DIR, '%s.log'%f_name)

    cfginfos = globalvar.CFG_INFOS
    tn = globalvar.TN

    cmd = 'ver'
    prompt = 'Bootrom:>'
    pattern = re.escape(cmd)+'.+'+prompt
    prompt_match = re.compile(pattern, re.IGNORECASE | re.DOTALL)
    wait_time = 10
    data = command.CmdGet(tn, cmd, [prompt_match],int(wait_time))
    if data == ERROR_RT: return ERROR_RT    

    uboot_version = cfginfos['Firmware_version']['uboot_version']
    pattern = re.escape(uboot_version)
    if re.search(pattern, data):
        strw = recode('Uboot版本比对成功')
        work.writerunlog(strw)
        print strw 
    else:
        strw = recode('Uboot版本比对失败')
        work.writerunlog(strw)
        print strw         
        return ERROR_RT

        #if UpdateUboot() == ERROR_RT:
        #    return ERROR_RT

        #if connection.ResetToUboot() == ERROR_RT:
        #    return ERROR_RT

    return SUCCESS_RT


## 写FRU
#
#  将相关FRU写入板卡并检查写入的信息是否正确
def updateFRU(tn, updatefru, item, board=''):
    """
    参数传递：       tn:           与板卡连接的通道
                    item:         表示要更新的是载板、扣板或者后IO的FRU信息;默认为载板
                    updatefru：   需要更新的FRU信息
    工作方式：       首先将fruinfos中的信息更新到板卡中fru_tmp这个文件中
    返回参数：       返回成功或者失败的结果
    """
    try:
        f_name = sys._getframe().f_code.co_name
        logpath = os.path.join(globalvar.LOG_DIR, '%s.log'%f_name)
        eptInfos = ''
        #首先通过item来辨别所需更新部件的fru信息
        if item == 'KOUBAN':
            # 需要更新的是扣板的fru信息
            cfginfos = globalvar.CFG_INFOS
            fruinfos = cfginfos['CPU_FRU']
            frucmd = globalvar.FRU_KOUBAN_CMD
            echotofile = 'Y'
        elif item == 'ZAIBAN':
            # 需要更新的是载板的fru信息
            cfginfos = globalvar.CFG_INFOS
            fruinfos = cfginfos['FRU']
            frucmd = globalvar.FRU_ZAIBAN_CMD
            echotofile = 'Y'
        elif item == 'RTM':
            #需要更新的是后IO的fru信息
            cfginfos = globalvar.CFG_INFOS
            fruinfos = cfginfos['RTM_FRU']
            frucmd = globalvar.FRU_RTM_CMD
            echotofile = 'Y'
            pass
        else:
            #上述都不是的出错处理
            strw = recode('未知的FRU类型，请检查！[目前支持：KOUBAN：扣板   ZAIBAN：载板   RTM：后IO]')
            print strw
            return ERROR_RT

        #将fruinfos和updatefru更新进板卡中，以fru_tmp的文件方式存在
        if echotofile == 'Y':
            FRU_FILE = globalvar.FRU_FILE
            cmd = 'rm -rf' + ' ' + FRU_FILE
            tn.write(cmd + ENTER)
            time.sleep(0.5)

        fruinfonum = len(fruinfos.keys())  # 获取命令的条目数
        for n in range(1, fruinfonum + 1):
            fruinfo = 'fru' + str(n)
            fru = fruinfos[fruinfo]
            if fru[:fru.find('=')] in updatefru.keys():
                fru = updatefru[fru[:fru.find('=')]]
            if fru.find(';') != -1:
                a = fru.count(';')
                fru = fru.replace(';', '\;', a)
            if fru.find('(') != -1:
                a = fru.count('(')
                fru = fru.replace('(', '\(', a)
            if fru.find(')') != -1:
                a = fru.count(')')
                fru = fru.replace(')', '\)', a)
            if fru.find('.') != -1:
                a = fru.count('.')
                fru = fru.replace('.', '\.', a)
            if fru.find('$') != -1:
                a = fru.count('$')
                fru = fru.replace('$', '\$', a)
            if fru.find('+') != -1:
                a = fru.count('+')
                fru = fru.replace('+', '\+', a)
            if echotofile == 'Y':
                time.sleep(0.5)
                cmd = 'echo %s >> %s' % (fru, FRU_FILE)
                #rtstr = FRU_FILE + '\s*\/.+\s*#'
                rtstr = '#'
                rtstr = re.compile(rtstr, re.IGNORECASE | re.DOTALL)
                tn.write(cmd + ENTER)
                (index, match, data) = tn.expect([rtstr], timeout=60)
                work.writecmdlog(data)
                work.writelogtofile(logfile, data)
                if index == -1:
                    strw = recode('更新FRU相关域失败！')
                    print strw
                    work.writerunlog(strw)
                    return ERROR_RT

            if fru.find(' ') != -1:
                a = fru.count(' ')
                fru = fru.replace(' ', '\s*', a)

            eptInfos = eptInfos + fru + '\s*'

        eptInfos = re.compile(eptInfos, re.IGNORECASE | re.DOTALL)
        # 更新fru并重新读取，并判别fru是否写入正确
        if item == 'RTM':
            import runconfig
            product = runconfig.product
            if product.upper() == 'FM1000':
                fcmd = frucmd + ' -f %s -n AM%s-fru' %(FRU_FILE, board)
                rcmd = frucmd + ' -r -n AM%s-fru' % board
            elif product.upper() == 'PM6800':
                fcmd = frucmd + ' -f %s' % FRU_FILE
                rcmd = frucmd + ' -r'
            else:
                fcmd = frucmd + ' -f %s -n 10' % FRU_FILE
                rcmd = frucmd + ' -r -n 10'
        else:
            fcmd = frucmd + ' write %s' % FRU_FILE
            rcmd = frucmd + ' read'
        tn.write(fcmd + ENTER)
        time.sleep(3)
        tn.write(rcmd + ENTER)
        (index, match, data) = tn.expect([eptInfos], timeout=60)
        work.writecmdlog(data)
        work.writelogtofile(logfile, data)
        if index == -1:
            tn.write(fcmd + ENTER)
            time.sleep(3)
            tn.write(rcmd + ENTER)
            (index, match, data) = tn.expect([eptInfos], timeout=60)
            work.writecmdlog(data)
            if index == -1:
                strw = recode('更新FRU信息失败！')
                print strw
                work.writerunlog(strw)
                return ERROR_RT
            else:
                strw = recode('已更新FRU信息.')
                print recode('************************')
                print strw
                print recode('*********************************************************************')
                work.writerunlog(strw)
        else:
            strw = recode('已更新FRU信息.')
            print '*********************************************************************'
            print strw
            print '*********************************************************************'
            work.writerunlog(strw)

        cmd = 'rm -rf' + ' ' + FRU_FILE
        tn.write(cmd + ENTER)
        tn.write(ENTER)

        # 配置完成，返回结果SUCCESS_RT
        return SUCCESS_RT

    except KeyboardInterrupt:
        strw = recode('程序执行到[app.updateFRU]被手动终止')
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
#    except Exception, err:
#        strw = recode('程序执行到[app.updateFRU]异常退出!异常信息为%s' % err)
#        print strw
#        work.writerunlog(strw)
#        return ERROR_RT

#构造IP地址
def CreateIP(mark='1'):
    try:
        test_environment = globalvar.test_environment

        # 根据规则，生成IP地址
        # IP地址前两位由config给出，第3位由ps中代表周的那两位，第4位由ps后5位去除字母对255取余生成(要检查是否为0)
        cfginfos = globalvar.CFG_INFOS
        ip2bit = cfginfos['IPINFO']['ip_2_byte']
        gatewayip = cfginfos['IPINFO']['gateway_ip']    # 获取config中的gateway_ip
        mask = cfginfos['IPINFO']['netmask']       # 获取config中的netmask
        _ps = cfginfos['SETTING']['ps']     # 获取前面输入的ps

        ps_wk = _ps[5:7]   # 获取ps中代表周别的两位
        ps_icr = _ps[-4:]  # 获取后4位流水号
        a = int(ps_icr) / 255  # 将后4位流水号除以255
        a3 = int(a) % 3     # 把后4位除以255的商对3取余
        b = int(ps_icr) % 255   # 对后4位流水号进行255取余
        if b == 0 or b == 1:
            b = '86'
        ip3 = int(str(a3) + ps_wk)
        if mark != 1:
            ip3 += 1
            if ip3 > 255:
                ip3 %= 255
        ip3 = str(ip3)  # 将之与周别相连接
        if test_environment == 'rd':
            ip3 = '0'

        ip4 = str(b)    # 转化格式

        if mask == '255.255.255.0':
            ip3 = '0'
            ip4 = '123'

        ip = '.'.join([ip2bit, ip3, ip4])     # 连接成IP地址

        globalvar.IP = ip

        # 配置完成，返回结果SUCCESS_RT
        return SUCCESS_RT

    except KeyboardInterrupt:
        strw = recode('程序执行到[app.SetIP]被手动终止')
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
#    except Exception, err:
#        strw = recode('程序执行到[app.SetIP]异常退出!异常信息为%s' % err)
#        print strw
#        work.writerunlog(strw)
#        return ERROR_RT


## 设置IP地址
#
# 为板卡设置IP地址
def SetIP(mark='1', eth='eth0'):
    """
    参数传递：       tn: 与板卡连接的通道
                    cfginfos: 从globalvar中获得，包含有外部环境IP前2码，比如10.1; gatewayIP, 比如:10.1.0.1
                    getInfos: 可以从中获取到板卡的ps，以便设置的IP地址是唯一的
                    loaddriver: 是否要加载网卡驱动的标志，默认为需要加载网卡驱动
                    eth: 所配置的网络设备名称，默认为eth0
                    workdir: 从globalvar传递过来的设置IP时候所需的环境，比如linux shell或者sysadmin
                    ethdrivercmd: 从globalvar传递过来的加载网卡驱动的命令，如果不需要加载驱动
    工作方式：       通过下面的规则生成IP，并对板卡进行设置，同时检查设置结果是否OK
    返回参数：       返回成功或者失败的结果

    """
    try:
        tn = globalvar.TN

        # 根据规则，生成IP地址
        # IP地址前两位由config给出，第3位由ps中代表周的那两位，第4位由ps后5位去除字母对255取余生成(要检查是否为0)
        cfginfos = globalvar.CFG_INFOS
        getinfos = globalvar.getinfos
        ip2bit = cfginfos['IPINFO']['ip_2_byte']
        gatewayip = cfginfos['IPINFO']['gateway_ip']    # 获取config中的gateway_ip
        networkip = cfginfos['IPINFO']['network_ip']
        _ps = getinfos['ps']     # 获取前面输入的ps

        ps_wk = _ps[5:7]   # 获取ps中代表周别的两位
        ps_icr = _ps[-4:]  # 获取后4位流水号
        a = int(ps_icr) / 255  # 将后4位流水号除以255
        a3 = int(a) % 3     # 把后4位除以255的商对3取余
        b = int(ps_icr) % 255   # 对后4位流水号进行255取余
        if b == 0 or b == 1:
            b = '86'
        ip3 = int(str(a3) + ps_wk)
        if mark != 1:
            ip3 += 1
            if ip3 > 255:
                ip3 %= 255
        ip3 = str(ip3)  # 将之与周别相连接
        if networkip == '255.255.255.0':
            ip3 = '33'
        ip4 = str(b)    # 转化格式
        ip = '.'.join([ip2bit, ip3, ip4])     # 连接成IP地址
        globalvar.IP = ip


        return SUCCESS_RT

    except KeyboardInterrupt:
        strw = recode('程序执行到[app.SetIP]被手动终止')
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
#    except Exception, err:
#        strw = recode('程序执行到[app.SetIP]异常退出!异常信息为%s' % err)
#        print strw
#        work.writerunlog(strw)
#        return ERROR_RT


## 下载相关文件
#
# 下载文件
def download_files():
    """
    参数传递：       tn:         与板卡交互的通道
                    bootmode:         板卡的启动形态
    工作方式：       将config中的命令传递给板卡，包括可能的切换路径，下载文件，解压压缩包等等
    返回参数：       返回执行的结果， SUCCESS_RT or ERROR_RT
    """
    try:
        loginfos = globalvar.loginfos
        tn = globalvar.TN
        f_name = sys._getframe().f_code.co_name
        dirValue = globalvar.LOG_DIR
        logfile = os.path.join(dirValue, '%s.log')%f_name
        flag = 'PASS'
        data_log = ''
        cfginfos = globalvar.CFG_INFOS
        file = cfginfos['DL_FILE_VER']['software_file']
        tftp_dir = cfginfos['DL_FILE_VER']['tftp_dir']

        # connection.ListenAndGotoLinux()

        if globalvar.BOARD_TYPE == 'YES':
            PingEth()
            connection.Gotoshell()
    
            strw = recode('正在烧录软件...')
            print strw
            work.writerunlog(strw)
    
            cmd_list = [
            'rm /mnt/flash/startup-config.conf',
            'rm -rf test',
            'mkdir test',
            'exit'
            ]
            for cmd in cmd_list:
                tn.write(cmd+ENTER)
    
            cmd = 'copy mgmt-if %s%s flash:/test/%s'%(tftp_dir,file,file)
            for i in cmd:
                tn.write(i)
                time.sleep(0.05)
            tn.write(ENTER)
            tn.expect(['Switch'],60)

            loginfos[f_name] = data_log
            globalvar.loginfos = loginfos
    
        strw = '请拔掉网线并插上管理网口的光模块'
        rt = wait_op_input(strw)
        if rt == ERROR_RT:
            return ERROR_RT

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


def ExecuteCommand(tn,cmd_dict):
    '''Execute Command and check its return value'''
    cmd      = cmd_dict['cmd']
    prompt   = cmd_dict['prompt']
    waittime = int(cmd_dict['waittime'])
    strmatch = cmd_dict['strmatch']

    pattern = re.escape(cmd[0:4])+'.+'+prompt
    prompt_match = re.compile(pattern,re.IGNORECASE | re.DOTALL)
    rt = command.CmdGet(tn,cmd,[prompt_match],int(waittime))
    if rt == ERROR_RT:return ERROR_RT
    p = re.compile(strmatch,re.IGNORECASE | re.DOTALL)
    if p.search(rt) == None:
        strw = recode('command %s 执行失败!' %cmd)
        print strw
        work.writerunlog(strw)
        return ERROR_RT

    return SUCCESS_RT

# diag sd data
def diag_sd_data():
    '''sd diag '''
    cfginfos = globalvar.CFG_INFOS
    f_name = sys._getframe().f_code.co_name
    globalvar.LOG_PATH = os.path.join(globalvar.LOG_DIR, '%s.log'%f_name)

    tn = globalvar.TN
    strw = recode('开始%s Test...'%f_name)
    print strw
    work.writerunlog(strw)

    cmd_dict = {}
    cmd_dict['cmd'] = 'sh /tmp/test/diag_sdx.sh /dev/sda1'
    cmd_dict['prompt'] = '#'
    cmd_dict['waittime'] = 60
    cmd_dict['strmatch'] = 'ok'
    if ExecuteCommand(tn,cmd_dict) == ERROR_RT:
        strw = recode('%s Test FAIL'%f_name)
        print strw
        work.writerunlog(strw)
        return ERROR_RT
    del globalvar.LOG_PATH
    strw = recode('%s Test PASS'%f_name)
    print strw
    work.writerunlog(strw)

    return SUCCESS_RT


# diag usb data
def diag_usb_data():
    '''usb diag '''
    cfginfos = globalvar.CFG_INFOS
    f_name = sys._getframe().f_code.co_name
    globalvar.LOG_PATH = os.path.join(globalvar.LOG_DIR, '%s.log'%f_name)

    tn = globalvar.TN
    strw = recode('开始%s Test...'%f_name)
    print strw
    work.writerunlog(strw)

    cmd_dict = {}
    cmd_dict['cmd'] = 'sh /tmp/test/diag_sdx.sh /dev/sdb1'
    cmd_dict['prompt'] = '#'
    cmd_dict['waittime'] = 60
    cmd_dict['strmatch'] = 'ok'
    if ExecuteCommand(tn,cmd_dict) == ERROR_RT:
        strw = recode('%s Test FAIL'%f_name)
        print strw
        work.writerunlog(strw)
        return ERROR_RT
    del globalvar.LOG_PATH
    strw = recode('%s Test PASS'%f_name)
    print strw
    work.writerunlog(strw)

    return SUCCESS_RT


## 测试网口
#
# 测试网口
def PingEth():
    """
    参数传递：       tn:          与板卡连接的通道
                    cfginfos:    从glovalvar中获得
                    MODE:        启动脚本的方式，CMD or Autotool；默认为CMD方式启动
                    ID：         当启动脚本方式为autotool的时候，用来与autotool交互的通道
    工作方式：       对给定的serverIP，ping 5000个长度为1500的包，要求不能有一个丢包
    返回参数：       返回成功或者失败的结果
    """
    try:
        f_name = sys._getframe().f_code.co_name
        dirValue = globalvar.LOG_DIR
        loginfos = globalvar.loginfos
        logfile = os.path.join(dirValue, '%s.log')%f_name
        tn = globalvar.TN
        cfginfos = globalvar.CFG_INFOS    # 从globalvar中获得CFG_INFOS
        gatewayip = cfginfos['IPINFO']['gateway_ip']
        pingip = cfginfos['IPINFO']['ping_ip']  # 从config中获取到所要ping的server ip     
        network_ip = cfginfos['IPINFO']['network_ip']
        data_log = ''
        flag = 'PASS'

        if globalvar.BOARD_TYPE == 'YES':
            SetIP()
            # strw = '请插上网线并拔下管理网口对应的光模块'
            # rt = wait_op_input(strw)
            # if rt == ERROR_RT:
            #     return ERROR_RT
            if network_ip == '255.255.255.0':
                networkip = 24
            elif network_ip == '255.255.0.0':
                networkip = 16
            else:
                strw = recode('config中网关设置出错')
                print strw
                work.writerunlog(strw)
                return ERROR_RT
    
            connection.Gotoshell()
    
            cmd = 'ip netns exec mgmt mgmt_phy eth0 22 0'
            tn.write(cmd+ENTER)
            tn.write('exit'+ENTER)
    
            cmd0 = 'configure terminal'
            cmd1 = 'management ip address %s/%s'%(globalvar.IP,networkip)
            cmd2 = 'management route gateway %s'%gatewayip
            cmd3 = 'exit'
            cmd_list = [cmd0,cmd1,cmd2,cmd3]
            for cmd in cmd_list:
                p = 'Switch'
                for i in cmd:
                    tn.write(i)
                    time.sleep(0.1)
                pattern = re.compile(p, re.IGNORECASE | re.DOTALL)
                tn.read_very_eager()
                time.sleep(0.5)
                tn.write(ENTER)
                time.sleep(0.5)
                (index, match, data) = tn.expect([pattern], timeout=6)
                data_log = data_log + data
                work.writecmdlog(data)
                work.writelogtofile(logfile, data)
                if index == -1:
                    strw = recode('命令%s执行失败'%cmd)
                    print strw
                    work.writerunlog(strw)
                    flag = 'FAIL'
    
            strw = recode('正在测试网口...')
            print strw
            work.writerunlog(strw)
    
            time.sleep(5)
            cmd = 'ping mgmt-if %s' % pingip
            #tn.write(cmd + ENTER)
            #tn.expect(['#'], timeout=10)
            for i in cmd:
                tn.write(i)
                time.sleep(0.1)
    
            pattern = '5\s*packets\s*transmitted,\s*5\s*received,\s*\d+%\s*packet\s*loss,\s*time\s*\d+ms(\s*.+)#'
            pattern = re.compile(pattern, re.DOTALL | re.IGNORECASE)
            tn.write(ENTER)
            (index, match, data) = tn.expect([pattern], timeout=60)
            data_log = data_log + data
            work.writelogtofile(logfile,data)
            if index == -1:
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


def DiagEth():
    '''Diag eth0 eth1 interface'''
    tn = globalvar.TN
    if PingServer() == ERROR_RT:
        return ERROR_RT

    cmd = 'ifconfig eth0 down'
    tn.write(cmd + ENTER)
    tn.expect(['#'],timeout=5)

    if SetIPEth1() == ERROR_RT:
        return ERROR_RT

    if PingServer(eth='eth1') == ERROR_RT:
        return ERROR_RT

    return SUCCESS_RT

def load_FPGA():
    """
    参数传递：       tn:         与板卡交互的通道;
    工作方式：       跑一下软件包给的软件包
    返回参数：       如果没err则返回SUCCESS_RT，有err则返回ERROR_RT
    """
    try:
        sub_board = globalvar.SUB_BOARD

        tn = globalvar.TN
        strw = recode('开始加载FPGA...')
        print strw
        work.writerunlog(strw)

        dirValue = globalvar.LOG_DIR
        bootFile = os.path.join(dirValue, 'load_driver.log')

        cmd = 'cd /usr/local/components/'
        tn.write(cmd + ENTER)
        time.sleep(0.5)


        #下载FPGA
        #开始下载FPGA文件
        tn.write('cd /usr/local/components/diag_tools' + ENTER)
        time.sleep(0.5)

        #开始加载FPGA
        cmd = '/usr/local/components/diag_tools/diag'
        rtStr = 'DIAG>>'
        rtStr = re.compile(rtStr, re.DOTALL | re.IGNORECASE)
        tn.read_very_eager()
        tn.write(cmd + ENTER)
        time.sleep(0.5)
        (index, match, data) = tn.expect([rtStr], timeout=60)
        work.writecmdlog(data)
        work.writelogtofile(bootFile, data)
        if index == -1:
            strw = recode('进入diag目录失败')
            print strw
            work.writerunlog(strw)
            return ERROR_RT

        import runconfig
        product = runconfig.product
        if product == 'EP7000':
            sub_board = globalvar.SUB_BOARD
            if sub_board != 'FM1000':
                strw = recode('没有FPGA子卡，将会跳过FPGA测试')
                print strw
                work.writerunlog(strw)
                return SUCCESS_RT
            else:
                ddr_co = ['0', '1']
        else:
            cfginfos = globalvar.CFG_INFOS
            subboard_count = cfginfos['CONTROL']['subboard_count']
            if subboard_count == '2':
                ddr_co = ['0', '1']
            else:
                ddr_co = ['0']
        for dim in ddr_co:
            cmd = 'fpga download %s fpga.bin' % dim
            rtStr = cmd + r'\s*.+success.+\s*DIAG>>'
            rtStr = re.compile(rtStr, re.DOTALL | re.IGNORECASE)
            failrtStr = cmd + r'\s*.+failed.+\s*DIAG>>'
            failrtStr = re.compile(failrtStr, re.DOTALL | re.IGNORECASE)
            tn.read_very_eager()
            tn.write(cmd + ENTER)
            time.sleep(0.5)
            (index, match, data) = tn.expect([failrtStr, rtStr], timeout=60)
            work.writecmdlog(data)
            work.writelogtofile(bootFile, data)
            if index == -1 or index == 0:
                strw = recode('加载FPGA失败')
                print strw
                work.writerunlog(strw)
                return ERROR_RT

        reset_cmds = ['slb write16 0xfa1 0x265',
                      'slb write16 0xfa1 0xe65']
        for cmd in reset_cmds:
            rtStr = cmd + r'\s*DIAG>>'
            rtStr = re.compile(rtStr, re.DOTALL | re.IGNORECASE)
            tn.read_very_eager()
            tn.write(cmd + ENTER)
            time.sleep(0.5)
            (index, match, data) = tn.expect([rtStr], timeout=60)
            work.writecmdlog(data)
            work.writelogtofile(bootFile, data)
            if index == -1:
                strw = recode('FPGA 初始化失败')
                print strw
                work.writerunlog(strw)
                return ERROR_RT

        ## tx enable
        cmd = 'slb write16 0xf48 0x0'
        rtStr = cmd + r'\s*DIAG>>'
        rtstr = re.compile(rtStr, re.DOTALL | re.IGNORECASE)
        tn.read_very_eager()
        time.sleep(0.5)
        tn.write(cmd + ENTER)
        (index, match, data) = tn.expect([rtstr], timeout=10)
        work.writecmdlog(data)
        if index == -1:
            strw = recode('sfp tx enable失败')
            print strw
            work.writerunlog(strw)
            return ERROR_RT

        time.sleep(5)

        #检查FM100上的PHY是否配置成功
        for dim in ddr_co:
            idx = str(int(dim) + 1)
            addr_list = ['0x0', '0x1', '0x2', '0x3']
            for addr in addr_list:
                cmd = 'mdio cyclone read_45 %s %s 0x1 0xca1a' %(idx, addr)
                rtStr = cmd + r'\s*.+0x128.+\s*DIAG>>'
                rtStr = re.compile(rtStr, re.DOTALL | re.IGNORECASE)
                tn.read_very_eager()
                tn.write(cmd + ENTER)
                time.sleep(0.5)
                (index, match, data) = tn.expect([rtStr], timeout=60)
                work.writecmdlog(data)
                work.writelogtofile(bootFile, data)
                if index == -1:
                    strw = recode('FM1000 10G PHY配置失败')
                    print strw
                    work.writerunlog(strw)
                    return ERROR_RT
                else:
                    strw = recode('FM1000 10G PHY配置成功')
                    print strw
                    work.writerunlog(strw)

        return SUCCESS_RT
    except KeyboardInterrupt:
        strw = recode('程序执行到[app.load_FPGA]被手动终止')
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[app.load_FPGA]异常退出!异常信息为%s' % err)
        print strw
        work.writerunlog(strw)
        return ERROR_RT

def ParseUbootInfo(Ubootinfo):
    #解析Uboot启动信息，从中获取各种规格信息并以字典的形式返回
    #cpu_type， frequency， dram_storage, nandflash_storage, norflash_storage
    board_parameter = {}
    pattern = 'OCTEON\s(.+)\s+pass.+Core clock:\s+(\d+)\s+MHz.+DRAM:\s+(\d+)\s+GiB.+NAND:\s+(\d+)\s+MiB.+Flash:\s+(\d+)\s+MiB'
    pattern = re.compile(pattern,re.IGNORECASE | re.DOTALL)
    p = re.search(pattern, Ubootinfo)
    if p == None:
        strw = recode('解析Uboot信息失败')
        print strw
        return ERROR_RT
    else:
        cpu_type, frequncy, dram_storage, nandflash_storage, norflash_storage = p.group(1), p.group(2), p.group(3), p.group(4), p.group(5)
        #print cpu_type, frequncy, dram_storage, nandflash_storage, norflash_storage

    board_parameter['cpu_type'] = cpu_type.replace('-', '')
    board_parameter['frequncy'] = frequncy
    board_parameter['dram_storage'] = dram_storage
    board_parameter['nandflash_storage'] = nandflash_storage
    board_parameter['norflash_storage'] = norflash_storage

    return board_parameter

def CheckBoardSpec():
    #从Uboot启动信息中获取板卡中各种规格参数
    #cpu_type,主频，内存容量，nandflash容量，norflash容量
    tn = globalvar.TN
    ip = globalvar.IP

    tn_ethernet = connection.TelnetBoard(ip)
    if tn_ethernet == ERROR_RT: return ERROR_RT

    for idx in [0, 1]:
        f_name = 'UbootInfo_CN6800%s' %(idx)
        logpath = os.path.join(globalvar.LOG_DIR, '%s.log'%f_name)
        cpu_idx = 'PM6800_' + str(idx)
        rt = ConsoleSwitch(cpu_idx)
        if rt == ERROR_RT: return ERROR_RT

        cmd = 'cd /usr/local'
        tn_ethernet.write(cmd + ENTER)
        (index, match, data) = tn_ethernet.expect(['#'], timeout=10)
        time.sleep(0.2)
        cmd = 'export OCTEON_REMOTE_PROTOCOL=PCI:%s' % str(idx)
        tn_ethernet.write(cmd + ENTER)
        (index, match, data) = tn_ethernet.expect(['#'], timeout=10)
        time.sleep(0.2)
        cmd = 'oct-remote-boot --board=cust_cn6880 uboot.bin --ddr_clock_hz 666666666 --envfile env.txt'
        tn_ethernet.write(cmd + ENTER)
        (index, match, data) = tn_ethernet.expect(['#'], timeout=10)
        time.sleep(0.2)

        pattern = 'Uboot_Octeon.+Boot.+mode'
        pattern = re.compile(pattern, re.IGNORECASE | re.DOTALL)
        (index, match, data) = tn.expect([pattern], timeout=30)
        if index == -1:
            strw = '获取CN6800-CPU%s启动信息失败' %str(idx)
            print strw
            work.writerunlog(strw)
            return ERROR_RT

        locals()['uboot%s'%str(idx)] = data
        work.writelogtofile(logfile, data)

    spec_cpu0_parameter = ParseUbootInfo(locals()['uboot0'])
    if spec_cpu0_parameter == ERROR_RT: return ERROR_RT
    print 'board info'
    print spec_cpu0_parameter

    board_parameter = {}
    pninfo = globalvar.pninfo
    capability = pninfo['_major_board_type']
    pattern = 'CPU:(.+)/(.+)G DRAM:DIMM/(\d+)GB/(\d+) FLASH:NOR/(\d+)MB/(\d+) FLASH:NAND/(\d+)GB/(\d+)'
    p = re.search(pattern, capability)
    if p == None:
        strw = recode('解析config中capability信息失败')
        print strw
        work.writerunlog(strw)
        return ERROR_RT
    else:
        cpu_type, frequncy, dimm_storage, dimm_num, flash_storge, flash_num, nand_storage, nand_num = p.group(1), p.group(2),p.group(3),p.group(4),p.group(5),p.group(6),p.group(7),p.group(8)

    board_parameter['cpu_type'] = cpu_type
    board_parameter['frequncy'] = str(int(float(frequncy) * 1000))
    board_parameter['dram_storage'] = int(dimm_storage) * int(dimm_num)
    board_parameter['nandflash_storage'] = int(nand_storage) * int(nand_num) * 1024
    board_parameter['norflash_storage'] =int(flash_storge) * int(flash_num)
    print 'config info'
    print board_parameter

    for keyx in board_parameter.keys():
        if str(board_parameter[keyx]) != str(spec_cpu0_parameter[keyx]):
            strw = recode('cpu0 %s检查失败' %keyx)
            print strw
            work.writerunlog(strw)
            return ERROR_RT
        else:
            strw = recode('cpu0 %s检查通过' %keyx)
            print strw
            work.writerunlog(strw)

    spec_cpu0_parameter = ParseUbootInfo(locals()['uboot1'])
    if spec_cpu0_parameter == ERROR_RT: return ERROR_RT
    print 'board info'
    print spec_cpu0_parameter

    board_parameter = {}
    pninfo = globalvar.pninfo2
    capability = pninfo['_major_board_type']
    pattern = 'CPU:(.+)/(.+)G DRAM:DIMM/(\d+)GB/(\d+) FLASH:NOR/(\d+)MB/(\d+) FLASH:NAND/(\d+)GB/(\d+)'
    p = re.search(pattern, capability)
    if p == None:
        strw = recode('解析config中capability信息失败')
        print strw
        work.writerunlog(strw)
        return ERROR_RT
    else:
        cpu_type, frequncy, dimm_storage, dimm_num, flash_storge, flash_num, nand_storage, nand_num = p.group(1), p.group(2), p.group(3), p.group(4), p.group(5), p.group(6), p.group(7), p.group(8)

    board_parameter['cpu_type'] = cpu_type
    board_parameter['frequncy'] = str(int(float(frequncy) * 1000))
    board_parameter['dram_storage'] = int(dimm_storage) * int(dimm_num)
    board_parameter['nandflash_storage'] = int(nand_storage) * int(nand_num) * 1024
    board_parameter['norflash_storage'] =int(flash_storge) * int(flash_num)
    print 'config info'
    print board_parameter

    for keyx in board_parameter.keys():
        if str(board_parameter[keyx]) != str(spec_cpu0_parameter[keyx]):
            strw = recode('cpu0 %s检查失败' %keyx)
            print strw
            work.writerunlog(strw)
            return ERROR_RT
        else:
            strw = recode('cpu0 %s检查通过' %keyx)
            print strw
            work.writerunlog(strw)

    rt = ConsoleSwitch()
    if rt == ERROR_RT: return ERROR_RT

    tn_ethernet.close()

    return SUCCESS_RT


def load_CPU():
    """
    参数传递：       tn:         与板卡交互的通道;
    工作方式：       跑一下软件包给的软件包
    返回参数：       如果没err则返回SUCCESS_RT，有err则返回ERROR_RT
    """
    try:
        sub_board = globalvar.SUB_BOARD
        if sub_board != 'PM6800':
            return SUCCESS_RT

        tn = globalvar.TN
        strw = recode('开始PCIe boot PM子卡...')
        print strw
        work.writerunlog(strw)

        tn.write('quit' + ENTER)
        tn.expect(['#'], timeout=5)

        #PCIe Boot两块PM6800子卡
        for idx in [0, 1]:
            cmd = 'cd /usr/local'
            tn.expect(['#'], timeout=5)
            tn.write(cmd + ENTER)
            cmd = 'export OCTEON_REMOTE_PROTOCOL=PCI:%s' %idx
            tn.write(cmd + ENTER)
            tn.expect(['#'], timeout=5)

            cmd = 'oct-remote-boot --board=cust_cn6880 uboot.bin --ddr_clock_hz 666666666 --envfile env.txt'
            tn.write(cmd + ENTER)
            tn.expect(['#'], timeout=10)
            time.sleep(10)

            cmd = 'oct-remote-load 0x20000000 kernel.bin'
            tn.write(cmd + ENTER)
            tn.expect(['#'], timeout=10)

            cmd = '''oct-remote-bootcmd "bootoctlinux 0x20000000"'''
            tn.write(cmd + ENTER)
            tn.expect(['#'], timeout=10)

        strw = recode('开始PCIe boot PM子卡...')
        print strw
        work.writerunlog(strw)
        tn.write(ENTER)
        tn.expect(['#'], timeout=10)
        time.sleep(5)

        cmd = '/usr/local/components/diag_tools/diag'
        rtStr = 'DIAG>>'
        rtStr = re.compile(rtStr, re.DOTALL | re.IGNORECASE)
        tn.read_very_eager()
        tn.write(cmd + ENTER)
        time.sleep(0.5)
        (index, match, data) = tn.expect([rtStr], timeout=60)
        work.writecmdlog(data)
        if index == -1:
            strw = recode('进入diag目录失败')
            print strw
            work.writerunlog(strw)
            return ERROR_RT

        return SUCCESS_RT
    except KeyboardInterrupt:
        strw = recode('程序执行到[app.load_CPU]被手动终止')
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[app.load_FPGA]异常退出!异常信息为%s' % err)
        print strw
        work.writerunlog(strw)
        return ERROR_RT


def check_base_link_status(port_list):
    tn = globalvar.TN
    flag = True
    f_name = sys._getframe().f_code.co_name
    logpath = os.path.join(globalvar.LOG_DIR, '%s.log'%f_name)

    cmd = 'cd /tmp/test/prd'
    pattern = '#'
    tn.write(cmd + ENTER)
    tn.expect([pattern],timeout=10)

    cmd = 'sh get_base_port_link_status.sh '
    pattern = '#'
    tn.write(cmd + ENTER)
    tn.expect([pattern],timeout=10)

    cmd = 'sh get_base_port_link_status.sh '
    pattern = '#'
    tn.write(cmd + ENTER)
    tn.expect([pattern],timeout=10)
    time.sleep(5)
    tn.read_very_eager()
    time.sleep(1)

    cmd = 'sh get_base_port_link_status.sh'
    rtstr = cmd + '\s*.+\s*#'
    rtstr = re.compile(rtstr, re.I | re.S)
    tn.write(cmd + ENTER)
    time.sleep(0.5)
    (index, match, data) = tn.expect([rtstr], timeout=10)
    work.writecmdlog(data)
    work.writelogtofile(logfile, data)
    if index == -1:
        strw = recode('获取端口link状态失败')
        print strw
        work.writerunlog(strw)
        return ERROR_RT
    else:
        for port in port_list:
            pattern = port + '\s+up'
            s = re.search(pattern, data)
            if s == None:
                strw = recode('端口%s link状态异常'%port)
                print strw
                work.writerunlog(strw)
                flag = False

    if flag:
        return SUCCESS_RT
    else:
        work.writerunlog(data)
        return ERROR_RT

def check_bcm_link_status():
    tn = globalvar.TN

    flag = True
    f_name = sys._getframe().f_code.co_name
    logpath = os.path.join(globalvar.LOG_DIR, '%s.log'%f_name)

    port_list = ['xe'+str(i) for i in range(0,13)]
    port_list.extend(['ce'+str(i) for i in range(0,19)])

    cmd = 'cd /tmp/test/prd'
    pattern = '#'
    tn.write(cmd + ENTER)
    tn.expect([pattern],timeout=10)

    cmd = 'sh config_port.sh '
    pattern = '#'
    tn.write(cmd + ENTER)
    tn.expect([pattern],timeout=10)

    cmd = 'sh get_fabric_port_link_status.sh '
    pattern = '#'
    tn.write(cmd + ENTER)
    tn.expect([pattern],timeout=10)

    cmd = 'sh get_fabric_port_link_status.sh '
    pattern = '#'
    tn.write(cmd + ENTER)
    tn.expect([pattern],timeout=10)
    time.sleep(5)
    tn.read_very_eager()
    time.sleep(1)
    cmd = 'sh get_fabric_port_link_status.sh'
    rtstr = cmd + '\s*.+\s*#'
    rtstr = re.compile(rtstr, re.I | re.S)
    tn.write(cmd + ENTER)
    time.sleep(0.5)
    (index, match, data) = tn.expect([rtstr], timeout=10)
    work.writecmdlog(data)
    work.writelogtofile(logfile, data)
    if index == -1:
        strw = recode('获取端口link状态失败')
        print strw
        work.writerunlog(strw)
        return ERROR_RT
    else:
        for port in port_list:
            pattern = port + '\s+up'
            s = re.search(pattern, data)
            if s == None:
                strw = recode('端口%s link状态异常'%port)
                print strw
                work.writerunlog(strw)
                flag = False

    if flag:
        return SUCCESS_RT
    else:
        work.writerunlog(data)
        return ERROR_RT


def start_bcm_send_pkt():
    f_name = sys._getframe().f_code.co_name
    logpath = os.path.join(globalvar.LOG_DIR, '%s.log'%f_name)

    tn = globalvar.TN

    cmd = 'sh start_fabric_port_packet.sh'
    tn.write(cmd + ENTER)
    tn.expect(['#'], timeout=5)
    (index, match, data) = tn.expect(['#'], timeout=10)
    work.writecmdlog(data)
    work.writelogtofile(logfile, data)

    return SUCCESS_RT


def check_bcm_err_counter(tn):
    flag = True

    cfginfos = globalvar.CFG_INFOS
    err_types = cfginfos['BCM_ERR']['err_types'].split(',')

    for err_type in err_types:
        cmd = 'show c ' + err_type.strip()
        eptstr = cmd + '\s*BCM(.*)>'
        eptstr = re.compile(eptstr, re.IGNORECASE | re.DOTALL)
        tn.read_very_eager()
        time.sleep(0.5)
        tn.write(cmd + ENTER)
        (index, match, data) = tn.expect([eptstr], timeout=5)
        work.writecmdlog(data)
        if index == -1:
            strw = recode('出现了%s类型的错包，请检查' % cmd.split()[-1].strip().upper())
            print strw
            work.writerunlog(strw)
            flag = False
    if flag:
        return SUCCESS_RT
    else:
        return ERROR_RT


def stop_check_bcm_counter():
    tn = globalvar.TN

    # stop bcm send pkt
    cmd = 'sh stop_fabric_port_packet.sh'
    tn.write(cmd + ENTER)
    tn.expect(['#'], timeout=5)

    time.sleep(5)

    cmd = 'sh get_fabric_port_counter.sh > bcm_fabric_counter.txt'
    tn.write(cmd + ENTER)
    tn.expect(['#'], timeout=10)

    cmd = 'bash check_bcm_tx_rx.sh'
    pattern = re.escape(cmd)+'.+'+'#'
    prompt_match = re.compile(pattern,re.IGNORECASE | re.DOTALL)
    waittime = 10
    data = command.CmdGet(tn, cmd, [prompt_match], waittime)
    if data == ERROR_RT: return ERROR_RT
    pattern = '([xc]e\d+).+FAIL'
    p_list = re.findall(pattern, data)
    if p_list:
        for p in p_list:
            strw = recode('端口%s收发包数量不等' %p)
            work.writerunlog(strw)
            print strw
        return ERROR_RT

    strw = recode('diag BCM Fabric PASS!')
    print strw
    work.writerunlog(strw)
    return SUCCESS_RT


def set_board_time():
    """
    参数传递：       child:         与板卡交互的通道
    工作方式：       给板卡设置时间
    返回参数：       返回执行的结果， SUCCESS_RT or ERROR_RT
    """
    dirValue = globalvar.LOG_DIR
    logFile = os.path.join(dirValue, 'setTime.log')

    try:
        child = globalvar.TN
        strw = recode('正在设置板卡时间...')
        print strw
        work.writerunlog(strw)
        # Get format time string by module os and set service time
        timestr = time.strftime('%Y%m%d%H%M', time.gmtime())
        cmd = 'shell date -s' + ' ' + timestr
        rtstr = cmd + '\s*.*' + 'DIAG>>'
        rtstr = re.compile(rtstr, re.DOTALL | re.IGNORECASE)
        child.write(cmd + ENTER)
        (i, match, data) = child.expect([rtstr], timeout=10)
        work.writecmdlog(data)
        work.writelogtofile(logFile, data)
        if i == -1:
            strw = recode('设置板卡时间失败，请检查！')
            print strw
            work.writerunlog(strw)
            return ERROR_RT
            #Write time in hardware
        cmd = 'shell hwclock -w'
        child.write(cmd + ENTER)
        (i, match, data) = child.expect(['DIAG>>'], timeout=10)
        work.writecmdlog(data)
        work.writelogtofile(logFile, data)
        if i == -1:
            strw = recode('设置板卡时间错误[%s]，请检查！' % cmd)
            print strw
            work.writerunlog(strw)
            return ERROR_RT
        elif i == 0:
            strw = recode('已设置板卡时间.')
            print strw
            work.writerunlog(strw)
        return SUCCESS_RT
    except KeyboardInterrupt:
        strw = recode('程序执行到[app.set_board_time]被手动终止')
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[app.set_board_time]异常退出!异常信息为%s' % err)
        print strw
        work.writerunlog(strw)
        return ERROR_RT


def check_power_margin():
    """
    @return ERROR_RT or SUCCESS_RT:
    """
    try:
        tn = globalvar.TN
        cfginfos = globalvar.CFG_INFOS
        voltage_lapian = cfginfos['SETTING']['voltage_lapian']
        strw = recode('开始检查电压拉偏功能是否正常')
        print strw
        work.writerunlog(strw)
        tn.write('cd /tmp/test' + ENTER)
        logdir = globalvar.LOG_DIR
        filename = 'power_margin.log'
        logfile = os.path.join(logdir, filename)

        min_test = 8
        flag = True

        pattern = r'^(k|z).+'

        #power_margin
        modes = ['H', 'L']
        for mode in modes:
            test_count = 0
            cmd = 'sh power_margin.sh -N >/dev/null 2>&1'
            tn.write(cmd + ENTER)
            time.sleep(2)
            tn.read_very_eager()
            cmd = 'sh power_margin.sh -%s >/dev/null 2>&1' % mode
            tn.write(cmd + ENTER)
            time.sleep(0.5)
            tn.read_very_eager()
            time.sleep(2)
            cmd = 'sh power_margin.sh -R'
            tn.write(cmd + ENTER)
            rtstr = 'End\s*of\s*Voltage\s*Read'
            rtstr = re.compile(rtstr, re.S | re.I)
            (index, match, data) = tn.expect([rtstr], timeout=10)
            work.writecmdlog(data)
            work.writelogtofile(logfile, data)
            if index == -1:
                strw = recode('获取拉偏后的电压失败')
                print strw
                work.writerunlog(strw)
                return ERROR_RT
            else:
                for line in data.split('\n'):
                    if re.match(pattern,line):
                        tmps = re.findall(r'(.+?)\s*:\s*\d+\.?\w*\s*\D?(\d+\.?\d*)%', line)
                        print tmps
                        if len(tmps) == 0:
                            strw = recode('获取的拉偏电压数据不正确[1]')
                            print strw
                            if globalvar.DEBUGMODE == 'SHOWALLFLAG':
                                print '-----------------------------------------'
                                print line
                                print '*****************************************'
                                print tmps
                                print '-----------------------------------------'
                            work.writerunlog(strw)
                            flag = False
                        else:
                            if len(tmps[0]) != 2:
                                strw = recode('获取的拉偏电压数据不正确[2]')
                                print strw
                                if globalvar.DEBUGMODE == 'SHOWALLFLAG':
                                    print '-----------------------------------------'
                                    print line
                                    print '*****************************************'
                                    print tmps
                                    print '-----------------------------------------'
                                work.writerunlog(strw)
                                flag = False
                            else:
                                test_count += 1
                                if abs(float(tmps[0][1])) > float(voltage_lapian):
                                    strw = recode('%s电压幅度超过百分之%s,当前为百分之%s' %(tmps[0][0],voltage_lapian,tmps[0][1]))
                                    print strw
                                    work.writerunlog(strw)
                                    flag = False
                                else:
                                    strw = recode('%s电压拉偏测试[%s]通过' %(tmps[0][0], mode))
                                    print strw
                                    work.writerunlog(strw)

            if test_count < min_test:
                strw = recode('有电压漏测试,请检查')
                print strw
                work.writerunlog(strw)
                flag = False

        if flag:
            strw = recode('电压拉偏测试通过!')
            work.writerunlog(strw)
            print strw
            return SUCCESS_RT
        else:
            strw = recode('电压拉偏测试失败!')
            work.writerunlog(strw)
            print strw
            return ERROR_RT

    except KeyboardInterrupt:
        strw = '程序执行到[app.check_power_margin]被手动终止'
        print recode(strw)
        return OTHER_ERROR
#    except Exception, err:
#        strw = '程序执行到[app.check_power_margin]异常退出!异常信息为%s' % err
#        print recode(strw)
#        return ERROR_RT


#与用户交互函数
def show_msg_to_op(infos):
    """提示用户动作的函数"""
    try:
        mode = globalvar.MODE
        id = globalvar.ID
        if mode == 'CMD':
            strw = infos
            while True:
                strw = recode(strw)
                rt = raw_input(strw)
                strw = infos + rt
                strw = recode(strw)
                work.writerunlog(strw)
                rt = rt.upper()
                if rt == 'Y':
                    break
                else:
                    strw = '输入错误！' + infos
                    continue
        else:
            while True:
                rt = tcplib.SendExChangeMsg(id, infos)
                strw = recode(infos + rt.upper())
                work.writerunlog(strw)
                if rt.upper() != 'YES':
                    continue
                else:
                    break
        return
    except KeyboardInterrupt:
        strw = recode('程序执行到[app.show_msg_to_op]被手动终止')
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[app.show_msg_to_op]异常退出!异常信息为%s' % err)
        print strw
        work.writerunlog(strw)
        return ERROR_RT


def wait_op_input(infos):
    """提示用户动作的函数"""
    try:
        mode = globalvar.MODE
        id = globalvar.ID
        if mode == 'CMD':
            strw = infos
            while True:
                strw = recode(strw)
                rt = raw_input(strw)
                strw = infos + rt
                strw = recode(strw)
                work.writerunlog(strw)
                rt = rt.upper()
                if rt == 'Y':
                    return SUCCESS_RT
                else:
                    return ERROR_RT
        else:
            while True:
                rt = tcplib.SendExChangeMsg(id, infos)
                strw = recode(infos + rt.upper())
                work.writerunlog(strw)
                if rt.upper() != 'YES':
                    return ERROR_RT
                else:
                    return SUCCESS_RT
        return
    except KeyboardInterrupt:
        strw = recode('程序执行到[app.wait_op_input]被手动终止')
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[app.wait_op_input]异常退出!异常信息为%s' % err)
        print strw
        work.writerunlog(strw)
        return ERROR_RT


def power_margin(power):
    """
    @param tn: telnet console
    @return ERROR_RT or SUCCESS_RT:
    """
    try:
        tn = globalvar.TN
        strw = recode('开始进行电压拉偏【%s】操作' % power)
        print strw
        work.writerunlog(strw)
        tn.write('quit' + ENTER)
        time.sleep(0.5)
        tn.write('cd /tmp' + ENTER)

        cmd = 'sh /tmp/power_margin.sh -N >/dev/null 2>&1'
        tn.write(cmd + ENTER)
        time.sleep(2)
        tn.read_very_eager()
        cmd = 'sh /tmp/power_margin.sh -%s >/dev/null 2>&1' % power
        tn.write(cmd + ENTER)
        time.sleep(0.5)
        tn.read_very_eager()
        time.sleep(2)

        return SUCCESS_RT
    except KeyboardInterrupt:
        strw = '程序执行到[app.power_margin]被手动终止'
        print recode(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = '程序执行到[app.power_margin]异常退出!异常信息为%s' % err
        print recode(strw)
        return ERROR_RT


## 将串口输出全部导入到指定文件 - 主程序
def RecordConsolePrint(csip, csport, port_counter=1):
    """
    @param csip: 串口服务器IP地址
    @param csport: 串口服务器的端口号
    @param port_counter: 串口的数量
    @return None:
    """
    tnlist = []
    path_list = []

    portstart = 0
    while port_counter != 0:
        port_counter -= 1
        subport = str(int(csport) + portstart)
        portstart += 1
        subtn = connection.TelnetServer(csip, subport)
        if subtn == ERROR_RT or subtn == OTHER_ERROR:
            return ERROR_RT
        else:
            tnlist.append(subtn)
            sublogname = 'ConsoleCatchlog_tn%s.log' % portstart
            logdir = globalvar.LOG_DIR
            sublogfile = os.path.join(logdir, sublogname)
            path_list.append(sublogfile)
    globalvar.Console_print_detect = 'start'
    ThreadRecordLog(tnlist, path_list)
    return


## 记录log
def LogRecord(tn, path):
    while True:
        pattern = '\n'
        (index, match, data) = tn.expect([pattern], timeout=5)
        work.writelogtofile(path, data)
        if globalvar.Console_print_detect == 'stop':
            tn.close()
            return


## 开始启动多线程记录多串口log
def ThreadRecordLog(tn_list, path_list):
    import threading

    threads = []
    num = len(tn_list)
    for i in range(0, int(num)):
        tn = tn_list[i]
        path = path_list[i]
        th = threading.Thread(target=LogRecord, args=(tn, path))
        threads.append(th)

    for th in threads:
        th.start()

def LedTest_2(q, ip, port):
    import telnetlib
    tn = telnetlib.Telnet(ip, port)

    # sys 红灯
    cmd = 'write epld 0 0x81 0xb0'
    tn.write(cmd + ENTER)
    tn.expect(['lcsh#'], timeout=5)
    # id led灭
    cmd = 'write epld 0 0x3 0x1'
    tn.write(cmd + ENTER)
    tn.expect(['lcsh#'], timeout=5)
    #数据黄灯
    cmd = 'write epld 0 0x24 0x1'
    tn.write(cmd + ENTER)
    tn.expect(['lcsh#'], timeout=5)
    time.sleep(2)
    cmd = 'write epld 0 0x25 0x0'
    tn.write(cmd + ENTER)
    tn.expect(['lcsh#'], timeout=5)



def LedTest_1(q, ip, port):
    import telnetlib
    tn = telnetlib.Telnet(ip, port)

    # sys led,亮绿灯
    cmd = 'write epld 0 0x81 0x70'
    tn.write(cmd + ENTER)
    tn.expect(['lcsh#'], timeout=5)
    # id led亮
    cmd = 'write epld 0 0x3 0x0'
    tn.write(cmd + ENTER)
    tn.expect(['lcsh#'], timeout=5)
    # 数据绿灯
    cmd = 'write epld 0 0x24 0x0'
    tn.write(cmd + ENTER)
    tn.expect(['lcsh#'], timeout=5)
    cmd = 'write epld 0 0x25 0x1'
    tn.write(cmd + ENTER)
    tn.expect(['lcsh#'], timeout=5)


## 提示查看所有LED信息
#
# 检查所有LED信息
def check_all_led():
    try:
        loginfos = globalvar.loginfos
        tn = globalvar.TN
        f_name = sys._getframe().f_code.co_name
        dirValue = globalvar.LOG_DIR
        logfile = os.path.join(dirValue, '%s.log')%f_name
        data_log = ''
        flag = 'PASS'

        strw = '电源灯和管理网口灯是否常亮'
        rt = wait_op_input(strw)
        if rt == ERROR_RT:
            strw = recode('LED灯第一次确认不正常')
            print strw
            work.writerunlog(strw)
            flag = 'FAIL'
            return ERROR_RT
        else:
            strw = recode('LED灯第一次确认正常')
            print strw
            work.writerunlog(strw)

        strw = '状态灯是否快速闪烁'
        rt = wait_op_input(strw)
        if rt == ERROR_RT:
            strw = recode('LED灯第二次确认不正常')
            print strw
            work.writerunlog(strw)
            flag = 'FAIL'
            return ERROR_RT
        else:
            strw = recode('LED灯第二次确认正常')
            print strw
            work.writerunlog(strw)

        time.sleep(1)

        strw = '切换灯是否慢速闪烁'
        rt = wait_op_input(strw)
        if rt == ERROR_RT:
            strw = recode('LED灯第三次确认不正常')
            print strw
            work.writerunlog(strw)
            flag = 'FAIL'
            return ERROR_RT
        else:
            strw = recode('LED灯第三次确认正常')
            print strw
            work.writerunlog(strw)

        time.sleep(1)

        strw = '数据灯是否常亮'
        rt = wait_op_input(strw)
        if rt == ERROR_RT:
            strw = recode('LED灯第四次确认不正常')
            print strw
            work.writerunlog(strw)
            flag = 'FAIL'
            return ERROR_RT
        else:
            strw = recode('LED灯第四次确认正常')
            print strw
            work.writerunlog(strw)

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


##check 网口灯
#
#ping ip来实现数据灯闪烁
def LEDCheckEther(tn):
    """
    输入:     tn    telnet通道
    返回值:   SUCCESS_RT   成功
              ERROR_RT     失败
    """
    try:
        mode = globalvar.MODE
        id = globalvar.ID
        cfginfos = globalvar.CFG_INFOS
        pingip = cfginfos['IPINFO']['ping_ip']

        #cmd = 'ping %s -f' % pingip
        #tn.write(cmd + ENTER)
        #work.writecmdlog(cmd)

        if mode == 'AUTOTOOL':
            while True:
                rt = tcplib.SendExChangeMsg(id, '请确认网口灯是否正常?')
                work.writerunlog(recode('请确认网口灯是否正常?'))
                if rt.upper() != 'YES':
                    return ERROR_RT
                else:
                    break

        if mode == 'CMD':
            strw = recode('请确认LED灯测试是否正常[Y/N]:')
            while True:
                rt = raw_input(strw)
                rt = rt.upper()
                if rt == 'Y':
                    break
                elif rt == 'N':
                    return ERROR_RT
                else:
                    strw = recode('输入错误,请确认LED灯测试是否正常 [Y/N]')

        tn.write('\003')
        tn.expect(['#'], timeout=5)

        return SUCCESS_RT

    except KeyboardInterrupt:
        strw = '程序执行到[app.LEDCheckEtherAB]被手动终止'
        print recode(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = '程序执行到[app.LEDCheckEther]异常退出!异常信息为%s' % err
        print recode(strw)
        return ERROR_RT


#检查Reset按键
def check_reset_button():
    try:
        loginfos = globalvar.loginfos
        tn = globalvar.TN
        f_name = sys._getframe().f_code.co_name
        dirValue = globalvar.LOG_DIR
        logfile = os.path.join(dirValue, '%s.log')%f_name
        data_log = ''
        flag = 'PASS'

        strw = '请按下Reset按键'
        rt = wait_op_input(strw)
        if rt == ERROR_RT:
            strw = recode('Reset按键测试失败')
            print strw
            work.writerunlog(strw)
            flag = 'FAIL'
            strw = recode('%s ...... %s'%(f_name, flag))
            print strw 
            work.writerunlog(strw)
            return ERROR_RT

        if connection.ListenAndGotoLinux() == ERROR_RT:
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

def check_power_status_data(data):
    '''check i2c data showed by the i2c diag script'''

    value=ParseRegData(data)
    if value != '0x03':
        return ERROR_RT

    return SUCCESS_RT

def check_dual_power():
    try:
        tn = globalvar.TN
        f_name = sys._getframe().f_code.co_name
        logpath = os.path.join(globalvar.LOG_DIR, '%s.log'%f_name)

        strw = recode('将要开始双电源测试...')
        print strw
        work.writerunlog(strw)

        if connection.GotoLcsh() == ERROR_RT:return ERROR_RT 

        cmd = 'read epld 0 0xb6 1'
        pattern = re.escape(cmd) + '.+' + '#'
        prompt_match = re.compile(pattern,re.IGNORECASE | re.DOTALL)
        waittime = 120
        data = command.CmdGet(tn, cmd, [prompt_match], waittime)
        work.writelogtofile(logfile, data)
        if data == ERROR_RT: return ERROR_RT

        if check_power_status_data(data) == ERROR_RT:
            connection.ExitLcsh()
            strw = recode('双电源检测失败')
            print strw
            work.writerunlog(strw)             
            return ERROR_RT

        connection.ExitLcsh()

        strw = recode('双电源检测通过')
        print strw
        work.writerunlog(strw)        

        return SUCCESS_RT
    except KeyboardInterrupt:
        strw = recode('程序执行到[special.check_reset_button]被手动终止')
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[special.check_reset_button]异常退出!异常信息为%s' % err)
        print strw
        work.writerunlog(strw)
        return ERROR_RT

# clear all connection
def close_all_connection():
    """
    close all connection
    """
    tn = globalvar.TN
    globalvar.Console_print_detect = 'stop'
    if tn is not None or tn != '':
        try:
            tn.write('exit'+ENTER)
            tn.close()
            tn = None
            globalvar.TN = tn
            time.sleep(5)
        except:
            pass
    return SUCCESS_RT


#linux下读取电源状态
def read_power_status_uboot(tn):
    """在uboot下面读取电源状态寄存器的值，如果读取失败，则返回ERROR_RT"""
    try:
        cmd1 = 'write64s  0x0001000000000020 0x4fc4'
        cmd2 = 'read64s 0x0001000000000022'
        tn.write(cmd1 + ENTER)
        time.sleep(0.5)
        tn.read_very_eager()
        tn.write(cmd2 + ENTER)
        epts = cmd2 + '\s*.+\s*U\s*Boot\s*#'
        epts = re.compile(epts, re.DOTALL | re.IGNORECASE)
        (index, match, data) = tn.expect([epts], timeout=30)
        work.writecmdlog(data)
        if index == -1:
            strw = recode('读取当前电源状态失败')
            print strw
            work.writerunlog(strw)
            return ERROR_RT
        temp = re.findall(r'0x8001000000000022:\s*(\w+)', data)
        if len(temp) != 0:
            current_value = temp[0]
            return current_value
        else:
            strw = recode('获取当前电源状态值失败')
            print strw
            work.writerunlog(strw)
            return ERROR_RT
    except KeyboardInterrupt:
        strw = recode('程序执行到[special.read_power_status_uboot]被手动终止')
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[special.read_power_status_uboot]异常退出!异常信息为%s' % err)
        print strw
        work.writerunlog(strw)
        return ERROR_RT


# linux下读取电源状态
def read_power_status_linux(tn):
    """在linux下面读取电源状态寄存器的值，如果读取失败，则返回ERROR_RT"""
    try:
        cmd = '/usr/local/bin/slb r 0 0xfc4'   # 在kernel下面获取当前电源状态值
        tn.read_very_eager()
        tn.write(cmd + ENTER)
        epts = 'slb.+\s*0xfc4.+\s*/.+#'
        epts = re.compile(epts, re.DOTALL | re.IGNORECASE)
        (index, match, data) = tn.expect([epts], timeout=30)
        work.writecmdlog(data)
        if index == -1:
            strw = recode('读取当前电源状态失败')
            print strw
            work.writerunlog(strw)
            return ERROR_RT
        temp = re.findall(r'0xfc4=(\w+)', data)
        if len(temp) != 0:
            current_value = temp[0]
            return current_value
        else:
            strw = recode('获取当前电源状态值失败')
            print strw
            work.writerunlog(strw)
            return ERROR_RT
    except KeyboardInterrupt:
        strw = recode('程序执行到[special.read_power_status_linux]被手动终止')
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[special.read_power_status_linux]异常退出!异常信息为%s' % err)
        print strw
        work.writerunlog(strw)
        return ERROR_RT


def diag_baser_init(tn):
    """ diag baser init """
    try:
        cmd = 'shell sh /tmp/config/config_baser.sh'
        rtstr = 'CONFIG\s*BASER\s*SUCCESS\s*.+DIAG>>'
        rtstr = re.compile(rtstr, re.I | re.S)
        tn.read_very_eager()
        time.sleep(0.5)
        tn.write(cmd + ENTER)
        (index, match, data) = tn.expect([rtstr], timeout=30)
        work.writecmdlog(data)
        if index == -1:
            strw = recode('执行命令[%s]失败' % cmd)
            print strw
            work.writerunlog(strw)
            return ERROR_RT

        return SUCCESS_RT
    except KeyboardInterrupt:
        strw = recode('程序执行到[app.diag_baser_init]被手动终止')
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[app.diag_baser_init]异常退出!异常信息为%s' % err)
        print strw
        work.writerunlog(strw)
        return ERROR_RT


def diag_baser_start(tn):
    """ diag baser start """
    try:
        flag = True
        dirValue = globalvar.LOG_DIR
        logfile = os.path.join(dirValue, 'diag_baser_start.log')

        cmds = ['fpga baser start 100 100 0 0 enable',
                'shell sleep 1',
                'fpga baser show 0']
        for cmd in cmds:
            rtstr = cmd + r'\s*.+\s*DIAG>>'
            rtstr = re.compile(rtstr, re.IGNORECASE | re.DOTALL)
            tn.read_very_eager()
            time.sleep(0.5)
            tn.write(cmd + ENTER)
            (index, match, data) = tn.expect([rtstr], timeout=10)
            work.writecmdlog(data)
            if index == -1:
                strw = recode('配置diag baser发包失败[%s]' % cmd)
                print strw
                work.writerunlog(strw)
                return ERROR_RT

        time.sleep(1)
        #检查发包是否正常并记录当前错包数目
        portrange = range(0, 12)
        for port in portrange:
            port = str(port)
            cmd = 'fpga baser show %s' % port
            tn.read_very_eager()
            time.sleep(0.5)
            tn.write(cmd + ENTER)
            rtstr = cmd + r'\s*.+\s*DIAG>>'
            rtstr = re.compile(rtstr, re.DOTALL | re.IGNORECASE)
            (index, match, data) = tn.expect([rtstr], timeout=10)
            work.writecmdlog(data)
            work.writelogtofile(logfile, data)
            if index == -1:
                strw = recode('端口%s - 获取baser错包计数器失败，请检查' % port)
                print strw
                work.writerunlog(strw)
                return ERROR_RT
            tmp = ''
            tmp = re.findall(r'P\d+\s*.+_errors\s*\|\s*(\d+)\s*pkts', data)
            if len(tmp) != 4:
                strw = recode('端口%s - 分析baser错包计数器失败，请检查' % port)
                print strw
                work.writerunlog(strw)
                flag = False
                return ERROR_RT
            else:
                globalvar.baser_start_errs[port] = tmp
            tmp = ''
            tmp = re.findall(r'P\d+\s*.+_packets\s*\|\s*(\d+)\s*pkts', data)
            if len(tmp) != 4:
                strw = recode('端口%s - 分析baser收发包计数器失败，请检查' % port)
                print strw
                work.writerunlog(strw)
                return ERROR_RT
            else:
                for i in tmp:
                    if int(i) == 0:
                        strw = recode('端口%s - 发包失败，请检查' % port)
                        print strw
                        work.writerunlog(strw)
                        flag = False
        if flag:
            return SUCCESS_RT
        else:
            return ERROR_RT
    except KeyboardInterrupt:
        strw = recode('程序执行到[app.diag_baser_start]被手动终止')
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[app.diag_baser_start]异常退出!异常信息为%s' % err)
        print strw
        work.writerunlog(strw)
        return ERROR_RT


def diag_baser_check(tn, stop=False):
    """
    check baser tx&rx counter and check err counter
    """
    try:
        #define command
        stop_cmd = 'fpga baser stop'

        #切换工作路径
        dirValue = globalvar.LOG_DIR
        logfile = os.path.join(dirValue, 'diag_baser_result.log')

        strw = recode('开始检查baser收发包结果...')
        print strw
        work.writerunlog(strw)

        if stop:
            strw = recode('准备开始停止baser发包...')
            print strw
            work.writerunlog(strw)

            tn.read_very_eager()
            time.sleep(0.5)
            rtstr = stop_cmd + r'\s*DIAG>>'
            rtstr = re.compile(rtstr, re.DOTALL | re.IGNORECASE)
            tn.write(stop_cmd + ENTER)
            (index, match, data) = tn.expect([rtstr], timeout=10)
            work.writecmdlog(data)
            if index == -1:
                strw = recode('停止baser收发包失败，请检查')
                print strw
                work.writerunlog(strw)
                return ERROR_RT

        flag = True  # diag result control flag
        #check err counter
        portrange = range(0, 12)
        for port in portrange:
            port = str(port)
            cmd = 'fpga baser show %s' % port
            tn.read_very_eager()
            time.sleep(0.5)
            tn.write(cmd + ENTER)
            rtstr = cmd + r'\s*.+\s*DIAG>>'
            rtstr = re.compile(rtstr, re.DOTALL | re.IGNORECASE)
            (index, match, data) = tn.expect([rtstr], timeout=10)
            work.writecmdlog(data)
            work.writelogtofile(logfile, data)
            if index == -1:
                strw = recode('端口%s - 获取baser错包计数器失败，请检查' % port)
                print strw
                work.writerunlog(strw)
                return ERROR_RT

            tmp = ''
            tmp = re.findall(r'P\d+\s*.+_errors\s*\|\s*(\d+)\s*pkts', data)
            if len(tmp) != 4:
                strw = recode('端口%s - 分析baser错包计数器失败，请检查' % port)
                print strw
                work.writerunlog(strw)
                flag = False
                continue
            else:
                old_errs = globalvar.baser_start_errs[port]
                if int(tmp[0]) != int(old_errs[0]) or int(tmp[2]) != int(old_errs[2]) \
                    or int(tmp[1]) != int(old_errs[1]) or int(tmp[3]) != int(old_errs[3]):
                    strw = recode('端口%s - baser有错包,收发包失败!' % port)
                    print strw
                    work.writerunlog(strw)
                    flag = False

            cfginfos = globalvar.CFG_INFOS
            tx_rx_value_check = cfginfos['TEST_CONTROL']['tx_rx_value_check']
            if tx_rx_value_check[0] == '1':
                tmp = ''
                tmp = re.findall(r'P\d+\s*.+_packets\s*\|\s*(\d+)\s*pkts', data)
                if len(tmp) != 4:
                    strw = recode('端口%s - 分析baser收发包计数器失败，请检查' % port)
                    print strw
                    work.writerunlog(strw)
                    flag = False
                    continue
                else:
                    if len(list(set(tmp))) != 1:
                        strw = recode('端口%s - baser收发包不等,收发包失败!' % port)
                        print strw
                        work.writerunlog(strw)
                        flag = False

        if flag:
            strw = recode('baser收发包测试通过')
            print strw
            work.writerunlog(strw)
            return SUCCESS_RT
        else:
            strw = recode('baser收发包测试不通过')
            print strw
            work.writerunlog(strw)
            return ERROR_RT

    except KeyboardInterrupt:
        strw = recode('程序执行到[app.diag_baser_check]被手动终止')
        print strw
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[app.diag_baser_check]异常退出!异常信息为%s' % err)
        print strw
        return ERROR_RT


# diag basekr init
def diag_basekr_init(tn):
    """ diag baser init """
    try:
        cmd = 'shell sh /tmp/config/config_baser40g.sh'
        rtstr = 'CONFIG\s*BASER40G\s*SUCCESS'
        rtstr = re.compile(rtstr, re.S | re.I)
        tn.read_very_eager()
        time.sleep(0.5)
        tn.write(cmd + ENTER)
        (index, match, data) = tn.expect([rtstr], timeout=30)
        work.writecmdlog(data)
        if index == -1:
            strw = recode('初始化baser40g参数失败')
            print strw
            work.writerunlog(strw)
            return ERROR_RT

        return SUCCESS_RT
    except KeyboardInterrupt:
        strw = recode('程序执行到[app.diag_basekr_init]被手动终止')
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[app.diag_basekr_init]异常退出!异常信息为%s' % err)
        print strw
        work.writerunlog(strw)
        return ERROR_RT


# diag basekr start
def diag_basekr_start(tn):
    """ diag baser start """
    try:
        dirValue = globalvar.LOG_DIR
        logname = 'diag_baser40g_start.log'
        logfile = os.path.join(dirValue, logname)

        cmds = ['fpga baser40g start 100 100 0 0 enable',
                'fpga baser40g show 0']
        for cmd in cmds:
            rtstr = cmd + r'\s*.+\s*DIAG>>'
            rtstr = re.compile(rtstr, re.IGNORECASE | re.DOTALL)
            tn.read_very_eager()
            time.sleep(0.5)
            tn.write(cmd + ENTER)
            (index, match, data) = tn.expect([rtstr], timeout=30)
            work.writecmdlog(data)
            if index == -1:
                strw = recode('配置diag basekr发包失败[%s]' % cmd)
                print strw
                work.writerunlog(strw)
                return ERROR_RT

        # check all port tx ok
        for i in range(0, 2):
            cmd = 'fpga baser40g show %s' % i
            rtstr = cmd + r'\s*.+\s*DIAG>>'
            rtstr = re.compile(rtstr, re.IGNORECASE | re.DOTALL)
            tn.read_very_eager()
            time.sleep(0.5)
            tn.write(cmd + ENTER)
            (index, match, data) = tn.expect([rtstr], timeout=30)
            work.writecmdlog(data)
            work.writelogtofile(logfile, data)
            if index == -1:
                strw = recode('配置diag basekr发包失败[%s]' % cmd)
                print strw
                work.writerunlog(strw)
                return ERROR_RT
            else:
                tmp = ''
                tmp = re.findall(r'P\d+\s*.+packets\s*\|\s*(\d+)\s*pkts', data)
                if len(tmp) != 5:
                    strw = recode('分析diag baser40g收发包数据失败')
                    print strw
                    work.writerunlog(strw)
                    return ERROR_RT
                else:
                    for j in tmp:
                        if int(j) == 0:
                            strw = recode('diag baser40g 发包有异常，请检查!')
                            print strw
                            work.writerunlog(strw)
                            return ERROR_RT

                # check current err counter
                tmp = re.findall(r'P\d+\s*.+errors\s*\|\s*(\d+)\s*pkts', data)
                if len(tmp) != 5:
                    strw = recode('分析diag baser40g收发包错包失败')
                    print strw
                    work.writerunlog(strw)
                    return ERROR_RT
                else:
                    globalvar.baser40g_start_errs[str(i)] = tmp
        return SUCCESS_RT
    except KeyboardInterrupt:
        strw = recode('程序执行到[app.diag_basekr_start]被手动终止')
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[app.diag_basekr_start]异常退出!异常信息为%s' % err)
        print strw
        work.writerunlog(strw)
        return ERROR_RT


# diag baser40g check
def diag_basekr_check(tn, stop=False):
    try:
        #切换工作路径
        dirValue = globalvar.LOG_DIR
        logfile = os.path.join(dirValue, 'diag_baser40g_result.log')

        strw = recode('开始检查baser40g收发包结果...')
        print strw
        work.writerunlog(strw)

        #define command
        stop_cmd = 'fpga baser40g stop'

        if stop:
            strw = recode('准备开始停止baser40g发包...')
            print strw
            work.writerunlog(strw)

            tn.read_very_eager()
            time.sleep(0.5)
            rtstr = stop_cmd + r'\s*DIAG>>'
            rtstr = re.compile(rtstr, re.DOTALL | re.IGNORECASE)
            tn.write(stop_cmd + ENTER)
            (index, match, data) = tn.expect([rtstr], timeout=10)
            work.writecmdlog(data)
            if index == -1:
                strw = recode('停止baser40g收发包失败，请检查')
                print strw
                work.writerunlog(strw)
                return ERROR_RT

        flag = True  # diag result control flag
        #check err counter
        portrange = range(0, 2)
        for port in portrange:
            port = str(port)
            cmd = 'fpga baser40g show %s' % port
            tn.read_very_eager()
            time.sleep(0.5)
            tn.write(cmd + ENTER)
            rtstr = cmd + r'\s*.+\s*DIAG>>'
            rtstr = re.compile(rtstr, re.DOTALL | re.IGNORECASE)
            (index, match, data) = tn.expect([rtstr], timeout=10)
            work.writecmdlog(data)
            work.writelogtofile(logfile, data)
            if index == -1:
                strw = recode('端口%s - 获取baser40g包计数器失败，请检查' % port)
                print strw
                work.writerunlog(strw)
                return ERROR_RT

            tmp = ''
            tmp = re.findall(r'P\d+\s*.+errors\s*\|\s*(\d+)\s*pkts', data)
            if len(tmp) != 5:
                strw = recode('端口%s - 分析baser40g错包计数器失败，请检查' % port)
                print strw
                work.writerunlog(strw)
                flag = False
                continue
            else:
                old_errs = globalvar.baser40g_start_errs[port]
                for cc in range(0, 5):
                    if int(tmp[cc]) != int(old_errs[cc]):
                        strw = recode('端口%s - baser40g有错包,收发包失败!' % port)
                        print strw
                        work.writerunlog(strw)
                        flag = False
                        break

            cfginfos = globalvar.CFG_INFOS
            tx_rx_value_check = cfginfos['TEST_CONTROL']['tx_rx_value_check']
            if tx_rx_value_check[3] == '1':
                tmp = ''
                tmp = re.findall(r'P\d+\s*.+_packets\s*\|\s*(\d+)\s*pkts', data)
                if len(tmp) != 5:
                    strw = recode('端口%s - 分析baser40g收发包计数器失败，请检查' % port)
                    print strw
                    work.writerunlog(strw)
                    flag = False
                    continue
                else:
                    if len(list(set(tmp))) != 1:
                        strw = recode('端口%s - baser40g收发包不等,收发包失败!' % port)
                        print strw
                        work.writerunlog(strw)
                        flag = False

        if flag:
            strw = recode('baser40g收发包测试通过')
            print strw
            work.writerunlog(strw)
            return SUCCESS_RT
        else:
            strw = recode('baser40g收发包测试不通过')
            print strw
            work.writerunlog(strw)
            return ERROR_RT

    except KeyboardInterrupt:
        strw = recode('程序执行到[app.diag_basekr_check]被手动终止')
        print strw
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[app.diag_basekr_check]异常退出!异常信息为%s' % err)
        print strw
        return ERROR_RT


# diag ddr start
def diag_fpga_ddr3_start(tn):
    """ diag FPGA ddr3 start """
    try:
        dirValue = globalvar.LOG_DIR
        logname = 'diag_ddr3_start.log'
        logfile = os.path.join(dirValue, logname)
        flag = True
        tn.write('cd /tmp' + ENTER)
        import runconfig
        product = runconfig.product
        if product == 'EP7000':
            ddr_co = ['1', '2']
        else:
            cfginfos = globalvar.CFG_INFOS
            subboard_count = cfginfos['CONTROL']['subboard_count']
            if subboard_count == '2':
                ddr_co = ['1', '2']
            else:
                ddr_co = ['1']
        for dim in ddr_co:
            cmd = 'slb -r 0x%sa1a' %dim
            rtStr = cmd + r'\s*.+0x00000003.+\s*#'
            rtStr = re.compile(rtStr, re.DOTALL | re.IGNORECASE)
            tn.read_very_eager()
            tn.write(cmd + ENTER)
            time.sleep(0.5)
            (index, match, data) = tn.expect([rtStr], timeout=60)
            work.writecmdlog(data)
            work.writelogtofile(logfile, data)
            if index == -1:
                strw = recode('FPGA-%s DDR1初始化失败'%str(dim))
                print strw
                work.writerunlog(strw)
                return ERROR_RT
            else:
                strw = recode('FPGA-%s DDR1初始化成功'%str(dim))
                print strw
                work.writerunlog(strw)

            cmd = 'slb -r 0x%sa5a' %dim
            rtStr = cmd + r'\s*.+0x00000003.+\s*#'
            rtStr = re.compile(rtStr, re.DOTALL | re.IGNORECASE)
            tn.read_very_eager()
            tn.write(cmd + ENTER)
            time.sleep(0.5)
            (index, match, data) = tn.expect([rtStr], timeout=60)
            work.writecmdlog(data)
            work.writelogtofile(logfile, data)
            if index == -1:
                strw = recode('FPGA-%s DDR2初始化失败'%str(dim))
                print strw
                work.writerunlog(strw)
                return ERROR_RT
            else:
                strw = recode('FPGA-%s DDR2初始化成功'%str(dim))
                print strw
                work.writerunlog(strw)

        for dim in ddr_co:
            cmd = 'sh /tmp/ddr3_diag.sh -start %s'%dim
            rtstr = cmd + r'\s*.+\s*/.+#'
            rtstr = re.compile(rtstr, re.IGNORECASE | re.DOTALL)
            tn.read_very_eager()
            time.sleep(0.5)
            tn.write(cmd + ENTER)
            (index, match, data) = tn.expect([rtstr], timeout=10)
            work.writecmdlog(data)
            work.writelogtofile(logfile, data)
            if index == -1:
                strw = recode('配置diag FPGA ddr3发包失败[%s]' % cmd)
                print strw
                work.writerunlog(strw)
                return ERROR_RT

        if flag:
            return SUCCESS_RT
        else:
            return ERROR_RT
    except KeyboardInterrupt:
        strw = recode('程序执行到[app.diag_fpga_ddr3_start]被手动终止')
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[app.diag_fpga_ddr3_start]异常退出!异常信息为%s' % err)
        print strw
        work.writerunlog(strw)
        return ERROR_RT


# diag FPGA ddr3 check
def diag_fpga_ddr3_check(tn):
    """ check diag ddr3 result"""
    try:
        flag = True
        dirValue = globalvar.LOG_DIR
        logname = 'diag_ddr3.log'
        logfile = os.path.join(dirValue, logname)

        tn.write('cd /tmp' + ENTER)
        import runconfig
        product = runconfig.product
        if product == 'EP7000':
            ddr_co = ['1', '2']
        else:
            cfginfos = globalvar.CFG_INFOS
            subboard_count = cfginfos['CONTROL']['subboard_count']
            if subboard_count == '2':
                ddr_co = ['1', '2']
            else:
                ddr_co = ['1']
        for dim in ddr_co:
            cmd = 'sh /tmp/ddr3_diag.sh -counter %s'%dim
            rtstr = cmd + r'\s*.+\s*/.+#'
            rtstr = re.compile(rtstr, re.IGNORECASE | re.DOTALL)
            tn.read_very_eager()
            time.sleep(0.5)
            tn.write(cmd + ENTER)
            (index, match, data) = tn.expect([rtstr], timeout=10)
            work.writecmdlog(data)
            work.writelogtofile(logfile, data)
            if index == -1:
                strw = recode('获取ddr3相关diag counter结果失败')
                print strw
                work.writerunlog(strw)
                return ERROR_RT
            else:
                tmp = re.findall(r'ddr\d+\s*:\s*(\d+)', data)
                if len(tmp) != 2:
                    strw = recode('分析ddr diag err counter结果失败')
                    print strw
                    work.writerunlog(strw)
                    return ERROR_RT
                else:
                    if len(list(set(tmp))) != 1 or list(set(tmp))[0] != '0':
                        strw = recode('[FPGA子卡%s] - diag ddr failed, please check!' % dim)
                        print strw
                        work.writerunlog(strw)
                        flag = False

        if flag:
            strw = recode('diag FPGA DDR3 OK！')
            print strw
            work.writerunlog(strw)
            return SUCCESS_RT
        else:
            strw = recode('diag FPGA DDR3 Failed！')
            print strw
            work.writerunlog(strw)
            return ERROR_RT

    except KeyboardInterrupt:
        strw = recode('程序执行到[app.diag_ddr3_check]被手动终止')
        print strw
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[app.diag_ddr3_check]异常退出!异常信息为%s' % err)
        print strw
        return ERROR_RT


# diag fpga cam
def diag_fpga_cam_auto_start(tn):
    """ diag FPGA cam auto start """
    try:
        dirValue = globalvar.LOG_DIR
        logname = 'diag_cam_start.log'
        logfile = os.path.join(dirValue, logname)
        flag = True
        tn.write('cd /tmp' + ENTER)
        import runconfig
        product = runconfig.product
        if product == 'EP7000':
            ddr_co = ['1', '2']
        else:
            cfginfos = globalvar.CFG_INFOS
            subboard_count = cfginfos['CONTROL']['subboard_count']
            if subboard_count == '2':
                ddr_co = ['1', '2']
            else:
                ddr_co = ['1']
        for dim in ddr_co:
            cmd = 'sh /tmp/cam_diag.sh -auto %s'%dim
            rtstr = cmd + r'\s*.+\s*/.+#'
            rtstr = re.compile(rtstr, re.IGNORECASE | re.DOTALL)
            tn.read_very_eager()
            time.sleep(0.5)
            tn.write(cmd + ENTER)
            (index, match, data) = tn.expect([rtstr], timeout=10)
            work.writecmdlog(data)
            work.writelogtofile(logfile, data)
            if index == -1:
                strw = recode('配置diag FPGA cam发包失败[%s]' % cmd)
                print strw
                work.writerunlog(strw)
                return ERROR_RT
            else:
                tmp1 = re.findall(r'cam\s*calibration\s*(\w+)!', data)
                tmp2 = re.findall(r'cam\s*read&write\s*diag\s*(\w+)', data)
                if len(tmp1) == 0 or len(tmp2) == 0:
                    strw = recode('分析diag cam start日志失败')
                    print strw
                    work.writerunlog(strw)
                    return ERROR_RT
                else:
                    if tmp1[0].upper() != 'PASS':
                        strw = recode('diag cam[%s] calibration Failed!'%dim)
                        print strw
                        work.writerunlog(strw)
                        flag = False
                    if tmp2[0].upper() != 'OK':
                        strw = recode('diag cam[%s] read&write diag Failed!'%dim)
                        print strw
                        work.writerunlog(strw)
                        flag = False

        if flag:
            return SUCCESS_RT
        else:
            return ERROR_RT
    except KeyboardInterrupt:
        strw = recode('程序执行到[app.diag_fpga_cam_auto_start]被手动终止')
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[app.diag_fpga_cam_auto_start]异常退出!异常信息为%s' % err)
        print strw
        work.writerunlog(strw)
        return ERROR_RT


# diag FPGA cam check
def diag_fpga_cam_check(tn, stop=False):
    """ check diag cam result"""
    try:
        flag = True
        dirValue = globalvar.LOG_DIR
        logname = 'diag_cam.log'
        logfile = os.path.join(dirValue, logname)

        if stop:
            cmd = 'sh /tmp/cam_diag.sh -stop'
            tn.write(cmd + ENTER)
            time.sleep(0.5)
            tn.read_very_eager()

        import runconfig
        product = runconfig.product
        if product == 'EP7000':
            ddr_co = ['1', '2']
        else:
            cfginfos = globalvar.CFG_INFOS
            subboard_count = cfginfos['CONTROL']['subboard_count']
            if subboard_count == '2':
                ddr_co = ['1', '2']
            else:
                ddr_co = ['1']
        for dim in ddr_co:
            cmd = 'sh /tmp/cam_diag.sh -counter %s' % dim
            rtstr = cmd + r'\s*.+\s*/.+#'
            rtstr = re.compile(rtstr, re.IGNORECASE | re.DOTALL)
            tn.read_very_eager()
            time.sleep(0.5)
            tn.write(cmd + ENTER)
            (index, match, data) = tn.expect([rtstr], timeout=10)
            work.writecmdlog(data)
            work.writelogtofile(logfile, data)
            if index == -1:
                strw = recode('获取cam相关diag counter结果失败')
                print strw
                work.writerunlog(strw)
                return ERROR_RT
            else:
                tmp = re.findall(r'\w+\s*:\s*(\d+)', data)
                if len(tmp) != 4:
                    strw = recode('分析ddr diag cam counter结果失败')
                    print strw
                    work.writerunlog(strw)
                    return ERROR_RT
                else:
                    if not stop:
                        if tmp[0] != '0':
                            strw = recode('子卡%s- diag cam Failed[err counter]' % dim)
                            print strw
                            work.writerunlog(strw)
                            flag = False
                    else:
                        if len(list(set(tmp))) != 2 and list(set(tmp))[1] == '0':
                            strw = recode('子卡%s- diag cam Failed[req val hit]' % dim)
                            print strw
                            work.writerunlog(strw)
                            flag = False

        if flag:
            strw = recode('diag FPGA CAM OK！')
            print strw
            work.writerunlog(strw)
            return SUCCESS_RT
        else:
            strw = recode('diag FPGA CAM Failed！')
            print strw
            work.writerunlog(strw)
            return ERROR_RT

    except KeyboardInterrupt:
        strw = recode('程序执行到[app.diag_fpga_cam_check]被手动终止')
        print strw
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[app.diag_fpga_cam_check]异常退出!异常信息为%s' % err)
        print strw
        return ERROR_RT


# diag fpga sgmii
def diag_fpga_sgmii_auto_start(tn):
    """ diag FPGA sgmii auto start """
    try:
        dirValue = globalvar.LOG_DIR
        logname = 'diag_sgmii_start.log'
        logfile = os.path.join(dirValue, logname)
        flag = True
        tn.write('cd /tmp' + ENTER)

        import runconfig
        product = runconfig.product
        if product == 'EP7000':
            ddr_co = ['1', '2']
        else:
            cfginfos = globalvar.CFG_INFOS
            subboard_count = cfginfos['CONTROL']['subboard_count']
            if subboard_count == '2':
                ddr_co = ['1', '2']
            else:
                ddr_co = ['1']
        #cmd = 'sh /tmp/start_passthrough.sh'
        #rtstr = cmd + r'\s*.+\s*/.+#'
        #rtstr = re.compile(rtstr, re.IGNORECASE | re.DOTALL)
        #tn.read_very_eager()
        #time.sleep(0.5)
        #tn.write(cmd + ENTER)
        #(index, match, data) = tn.expect([rtstr], timeout=10)
        #work.writecmdlog(data)
        #work.writelogtofile(logfile, data)
        #if index == -1:
        #    strw = recode('启动passthrough失败')
        #    print strw
        #    work.writerunlog(strw)
        #    return ERROR_RT
        #time.sleep(5)
        #tn.write(ENTER)
        for dim in ddr_co:
            '''
            #删除CPU端loopback
            cmds = ['oct-linux-csr pcs1_int00%s_en_reg 0x07b4'%dim,
                    'oct-linux-csr pcs1_misc00%s_ctl_reg 0x1405'%dim,
                    'oct-linux-csr pcs1_mr00%s_control_reg 0x9140'%dim,
                    'ifconfig eth%s promisc up'%dim]
            for cmd in cmds:
                rtstr = '/.+#'
                rtstr = re.compile(rtstr, re.IGNORECASE | re.DOTALL)
                tn.read_very_eager()
                time.sleep(0.5)
                tn.write(cmd + ENTER)
                (index, match, data) = tn.expect([rtstr], timeout=10)
                work.writecmdlog(data)
                work.writelogtofile(logfile, data)
                if index == -1:
                    strw = recode('配置CPU LOOP失败[%s]' % cmd)
                    print strw
                    work.writerunlog(strw)
                    return ERROR_RT
            '''
            cmd = 'sh /tmp/sgmii_diag.sh -auto %s'%dim
            rtstr = cmd + r'\s*.+\s*/.+#'
            rtstr = re.compile(rtstr, re.IGNORECASE | re.DOTALL)
            tn.read_very_eager()
            time.sleep(0.5)
            tn.write(cmd + ENTER)
            (index, match, data) = tn.expect([rtstr], timeout=10)
            work.writecmdlog(data)
            work.writelogtofile(logfile, data)
            if index == -1:
                strw = recode('配置diag FPGA sgmii发包失败[%s]' % cmd)
                print strw
                work.writerunlog(strw)
                return ERROR_RT

        if flag:
            return SUCCESS_RT
        else:
            return ERROR_RT
    except KeyboardInterrupt:
        strw = recode('程序执行到[app.diag_fpga_sgmii_auto_start]被手动终止')
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[app.diag_fpga_sgmii_auto_start]异常退出!异常信息为%s' % err)
        print strw
        work.writerunlog(strw)
        return ERROR_RT


# diag FPGA sgmi check
def diag_fpga_sgmii_check(tn, stop=False):
    """ check diag cam result"""
    try:
        flag = True
        dirValue = globalvar.LOG_DIR
        logname = 'diag_sgmii.log'
        logfile = os.path.join(dirValue, logname)

        if stop:
            cmd = 'sh /tmp/sgmii_diag.sh -stop'
            tn.write(cmd + ENTER)
            time.sleep(0.5)
            tn.read_very_eager()

        import runconfig
        product = runconfig.product
        if product == 'EP7000':
            ddr_co = ['1', '2']
        else:
            cfginfos = globalvar.CFG_INFOS
            subboard_count = cfginfos['CONTROL']['subboard_count']
            if subboard_count == '2':
                ddr_co = ['1', '2']
            else:
                ddr_co = ['1']
        for dim in ddr_co:
            cmd = 'sh /tmp/sgmii_diag.sh -counter %s' % dim
            rtstr = cmd + r'\s*.+\s*/.+#'
            rtstr = re.compile(rtstr, re.IGNORECASE | re.DOTALL)
            tn.read_very_eager()
            time.sleep(0.5)
            tn.write(cmd + ENTER)
            (index, match, data) = tn.expect([rtstr], timeout=10)
            work.writecmdlog(data)
            work.writelogtofile(logfile, data)
            if index == -1:
                strw = recode('获取sgmii相关diag counter结果失败')
                print strw
                work.writerunlog(strw)
                return ERROR_RT
            else:
                result = dict()
                for line in re.split('\n|\|', data):
                    #print line
                    tmp = line.split(':')
                    if len(tmp) != 2:
                        continue
                    else:
                        key = tmp[0].strip()
                        value = tmp[1].strip()
                        result[key] = value

                if stop:
                    try:
                        if result['rx_err'] != '0':
                            strw = recode('diag sgmii err![rx err]')
                            print strw
                            work.writerunlog(strw)
                            flag = False
                    except:
                        strw = recode('分析sgmii diag counter 失败[rx_err not in result dict]')
                        print strw
                        work.writerunlog(strw)
                        flag = False

                try:
                #if True:
                    print result
                    eth_tx_key = 'eth%s_tx_pkt' % dim
                    eth_rx_key = 'eth%s_rx_pkt' % dim
                    if int(result['rx_pkt']) != int(result[eth_tx_key]) - 6 or result['rx_pkt'] == '0':
                        strw = recode('diag sgmii err![tx != rx]')
                        print strw
                        work.writerunlog(strw)
                        flag = False
                    if int(result['tx_pkt']) != int(result[eth_rx_key]) or result['tx_pkt'] == '0':
                        strw = recode('diag sgmii err![tx != rx]')
                        print strw
                        work.writerunlog(strw)
                        flag = False

                except:
                    strw = recode('分析sgmii diag counter 失败[some key not in result dict]')
                    print strw
                    work.writerunlog(strw)
                    flag = False

        if flag:
            strw = recode('diag FPGA SGMII OK！')
            print strw
            work.writerunlog(strw)
            return SUCCESS_RT
        else:
            strw = recode('diag FPGA SGMII Failed！')
            print strw
            work.writerunlog(strw)
            return ERROR_RT

    except KeyboardInterrupt:
        strw = recode('程序执行到[app.diag_fpga_sgmii_check]被手动终止')
        print strw
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[app.diag_fpga_sgmii_check]异常退出!异常信息为%s' % err)
        print strw
        return ERROR_RT


# diag fpga xaui
def diag_fpga_xaui_start(tn):
    """ diag FPGA xaui start """
    try:
        dirValue = globalvar.LOG_DIR
        logname = 'diag_xaui_loop.log'
        logfile = os.path.join(dirValue, logname)
        flag = True
        tn.write('cd /tmp' + ENTER)
        import runconfig
        product = runconfig.product
        if product == 'EP7000':
            ddr_co = ['1', '2']
        else:
            cfginfos = globalvar.CFG_INFOS
            subboard_count = cfginfos['CONTROL']['subboard_count']
            if subboard_count == '2':
                ddr_co = ['1', '2']
            else:
                ddr_co = ['1']
        for dim in ddr_co:
            cmd = 'sh /tmp/xaui_diag.sh -loop %s'%dim
            rtstr = cmd + r'\s*.+\s*/.+#'
            rtstr = re.compile(rtstr, re.IGNORECASE | re.DOTALL)
            tn.read_very_eager()
            time.sleep(0.5)
            tn.write(cmd + ENTER)
            (index, match, data) = tn.expect([rtstr], timeout=10)
            work.writecmdlog(data)
            work.writelogtofile(logfile, data)
            if index == -1:
                strw = recode('配置diag FPGA loop失败[%s]' % cmd)
                print strw
                work.writerunlog(strw)
                return ERROR_RT

        if flag:
            return SUCCESS_RT
        else:
            return ERROR_RT
    except KeyboardInterrupt:
        strw = recode('程序执行到[app.diag_fpga_xaui_start]被手动终止')
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[app.diag_fpga_xaui_start]异常退出!异常信息为%s' % err)
        print strw
        work.writerunlog(strw)
        return ERROR_RT


def start_powercycle_test():

    mode = globalvar.MODE
    if mode == 'CMD':
        rt = powercycle_burn()
    else:
        rt = atool_powercycle_burn()
    if rt == ERROR_RT or rt == OTHER_ERROR:
        strw = recode('PowerCycle Test Failed!')
        print strw
        work.writerunlog(strw)
        return ERROR_RT

    strw = recode('PowerCycle Test Pass!')
    print strw
    work.writerunlog(strw)
    return SUCCESS_RT


def reboot_all_dut():
    tn= globalvar.TN
    cfginfos = globalvar.CFG_INFOS
    reboot_times = cfginfos['BURNINTIME']['reboot_times']

    flag = True
    try:
        reboot_times = int(reboot_times)
        tt = 0

        while tt < reboot_times:
            strw = recode('重启测试次数一共为%s, 当前测试次数为%s' %(str(reboot_times), str(tt+1)))
            print strw
            work.writerunlog(strw)
            if connection.RebootAndGotoLinux() == ERROR_RT:
                flag = False
                break
            tt = tt + 1
            globalvar.tt = tt
        if not flag:
            strw = recode('重启拷机失败.')
            print strw
            work.writerunlog(strw)
            MODE = globalvar.MODE
            if MODE == 'AUTOTOOL':
                ID = globalvar.MODE
                tcplib.SendStatusMsg(ID, 'FAIL-Reboot重启拷机失败！')
            return ERROR_RT
        else:
            strw = recode('重启拷机通过.')
            print strw
            work.writerunlog(strw)
            return SUCCESS_RT

    except KeyboardInterrupt:
        strw = '程序执行到[app.reboot_all_dut]被手动终止'
        print recode(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = '程序执行到[app.reboot_all_dut]异常退出!异常信息为%s' % err
        print recode(strw)
        return ERROR_RT


#CMD模式下面重启拷机
def powercycle_burn():
    """
    参数传递：        path:              流程log控制文件
    工作方式：       开始上下电重启拷机
    返回参数：       返回执行的结果， SUCCESS_RT or ERROR_RT
    """
    try:
        '''here will start power cycle test'''

        strw = recode('准备开始 上下电重启拷机...')
        print strw
        work.writerunlog(strw)

        #To ssh devices
        cfgInfos = globalvar.CFG_INFOS

        status_d = 'power_cycle'

        powercycle_times = cfgInfos['BURNINTIME']['powercycle_times']
        NPS_IP = cfgInfos['NPSINFO']['nps_ip']
        NPS_PORT_L = cfgInfos['NPSINFO']['nps_port_l']
        NPS_PORT_R = cfgInfos['NPSINFO']['nps_port_r']


        global g_mutex
        global STOP
        global result
        global status
        thread_pool = []
        status = {}
        status['Port'] = ''
        import threading
        g_mutex = threading.Lock()
        t = 0

        tn = globalvar.TN
        sublogDir = globalvar.LOG_DIR
        cfginfos = globalvar.CFG_INFOS
        ps = cfginfos['SETTING']['ps']
        STOP = 'N'
        result = {}
        th = threading.Thread(target=power_cycle_save_to_file_catch_err,args=(tn, sublogDir, status_d,ps));
        th.setDaemon(True)
        thread_pool.append(th)
        t += 1

        status['status'] = t
        status['allexps'] = t
        # start threads one by one
        for i in range(t):
            thread_pool[i].start()

        old_boot = 0
        strw = recode('开始上下电拷机...')
        print strw

        NPS_PORTS = [NPS_PORT_L, NPS_PORT_R]

        print recode('开始将所有电源都关闭')
        for NPS_PORT in NPS_PORTS:
            if connection.work_NPS(NPS_IP, NPS_PORT, 'OFF') == ERROR_RT:
                strw = recode('控制powercycle失败，请检查')
                print strw
                g_mutex.acquire()
                STOP = 'Y'
                status['status'] = 0
                g_mutex.release()
                return ERROR_RT
            time.sleep(5)

        print recode('所有电源都已经关闭')
        while old_boot < int(powercycle_times) + 1:
            for NPS_PORT in NPS_PORTS:
                if NPS_PORT == NPS_PORT_L:
                    g_mutex.acquire()
                    status['Port'] = '左'
                    g_mutex.release()
                else:
                    g_mutex.acquire()
                    status['Port'] = '右'
                    g_mutex.release()
                if connection.work_NPS(NPS_IP, NPS_PORT, 'ON') == ERROR_RT:
                    strw = recode('控制powercycle失败，请检查')
                    print strw
                    g_mutex.acquire()
                    STOP = 'Y'
                    status['status'] = 0
                    g_mutex.release()
                    return ERROR_RT
                g_mutex.acquire()
                status['status'] = 0
                g_mutex.release()
                while True:
                    if status['status'] == t:
                        if connection.work_NPS(NPS_IP, NPS_PORT, 'OFF') == ERROR_RT:
                            strw = recode('控制powercycle失败，请检查')
                            print strw
                            g_mutex.acquire()
                            STOP = 'Y'
                            status['status'] = 0
                            g_mutex.release()
                            return ERROR_RT
                        break
                    else:
                        continue
            old_boot += 1
            continue
        while True:
            if status['status'] == t:
                g_mutex.acquire()
                STOP = 'Y'
                g_mutex.release()
                break
            else:
                continue
        #重新将所有NPS端口都打开
        for NPS_PORT in NPS_PORTS:
            if connection.work_NPS(NPS_IP, NPS_PORT, 'ON') == ERROR_RT:
                strw = recode('控制powercycle失败，请检查')
                print strw
                g_mutex.acquire()
                STOP = 'Y'
                status['status'] = 0
                g_mutex.release()
                return ERROR_RT
            time.sleep(5)

        time.sleep(10)
        strw = recode('等待所有拷机结束')
        print strw
        #开始对所有是否结束进行判断！
        for i in range(t):
            threading.Thread.join(thread_pool[i])
        print recode('所有拷机都已经结束')

        rakes = result.keys()
        rakes.sort()
        for key in rakes:
            kraut = result[key]
            for kk in kraut.keys():
                strw = recode('[P/S:%s]-[%s]路电源重启时候，失败[%d]次'%(key, kk, kraut[kk]))
                print strw
                work.writerunlog(strw)
        return SUCCESS_RT

    except KeyboardInterrupt:
        strw = recode('程序执行到[app.powercycle_burn]被手动终止')
        print strw
        return OTHER_ERROR
    except Exception,err:
        strw = recode('程序执行到[app.powercycle_burn]异常退出!异常信息为%s'%err)
        print strw
        return ERROR_RT


## 上下电重启拷机-CMD模式
#
# 用来在CMD模式做上下电重启拷机
def power_cycle_save_to_file_catch_err(subchild, sublogDir, statusd, k):
    """将制动的串口的输出重定向到指定的文件中"""
    global STOP
    global result
    global status

    try:
        sublogFile = sublogDir + '/' + statusd +'_console.log'
        logtime = os.path.join(sublogDir, 'reboot.log')
        max_rtimes = 5
        rtimes = 0
        tt = 0
        ttt = 0

        eptAppStr = '/.+#'
        eptAppStr = re.compile(eptAppStr, re.IGNORECASE | re.DOTALL)
        eptAppStr1 = '~.+#'
        eptAppStr1 = re.compile(eptAppStr1, re.IGNORECASE | re.DOTALL)
        eptCliStr = 'CLI>'
        eptCliStr = re.compile(eptCliStr, re.IGNORECASE | re.DOTALL)
        eptUboot = 'Uboot\s*#'
        eptUboot = re.compile(eptUboot, re.IGNORECASE | re.DOTALL)
        rt1 = 'U-Boot'
        rt1 = re.compile(rt1, re.IGNORECASE | re.DOTALL)
        rt2 = 'Uboot_Octeon_cpf6100_Prog'
        rt2 = re.compile(rt2, re.IGNORECASE | re.DOTALL)
        rtline = '\n'
        rtline = re.compile(rtline, re.IGNORECASE | re.DOTALL)
        mark = 'bootend'
        while True:
            if status['status'] == 0 and mark == 'bootend':
                mark = 'ReStart'
                rtimes = 0
            (i, match, data) = subchild.expect([rt1, rt2, eptAppStr, eptAppStr1, eptCliStr, eptUboot, rtline], timeout=60)
            work.writelogtofile(sublogFile, data)
            if i == -1:
                g_mutex.acquire()
                tru_status = status['status']
                port = status['Port']
                allexps = status['allexps']
                g_mutex.release()
                if tru_status == allexps or mark == 'bootend':
                    strw = recode('等待其他设备完成，或者等待power cycle设备启动')
                    log = open(logtime, 'a')
                    print >> log, strw
                    log.close()
                    if STOP == 'Y':
                        break
                    else:
                        continue
                else:
                    strw = recode('超时啦~~')
                    log = open(logtime, 'a')
                    print >> log, strw
                    log.close()
                    rtimes += 1
                    if rtimes > max_rtimes:
                        ttt += 1
                        strw = recode('设备【Port%s】：[%s]路电源供电，启动失败%d次'%(k,port,ttt))
                        print strw
                        g_mutex.acquire()
                        status['status'] += 1
                        if k not in result.keys():
                            result[k] = {}
                            result[k][port] = 1
                        else:
                            if port not in result[k].keys():
                                result[k][port] = 1
                            else:
                                result[k][port] += 1
                        g_mutex.release()
                        if STOP == 'Y':
                            break
                        else:
                            mark = 'bootend'
                            rtimes = 0
                            continue
                    else:
                        continue
            elif i == 0 or i == 1:
                mark = 'Rebooting'
                rtimes = 0
                continue
            elif i == 2 or i == 3 or i == 4 or i == 5:
                rtimes = 0
                if mark == 'Rebooting':
                    mark = 'boot end'
                    g_mutex.acquire()
                    status['status'] += 1
                    g_mutex.release()
                    tt += 1
                    strw = recode('设备【Port%s】：开始第[%d]次Reboot拷机...\n' %(k, tt))
                    #print strw
                    log = open(logtime, 'a')
                    print >> log, strw
                    log.close()
                    if STOP == 'Y':
                        break
                    else:
                        continue
                else:
                    rtimes = 0
                    continue
            else:
                rtimes = 0
                continue

        strw = recode('设备【Port%s】：上下电拷机结束.' %k)
        print strw
        log = open(logtime, 'a')
        print >> log, strw
        log.close()
        return SUCCESS_RT
    except KeyboardInterrupt:
        strw = recode('程序执行到[app.power_cycle_save_to_file_catch_err]被手动终止')
        print strw
        return OTHER_ERROR
    except Exception,err:
        strw = recode('程序执行到[app.power_cycle_save_to_file_catch_err]异常退出!异常信息为%s'%err)
        print strw
        return ERROR_RT


#autotool模式下面重启拷机
def atool_powercycle_burn():
    """
    参数传递：        path:              流程log控制文件
    工作方式：       开始上下电重启拷机
    返回参数：       返回执行的结果， SUCCESS_RT or ERROR_RT
    """
    try:
        '''here will start power cycle test'''
        ID = globalvar.ID  #用来与autotool交互的ID

        strw = recode('准备开始 上下电重启拷机...')
        print strw
        work.writerunlog(strw)

        global result
        result = {}
        cfginfos = globalvar.CFG_INFOS
        powercycle_times = cfginfos['BURNINTIME']['powercycle_times']
        #port_list = ['nps_port_l', 'nps_port_r']
        port_list = ['A', 'B']
        #首先将所有电都关闭
        for port in port_list:
            if tcplib.SendPCycleDownMsg(ID,port) == ERROR_RT:
                return ERROR_RT
            time.sleep(1)
        time.sleep(5)
        flag = True
        for i in range(1, int(powercycle_times)+1):
            for port in port_list:
                #if port == 'nps_port_l':
                if port == 'A':
                    k = '左'
                else:
                    k = '右'
                if tcplib.SendPCycleUpMsg(ID,port) == ERROR_RT:
                    return ERROR_RT
                time.sleep(20)
                tn = globalvar.TN
                sublogDir = globalvar.LOG_DIR
                ps = cfginfos['SETTING']['ps']
                rt = atool_power_cycle_reboot(tn, sublogDir, ps, k)
                if rt == ERROR_RT or rt == OTHER_ERROR:
                    flag = False
                    tcplib.SendStatusMsg(ID, '设备%s路电源第%d次上下电测试失败 ！'%(k,i))
                    strw = recode('设备%s路电源第%i次上下电测试失败'%(k,i))
                    work.writerunlog(strw)
                    break
                else:
                    strw = recode('设备%s路电源第%i次上下电测试成功'%(k,i))
                    work.writerunlog(strw)

                #登陆到板卡上
                tn.write('root' + ENTER)
                time.sleep(0.5)
                tn.write('embed220' + ENTER)
                time.sleep(0.5)

                #执行Diag操作
                test_list = [
                    SetIP,                          # 设置IP地址
                    download_files,                 # 下载必要的工具包
                    get_fru_info,                   # 获取产品FRU相关信息
                    get_board_type,                 # 获取板卡类型
                    load_driver,                    # 加载驱动
                    download_FPGA,                  # 下载FPGA
                    load_FPGA,                      # 加载FPGA
                    special.diag_i2c,               # diag i2c接口
                    special.diag_mdio,              # diag mdio
                    special.diag_FPGA_funcs_start,  # diag FPGA functions start
                    special.diag_bcm_start,         # diag bcm start send pkt
                    special.start_diag_sfp,         # start diag sfp shell script
                    special.check_diag_sfp,         # check diag sfp shell script result
                    special.start_temp_vol_read,    # start read voltage and temp
                    special.check_temp_vol,         # check voltage and temp
                    special.diag_FPGA_funcs_check,  # check diag FPGA functions result
                    #special.diag_bcm_check,         # check bcm
                    check_power_margin              # check power margin function
                ]

                for func in test_list:
                    if func() != SUCCESS_RT:
                        show_fail_info('FAIL-Test[%s]失败' % func.__name__)
                        return ERROR_RT

                if tcplib.SendPCycleDownMsg(ID,port) == ERROR_RT:
                    return ERROR_RT

                #time.sleep(10*60)

                time.sleep(2)
        #首先将所有电都关闭
        for port in port_list:
            if tcplib.SendPCycleUpMsg(ID,port) == ERROR_RT:
                return ERROR_RT
            time.sleep(1)
        time.sleep(5)
        rkeys= result.keys()
        rkeys.sort()
        for key in rkeys:
            kresult = result[key]
            for kk in kresult.keys():
                strw = recode('[P/S:%s]-[%s]路电源重启时候，失败[%d]次'%(key, kk, kresult[kk]))
                print strw
                work.writerunlog(strw)
        #将所有log上传到ftp上面去
        if not flag:
            return ERROR_RT
        else:
            return SUCCESS_RT

    except KeyboardInterrupt:
        strw = recode('程序执行到[special.atool_powercycle_burn]被手动终止')
        print strw
        return OTHER_ERROR
#    except Exception,err:
#        strw = recode('程序执行到[special.atool_powercycle_burn]异常退出!异常信息为%s'%err)
#        print strw
#        return ERROR_RT


## 上下电重启拷机-autotool模式
#
# 用来在autotool模式模式做上下电重启拷机
def atool_power_cycle_reboot(subchild, sublogDir, k, port):
    """将制动的串口的输出重定向到指定的文件中"""
    global result

    try:
        logtime = os.path.join(sublogDir, 'power_cycle_reboot.log')
        logtime_console = os.path.join(sublogDir, 'power_cycle_reboot_console.log')
        max_rtimes = 5
        rtimes = 0
        tt = 0
        ttt = 0

        eptAppStr = 'login:'
        eptAppStr = re.compile(eptAppStr, re.IGNORECASE | re.DOTALL)
        eptAppStr1 = 'login:'
        eptAppStr1 = re.compile(eptAppStr1, re.IGNORECASE | re.DOTALL)
        eptCliStr = 'CLI>'
        eptCliStr = re.compile(eptCliStr, re.IGNORECASE | re.DOTALL)
        eptUboot = 'Uboot\s*#'
        eptUboot = re.compile(eptUboot, re.IGNORECASE | re.DOTALL)
        rt1 = 'U-Boot'
        rt1 = re.compile(rt1, re.IGNORECASE | re.DOTALL)
        rt2 = 'Uboot_Octeon'
        rt2 = re.compile(rt2, re.IGNORECASE | re.DOTALL)
        rtline = '\n'
        rtline = re.compile(rtline, re.IGNORECASE | re.DOTALL)

        while True:
            (i, match, data) = subchild.expect([rt1, rt2, eptAppStr, eptAppStr1, eptCliStr, eptUboot, rtline], timeout=60)
            work.writelogtofile(logtime_console, data)
            if i == -1:
                strw = recode('超时啦~~')
                log = open(logtime, 'a')
                print >> log, strw
                log.close()
                rtimes += 1
                if rtimes > max_rtimes:
                    ttt += 1
                    strw = recode('设备【Port%s】：[%s]路电源供电，启动失败[%d]次'%(k,port,ttt))
                    print strw
                    if k not in result.keys():
                        result[k] = {}
                        result[k][port] = 1
                    else:
                        if port not in result[k].keys():
                            result[k][port] = 1
                        else:
                            result[k][port] += 1
                    return ERROR_RT
                else:
                    continue
            elif i == 0 or i == 1:
                rtimes = 0
                continue
            elif i == 2 or i == 3 or i == 4 or i == 5:
                time.sleep(0.5)
                (i, match, data) = subchild.expect([rt1, rt2, eptAppStr, eptAppStr1, eptCliStr, eptUboot, rtline], timeout=10)
                work.writelogtofile(logtime_console, data)
                tt += 1
                strw = recode('设备【Port%s】：开始第[%d]次Reboot拷机...\n' %(k, tt))
                #print strw
                log = open(logtime, 'a')
                print >> log, strw
                log.close()
                return SUCCESS_RT
            else:
                rtimes = 0
                continue

    except KeyboardInterrupt:
        strw = recode('程序执行到[special.atool_power_cycle_reboot]被手动终止')
        print strw
        return OTHER_ERROR
    except Exception,err:
        strw = recode('程序执行到[special.atool_power_cycle_reboot]异常退出!异常信息为%s'%err)
        print strw
        return ERROR_RT


def save_file_to_flash():
    """
    参数传递：       tn:         与板卡交互的通道; kouban:  扣板的类型
    工作方式：       跑一下软件包给的软件包
    返回参数：       如果没err则返回SUCCESS_RT，有err则返回ERROR_RT
    """
    try:
        tn = globalvar.TN
        workdir = globalvar.LOG_DIR
        bootFile = os.path.join(workdir, 'burn_flash.log')

        strw = recode('开始烧录flash...')
        print strw
        work.writerunlog(strw)

        cfginfos = globalvar.CFG_INFOS
        getinfos = globalvar.getinfos
        part_number = getinfos['pn']
        if re.search('71', part_number):
            kernelver = cfginfos['CUST_IMAGE']['kernelver_71']
        elif re.search('70', part_number):
            kernelver = cfginfos['CUST_IMAGE']['kernelver_70']
        elif re.search('72', part_number):
            kernelver = cfginfos['CUST_IMAGE']['kernelver_72']
        else:
            strw = recode('不支持的市场型号[%s]'%part_number)
            print strw
            work.writerunlog(strw)
            return ERROR_RT


        cfginfos = globalvar.CFG_INFOS
        end_addr = '0x17ffffff'
        savecmd = 'saveenv'
        protectup = 'protect up 0x10e00000 %s'%end_addr
        protectoff = 'protect off 0x10e00000 %s'%end_addr
        erasecmd = 'erase 0x10e00000 %s'%end_addr
        cpcmd = 'cp.b 0x20000000 0x10e00000 0x2800000'
        cmpcmd = 'cmp.b 0x20000000 0x10e00000 0x2800000'
        setenvcmd = 'cp.b 0x10e00000 0x20000000 0x2800000;bootoctlinux 0x20000000 coremask=0x1 rdinit=/preinit'
        tftpcmd = 'tftpboot 0x20000000 %s'%kernelver

        #下载kernel到mem中
        tn.read_very_eager()
        end_str = 'done'
        end_str = re.compile(end_str, re.DOTALL | re.IGNORECASE)
        nofile = 'file\s*not\s*found'
        nofile = re.compile(nofile, re.DOTALL | re.IGNORECASE)
        tn.write(tftpcmd + ENTER)
        (index, match, data) = tn.expect([nofile,end_str], timeout=300)
        work.writecmdlog(data)
        work.writelogtofile(bootFile, data)
        if index == -1:
            strw = recode('下载kernel文件失败')
            print strw
            work.writerunlog(strw)
            return ERROR_RT
        elif index == 0:
            strw = recode('kernel文件不存在，请检查')
            print strw
            work.writerunlog(strw)
            return ERROR_RT

        #解除flash锁定
        tn.read_very_eager()
        end_str = 'Protected'
        end_str = re.compile(end_str, re.DOTALL | re.IGNORECASE)
        tn.write(protectup + ENTER)
        (index, match, data) = tn.expect([end_str], timeout=60)
        work.writecmdlog(data)
        work.writelogtofile(bootFile, data)
        if index == -1:
            strw = recode('解除flash写保护失败')
            print strw
            work.writerunlog(strw)
            return ERROR_RT


        tn.read_very_eager()
        end_str = 'Un-Protected'
        end_str = re.compile(end_str, re.DOTALL | re.IGNORECASE)
        tn.write(protectoff + ENTER)
        (index, match, data) = tn.expect([end_str], timeout=60)
        work.writecmdlog(data)
        work.writelogtofile(bootFile, data)
        if index == -1:
            strw = recode('解除flash写保护失败')
            print strw
            work.writerunlog(strw)
            return ERROR_RT

        #檫除flash
        tn.read_very_eager()
        end_str = 'sectors'
        end_str = re.compile(end_str, re.DOTALL | re.IGNORECASE)
        start_str = erasecmd
        start_str = re.compile(start_str, re.DOTALL | re.IGNORECASE)
        wk_str = '\n'
        wk_str = re.compile(wk_str, re.DOTALL | re.IGNORECASE)
        tn.write(erasecmd + ENTER)
        logStart = False
        while True:
            (index, match, data) = tn.expect([start_str, end_str, wk_str], timeout=60)
            work.writelogtofile(bootFile, data)
            if index == -1:
                continue
            elif index == 0:
                logStart = True
                continue
            elif index == 1:
                if logStart:
                    break
                else:
                    continue
            else:
                continue

        time.sleep(1)
        #将kernel文件写到flash当中
        tn.read_very_eager()
        end_str = 'done'
        end_str = re.compile(end_str, re.DOTALL | re.IGNORECASE)
        start_str = 'Copy\s*to\s*Flash'
        start_str = re.compile(start_str, re.DOTALL | re.IGNORECASE)
        wk_str = '\n'
        wk_str = re.compile(wk_str, re.DOTALL | re.IGNORECASE)
        tn.write(cpcmd + ENTER)
        logStart = False
        while True:
            (index, match, data) = tn.expect([start_str, end_str, wk_str], timeout=60)
            work.writelogtofile(bootFile, data)
            if index == -1:
                continue
            elif index == 0:
                logStart = True
                continue
            elif index == 1:
                if logStart:
                    break
                else:
                    continue
            else:
                continue

        #比对写入的是否一致
        tn.read_very_eager()
        end_str = 'were\s*the\s*same'
        end_str = re.compile(end_str, re.DOTALL | re.IGNORECASE)
        tn.write(cmpcmd + ENTER)
        (index, match, data) = tn.expect([end_str], timeout=600)
        work.writecmdlog(data)
        work.writelogtofile(bootFile, data)
        if index == -1:
            strw = recode('烧录进去的文件比对不正确')
            print strw
            work.writerunlog(strw)
            return ERROR_RT

        tn.read_very_eager()
        tn.write('askenv bootcmd' + ENTER)
        tn.expect([':'], timeout=10)

        #保存环境变量
        tn.read_very_eager()
        tn.write(setenvcmd + ENTER)
        uboot_str = 'uboot\s*#'
        uboot_str = re.compile(uboot_str, re.DOTALL | re.IGNORECASE)
        (index, match, data) = tn.expect([uboot_str], timeout=10)
        if index == -1:
            strw = recode('设置环境变量失败')
            print strw
            work.writerunlog(strw)
            return ERROR_RT

        tn.read_very_eager()
        tn.write(savecmd + ENTER)
        uboot_str = 'uboot\s*#'
        uboot_str = re.compile(uboot_str, re.DOTALL | re.IGNORECASE)
        (index, match, data) = tn.expect([uboot_str], timeout=10)
        if index == -1:
            strw = recode('设置环境变量失败')
            print strw
            work.writerunlog(strw)
            return ERROR_RT

        return SUCCESS_RT
    except KeyboardInterrupt:
        strw = recode('程序执行到[app.save_file_to_flash]被手动终止')
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception,err:
        strw = recode('程序执行到[app.save_file_to_flash]异常退出!异常信息为%s'%err)
        print strw
        work.writerunlog(strw)
        return ERROR_RT

##根据config中的section安装相应的应用软件
#
#传递参数section,然后自动执行section中语句
def InstallSoftware(section):
    tn = globalvar.TN
    workdir = globalvar.LOG_DIR
    bootFile = os.path.join(workdir, 'InstallSoftware.log')

    strw = recode('开始烧录安装软件%s...' %section)
    print strw
    work.writerunlog(strw)

    cfginfos = globalvar.CFG_INFOS

    cmdnum = cfginfos[section]['cmdnum']
    for num in range(1, int(cmdnum)+1):
        idx = 'cmd' + str(num)
        cmd = cfginfos[section][idx]
        p1, p2 = '#', '>'
        pattern = [re.compile(p1, re.IGNORECASE | re.DOTALL), re.compile(p2, re.IGNORECASE | re.DOTALL)]
        if re.search('wget',cmd) or re.search('add application', cmd):
            times_sum = 3
            flag = True
            for i in range(1, times_sum+1):
                #输入Ctrl+C打断
                tn.write('\003' + ENTER)
                tn.read_very_eager()
                time.sleep(0.5)

                #首先删除之前的文件
                tn.read_very_eager()
                time.sleep(0.5)
                try:
                    cmd_del = 'rm -rf %s' % cmd.split('/')[-1]
                    tn.write(cmd_del + ENTER)
                    time.sleep(0.5)
                    (index, match, data) = tn.expect(pattern, timeout=60)
                    work.writecmdlog(data)
                    work.writelogtofile(bootFile, data)
                except:
                    pass

                #清除ARP表格
                ip_pattern = '@(\d+\.\d+\.\d+\.\d+)/'
                p = re.search(ip_pattern, cmd)
                if p:
                    tn.read_very_eager()
                    arp_cmd = 'arp -d %s' % p.group(1)
                    tn.write(arp_cmd + ENTER)
                    tn.expect(['#', '>'], timeout=10)
                else:
                    strw = recode('命令%s中ip格式有问题')
                    print strw
                    work.writerunlog(strw)
                    return ERROR_RT

                tn.read_very_eager()
                arp_cmd = 'arp -d %s' %cfginfos['IPINFO']['gateway_ip']
                tn.write(arp_cmd + ENTER)
                tn.expect(['#', '>'], timeout=10)

                #添加retry机制
                tn.read_very_eager()
                if i > 1:
                    time.sleep(5)
                else:
                    time.sleep(0.5)
                tn.write(cmd + ENTER)
                if i > 1:
                    time.sleep(5)
                else:
                    time.sleep(0.5)
                (index, match, data) = tn.expect(pattern, timeout=300)
                work.writecmdlog(data)
                work.writelogtofile(bootFile, data)

                str_match = '100\s*%'
                if re.search(str_match, data) is None:
                    flag = False
                    time.sleep(5)
                else:
                    flag = True
                    break

            if flag is False:
                strw = recode('命令%s执行失败,返回值没有匹配%s'% (cmd, str_match))
                print strw
                work.writerunlog(strw)
                return ERROR_RT
        else:
            tn.read_very_eager()
            time.sleep(0.5)
            tn.write(cmd + ENTER)
            time.sleep(0.5)
            (index, match, data) = tn.expect(pattern, timeout=600)
            work.writecmdlog(data)
            work.writelogtofile(bootFile, data)
            if index == -1:
                strw = recode('命令%s执行失败'%cmd)
                print strw
                work.writerunlog(strw)
                return ERROR_RT

    strw = recode('软件%s安装成功'%section)
    print strw
    work.writerunlog(strw)
    return SUCCESS_RT

##根据市场型号来烧录软件到flash中
#
#烧录软件到flash中
def dl_app_to_flash():
    tn = globalvar.TN
    workdir = globalvar.LOG_DIR

    strw = recode('开始烧录软件到flash...')
    print strw
    work.writerunlog(strw)

    getinfos = globalvar.getinfos
    part_number = getinfos['pn']
    if re.search('71', part_number):
        section = 'software_ver_71'
        if InstallSoftware(section) == ERROR_RT: return ERROR_RT
        if connection.ResetToLinux() == ERROR_RT: return ERROR_RT

    elif re.search('70', part_number):
        section = 'oceanpark'
        if InstallSoftware(section) == ERROR_RT: return ERROR_RT
        if connection.ResetToLinux() == ERROR_RT: return ERROR_RT
        if SetIP() == ERROR_RT: return ERROR_RT

        section = 'software_ver_70'
        if InstallSoftware(section) == ERROR_RT: return ERROR_RT
        if connection.ResetToLinux() == ERROR_RT: return ERROR_RT
    elif re.search('72', part_number):
        section = 'oceanpark'
        if InstallSoftware(section) == ERROR_RT: return ERROR_RT
        if connection.ResetToLinux() == ERROR_RT: return ERROR_RT
        if SetIP() == ERROR_RT: return ERROR_RT

        section = 'software_ver_72'
        if InstallSoftware(section) == ERROR_RT: return ERROR_RT
        if connection.ResetToLinux() == ERROR_RT: return ERROR_RT

    else:
        strw = recode('不支持的市场型号[%s]'%part_number)
        print strw
        work.writerunlog(strw)
        return ERROR_RT

    return SUCCESS_RT


## 写FRU
#
#  将相关FRU写入板卡并检查写入的信息是否正确
def checkFRU(tn, updatefru, item, board=''):
    """
    参数传递：       tn:           与板卡连接的通道
                    item:         表示要更新的是载板、扣板或者后IO的FRU信息;默认为载板
                    updatefru：   需要更新的FRU信息
    工作方式：       首先将fruinfos中的信息更新到板卡中fru_tmp这个文件中
    返回参数：       返回成功或者失败的结果
    """
    try:
        eptInfos = ''
        #首先通过item来辨别所需更新部件的fru信息
        if item == 'KOUBAN':
            # 需要更新的是扣板的fru信息
            cfginfos = globalvar.CFG_INFOS
            fruinfos = cfginfos['CPU_FRU']
            frucmd = globalvar.FRU_KOUBAN_CMD
            echotofile = 'N'
        elif item == 'ZAIBAN':
            # 需要更新的是载板的fru信息
            cfginfos = globalvar.CFG_INFOS
            fruinfos = cfginfos['FB_FRU']
            frucmd = globalvar.FRU_ZAIBAN_CMD
            echotofile = 'N'
        elif item == 'RTM':
            #需要更新的是后IO的fru信息
            cfginfos = globalvar.CFG_INFOS
            fruinfos = cfginfos['RTM_FRU']
            frucmd = globalvar.FRU_RTM_CMD
            echotofile = 'N'
            pass
        else:
            #上述都不是的出错处理
            strw = recode('未知的FRU类型，请检查！[目前支持：KOUBAN：扣板   ZAIBAN：载板   RTM：后IO]')
            print strw
            return ERROR_RT

        #将fruinfos和updatefru更新进板卡中，以fru_tmp的文件方式存在
        tn.write('shell' + ENTER)
        time.sleep(0.5)
        tn.write('cd /tmp' + ENTER)
        if echotofile == 'Y':
            FRU_FILE = globalvar.FRU_FILE
            cmd = 'rm -rf' + ' ' + FRU_FILE
            tn.write(cmd + ENTER)
            time.sleep(0.5)

        fruinfonum = len(fruinfos.keys())  # 获取命令的条目数
        for n in range(1, fruinfonum + 1):
            fruinfo = 'fru' + str(n)
            fru = fruinfos[fruinfo]
            if fru[:fru.find('=')] in updatefru.keys():
                fru = updatefru[fru[:fru.find('=')]]
            if fru.find(';') != -1:
                a = fru.count(';')
                fru = fru.replace(';', '\;', a)
            if fru.find('(') != -1:
                a = fru.count('(')
                fru = fru.replace('(', '\(', a)
            if fru.find(')') != -1:
                a = fru.count(')')
                fru = fru.replace(')', '\)', a)
            if fru.find('.') != -1:
                a = fru.count('.')
                fru = fru.replace('.', '\.', a)
            if fru.find('$') != -1:
                a = fru.count('$')
                fru = fru.replace('$', '\$', a)
            if fru.find('+') != -1:
                a = fru.count('+')
                fru = fru.replace('+', '\+', a)
            if echotofile == 'Y':
                cmd = 'echo %s >> %s' % (fru, FRU_FILE)
                rtstr = FRU_FILE + '\s*.+\/.+\s*.+#'
                rtstr = re.compile(rtstr, re.IGNORECASE | re.DOTALL)
                tn.write(cmd + ENTER)
                (index, match, data) = tn.expect([rtstr], timeout=60)
                work.writecmdlog(data)
                if index == -1:
                    strw = recode('更新FRU相关域失败！')
                    print strw
                    work.writerunlog(strw)
                    return ERROR_RT

            if fru.find(' ') != -1:
                a = fru.count(' ')
                fru = fru.replace(' ', '\s*', a)

            eptInfos = eptInfos + fru + '\s*'

        eptInfos = re.compile(eptInfos, re.IGNORECASE | re.DOTALL)
        # 更新fru并重新读取，并判别fru是否写入正确
        if item == 'RTM':
            import runconfig
            product = runconfig.product
            if product.upper() == 'FM1000':
                rcmd = frucmd + ' -r -n AM%s-fru' % board
            else:
                rcmd = frucmd + ' -r -n 10'
        else:
            rcmd = frucmd + ' -r'
        tn.write(rcmd + ENTER)
        (index, match, data) = tn.expect([eptInfos], timeout=60)
        work.writecmdlog(data)
        if index == -1:
            tn.write(rcmd + ENTER)
            (index, match, data) = tn.expect([eptInfos], timeout=60)
            work.writecmdlog(data)
            if index == -1:
                strw = recode('更新FRU信息失败！')
                print strw
                work.writerunlog(strw)
                return ERROR_RT
            else:
                strw = recode('FRU检查通过.')
                print recode('************************')
                print strw
                print recode('*********************************************************************')
                work.writerunlog(strw)
        else:
            strw = recode('FRU检查通过.')
            print '*********************************************************************'
            print strw
            print '*********************************************************************'
            work.writerunlog(strw)

        if echotofile == 'Y':
            cmd = 'rm -rf' + ' ' + FRU_FILE
            tn.write(cmd + ENTER)
            tn.write('exit' + ENTER)

        # 配置完成，返回结果SUCCESS_RT
        return SUCCESS_RT

    except KeyboardInterrupt:
        strw = recode('程序执行到[app.updateFRU]被手动终止')
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[app.updateFRU]异常退出!异常信息为%s' % err)
        print strw
        work.writerunlog(strw)
        return ERROR_RT


def ShowSelf():
    tn = globalvar.TN
    cmd = 'cat /tmp/cpu_type'
    tn.write(cmd + ENTER)
    #tn.expect(['#'], timeout=5)
    return SUCCESS_RT


def check_board_time():
    """
    输入:     tn      连接通道
    返回:     SUCCESS_RT  版本正确
              ERROR_RT    版本错误
    """
    try:
        tn = globalvar.TN
        flag = True
        dirValue = globalvar.LOG_DIR
        bootFile = os.path.join(dirValue, 'check_board_time.log')

        month = {'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06','Jul':'07', \
            'Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}

        #开始检查板卡时间
        seconds = time.time()
        cmd = 'show clock'
        clistr = '#'
        clistr = re.compile(clistr, re.DOTALL | re.IGNORECASE)
        tn.read_very_eager()
        tn.write(cmd + ENTER)
        (index, match, data) = tn.expect([clistr], timeout=10)
        work.writecmdlog(data)
        work.writelogtofile(bootFile, data)
        if index == -1:
            strw = recode('获取板卡时间信息返回值失败')
            print strw
            work.writerunlog(strw)
            flag = False
        else:
            # 10:05:36 UTC Thu Nov 24 2016
            pattern = '(\d+):(\d+):(\d+)\s\w+\s+\w+\s+(\w+)\s+(\d+)\s+(\d+)'
            s = re.search(pattern, data)
            if s != None:
                #print s.group(5)
                day = s.group(5)
                if len(day) == 1:
                    day = '0%s' % day
                rtc = '%s-%s-%s %s:%s:%s' %(s.group(6),month[s.group(4)],day,s.group(1),s.group(2),s.group(3))
                print rtc
            else:
                strw = recode('获取板卡时间失败')
                print strw
                work.writerunlog(strw)
                return ERROR_RT

            tmp = re.findall(r'(\d+-\d+-\d+\s*\d+:\d+:\d+)', rtc)
            if len(tmp) == 0:
                strw = recode('解析板卡时间失败')
                print strw
                work.writerunlog(strw)
                flag = False
            else:
                board_time = tmp[0]

                if '1970-01-01' in board_time:
                    strw = recode('板卡时间比对失败!')
                    print strw
                    work.writerunlog(strw)
                    return ERROR_RT

                tmpSeconds = time.mktime(time.strptime(board_time, '%Y-%m-%d %H:%M:%S'))
                result = int(seconds) - int(tmpSeconds)
                if -600 <= result <= 600:
                    strw = recode('设备时间正确.')
                    print strw
                    work.writerunlog(strw)
                else:
                    strw = recode('板卡时间比对失败!')
                    print strw
                    work.writerunlog(strw)
                    flag = False

        if not flag:
            return ERROR_RT
        return SUCCESS_RT

    except KeyboardInterrupt:
        strw = recode('程序执行到[app.check_board_time]被手动终止')
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception,err:
        strw = recode('程序执行到[app.check_board_time]异常退出!异常信息为%s'%err)
        print strw
        work.writerunlog(strw)
        return ERROR_RT


def read_temp():
    try:
        loginfos = globalvar.loginfos
        tn = globalvar.TN
        f_name = sys._getframe().f_code.co_name
        dirValue = globalvar.LOG_DIR
        logfile = os.path.join(dirValue, '%s.log')%f_name
        data_log = ''
        flag = 'PASS'


        cmd0 = 'i2cget -y 0 0x4A 0x0'
        cmd1 = 'i2cget -y 0 0x4B 0x0'
        cmd_list = [cmd0,cmd1]
        for cmd in cmd_list:
            p = cmd+'.+'+'$'
            pattern = [re.compile(p, re.IGNORECASE | re.DOTALL)]
            for i in cmd:
                tn.write(i)
                time.sleep(0.05)
            tn.write(ENTER)
            time.sleep(0.5)
            (index, match, data) = tn.expect(pattern, timeout=60)
            data_log = data_log + data
            print data
            work.writecmdlog(data)
            work.writelogtofile(logfile, data)
            if index == -1:
                strw = recode('命令%s执行失败'%cmd)
                print strw
                work.writerunlog(strw)
                flag = 'FAIL'

            pattern = '0x\S\S'
            pattern = re.compile(pattern, re.DOTALL | re.IGNORECASE)
            p = re.findall(pattern, data)
            if p:
                print p[1]
                temp = int(p[1],16)
            else:
                strw = recode('温度读取失败')
                print strw
                work.writerunlog(strw)
                flag = 'FAIL'

            if temp >= 20 and temp <= 70:
                strw = recode('温度在合理范围内')
                print strw
                work.writerunlog(strw)
            else:
                flag = 'FAIL'
                strw = recode('温度不在合理范围内')
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