subprocess.run(args, check=True, stdout=subprocess.PIPE).stdout）

（1） args：启动进程的参数，默认为字符串序列（列表或元组），也可为字符串（设为字符串时一般需将shell参数赋值为True）；
（2） shell：shell为True，表示args命令通过shell执行，则可访问shell的特性；
（3） check：check为True时，表示执行命令的进程以非0状态码退出时会抛出；subprocess.CalledProcessError异常；check为False时，状态码为非0退出时不会抛出异常；
（4） stdout、stdin、stderr：分别表示程序标准标输出、输入、错误信息；
run函数返回值为CompletedProcess类，若需获取执行结果，可通过获取返回值的stdout和stderr来捕获；


keyboardInterrupt 异常的处理
将获取的键盘的终止命令，进行异常处理
try:
except keyboardInterrupy

run调用配置脚本，通过中间脚本调用Log和shell脚本