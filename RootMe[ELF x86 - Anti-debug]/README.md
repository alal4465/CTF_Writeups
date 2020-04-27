# ELF x86 - Anti-debug

this is a binary implementing some anti-debug tricks.     
          
a common theme throughut this binary is:        
```nasm
mov     eax, 30h
mov     ebx, 5          ; SIGTRAP
mov     ecx, offset handler_1 ; handler
int     80h             ; LINUX - sys_signal
jmp     short loc_8048077
loc_8048077:            
int     3               ; Trap to Debugger
jmp     short loc_804807B
```
this code sets up an exception handler and then uses INT 3 to cause an exception.                
if a debugger is present it would catch this exception.              
if not, the handler routine will be executed.              
this is a classic anti-debug trick.            

the first handler that we come across is modifying the code inside the binary.         
this is the boiled down code:
```nasm
handler_1  proc near               ; DATA XREF: start+D↑o
mov     eax, offset handler_3
...
loop_start:
cmp     eax, 80482E8h
jz      short end_loop
...
xor     dword ptr [eax], 8048FC1h
add     eax, 4
...
jmp     short loop_start
...
end_loop:                         ; CODE XREF: handler_1+C↑j
retn
endp
```
so its xoring 4 bytes at a time from the offset of the 3rd handler.           
we can write a simple python script to get the unencrypted binary.           
```python
from pwn import *

with open('ch13','rb') as f:
    data=f.read() # read contents of binary

data=bytearray(data)
xor_key=0x8048FC1 # define xor key

for i in xrange(0x104,0x2E8,4):
    data[i:i+4] =p32(int(hex(u32(data[i:i+4])),16) ^ xor_key) # xor the encrypted section 4 bytes at a time

with open('ch13_modified','wb') as f:
    f.write(data) # write to new "ch13_modified" file.

```

this time the binary looks alot cleaner and we can also see an unencrypted "Enter the password:" string.        
handler 3 reads our password an stores it in a fixed buffer
```nasm
handle_3 proc near
mov     ebx, 1
mov     ecx, offset aEnterThePasswo ; "Enter the password: "
mov     edx, 14h
call    write ; fuction uses "write" syscall
mov     ebx, 0
mov     ecx, 8048251h   ; *buf
mov     edx, 80h
call    read  ; fuction uses "read" syscall
```
the 4th handler seems to xor our password with a fixed 0xFC
```nasm
handle_4 proc near
mov     eax, 8048251h # fixed buffer
start_loop:
cmp     byte ptr [eax], 0 # if a null byte is reached stop xoring
jz      short end_proc

xor     byte ptr [eax], 0FCh # xor char with 0xfc
inc     eax # increase pointer
jmp     short start_loop:

end_proc:
retn
handle_4 endp
```
the 5th handler seems to do our password checking.           
it takes our xored input and checks if its equal to some byte array.              
```nasm
handle_5 proc near
mov     eax, 8048251h ; eax - *input
mov     ebx, offset byte_80482D1 ; ebx - *some_char_array 
start_loop:
mov     cl, [eax] ; byte from input
cmp     cl, [ebx] ; if byte not equal -> print bad message
jnz     short print_bad
cmp     cl, 0 ; if null byte (end of string) print good message
jz      short print_good
inc     eax
inc     ebx
jmp     short start_loop
print_good:
mov     ebx, 1
mov     ecx, offset dword_80481E4
mov     edx, 23h        ; probably correct message
call    write
call    exit
print_bad:
mov     ebx, 1
mov     ecx, offset byte_8048207
mov     edx, 16h        ; probably false message
call    write
call    exit
```
we can also write a simple python script to extract this password.            
```python
byte_arr = [0xA5, 0xCF, 0x9D, 0xB4, 0xDD, 0x88, 0xB4, 0x95, 0xAF, 0x95, 0xAF, 0x88, 0xB4, 0xCF, 0x97, 0xB9, 0x85, 0xDD]

xor_key = 0xfc

print "".join([chr(0xfc ^ ch) for ch in byte_arr ])
```
trying it on the binary...            
```console
root@kali:~/CTF/crackmes# ./ch13 
Enter the password: #censored#
Gratz, this is the good password !
```
nice.     
