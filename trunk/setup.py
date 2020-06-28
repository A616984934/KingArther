#!/usr/bin/env python
# This Python file uses the following encoding: utf-8

from distutils.core import setup
import py2exe
import os
import shutil
import time
import sys
import zipfile
import re
import globalvar
import runconfig

from glob import glob
# import sys
# sys.path.append(r'E:\SVN\automationtest\CodeLib\recordtime')
# import record_time


## 获取编译后的名称

product = runconfig.product
station = runconfig.station
exe_filename = 'Auto%s%s' % (product, station)

##定位main_file的名称
main_file = 'Auto%sBurnIN.py'%product

##版本
version = runconfig.version
svn_version = '1464'

## 定义最终生成的目录
ZIP_DIR = 'D:\ZIP_DIR'
FOLDER = '%s'%product

# 获取当前系统.
ENCODE_TYPE = sys.getfilesystemencoding()

# 将字符串strw从utf-8编码转换成ENCODE_TYPE编码.
def recode(strw):
    return strw.decode('UTF-8').encode(ENCODE_TYPE)

## 获取当前文件所在文件夹路径.
#
# 通过sys.path[0]判断并返回当前文件所在文件夹路径.
def cur_file_dir():
    path = sys.path[0]
    if os.path.isdir(path):
        return path
    if os.path.isfile(path):
        return os.path.dirname(path)


def GetInputVersion():
    global svn_version    
    strw = 'Please input svn version:'
    while True:
        rt = raw_input(strw)
        pattern = '\d+'
        if re.match(pattern, rt) == None:
            strw = 'version format invalid, eg 1642:'
        else:
            break
    svn_version = rt   

    return None
 
##将文件夹打包
#
#打包的时候,根据flag在打包的名字后面加上PASS或者FAIL
def MakeZip(log_dir,zip_file_name):
    """To make log zip packege.
    传入参数:    logdir(文件夹)
                 flag(标志,当flag为False的时候,
                      在打包文件末尾加上FAIL)
    返回值:      zpath(打包的文件路径)
    """
    strw = recode('正在打包日志文件夹...')
    # print strw

    #last_level_dir = os.path.dirname(cur_file_dir())
    #zip_dir = os.path.join(last_level_dir, 'ZIP_DIR')
    
    zip_dir = os.path.join(ZIP_DIR, FOLDER)
    if not os.path.exists(zip_dir):
        os.makedirs(zip_dir)

    zpath = os.path.join(zip_dir, zip_file_name)
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


    strw = recode('已打包日志文件%s.' % os.path.basename(zpath))
    # print strw
    return

def GenerateSvnVersionFile():
    f = open('svn_version.txt', 'a')
    f.write('svn version:' + svn_version + '\n')
    f.close()

    
GetInputVersion()
GenerateSvnVersionFile()

## 将config文件进行重定位
wkdir = os.getcwd()
config_file = os.path.join(wkdir, '%s%s_config.ini' %(product, station))
target_file = os.path.join(wkdir, 'config.ini')
if os.path.exists(config_file):
    # if os.path.exists(target_file):
    #     os.remove(target_file)
    shutil.copyfile(config_file, target_file)
else:
    print 'no file named %s' % os.path.basename(config_file)
    
    
## 定义需要包含进工程的文件.
data_files = [("Microsoft.VC90.CRT",
               glob('Microsoft.VC90.CRT\*.*')),
              (".\\", glob("config.ini")),
              (".\\", glob("changenote.txt")),
              (".\\", glob("SnMacGeneratorExe.bat")),
              (".\\", glob("svn_version.txt")),
              (".\\",glob("readme.txt"))]

## 环境相关，具体可参见py2exe首页.
includes = ["encodings",
            "encodings.*"]

## 编译选项. 
options = {"py2exe": {"bundle_files": 1}}

## 编译规则.
setup(version = version,
      data_files=data_files,
      options=options,
      zipfile=None,
      windows=[{"script": main_file, "dest_base": exe_filename}])

time.sleep(2)
##编译完成后,还要自动将程序进行打包

time_str = time.strftime('%Y%m%d%H%M')
zip_file_name = exe_filename + '_' + version + '.zip'
log_dir = os.path.join(cur_file_dir(), 'dist')
MakeZip(log_dir,zip_file_name)

time.sleep(2)

# 删除build和dist
import shutil
dir_list = [
    'build',
    'dist'
    ]
for dir in dir_list:
    dir = os.path.join(cur_file_dir(),  dir)
    shutil.rmtree(dir)

file = os.path.join(cur_file_dir(),  'svn_version.txt')
os.remove(file)


del_paths = [name for name in os.listdir('.') if name.endswith('.pyc') or name.endswith('.py~')]
for del_path in del_paths:
    os.remove(del_path)






