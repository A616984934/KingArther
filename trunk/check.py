#!/usr/bin/env python
# This Python file uses the following encoding: utf-8

# @package check
# 功能：获取config配置文件模块
#
# 作者：ma.chunqiang.
#
# 日期：2016-7-25.
#
# 文件：check.py.
# import system modules
import os
import re
import ConfigParser

# # import our modules
import globalvar
from work import recode

# 获取相关的全局变量
#
# 将本地的全局变量都指向到globalvar中全局变量
ENCODE_TYPE = globalvar.ENCODE_TYPE     # 文件默认的系统编码
ERROR_RT = globalvar.ERROR_RT           # 错误返回值
SUCCESS_RT = globalvar.SUCCESS_RT       # 成功返回值
OTHER_ERROR = globalvar.OTHER_ERROR     # 其他错误返回值
DEBUGMODE = globalvar.DEBUGMODE         # debug模式开关
ENTER = globalvar.ENTER                 # 回车符重定义

##读取配置文件
#
#读取配置文件并且把读到的结果返回一个字典
def cfg_parser():
    """
    @param filename: 配置文件名称
    @return cfginfos: 包含配置文件所有内容的字典
    change history:
            2013-11-14 :  re-format all config info to string.     hchen
    """
    try:
        filename = globalvar.CONFIG

        import codecs

        strw = recode('正在获取配置文件信息...')
        print strw

        if not os.path.exists(filename):
            strw = recode('配置文件%s不存在！' % filename)
            print strw
            return ERROR_RT

        cfginfos = {}
        cfg = ConfigParser.ConfigParser()
        filename = os.path.normcase(filename)
        try:
            fObj = codecs.open(filename, 'r', 'utf-8-sig')
            cfg.readfp(fObj)
        except UnicodeDecodeError:
            try:
                fObj = codecs.open(filename, 'r', 'utf-8')
                cfg.readfp(fObj)
            except UnicodeDecodeError:
                try:
                    fObj = open(filename, 'r')
                    cfg.readfp(fObj)
                except UnicodeDecodeError:
                    strw = recode('文件%s编码不支持' % filename)
                    print strw
                    return ERROR_RT

        #get all the sections in the cfg
        section_list = cfg.sections()

        for section in section_list:
            #get all the options in the section
            option_list = cfg.options(section)
            secinfos = {}
            for option in option_list:
                value = str(cfg.get(section, option).strip())
                if value == '':
                    strw = recode('配置文件中{0:s}段{1:s}项为空！'.format(section, option))
                    print strw
                    return ERROR_RT
                # check the format of option value is correct or not
                rt = optionvaluecheck(filename, section, option, value)
                if rt == ERROR_RT:
                    return ERROR_RT

                p = re.compile('portrange$', re.IGNORECASE | re.DOTALL)
                if p.search(option) is not None:
                    value = parserange(value)
                    if value == ERROR_RT:
                        return ERROR_RT
                option = str(option)
                secinfos[option] = value
            section = str(section)
            cfginfos[section] = secinfos

        #进行相关的变量替代,变量以section和key来定义精准制定一个变量
        ReplaceFunction = lambda matched: cfginfos[matched.group("section")][matched.group("key")]
        pattern = '\$\{\[(?P<section>\w+)\]\[(?P<key>\w+)\]\}'
        for section in section_list:
            option_list = cfg.options(section)
            for option in option_list:
                cfginfos[section][option] = re.sub(pattern, ReplaceFunction, cfginfos[section][option])

        fObj.close()
        strw = recode('获取配置文件信息成功')
        print strw

        globalvar.CFG_INFOS = cfginfos
        return SUCCESS_RT
    except KeyboardInterrupt:
        strw = recode('程序执行中断!')
        print strw
        return ERROR_RT
    except Exception, err:
        strw = recode('程序异常退出!check.cfg_parser,异常信息为%s' %err)
        print strw
        return ERROR_RT


##对每个section的option后面的值进行检查
#
#按照提前统一的option命名格式来检查后面的value
#后面根据config.ini设置的需要会在这个函数之中
#加入更多的检查选项
def optionvaluecheck(filename, section, option, value):
    """
    @param filename: config文件名称
    @param section: section
    @param option:
    @param value:
    @return 检查的结果，ERROR_RT or SUCCESS_RT:
    """
    try:
        #检查以ip结尾的option后的value是不是ip的格式
        p = re.compile('ip$', re.IGNORECASE | re.DOTALL)
        if p.search(option) is not None:
            pattern = r'^\d{1,3}\.\d{1,3}\.(\d|\*){1,3}\.(\d|\*){1,3}$'
            if re.match(pattern, value) is None:
                strw = recode('%s中[%s]的%s 格式设置错误' % (filename, section, option))
                print strw
                return ERROR_RT

            for i in value.split('.'):
                i = int(i)
                if i not in xrange(0, 256):
                    strw = recode('%s中[%s]的%s 格式设置错误' % (filename, section, option))
                    print strw
                    return ERROR_RT

        #检查netmask
        p = re.compile('netmask$', re.IGNORECASE | re.DOTALL)
        if p.search(option) is not None:
            if value == '255.255.0.0' or value == '255.255.255.0':
                pass
            else:
                strw = recode('%s中[%s]的%s 格式设置错误' % (filename, section, option))
                print strw
                return ERROR_RT

                #检查ip_2_byte
        p = re.compile('ip_2_byte', re.IGNORECASE | re.DOTALL)
        if p.search(option) is not None:
            pattern = r'^\d{1,3}\.\d{1,3}$'
            if re.match(pattern, value) is None:
                strw = recode('%s中[%s]的%s 格式设置错误' % (filename, section, option))
                print strw
                return ERROR_RT

            for i in value.split('.'):
                i = int(i)
                if i < 0 or i > 255:
                    strw = recode('%s中[%s]的%s 格式设置错误' % (filename, section, option))
                    print strw
                    return ERROR_RT

        return SUCCESS_RT
    except KeyboardInterrupt:
        strw = recode('程序执行中断!')
        print strw
        return ERROR_RT
    except Exception, err:
        strw = recode('程序异常退出!check.OptionValueCheck,异常信息为%s' % err)
        print strw
        return ERROR_RT


##转换portrange为一个列表
#
#传入参数的方式
#10001
#10001-10005
#10001-10005,10009
#注意port每位数字只能是五位,中间的连接符号只能是','
def parserange(string):
    """
    @param string: portrange格式的字符串
    @return rangelist: rangelist转换后的列表
    """
    try:
        if not isinstance(string, str):
            strw = recode('传入参数%s不是字符串' % string)
            print strw
            return ERROR_RT

        p1 = r'^\d{5}$'
        p2 = r'^\d{5}\-\d{5}$'
        if string.find(',') == -1:
            if re.match(p1, string) is not None and re.match(p2, string) is not None:
                strw = recode('传入参数%s格式错误' % string)
                print strw
                return ERROR_RT
        else:
            for port in string.split(','):
                port = port.strip()
                if re.match(p1, port) is not None and re.match(p2, port) is not None:
                    strw = recode('传入参数%s格式错误' % string)
                    print strw
                    return ERROR_RT

        rangelist = []
        if string.find(',') == -1 and string.find('-') == -1:
            rangelist.append(string)
            return rangelist
        tmplist = string.split(',')
        for i in tmplist:
            if i.find('-') == -1:
                rangelist.append(i)
            else:
                tmp = i.split('-')
                start = tmp[0].strip()
                end = tmp[1].strip()
                if int(start) > int(end):
                    strw = recode('传入参数%s格式错误' % string)
                    print strw
                    return ERROR_RT
                for j in range(int(start), int(end) + 1):
                    rangelist.append(str(j))

        if len(list(set(rangelist))) != len(rangelist):
            strw = recode('%s中含有重复的port' % string)
            print strw
            return ERROR_RT

        rangelist.sort()
        return rangelist

    except KeyboardInterrupt:
        strw = recode('程序执行中断!')
        print strw
        return OTHER_ERROR

#    except Exception, err:
#        strw = recode('程序异常退出!,ParseRange,异常信息为%s' % err)
#        print strw
#        return ERROR_RT
