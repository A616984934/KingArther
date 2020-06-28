#!/usr/bin/env python
# This Python file uses the following encoding: utf-8

# @package AutoTest
# 功能：主要用来配置整个脚本如何运行，运行哪些测试item的脚本.
#
# 作者：Ma.chunqiang
#
# 日期：2015-09-21
#
# 文件：runconfig.py

# import private module
import app
import appconfig
import globalvar
import special
import connection

# 定义当前激活的相关信息
station = 'BurnIn'  # 站别信息，包括:Prd(生产),BurnIn(拷机),outQC(出货)
product = 'VX6300'  # 产品名称，包括VX3100
globalvar.STATION = station

# 详细配置信息
test_configs = dict()

## VX3100_PreTest
VX6300Prd_version = 'V1.0.0'  # 修改版本信息
VX6300Prd_name = 'VX6300PreTest'  # 修改项目名称
VX6300Prd_description = 'VX6300 PreTest Script'  # 修改项目描述
test_configs['VX6300Prd'] = [
    appconfig.GetSerialNumInfos,  # 获取输入的SN相关信息
    app.get_board_type,  # 分析板卡硬件类型
    appconfig.ConnectToBoard,  # 登陆到板卡
    connection.ListenAndGotoUboot,   # 进入Pmon界面  TODO 检查mtd1
    special.Downloadpmon,            # 下载PMON文件
    special.ClearFlash,              # 擦除flash
    connection.BootAndGotoLinux,     # 重启板卡并进入linux界面
    connection.ListenAndGotoLinux,  # 进入linux界面
    appconfig.UpdateFRU,  # 升级FRU
    app.PingEth,  # ping
    special.DownloadLinuxFile,       # 下载版本文件
    special.CopylinuxFile,           # 备份镜像文件
    connection.ListenAndGotoLinux,   # 进入linux界面
    special.RestorePartition,  # 恢复默认分区
    app.download_files,  # 下载diag包
    special.SetOEMInformation,  # 设置OEM信息
    app.check_version,  # 检查相关版本信息
    special.read_temp,  # 读取温度测试
    special.check_memtester,  # 测试内存
    special.diag_all_i2c,  # 测试i2c
    special.CheckPacketTest,  # check packet
    special.CheckNetPortTest,  # check packet
    app.check_all_led,  # check all led
    app.close_all_connection  # 断开所有连接
]

## VX3100_BurnIn
VX6300BurnIn_version = 'V0.0.1'  # 修改版本信息
VX6300BurnIn_name = 'VX6300_BurnIn'  # 修改项目名称
VX6300BurnIn_description = 'VX6300 BurnIn Script'  # 修改项目描述
test_configs['VX6300BurnIn'] = dict()
test_configs['VX6300BurnIn']['data'] = [
    appconfig.ConnectToBoard,               # 登陆到板卡

    app.get_fru_info,                       # 获取产品FRU相关信息
    app.set_iophy,                          # 前3个电口（IO上3个口）phy层打环
    app.get_fru_info,                       # 再次连接到switch#中去
    special.StartPacketTestBurnIn,          # start packet
    special.BurninWait,                     # 拷机时间
    special.CheckPacketTestBurnIn,          # check packet
    special.sleep_time,                     # 高温到低温静置时间
    app.reboot_all_dut,                     # 重启并检查port mac
    appconfig.ConnectToNps,                 # 连接到NPS
    special.lowtemp_sleep,                  # powercycle 关机并等待时间后开机
    connection.lowtemp_gotolinuxcheckport,  # 检查port mac
    app.close_all_connection                # 断开所有连接
]

test_configs['VX6300BurnIn']['reboot'] = [
    appconfig.ConnectToBoard,  # 登陆到板卡
    connection.ListenAndGotoLinux,  # 进入linux界面
    #app.get_fru_info,               # 获取产品FRU相关信息
    #app.get_board_type,             # 获取板卡类型
    app.reboot_all_dut,  # 开始reboot
    app.close_all_connection  # 断开所有连接
]
test_configs['VX6300BurnIn']['powercycle'] = [
    appconfig.ConnectToShell,  # 登陆板卡，并进去shell界面
    app.close_all_connection  # 断开所有连接
]

test_configs['VX6300BurnIn']['DL_IMG'] = [
    appconfig.ConnectToShell,  # 登陆板卡，并进去shell界面
    app.close_all_connection  # 断开所有连接
]

## VX3100_outQC
VX6300outQC_version = 'V0.8.0'  # 修改版本信息
VX6300outQC_name = 'VX6300outQC'  # 修改项目名称
VX6300outQC_description = 'VX6300 outQC Script'  # 修改项目描述
test_configs['VX6300outQC'] = [
    app.close_all_connection  # 断开所有连接
]

# 定义版本信息
# note: 此处必须要放在最后
version = locals()['%s%s_version' % (product, station)]
name = locals()['%s%s_name' % (product, station)]
description = locals()['%s%s_description' % (product, station)]
