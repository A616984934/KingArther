import re
import os
import subprocess
import start
import log
import signal


log = log.log
args = start.args
__version__ = '0.0.1'
def Getpid(cmd1):

    proc = subprocess.run(cmd1, shell=True, stdin=subprocess.PIPE)
    new_pid = proc.pid
    return new_pid+1

def datewith(ehto):
    cmd = 'ifconfig {}'.format(ehto)
    cmp = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    result = cmp.stdout
    pattern1 = re.compile('(发送字节:.*?(\d+))', re.DOTALL)
    Conse = re.search(pattern1, result)
    conseque = Conse.group(1)
    pattern2 = re.compile('(发送数据包:.*?(\d+))', re.DOTALL)
    Conse2 = re.search(pattern2, result)
    conseque2 = Conse2.group(2)
    print("此时数据包为")
    return conseque, conseque2
e1 = 3
eht = args.i
# 获取全部数据
# def Result_test(eht0):
#     cmd = 'cat /proc/net/pktgen/{}'.format(eht0)
#     cmp = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
#     result = cmp.stdout

def sigintHandler(signum,frame):
    PauseSendBytes = datewith(eht)[0]
    PauseSendPackages = datewith(eht)[1]
    dif_bytes = str(int(FirstSendBytes)-int(PauseSendBytes))
    dif_Packages = str(int(FirstSendPackages)-int(PauseSendPackages))
    log.warning('中断发送，已经发送的总字节数{}，已经发送的总数据包{}'.format(dif_bytes, dif_Packages))
    print("记录日志")
    os.kill()

def run():

    if args.r is not None:
        R = args.r
    else:
        R = ""
    if args.l is not None:
        L = args.l
    else:
        L = ""
    if args.s is not None:
        S = args.s
    else:
        S = ""
    if args.c is not None:
        C = args.c
    else:
        C = ""
    cmd1 = 'nohup ./pktgent.sh -i enp5s0f0 -r 100 -l 2000 >my.log 2>&1 &'
    cmd = 'bash pktgen.sh -i {} -r {} -l {} -s {} -c {}'.format(eht, R, L, S, C)
    print('execute pktgen cmd: ', cmd)

    if R != "":
        R1 = R
    if L != "":
        L1 = L
    if S != "":
        S1 = S
    if C != "":
        C1 = C
    log.info("测试网口{}，发包速率{}，发送包长度{}，发送速度{}，总的发包数量{}".format(eht, R1, L1, S1, C1))
    signal.signal(signal.SIGINT,sigintHandler)
    signal.signal(signal.SIGTERM,sigintHandler)

if __name__ == "__main__":
    FirstSendBytes = datewith(eht)[0]
    FirstSendPackages = datewith(eht)[1]
    log.info('初始数据为{}字节，{}数据包'.format(FirstSendBytes,FirstSendPackages))
    try:
        run()
    except Exception as e:
        print("无法执行，请检查相关日志")
