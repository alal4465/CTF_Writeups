# PE x86 - Xor Madness
#### "xor, sub, call, ret. Nothing else."
this is a challange in the cracking category from https://www.root-me.org/ .         
it's cool because the author decided to use only xor, sub, call and ret across the whole binary.    
before aproaching this challange you should know the basic properties of xor.         
      
in the binary often found are these type of obuscations:      
```nasm
xor     edx, edx
xor     edx, eax ; for moving a value
```
```nasm
call    $+5 ; in the contex of this challange this is practically garbage
```
```nasm
xor     ecx, ecx
xor     ecx, [eax]
xor     [eax], ecx ; for setting memory at eax to zero
```
      
the main function is heavily obuscated and is not for the faint of heart.  
## basic summary of the main function:
it prints "password:" and scans input with scanf.         
here comes the meaningfull part:         
      
it takes our input and subtracts 0x100 from it's address.   
```nasm
xor     esp, esp
xor     esp, edi        ; edi/esp point to input
...
sub     esp, 100h
```
it xores the first byte of our input with a hard-coded value(59307554h).        
```nasm
xor     ebx, ebx
xor     bl, [esi]       ; first byte of string to bl
xor     ebx, 59307554h  ; xored with const
xor     ecx, ecx
xor     cl, bl
xor     ebx, ebx
xor     bl, cl          ; bl/cl have xored 1st byte
```
it then takes this xored value and xores it once more with input_addr - 0x100.     
```nasm
xor     eax, eax
xor     eax, esp        ; eax/esp = input_addr - 0x100
xor     eax, ebx        ; eax=xored_1st_byte ^ (input_addr-0x100)
```
the whole thing is practiclly equivilent to:      
passwd[0] ^ 0x54 ^ (input_addr - 0x100)     
it stores this value in edx and moves on.      
        
it then takes the input_addr - 0x100 and xores if with some more hard-coded values.     
```nasm
xor     eax, esp        ; eax/esp = input_addr - 0x100
xor     eax, 0F2h
xor     eax, 82h        ; eax^ some_tings
```
it goes on to set the value at the xored address to 1.     
```nasm
xor     ecx, ecx
xor     ecx, [eax]
xor     [eax], ecx      ; [eax]=0
xor     byte ptr [eax], 1 ; xor first byte in [eax] (we know it to be 0 so set it to 1)
```
and sets edx to the memory at the address calculated from our input (passwd[0] ^ 0x54 ^ (input_addr - 0x100))     
```nasm
xor     eax, eax
xor     eax, edx        ; eax/edx=1st_input_byte ^ (input_addr-0x100)
xor     edx, edx
xor     edx, [eax]      ; edx=[eax]. we will later find out that it needs to be 1
xor     ebx, ebx
```
it then calls some function and as a paremeter it passes the function that continues the password-checking routine.
```nasm
xor     [esp], offset A
call    jump_func_if_edx_1
```
## transition function:
this function decides if we get to continue our password checking.     
lets check it out.      
```nasm
xor     eax, eax
xor     eax, [esp+arg_0] ; eax = nextFunc
sub     eax, [esp+0]    ; eax =nextfunc-someValue
mul     dl              ; eax=eax*dl
add     eax, [esp+0]    ; eax+=someValue
xor     ecx, ecx
xor     ecx, [esp+0]
xor     [esp+0], ecx
xor     [esp+0], eax    ; ret_pointer=eax
retn    4
```
1.it takes the address of out target function     
2.subtracts some value from it      
3.multiplies the outcome by dl      
4.adds the same value to it       
5.jumps to the final computed value       
so in order to get to our target function dl has to equal 1.     
```
(pFunc-Value)*1 + value = pFunc - Value + Value = pFunc         
```
## profit
at this point everything starts to click.       
we set dl to the memory at (1st_input_byte^0x54^ (input_addr-0x100)).       
we also set the memory at (hard_coded_values ^ (input_addr-0x100)) to 1.      
from this we conclude that in order to continue the password-checking:        
hard_coded_values ^ (input_addr-0x100) needs to equal 1st_input_byte^0x54^ (input_addr-0x100)       
after some rearranging:     
hard_coded_values = 1st_input_byte ^ 0x54      
....     
1st_input_byte = 0x54 ^ hard_coded_values.     
so we can calculate our first char!      
```python
>>> chr(0x54 ^ 0x82 ^ 0xF2)
'$'
```
the other checking fuctions do preety much the same thing with diffrent hard-coded values.      
we can calculate the password:       
```python
>>> passwd = [0x82^0xf2^0x54,0x67....
>>> "".join([chr(i) for i in passwd])
'#censored#'
```
```
