#!/bin/bash
NO_ARGS=0
E_OPTERROR=85
COUNT=0
PKT_SIZE=""
ASSIGN_DEVICE=""
RATE=20
Speed=50

starttime=`date +'%Y-%m-%d %H:%M:%S'`

function usage() {
    echo "Usage: `basename $0` options (-i:r:l:c:d:h:s)"
    echo "      -i  Interface"
    echo "      -r  Rate"
    echo "      -l  Pkt len"
    echo "      -c  Pkt count"
    echo "      -d  Deamon mode"
    echo "      -s  rate Speed"
    echo "      -h  show this help"
}

if [ $# -eq "$NO_ARGS" ]
then
    usage
    exit $E_OPTERROR
fi


# 第一个冒号表示忽略错误，字符后面的冒号表示此字符需要参数2=
while getopts ":i:r:l:c:d:h:s" Option
do
    case $Option in
    i)      ASSIGN_DEVICE=$OPTARG
        echo "First device: ${ASSIGN_DEVICE}" ;;
    r)      RATE=$OPTARG
        echo "Send Rata 速率为: ${RATE}%" ;;
    l)      PKT_SIZE=$OPTARG
        echo "Pkt len: ${PKT_SIZE}" ;;
    c)      COUNT=$OPTARG
        echo "Packet count: ${COUNT}" ;;
    d)
        echo "进入进入后台模式" ;;
    s)      Speed=$OPTARG
        echo "rate Speed：${Speed}";;
    h)
        usage
        exit 0
        ;;
    *)
        echo "Unimplemented option";;
    esac
done
echo "--------------$COUNT------------"


#卸载驱动
rmmod pktgen

sleep 1

#删除已有文件
rm -rf /proc/net/pktgen/kpktgend_*

#加载驱动
modprobe pktgen

echo "继续执行"
function pgset() {
    local result
    
    echo $1 > $PGDEV
    result=`cat $PGDEV | fgrep "Result: OK:"`
    if [ "$result" = "" ]; then
        cat $PGDEV | fgrep Result:
    fi
}

function pg() {
    echo inject > $PGDEV
    cat $PGDEV
}

# Config Start Here -----------------------------------------------------------


# 多线程控制，使用add_device,rem_device_all
# max_before_softirq 在最多发送多少个包后，执行do_softirp
# Each CPU has own thread. Two CPU, two device example.

PGDEV=/proc/net/pktgen/kpktgend_2
echo "Adding ${ASSIGN_DEVICE}"
pgset "add_device ${ASSIGN_DEVICE}"
# device config
echo "配置加载"
#CLONE_SKB="clone_skb 100000"
## NIC adds 4 bytes CRC
#MIN_PKT_SIZE="min_pkt_size 1280"
#MAX_PKT_SIZE="max_pkt_size 1280"

if [ ! -n "$PKT_SIZE" ];
then
    PKT_SIZE=1024
fi
echo "==============$PKT_SIZE================"

 PGDEV=/proc/net/pktgen/${ASSIGN_DEVICE}
   echo "Configuring $PGDEV"
  pgset "clone_skb 100000"
  pgset "count ${COUNT}"
  pgset "pkt_size $PKT_SIZE"
  pgset "rate ${RATE}%"
  pgset "rate ${Speed}M"
  pgset "flag QUEUE_MAP_RND"
  pgset "flag IPSRC_RND"
  pgset "flag IPDST_RND"
  pgset "src_min 11.0.0.0"
  pgset "src_max 11.255.255.255"
  pgset "dst_min 10.0.0.0"
  pgset "dst_max 10.255.255.255"
  pgset "dst_mac  00:04:23:08:91:dc"
  pgset "dst_mac_count 1024"

echo "配置加载完成"
# Result can be vieved in /proc/net/pktgen/eth[1,2]
PGDEV=/proc/net/pktgen/pgctrl

echo "Running... ctrl^C to stop"
pgset "start"
endtime=`date +'%Y-%m-%d %H:%M:%S'`
start_seconds=$(date --date="$starttime" +%s);
end_seconds=$(date --date="$endtime" +%s);
echo "本次运行时间： "$((end_seconds-start_seconds))"s"
echo "Done"
