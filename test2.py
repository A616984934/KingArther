import argparse

#prog = 错误参数，usage报错具体内容
parser = argparse.ArgumentParser(description='owen1',prog='xxx',usage='尝试更改相关的文件',epilog='帮助信息')

#https://blog.csdn.net/explorer9607/article/details/82623591 需要输入相应的命令和文件进行交互
#如果不设定值默认为str类型的文件，type修改完成就好
#choice=[]限制变量只能在choice中
parser.add_argument("-x", help="横坐标",type=int)
parser.add_argument('-y', help="纵坐标",type=int)

# 设置一个常量进行输入,const设置的就是固定的参数
parser.add_argument('--foo',action='store_const',const=43)
parser.add_argument('-v','--version',help='目标翻倍',action='store_true',)

# 同一个参数需要多个值得时候，则要制定action='append'
parser.add_argument('-a',action='append')
# 输入的命令xx.py -a 1 -a b 可以添加多个参数,可以加多个值

# dest修改变量的名字，使用xx调用相应的值
parser.add_argument('-p','--port',dest='xx',default='/dev/ttyUSB0',help='mcu test connect')

#nargs 可以指定一个参数可以具体有几个变量
#通配符 + 一个或者多个变量， ? 0/1个变量  *任意变量
parser.add_argument('--foo',nargs=3)
#--foo 3 2 1   -------------namespace(foo=['3''2''1']

# 可选参数-或者--，可以不用输入，但是，如果不加-或者--，那么就是位置参数，如果不填写内容的话，则会报错
args = parser.parse_args()
x = args.x
y = args.y
# 此处必须使用-- 后面的值才能添加到相应的命名空间中
if args.version:
    args.x=args.x*2
z = args.x
# 默认参数
print(args.foo)

if x == '1':
    print('头顶一片大草原')

"""
action 對應的參數-----选择需要执行的操作：
store 默认选项，存储参数的值
store_const 存储被const命名的参数值
('--foo',action='store_const',const=42)
store_true/store_false分别用作存储True和False值的特殊用例，
其默认值为False/True('--foo',action='store_true')
count 计算每一个关键字参数出现的数目或者次数
parser.add_argument('--verbose','-v',action='count',default=0)
"""
# 将参数按照功能进行概念分组，便于用户调用
info_group = parser.add_argument_group('device information')