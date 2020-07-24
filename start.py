import argparse
import os
import log
__version__ = '0.0.1'

parser = argparse.ArgumentParser(description='操作pktgen')
parser.add_argument('-v', '--version', action='version', version='此版本为{}'.format(__version__))
parser.add_argument('-i', help='Specify the network interface to send packets')
parser.add_argument('-r', help='Specify packets send rate percent, default is 50%')
parser.add_argument('-l', help='Specify the packets length, default is 1024')
parser.add_argument('-s', help='Rate Speed')
parser.add_argument('-c', help='Specify the total packets to send, default is 0, mean unlimite')
parser.add_argument('-d', help='run in the background', action='store_true')
args = parser.parse_args()
print(args)

if args.d:
    cmd = 'nohup python3 -u run.py > out.log 2>&1 &'
    os.system(cmd)
    log.log.info('进入后台模式')
    exit()
else:
    log.log.info('进入正常模式')



