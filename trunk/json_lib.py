#!/usr/bin/env python
# This Python file uses the following encoding: utf-8

import sys
import json
import os

ENCODE_TYPE = sys.getfilesystemencoding()

#获取脚本文件的当前路径
def cur_file_dir():
    path = sys.path[0]
    if os.path.isdir(path):
        return path
    if os.path.isfile(path):
        return os.path.dirname(path)

def recode(strw):
    return strw.decode('UTF-8').encode(ENCODE_TYPE)
    

def GenerateDataBaseInfos():
    '''构建测试用数据库内容'''
    databaseinfos  = {}
    tesetinfos       = {}
    functioninfos   = {}
    macinfos        = {}

    recordinfos = {
        'Result1ID'         :    '1',
        'Project'             :    'OceanwayII',
        'BoardName'       :    'AC2820A3',
        'PS'                   :    'N42H5130002',
        'Station'             :    'PRD',
        'FromTime'         :    '2015/7/22 20:11:00',
        'ToTime'             :    '2015/7/22 20:15:00',
        'Duration'           :    '4:25',
        'ResultDesc'        :    'PASS'
    }

    tesetinfos['record'] = recordinfos

    functionsinfos = {}
    function_list = ['WriteFru', 'DiagEth', 'ac_withstand_voltage_check', 'SendpktTest', 'LedTest', 'ResetTest', 'ButtonTest']
    id = 1
    for function in function_list:
        function_key = 'function' + str(id)
        flag = 'PASS'
        tmpinfos = {}
        tmpinfos['name']        = function
        tmpinfos['flag']          = flag
        tmpinfos['Result1ID']  = '1'
        functioninfos[function_key] = tmpinfos
        id = id + 1

    loginfos = {}
    data='123'
    loginfos['ac_withstand_voltage_check'] = data

    macinfos = {}
    mac_list = ['000906123456', '000906123457']
    id = 1
    for mac in mac_list:
        keyx = 'mac' + str(id)
        macinfos[keyx] = mac
        id = id + 1


    databaseinfos['test']          =   tesetinfos
    databaseinfos['function']    =   functioninfos
    databaseinfos['mac']         =    macinfos
    databaseinfos['log']         =   loginfos

    return databaseinfos

    
def WriteDataToJson(databaseinfos, database_file_name):
    path = 'D:\\database'
    if os.path.exists(path) == False:
        os.mkdir(path)
    file_path = os.path.join(path, database_file_name)
    data = json.dumps(databaseinfos, indent=4)
    with open(file_path, 'w') as f:
        f.write(data)
    
def test():
    name = 'N10A4567890_QC_201406091904_PASS.json'
    databaseinfos = GenerateDataBaseInfos()
    WriteDataToJson(databaseinfos, name)

if __name__ == '__main__':
    test()