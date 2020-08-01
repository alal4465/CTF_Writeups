# Maze[rev]
Maze is challange in the reversing category from UNCTF-2019.
```console
root@kali:~/CTF/WMCTF/easy_maze# ./easy_Maze 
Please help me out!
asdf
Oh no!,Please try again~~
```
When reversing we can see the verifying function being called with some array.
```asm
mov     rdi, rax        ; some array
call    _Z6Step_2PA7_ii
```
After staring at this function, it is clear this array represents 
some sort of maze through which we move by controlling x and y values.
The maze ends at the coordinate (6,6) and the values are 1's and 0's.
1's can be walked on while 0's can not.
                      
The array dumped through radare2:               
```asm
0x7fff618d87c0 0x0000000000000001   ........ @rsp 1
0x7fff618d87c8 0x0000000100000000   ........ 4294967296
0x7fff618d87d0 0x0000000100000001   ........ 4294967297
0x7fff618d87d8 0x0000000100000001   ........ 4294967297
0x7fff618d87e0 0x0000000100000000   ........ 4294967296
0x7fff618d87e8 0x0000000000000001   ........ 1
0x7fff618d87f0 0x0000000100000000   ........ 4294967296
0x7fff618d87f8 0x0000000100000001   ........ 4294967297
0x7fff618d8800 0x0000000000000001   ........ 1
0x7fff618d8808 0x0000000100000001   ........ 4294967297
0x7fff618d8810 0x0000000000000001   ........ 1
0x7fff618d8818 0x0000000000000000   00000000 
0x7fff618d8820 0x0000000100000001   ........ 4294967297
0x7fff618d8828 0x0000000000000000   00000000 
0x7fff618d8830 0x0000000100000001   ........ 4294967297
0x7fff618d8838 0x0000000100000001   ........ 4294967297
0x7fff618d8840 0x0000000000000000   00000000 
0x7fff618d8848 0x0000000100000000   ........ 4294967296
0x7fff618d8850 0x0000000000000000   00000000 
0x7fff618d8858 0x0000000100000000   ........ 4294967296
0x7fff618d8860 0x0000000100000001   ........ 4294967297
0x7fff618d8868 0x0000000100000001   ........ 4294967297
0x7fff618d8870 0x0000000100000001   ........ 4294967297
0x7fff618d8878 0x0000000000000001   ........ 1
0x7fff618d8880 0x0000000000000001   ........ 1
```
Player input:           
```asm
cmp     eax, 64h ; 'd'
jz      short add_x

cmp     eax, 73h ; 's'
jz      short add_y

cmp     eax, 77h ; 'w'
jnz     short loc_17BC
...

sub_y: 
...
sub     [rbp+y], 1
jmp     short loc_17E5

add_y:                               
add     [rbp+y], 1
jmp     short loc_17E5

sub_x:                              
sub     [rbp+x], 1
jmp     short loc_17E5

add_x:                             
add     [rbp+x], 1
jmp     short loc_17E5
```
The index into the array is chosen so:
```asm
mov     eax, [rbp+y]
movsxd  rdx, eax
mov     rax, rdx
shl     rax, 3
sub     rax, rdx
shl     rax, 2
mov     rdx, rax        ; rdx = rax = y*28
mov     rax, [rbp+arr]
add     rdx, rax        ; arr + y*28
mov     eax, [rbp+x]
cdqe
mov     eax, [rdx+rax*4]; arr[y*7 + x] == 1
cmp     eax, 1
```
Because the y value is multiplied by 7 it is clear the array is 7xn.
A simple script in python to print the array in format:
```python
import re

def split_every_n(line,n):
    return [line[i:i+n] for i in range(0, len(line), n)]

# read dump file
with open("dump","r") as f:
    data = f.read()

# extract array from dump using regex
hex_regex = re.findall("0x0[0-9a-fA-F]+", data)

# split every string in array to two parts
hex_regex = [split_every_n(s[2:],8) for s in hex_regex]

# flatten sublists
hex_regex = [val for sublist in hex_regex for val in sublist[::-1]]

# convert list to a string with '0'(can't walk there) '1'(free to walk)
maze = "".join([hx[-1] for hx in hex_regex])

# split the string every 7th character
maze = split_every_n(maze,7)

# write to file
with open("maze_map","w") as f:
    f.write("\n".join(maze))
```

The formated maze looks like this:
```
 x
y 1001111
  1011001
  1110111
  0001100
  1111000
  1000111
  1111101
```

We can see a clear path of 1's that leads to the cordinate (6,6).
```console
root@kali:~/CTF/WMCTF/easy_maze# ./easy_Maze 
Please help me out!
ssddwdwdddssaasasaaassddddwdds
Congratulations!
Thanks! Give you a flag: UNCTF{ssddwdwdddssaasasaaassddddwdds}
```
