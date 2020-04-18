import r2pipe
import re
r = r2pipe.open('./ch28.bin', flags=['-d'])
r.cmd('dor stdin=./input.txt')
r.cmd('doo')
r.cmd('aaaa')
r.cmd('db 0x0040080d')
flag=''
for i in range(14):
    r.cmd('dc')
    r.cmd('dc')
    passwd_char=re.findall('0[xX][0-9a-fA-F]+',r.cmd('dr rax=rdx'))[1]
    flag+=chr(int(passwd_char,16))

print(flag)
