
import sys
import argparse
# 指向此文件的本身
a = sys.argv[1]
print(a)
if a == '0':
    print('測試成功')
# 将255转化成16机制，并且截断左边显示的左边的字符
hex(255).lstrip()
# $()执行并获取命令输出赋值到变量
# 将..添加到文件路径
sys.path.append('..')

# 默認程序sys.argv[0],prog = default



