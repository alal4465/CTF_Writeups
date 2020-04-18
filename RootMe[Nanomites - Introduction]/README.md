# ELF x64 - Nanomites - Introduction

This is a crack me with some basic nanomite usage.     
        
Nanomites are a debugger/debuggee anti-RE schema in which the parent process will launch a child process.       
The parent will then debug the child (in this challange this is done via ptrace) and wait for an exception.     
The child will obuscate it's code using different exceptions which the parent will receive and then perform different operations depending on the exception.         
            
Lets jump in.     
The main function does nothing of interest. It prints "please input the flag" and calls a different function.     
This other function contains the interesting stuff.         
              
We can see a fork and then a branch(parent/child).        
```nasm
call    _fork
mov     [rbp+pid], eax
cmp     [rbp+pid], 0
jnz     loc_40098B
```
## The child process: 
will exit if we attempt to debug it (we can of course patch this but it's not essential)           
```nasm
mov     ecx, 0
mov     edx, 0
mov     esi, 0
mov     edi, 0          ; request
mov     eax, 0
call    _ptrace
cmp     rax, 0FFFFFFFFFFFFFFFFh
jnz     short loc_40091B ; child process
mov     edi, offset aSoYouWantToTra ; "So you want to trace me?!"
call    _puts
mov     edi, 2Ah        ; status
call    _exit
```
If everything is ok it will execute the following code:
```nasm
child_code:                             ; DATA XREF: .data:src↓o
.rodata:0000000000400AC0                 xor     rax, rax
.rodata:0000000000400AC3                 xor     rcx, rcx
.rodata:0000000000400AC6                 xor     rbx, rbx
.rodata:0000000000400AC9                 mov     al, [rdi] ; rdi points to input. first char is in al.
.rodata:0000000000400ACB                 int     3               ; Trap to Debugger
.rodata:0000000000400ACC                 nop
.rodata:0000000000400ACD                 jnz     short loc_400B44
.rodata:0000000000400ACF                 inc     rdi
.rodata:0000000000400AD2                 mov     al, [rdi] ; second char is in al.
.rodata:0000000000400AD4                 int     3               ; Trap to Debugger
...
```
So the child puts a char of our input in al and causes an exception(which the parent will catch).        
The parent will probably change the child's ZF and the child will preform a jump based on that (most likely if the char check is successful).          

## The parent:
```
lea     rcx, [rbp+stat_loc]
mov     eax, [rbp+pid]
mov     edx, 0          ; options
mov     rsi, rcx        ; stat_loc
mov     edi, eax        ; pid
call    _waitpid
```
The parent waits for the child process.        
if the ecxeption in the child is relevent it will call this code:       
```nasm
mov     edx, [rbp+pid]
mov     rax, [rbp+pChildCode]
mov     esi, edx
mov     rdi, rax
call    check_pass_char
```
at the beginning of the function we see a call to ptrace with PTRACE_GETREGS.        
the child's registers are stored in a user_regs_struct at rbp-0F0h.          
```nasm
lea     rdx, [rbp+regs]
mov     eax, [rbp+pid]
mov     rcx, rdx        ; *data
mov     edx, 0          ; *addr
mov     esi, eax        ; pid
mov     edi, 0Ch        ; request
mov     eax, 0
call    _ptrace         ; PTRACE_GETREGS
mov     [rbp+i], 0
jmp     loc_40084A
```
So after looking at the validation algorithm for about 30 minutes I realised it could easily be bypassed.      
A character from our input is compared to the char calculated from the algorithm so we can set a breakpoint there and compare it.         
```nasm
mov     rax, [rbp+regs.rax] ; rax contains byte from input
cmp     rdx, rax        
jnz     short loc_40081E
mov     rax, [rbp+regs.eflags] ; if true set ZF (correct char)
or      rax, 40h
mov     [rbp+regs.eflags], rax ; sets ZF
```
after that another ptrace call will be made to modify the childs ZF and then back to waiting for an exception.          
we can write a simple script using r2pipe to carve out the flag.         

```zsh
root@kali:~/CTF/crackmes# python grab_flag.py 
Process with PID 1821 started...
...
...
'#censored#'
```




