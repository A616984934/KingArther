
import os
import re
import time

ERROR_RT    = '11'
SUCCESS_RT  = '22'

def ShellCmd(cmd,wait=True):
    time.sleep(0.1)
    p = os.popen(cmd)
    if wait:
        rt = p.read()
    else:
        return SUCCESS_RT
    return rt

def get_port():
    cmd = 'lspci -d 8086:150e | cut -d" " -f 1'
    data = ShellCmd(cmd)
    rx_list1 = data.split('\r')[0].split('\n')
    rx_list1 = [i for i in rx_list1 if i != '']
    for j in range(0,len(rx_list1),2):
        rx_list1[j],rx_list1[j+1] = rx_list1[j+1],rx_list1[j]
    cmd = 'lspci -d 8086:150f | cut -d" " -f 1'
    data = ShellCmd(cmd)
    rx_list2 = data.split('\r')[0].split('\n')
    rx_list2 = [i for i in rx_list2 if i != '']
    rx_list = rx_list1+rx_list2

    #print rx_list
    rx_port_list = ''
    for port in rx_list:
        cmd = r"ls /sys/class/net/ -lh | grep '%s' >%s.txt "%(port,i)
        data = ShellCmd(cmd)
        cmd = r'''cat %s.txt'''%i
        #print cmd
        data = ShellCmd(cmd)
        p = re.search('en\S+', data)
        if p==None:
            data=''
        else:
            data=p.group()
        rx_port_list = rx_port_list + data + ' '
    print (rx_port_list)
    return rx_port_list
get_port()
