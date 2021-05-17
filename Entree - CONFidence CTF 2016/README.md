# Entree
This is an old(-ish) challange I picked up to practice some windows userland exploitation.         
We are given a 32bit windows binary:
```console
alon@alon-PC:/mnt/c/Users/alon/Ctfs/Entree$ winchecksec/winchecksec.exe entree.exe
Results for: entree.exe
Dynamic Base    : "Present"
ASLR            : "Present"
High Entropy VA : "NotPresent"
Force Integrity : "NotPresent"
Isolation       : "Present"
NX              : "Present"
SEH             : "Present"
CFG             : "NotPresent"
RFG             : "NotPresent"
SafeSEH         : "NotPresent"
GS              : "Present"
Authenticode    : "NotPresent"
.NET            : "NotPresent"
```
It's a simple service that reverse-echo's your input. 
```console
alon@alon-PC:/mnt/c/Users/alon/Ctfs/Entree$ ./entree.exe
Welcome to the reverse echo service!
Enter number of bytes: 4
Enter data: ASDF
FDSA
Enter number of bytes:
```

## Reversing
Looks like the binary adds a Vectored Exception Handler at the beginning of main.
```asm
push    offset Handler  ; Handler
push    1               ; The first handler to be called
call    ds:AddVectoredExceptionHandler
```
This handler simply re-executes main if it's called the first time, else it calls ExitProcess.
```asm
cmp     is_not_first_called_flag, 0
jnz     short not_first_call
push    offset aFirstChanceExc ; "First-chance exception detected, restar"...
call    _printf
mov     eax, [ebp+ExceptionInfo]
add     esp, 4
inc     is_not_first_called_flag
mov     eax, [eax+4]
mov     dword ptr [eax+0B8h], offset _main
or      eax, 0FFFFFFFFh
pop     ebp
retn    4
not_first_call:
push    offset aByeBye  ; "Bye, bye!\n"
call    _printf
add     esp, 4
push    1               ; uExitCode
call    ds:ExitProcess
```
The binary receives size and data in a loop. There are no apparent overflows.
It then checks if the ptr is below 0x1000 in size.
If it's smaller, it mallocs it. Else, it sets it to zero.
```asm
                push    offset aEnterData ; "Enter data: "
                call    _printf
                mov     esi, [ebp+number_of_bytes]
                add     esp, 4
                lea     eax, [esi+1]    ; eax = number_of_bytes + 1 (nullbyte)
                cmp     eax, 10000h
                jbe     short loc_4010F1 ; if size is below 0x10000
                xor     edi, edi        ; if is more than 0x10000, null ptr dref
                jmp     short loc_4010FC
---------------------------------------------------------------------------
loc_4010F1:                             ; CODE XREF: _main+9B↑j
                push    eax             ; size_t
                call    _malloc
                add     esp, 4
                mov     edi, eax

loc_4010FC:                             ; CODE XREF: _main+9F↑j
```
It then calls get_char in a loop and fills the input from ptr+offset till ptr in reverse.
```asm
call    get_char
mov     [esi+edi], al
dec     esi
jns     short loc_401110
```
And prints the result
```asm
loc_40111B:             ; char* format
push    edi
call    _printf
```
## Vulnerabilities
1. A format strings on the reverse input in printf
2. The null ptr with an arbitrary offset gives us a write-what-where.

## Exploitation:
* Leak pointers from the stack that to break binary and stack aslr.
* construct a rop chain at the stack from the main ret_ptr
* that in put will crash the binary as we'll add garbage data after the payload(the handler will restart main)
* ROP
* profit?

In reality, the rop is rather difficult and time consuming.
We call CreateFileW to open flag.txt and ReadFile to read it,
GetStdHandle to get a handle to stdout and print the flag to it.
We have to construct calls with dynamic parameters(handles are only known at runtime) and read and write to memory at predictable offsets.
Long story short, I used mov dword ptr [ecx], eax to overwrite the future parameters at runtime.
The ROP chain is preety cool, It's available in 'sploit.py'.

```console
alon@alon-PC:/mnt/c/Users/alon/Ctfs/Entree$ python3 sploit.py
[+] Starting local process './entree.exe': pid 182

Enter number of bytes:
 Enter data:
[+] leaked_values: [' d617b5', 'd617b5', '1e', 'd17acf02', '19fd44', 'd61738', '1', '63d150', '635c70', 'd17aceba', '']
[+] stack_canary: 0xd17acf02
[+] stack_leak: 0x19fd44
[+] main_ret_ptr: 0x19fcec
[+] image_leak: 0xd61738
[+] image_base: 0xd60000
Enter number of bytes:
 Enter data:
[*] Switching to interactive mode


Enter number of bytes: DrgnS{NULl_p7r_d3r3f3r3Nc35_N07_4LL_7H47_H4RmL355}\xd6\xe7\x88\xd6\x00\x00\x00\xf4↓☺\x00\x00\x00\x00\xf7↓\x00\x00\xf4↓\xddG\xd6
\x00\x00\x00\x00\xf6↓*@\xd6
XXX @\xd7\xcc\xf4\x19\x00\x00\x00\x00rG\xd6XXXXXXXXXXXXXXXX0L\xd7\x90Pd\x00"d\x00XXXXXXX\x00\x00\x88"d\x00\x00\x00\x00\x00\x0

[*] Process './entree.exe' stopped with exit code 1 (pid 182)
[*] Got EOF while reading in interactive
$
[*] Interrupted
```
