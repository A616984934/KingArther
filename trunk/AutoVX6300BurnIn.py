#!/usr/bin/env python
# This Python file uses the following encoding: utf-8
#
# @package autoSF4800
# 功能：自动化测试脚本主模块，定义main函数调用其他模块提供的测试接口并启动整个程序.
#
# 作者：Ma.chunqiang.
#
# 日期：2016-07-25.
#
# 文件：main.py

# import public module, such as: os, sys.
import os
import sys
import re
import time

# import private module
from work import recode
import globalvar
import runconfig
import work
import check
import tcplib
import app
import json_lib
# import sys
# sys.path.append(r'E:\SVN\automationtest\CodeLib\recordtime')
# import record_time

# 将本地的全局变量都指向到globalvar中全局变量
ENCODE_TYPE = globalvar.ENCODE_TYPE     # 文件默认的系统编码
ERROR_RT = globalvar.ERROR_RT           # 错误返回值
SUCCESS_RT = globalvar.SUCCESS_RT       # 成功返回值
OTHER_ERROR = globalvar.OTHER_ERROR     # 其他错误返回值
DEBUGMODE = globalvar.DEBUGMODE         # debug模式开关
ENTER = globalvar.ENTER                 # 回车符重定义
databaseinfos = globalvar.DATABASE_INFOS

# 获取当前文件所在文件夹路径.
#
# 通过sys.path[0]判断并返回当前文件所在文件夹路径.
def cur_file_dir():
    path = sys.path[0]
    if os.path.isdir(path):
        return path
    if os.path.isfile(path):
        return os.path.dirname(path)

## show fail
def show_fail_info(strw):
    tn = globalvar.TN
    # 用来传递给串口记录程序结束使用
    globalvar.Console_print_detect = 'stop'
    mode = globalvar.MODE
    strW = recode(strw)
    print strW
    work.writerunlog(strW)
    work.UploadLogDir()
    if mode == 'AUTOTOOL':
        id = globalvar.ID
        tcplib.SendStatusMsg(id, strw)
    return

# project entrance
def main():
    try:
        # 初始化一些后续使用的变量
        csip = ''
        csport = ''
        id = ''

        #通过判断函数带的参数数量来得到启动模式,并赋值给全局变量MODE
        # 5: AUTOTOOL     1: CMD
        print sys.argv
        if len(sys.argv) != 5 and len(sys.argv) != 1:
            print ( recode('程序启动参数数量有误！'))
            return
        elif len(sys.argv) == 1:
            mode = 'CMD'
            globalvar.TOP_LOG_FOLDER_NAME = 'logdir'
        else:
            mode = 'AUTOTOOL'
            globalvar.TOP_LOG_FOLDER_NAME = sys.argv[1]
            csip = sys.argv[2]
            csport = sys.argv[3]
            id = sys.argv[4]
        # 得到config文件的路径，并且赋值给全局变量CONFIG
        config = globalvar.CONFIG
        config = os.path.join(cur_file_dir(), config)

        # 将当前的变量传递给globalvar
        globalvar.MODE = mode
        globalvar.CONFIG = config
        globalvar.ID = id

        name = sys.argv[0]
        #pattern = '\.py'
        #if re.search(pattern, name):
        #    globalvar.debug_mode = True
        #else:
        #    globalvar.debug_mode = False

        # 开始创建log文件夹
        if not work.MakeLogDir() == SUCCESS_RT:
            strW = recode('创建测试log文件夹失败，请检查!')
            print strW
            return

        # 获取config文件内容
        if not check.cfg_parser() == SUCCESS_RT:
            strW = recode('获取config文件内容失败，请检查!')
            print strW
            return

        # 更新cfginfos中内容
        cfginfos = globalvar.CFG_INFOS
        if mode == 'AUTOTOOL':
            cfginfos['SETTING']['cs_ip'] = csip
            cfginfos['SETTING']['cs_port'] = csport
        if 'ps' not in cfginfos['SETTING'].keys():
            cfginfos['SETTING']['ps'] = cfginfos['SETTING']['cs_port']

        globalvar.CFG_INFOS = cfginfos

        # 获取当前激活的config配置信息
        station = runconfig.station
        product = runconfig.product
        test_configs = runconfig.test_configs
        test_key = '%s%s' % (product, station)
        if not test_configs.has_key(test_key):
            strW = recode('测试配置[%s]不在runconfig中的test_configs中,请检查!'%test_key)
            print strW
            work.writerunlog(strW)
            work.UploadLogDir()
            return

        import datetime
        globalvar.test_start_time = time.strftime('%Y-%m-%d %H:%M:%S')
        globalvar.datetime_start_time = datetime.datetime.now()

        # 开始测试

        if station.upper() != 'BURNIN':
            test_fail_flag = False
            f_name_list = []
            for func in test_configs[test_key]:
                f_name = func.__name__
                f_name = f_name.lower()
                f_name_list.append(f_name)
                
            cfginfos['f_name_list'] = f_name_list
            globalvar.CFG_INFOS = cfginfos 

            test_flag = 'PASS'
            functionsinfos = {}
            num = 1 

            for func in test_configs[test_key]:
                flag = 'PASS'
                f_name = func.__name__
                f_name = f_name.lower()
                function_key = 'function' + str(num)
                if f_name in cfginfos['MODE']:
                    if cfginfos['MODE'][f_name] == '0':
                        continue
                if func() != SUCCESS_RT:
                    test_fail_flag = True
                    if globalvar.debug_mode:
                        strw = recode('========== 函数%s返回值为ERROR_RT ===========' %f_name)
                        print strw
                        flag = 'FAIL'
                    else:
                        show_fail_info('FAIL-Test[%s]失败' %func.__name__)
                        flag = 'FAIL'
                        return

                tmpinfos = {}
                tmpinfos['name'] = f_name
                tmpinfos['flag'] = flag
                tmpinfos['Result1ID'] = '1'
                functionsinfos[function_key] = tmpinfos
                num = num + 1
                if flag == 'FAIL':
                    test_flag = 'FAIL'
                if test_flag == 'FAIL':
                    break

            databaseinfos['function'] = functionsinfos
            databaseinfos['log'] = globalvar.loginfos
            globalvar.DATABASE_INFOS = databaseinfos

            globalvar.test_end_time = time.strftime('%Y-%m-%d %H:%M:%S')
            globalvar.datetime_end_time = datetime.datetime.now()
            globalvar.duration = '%s' % str((globalvar.datetime_end_time - globalvar.datetime_start_time).seconds)

            getinfos = globalvar.getinfos
            tesetinfos = {}
            recordinfos = []
            recordinfos = {
                'Result1ID'         :    '1',
                'Project'             :    'ES6200',
                'BoardName'       :    globalvar.BOARD_TYPE,
                'PS'                   :    getinfos['ps'],
                'Station'             :    globalvar.STATION,
                'FromTime'         :    globalvar.test_start_time,
                'ToTime'             :    globalvar.test_end_time,
                'Duration'           :    globalvar.duration,
                'ResultDesc'        :    test_flag
            }
            tesetinfos['record'] = recordinfos
            databaseinfos['test'] = tesetinfos

            macinfos = {}        
            mac_list = [getinfos['mac']]
            num = 1
            for mac in mac_list:
                keyx = 'mac' + str(num)
                macinfos[keyx] = mac
                num = num + 1
            databaseinfos['mac'] = macinfos

            globalvar.DATABASE_INFOS = databaseinfos

            database_file_name = getinfos['ps'] + '_' + station + '_' + time.strftime('%Y%m%d%H%M%S') + '_' + test_flag + '.json'
            strw = recode('正在上传数据库文件%s....'%database_file_name)
            print strw
            work.writerunlog(strw)
            try:
                json_lib.WriteDataToJson(databaseinfos, database_file_name)
            except Exception,err:
                strw = recode('程序执行到[main]异常退出!异常信息为%s'%err)
    
            strw = recode('上传数据库文件%s成功'%database_file_name)
            print strw
            work.writerunlog(strw)

            if test_flag == 'FAIL':
                show_fail_info('FAIL-Test')
                return 

        else:
            # 当为拷机的时候，需要进行特殊处理
            run_mode = app.select_burnin_mode()
            globalvar.burnin_mode = run_mode
            if run_mode == 'A' or run_mode == '1':
                # 开始数据拷机
                f_name_list = []
                for func in test_configs[test_key]['data']:
                    f_name = func.__name__
                    f_name = f_name.lower()
                    f_name_list.append(f_name)

                    cfginfos['f_name_list'] = f_name_list
                    globalvar.CFG_INFOS = cfginfos

                    test_flag = 'PASS'
                    functionsinfos = {}
                    num = 1

                for func in test_configs[test_key]['data']:
                    flag = 'PASS'
                    f_name = func.__name__
                    function_key = 'function' + str(num)
                    # func = record_time.record_time(func)

                    if func() != SUCCESS_RT:
                        if globalvar.debug_mode:
                            strw = recode('========== 函数%s返回值为ERROR_RT ===========' %f_name)
                            print strw
                            flag = 'FAIL'
                        else:
                            show_fail_info('FAIL-Test[%s]失败' %func.__name__)
                            flag = 'FAIL'
                            return

                    # 切换回默认的串口设置
                    # 此处只是用来做演示，实际使用过程中还需要必要的设置
                    # globalvar.TN = tn

                    tmpinfos = {}
                    tmpinfos['name'] = f_name
                    tmpinfos['flag'] = flag
                    tmpinfos['Result1ID'] = '1'
                    functionsinfos[function_key] = tmpinfos
                    num = num + 1
                    if flag == 'FAIL':
                        test_flag = 'FAIL'
                    if test_flag == 'FAIL':
                        break

                databaseinfos['function'] = functionsinfos
                databaseinfos['log'] = globalvar.loginfos
                globalvar.DATABASE_INFOS = databaseinfos

                globalvar.test_end_time = time.strftime('%Y-%m-%d %H:%M:%S')
                globalvar.datetime_end_time = datetime.datetime.now()
                globalvar.duration = '%s' % str((globalvar.datetime_end_time - globalvar.datetime_start_time).seconds)

                getinfos = globalvar.getinfos
                tesetinfos = {}
                recordinfos = []
                recordinfos = {
                    'Result1ID'         :    '1',
                    'Project'             :    globalvar.boardtype,
                    'BoardName'       :    globalvar.BOARD_TYPE,
                    'PS'                   :    globalvar.PS,
                    'Station'             :    station,
                    'FromTime'         :    globalvar.test_start_time,
                    'ToTime'             :    globalvar.test_end_time,
                    'Duration'           :    globalvar.duration,
                    'ResultDesc'        :    test_flag
                }
                tesetinfos['record'] = recordinfos
                databaseinfos['test'] = tesetinfos

                macinfos = {}
                getinfos['mac'] = globalvar.MAC
                mac_list = [getinfos['mac']]
                num = 1
                for mac in mac_list:
                    keyx = 'mac' + str(num)
                    macinfos[keyx] = mac
                    num = num + 1
                databaseinfos['mac'] = macinfos

                globalvar.DATABASE_INFOS = databaseinfos
                database_file_name = globalvar.PS + '_' + station + '_' + time.strftime('%Y%m%d%H%M%S') + '_' + test_flag + '.json'
                strw = recode('正在上传数据库文件%s....'%database_file_name)
                print strw
                work.writerunlog(strw)
                try:
                    json_lib.WriteDataToJson(databaseinfos, database_file_name)
                except Exception,err:
                    strw = recode('程序执行到[writedatatodatabase]异常退出!异常信息为%s'%err)
                    #print strw
                    #work.writerunlog(strw)

                strw = recode('上传数据库文件%s成功'%database_file_name)
                print strw
                work.writerunlog(strw)

                strw = recode('数据拷机测试通过')
                print strw
                work.writerunlog(strw)

                if test_flag == 'FAIL':
                    show_fail_info('FAIL-Test')
                    return 

            if run_mode == 'A' or run_mode == '2':
                globalvar.diag_mem = False
                for func in test_configs[test_key]['reboot']:
                    if func() != SUCCESS_RT:
                        show_fail_info('FAIL-Test[%s]失败' % func.__name__)
                        return
                strW = recode('Reboot拷机测试通过!')
                print strW
                work.writerunlog(strW)
            if run_mode == 'A' or run_mode == '3':
                globalvar.diag_mem = False
                if cfginfos['BURNIN_CONTROL']['auto_powercycle'] == 'Y' or run_mode == '3':
                    for func in test_configs[test_key]['powercycle']:
                        if func() != SUCCESS_RT:
                            show_fail_info('FAIL-Test[%s]失败' % func.__name__)
                            return
                    strW = recode('PowerCycle重启拷机测试通过!')
                    print strW
                    work.writerunlog(strW)

            if run_mode == 'A' or run_mode == '4':
                globalvar.diag_mem = False
                # 开始烧录出货软件
                kw = 'AutoDownloadCustImage'
                kw = kw.lower()
                if cfginfos['BURNIN_CONTROL'][kw] == 'Y' or run_mode == '4':
                    for func in test_configs[test_key]['DL_IMG']:
                        if func() != SUCCESS_RT:
                            show_fail_info('FAIL-Test[%s]失败' % func.__name__)
                            return
                    strW = recode('下载出货软件通过!')
                    print strW
                    work.writerunlog(strW)

        # close all connection
        app.close_all_connection()

        # upload log
        if work.UploadLogDir(True) != SUCCESS_RT:
            if mode == 'AUTOTOOL':
                tcplib.SendStatusMsg(id, 'FAIL-上传测试log失败！')
                return

        # add for end
        if mode != 'CMD':
            tcplib.SendStatusMsg(id, 'PASS')
            return

    except KeyboardInterrupt:
        strw = recode('程序执行中断!')
        print strw
        return

#    except Exception, e:
#        print e
#        return
#
#    finally:
#        pass
#

# the whole project entrance
if __name__ == '__main__':
    main()
