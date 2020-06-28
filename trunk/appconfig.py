#!/usr/bin/env python
# This Python file uses the following encoding: utf-8

# @package appconfig
# 功能：定义一些常见的功能测试模块
#
# 作者：MA.chunqiang
#
# 日期：2016-07-25
#
# 文件：appconfig.py

# import system modules
import sys
import os
import time
import re

# import our modules
import work                 # 写日志，以及上传到ftp的相关函数
import connection           # 登陆板卡的一些函数，以及在板卡上切换工作路径的函数
import tcplib               # 与autotool通信的函数
import app                  # 通用的功能函数，比如：写FRU，获取序列号等
import globalvar            # 一些全局变量
import runconfig
from work import recode     # 从work那边获取recode
import command


# 获取相关的全局变量
#
# 将本地的全局变量都指向到globalvar中全局变量
ENCODE_TYPE = globalvar.ENCODE_TYPE     # 文件默认的系统编码
ERROR_RT = globalvar.ERROR_RT           # 错误返回值
SUCCESS_RT = globalvar.SUCCESS_RT       # 成功返回值
OTHER_ERROR = globalvar.OTHER_ERROR     # 其他错误返回值
DEBUGMODE = globalvar.DEBUGMODE         # debug模式开关
ENTER = globalvar.ENTER                 # 回车符重定义

## app模块相关特殊变量设置


# 获取所有输入的SN信息
def GetSerialNumInfos():
    # return SUCCESS_RT
    """
    Get All Input SerialNum Infos
    """
    cfginfos = globalvar.CFG_INFOS
    getinfos = dict()
    import runconfig
    product = runconfig.product
    station = runconfig.station
    mode = globalvar.MODE
    cfg_ps = ''

    id = globalvar.ID
    #获取autoTool传递过来的相关参数，并赋值。并更新cfginfos
    #从global处获取所有需要的SN list；每次新产品的脚本都需要修改
    if product.upper() == 'VX3100':
        if station.upper() == 'PRD':
            snlist = globalvar.ES6200prd_snlist
        else:
            snlist = globalvar.ES6200outqc_snlist
    else:
        return ERROR_RT
    #获取上述需要的条码
    print globalvar.debug_mode
    if globalvar.debug_mode==False:
        getinfos = {'ps': 'Q07H4340001', 'bn': '6000-142102', 'pn': '7516-029701',
                    'bs': '423G4310007', 'mac': '00:09:06:12:34:56'}
        pninfo = {'_board_version': '0x1', 'BN': 'VX3100', 'product_version': '01',
                 '_major_board_type': '0x4728', 'PN': 'VX3100-101', '_minor_board_type': '0x1ff'}
    else:
        (getinfos, pninfo) = app.autotoolGetInputInfos(id, snlist)
        if getinfos == ERROR_RT or getinfos == OTHER_ERROR:
            tcplib.SendStatusMsg(id, 'FAIL-获取输入信息失败！')
            return ERROR_RT

        cfg_ps = getinfos['ps']
        if 'ps2' in getinfos.keys():
            cfg_ps = cfg_ps + '-' + getinfos['ps2']

    #update globalval.CFG_INFOS
    cfginfos['SETTING']['ps'] = cfg_ps
    globalvar.CFG_INFOS = cfginfos
    globalvar.getinfos = getinfos
    globalvar.pninfo = pninfo

    print recode('获取pninfo和bninfo信息成功')
    return SUCCESS_RT


# connect to board
def ConnectToBoard():
    """
    connect to board and update tn
    """
    cfginfos = globalvar.CFG_INFOS
    csip = cfginfos['SETTING']['cs_ip']
    csport = cfginfos['SETTING']['cs_port']
    tn = connection.TelnetServer(csip, csport)
    if tn == ERROR_RT or tn == OTHER_ERROR:
        strw = recode('FAIL - 登陆板卡失败!')
        print strw
        work.writerunlog(strw)
        return ERROR_RT

    globalvar.TN = tn
    if app.RecordConsolePrint(csip, csport) == ERROR_RT:
        strw = recode('启动串口监控线程失败')
        print strw
        work.writerunlog(strw)
        globalvar.Console_print_detect = 'stop'
        return ERROR_RT

    return SUCCESS_RT

def ConnectToNps():
    try:
        cfginfos = globalvar.CFG_INFOS
        f_name = sys._getframe().f_code.co_name
        nps_ip = cfginfos['NPSINFO']['nps_ip']
        nps_port = cfginfos['NPSINFO']['nps_port']
        nps_tn = connection.TelnetServer(nps_ip, nps_port)
        print nps_tn
        if nps_tn == ERROR_RT or nps_tn == OTHER_ERROR:
            strw = recode('FAIL - 登陆NPS失败!')
            print strw
            work.writerunlog(strw)
            return ERROR_RT

        globalvar.NPS_TN = nps_tn
        # if app.RecordConsolePrint(nps_tn, nps_port) == ERROR_RT:
        #     strw = recode('启动NPS串口监控线程失败')
        #     print strw
        #     work.writerunlog(strw)
        #     globalvar.Console_print_detect = 'stop'
        #     return ERROR_RT


        return SUCCESS_RT

    except KeyboardInterrupt:
        strw = recode('程序执行到[%s]被手动终止'%f_name)
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[%s]异常退出!异常信息为%s' % (f_name,err))
        print strw
        work.writerunlog(strw)
        return ERROR_RT




def ConnectToTelnet1():
    """
    connect to board and update tn
    """
    cfginfos = globalvar.CFG_INFOS
    csip = globalvar.IP
    #csip = '192.168.33.101'
    csport = '23'
    tn1 = connection.TelnetServer(csip, csport)
    if tn1 == ERROR_RT or tn1 == OTHER_ERROR:
        strw = recode('FAIL - 登陆板卡失败!')
        print strw
        work.writerunlog(strw)
        return ERROR_RT

    globalvar.tn1 = tn1
    if app.RecordConsolePrint(csip, csport) == ERROR_RT:
        strw = recode('启动串口监控线程失败')
        print strw
        work.writerunlog(strw)
        globalvar.Console_print_detect = 'stop'
        return ERROR_RT

    return SUCCESS_RT


# connect to board and goto shell prompt
def ConnectToShell():
    """
    connect to board and update tn
    """
    cfginfos = globalvar.CFG_INFOS
    csip = cfginfos['SETTING']['cs_ip']
    csport = cfginfos['SETTING']['cs_port']
    tn = connection.TelnetToShell(csip, csport)
    if tn == ERROR_RT or tn == OTHER_ERROR:
        strw = recode('FAIL - 登陆板卡失败!')
        print strw
        work.writerunlog(strw)
        return ERROR_RT

    globalvar.TN = tn
    if app.RecordConsolePrint(csip, csport) == ERROR_RT:
        strw = recode('启动串口监控线程失败')
        print strw
        work.writerunlog(strw)
        globalvar.Console_print_detect = 'stop'
        return ERROR_RT

    return SUCCESS_RT

def ParseFruData(data):
    fru_dict = {
        'Device Version'    :'',
        'MAC Addresses'    :'',
        'Manufacture Date':'',
        'Serial Number'     :'',
        'Base MAC Address':'',
        'Product Name'       :'',
        'Platform Name'      :''
    }    
    read_dict = {}
    for key in fru_dict.keys():
        pattern = key + '\s+0x[0-9A-Z]{2}\s+\d{1,2}(.+)\n'
        p = re.search(pattern, data)
        if p == None :return ERROR_RT
        
        read_dict[key] = p.group(1).strip()
    return read_dict

# update FRU infos
def UpdateFRU():
    try:
        loginfos = globalvar.loginfos
        tn = globalvar.TN
        f_name = sys._getframe().f_code.co_name
        dirValue = globalvar.LOG_DIR
        logfile = os.path.join(dirValue, '%s.log')%f_name
        data_log = ''
        flag = 'PASS'
        getinfos = globalvar.getinfos

        if globalvar.BOARD_TYPE == 'YES':
            # get infos
            product = runconfig.product

            connection.Gotoshell()

            now_time = '"' + time.strftime('%m/%d/%Y %H:%M:%S') + '"'

            cmd_list = [
                'onie-syseeprom -s 0x21=HW-VX3100A4',                    
                'onie-syseeprom -s 0x2a=32',                            
                'onie-syseeprom -s 0x28=2H-CTC5160-26x1Q',                          
                'onie-syseeprom -s 0x25=%s'%now_time,                    
                'onie-syseeprom -s 0x23=%s'%getinfos['ps'],                        
                'onie-syseeprom -s 0x24=%s'%getinfos['mac'],                      
            ]
            for cmd in cmd_list:
                pattern, timeout = '$', 10
                data = command.CmdGet(tn, cmd, [pattern], timeout)
                data_log = data_log + data
                work.writelogtofile(logfile, data)
                if data == ERROR_RT: 
                    flag = 'FAIL'

            tn.read_very_eager()
            tn.write(ENTER)
            tn.expect(['$'],5)
            fru_list = [
                'Product Name         0x21  12 HW-VX3100A3',
                'MAC Addresses        0x2A   2 32',
                'Platform Name        0x28  26 2H-CTC5160-25x1Q',
                'Serial Number        0x23  11 %s'%getinfos['ps'],
                'Base MAC Address     0x24   6 %s'%getinfos['mac'],
            ]
            print getinfos['mac']
            cmd = 'onie-syseeprom'
            pattern = 'Checksum is valid'
            data = command.CmdGet(tn, cmd, [pattern], timeout)
            print data
            data_log = data_log + data
            work.writelogtofile(logfile, data)
            if data == ERROR_RT:
                strw = recode('读取fru信息失败')
                print strw
                work.writerunlog(strw)
                flag = 'FAIL'

            for pattern in fru_list:
                p = re.search(pattern, data)
                if p:
                    strw = recode('更新FRU %s信息成功'%pattern)
                    print strw
                    work.writerunlog(strw)       
                else:
                    strw = recode('更新FRU %s信息成功'%pattern)
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
        strw = recode('程序执行到[%s]被手动终止'%f_name)
        print strw
        work.writerunlog(strw)
        return OTHER_ERROR
    except Exception, err:
        strw = recode('程序执行到[%s]异常退出!异常信息为%s' % (f_name,err))
        print strw
        work.writerunlog(strw)
        return ERROR_RT

