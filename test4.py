from subprocess import check_output
import subprocess
import re
cmd = 'nohup ./pktgent.sh -i enp5s0f0 -r 100 -l 2000 >my.log 2>&1 &'
cmp = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
result = cmp.stdout
print(result)
pattern1 = re.compile('(\d+).*?(\d+)', re.DOTALL)
Conse = re.search(pattern1, result)
conseque = Conse.group(1)




